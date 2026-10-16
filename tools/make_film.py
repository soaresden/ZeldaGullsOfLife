"""Fabrique les graphismes du film d'ouverture (avant l'écran titre).

Écrit dans oracles-disasm/gfx_compressible/ages/ :
- gfx_film_bg.png : tuiles du décor (ciel à l'aube, horizon, mer), sans doublons ;
- map_film_bg.bin / flg_film_bg.bin : carte du décor (32 x 18 tuiles) et attributs (palettes) ;
- spr_film.png : sprites (poses de Link prises dans spr_link.png, Marine en mouette,
  rondin, soleil, bulles « ! » et « ? », cœur, visage de Marine dans les nuages et sa fleur).

La mer se répète tous les 32 pixels : le jeu peut faire défiler tout le décor (le ciel est
uni sur chaque ligne, on ne voit bouger que les vagues).

Usage : python tools/make_film.py   (depuis la racine du dépôt)
"""
import math
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GFX = os.path.join(ROOT, 'oracles-disasm', 'gfx_compressible', 'ages')
LINK_PNG = os.path.join(ROOT, 'oracles-disasm', 'gfx', 'common', 'spr_link.png')

# Décor : couleurs 0-3 de chaque palette (voir PALH_FILM dans paletteHeaders.s)
#   palette 0 : bandes noires ; 1 : ciel (0 bleu nuit -> 3 lueur de l'aube) ;
#   palette 2 : mer (0 bleu profond, 1 bleu, 2 cyan, 3 écume)
BG_GREY = [255, 170, 85, 0]   # gfx_* : blanc = couleur 0, ..., noir = couleur 3
SPR_GREY = {'.': 0, 'k': 85, 'r': 170, 'w': 255}  # spr_* : couleurs inversées
HORIZON = 80   # ligne de l'horizon (pixels)


# Nuages : cercles (x, y, rayon) ; le décor fait 256 pixels de large et se répète
CLOUDS = [
    [(20, 34, 7), (30, 30, 9), (42, 32, 8), (52, 35, 6), (36, 37, 7)],
    [(138, 44, 5), (147, 41, 7), (157, 44, 5)],
    [(196, 26, 6), (207, 22, 8), (219, 25, 7), (229, 28, 5), (210, 29, 6)],
]


def in_cloud(x, y):
    for cloud in CLOUDS:
        for (cx, cy, r) in cloud:
            dx = (x - cx + 128) % 256 - 128
            if dx * dx + (y - cy) * (y - cy) * 2 <= r * r:
                return True
    return False


def sky_color(x, y):
    """Dégradé du haut (bleu nuit) vers l'horizon (lueur), avec un tramage entre les bandes.
    Les nuages sont bleu clair, dorés par le soleil levant sur leur bord inférieur."""
    if in_cloud(x, y):
        return 3 if not in_cloud(x, y + 2) else 2
    t = (y - 16) / (HORIZON - 16) * 3.0   # 0 en haut du ciel, 3 à l'horizon
    base = int(t)
    frac = t - base
    # tramage ordonné 2x2 : la bande suivante gagne du terrain
    seuil = [[0.2, 0.6], [0.8, 0.4]][y % 2][x % 2]
    return min(3, base + (1 if frac > seuil else 0))


def sea_color(x, y):
    """Mer : bleu, crêtes de vagues de plus en plus grandes vers le bas (perspective)."""
    d = y - HORIZON
    if d < 2:
        return 2                     # reflet clair sur l'horizon
    col = 1 if d < 24 else 0         # plus profond au premier plan
    # lignes de vagues : position, longueur de crête, décalage (période 32 px)
    for (wy, length, shift) in ((4, 6, 0), (9, 8, 13), (15, 10, 5), (22, 12, 21), (31, 14, 9), (41, 16, 26)):
        dx = (x + shift) % 32
        if d == wy and dx < length:
            return 3                 # écume
        if d == wy + 1 and dx < length + 2 and dx > 0:
            return 2                 # creux clair sous la crête
    return col


def build_background():
    w, h = 256, 144
    pixels = [[0] * w for _ in range(h)]
    pal_rows = []
    for ty in range(18):
        y0 = ty * 8
        if y0 < 16 or y0 >= 128:
            pal = 0
        elif y0 < HORIZON:
            pal = 1
        else:
            pal = 2
        pal_rows.append(pal)
        for y in range(y0, y0 + 8):
            for x in range(w):
                if pal == 0:
                    c = 0
                elif pal == 1:
                    c = sky_color(x, y)
                else:
                    c = sea_color(x, y)
                pixels[y][x] = c
    # Découpage en tuiles 8x8 sans doublons
    tiles, index = [], {}
    tilemap = []
    for ty in range(18):
        row = []
        for tx in range(32):
            t = tuple(pixels[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            row.append(index[t])
        tilemap.append(row)
    assert len(tiles) <= 128, len(tiles)
    # Image des tuiles : 16 tuiles par ligne
    n_rows = (len(tiles) + 15) // 16
    im = Image.new('P', (128, n_rows * 8))
    im.putpalette([v for g in (255, 170, 85, 0) for v in (g, g, g)] + [0] * (768 - 12))
    for i, t in enumerate(tiles):
        for p, c in enumerate(t):
            im.putpixel(((i % 16) * 8 + p % 8, (i // 16) * 8 + p // 8), c)
    # Le convertisseur trie les couleurs par luminosité : garantir les 4 nuances
    im.putpixel((127, n_rows * 8 - 1), 3)
    im.putpixel((126, n_rows * 8 - 1), 2)
    im.putpixel((125, n_rows * 8 - 1), 1)
    im.save(os.path.join(GFX, 'gfx_film_bg.png'))
    with open(os.path.join(GFX, 'map_film_bg.bin'), 'wb') as f:
        f.write(bytes(i for row in tilemap for i in row))
    with open(os.path.join(GFX, 'flg_film_bg.bin'), 'wb') as f:
        f.write(bytes(pal_rows[ty] for ty in range(18) for _ in range(32)))
    return len(tiles)


def read_art(path):
    """Lit les dessins « @nom largeur » d'un fichier texte."""
    art, name = {}, None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('#') or not line.strip():
            continue
        if line.startswith('@'):
            name, width = line[1:].split()
            art[name] = (int(width), [])
            continue
        width, rows = art[name]
        assert len(line) == width, (name, len(art[name][1]), line)
        rows.append(line)
    return {k: rows for k, (w, rows) in art.items()}


def read_gull_frames():
    rows = [l.rstrip('\n') for l in open(os.path.join(ROOT, 'art', 'marine_mouette.txt'), encoding='utf-8')
            if l.strip() and not l.startswith('#')]
    return [rows[i:i + 16] for i in range(0, len(rows), 16)]


def build_sprites():
    im = Image.new('L', (128, 64), 0)
    link = Image.open(LINK_PNG).convert('L')

    def put_cell(cell, row, rows=None, link_cell=None):
        x0, y0 = cell * 16, row * 16
        if link_cell is not None:
            sx, sy = (link_cell % 8) * 16, (link_cell // 8) * 16
            im.paste(link.crop((sx, sy, sx + 16, sy + 16)), (x0, y0))
            return
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                im.putpixel((x0 + x, y0 + y), SPR_GREY[c])

    # Ligne 0 : Link de profil, de dos, de face, bras levés ; Marine posée, en vol, clin d'œil ; bulle
    for cell, link_cell in enumerate((2, 0, 8, 22)):
        put_cell(cell, 0, link_cell=link_cell)
    perched, _, flying = read_gull_frames()
    wink = [list(r) for r in perched]
    wink[3][5] = 'k'        # paupière en accent circonflexe : œil fermé, content
    wink[4][4] = 'k'
    wink[4][5] = 'w'
    wink[4][6] = 'k'
    wink = [''.join(r) for r in wink]
    art = read_art(os.path.join(ROOT, 'art', 'film_sprites.txt'))
    put_cell(4, 0, perched)
    put_cell(5, 0, flying)
    put_cell(6, 0, wink)
    put_cell(7, 0, art['bubble'])
    # Ligne 1 : rondin (3 cases), soleil (2 cases), cœur, bulle « ? »
    for i in range(3):
        put_cell(i, 1, [r[i * 16:i * 16 + 16] for r in art['log']])
    for i in range(2):
        put_cell(3 + i, 1, [r[i * 16:i * 16 + 16] for r in art['sun']])
    put_cell(5, 1, art['heart'])
    put_cell(6, 1, art['question'])
    # Lignes 2-3 : visage de Marine (2x2 cases), sa fleur
    for i in range(2):
        for j in range(2):
            put_cell(i, 2 + j, [r[i * 16:i * 16 + 16] for r in art['face'][j * 16:j * 16 + 16]])
    put_cell(2, 2, art['flower'])

    out = Image.new('P', im.size)
    out.putpalette([0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255] + [0] * (768 - 12))
    out.putdata([{0: 0, 85: 1, 170: 2, 255: 3}[v] for v in im.getdata()])
    out.save(os.path.join(GFX, 'spr_film.png'))


def main():
    n = build_background()
    build_sprites()
    print('film : %d tuiles de décor, sprites -> gfx_compressible/ages/' % n)


main()
