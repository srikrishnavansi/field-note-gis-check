"""25 scripted field voice notes (transcribed), one per real hydrant from data/real_sample.json.
Real: hydrant number, street, house number, PLZ, type, install year (Stadt Zuerich open data, CC0).
Scripted by me: the note wording, depth, pipe DN, material, dates, and 6 planted crew mistakes (bad=True).
truth = what the note actually says (null = not said), so extraction is scored against the note."""
F = ['hydrant_nr', 'street', 'house_number', 'plz', 'hydrant_type', 'install_year', 'depth_m', 'pipe_dn', 'pipe_material', 'date']
def T(nr, st, hn, plz, ty=None, yr=None, d=None, dn=None, mat=None, date=None): return dict(zip(F, [nr, st, hn, plz, ty, yr, d, dn, mat, date]))
OF = 'Oberflurhydrant'
NOTES = [
 ("Hoi, Gfellstrasse 2, 8002. Hydrant zwei drei acht vier, Oberflur, Graben isch offe, Tiefi öppe 1 Meter 20, Leitig DN 150 Guss. Fotos chömed.", T('2384', 'Gfellstrasse', '2', 8002, OF, None, 1.2, 150, 'Guss'), False),
 ("Loogartenstrasse 31b in 8048, hydrant number 2754, Oberflur. Depth 1.10, pipe is PE, DN 125. Year on the plate says 2003.", T('2754', 'Loogartenstrasse', '31b', 8048, OF, 2003, 1.1, 125, 'PE'), True),
 ("Frohburgstrasse 200, PLZ 8057. Hydrant 4337. Mir händ de Hausaschluss freigleit, Tiefi 1.45, DN 100 duktil. Erfasst am 27. Oktober 2026.", T('4337', 'Frohburgstrasse', '200', 8057, None, None, 1.45, 100, 'Duktil', '2026-10-27'), False),
 ("Zellerstrasse 52, 8038 Wollishofen, Oberflurhydrant 5174, verlegt 2019. Graben 1.30 tief, Leitung DN 150, Material Guss.", T('5174', 'Zellerstrasse', '52', 8038, OF, 2019, 1.3, 150, 'Guss'), False),
 ("ok recording, Leutschenbachstrasse 75, 8050, Hydrant drei fünf neun drei. Pipe steel, DN 200, trench depth 1.60. thats it.", T('3593', 'Leutschenbachstrasse', '75', 8050, None, None, 1.6, 200, 'Stahl'), False),
 ("In Böden 175, 8046. Hydrant 4460, Überflur. Tiefi eis komma füfzg. Leitig PE DN 110.", T('4460', 'In Böden', '175', 8046, OF, None, 1.5, 110, 'PE'), False),
 ("Meinrad-Lienert-Strasse 4, 8003. Hydrant Nummer 3372, Oberflur, Baujahr 2003. Depth 1.25, DN 150 Guss. Datum 26.10.2026.", T('3372', 'Meinrad-Lienert-Strasse', '4', 8003, OF, 2003, 1.25, 150, 'Guss', '2026-10-26'), False),
 ("Mühlebachstrasse 185, 8008. Hydrant 5789, nagelneu, Oberflur. Tiefi 1.40, DN 125 duktil.", T('5789', 'Mühlebachstrasse', '185', 8008, OF, None, 1.4, 125, 'Duktil'), True),
 ("Riedhofstrasse 86, 8049 Höngg. Hydrant 1581. Leitung Guss DN 100, Graben 1.15 tief. Hydrant is from 1988 according to the plate.", T('1581', 'Riedhofstrasse', '86', 8049, None, 1988, 1.15, 100, 'Guss'), False),
 ("Auhofstrasse 1, 8051, Hydrant 859, Oberflur. Tiefi 1.35. Material weiss ich nöd, DN 150.", T('859', 'Auhofstrasse', '1', 8051, OF, None, 1.35, 150, None), False),
 ("Pflanzschulstrasse 17, 8004, hydrant 4200, Oberflurhydrant, laid 2011. Trench 1.20, PE DN 160. Captured 25 October 2026.", T('4200', 'Pflanzschulstrasse', '17', 8004, OF, 2011, 1.2, 160, 'PE', '2026-10-25'), False),
 ("Kanzleistrasse 411, 8004. Hydrant 4248, Oberflur. Tiefi 1.50, DN 150 Guss.", T('4248', 'Kanzleistrasse', '411', 8004, OF, None, 1.5, 150, 'Guss'), True),
 ("Hohlstrasse 176, 8004. Hydrant füf drei sibe. Leitig Stahl DN 200, Tiefi 1.70. Verlegt 2004.", T('537', 'Hohlstrasse', '176', 8004, None, 2004, 1.7, 200, 'Stahl'), False),
 ("Enzenbühlstrasse 74, 8008, Hydrant 1152, Oberflur. DN 100, Guss, Tiefe 1.05 Meter.", T('1152', 'Enzenbühlstrasse', '74', 8008, OF, None, 1.05, 100, 'Guss'), False),
 ("Entlisbergweg 5, 8041, hydrant 3279. depth 1.30, PE pipe DN 125. date 24.10.2026.", T('3279', 'Entlisbergweg', '5', 8041, None, None, 1.3, 125, 'PE', '2026-10-24'), False),
 ("Feusisbergli 23, 8048. Oberflurhydrant 2749, Baujahr 2003. Graben 1.20, Leitig duktil DN 150.", T('2749', 'Feusisbergli', '23', 8048, OF, 2003, 1.2, 150, 'Duktil'), False),
 ("Birchstrasse 251, 8052, Hydrant 5382, Oberflur. Tiefi 1.55, DN 200 duktil. Verlegt 2020.", T('5382', 'Birchstrasse', '251', 8052, OF, 2020, 1.55, 200, 'Duktil'), True),
 ("Seefeldstrasse 149, 8008. Hydrant 3782, Oberflur. Pipe cast iron, DN 150, depth 1.40.", T('3782', 'Seefeldstrasse', '149', 8008, OF, None, 1.4, 150, 'Guss'), False),
 ("Pfingstweidstrasse 10, 8005. Hydrant vier null füf füf. Leitung PE DN 160, Graben 1.25. Hydrant isch vo 2010.", T('4055', 'Pfingstweidstrasse', '10', 8005, None, 2010, 1.25, 160, 'PE'), False),
 ("Letzistrasse 91, 8006, Hydrant 2012, Oberflur. Tiefi 1.10, Guss DN 100.", T('2012', 'Letzistrasse', '91', 8006, OF, None, 1.1, 100, 'Guss'), True),
 ("Keltenstrasse 28, 8044. Hydrant 2076, Oberflur, 1993. DN 125 Guss, depth 1.35. Erfasst 23.10.2026.", T('2076', 'Keltenstrasse', '28', 8044, OF, 1993, 1.35, 125, 'Guss', '2026-10-23'), False),
 ("Farenweg 9, 8038. Hydrant 4657. Tiefi 1.20, PE DN 110. Fotos vo Muffe und Hausiifüehrig.", T('4657', 'Farenweg', '9', 8038, None, None, 1.2, 110, 'PE'), False),
 ("Tramstrasse 87a, 8050, hydrant 1842, Oberflur, from 1986. Steel DN 150, trench 1.65.", T('1842', 'Tramstrasse', '87a', 8050, OF, 1986, 1.65, 150, 'Stahl'), False),
 ("Zehntenhausstrasse 110, 8046. Hydrant 718, Oberflur. Tiefi 1.30, DN 100 Guss.", T('718', 'Zehntenhausstrasse', '110', 8046, OF, None, 1.3, 100, 'Guss'), True),
 ("Kilchbergstrasse 39, 8038. Hydrant 2435, Oberflurhydrant, verlegt 1999. DN 150 duktil, Tiefi 1.40. Datum 22.10.2026.", T('2435', 'Kilchbergstrasse', '39', 8038, OF, 1999, 1.4, 150, 'Duktil', '2026-10-22'), False),
]
