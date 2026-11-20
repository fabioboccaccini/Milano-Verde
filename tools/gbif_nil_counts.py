"""Conteggi GBIF delle occorrenze animali per NIL, salvati in data/gbif_nil.json.

La pagina legge questo file invece di interrogare GBIF 88 volte a ogni visita
(GBIF risponde 429 a raffiche del genere). Da rilanciare ogni tanto:

    python3 tools/gbif_nil_counts.py

Richieste in sequenza, con una pausa tra l'una e l'altra e nuovi tentativi
se GBIF chiede di rallentare.
"""
import datetime, json, os, sys, time, urllib.parse, urllib.request

NIL_URL = 'https://dati.comune.milano.it/dataset/e8e765fc-d882-40b8-95d8-16ff3d39eb7c/resource/9c4e0776-56fc-4f3d-8a90-f4992a3be426/download/ds964_nil_wm.geojson'
GBIF = 'https://api.gbif.org/v1/occurrence/search'
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'gbif_nil.json')
UA = {'User-Agent': 'milano-verde/1.0 (script per i conteggi per quartiere)'}
MAX_PTS = 120   # punti del poligono semplificato: tiene corto l'URL
PAUSA = 1.0     # secondi tra una richiesta e l'altra


def get_json(url, tries=6):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and k < tries - 1:
                attesa = 5 * 2 ** k
                print(f'  HTTP {e.code}, riprovo tra {attesa} s', file=sys.stderr)
                time.sleep(attesa)
                continue
            raise


def ring_area(r):  # stessa formula della pagina: positiva = verso antiorario
    a = 0.0
    for i in range(len(r)):
        j = i - 1
        a += (r[j][0] - r[i][0]) * (r[j][1] + r[i][1])
    return a / 2


def _dp(pts, tol):
    """Douglas-Peucker: tiene i punti che descrivono la forma."""
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0][:2], pts[-1][:2]
    dx, dy = x2 - x1, y2 - y1
    den = (dx * dx + dy * dy) ** 0.5 or 1e-12
    k, dmax = 0, -1.0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / den
        if d > dmax:
            k, dmax = i, d
    if dmax <= tol:
        return [pts[0], pts[-1]]
    return _dp(pts[:k + 1], tol)[:-1] + _dp(pts[k:], tol)


def _cross(a, b, c, d):
    o = lambda p, q, r: (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


def _simple(ring):
    """Vero se l'anello chiuso non si interseca da solo."""
    segs = [(ring[i], ring[i + 1]) for i in range(len(ring) - 1)]
    n = len(segs)
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if _cross(*segs[i], *segs[j]):
                return False
    return True


def wkt_of(geom):
    polys = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']
    ring = [tuple(c[:2]) for c in max((p[0] for p in polys), key=lambda r: abs(ring_area(r)))]
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    tol = 0.0004  # gradi, circa 30-40 m
    while True:
        pts = _dp(ring[:-1], tol) + [ring[0]] if tol else ring
        pts = [tuple(round(v, 5) for v in c) for c in pts]
        if len(pts) <= MAX_PTS and len(pts) >= 4 and _simple(pts):
            break
        tol = tol / 2 if len(pts) <= MAX_PTS else tol * 1.5
        if tol < 1e-6:
            raise ValueError('confine non semplificabile')
    if ring_area(pts) < 0:
        pts = pts[::-1]  # GBIF vuole il verso antiorario
    return 'POLYGON((' + ','.join(f'{c[0]:.5f} {c[1]:.5f}' for c in pts) + '))'


def main():
    nil = get_json(NIL_URL)
    counts, n = {}, len(nil['features'])
    for k, f in enumerate(nil['features'], 1):
        nid = int(f['properties']['ID_NIL'])
        q = urllib.parse.urlencode({'geometry': wkt_of(f['geometry']), 'kingdomKey': 1, 'hasGeospatialIssue': 'false',
                                    'occurrenceStatus': 'PRESENT', 'limit': 0})
        counts[str(nid)] = get_json(GBIF + '?' + q)['count']
        print(f'{k}/{n} NIL {nid} {f["properties"]["NIL"]}: {counts[str(nid)]}')
        time.sleep(PAUSA)
    out = {'updated': datetime.date.today().isoformat(), 'source': 'GBIF.org, occurrence search, kingdomKey=1 (Animalia)',
           'total': sum(counts.values()), 'counts': counts}
    with open(OUT, 'w') as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(',', ':'))
    print('scritto', os.path.normpath(OUT), 'totale', out['total'])


if __name__ == '__main__':
    main()
