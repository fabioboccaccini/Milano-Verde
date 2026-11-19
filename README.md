# Milano Verde

Mappa interattiva di flora e fauna di Milano in stile pixel art anni '90. Un'unica pagina HTML che legge i dati in diretta dalle fonti aperte: nessun dato è incorporato, tranne le tabelle botaniche scritte a mano (fioriture, allergeni, nomi comuni).

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
| GBIF, conteggi per NIL | Non provati. Se incoerenti si ripiega sul campione di punti |
| eBird | Richiede chiave personale (campo nel pannello) |
| CARTO Basemaps | Da fine agosto 2026 richiede una chiave. Funziona con la chiave in `a_tables.js` |
| Pollini, Landsat | Sezioni predisposte, nessuna fonte integrata |

Catena degli alberi all'avvio: portale del Comune → file salvato nel browser (IndexedDB) → geoportale → OpenStreetMap. Il file ufficiale (`ds2484_alberi_20240331_geojson.zip`, 247.779 alberi) si carica dal pannello Livelli e resta salvato nel browser.

## Problemi aperti e prossimi passi

1. **Lentezza al caricamento.** Ipotesi da verificare: la schermata aspetta gli alberi fino a 14 s e le tre pagine iNaturalist (con pausa di 1 s tra l'una e l'altra). Idee: aprire la mappa appena pronti NIL e parchi, togliere il geoportale dalla catena, una sola pagina iNaturalist all'avvio.
2. **Alberi senza caricamento a mano.** Mettere lo ZIP ufficiale nel repository come `alberi.zip` e aggiungere alla catena la lettura del file accanto alla pagina. Licenza CC BY 4.0, citando il Comune.
3. **Chiave CARTO pubblica.** In un repository pubblico è leggibile: prima di pubblicare, vincolarla al dominio GitHub Pages dal pannello di CARTO. Attenzione: col vincolo attivo, aprire `index.html` come file locale potrebbe non mostrare la mappa di base.
4. **Varianti CARTO.** La pagina usa `light_nolabels` e `light_only_labels`, non documentate con il nuovo schema a chiave. Se mancano, ripiega da sola su `light_all`.
5. **Zoom massimo.** Tasselli limitati al livello 18 e ingranditi oltre: da confermare che CARTO non serva il 19.
6. **Geolocalizzazione.** Funziona solo in https (GitHub Pages). Da provare su telefono vero.
7. **Icone.** I glicini seguono la scala degli alberi. Orti, giardini condivisi e monumentali sono ancora più grandi: decidere se allinearli.
8. **Tabelle botaniche.** Fioriture e allergeni sono approssimazioni scritte a mano per genere, senza fonte verificata.

## Crediti e licenze

Dati © Comune di Milano (CC BY 4.0), iNaturalist e GBIF (licenza per record), OpenStreetMap contributors (ODbL), tasselli © CARTO. Leaflet (BSD-2), Press Start 2P (SIL OFL). Sprite originali generati dal codice.
