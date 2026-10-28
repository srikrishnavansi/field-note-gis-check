"""Voice note -> GIS hydrant record with claude-haiku-5-5, k=2; field scoring vs the note; code verify vs real Stadt Zuerich data. Needs ANTHROPIC_API_KEY in the environment."""
import gzip, json, os, sys, math
from concurrent.futures import ThreadPoolExecutor
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import llm as em
from notes import NOTES, F
PACK, MODEL, MAX_M = 'field-note-gis-check', 'claude-haiku-5-5', 60  # calibration knob: hydrant must sit within 60 m of the stated address

H = {x['properties']['oberflur_nummer']: x['properties'] for x in json.load(open('data/hydranten.geojson'))['features'] if x['properties']['oberflur_nummer']}
A = {(a['lokalisationsname'], a['hausnummer'], int(a['plz'])): a for a in (x['properties'] for x in json.load(gzip.open('data/adressen.geojson.gz'))['features']) if a['status_txt'] == 'real' and a['hausnummer']}

def verify(r):
    """Refuse a record unless its hydrant and address are real and near each other. Returns list of reasons (empty = accepted)."""
    why = []
    h, a = H.get(str(r['hydrant_nr'])), A.get((r['street'], str(r['house_number']), r['plz']))
    if not h: why.append('hydrant_nr not in Stadt Zuerich hydrant register')
    if not a: why.append('street + house number + PLZ not in Stadt Zuerich address register')
    if h and a:
        d = math.dist((h['xkoord'], h['ykoord']), (a['hausnummer_koord_ost'], a['hausnummer_koord_nord']))
        if d > MAX_M: why.append(f'hydrant is {d:.0f} m from that address')
        if r['install_year'] is not None and r['install_year'] != h['verlegejahr']: why.append(f"install_year {r['install_year']} but register says {h['verlegejahr']}")
    return why

N = lambda t: {"anyOf": [{"type": t}, {"type": "null"}]}
SCHEMA = {"type": "object", "additionalProperties": False, "required": F, "properties": {
    "hydrant_nr": N("string"), "street": N("string"), "house_number": N("string"), "plz": N("integer"),
    "hydrant_type": {"anyOf": [{"type": "string", "enum": ["Oberflurhydrant", "Unterflurhydrant"]}, {"type": "null"}]},
    "install_year": N("integer"), "depth_m": N("number"), "pipe_dn": N("integer"),
    "pipe_material": {"anyOf": [{"type": "string", "enum": ["Guss", "Duktil", "PE", "Stahl"]}, {"type": "null"}]},
    "date": {"anyOf": [{"type": "string", "description": "YYYY-MM-DD"}, {"type": "null"}]}}}
SYS = ("You turn a construction crew's transcribed voice note (Swiss German, German or English, spoken numbers possible) into a GIS record for a "
       "water hydrant at an open trench in Zurich. Write street names in standard German spelling as an official address would be. "
       "Cast iron = Guss. Use null for anything the note does not state; never guess or fill in.")

def run(n):
    for a in range(4):
        try: return em.call(PACK, f'{MODEL} extract', MODEL, SYS, [{"type": "text", "text": n[0]}], schema=SCHEMA, max_tokens=500, effort='low')
        except Exception as e:
            if a == 3 or isinstance(e, SystemExit): raise

def same(k, a, b):
    if a is None or b is None: return a is None and b is None
    return abs(a - b) < 1e-6 if k == 'depth_m' else str(a).strip().lower() == str(b).strip().lower()

if __name__ == '__main__':
    assert verify(NOTES[0][1]) == [] and verify(NOTES[1][1]), 'verify self-check'
    runs = []
    for k in (1, 2):
        with ThreadPoolExecutor(6) as ex: runs.append(list(ex.map(run, NOTES)))
    rows, S = [], {}
    for i, (note, truth, bad) in enumerate(NOTES):
        rr = [r[i] for r in runs]
        rows.append({'i': i, 'note': note, 'truth': truth, 'planted_crew_error': bad, 'truth_verify': verify(truth),
                     'runs': [{'rec': r, 'wrong': [k for k in F if not same(k, r[k], truth[k])],
                               'invented': [k for k in F if truth[k] is None and r[k] is not None], 'verify': verify(r)} for r in rr]})
    for j in (0, 1):
        R = [r['runs'][j] for r in rows]
        S[f'run{j+1}'] = {'fields_exact': sum(len(F) - len(x['wrong']) for x in R), 'fields_total': len(F) * len(R),
                          'records_all_fields_exact': sum(not x['wrong'] for x in R),
                          'invented_values': sum(len(x['invented']) for x in R),
                          'refused': sum(bool(x['verify']) for x in R),
                          'planted_refused': sum(bool(x['verify']) for x, r in zip(R, rows) if r['planted_crew_error']),
                          'good_refused': sum(bool(x['verify']) for x, r in zip(R, rows) if not r['planted_crew_error']),
                          'refused_model_misreads': sum(bool(x['verify']) and bool(x['wrong']) for x, r in zip(R, rows) if not r['planted_crew_error']),
                          'refused_but_fully_correct_good': sum(bool(x['verify']) and not x['wrong'] for x, r in zip(R, rows) if not r['planted_crew_error']),
                          'accepted_with_wrong_field': sum(not x['verify'] and bool(x['wrong']) for x in R)}
    S['records_identical_k2'] = sum(r['runs'][0]['rec'] == r['runs'][1]['rec'] for r in rows)
    S['planted'] = sum(r['planted_crew_error'] for r in rows)
    S['truth_verify_refuses_planted'] = sum(bool(r['truth_verify']) for r in rows if r['planted_crew_error'])
    S['truth_verify_refuses_good'] = sum(bool(r['truth_verify']) for r in rows if not r['planted_crew_error'])
    S['usd_pack_total'] = round(em.spent(PACK), 4)
    json.dump({'model': MODEL, 'summary': S, 'rows': rows}, open('results.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(S, indent=1))
    for r in rows: print(r['i'], 'BAD' if r['planted_crew_error'] else 'ok ', [x['wrong'] for x in r['runs']], [x['invented'] for x in r['runs']], r['runs'][0]['verify'])
