/* =====================================================================
   SPRITE — pixel art originale, generata da codice su canvas 16x16.
   Nessuno sprite proviene da videogiochi esistenti.
   ===================================================================== */
function mkCanvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function hash2(x, y, s) { let h = (Math.imul(x + 11, 374761393) ^ Math.imul(y + 7, 668265263) ^ Math.imul(s + 3, 2246822519)) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }
function ell(x, y, cx, cy, rx, ry) { const dx = (x - cx) / rx, dy = (y - cy) / ry; return dx * dx + dy * dy <= 1; }

const SHAPES = {
  round:  (x, y) => ell(x, y, 7.5, 6.5, 6.6, 5.7),
  wide:   (x, y) => ell(x, y, 7.5, 6.2, 7.6, 4.7),
  oval:   (x, y) => ell(x, y, 7.5, 6.5, 5.1, 6.5),
  column: (x, y) => ell(x, y, 7.5, 7, 3.2, 7.3),
  cone:   (x, y) => y >= 0 && y <= 12 && Math.abs(x - 7.5) <= [0.5, 1, 1.5, 2.5, 2, 3, 4, 3.5, 4.5, 5.5, 5, 6, 6.5][y],
  vase:   (x, y) => y >= 0 && y <= 11 && Math.abs(x - 7.5) <= (y < 3 ? 4.5 + y : y < 7 ? 7.4 : 7.4 - (y - 6) * 1.35),
  cloud:  (x, y) => ell(x, y, 4.4, 6.6, 4.3, 4.2) || ell(x, y, 10.6, 6.6, 4.3, 4.2) || ell(x, y, 7.5, 4.4, 4.7, 4.3) || ell(x, y, 7.5, 8.2, 5, 3.3),
  weep:   (x, y) => ell(x, y, 7.5, 5.2, 6.9, 4.9) || (y >= 6 && y <= 9 + (x * 7) % 4 && (x === 1 || x === 3 || x === 5 || x === 10 || x === 12 || x === 14)),
  airy:   (x, y) => ell(x, y, 7.5, 6, 5.7, 5.9) && hash2(x, y, 3) > 0.17,
  big:    (x, y) => ell(x, y, 7.5, 6, 7.9, 6.2)
};

/* Circa una dozzina di generi con sprite dedicato, più conifere e generico */
const TREE_SPR = {
  Platanus:   {shape:'cloud', c:['#2f6b3a','#5a9a45','#a3d268'], trunk:'#b9a47a', patch:'#ece2bd'},
  Tilia:      {shape:'oval',  c:['#1f5c3a','#3a8f4b','#7cc35a'], dots:{c:'#e9e07a',p:.07}},
  Acer:       {shape:'round', c:['#476b23','#7aa836','#c0dc58']},
  Celtis:     {shape:'wide',  c:['#1d4f38','#2f7a4d','#5fae62'], trunk:'#8b8b93'},
  Carpinus:   {shape:'oval',  c:['#24583a','#3f8a52','#86c46c'], trunk:'#6b6b73'},
  Quercus:    {shape:'cloud', c:['#17452f','#2c6e3f','#57a04f'], trunk:'#5c3a22'},
  Prunus:     {shape:'round', c:['#3a6b3a','#5f9e52','#a6d67a'], dots:{c:'#f7b6d2',p:.13}, trunk:'#5a2f2a'},
  Ulmus:      {shape:'vase',  c:['#2a5a2a','#4b8a3c','#8fc45a']},
  Fraxinus:   {shape:'oval',  c:['#356b2f','#63a544','#b0dc6a']},
  Populus:    {shape:'column',c:['#2a6140','#4c9457','#9ad07a'], trunk:'#a9a9a0'},
  Robinia:    {shape:'airy',  c:['#3a6b33','#69a24a','#b3d873'], dots:{c:'#ffffff',p:.06}, trunk:'#4a3626'},
  Aesculus:   {shape:'big',   c:['#184a2f','#2d7a43','#5cab55'], dots:{c:'#fff3d6',p:.07}},
  Betula:     {shape:'airy',  c:['#4a7d33','#7fb548','#c4e86b'], trunk:'#f2ecd8', patch:'#1b1c2e'},
  Magnolia:   {shape:'round', c:['#1c5136','#2f7d4a','#58a85a'], dots:{c:'#fbe3ee',p:.11}},
  Ginkgo:     {shape:'vase',  c:['#6d7a22','#a8b83a','#dde36a']},
  Liquidambar:{shape:'oval',  c:['#7a3b24','#b5552c','#e8853a']},
  Salix:      {shape:'weep',  c:['#3d6b2c','#74a83f','#b9dc6a']},
  Conifera:   {shape:'cone',  c:['#123b3a','#1f6157','#3f8f78'], trunk:'#5c3a22'},
  Cipresso:   {shape:'column',c:['#0f3330','#1b544b','#337a68'], trunk:'#5c3a22'},
  generic:    {shape:'round', c:['#2a5d44','#4a8a5f','#86bf86']}
};
const SPR_ALIAS = {Pinus:'Conifera',Cedrus:'Conifera',Picea:'Conifera',Abies:'Conifera',Taxus:'Conifera',Thuja:'Conifera',Sequoia:'Conifera',
  Sequoiadendron:'Conifera',Metasequoia:'Conifera',Taxodium:'Conifera',Chamaecyparis:'Conifera',Calocedrus:'Conifera',Cryptomeria:'Conifera',Larix:'Conifera',
  Cupressus:'Cipresso',Cupressocyparis:'Cipresso',Juniperus:'Cipresso',Ostrya:'Carpinus',Sophora:'Robinia',Styphnolobium:'Robinia',Gleditsia:'Robinia',
  Malus:'Prunus',Pyrus:'Prunus',Zelkova:'Ulmus',Fagus:'Quercus'};
function sprKey(genus) { return TREE_SPR[genus] ? genus : (SPR_ALIAS[genus] || 'generic'); }

function drawTreeSprite(def, opt) {
  opt = opt || {};
  const c = mkCanvas(16, 16), g = c.getContext('2d'), m = SHAPES[def.shape];
  const px = (x, y, col) => { g.fillStyle = col; g.fillRect(x, y, 1, 1); };
  let bottom = 0;
  for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) if (m(x, y)) bottom = Math.max(bottom, y);
  const tk = def.trunk || PAL.brown;
  for (let y = Math.max(0, bottom - 2); y < 16; y++) {
    px(7, y, tk); px(8, y, tk);
    g.fillStyle = 'rgba(27,28,46,.35)'; g.fillRect(8, y, 1, 1);
    if (def.patch && hash2(7, y, 5) > 0.45) px(7, y, def.patch);
  }
  px(6, 15, PAL.ink); px(9, 15, PAL.ink);
  const out = opt.outline || '#12301f';
  for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) {
    if (!m(x, y)) continue;
    const edge = !m(x - 1, y) || !m(x + 1, y) || !m(x, y - 1) || !m(x, y + 1);
    const t = (x - 7.5) * 0.6 + (y - 6) * 0.9 + (hash2(x, y, 1) - 0.5) * 3;
    let col = edge ? out : t < -2.4 ? def.c[2] : t > 3 ? def.c[0] : def.c[1];
    if (!edge && def.dots && !opt.bloom && hash2(x, y, 7) < def.dots.p) col = def.dots.c;
    if (!edge && opt.bloom && hash2(x, y, 9) < (opt.showy ? 0.38 : 0.2)) col = opt.bloom;
    px(x, y, col);
  }
  return c;
}
// alone colorato (modalità allergie) intorno a uno sprite
function withHalo(src, color) {
  const c = mkCanvas(18, 18), g = c.getContext('2d'), tmp = mkCanvas(16, 16), t = tmp.getContext('2d');
  t.drawImage(src, 0, 0); t.globalCompositeOperation = 'source-in'; t.fillStyle = color; t.fillRect(0, 0, 16, 16);
  for (const [dx, dy] of [[0,1],[2,1],[1,0],[1,2],[0,0],[2,0],[0,2],[2,2]]) g.drawImage(tmp, dx, dy);
  g.drawImage(src, 1, 1);
  return c;
}
const _sprCache = new Map();
function treeSprite(genus, variant, color, showy) {
  const k = sprKey(genus), key = k + '|' + variant + '|' + (color || '') + '|' + (showy ? 1 : 0);
  let s = _sprCache.get(key);
  if (!s) {
    const def = TREE_SPR[k];
    if (variant === 'bloom') s = drawTreeSprite(def, {bloom: color, showy});
    else if (variant === 'halo') s = withHalo(drawTreeSprite(def), color);
    else s = drawTreeSprite(def);
    _sprCache.set(key, s);
  }
  return s;
}
function genusColor(genus) { return TREE_SPR[sprKey(genus)].c[1]; }

/* Sprite da mappa di caratteri */
function fromMap(rows, pal, mirror) {
  const h = rows.length, w = mirror ? rows[0].length * 2 : rows[0].length, c = mkCanvas(w, h), g = c.getContext('2d');
  rows.forEach((r, y) => { for (let x = 0; x < r.length; x++) { const col = pal[r[x]]; if (!col) continue; g.fillStyle = col; g.fillRect(x, y, 1, 1); if (mirror) g.fillRect(w - 1 - x, y, 1, 1); } });
  return c;
}
const K = PAL.ink;
const SPR = {};
function buildSprites() {
  SPR.uccelli = fromMap([
    '................','................','.....kkkk.......','....kbbbbk......','...kbbwebbkoo...','...kbbbbbbkk....',
    '..kkbbbbwwk.....','.kddkbbwwwwk....','kddddkwwwwwk....','.kkdddkwwwk.....','...kkddkkk......','.....kkk.k......',
    '......o..o......','.....oo.oo......','................','................'], {k:K,b:PAL.water,d:'#2c5f96',w:PAL.white,e:K,o:PAL.orange});
  SPR.insetti = fromMap([
    '........','........','.kk.....','kook....','koook..k','koyook.k','koooookk','.koooykk','..kkkkkk','.kppppkk','kppyppkk','kppppk.k','.kppk..k','..kk....','........','........'],
    {k:K,o:PAL.orange,y:PAL.sun,p:'#e0b040'}, true);
  SPR.rettili = fromMap([
    '........','........','........','..kkk...','.kwwkk..','.kwekgkk','.kkkgggg','kggggggg','kgggggll','kgggglll','.kggglll','kkgkkggg','kggk.kkk','.kk.....','........','........'],
    {k:K,g:PAL.leaf2,l:PAL.lime,w:PAL.white,e:K}, true);
  SPR.mammiferi = fromMap([
    '................','................','................','.....k.k.k.k....','....kbkbkbkbk...','...kbbdbbdbbbk..','..kbbbbbbbbbdk..',
    '.kkbbdbbbdbbbbk.','ksskkbbbbbbbdbk.','kessskbbdbbbbbk.','.kssssbbbbbbbk..','..kkskkkkkskk...','....kk....kk....','................','................','................'],
    {k:K,b:PAL.brown,d:'#4d2f1b',s:PAL.sand,e:K});
  SPR.altro = fromMap([
    '................','................','................','................','.......kkkk.....','......kvvvvk....','.....kvvkkvvk...',
    '.k.k.kvkvvkvk...','.k.k.kvkkvvvk...','.kkk.kvvvvvk....','kyyykkkkkkyk....','kyyyyyyyyyyyk...','.kkkkkkkkkkk....','................','................','................'],
    {k:K,v:PAL.violet,y:PAL.sand});
  SPR.orto = fromMap([
    '................','.....g...g......','......g.gg......','.....ggggg......','......ggg.......','.....kkkkk......','....kooooook....',
    '....koooyook....','.....koooook....','.....koyook.....','......koook.....','......kook......','.......kok......','.......kk.......','................','................'],
    {k:K,o:PAL.orange,y:PAL.sun,g:PAL.leaf2});
  SPR.giardino = fromMap([
    '................','.....kk..kk.....','....kppkkppk....','...kppppppppk...','...kppyyyyppk...','....kpyooypk....','...kppyyyyppk...',
    '...kppppppppk...','....kppkkppk....','.....kkggkk.....','..kk...gg.......','.kllk..gg..kk...','..kllk.gg.kllk..','...kkkgggkllk...','.....kggggkk....','......kkkk......'],
    {k:K,p:PAL.pink,y:PAL.sun,o:PAL.orange,g:PAL.leaf2,l:PAL.leaf3});
  SPR.glicine = fromMap([
    '................','.bbbbbbbbbbbbbb.','kggvggvggvggvggk','kvvvgvvvgvvvgvvk','.kvpvkvpvkvpvkk.','.bvpv.vpv.vpv.b.','.b.vp.kvp.kvp.b.',
    '.b.pv..pv..pv.b.','.b..v..vp..v..b.','.b..p...v..p..b.','.b......p.....b.','.b............b.','.b............b.','.b............b.','kbk..........kbk','................'],
    {k:K,b:PAL.brown,g:PAL.leaf2,v:PAL.violet,p:'#c9a8f0'});
  // albero monumentale: chioma grande, contorno dorato e stella
  const mon = drawTreeSprite({shape:'big', c:['#17452f','#2c6e3f','#6ab85a'], trunk:'#5c3a22'}, {outline:'#8a6a12'});
  const mg = mon.getContext('2d');
  ['..y..','.yyy.','yyyyy','.yyy.','..y..'].forEach((r, y) => { for (let x = 0; x < 5; x++) if (r[x] === 'y') { mg.fillStyle = (x === 2 && y === 2) ? '#fff7c2' : PAL.sun; mg.fillRect(11 + x, y, 1, 1); } });
  SPR.monum = withHalo(mon, PAL.sun);
  SPR.parco = fromMap([
    '................','................','....kkk....kkk..','...kgggk..kgggk.','..kglgggkkglgggk','..kgggggkkgggggk','...kgggk..kgggk.','....kbk....kbk..',
    '....kbk....kbk..','kkkkkbkkkkkkbkkk','kllllllllllllllk','klglllglllglllgk','kllllllllllllllk','kkkkkkkkkkkkkkkk','................','................'],
    {k:K,g:PAL.leaf2,l:PAL.leaf3,b:PAL.brown});
  SPR.nil = fromMap([
    '................','.kkkkkk.kkkkkk..','.k....k.k....k..','.k....kkk....kk.','.k...........k..','.kk..........k..','..k.........kk..','..k.........k...',
    '.kk....kkk..k...','.k.....k.k..kk..','.k....kk.k...k..','.kkkkkk..kkkkk..','................','................','................','................'], {k:K});
  SPR.calore = fromMap([
    '................','.......kk.......','......krrk......','......krrk......','.....krrork.....','.....kroork.....','....kroooork....','....kroyyork....',
    '...krooyyoork...','...kroyyyyork...','...kroyyyyork...','....kroyyork....','.....kkkkkk.....','................','................','................'],
    {k:K,r:PAL.red,o:PAL.orange,y:PAL.sun});
}
function sprURL(c, scale) { const s = scale || 2, o = mkCanvas(c.width * s, c.height * s), g = o.getContext('2d'); g.imageSmoothingEnabled = false; g.drawImage(c, 0, 0, o.width, o.height); return o.toDataURL(); }
function sprIcon(c, px, cls) { return L.divIcon({className: 'spr-ico' + (cls ? ' ' + cls : ''), iconSize: [px, px], iconAnchor: [px / 2, px - 2], popupAnchor: [0, -px + 6], html: '<img class="pix" width="' + px + '" height="' + px + '" src="' + sprURL(c, 2) + '" alt="">'}); }

/* ---------------------------------------------------------------------
   Schermata di caricamento: una pianta che cresce col caricamento reale
   --------------------------------------------------------------------- */
const FLOWER = ['...ppp.....','..ppppp.pp.','..ppppppppp','.pp.pyyppp.','ppppyyyyp..','pppyyoyyppp','.ppyyyyyppp','..ppyyypp..','.ppppppppp.','.ppp.pppp..','.....ppp...'];
function drawPlant(g, p, t) {
  const W = 48, H = 56, px = (x, y, c, w, h) => { g.fillStyle = c; g.fillRect(x, y, w || 1, h || 1); };
  g.clearRect(0, 0, W, H);
  // terreno
  px(6, 47, '#4d2f1b', 36, 9); px(8, 46, PAL.brown, 32, 2); px(6, 48, PAL.brown, 36, 3);
  for (let i = 0; i < 26; i++) px(7 + Math.floor(hash2(i, 1, 2) * 34), 49 + Math.floor(hash2(i, 2, 2) * 6), i % 3 ? '#3a2314' : '#9a6a40');
  px(10, 46, PAL.leaf2, 3, 1); px(34, 46, PAL.leaf2, 4, 1); px(20, 46, PAL.leaf3, 2, 1);
  if (p < 0.06) { px(23, 44, PAL.sand, 2, 2); px(23, 45, '#b89a5a', 2, 1); return; }
  const stem = Math.round(Math.min(1, (p - 0.04) / 0.72) * 28);
  for (let i = 0; i < stem; i++) { const y = 45 - i, sx = 23 + ((i > 9 && i < 17) ? 1 : 0); px(sx, y, PAL.leaf2); px(sx + 1, y, PAL.leaf1); }
  const leaf = (y, dir, size) => {
    const sx = 23 + ((45 - y > 9 && 45 - y < 17) ? 1 : 0);
    for (let i = 1; i <= size; i++) {
      const x = dir > 0 ? sx + 1 + i : sx - i, hgt = i < size ? (i === 1 ? 1 : 2) : 1;
      px(x, y - Math.min(i, 2), i % 2 ? PAL.leaf3 : PAL.leaf2, 1, hgt + 1);
    }
    px(dir > 0 ? sx + 1 + size : sx - size, y - 2, PAL.lime);
  };
  [[5, 1], [10, -1], [15, 1], [20, -1], [25, 1]].forEach(([at, dir]) => { if (stem >= at) leaf(45 - at, dir, Math.min(6, 2 + Math.floor((stem - at) / 2))); });
  const top = 45 - stem, sx = 23 + ((stem > 9 && stem < 17) ? 1 : 0);
  if (p >= 1) {
    const ox = sx - 5, oy = top - 9;
    FLOWER.forEach((r, y) => { for (let x = 0; x < r.length; x++) { const ch = r[x]; if (ch === '.') continue; px(ox + x, oy + y, ch === 'p' ? ((x + y) % 5 === 0 ? '#fbd0e4' : PAL.pink) : ch === 'y' ? PAL.sun : PAL.orange); } });
    for (let i = 0; i < 6; i++) if (Math.floor(t / 180 + i * 1.7) % 3 === 0) px(6 + Math.floor(hash2(i, 5, Math.floor(t / 540)) * 36), 4 + Math.floor(hash2(i, 6, Math.floor(t / 540)) * 30), i % 2 ? PAL.sun : PAL.white);
  } else if (p > 0.72) {
    const s = p > 0.9 ? 3 : 2;
    px(sx - s + 1, top - 2 * s + 1, PAL.leaf3, 2 * s, 2 * s); px(sx - s + 2, top - 2 * s, PAL.leaf3, 2 * s - 2, 1);
    if (p > 0.84) px(sx - 1, top - 2 * s, PAL.pink, 3, s);
  } else if (stem > 2) { px(sx, top - 1, PAL.lime, 2, 1); }
}
