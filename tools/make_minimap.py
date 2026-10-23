"""Dessine la carte du jeu (Select : la carte du Réel et celle du Songe) d'après nos vraies salles.

La carte d'Ages montre une grille de 14 x 14 salles (une tuile de 8 x 8 par salle, colonnes 3-16,
lignes 2-15 de l'écran) au milieu des paysages de Labrynna. Ici : chaque salle de nos îles devient
une petite image de 8 x 8 (la salle dessinée par tools/render_room.py, réduite), le reste est la
mer, tout autour aussi ; le ciel et les nuages du haut restent. Les tuiles sont dédoublonnées (et
leurs miroirs) ; si elles dépassent la place (96 + 32), les plus proches sont fusionnées.

Couleurs : nos palettes 0, 3, 5, 6, 7 (la 1 = le ciel, la 4 = les nuages, la 2 = le brouillard des
salles pas encore vues, comme Ages). Le Songe : les mêmes, bleutées.

Écrit (oracles-disasm) : gfx_compressible/ages/gfx_minimap_tiles_{past,present}_{1,2}.png,
{map,flg}_{past,present}_minimap.bin, et les couleurs dans data/ages/paletteData.s
(paletteData40d8 : le Réel ; paletteData4098 : le Songe). Aperçu : out/carte_jeu.png.

Usage : python tools/make_minimap.py   (après tools/make_rooms.py : il lit les salles compilées)
"""
import glob
import io
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_room  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
GFX = os.path.join(DISASM, 'gfx_compressible', 'ages')
GRID_X, GRID_Y, SIZE = 3, 2, 14

# Nos palettes (RGB 0-255) : 4 couleurs chacune ; recalculées d'après les salles (make_palettes)
PALETTES = {
    0: [(24, 64, 160), (72, 136, 216), (232, 208, 136), (88, 168, 72)],     # la mer et la côte
    3: [(88, 168, 72), (32, 96, 48), (232, 208, 136), (136, 96, 64)],       # la terre, les bois
    5: [(88, 168, 72), (200, 72, 56), (176, 176, 168), (136, 96, 64)],      # les villages
    6: [(136, 192, 240), (240, 240, 248), (152, 152, 168), (24, 64, 160)],  # le ciel, la neige
    7: [(56, 40, 88), (232, 120, 40), (120, 112, 120), (24, 64, 160)],      # la nuit, la braise
}
SKY = (136, 192, 240)
SEA = (64, 72, 200)                # (recalculée : la couleur la plus fréquente au bord des salles)
WHITE = (248, 248, 248)
SEA_TILE = ((0,) * 64, 0)          # (motif, palette)


def island_rooms():
    rooms = set()
    for p in glob.glob(os.path.join(ROOT, 'story', 'salles', 'ile_*.txt')):
        for line in open(p, encoding='utf-8'):
            m = re.match(r'salle ([0-9a-f]{2}) decor', line)
            if m:
                rooms.add(int(m.group(1), 16))
    return sorted(r for r in rooms if r >> 4 < SIZE and r & 15 < SIZE)


def shrink(img):
    """160 x 128 -> 8 x 8 : la couleur moyenne de chaque bloc de 20 x 16."""
    small = img.resize((8, 8), Image.BOX)
    return [small.getpixel((x, y)) for y in range(8) for x in range(8)]


def dist(a, b):
    return sum((p - q) ** 2 for p, q in zip(a, b))


def to_tile(pixels):
    best = None
    for pal, cols in PALETTES.items():
        idx = [min(range(4), key=lambda i: dist(px, cols[i])) for px in pixels]
        err = sum(dist(px, cols[i]) for px, i in zip(pixels, idx))
        if best is None or err < best[0]:
            best = (err, tuple(idx), pal)
    return best[1], best[2]


def flips(pattern):
    rows = [pattern[i * 8:i * 8 + 8] for i in range(8)]
    yield pattern, 0
    yield tuple(v for r in rows for v in reversed(r)), 0x20
    yield tuple(v for r in reversed(rows) for v in r), 0x40
    yield tuple(v for r in reversed(rows) for v in reversed(r)), 0x60


def quantize(pixels, n):
    """n couleurs pour une liste de pixels (la coupe médiane de PIL)."""
    img = Image.new('RGB', (len(pixels), 1))
    img.putdata(pixels)
    q = img.quantize(n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:n * 3]
    cols = [tuple(pal[i * 3:i * 3 + 3]) for i in range(n)]
    while len(cols) < n:
        cols.append(cols[-1])
    return cols


def make_palettes(rooms):
    """Nos 5 palettes d'après les vraies couleurs : chaque salle a ses 4 couleurs, puis les salles
    se regroupent en 5 familles (k-moyennes), chaque famille a les 4 couleurs de tous ses pixels.
    La palette 0 garde la couleur de la mer (le fond de la carte)."""
    import random
    own = {r: sorted(quantize(px, 4)) for r, px in rooms.items()}
    keys = list(own)
    rnd = random.Random(1)
    centers = [own[k] for k in rnd.sample(keys, 5)]
    for _ in range(12):
        groups = [[] for _ in centers]
        for k in keys:
            g = min(range(len(centers)), key=lambda c: sum(dist(a, b) for a, b in zip(own[k], centers[c])))
            groups[g].append(k)
        centers = [sorted(quantize([p for k in g for p in rooms[k]], 4)) if g else centers[i]
                   for i, g in enumerate(groups)]
    pals = [quantize([p for k in g for p in rooms[k]] or [SEA], 4) for g in groups]
    return dict(zip((0, 3, 5, 6, 7), pals))


def build():
    global PALETTES, SEA
    pixels = {}
    for room in island_rooms():
        img, _ = render_room.render(1, room)
        pixels[room] = shrink(img)
    # La mer : la couleur bleue la plus fréquente au bord des salles (couleurs voisines regroupées ;
    # pas le bleu très clair du ciel du Nid des Vents)
    edges = [px for p in pixels.values() for px in (p[:8] + p[-8:])
             if px[2] > px[0] and px[2] > px[1] and sum(px) < 600]
    buckets = {}
    for px in edges:
        buckets.setdefault(tuple(v // 24 for v in px), []).append(px)
    best = max(buckets.values(), key=len)
    SEA = tuple(sum(c) // len(best) for c in zip(*best))
    PALETTES = make_palettes(pixels)
    # La palette 0 commence par la mer (le fond de la carte, la tuile unie)
    p0 = PALETTES[0]
    k = min(range(4), key=lambda i: dist(p0[i], SEA))
    p0[0], p0[k] = p0[k], p0[0]
    p0[0] = SEA
    cells = {room: to_tile(px) for room, px in pixels.items()}

    # Les motifs : le premier est la mer (unie)
    patterns = [SEA_TILE[0]]
    placed = {}
    for room, (pat, pal) in cells.items():
        for variant, flip in flips(pat):
            if variant in patterns:
                placed[room] = (patterns.index(variant), pal, flip)
                break
        else:
            patterns.append(pat)
            placed[room] = (len(patterns) - 1, pal, 0)

    # Trop de motifs : fusionner les plus proches (jamais la mer)
    limit = 96 + 32
    while len(patterns) > limit:
        best = None
        for i in range(1, len(patterns)):
            for j in range(i + 1, len(patterns)):
                d = sum(a != b for a, b in zip(patterns[i], patterns[j]))
                if best is None or d < best[0]:
                    best = (d, i, j)
        _, i, j = best
        for room, (k, pal, flip) in list(placed.items()):
            if k == j:
                placed[room] = (i, pal, 0)
            elif k > j:
                placed[room] = (k - 1, pal, flip)
        del patterns[j]
    return patterns, placed


def tile_index(k):
    """Motif k -> numéro de tuile : les 96 premiers en $80-$df (_1), les 32 suivants en $60-$7f (_2)."""
    return 0x80 + k if k < 96 else 0x60 + (k - 96)


def write_tiles(patterns, kind):
    for part, first, count, h in (('1', 0, 96, 48), ('2', 96, 32, 16)):
        im = Image.new('P', (128, h), 0)
        im.putpalette([255, 255, 255, 170, 170, 170, 85, 85, 85, 0, 0, 0] + [0] * 756)
        for n in range(count):
            k = first + n
            if k >= len(patterns):
                break
            x0, y0 = (n % 16) * 8, (n // 16) * 8
            for i, v in enumerate(patterns[k]):
                im.putpixel((x0 + i % 8, y0 + i // 8), v)
        im.save(os.path.join(GFX, 'gfx_minimap_tiles_%s_%s.png' % (kind, part)))


def write_map(placed, kind):
    """La carte : 32 x 18 tuiles (et leurs attributs)."""
    old_m = open(os.path.join(GFX, 'map_%s_minimap.bin' % kind), 'rb').read()
    old_f = open(os.path.join(GFX, 'flg_%s_minimap.bin' % kind), 'rb').read()
    m, f = bytearray(32 * 18), bytearray(32 * 18)
    sea = tile_index(0)
    for i in range(32 * 18):
        m[i], f[i] = sea, 0x08            # la mer (palette 0, banque 1)
    # Le ciel et les nuages du haut (lignes 0-1), sans le dessin d'Ages au milieu
    for i in range(64):
        m[i], f[i] = old_m[i], old_f[i]
        if 8 <= i % 32 <= 11:
            m[i], f[i] = 0x00, 0x09
    for room, (k, pal, flip) in placed.items():
        y, x = room >> 4, room & 15
        i = (GRID_Y + y) * 32 + GRID_X + x
        m[i], f[i] = tile_index(k), 0x08 | pal | flip
    open(os.path.join(GFX, 'map_%s_minimap.bin' % kind), 'wb').write(m)
    open(os.path.join(GFX, 'flg_%s_minimap.bin' % kind), 'wb').write(f)
    return m, f


def dream(c):
    """Le Songe : bleuté (comme tools/make_songe.py, en plus simple)."""
    r, g, b = c
    grey = (r + g + b) // 3
    return (min(255, grey * 2 // 3 + 40), min(255, grey * 3 // 4 + 50), min(255, grey + 70))


def rgb16(c):
    return '\tm_RGB16 $%02x $%02x $%02x' % tuple(v >> 3 for v in c)


def write_palettes():
    """Les 8 palettes de la carte (32 lignes m_RGB16 après l'étiquette) : les nôtres, le ciel (1),
    les nuages (4) ; la 2 (le brouillard) et les couleurs inutilisées restent celles d'Ages."""
    path = os.path.join(DISASM, 'data', 'ages', 'paletteData.s')
    lines = io.open(path, encoding='utf-8').read().split('\n')
    for label, conv in (('paletteData40d8', lambda c: c), ('paletteData4098', dream)):
        start = lines.index(label + ':') + 1
        rgb, k = [], start
        while len(rgb) < 32:
            if lines[k].strip().startswith('m_RGB16'):
                rgb.append(lines[k])
            k += 1
        pals = [rgb[p * 4:p * 4 + 4] for p in range(8)]
        out = []
        for p in range(8):
            if p in PALETTES:
                cols = [rgb16(conv(c)) for c in PALETTES[p]]
            elif p == 1:
                cols = [rgb16(conv(SKY))] + pals[1][1:]
            elif p == 4:
                cols = [rgb16(conv(WHITE)), rgb16(conv(SKY))] + pals[4][2:]
            else:
                cols = pals[p]
            out += cols + ['']
        # (le commentaire d'un passage précédent est remplacé avec le reste)
        lines[start:k] = ['\t; BALLADE: la carte de nos îles (tools/make_minimap.py)'] + out[:-1]
    io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))


def preview(patterns, m, f):
    img = Image.new('RGB', (160, 144))
    for ty in range(18):
        for tx in range(20):
            t, a = m[ty * 32 + tx], f[ty * 32 + tx]
            pal = a & 7
            if t >= 0x80:
                k = t - 0x80
            elif 0x60 <= t < 0x80:
                k = 96 + t - 0x60
            else:
                k = None
            for i in range(64):
                x, y = i % 8, i // 8
                if a & 0x20:
                    x = 7 - x
                if a & 0x40:
                    y = 7 - y
                if k is not None and k < len(patterns):
                    col = (PALETTES.get(pal) or [SKY] * 4)[patterns[k][y * 8 + x]]
                else:
                    col = SKY if ty < 2 else (60, 60, 60)
                img.putpixel((tx * 8 + i % 8, ty * 8 + i // 8), col)
    out = os.path.join(ROOT, 'out', 'carte_jeu.png')
    img.resize((480, 432), Image.NEAREST).save(out)
    return out


# Les noms sur la carte (TX_03xx, story/textes.yaml) : chaque fichier d'île -> son nom ; la mer
NAME_OF_FILE = {'ile_grelot': 0x02, 'ile_lagune': 0x03, 'ile_braise': 0x04, 'ile_echos': 0x05,
                'ile_nid': 0x06, 'ile_sommeil': 0x07, 'ile_oeil': 0x08, 'ile_marine': 0x09}
NAME_SEA = 0x0a
# L'île de la Brume : Île de la Brume ($36), Port-Veille ($37), le Cap du Phare ($38)
BRUME = {0x7a: 0x38, 0x7b: 0x38, 0x99: 0x37, 0x9a: 0x37, 0x9b: 0x37, 0x9c: 0x37, 0xab: 0x37}


def write_names():
    """Les tables pastMapTextIndices et presentMapTextIndices (14 x 14, une par carte : les mêmes)."""
    table = [NAME_SEA] * (SIZE * SIZE)
    for p in glob.glob(os.path.join(ROOT, 'story', 'salles', 'ile_*.txt')):
        name = os.path.splitext(os.path.basename(p))[0]
        for line in open(p, encoding='utf-8'):
            m = re.match(r'salle ([0-9a-f]{2}) decor', line)
            if not m:
                continue
            room = int(m.group(1), 16)
            if room >> 4 >= SIZE or room & 15 >= SIZE:
                continue
            if name == 'ile_brume':
                value = BRUME.get(room, 0x36)
            else:
                value = NAME_OF_FILE[name]
            table[(room >> 4) * SIZE + (room & 15)] = value
    rows = ['\t.db ' + ' '.join('$%02x' % v for v in table[r * SIZE:(r + 1) * SIZE]) for r in range(SIZE)]
    path = os.path.join(DISASM, 'data', 'ages', 'mapTextAndPopups.s')
    lines = io.open(path, encoding='utf-8').read().split('\n')
    for label in ('presentMapTextIndices:', 'pastMapTextIndices:'):
        i = lines.index(label) + 1
        assert all(lines[i + k].startswith('\t.db ') for k in range(SIZE))
        lines[i:i + SIZE] = rows
    io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))


def main():
    patterns, placed = build()
    for kind in ('past', 'present'):
        write_tiles(patterns, kind)
        m, f = write_map(placed, kind)
    write_palettes()
    write_names()
    print('carte du jeu : %d salles, %d tuiles -> %s' % (len(placed), len(patterns), preview(patterns, m, f)))


if __name__ == '__main__':
    main()
