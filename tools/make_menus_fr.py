"""Menus graphiques en français (choix du fichier, nom, sauvegarde, Game Over).

On ne prend PAS les images de la version européenne de Nintendo : les mots français sont
recomposés avec les lettres des menus anglais d'Ages (mêmes traits, même hauteur), les lettres
absentes (B, J, X, Z, accents) sont dessinées ici, et le fond rayé est recousu à partir des
rayures d'origine (colonnes sans texte) pour que rien ne se voie.

Écrit oracles-disasm/gfx_compressible/common/gfx_*_fr.png (+ .properties) ; le jeu les charge
quand wActiveLanguage = 1 (code/bank0.s, balladeLangGfxHeader ; data/ages/gfxHeaders.s).
Aperçu : out/menus_fr.png.
"""
import os
import random

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GFX = os.path.join(ROOT, 'oracles-disasm', 'gfx_compressible', 'common')

# Image anglaise -> segments (première colonne de 8 px, nombre de colonnes, mot anglais, mot
# français). Les images « interleave » sont des bandes de colonnes 8x16 lues ligne après ligne.
# Dans les mots : « _ » = petit espace (4 px), « ^ » = pas d'espace (lettre collée).
IMAGES = [
    ('gfx_pickafile', [(0, 16, 'PICK A FILE', 'QUEL FICHIER^?')]),
    ('gfx_pickafile_2', [(0, 16, 'PICK A FILE', 'QUEL FICHIER^?')]),
    ('gfx_gameover', [(0, 16, 'GAME OVER', 'FIN DE PARTIE')]),
    ('gfx_done', [(0, 16, 'DONE', 'TERMINÉ')]),
    ('gfx_error', [(0, 16, 'ERROR', 'ERREUR')]),
    ('gfx_copywhatwhere', [(0, 16, 'COPY WHAT? WHERE?', 'QUOI^? VERS OÙ^?')]),
    ('gfx_savescreen', [(0, 16, 'SAVE', 'SAUVEGARDE'),
                        (16, 12, 'CONTINUE', 'CONTINUER'),
                        (28, 12, 'SAVE & CONT.', 'SAUV.^&^CONT.'),
                        (40, 12, 'SAVE & QUIT', 'SAUV.^&^QUIT.')]),
    ('gfx_newfilescreen', [(0, 16, 'PICK A FILE', 'QUEL FICHIER^?'),
                           (16, 12, 'NEW GAME', 'COMMENCER'),
                           (28, 12, 'SECRETS', 'SECRETS'),
                           (40, 12, 'GAME LINK', 'LIAISON')]),
    ('gfx_copy', [(0, 5, 'COPY', 'COPIE')]),
    ('gfx_erase', [(0, 5, 'ERASE', 'VIDER')]),
    ('gfx_quit_2', [(0, 5, 'QUIT', 'FIN')]),
    ('gfx_quit', [(0, 5, 'QUIT', 'FIN')]),
    ('gfx_name', [(0, 5, 'NAME', 'NOM')]),
]

# Lettres absentes des menus anglais, dessinées dans le même style (traits de 2 pixels).
# 12 lignes de haut ; la version à 11 lignes enlève la 6e ligne.
DRAWN = {
    'B': ['@@@@@.', '@@@@@@', '@@..@@', '@@..@@', '@@.@@.', '@@@@@.',
          '@@@@@.', '@@.@@.', '@@..@@', '@@..@@', '@@@@@@', '@@@@@.'],
    'J': ['....@@', '....@@', '....@@', '....@@', '....@@', '....@@',
          '....@@', '....@@', '@@..@@', '@@..@@', '@@@@@@', '.@@@@.'],
    'X': ['@@..@@', '@@..@@', '@@..@@', '.@@@@.', '.@@@@.', '..@@..',
          '..@@..', '.@@@@.', '.@@@@.', '@@..@@', '@@..@@', '@@..@@'],
    'Z': ['@@@@@@', '@@@@@@', '....@@', '...@@.', '...@@.', '..@@..',
          '..@@..', '.@@...', '.@@...', '@@....', '@@@@@@', '@@@@@@'],
}
# Accents : une ligne au-dessus de la lettre, séparée par une ligne vide.
ACCENTS = {'É': ('E', '...@@.'), 'È': ('E', '.@@...'), 'Ù': ('U', '.@@...'),
           'À': ('A', '.@@...'), 'Ê': ('E', '.@@@@.')}

GAP = 2      # entre deux lettres
SPACE = 8    # entre deux mots
SMALL = 4    # « _ »


def load(name):
    im = Image.open(os.path.join(GFX, name + '.png'))
    w, h = im.size
    return [[im.getpixel((x, y)) for x in range(w)] for y in range(h)], w, h


def interleaved(name):
    p = os.path.join(GFX, name + '.properties')
    return os.path.exists(p) and 'interleave: true' in open(p).read()


def unroll(px, w, h):
    """Image -> bande de colonnes 8x16 (16 lignes)."""
    cols = []
    for r in range(h // 16):
        for c in range(w // 8):
            cols.append([px[r * 16 + y][c * 8:c * 8 + 8] for y in range(16)])
    return [[v for col in cols for v in col[y]] for y in range(16)]


def reroll(strip, w, h):
    px = [[0] * w for _ in range(h)]
    ncol = len(strip[0]) // 8
    for i in range(ncol):
        r, c = divmod(i, w // 8)
        for y in range(16):
            px[r * 16 + y][c * 8:c * 8 + 8] = strip[y][i * 8:i * 8 + 8]
    return px


def text_mask(seg):
    """Pixels du texte (noir) d'un segment : ni lignes noires pleines, ni bords."""
    h, w = len(seg), len(seg[0])
    full = [sum(v == 3 for v in row) > w * 9 // 10 for row in seg]
    m = [[seg[y][x] == 3 and not full[y] and 2 <= x < w - 2 for x in range(w)] for y in range(h)]
    return m


def columns_runs(mask):
    w = len(mask[0])
    used = [any(row[x] for row in mask) for x in range(w)]
    runs, x = [], 0
    while x < w:
        if used[x]:
            x0 = x
            while x < w and used[x]:
                x += 1
            runs.append((x0, x))
        else:
            x += 1
    return runs


def extract(fonts, seg, word):
    mask = text_mask(seg)
    rows = [y for y in range(16) if any(mask[y])]
    top, bot = rows[0], rows[-1]
    runs = columns_runs(mask)
    letters = word.replace(' ', '')
    if len(runs) == len(letters) - 1 and letters.endswith('.'):
        x0, x1 = runs[-1]   # « T. » collés : le point = 2 dernières colonnes
        runs[-1:] = [(x0, x1 - 2), (x1 - 2, x1)]
    assert len(runs) == len(letters), (word, runs)
    for (x0, x1), ch in zip(runs, letters):
        g = [[mask[y][x] for x in range(x0, x1)] for y in range(top, top + 11)]
        full = [[mask[y][x] for x in range(x0, x1)] for y in range(top, bot + 1)]
        h = 'H12' if bot - top + 1 >= 12 else 'H11'
        if h == 'H12':
            g = [[mask[y][x] for x in range(x0, x1)] for y in range(top, top + 12)]
        fonts[h].setdefault(ch, g)
    return top, bot, (runs[0][0], runs[-1][1])


def drawn(ch):
    return [[c == '@' for c in row] for row in DRAWN[ch]]


def glyph(fonts, ch, height):
    """Lettre à la hauteur voulue (12 ou 11 lignes), extraite, convertie ou dessinée."""
    if ch in ACCENTS:
        base, acc = ACCENTS[ch]
        g, _ = glyph(fonts, base, height)
        return g, [c == '@' for c in acc]
    own, other = ('H12', 'H11') if height == 12 else ('H11', 'H12')
    if ch in fonts[own]:
        return fonts[own][ch], None
    if ch in fonts[other]:
        g = fonts[other][ch]
    else:
        g = drawn(ch)
    if len(g) == 12 and height == 11:
        return g[:5] + g[6:], None
    if len(g) == 11 and height == 12:
        return g[:6] + g[5:], None
    return g, None


def layout(fonts, word, height, gap=GAP):
    """Liste (x, glyphe, accent) et largeur totale."""
    items, x, prev = [], 0, None
    for ch in word:
        if ch == ' ':
            x += SPACE
            prev = None
            continue
        if ch == '_':
            x += SMALL
            prev = None
            continue
        if ch == '^':
            continue
        if prev is not None:
            x += gap
        g, acc = glyph(fonts, ch, height)
        items.append((x, g, acc))
        x += len(g[0])
        prev = ch
    return items, x


# Lignes rayées de chaque sorte de segment (16 colonnes = bannière, 12 = bouton, 5 = petit bouton)
STRIPE_ROWS = {16: (0, 14), 12: (3, 16), 5: (3, 15)}


def pool_columns(segs):
    """Colonnes de rayures des bannières, sans texte ni décor (pour recoudre le fond)."""
    pool = []
    for seg in segs:
        w = len(seg[0])
        mask = text_mask(seg)
        ok = [not any(mask[y][x] for y in range(16)) and
              not any(seg[y][x] >= 2 for y in range(0, 14)) and 3 <= x < w - 3
              for x in range(w)]
        x = 0
        while x < w:
            if ok[x]:
                x0 = x
                while x < w and ok[x]:
                    x += 1
                if x - x0 >= 6:
                    pool.append([[seg[y][i] for y in range(14)] for i in range(x0, x)])
            else:
                x += 1
    return pool


def diff(a, b):
    return sum(u != v for u, v in zip(a, b))


def quilt(seg, a, b, pool, rnd):
    """Remplace les rayures des colonnes [a, b) par des rayures d'origine bien raccordées."""
    r0, r1 = STRIPE_ROWS[len(seg[0]) // 8]
    nr = r1 - r0
    col = lambda x: [seg[y][x] for y in range(r0, r1)]
    out = [col(x) for x in range(len(seg[0]))]
    runs = [[c[:nr] for c in run] for run in pool]
    longest = max(len(run) for run in runs) - 2
    x = a
    while x < b:
        n = min(b - x, rnd.randint(5, 10), longest)
        if b - x - n < 4 and b - x <= longest:
            n = b - x
        best = None
        for run in runs:
            for s in range(1, len(run) - n):
                d = diff(run[s - 1], out[x - 1]) * 2
                if x + n == b and b < len(out):
                    d += diff(run[s + n], out[b]) * 2
                d += rnd.random() * 0.5
                if best is None or d < best[0]:
                    best = (d, run, s)
        _, run, s = best
        for i in range(n):
            out[x + i] = list(run[s + i])
        x += n
    for y in range(r0, r1):
        for x in range(a, b):
            seg[y][x] = out[x][y - r0]


# « Message Speed » (écran du fichier choisi) : police des dialogues (gfx_font.png), fond = couleur 2,
# encre = 3. « Slow » / « Fast » : petite police (couleur 1), dessinée ici.
SPEED_TITLE = 'Vitesse du texte'
TINY = {
    'L': [':...', ':...', ':...', ':...', ':...', ':...', '::::'],
    'e': ['.....', '.....', '.:::.', ':...:', ':::::', ':....', '.::::'],
    'n': ['....', '....', ':::.', ':..:', ':..:', ':..:', ':..:'],
    't': ['...', '.:.', ':::', '.:.', '.:.', '.:.', '..:'],
    'V': [':...:', ':...:', ':...:', ':...:', '.:.:.', '.:.:.', '..:..'],
    'i': [':', '.', ':', ':', ':', ':', ':'],
}


def make_messagespeed():
    src = Image.open(os.path.join(GFX, 'gfx_messagespeed.png'))
    w, h = src.size
    px = [[src.getpixel((x, y)) for x in range(w)] for y in range(h)]
    # Titre : 13 tuiles de large sur 2 lignes (x 0-103), on efface puis on écrit
    for y in range(16):
        for x in range(104):
            px[y][x] = 2
    font = Image.open(os.path.join(ROOT, 'oracles-disasm', 'gfx', 'common', 'gfx_font.png')).convert('L')
    glyphs = []
    for ch in SPEED_TITLE:
        code = ord(ch)
        gx, gy = (code % 16) * 8, (code // 16) * 16
        ink = [[font.getpixel((gx + x, gy + y)) >= 128 for x in range(8)] for y in range(16)]
        cols = [x for x in range(8) if any(ink[y][x] for y in range(16))]
        if not cols:
            glyphs.append((None, 3))
            continue
        glyphs.append(([row[cols[0]:cols[-1] + 1] for row in ink], cols[-1] - cols[0] + 1))
    total = sum(gw for _, gw in glyphs) + len(glyphs) - 1
    assert total <= 102, total
    x = (104 - total) // 2
    for g, gw in glyphs:
        if g:
            for y in range(5, 16):   # majuscules du jeu en lignes 6-14 -> lignes 1-9 ici
                for i in range(gw):
                    if g[y][i]:
                        px[y - 5][x + i] = 3
        x += gw + 1
    # Lent / Vite : tuiles de 24x8 en (104, 0) et (104, 8)
    for word, y0 in (('Lent', 0), ('Vite', 8)):
        for y in range(8):
            for xx in range(104, 128):
                px[y0 + y][xx] = 2
        x = 106
        for ch in word:
            g = TINY[ch]
            for y, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == ':':
                        px[y0 + y][x + i] = 1
            x += len(g[0]) + 1
        assert x <= 129, word
    im = Image.new('P', (w, h))
    im.putpalette(src.getpalette())
    im.putdata([v for row in px for v in row])
    im.save(os.path.join(GFX, 'gfx_messagespeed_fr.png'))
    return px


# Bouton rouge « SAVE » de l'inventaire (gfx_save : 8 tuiles 8x8, haut/bas de chaque colonne) :
# « SAUV ». S et A gardés, U dessiné à partir du V (bas arrondi), V décalé à la place du E.
U_BOTTOM = ['@:#@.@:#@', '@:#@@@:#@', '@:#:::##@', '.@#####@.', '..@@@@@..']


def make_save_button():
    src = Image.open(os.path.join(GFX, 'gfx_save.png'))
    tiles = [[[src.getpixel((i * 8 + x, y)) for x in range(8)] for y in range(8)] for i in range(8)]
    old = [[tiles[(x // 8) * 2 + y // 8][y % 8][x % 8] for x in range(32)] for y in range(16)]
    new = [[0] * 32 for _ in range(16)]
    for y in range(16):
        for x in range(1, 25):          # S, A, et le V qui devient U, un pixel à gauche
            new[y][x - 1] = old[y][x]
    for i, row in enumerate(U_BOTTOM):  # bas du U (lignes 10-14, colonnes 15-23)
        for x, c in enumerate(row):
            if 1 <= x <= (8 if i >= 3 else 7):
                new[10 + i][15 + x] = 0
            if c != '.':
                new[10 + i][15 + x] = '.:#@'.index(c)
    for y in range(16):                 # V à la place du E (colonnes 23-31)
        for x in range(16, 25 if y < 13 else 24):   # col. 24 en bas = contour du E
            if old[y][x]:
                new[y][x + 7] = old[y][x]
    im = Image.new('P', src.size)
    im.putpalette(src.getpalette())
    for x in range(32):
        for y in range(16):
            i = (x // 8) * 2 + y // 8
            im.putpixel((i * 8 + x % 8, y % 8), new[y][x])
    im.save(os.path.join(GFX, 'gfx_save_fr.png'))
    return new, old


def build():
    fonts = {'H12': {}, 'H11': {}}
    data = []
    for name, segs in IMAGES:
        px, w, h = load(name)
        inter = interleaved(name)
        strip = unroll(px, w, h) if inter else px
        parts = []
        for c0, nc, en, fr in segs:
            seg = [row[c0 * 8:(c0 + nc) * 8] for row in strip]
            info = extract(fonts, seg, en)
            parts.append((c0, nc, seg, info, fr))
        data.append((name, px, w, h, inter, strip, parts))

    pool = pool_columns([p[2] for d in data for p in d[6] if p[1] == 16])
    previews = []
    for name, px, w, h, inter, strip, parts in data:
        rnd = random.Random(name)
        for c0, nc, seg, (top, bot, (ex0, ex1)), fr in parts:
            height = 12 if bot - top + 1 >= 12 else 11
            items, tw = layout(fonts, fr, height)
            sw = nc * 8
            # bouton de 40 px : la marge de gauche décorée compte comme fond
            if sw == 40 and tw > 26:   # petit bouton : lettres plus serrées
                items, tw = layout(fonts, fr, height, gap=1)
            x0 = (sw - tw + 1) // 2
            assert x0 >= 2 and x0 + tw <= sw - 2, (name, fr, tw, sw)
            a = max(1, min(ex0, x0) - 2)
            b = min(sw - 1, max(ex1, x0 + tw) + 2)
            if sw == 40:   # petits boutons : bord droit = cadre
                b = min(b, sw - 2)
            work = [list(r) for r in seg]
            quilt(work, a, b, pool, rnd)
            for gx, g, acc in items:
                # fond crème sous la lettre (sinon une rayure ressemble à un trait)
                for y in range(-2 if acc else 0, len(g)):
                    for x in range(len(g[0])):
                        on = acc[x] if y == -2 else (y >= 0 and g[y][x])
                        work[top + y][x0 + gx + x] = 3 if on else 0
            for y in range(16):
                strip[y][c0 * 8:(c0 + nc) * 8] = work[y]
        newpx = reroll(strip, w, h) if inter else strip
        src = Image.open(os.path.join(GFX, name + '.png'))
        im = Image.new('P', (w, h))
        im.putpalette(src.getpalette())
        im.putdata([v for row in newpx for v in row])
        im.save(os.path.join(GFX, name + '_fr.png'))
        prop = os.path.join(GFX, name + '.properties')
        if os.path.exists(prop):
            out = os.path.join(GFX, name + '_fr.properties')
            with open(prop) as f, open(out, 'w', newline='\n') as g:
                g.write(f.read())
        previews.append((name, strip if inter else newpx, unroll(px, w, h) if inter else px))

    src = Image.open(os.path.join(GFX, 'gfx_messagespeed.png'))
    en = [[src.getpixel((x, y)) for x in range(src.size[0])] for y in range(src.size[1])]
    previews.append(('gfx_messagespeed', make_messagespeed(), en))
    new, old = make_save_button()
    previews.append(('gfx_save', new, old))

    # Aperçu : anglais / français, en bandes, couleurs de l'écran de sauvegarde
    colors = [(248, 248, 208), (120, 176, 232), (40, 80, 160), (0, 0, 0)]
    rows = []
    for name, fr, en in previews:
        rows += [en, fr]
    W = max(len(r[0]) for r in rows)
    H = sum(len(r) + 2 for r in rows)
    im = Image.new('RGB', (W, H), (255, 0, 255))
    y = 0
    for r in rows:
        for yy, row in enumerate(r):
            for x, v in enumerate(row):
                im.putpixel((x, y + yy), colors[v])
        y += len(r) + 2
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    im.resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(ROOT, 'out', 'menus_fr.png'))
    print('menus FR :', ', '.join(n + '_fr' for n, _ in IMAGES), '+ gfx_messagespeed_fr, gfx_save_fr')


build()
