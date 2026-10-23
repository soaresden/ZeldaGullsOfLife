"""Test du temple du Phare, joué de bout en bout comme un joueur : la clé des Zols, la statue sur
le bouton, la porte à clé, la Lanterne, le mur qui brûle, le cristal (le pont de la douve), la
garde, la douve, les torches du pied du phare, le bloc à serrure, le mini-boss, les 3 torches, la
porte du balcon ouest et sa statue (la clé du boss), le balcon est, puis Jack : sa citrouille
tombe, la Lanterne la brûle, son fantôme est à découvert.

Seule triche : les ennemis sont retirés (sauf Jack), et Link garde sa vie pleine. L'épée vient du
vieux pêcheur, comme dans le jeu.

Usage : python tools/test_temple.py DOSSIER_CAPTURES
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
ROOM_LAYOUT = 0xcf00
TORCHES = 0xcc8f          # wNumTorchesLit
RUPEES = 0xc6ad           # wNumRupees (BCD)
SMALL_KEYS = 0xc672 + 1   # wDungeonSmallKeys, donjon 1
BOSS_KEYS = 0xc682        # wDungeonBossKeys
SWITCH = 0xcdd3           # wSwitchState
ENEMY = {'id': 0x81, 'subid': 0x82, 'state': 0x84, 'yh': 0x8b, 'xh': 0x8d,
         'collision': 0xa4, 'health': 0xa9}
errors = []


def w(n):
    for _ in range(n):
        m[0xc6aa] = m[0xc6ab]   # vie pleine
        pb.tick(1, True)


def press(b, n=4):
    pb.button(b, 3)
    w(n)


def walk(b, n):
    pb.button_press(b)
    w(n)
    pb.button_release(b)
    w(4)


def shot(name):
    pb.screen.image.save(os.path.join(OUT, name + '.png'))


def room():
    return m[0xcc30]


def rupees():
    bcd = lambda v: (v >> 4) * 10 + (v & 15)
    return bcd(m[RUPEES]) + 100 * bcd(m[RUPEES + 1])


def where(t):
    print(t, 'groupe', m[0xcc2d], 'salle', hex(room()), 'y', hex(m[0xd00b]), 'x', hex(m[0xd00d]),
          'clés', m[SMALL_KEYS], 'rubis', rupees())


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        where('  (là)')
        shot('rate_%02d' % len(errors))


def goto(y=None, x=None, limit=400):
    """Guide Link jusqu'à une position (en pixels), un axe puis l'autre."""
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


def stand(row, col, yx_first=False):
    """Amener Link au centre d'une case (d'abord en x, ou d'abord en y)."""
    y, x = row * 16 + 8, col * 16 + 8
    if yx_first:
        goto(y, None)
        goto(None, x)
    else:
        goto(None, x)
        goto(y, None)


def warp(g, r, pos):
    for i, v in enumerate((0x80 | g, r, 0x00, pos, 0x03)):
        m[0xcc47 + i] = v
    w(220)


def go(direction, target, limit=40):
    """Marcher vers une porte jusqu'à changer de salle (et faire un pas dans la salle)."""
    for _ in range(limit):
        walk(direction, 20)
        if room() == target:
            break
    w(60)
    walk(direction, 14)
    check(room() == target, 'arrivée en 4:%02x' % target)


def tile(row, col):
    return m[ROOM_LAYOUT + row * 16 + col]


def clear_enemies():
    """La seule triche : les ennemis de la salle n'ont plus de vie (ils meurent comme d'un coup
    d'épée : le mini-boss lance sa fin, les volets s'ouvrent)."""
    for _ in range(3):
        for d in range(0xd0, 0xe0):
            base = d << 8
            if m[base + 0x80] and m[base + ENEMY['id']] != 0x78:
                m[base + ENEMY['health']] = 0
        w(90)


def open_chest(row, col, name):
    """Ouvrir le coffre (row, col) par en dessous ; rend (clés gagnées, clé du boss, rubis gagnés)."""
    stand(row + 1, col, yx_first=True)
    walk('up', 12)
    keys, boss, money = m[SMALL_KEYS], m[BOSS_KEYS], rupees()
    press('a', 60)
    text_through(20)
    w(60)
    check(tile(row, col) == 0xf0, 'coffre ouvert : ' + name)
    return m[SMALL_KEYS] - keys, m[BOSS_KEYS] != boss, rupees() - money


def push(direction, times):
    for _ in range(times):
        walk(direction, 40)
        w(16)


def button(item):
    """Le bouton (A ou B) où est rangé un objet (5 = l'épée, $11 = la Lanterne)."""
    return 'b' if m[0xc688] == item else 'a'


def lantern(face):
    walk(face, 3)
    press(button(0x11), 10)
    w(90)


def sword(face):
    walk(face, 3)
    press(button(0x05), 30)


def text_through(n=40):
    """Faire défiler un texte jusqu'au bout (sans relancer une discussion)."""
    for _ in range(n):
        if not m[0xcba0]:
            w(20)
            if not m[0xcba0]:
                return
        press('a', 20)


def route(*cells):
    """Amener Link de case en case (chaque étape : d'abord en x, puis en y)."""
    for row, col in cells:
        stand(row, col)


# --- Nouvelle partie, la plage ---
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if m[0xcc8a] == 0 and i > 60:
        break
w(60)

# --- L'épée : le vieux pêcheur (1:ab, case 3,5) ---
warp(1, 0xab, 0x45)
walk('up', 4)
press('a', 40)
text_through(70)
w(60)
check(5 in (m[0xc688], m[0xc689]), "l'épée du pêcheur")

# --- Le Phare : l'entrée, puis les Zols (clé 1) ---
warp(4, 0x24, 0x97)
text_through(6)
route((5, 7), (5, 2))
go('left', 0x1e)
clear_enemies()
keys, _, _ = open_chest(5, 7, 'les Zols')
check(keys == 1, 'petite clé 1')

# --- La statue sur le bouton (30 rubis), la porte à clé ---
route((6, 13), (5, 13))
go('right', 0x24)
route((5, 12))
go('right', 0x1f)
# la statue (6,4) : à droite jusqu'au pilier (6,8), en haut jusqu'à (3,8), à droite jusqu'au bouton (3,10)
route((5, 3), (6, 3))
push('right', 4)
route((7, 7), (7, 8))
push('up', 3)
route((3, 7))
push('right', 2)
w(60)
check(tile(8, 12) == 0xf1, 'la statue sur le bouton : le coffre apparaît')
shot('statue')
route((3, 11), (9, 11))
_, _, money = open_chest(8, 12, 'la statue')
check(money == 30, '30 rubis')
route((9, 7), (1, 7))
go('up', 0x15)

# --- La Lanterne ---
clear_enemies()
open_chest(5, 7, 'la Lanterne')
check(0x11 in (m[0xc688], m[0xc689]), 'la Lanterne (A ou B)')

# --- Le mur fissuré brûle ; le cristal ; 50 rubis ---
route((6, 13), (5, 13))
lantern('right')
w(60)
shot('mur_brule')
go('right', 0x1d)
clear_enemies()
route((4, 2), (4, 11), (5, 11))
sword('left')
w(60)
check(bool(m[SWITCH] & 1), 'le cristal frappé')
route((3, 12))
_, _, money = open_chest(2, 12, 'derrière le mur')
check(money == 50, '50 rubis')
route((3, 1), (5, 1))
go('left', 0x15)

# --- La garde (volet), la douve (le pont, la clé 2) ---
route((8, 13), (8, 1), (5, 1))
go('left', 0x14)
route((5, 1))
go('left', 0x1b)
clear_enemies()
route((5, 1))
go('left', 0x1c)
check(tile(5, 7) == 0xa0, 'le pont de la douve est là')
shot('douve')
route((5, 4))
keys, _, _ = open_chest(5, 3, 'la douve')
check(keys == 1, 'petite clé 2')
route((6, 4), (5, 4), (5, 13))
go('right', 0x1b)
route((5, 13))
go('right', 0x14)

# --- Le pied du phare : les 2 torches ---
route((5, 5), (2, 5))
lantern('up')
route((2, 9))
lantern('up')
w(60)
check(m[TORCHES] == 2 and tile(0, 7) == 0xa0, 'pied du phare : 2 torches, la tour ouverte')
route((2, 7), (1, 7))
go('up', 0x16)

# --- La tour, bas : les torches, le bloc à serrure ---
route((9, 5), (2, 5))
lantern('up')
route((2, 9))
lantern('up')
route((2, 7))
walk('up', 40)
w(60)
check(tile(1, 7) == 0xa0, 'le bloc à serrure')
shot('tour_bas')
route((1, 7))
go('up', 0x18)

# --- Le mini-boss : il arrive quand les volets se sont refermés derrière Link ---
def miniboss_here():
    return any(m[(d << 8) + 0x80] and m[(d << 8) + ENEMY['id']] == 0x70 for d in range(0xd0, 0xe0))


for _ in range(60):
    w(20)
    if miniboss_here() and m[0xcc8a] == 0:
        break
check(miniboss_here(), 'le Ghini géant est là')
w(60)
clear_enemies()
w(300)
check(m[0xcc8a] == 0 and tile(0, 7) == 0xa0, 'mini-boss battu : Link libre, le volet ouvert')
# (au milieu, le portail du mini-boss ramène à l'entrée : on le contourne)
route((9, 3), (1, 3), (1, 7))
go('up', 0x17)

# --- La tour, haut : 3 torches, la clé 3 ---
route((9, 7))
lantern('up')
route((9, 2), (3, 2))
lantern('up')
route((3, 12))
lantern('up')
w(60)
check(tile(5, 7) == 0xf1, '3 torches : le coffre apparaît')
route((6, 12))
keys, _, _ = open_chest(5, 7, 'la tour')
check(keys == 1, 'petite clé 3')
route((6, 10), (1, 10), (1, 7))
go('up', 0x12)

# --- La galerie, le balcon ouest (porte à clé, la statue, la clé du boss) ---
clear_enemies()
route((5, 7), (5, 1))
go('left', 0x19)
# la statue (7,6) : à gauche jusqu'au pilier (7,5), en haut jusqu'à (2,5), à gauche jusqu'au bouton (2,2)
route((5, 7), (7, 7))
push('left', 1)
route((8, 6), (8, 5))
push('up', 5)
route((3, 6), (2, 6))
push('left', 3)
w(60)
check(tile(5, 10) == 0xf1, 'la statue sur le bouton : le coffre de la clé du boss')
_, boss, _ = open_chest(5, 10, 'le balcon ouest')
check(boss, 'la clé du boss')
route((6, 13), (5, 13))
go('right', 0x12)

# --- Le balcon est : le bloc, 100 rubis ---
clear_enemies()
route((5, 13))
go('right', 0x1a)
clear_enemies()
route((5, 11), (2, 11))
push('right', 1)
_, _, money = open_chest(1, 12, 'le balcon est')
check(money == 100, '100 rubis')
route((2, 1), (5, 1))
go('left', 0x12)

# --- Jack ---
route((5, 7), (1, 7))
go('up', 0x13, limit=60)
for i in range(30):
    if m[0xcba0]:
        shot('jack_%02d' % i)
    press('a', 30)
walk('up', 30)
w(200)


def bosses():
    out = []
    for d in range(0xd0, 0xe0):
        base = d << 8
        if m[base + 0x80] and m[base + ENEMY['id']] == 0x78:
            out.append(base)
    return out


bs = bosses()
body = [b for b in bs if m[b + ENEMY['subid']] == 1]
ghost = [b for b in bs if m[b + ENEMY['subid']] == 2]
head = [b for b in bs if m[b + ENEMY['subid']] == 3]
check(bool(body and ghost and head), 'Jack est là')
if body and ghost and head:
    body, ghost, head = body[0], ghost[0], head[0]
    check(m[body + ENEMY['health']] == 24, 'Jack : 24 points de vie')
    m[body + ENEMY['health']] = 0
    for i in range(300):
        w(1)
        if m[head + ENEMY['state']] == 0x12:
            break
    goto(m[head + ENEMY['yh']] + 14, m[head + ENEMY['xh']])
    walk('up', 2)
    press(button(0x11), 6)
    for i in range(60):
        w(1)
        if m[head + ENEMY['state']] == 0x17:
            break
    check(m[head + ENEMY['state']] == 0x17 and bool(m[ghost + ENEMY['collision']] & 0x80),
          'la citrouille brûle, le fantôme est à découvert')
    shot('jack_brule')
    m[ghost + ENEMY['health']] = 0
    w(600)
    check(bool(m[0xc900 + 0x13] & 0x80), 'Jack est vaincu')
    for i in range(3):
        stand(9, 7)
        text_through(8)
    goto(None, 0x58)
    goto(0x18, None)
    goto(None, 0x78)
    for i in range(30):
        walk('up', 30)
        if room() == 0x11:
            break
    w(120)
    check(room() == 0x11, 'la lumière (essence)')
where('fin')
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
