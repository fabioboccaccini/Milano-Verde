"""Voce di Wikipedia, foto e licenza per le specie animali osservate a Milano: scrive data/wiki_fauna.json.

Elenco delle specie: quelle di data/gbif_fauna.json (eBird e atlanti) più le 500 più osservate su
iNaturalist nel riquadro di Milano. Per ciascuna stesse regole delle piante (tools/wiki_species.py):
Wikipedia italiana, poi il genere, poi l'inglese; solo foto di Wikimedia Commons, con autore e licenza.
Circa 25 minuti, una richiesta al secondo:

    python3 tools/wiki_fauna.py
"""
import datetime, json, os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiki_species import get_json, summary, scheda  # stesse regole e stessa pausa tra le richieste

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
OUT = os.path.join(ROOT, 'wiki_fauna.json')
BBOX = {'s': 45.386, 'w': 9.04, 'n': 45.536, 'e': 9.28}   # come CFG.bbox
ICONIC = 'Aves,Insecta,Mammalia,Reptilia,Amphibia,Arachnida,Mollusca,Actinopterygii'   # come loadInat


def specie_inat():
    q = urllib.parse.urlencode({'nelat': BBOX['n'], 'nelng': BBOX['e'], 'swlat': BBOX['s'], 'swlng': BBOX['w'], 'iconic_taxa': ICONIC,
                                'quality_grade': 'research', 'per_page': 500, 'locale': 'it'})
    js = get_json('https://api.inaturalist.org/v1/observations/species_counts?' + q) or {}
    return [r['taxon']['name'] for r in js.get('results', []) if r.get('taxon', {}).get('name')]


def main():
    nomi = set()
    try:
        nomi |= {r[5] for r in json.load(open(os.path.join(ROOT, 'gbif_fauna.json')))['rec'] if r[5]}
    except Exception as e:
        print('gbif_fauna.json non letto:', e)
    nomi |= set(specie_inat())
    nomi = sorted(n for n in nomi if len(n.split()) >= 2)   # solo specie (e sottospecie), non generi o famiglie
    print(len(nomi), 'specie da cercare')
    out, generi = {}, {}
    for k, sp in enumerate(nomi, 1):
        found = None
        base = ' '.join(sp.split()[:2])   # le sottospecie si cercano come specie
        for lang in ('it', 'en'):
            d = summary(lang, base)
            if d:
                found = scheda(d, lang, 'specie'); break
        if not found:
            g = sp.split()[0]
            if g not in generi:
                gg = None
                for lang, titolo in (('it', g), ('it', g + ' (zoologia)'), ('en', g)):
                    d = summary(lang, titolo)
                    if d:
                        gg = scheda(d, lang, 'genere'); break
                generi[g] = gg
            found = generi[g]
        if found:
            out[base] = found
        print(f"{k}/{len(nomi)} {sp}: " + (f"{found['lang']} {found['liv']} «{found['t']}»" + (' + foto' if found.get('i') else '') if found else 'niente'), flush=True)
    for g, s in generi.items():
        if s and g not in out:
            out[g] = s
    json.dump({'updated': datetime.date.today().isoformat(), 'species': out}, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('scritto', os.path.normpath(OUT), len(out), 'voci')


if __name__ == '__main__':
    main()
