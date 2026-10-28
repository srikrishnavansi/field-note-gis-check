# field-note-gis-check

A crew member at a trench says something like "Hoi, Gfellstrasse 2, 8002. Hydrant zwei drei acht vier, Oberflur, Tiefi öppe 1 Meter 20". Can a model turn that into a correct GIS record? And can plain code catch it when the record is wrong?

Real data: the City of Zürich's open hydrant register (6,973 hydrants) and address register (59,377 addresses), both CC0 from data.stadt-zuerich.ch, in `data/`. `sample.py` picks 25 real hydrants with their nearest real address.

Scripted by me: the 25 notes in `notes.py` (Swiss German, German and English mixed, some numbers spoken), with 6 planted crew slips (swapped digits, wrong house numbers).

`extract.py` has Claude Haiku 5.5 write a 10-field record per note, twice. Then `verify()` refuses a record unless the hydrant exists, the address exists, the two are within 60 m of each other, and any stated year matches the register.

- 246 of 250 fields exact, in both runs. The two runs gave identical records.
- 1 invented value: "Hydrant 2012" read as an install year.
- verify refused all 8 bad records (the 6 planted slips plus 2 model misreads), refused 0 of the 17 correct ones, and let through 0 records with a wrong field.
- The catch I like: "drei fünf neun drei" became 3539. That is a real hydrant, but it is 3.4 km from that address. A schema check would have passed it.

Limits: typed notes, not audio, and no photos. I wrote the notes. Cost $0.016.

```
pip install anthropic
python sample.py
ANTHROPIC_API_KEY=... python extract.py
```
