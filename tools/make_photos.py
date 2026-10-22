"""Les photos de Cocolint (la scène des photos avec Marine, à l'auberge) : les vraies photos de
l'album de Link's Awakening DX, en sépia (art/photos/N-nom.png, 160 x 144, quatre nuances,
capturées dans l'album du jeu ; on peut les retoucher : la falaise a reçu ses mouettes).

Pour chaque photo, écrit dans oracles-disasm/gfx_compressible/ages/ :
- gfx_photo_N.png et _Nb : ses tuiles sans doublons (176 au plus : au-delà, les plus
  ressemblantes sont fusionnées), chargées en $8800 et $9100 (voir SLOTS : le texte garde ses
  tuiles) ;
- map_photo_N.bin / flg_photo_N.bin : sa carte (32 x 18 tuiles) et ses attributs (palette 2 : la 0
  reste celle de la boîte de texte).
Les quatre nuances : PALH_PHOTO (paletteHeaders.s, palette 2), de la plus claire (couleur 0) à
la plus sombre (3). Voir code/ages/cutscenes/photos.s.

Usage : python tools/make_photos.py   (lancé par build.sh)
"""
import glob
import os

from PIL import Image

# Les numéros de tuiles que la photo peut prendre (mode signé : $80-$ff = $8800-$8fff, $00-$7f =
# $9000-$97ff). Restent au jeu : $00-$0f (la boîte de texte y prend son fond noir, la tuile $02 :
# textbox.s, initTextboxMapping) et $40-$7f ($9400-$97ff : les lettres du texte, dmaTextGfxBuffer).
SLOTS = list(range(0x80, 0x100)) + list(range(0x10, 0x40))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GFX = os.path.join(ROOT, 'oracles-disasm', 'gfx_compressible', 'ages')


def convert(path, n):
    im = Image.open(path).convert('RGB')
    assert im.size == (160, 144), (path, im.size)
    colors = sorted(set(im.getpixel((x, y)) for y in range(144) for x in range(160)), key=sum, reverse=True)
    assert len(colors) <= 4, (path, colors)
    shade = {c: i for i, c in enumerate(colors)}
    tiles, index, tilemap = [], {}, []
    for ty in range(18):
        row = []
        for tx in range(32):
            if tx < 20:
                t = tuple(shade[im.getpixel((tx * 8 + x, ty * 8 + y))] for y in range(8) for x in range(8))
            else:
                t = (0,) * 64
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            row.append(index[t])
        tilemap.append(row)
    tiles, tilemap = merge(tiles, tilemap, len(SLOTS))
    # (une entrée de gfxHeaders.s charge 128 tuiles au plus : $8800 (128), $9100 (48))
    parts = [tiles[:128], tiles[128:]]
    for suffix, part in zip(('', 'b'), parts):
        save_tiles(part or [(0,) * 64], 'gfx_photo_%d%s.png' % (n, suffix))
    tilemap = [[SLOTS[i] for i in row] for row in tilemap]
    with open(os.path.join(GFX, 'map_photo_%d.bin' % n), 'wb') as f:
        f.write(bytes(i for row in tilemap for i in row))
    with open(os.path.join(GFX, 'flg_photo_%d.bin' % n), 'wb') as f:
        f.write(bytes([2] * (18 * 32)))
    return len(tiles)


def merge(tiles, tilemap, limit):
    """Trop de tuiles : fusionner les plus ressemblantes (le moins de pixels différents)."""
    alive = list(range(len(tiles)))
    target = {i: i for i in alive}
    while len(alive) > limit:
        best = None
        for a in alive:
            for b in alive:
                if a < b:
                    d = sum(x != y for x, y in zip(tiles[a], tiles[b]))
                    if best is None or d < best[0]:
                        best = (d, a, b)
        _, a, b = best
        alive.remove(b)
        for k, v in target.items():
            if v == b:
                target[k] = a
    new = {old: i for i, old in enumerate(alive)}
    return [tiles[i] for i in alive], [[new[target[i]] for i in row] for row in tilemap]


def save_tiles(tiles, name):
    n_rows = (len(tiles) + 15) // 16
    out = Image.new('P', (128, n_rows * 8))
    out.putpalette([v for g in (255, 170, 85, 0) for v in (g, g, g)] + [0] * (768 - 12))
    for i, t in enumerate(tiles):
        for p, c in enumerate(t):
            out.putpixel(((i % 16) * 8 + p % 8, (i // 16) * 8 + p // 8), c)
    # (le convertisseur trie les couleurs par luminosité : garantir les 4 nuances, dans la place
    # libre après la dernière tuile)
    if {c for t in tiles for c in t} != {0, 1, 2, 3}:
        assert len(tiles) % 16, (name, 'pas de place pour les 4 nuances')
        for c in (1, 2, 3):
            out.putpixel((128 - c, n_rows * 8 - 1), c)
    out.save(os.path.join(GFX, name))


def main():
    paths = sorted(glob.glob(os.path.join(ROOT, 'art', 'photos', '*.png')))
    for n, path in enumerate(paths, 1):
        print('photo %d : %s, %d tuiles' % (n, os.path.basename(path), convert(path, n)))


main()
