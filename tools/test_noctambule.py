"""Mesure du noctambule : le trajet idéal de la porte de l'auberge du Songe à l'autre côté de la mer
ouverte (le temps donné dans BALLADE_NOCTAMBULE_FRAMES, constants/common/version.s).

Usage : python tools/test_noctambule.py DOSSIER_CAPTURES
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


def timer():
    return pb.memory[0xcde6] | pb.memory[0xcde7] << 8


def walk_until(button, test, limit=600):
    pb.button_press(button)
    for _ in range(limit):
        w(1)
        if pb.memory[0xcba0]:   # Marine prévient : on ferme sa boîte et on continue
            shot()
            pb.button_release(button)
            for _ in range(40):
                press('a', 4)
                if not pb.memory[0xcba0]:
                    break
            pb.button_press(button)
        if test():
            break
    pb.button_release(button)


# Nouvelle partie (la langue : français), scène de la plage
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(200):
    press('a', 22)
    if pb.memory[0xcc8a] == 0 and i > 80:
        break
w(60)
# Le lit de l'auberge (« Dormir un peu ? » : Oui), puis le Songe ; les retrouvailles : on passe
# les textes jusqu'à ce que Link soit libre
warp(3, 0x9e, 0x17)
walk('right', 6)
press('a', 4)
for i in range(60):
    w(4)
    if pb.memory[0xcba0]:
        break
w(150)
press('a', 4)
for i in range(300):
    w(4)
    if pb.memory[0xcc2d] == 2:
        break
free = 0
for i in range(2000):
    w(4)
    if pb.memory[0xcba0]:
        free = 0
        if i % 4 == 0:
            press('a', 2)
    elif pb.memory[0xcc8a] == 0 and pb.memory[0xcc2d] == 2 and pb.memory[0xd004] == 1:
        free += 1
        if free > 15:
            break
where('réveil dans le Songe')
print('objets', [(hex(pb.memory[h*0x100+0x41]), hex(pb.memory[h*0x100+0x42])) for h in range(0xd2,0xe0) if pb.memory[h*0x100+0x40]], 'link etat', hex(pb.memory[0xd004]), 'cc8a', pb.memory[0xcc8a], 'menu', pb.memory[0xcc8f] if False else '')
shot()
# Sortir de l'auberge : descendre devant le meuble, à gauche, puis la porte en bas
goto(y=0x38)
goto(x=0x50)
walk_until('down', lambda: pb.memory[0xcc2d] == 0)
# Le temps du noctambule commence dès l'arrivée dehors
walk_until('down', lambda: timer() != 0, limit=120)
start = timer()
where('devant l auberge')
print('temps au départ', start)
# Port-Veille : à gauche, puis tout droit vers le nord (le sentier)
goto(x=0x28)
walk_until('up', lambda: pb.memory[0xcc30] == 0x8a)
where('sentier')
# Le sentier : monter au niveau de la mer ouverte, puis la traverser vers l'est
goto(y=0x40)
walk_until('right', lambda: pb.memory[0xd00d] >= 0x78)
where('de l autre coté')
end = timer()
print('temps restant', end, '-> trajet', start - end, 'images, soit %.1f secondes' % ((start - end) / 60))
shot()
# Le temps s'écoule : Marine prévient, puis Link se réveille de l'autre côté (dans le Réel)
for i in range(120):
    w(10)
    if pb.memory[0xcba0]:
        shot()
        press('a', 4)
    if pb.memory[0xcc2d] == 1:
        break
w(120)
where('réveil')
shot()
