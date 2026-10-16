"""Dessine des salles sans lancer le jeu, à partir des fichiers du décor (hack-base).

Pour chaque brique : tilesetMappingsXX.bin donne 4 tuiles + 4 attributs (palette, banque
vidéo, miroirs) ; les tuiles sont dans gfx/ages/gfx_tilesetXX.png ; les couleurs viennent de
l'en-tête de palette du décor (data/ages/paletteHeaders.s). Marche pour les petites salles
(10 x 8) comme pour les grandes salles de donjon (15 x 11, stockées sur 16 colonnes).

Usage :
  python tools/render_room.py SORTIE.png G:SS [G:SS ...]    (ex. 1:9a 4:10)
  python tools/render_room.py SORTIE.png --decor 36        (planche des 256 briques d'un décor)
Options : --numeros  écrit le numéro de chaque brique.
"""
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
LAYOUT_GROUP = {0: 0x00, 1: 0x02, 2: 0x01, 3: 0x03, 4: 0x04, 5: 0x05}
LARGE_GROUPS = (4, 5)


def read(path, mode='r'):
    return open(os.path.join(DISASM, path), mode, **({} if 'b' in mode else {'encoding': 'utf-8'}))


TILESETS_S = read('data/ages/tilesets.s').read()
HEADERS_S = read('data/ages/paletteHeaders.s').read()
PALDATA_S = read('data/ages/paletteData.s').read()


def tileset_palette_header(ts):
    lines = TILESETS_S.split('\n')
    for n, l in enumerate(lines):
        if l == '\t; 0x%02x' % ts:
            return lines[n + 4].replace('.db', '').strip()
        if l.endswith('; Tileset 0x%02x BALLADE: Songe' % ts):
            return l.split(';')[0].replace('.db', '').split(',')[4].strip()
    raise KeyError(ts)


def palettes(ts):
    """8 palettes de 4 couleurs (RGB 0-255). Les palettes 0-1 (communes) restent grises."""
    pal = [[(255, 255, 255), (170, 170, 170), (85, 85, 85), (0, 0, 0)] for _ in range(8)]
    name = tileset_palette_header(ts)
    m = re.search(r'm_PaletteHeaderStart \$[0-9a-f]+, %s\n((?:\tm_PaletteHeader\w+ .*\n)+)' % name, HEADERS_S)
    for line in m.group(1).strip().split('\n'):
        if 'Bg' not in line:
            continue
        first, count, label = [w.strip() for w in line.split(None, 1)[1].split(',')]
        block = re.search(r'^%s:[^\n]*\n((?:\tm_RGB16 .*\n|\n)+)' % label, PALDATA_S, re.M).group(1)
        cols = [tuple(int(v[1:], 16) * 255 // 31 for v in l.split()[1:4]) for l in block.split('\n') if 'm_RGB16' in l]
        for i in range(int(count)):
            pal[int(first) + i] = cols[i * 4:i * 4 + 4]
    return pal


def tile_images(ts):
    im = Image.open(os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % ts)).convert('L')
    grey = {255: 0, 170: 1, 85: 2, 0: 3}
    tiles = []
    for t in range(256):
        x0, y0 = (t % 16) * 8, (t // 16) * 8
        tiles.append([[grey.get(im.getpixel((x0 + x, y0 + y)), 0) for x in range(8)] for y in range(8)])
    return tiles


CACHE = {}


def metatile(ts, n):
    if ts not in CACHE:
        CACHE[ts] = (read('tileset_layouts_expanded/ages/tilesetMappings%02x.bin' % ts, 'rb').read(),
                     tile_images(ts), palettes(ts))
    maps, tiles, pal = CACHE[ts]
    e = maps[n * 8:n * 8 + 8]
    out = Image.new('RGB', (16, 16))
    for q in range(4):
        idx, attr = e[q], e[4 + q]
        # Adressage « signé » de la Game Boy : tuiles $80-$ff en premier dans l'image, puis $00-$7f
        # (vérifié contre les captures de tools/catalog.py)
        t = tiles[idx ^ 0x80]
        p = pal[attr & 0x07]
        for y in range(8):
            for x in range(8):
                sx = 7 - x if attr & 0x20 else x
                sy = 7 - y if attr & 0x40 else y
                out.putpixel(((q % 2) * 8 + x, (q // 2) * 8 + y), p[t[sy][sx]])
    return out


def room_tileset(group, room):
    return read('rooms/ages/group%dTilesets.bin' % group, 'rb').read()[room] & 0x7f


def render(group, room, numbers=False):
    ts = room_tileset(group, room)
    large = group in LARGE_GROUPS
    w, h = (15, 11) if large else (10, 8)
    stride = 16 if large else 10
    path = 'rooms/ages/%s/room%02x%02x.bin' % ('large' if large else 'small', LAYOUT_GROUP[group], room)
    data = read(path, 'rb').read()
    img = Image.new('RGB', (w * 16, h * 16))
    for y in range(h):
        for x in range(w):
            img.paste(metatile(ts, data[y * stride + x]), (x * 16, y * 16))
    if numbers:
        img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
        d = ImageDraw.Draw(img)
        f = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 10)
        for y in range(h):
            for x in range(w):
                d.rectangle([x * 32, y * 32, x * 32 + 13, y * 32 + 9], fill=(0, 0, 0))
                d.text((x * 32 + 1, y * 32 - 1), '%02x' % data[y * stride + x], font=f, fill=(255, 255, 0))
    return img, ts


def catalog(out, ts):
    """Planche des 256 briques d'un décor, numérotées."""
    sheet = Image.new('RGB', (16 * 36, 16 * 36), 'black')
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 10)
    for n in range(256):
        x, y = (n % 16) * 36, (n // 16) * 36
        sheet.paste(metatile(ts, n).resize((32, 32), Image.NEAREST), (x + 2, y + 2))
        d.rectangle([x + 2, y + 2, x + 15, y + 11], fill=(0, 0, 0))
        d.text((x + 3, y + 1), '%02x' % n, font=f, fill=(255, 255, 0))
    sheet.save(out)
    print('->', out)


def main():
    out, args = sys.argv[1], sys.argv[2:]
    if args[0] == '--decor':
        return catalog(out, int(args[1], 16))
    numbers = '--numeros' in args
    args = [a for a in args if a != '--numeros']
    rooms = [(int(a.split(':')[0]), int(a.split(':')[1], 16)) for a in args]
    imgs = [render(g, r, numbers) + ((g, r),) for g, r in rooms]
    W = max(i.width for i, _, _ in imgs)
    cols = 3 if len(imgs) > 2 else len(imgs)
    rows = (len(imgs) + cols - 1) // cols
    H = max(i.height for i, _, _ in imgs) + 16
    sheet = Image.new('RGB', (W * cols, H * rows), 'black')
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 13)
    for k, (im, ts, (g, r)) in enumerate(imgs):
        x0, y0 = (k % cols) * W, (k // cols) * H
        d.text((x0 + 3, y0 + 1), 'salle %d:%02x  decor %02x' % (g, r, ts), font=f, fill='white')
        sheet.paste(im, (x0, y0 + 16))
    sheet.save(out)
    print('->', out)


main()
