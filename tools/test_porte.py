"""Test de la porte à clé du rez-de-chaussée du Phare (petite clé de la salle ouest).

Usage : python tools/test_porte.py DOSSIER_CAPTURES
"""
import os
import sys

from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
pb = PyBoy(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), window='null', sound_emulated=True)
pb.set_emulation_speed(0)
shots = [0]


def w(n):
    pb.tick(n, True)


def press(b, n=4):
    pb.button(b, 3)
    w(n)


def walk(b, n):
    pb.button_press(b)
    w(n)
    pb.button_release(b)
    w(4)


def shot():
    pb.screen.image.save(os.path.join(OUT, '%02d.png' % shots[0]))
    shots[0] += 1


def where(t):
    m = pb.memory
    print(t, 'groupe', m[0xcc2d], 'salle', hex(m[0xcc30]), 'y', hex(m[0xd00b]), 'x', hex(m[0xd00d]))


def goto(y=None, x=None, limit=400):
    """Guide Link jusqu'à une position (en pixels), un axe puis l'autre."""
    for axis, target, minus, plus in (('x', x, 'left', 'right'), ('y', y, 'up', 'down')):
        if target is None:
            continue
        addr = 0xd00d if axis == 'x' else 0xd00b
        for _ in range(limit):
            cur = pb.memory[addr]
            if abs(cur - target) <= 1:
                break
            b = minus if cur > target else plus
            pb.button_press(b)
            w(2)
            pb.button_release(b)


def warp(g, r, pos):
    for i, v in enumerate((0x80 | g, r, 0x00, pos, 0x03)):
        pb.memory[0xcc47 + i] = v
    w(220)


# Nouvelle partie, scène de la plage
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if pb.memory[0xcc8a] == 0 and i > 60:
        break
w(60)
# La petite clé (4:1b, coffre en ligne 5 colonne 4), puis la porte à clé du hall (4:24, à l'est)
warp(4, 0x1b, 0x64)
walk('up', 8)
press('a', 60)
for i in range(6):
    press('a', 30)
print('petites clés', [hex(pb.memory[0xc672 + k]) for k in range(4)])
pb.screen.image.save(os.path.join(OUT, 'cle.png'))
warp(4, 0x24, 0x5c)
where('hall')
print('musique', hex(pb.memory[0xcc2f]) if False else '', hex(pb.memory[0xcd45]) if False else '')
pb.screen.image.save(os.path.join(OUT, 'hall.png'))
walk('right', 90)
w(60)
pb.screen.image.save(os.path.join(OUT, 'porte.png'))
walk('right', 60)
w(120)
where('après la porte')
pb.screen.image.save(os.path.join(OUT, 'apres.png'))
