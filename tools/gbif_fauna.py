"""Punti di fauna da GBIF (eBird e i maggiori dataset non iNaturalist) salvati in data/gbif_fauna.json.

GBIF non comprime le risposte: 300 record pesano circa 1,5 MB, troppo per chiederli a ogni visita da
telefono. I dataset coinvolti (eBird su GBIF, atlanti degli uccelli) si aggiornano solo periodicamente,
quindi una copia compatta rigenerata ogni tanto non perde freschezza:

    python3 tools/gbif_fauna.py
"""
import datetime, json, os, sys, time, urllib.parse, urllib.request

GBIF = 'https://api.gbif.org/v1/occurrence/search'
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'gbif_fauna.json')
UA = {'User-Agent': 'fogliami/1.0 (https://github.com/nashkaze/fogliami)'}
BBOX = {'s': 45.386, 'w': 9.04, 'n': 45.536, 'e': 9.28}   # come CFG.bbox
INAT = '50c9509d-22c7-4a22-a47d-8c48425ef4a7'
EBIRD = '4fa7b334-ce0d-4e88-aaae-2e0c138d049e'
EBIRD_PAGINE, EBIRD_ANNI = 10, 3      # fino a 3.000 osservazioni eBird degli ultimi 3 anni
ALTRI, ALTRI_PAGINE = 2, 2            # i 2 maggiori dataset dopo iNaturalist ed eBird, 600 record ciascuno
GEO = {'decimalLatitude': f"{BBOX['s']},{BBOX['n']}", 'decimalLongitude': f"{BBOX['w']},{BBOX['e']}", 'kingdomKey': 1,
       'hasCoordinate': 'true', 'hasGeospatialIssue': 'false', 'occurrenceStatus': 'PRESENT'}


def get(params, tries=5):
    url = GBIF + '?' + urllib.parse.urlencode({**GEO, **params})
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if k == tries - 1:
                raise
            time.sleep(5 * 2 ** k)


def lic(u):
    u = (u or '').replace('http://', 'https://')
    for pre in ('https://creativecommons.org/licenses/', 'https://creativecommons.org/publicdomain/'):
        if u.startswith(pre):
            return 'CC ' + u[len(pre):].replace('/legalcode', '').strip('/').replace('/', ' ').upper()
    return u.upper()


def main():
    fc = get({'limit': 0, 'facet': 'datasetKey', 'facetLimit': 8})
    altri = [c['name'] for c in fc['facets'][0]['counts'] if c['name'] not in (INAT, EBIRD)][:ALTRI]
    y = datetime.date.today().year
    richieste = [({'datasetKey': EBIRD, 'year': f'{y - EBIRD_ANNI},{y}', 'offset': i * 300}, 'ebird') for i in range(EBIRD_PAGINE)]
    richieste += [({'datasetKey': d, 'offset': i * 300}, 'gbif') for d in altri for i in range(ALTRI_PAGINE)]
    dataset, recs, visti = {}, [], set()
    for params, fonte in richieste:
        js = get({**params, 'limit': 300}); time.sleep(0.5)
        for r in js.get('results', []):
            if r['key'] in visti or (r.get('coordinateUncertaintyInMeters') or 0) > 1000:
                continue
            visti.add(r['key'])
            dk = r.get('datasetKey', '')
            if dk not in dataset:
                dataset[dk] = len(dataset)
            recs.append([round(r['decimalLongitude'], 5), round(r['decimalLatitude'], 5), fonte, r.get('class') or '',
                         r.get('vernacularName') or '', r.get('species') or r.get('scientificName') or '',
                         (r.get('eventDate') or '')[:10], r['key'], (r.get('recordedBy') or '')[:60], lic(r.get('license')), dataset[dk]])
        print(fonte, params.get('datasetKey', '')[:8], params.get('offset'), '->', len(recs))
    nomi = {}
    for dk in dataset:
        try:
            with urllib.request.urlopen(urllib.request.Request('https://api.gbif.org/v1/dataset/' + dk, headers=UA), timeout=30) as r:
                nomi[dk] = json.load(r)['title']
        except Exception:
            nomi[dk] = dk
    # nomi comuni in italiano da iNaturalist (GBIF li dà quasi sempre in inglese), una richiesta al secondo
    nomi_it = {}
    for sp in sorted({r[5] for r in recs if r[5]}):
        try:
            u = 'https://api.inaturalist.org/v1/taxa?' + urllib.parse.urlencode({'q': sp, 'locale': 'it', 'per_page': 1, 'is_active': 'true'})
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                res = json.load(r).get('results') or []
            if res and res[0].get('name', '').lower() == sp.lower() and res[0].get('preferred_common_name'):
                nomi_it[sp] = res[0]['preferred_common_name']
        except Exception:
            pass
        time.sleep(1.0)
    print(len(nomi_it), 'nomi italiani')
    out = {'updated': datetime.date.today().isoformat(), 'totale_riquadro': fc['count'], 'nomi_it': nomi_it,
           'campi': ['lon', 'lat', 'fonte', 'classe', 'nome', 'specie', 'data', 'gbif', 'osservatore', 'licenza', 'dataset'],
           'dataset': [nomi[dk] for dk in sorted(dataset, key=dataset.get)], 'rec': recs}
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('scritto', os.path.normpath(OUT), len(recs), 'record,', os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()
