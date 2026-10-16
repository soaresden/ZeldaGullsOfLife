"""Test de la Lanterne des Songes dans PyBoy : dehors, elle fait passer du Réel au Songe et retour.

Usage : python tools/test_lanterne.py DOSSIER_CAPTURES
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
# La Lanterne, dans son coffre (4:15, ligne 5 colonne 7) : Link juste dessous, face au coffre
warp(4, 0x15, 0x67)
walk('up', 8)
press('a', 60)
for i in range(8):
    press('a', 30)
print('bouton B', hex(pb.memory[0xc688]), 'air', pb.memory[0xc6b7])
# Dehors, au village : Lanterne -> Songe
warp(1, 0x9a, 0x55)
w(60)
where('village (Réel)')
shot()
press('b', 10)
for i in range(12):
    w(60)
    if i % 3 == 0:
        shot()
w(200)
where('après la Lanterne')
shot()
press('b', 10)
w(900)
where('encore la Lanterne')
shot()
# Sur le pont du Songe : en dessous, dans le Réel, c'est l'eau
warp(0, 0x8a, 0x35)
w(60)
where('pont du Songe')
shot()
press('b', 10)
w(900)
where('Lanterne sur le pont')
shot()
w(300)
where('plus tard')
shot()
