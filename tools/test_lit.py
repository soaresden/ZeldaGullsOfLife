"""Test du lit de l'auberge : A devant le lit, « Dormir un peu ? », oui, Link s'endort et passe dans le Songe (retrouvailles avec Marine).

Usage : python tools/test_lit.py DOSSIER_CAPTURES [dessous]
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
# Devant le lit de l'auberge (3:9e), tourné vers lui
# Devant l'oreiller (par défaut) ou sous le lit (argument « dessous »)
if len(sys.argv) > 2 and sys.argv[2] == 'dessous':
    warp(3, 0x9e, 0x38)
    walk('up', 6)
else:
    warp(3, 0x9e, 0x17)
    walk('right', 6)
where('devant le lit')
press('a', 30)
shot_n = [0]


def snap():
    pb.screen.image.save(os.path.join(OUT, 'lit_%03d.png' % shot_n[0]))
    shot_n[0] += 1


snap()
press('a', 30)   # « Oui »
for i in range(150):
    w(6)
    if pb.memory[0xcba0] and i % 10 == 9:
        press('a', 2)
    if i % 2 == 0:
        snap()
where('fin')
