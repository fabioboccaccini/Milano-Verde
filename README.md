# Milano Verde

Mappa interattiva di flora e fauna di Milano in stile pixel art anni '90. Un'unica pagina HTML che legge i dati in diretta dalle fonti aperte. Fanno eccezione le tabelle botaniche scritte a mano (fioriture, allergeni, nomi comuni) e i file in `data/` (censimento degli alberi, confini dei NIL di riserva, conteggi GBIF per quartiere).

## Struttura

| File | Contenuto |
|---|---|
| `src/a_tables.js` | Configurazione (URL delle fonti, chiave CARTO), palette, tabelle di fioritura e allergeni, nomi comuni |
| `src/b_sprites.js` | Sprite pixel art generati da codice, animazione della schermata di caricamento |
| `src/c_core.js` | Utilità, lettura ZIP/CSV/GeoJSON a flusso, mappa di base, livello sprite su canvas, NIL, archivio alberi e catena delle fonti |
| `src/d_app.js` | Disegno di alberi e fauna, popup, iNaturalist/GBIF/eBird, livelli vettoriali del Comune, KML dei glicini |
| `src/e_ui.js` | Metriche per NIL, coropletica, classifica, incroci, pannello, geolocalizzazione, avvio |
| `src/style.css`, `src/body.html` | Stile e struttura della pagina |
| `build.py` | Concatena tutto in `index.html` |
| `data/nil.geojson` | Copia dei confini dei NIL (ds964, PGT 2030, fermi al 2020), usata se il portale non li serve: a volte li manda senza CORS |
| `data/parchi.json` | Copia dei parchi e giardini (ds89, versione del 06/05/2024) con le sole colonne usate e coordinate al metro: 1,1 MB, 180 KB compressi, contro 5 MB non compressi dal portale. È la prima scelta; il portale è il ripiego. Da rigenerare se il Comune aggiorna il dataset |
| `data/gbif_nil.json` | Conteggi GBIF delle occorrenze animali per NIL, generati da `tools/gbif_nil_counts.py` |
| `tools/gbif_nil_counts.py` | Rigenera `data/gbif_nil.json` (88 richieste in sequenza a GBIF, circa due minuti): da rilanciare ogni tanto |
| `data/alberi.zip` | Censimento degli alberi del Comune (ds2484, 31/03/2024, 247.779 alberi), ridotto alle colonne usate e compresso (2,6 MB) |

Si modifica `src/`, poi si rigenera:

```
python3 build.py          # scrive index.html
python3 build.py v9       # scrive milano-verde-v9.html (copia di lavoro, ignorata da git)
```

Dipendenze esterne caricate da CDN: Leaflet 1.9.4 (con hash di integrità) e il font Press Start 2P.

## Fonti

| Fonte | Stato al 17/11/2026 |
|---|---|
| Comune di Milano: NIL, residenti per NIL (ds27, via SQL sul DataStore), parchi e giardini, orti urbani, giardini condivisi, alberi monumentali, indici di calore e verde per NIL (ds2811, ds2813), aree verdi per tipologia 2014 (ds339) | Funzionano, CORS aperto |
| Comune di Milano: alberi (ds2484) | **Ritirato dal portale** (pagina 404, API 403). La pagina lo cerca a ogni avvio e lo usa se torna |
| Vecchio geoportale ArcGIS (livello Alberi) | Server non raggiungibile. Ancora in catena: candidato alla rimozione |
| OpenStreetMap via Overpass | Ripiego per gli alberi, mai provato dal vivo |
| iNaturalist, GBIF | Formato verificato su risposte reali, flusso completo non provato dal vivo |
| GBIF, conteggi per NIL | Precalcolati in `data/gbif_nil.json`: chiesti dal vivo (88 richieste a visita) GBIF rispondeva 429 e bloccava anche i punti |
| eBird | Richiede chiave personale (campo nel pannello) |
| CARTO Basemaps | Da fine agosto 2026 richiede una chiave. Funziona con la chiave in `a_tables.js` |
| Pollini, Landsat | Sezioni predisposte, nessuna fonte integrata |

Catena degli alberi all'avvio: portale del Comune → copia nel repository (`data/alberi.zip`) → file salvato nel browser (IndexedDB) → geoportale → OpenStreetMap. Un file diverso si può sempre caricare a mano dal pannello Livelli.

## Problemi aperti e prossimi passi

1. **Lentezza al caricamento.** Ipotesi da verificare: la schermata aspetta gli alberi fino a 14 s e le tre pagine iNaturalist (con pausa di 1 s tra l'una e l'altra). Idee: aprire la mappa appena pronti NIL e parchi, togliere il geoportale dalla catena, una sola pagina iNaturalist all'avvio.
2. **Alberi senza caricamento a mano.** Fatto: `data/alberi.zip`, ricavato da `ds2484_alberi_20240331.geojson` (colonne lon, lat, genere, specie, varieta, h_m, diam_tronc, diam_chiom, localita, anno di impianto; coordinate a 6 decimali).
3. **Chiave CARTO pubblica.** Vincolata al dominio `nashkaze.github.io` (verificato: 200 da quel dominio, 403 da altri). Il campo nel pannello è stato tolto. Aprendo `index.html` come file locale la mappa di base non compare.
4. **Varianti CARTO.** La pagina usa `light_nolabels` e `light_only_labels`, non documentate con il nuovo schema a chiave. Se mancano, ripiega da sola su `light_all`.
5. **Zoom massimo.** Tasselli limitati al livello 18 e ingranditi oltre: da confermare che CARTO non serva il 19.
6. **Geolocalizzazione.** Funziona solo in https (GitHub Pages). Da provare su telefono vero.
7. **Icone.** I glicini seguono la scala degli alberi. Orti, giardini condivisi e monumentali sono ancora più grandi: decidere se allinearli.
8. **Tabelle botaniche.** Fioriture e allergeni sono approssimazioni scritte a mano per genere, senza fonte verificata.

## Crediti e licenze

Dati © Comune di Milano (CC BY 4.0), iNaturalist e GBIF (licenza per record), OpenStreetMap contributors (ODbL), tasselli © CARTO. Leaflet (BSD-2), Press Start 2P (SIL OFL). Sprite originali generati dal codice.
