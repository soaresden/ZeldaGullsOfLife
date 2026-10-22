"""Teste la barre d'état en bas (option hud, tools/options.py) : les mêmes scènes avec la barre en
haut et en bas, côte à côte.

Le village (dehors), une boîte de texte de Marine, le passage à l'écran voisin, l'inventaire
(Start), la carte (Select), le Songe (l'ondulation), un intérieur, un donjon. Vérifie que la barre
n'est en bas que si l'option est mise (wBalladeHudBas).

Usage : python tools/test_hud.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
Fabrique DOSSIER/gulls_hud_bas.gbc (tools/options.py), écrit DOSSIER/haut_*.png, DOSSIER/bas_*.png
et DOSSIER/planche.png (une ligne par scène : en haut | en bas).
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import ROOT, Game  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
ROM = os.environ.get('ROM') or os.path.join(ROOT, 'out', 'gulls_of_life.gbc')
ROM_BAS = os.path.join(OUT, 'gulls_hud_bas.gbc')
HUD_BAS = 0xc593        # wBalladeHudBas
SELECT_HOLD = 20        # BALLADE_SELECT_HOLD_FRAMES

subprocess.check_call([sys.executable, os.path.join(ROOT, 'tools', 'options.py'), ROM, 'hud=bas',
                       ROM_BAS])
errors = []


def check(ok, what):
    print(('ok    ' if ok else 'ÉCHEC ') + what)
    if not ok:
        errors.append(what)


def scenes(name, rom, bottom):
    g = Game(rom)
    shots = []
    expected = 1 if bottom else 0

    def shot(scene):
        path = os.path.join(OUT, '%s_%02d.png' % (name, len(shots)))
        g.shot(path)
        shots.append((path, scene))

    g.level(1, 'Ville', 'fr')
    check(g.m[HUD_BAS] == expected, '%s : en jeu, wBalladeHudBas = %d' % (name, expected))
    shot('le village')

    # Marine parle (Select maintenu)
    g.hold('select', SELECT_HOLD + 10)
    g.wait_text()
    g.w(60)
    shot('Marine parle')
    g.text_through()
    g.w(20)

    # Le passage à l'écran voisin (photo pendant le défilement)
    # (une direction après l'autre, jusqu'à ce que l'écran défile)
    start = g.where()
    for direction in ('down', 'left', 'right', 'up'):
        g.pb.button_press(direction)
        for _ in range(240):
            g.w()
            if g.where() != start or not (g.m[0xcd00] & 1):
                break
        if g.where() != start or not (g.m[0xcd00] & 1):
            break
        g.pb.button_release(direction)
    g.w(12)
    shot('défilement')
    g.w(60)
    g.pb.button_release(direction)
    g.settled()
    g.w(20)
    check(g.where() != start, '%s : passage à l\'écran voisin (%d:%02x)' % ((name,) + g.where()))
    shot("l'écran voisin")

    # L'inventaire
    g.press('start', 60)
    check(g.m[HUD_BAS] == (2 if bottom else 0), '%s : inventaire, wBalladeHudBas = %d'
          % (name, 2 if bottom else 0))
    shot('inventaire')
    g.press('start', 60)
    g.settled()

    # La carte (Select court)
    g.press('select', 70)
    shot('la carte')
    g.press('select', 60)
    g.press('b', 60)
    g.settled()
    g.w(20)

    # Le Songe : l'ondulation
    group, room = g.where()
    g.warp(group ^ 1, room, 0x55)
    g.settled()
    g.w(90)
    check(g.m[HUD_BAS] == expected, '%s : Songe, wBalladeHudBas = %d' % (name, expected))
    shot('le Songe (ondulation)')

    # Un intérieur (l'auberge) et un donjon
    g.warp(3, 0x9e, 0x55)
    g.settled()
    g.w(40)
    shot("l'auberge")
    g.warp(4, 0x1b, 0x57)
    g.settled()
    g.w(60)
    shot('le Phare (donjon 1)')
    g.stop()
    return shots


haut = scenes('haut', ROM, False)
bas = scenes('bas', ROM_BAS, True)

W, H = 320, 288 + 18
sheet = Image.new('RGB', (W * 2, H * len(haut)), (16, 16, 32))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 14)
except OSError:
    font = ImageFont.load_default()
for row, ((p1, label), (p2, _)) in enumerate(zip(haut, bas)):
    for col, (p, side) in enumerate(((p1, 'en haut'), (p2, 'en bas'))):
        sheet.paste(Image.open(p).convert('RGB').resize((W, 288), Image.NEAREST), (col * W, row * H + 18))
        d.text((col * W + 4, row * H + 1), '%s - barre %s' % (label, side), fill=(255, 255, 255),
               font=font)
sheet.save(os.path.join(OUT, 'planche.png'))
print('->', os.path.join(OUT, 'planche.png'))
if errors:
    sys.exit('%d échec(s)' % len(errors))
print('Tout est bon.')
