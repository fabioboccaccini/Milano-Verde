"""Rigenera le copie dei dati del Comune pubblicate nel sito: data/parchi.json e data/nil.geojson.

Il portale a volte serve i NIL senza CORS e manda i parchi non compressi (5 MB): la pagina usa queste
copie. Qui, lato server, il CORS non conta. Se il portale non risponde, le copie restano come sono.

    python3 tools/copie_comune.py
"""
import datetime, json, os, sys, urllib.request

ROOT = os.path.join(os.path.dirname(__file__), '..', 'data')
UA = {'User-Agent': 'fogliami/1.0 (https://github.com/nashkaze/fogliami)'}
CKAN = 'https://dati.comune.milano.it'
FONTI = {  # id del dataset, formato, URL di ripiego (come CFG.pkg in a_tables.js)
    'parchi': ('ds89_infogeo_parchi_giardini_localizzazione_', '/dataset/8920bbea-fe1a-4061-8c6e-0746d95316c1/resource/7cba11e7-c236-49a7-aef4-4db6329eec5d/download/parchi.geojson'),
    'nil': ('ds964-nil-vigenti-pgt-2030', '/dataset/e8e765fc-d882-40b8-95d8-16ff3d39eb7c/resource/9c4e0776-56fc-4f3d-8a90-f4992a3be426/download/ds964_nil_wm.geojson'),
}


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return json.load(r)


def scarica(chiave):
    pid, ripiego = FONTI[chiave]
    url, data = CKAN + ripiego, ''
    try:  # URL e data di aggiornamento correnti dal catalogo
        res = get_json(CKAN + '/api/3/action/package_show?id=' + pid)['result']
        r = next(x for x in res['resources'] if str(x.get('format', '')).lower() == 'geojson')
        url, data = r['url'], (r.get('last_modified') or res.get('metadata_modified') or '')[:10]
    except Exception as e:
        print('catalogo non disponibile per', chiave, '-', e)
    return get_json(url), data


def arrotonda(c, dec):
    if isinstance(c[0], list):
        out = [arrotonda(x, dec) for x in c]
        if out and not isinstance(out[0][0], list):  # anello: via i punti doppi consecutivi
            ded = [out[0]] + [p for a, p in zip(out, out[1:]) if p != a]
            if len(ded) >= 4:
                out = ded
        return out
    return [round(c[0], dec), round(c[1], dec)]


def main():
    esito = 0
    for chiave, nome, dec, campi in (('parchi', 'parchi.json', 5, ['PARCO', 'AREA_MQ', 'PERIM_M', 'ZONA']), ('nil', 'nil.geojson', 6, None)):
        try:
            gj, data = scarica(chiave)
            assert gj.get('features'), 'nessun elemento'
            for f in gj['features']:
                if f.get('geometry'):
                    f['geometry']['coordinates'] = arrotonda(f['geometry']['coordinates'], dec)
                if campi:
                    f['properties'] = {k: f['properties'].get(k) for k in campi}
            gj.pop('crs', None)
            gj['_aggiornato'] = data or datetime.date.today().isoformat()
            json.dump(gj, open(os.path.join(ROOT, nome), 'w'), ensure_ascii=False, separators=(',', ':'))
            print(nome, len(gj['features']), 'elementi, versione del', gj['_aggiornato'])
        except Exception as e:
            print('copia di', chiave, 'non aggiornata:', e); esito = 1
    sys.exit(esito)


if __name__ == '__main__':
    main()
