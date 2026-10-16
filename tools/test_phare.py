"""Test du Phare Éteint dans PyBoy : clé du boss, combat (la vie du boss est mise à zéro),
réceptacle de cœur, essence (le premier couplet) et ce qui suit.

Usage : python tools/test_phare.py DOSSIER_CAPTURES
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
    pb.memory[0xc6aa] = pb.memory[0xc6ab]   # vie pleine : le test traverse le donjon au pas de course
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
warp(1, 0x7b, 0x54)
walk('up', 50)
w(150)
warp(4, 0x1c, 0x6a)
walk('up', 8)
press('a', 60)
for i in range(6):
    press('a', 30)
warp(4, 0x12, 0x7c)
# Les fantômes de l'antichambre repoussent Link : on les fait disparaître
for h in range(0xd0, 0xe0):
    if pb.memory[h * 0x100 + 0x80]:
        pb.memory[h * 0x100 + 0xa9] = 0
w(60)
walk('right', 60)
w(150)
walk('right', 40)
w(300)
where('salle du boss')
for h in range(0xd0, 0xe0):
    if pb.memory[h * 0x100 + 0x80] and pb.memory[h * 0x100 + 0x81] == 0x78:
        pb.memory[h * 0x100 + 0xa9] = 0
w(400)
shot()
# Le réceptacle de cœur, puis la porte du haut (colonne 7)
inter = [(pb.memory[h * 0x100 + 0x41], pb.memory[h * 0x100 + 0x4b], pb.memory[h * 0x100 + 0x4d])
         for h in range(0xd2, 0xe0) if pb.memory[h * 0x100 + 0x40]]
print('interactions', [(hex(i), hex(y), hex(x)) for i, y, x in inter])
hearts = [(y, x) for i, y, x in inter if i == 0x60]   # INTERAC_TREASURE
if hearts:
    goto(y=hearts[0][0], x=hearts[0][1])
w(60)
shot()
for i in range(10):
    press('a', 30)
goto(x=0x78)
goto(y=0x18)
walk('up', 80)
w(100)
w(120)
where('salle de l essence')
shot()
goto(y=0x48, limit=600)
w(30)
where('devant l essence')
shot()
walk('up', 40)
w(60)
shot()
for i in range(60):
    press('a', 30)
    if i % 6 == 0:
        shot()
w(300)
shot()
where('fin')
w(600)
shot()
where('plus tard')
# La fin du chapitre : Marine parle, « À suivre... », puis retour au jeu sur le cap
for i in range(100):
    w(10)
    if i % 3 == 0:
        shot()
    if i % 6 == 5:
        press('a', 4)
w(400)
shot()
where('retour au jeu')
