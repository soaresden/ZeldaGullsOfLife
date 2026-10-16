"""Photographie les 256 briques (metatiles) d'un décor d'Ages, avec leur numéro.

Remplit temporairement 4 salles du passé (1:00-1:03) avec les briques 0 à 255 du décor
demandé, compile, téléporte Link dans chacune avec PyBoy et assemble les captures en une
planche numérotée. Les fichiers de salles sont remis en état à la fin (git checkout).

Usage : python tools/catalog.py DECOR [DECOR ...]   (DECOR en hexadécimal, ex. 10 18 1a)
Sortie : out/catalog/decor_XX.png

Autre mode, sans rien modifier : photographier des salles existantes du passé (groupe 1) avec
le numéro de chaque brique : python tools/catalog.py --salles 79 7a 89
Sortie : out/catalog/salles.png
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
OUT = os.path.join(ROOT, 'out', 'catalog')
ROOMS = [0x00, 0x01, 0x02, 0x03]
TILESETS = os.path.join(DISASM, 'rooms', 'ages', 'group1Tilesets.bin')
WARP = 0xcc47          # wWarpDestVariables
NEW_GAME = ('w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a').split()


def layout_group(tileset):
    """Groupe de disposition du décor (octet 6 de tilesetData) : les salles sont lues dans
    rooms/ages/small/roomGGSS.bin (GG = ce groupe, SS = salle)."""
    lines = open(os.path.join(DISASM, 'data', 'ages', 'tilesets.s'), encoding='utf-8').read().split('\n')
    i = lines.index('\t; 0x%02x' % tileset)
    last = lines[i + 5].replace('.db', '').split(',')   # b5, b6, b7
    return int(last[1].strip()[1:], 16)


LAYOUT = None


def room_path(room):
    return os.path.join(DISASM, 'rooms', 'ages', 'small', 'room%02x%02x.bin' % (LAYOUT, room))


def prepare(tileset):
    global LAYOUT
    LAYOUT = layout_group(tileset)
    t = bytearray(open(TILESETS, 'rb').read())
    for i, room in enumerate(ROOMS):
        t[room] = tileset | 0x80
        with open(room_path(room), 'wb') as f:
            f.write(bytes(min(255, i * 80 + k) for k in range(80)))
    open(TILESETS, 'wb').write(t)


def restore():
    files = ['rooms/ages/group1Tilesets.bin'] + ['rooms/ages/small/room%02x%02x.bin' % (LAYOUT, r) for r in ROOMS]
    subprocess.run(['git', 'checkout', '--'] + files, cwd=DISASM, check=True)


def run(pb, script):
    for cmd in script:
        if cmd[0] == 'w':
            pb.tick(int(cmd[1:]), True)
        else:
            pb.button(cmd, 3)
            pb.tick(4, True)


def label(d, f, x0, y0, sc, ids):
    for k, n in enumerate(ids):
        x, y = x0 + (k % 10) * 16 * sc, y0 + (k // 10) * 16 * sc
        d.rectangle([x, y, x + 20, y + 13], fill=(0, 0, 0))
        d.text((x + 1, y), '%02x' % n, font=f, fill=(255, 255, 0))


def shoot_rooms(rooms):
    pb = PyBoy(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), window='null', sound_emulated=True)
    pb.set_emulation_speed(0)
    run(pb, NEW_GAME)
    pb.tick(300, True)
    t = open(TILESETS, 'rb').read()
    sc, cols = 3, 3
    rows = (len(rooms) + cols - 1) // cols
    sheet = Image.new('RGB', (160 * sc * cols, (128 * sc + 20) * rows), 'black')
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 13)
    big = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 16)
    for i, room in enumerate(rooms):
        for j, v in enumerate((0x81, room, 0x00, 0x00, 0x03)):
            pb.memory[WARP + j] = v
        pb.tick(150, True)
        im = pb.screen.image.convert('RGB').crop((0, 16, 160, 144))
        x0, y0 = (i % cols) * 160 * sc, (i // cols) * (128 * sc + 20)
        sheet.paste(im.resize((160 * sc, 128 * sc), Image.NEAREST), (x0, y0 + 20))
        global LAYOUT
        LAYOUT = layout_group(t[room] & 0x7f)
        ids = open(room_path(room), 'rb').read()
        label(d, f, x0, y0 + 20, sc, ids)
        d.text((x0 + 4, y0 + 2), 'salle 1:%02x  decor %02x' % (room, t[room] & 0x7f), font=big, fill=(255, 255, 255))
    pb.stop(save=False)
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, 'salles.png')
    sheet.save(out)
    print('->', os.path.relpath(out, ROOT))


def shoot(tileset):
    pb = PyBoy(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), window='null', sound_emulated=True)
    pb.set_emulation_speed(0)
    run(pb, NEW_GAME)
    pb.tick(300, True)
    shots = []
    for room in ROOMS:
        for i, v in enumerate((0x81, room, 0x00, 0x00, 0x03)):
            pb.memory[WARP + i] = v
        pb.tick(150, True)
        shots.append(pb.screen.image.convert('RGB').crop((0, 16, 160, 144)))
    pb.stop(save=False)
    # Planche : 4 salles l'une sous l'autre, numéros en surimpression
    sc = 3
    sheet = Image.new('RGB', (160 * sc, 128 * sc * 4), 'black')
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 13)
    for i, im in enumerate(shots):
        sheet.paste(im.resize((160 * sc, 128 * sc), Image.NEAREST), (0, i * 128 * sc))
        for k in range(80):
            n = i * 80 + k
            if n > 255:
                break
            x, y = (k % 10) * 16 * sc, i * 128 * sc + (k // 10) * 16 * sc
            d.rectangle([x, y, x + 20, y + 13], fill=(0, 0, 0))
            d.text((x + 1, y), '%02x' % n, font=f, fill=(255, 255, 0))
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, 'decor_%02x.png' % tileset)
    sheet.save(out)
    print('->', os.path.relpath(out, ROOT))


def main():
    if sys.argv[1] == '--salles':
        shoot_rooms([int(a, 16) for a in sys.argv[2:]])
        return
    for arg in sys.argv[1:]:
        tileset = int(arg, 16)
        prepare(tileset)
        try:
            r = subprocess.run(['bash', os.path.join(ROOT, 'build.sh')], cwd=ROOT,
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
            if r.returncode:
                print(r.stdout[-2000:], r.stderr[-2000:])
                sys.exit(1)
            shoot(tileset)
        finally:
            restore()
    # Remettre la ROM normale
    subprocess.run(['bash', os.path.join(ROOT, 'build.sh')], cwd=ROOT, capture_output=True)


main()
