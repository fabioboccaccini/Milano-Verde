"""Voce di Wikipedia, foto e licenza per ogni specie del censimento: scrive data/wiki.json.

La pagina legge questo file quando apre il popup di un albero, invece di interrogare Wikipedia
a ogni tocco. Da rilanciare se cambia il censimento (circa 15 minuti, una richiesta al secondo):

    python3 tools/wiki_species.py

Per ogni specie prova, nell'ordine: la Wikipedia italiana con il nome scientifico (ibridi con ×,
qualche sinonimo noto), poi la voce del genere, poi la Wikipedia inglese. Tiene solo foto di
Wikimedia Commons (licenze libere) e ne salva autore e licenza per la citazione.
"""
import csv, datetime, html, io, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, zipfile

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'data', 'alberi.zip')
OUT = os.path.join(ROOT, 'data', 'wiki.json')
UA = {'User-Agent': 'linfami/1.0 (https://github.com/nashkaze/linfami)'}
PAUSA = 1.0
# nomi del censimento che Wikipedia conosce sotto un altro titolo
SINONIMI = {
    'Platanus hybrida': 'Platanus × hispanica',
    'Platanus × acerifolia': 'Platanus × hispanica',
    'Platanus acerifolia': 'Platanus × hispanica',
}


def get_json(url, tries=6):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and k < tries - 1:
                attesa = int(e.headers.get('Retry-After') or 0) or 5 * 2 ** k
                print(f'  HTTP {e.code}, attendo {attesa} s', file=sys.stderr)
                time.sleep(attesa)
                continue
            return None
        except Exception:
            time.sleep(3)
    return None


# --- stessa normalizzazione dei nomi usata dalla pagina (addTree in c_core.js) ---
def clean_genus(s):
    s = re.sub(r'^x\s+', '', (s or '').strip(), flags=re.I)
    s = re.split(r'[\s(]', s)[0] if s else ''
    s = re.sub(r'[^A-Za-zÀ-ÿ\-]', '', s)
    return s[:1].upper() + s[1:].lower() if len(s) > 1 else ''


def species_key(genus, species):
    G, S = clean_genus(genus), (species or '').strip()
    if not G and S:
        G, S = clean_genus(S), ' '.join(S.split()[1:])
    if G and S.lower().startswith(G.lower() + ' '):
        S = S[len(G) + 1:]
    S = re.sub(r'\s+', ' ', S).lower()
    if re.fullmatch(r'(sp\.?|spp\.?|n\.?d\.?|-)', S):
        S = ''
    if not G:
        return None, None
    return (G + ' ' + S if S else G), G


def candidates(key, genus):
    out = []
    name = key.replace(' x ', ' × ')
    name = re.sub(r'^(\S+) x(\S)', r'\1 × \2', name)
    for n in (SINONIMI.get(key), SINONIMI.get(name), name, ' '.join(name.split()[:3]) if '×' in name else ' '.join(name.split()[:2])):
        if n and n not in out:
            out.append(n)
    return out


def summary(lang, title):
    d = get_json(f'https://{lang}.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(title.replace(' ', '_')))
    time.sleep(PAUSA)
    if not d or d.get('type') != 'standard':
        return None
    return d


def licenza(thumb):
    """Autore e licenza della foto da Wikimedia Commons; None se la foto non è su Commons."""
    m = re.search(r'/wikipedia/commons/thumb/[0-9a-f]/[0-9a-f]{2}/([^/]+)/', thumb) or re.search(r'/wikipedia/commons/[0-9a-f]/[0-9a-f]{2}/([^/]+)$', thumb)
    if not m:
        return None
    fname = urllib.parse.unquote(m.group(1))
    d = get_json('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=extmetadata&titles=' + urllib.parse.quote('File:' + fname))
    time.sleep(PAUSA)
    try:
        page = next(iter(d['query']['pages'].values()))
        md = page['imageinfo'][0]['extmetadata']
    except Exception:
        return None
    txt = lambda k: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', (md.get(k) or {}).get('value', '')))).strip()
    return {'a': autore(txt('Artist')), 'l': txt('LicenseShortName') or 'vedi Commons',
            'f': 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote('File:' + fname.replace(' ', '_'))}


def prima_frase(x):
    """Prima frase della voce, senza fermarsi alle abbreviazioni dei nomi (Mill., L., ex.): almeno 60 caratteri."""
    x = re.sub(r'\s+', ' ', x).strip()
    for m in re.finditer(r'\. (?=[A-ZÀ-Ý])', x):
        if m.start() >= 60:
            return x[:m.start() + 1]
    return x


def autore(a):
    m = re.search(r'No machine-readable author provided\. (.+?) assumed', a)
    a = m.group(1) if m else a
    a = re.sub(r'^(Photo by|Foto di|Own work by)\s+', '', a, flags=re.I)
    a = re.sub(r'\buser:', '', a, flags=re.I)
    a = re.sub(r'\s*\[\d+\]', '', a)
    return a.strip()[:80] or 'autore sconosciuto'


def scheda(d, lang, livello):
    frase = prima_frase(d.get('extract') or '')
    if len(frase) > 260:
        frase = frase[:257].rsplit(' ', 1)[0] + '…'
    s = {'t': d['title'], 'u': d['content_urls']['desktop']['page'], 'x': frase, 'lang': lang, 'liv': livello}
    th = (d.get('thumbnail') or {}).get('source')
    if th:
        lic = licenza(th)
        if lic:
            s.update({'i': th, **lic})
    return s


def main():
    with zipfile.ZipFile(SRC) as z:
        rows = csv.DictReader(io.TextIOWrapper(z.open('alberi.csv'), encoding='utf-8'))
        keys = {}
        for r in rows:
            k, g = species_key(r['genere'], r['specie'])
            if k:
                keys[k] = g
    print(len(keys), 'nomi distinti nel censimento')
    out, generi = {}, {}
    for n, (key, genus) in enumerate(sorted(keys.items()), 1):
        found = None
        if key != genus:
            for lang in ('it', 'en'):
                for c in candidates(key, genus):
                    d = summary(lang, c)
                    if d:
                        found = scheda(d, lang, 'specie'); break
                if found:
                    break
        if not found:
            if genus not in generi:
                g = None
                for lang, titolo in (('it', genus), ('it', genus + ' (botanica)'), ('en', genus), ('en', genus + ' (plant)')):
                    d = summary(lang, titolo)
                    if d:
                        g = scheda(d, lang, 'genere'); break
                generi[genus] = g
            found = generi[genus]
        if found:
            out[key] = found
        print(f'{n}/{len(keys)} {key}: ' + (f"{found['lang']} {found['liv']} «{found['t']}»" + (' + foto' if found.get('i') else '') if found else 'niente'))
    for g, s in generi.items():
        if s and g not in out:
            out[g] = s
    json.dump({'updated': datetime.date.today().isoformat(), 'species': out}, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('scritto', os.path.normpath(OUT), len(out), 'voci')


if __name__ == '__main__':
    main()
