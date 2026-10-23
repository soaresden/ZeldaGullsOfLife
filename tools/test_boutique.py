"""Test de la boutique de Port-Veille (la maison de gauche de la place) : on y entre, on achète 3
cœurs, la fée en bouteille, le bouclier de fer (150 rubis), et la fée relève Link quand il tombe à zéro cœur.

Usage : python tools/test_boutique.py DOSSIER_CAPTURES
"""
import os
import sys

from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
pb = PyBoy(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), window='null', sound_emulated=True)
pb.set_emulation_speed(0)
m = pb.memory
HEALTH, MAX_HEALTH = 0xc6aa, 0xc6ab
RUPEES = 0xc6ad
POTION = (0xc69a + 0x2f // 8, 1 << (0x2f % 8))   # TREASURE_POTION : la fée en bouteille
errors = []
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


def shot(name):
    pb.screen.image.save(os.path.join(OUT, '%02d_%s.png' % (shots[0], name)))
    shots[0] += 1


def rupees():
    bcd = lambda v: (v >> 4) * 10 + (v & 15)
    return bcd(m[RUPEES]) + 100 * bcd(m[RUPEES + 1])


def where(t):
    print(t, 'groupe', m[0xcc2d], 'salle', hex(m[0xcc30]), 'y', hex(m[0xd00b]), 'x', hex(m[0xd00d]),
          'vie', m[HEALTH], '/', m[MAX_HEALTH], 'rubis', rupees(), flush=True)


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        where('  (là)')
        shot('rate')


def goto(y=None, x=None, limit=300):
    for axis, target, minus, plus in (('x', x, 'left', 'right'), ('y', y, 'up', 'down')):
        if target is None:
            continue
        addr = 0xd00d if axis == 'x' else 0xd00b
        for _ in range(limit):
            cur = m[addr]
            if abs(cur - target) <= 1:
                break
            b = minus if cur > target else plus
            pb.button_press(b)
            w(2)
            pb.button_release(b)


def text_through(n=30):
    for _ in range(n):
        if not m[0xcba0]:
            w(20)
            if not m[0xcba0]:
                return
        press('a', 20)


def warp(g, r, pos):
    for i, v in enumerate((0x80 | g, r, 0x00, pos, 0x03)):
        m[0xcc47 + i] = v
    w(220)


def buy(item_x, name):
    """Prendre l'objet sur le comptoir, l'apporter au marchand, dire oui."""
    money = rupees()
    goto(None, 0x58)
    goto(0x40, None)
    goto(None, item_x)
    walk('up', 8)
    press('a', 30)
    shot('prend_' + name)
    # le marchand : on lui parle d'au-dessus, tourné vers lui
    goto(None, 0x88)
    goto(0x48, None)
    walk('down', 2)
    press('a', 40)
    shot('marchand_' + name)
    for _ in range(4):
        press('a', 30)   # le prix, puis « OK »
        shot('achat_' + name)
    text_through()
    w(60)
    return money - rupees()


# Nouvelle partie, la plage
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if m[0xcc8a] == 0 and i > 60:
        break
w(60)
m[RUPEES] = 0x99           # 99 rubis
m[HEALTH] = 4              # un seul cœur

# La place : la porte de la maison de gauche (ligne 3, colonne 2)
warp(1, 0x9b, 0x42)
shot('place')
walk('up', 30)
w(120)
where('dedans')
check(m[0xcc2d] == 3 and m[0xcc30] == 0x5e, 'la porte de la place mène à la boutique (3:5e)')
shot('boutique')

paid = buy(0x80, 'coeurs')
check(paid == 10 and m[HEALTH] > 4, '3 cœurs pour 10 rubis (vie %d)' % m[HEALTH])
paid = buy(0x68, 'fee')
check(paid == 60 and bool(m[POTION[0]] & POTION[1]), 'la fée en bouteille pour 60 rubis')
# Link a déjà un bouclier : le bouclier de fer (150)
m[RUPEES], m[RUPEES + 1] = 0x99, 0x01
paid = buy(0x50, 'bouclier')
check(paid == 150 and m[0xc6af] == 2, 'le bouclier de fer pour 150 rubis (payé %d, niveau %d)' % (paid, m[0xc6af]))

# Un coup qui devrait être fatal : la fée relève Link
m[HEALTH] = 2
m[0xd025] = 0xe0           # w1Link.damageToApply : 8 cœurs
for i in range(30):
    w(4)
    if i in (2, 8, 20):
        shot('fee_%d' % i)
where('après le coup')
check(m[HEALTH] == m[MAX_HEALTH] and not (m[POTION[0]] & POTION[1]), 'la fée a relevé Link, la bouteille est vide')
w(300)
check(m[0xcc2d] == 3, 'pas de Game Over')

# La sortie : devant la porte
goto(0x68, 0x60)
walk('down', 60)
w(120)
where('dehors')
check(m[0xcc2d] == 1 and m[0xcc30] == 0x9b, 'la sortie ramène sur la place')
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
