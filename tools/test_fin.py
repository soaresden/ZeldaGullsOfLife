"""Test rapide de la fin du chapitre 1 (Marine sur le cap, « À suivre... ») dans PyBoy.

Usage : python tools/test_fin.py DOSSIER_CAPTURES
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
# Comme après le Phare : la première essence, puis le cap
pb.memory[0xc6bf] |= 1
warp(1, 0x7b, 0x44)
# Le tour du village : le cap, la place, la plage, l'auberge, le port (texte -> capture)
rooms, last = [], None
for i in range(500):
    w(10)
    room = (pb.memory[0xcc2d], pb.memory[0xcc30])
    if room != last:
        rooms.append('%d:%02x' % room)
        last = room
    if pb.memory[0xcba0] and i % 4 == 0:
        shot()
    if i % 6 == 5:
        press('a', 4)
    if len(rooms) >= 5 and pb.memory[0xcdf4] == 0 and not pb.memory[0xcba0] and i > 60:
        break
print('salles', ' '.join(rooms))
print('étape', pb.memory[0xcdf4], 'Link peut bouger', pb.memory[0xcc8a] == 0)
where('fin')
