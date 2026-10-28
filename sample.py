"""Pick 25 real numbered hydrants (Wasserversorgung Stadt Zuerich, CC0) and the nearest real building address (Adressen Stadt Zuerich, CC0)."""
import gzip, json, random, math
H = [x['properties'] for x in json.load(open('data/hydranten.geojson'))['features'] if x['properties']['oberflur_nummer']]
A = [x['properties'] for x in json.load(gzip.open('data/adressen.geojson.gz'))['features'] if x['properties']['status_txt'] == 'real']
random.seed(28)
out = []
for h in random.sample(H, 60):
    a = min(A, key=lambda a: (a['hausnummer_koord_ost'] - h['xkoord'])**2 + (a['hausnummer_koord_nord'] - h['ykoord'])**2)
    d = math.dist((a['hausnummer_koord_ost'], a['hausnummer_koord_nord']), (h['xkoord'], h['ykoord']))
    if d < 40 and a['hausnummer']:
        out.append({'hydrant_nr': h['oberflur_nummer'], 'hydrant_type': h['art_txt'], 'arms': h['subart_txt'], 'owner': h['eigentuemer_txt'],
                    'install_year': h['verlegejahr'], 'street': a['lokalisationsname'], 'house_number': a['hausnummer'], 'plz': int(a['plz']),
                    'egid': a['gwr_egid'], 'dist_m': round(d, 1)})
    if len(out) == 25: break
json.dump(out, open('data/real_sample.json', 'w'), indent=1, ensure_ascii=False)
for o in out: print(o)
