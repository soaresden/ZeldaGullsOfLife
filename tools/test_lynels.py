"""Test du Labyrinthe des Lynels (le 3e jeu du forain, salle 5:e9, code/ages/balladePac.s) : on y
arrive (Link n'a que son épée, sur B), les rubis sont comptés, les Lynels sortent de l'enclos et
poursuivent Link, un rubis ramassé, une gemme (ils ont peur, Link brille : le toucher ne fait rien,
un coup d'épée en terrasse un), un Lynel attrape Link (il ne lui reste qu'un cœur, tous à l'enclos),
puis tous les rubis (le 2e labyrinthe, puis gagné, retour chez le forain : ses objets reviennent) ;
enfin une défaite.

Usage : python tools/test_lynels.py DOSSIER_CAPTURES
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
HEALTH, MAX_HEALTH, RUPEES = 0xc6aa, 0xc6ab, 0xc6ad
STATE, LEFT, POWER, COMBO, CAUGHT = 0xc5a0, 0xc5a1, 0xc5a2, 0xc5a3, 0xc5a4
LAYOUT = 0xcf00
LINK_Y, LINK_X = 0xd00b, 0xd00d
INVINCIBLE = 0xd02b
LINK_PAL = 0xd01c           # w1Link.oamFlags
INV_B, INV_A = 0xc688, 0xc689
TREASURES, SWORD_LEVEL = 0xc69a, 0xc6b2
ITEM_SWORD, ITEM_BOMBS = 0x05, 0x03
errors = []


def w(n):
    pb.tick(n, True)


def press(b, n=4):
    pb.button(b, 3)
    w(n)


def shot(name, scale=3):
    im = pb.screen.image
    im.resize((im.size[0] * scale, im.size[1] * scale)).save(os.path.join(OUT, name + '.png'))


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        shot('rate_%02d' % len(errors))


def where():
    return m[0xcc49 - 0x1d], m[0xcc30]


def lynels():
    """(sous-type, y, x, état, a peur) des Lynels (ennemis $0d) dans les emplacements d'ennemis."""
    out = []
    for slot in range(0xd0, 0xe0):
        base = slot << 8
        if m[base + 0x80] and m[base + 0x81] == 0x0d:
            o = base + 0x80
            out.append((m[o + 2], m[o + 0x0b], m[o + 0x0d], m[o + 0x30], m[o + 0x32]))
    return out


def warp(group, room, pos):
    for i, v in enumerate((0x80 | group, room, 0x00, pos, 0x03)):
        m[0xcc47 + i] = v
    w(200)


def text_through(n=40):
    for _ in range(n):
        if not m[0xcba0]:
            w(20)
            if not m[0xcba0]:
                return
        press('a', 20)


# Nouvelle partie
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if m[0xcc8a] == 0 and i > 60:
        break
w(60)
m[MAX_HEALTH] = 12
m[HEALTH] = 12
# Link a l'épée (sur A) et les bombes (sur B)
m[TREASURES] |= 1 << ITEM_SWORD
m[SWORD_LEVEL] = 1
m[INV_A], m[INV_B] = ITEM_SWORD, ITEM_BOMBS
warp(5, 0xe9, 0x77)
check(m[0xcc30] == 0xe9, 'le labyrinthe (5:e9)')
check(m[INV_B] == ITEM_SWORD and m[INV_A] == 0, "rien que l'épée, sur B (A %02x, B %02x)" % (m[INV_A], m[INV_B]))
check(m[STATE] == 1 and m[LEFT] == 69, 'la partie commence : %d rubis' % m[LEFT])
shot('arrivee')
w(240)
ls = lynels()
print('  Lynels', ls, flush=True)
check(len(ls) == 4, 'quatre Lynels')
shot('poursuite')
w(400)
ls2 = lynels()
print('  Lynels', ls2, flush=True)
check(sum(1 for l in ls2 if l[3] == 2) >= 2, 'ils sortent de l\'enclos')

# Un rubis : Link fait un pas à gauche (la case 7,6)
r0, left0 = m[RUPEES], m[LEFT]
m[LINK_Y], m[LINK_X] = 0x78, 0x78
for _ in range(4):
    pb.button_press('left')
    w(6)
    pb.button_release('left')
    w(2)
w(40)
check(m[LEFT] < left0 and m[LAYOUT + 0x76] == 0xa0, 'un rubis ramassé (%d -> %d)' % (left0, m[LEFT]))
check(m[RUPEES] != r0, 'un rubis de plus (%02x -> %02x)' % (r0, m[RUPEES]))

# Une gemme (1,1) : ils ont peur
m[LINK_Y], m[LINK_X] = 0x18, 0x18
w(10)
check(m[POWER] > 0 and m[LAYOUT + 0x11] == 0xa0, 'la gemme : les Lynels ont peur')
w(20)
ls = lynels()
check(all(l[4] for l in ls), 'tous ont peur ' + str(ls))
shot('peur')
pals = set()
for _ in range(16):
    pals.add(m[LINK_PAL] & 7)
    w(1)
check(pals == {0, 3}, 'Link brille (palettes %s)' % sorted(pals))
# Le toucher ne fait rien
out = [l for l in lynels() if l[3] == 2][0]
h0 = m[HEALTH]
m[LINK_Y], m[LINK_X] = out[1], out[2]
w(6)
check(m[COMBO] == 0 and m[HEALTH] == h0, 'le toucher ne fait rien (combo %d)' % m[COMBO])
# Un coup d'épée : terrassé, retour à l'enclos
for _ in range(6):
    out = [l for l in lynels() if l[0] == out[0]][0]
    m[LINK_Y], m[LINK_X] = out[1], (out[2] - 14) & 0xff
    pb.button_press('right')
    w(1)
    pb.button_release('right')
    m[LINK_Y], m[LINK_X] = out[1], (out[2] - 14) & 0xff
    press('b', 14)
    if m[COMBO]:
        break
back = [l for l in lynels() if l[0] == out[0]][0]
check(m[COMBO] == 1 and back[3] == 0 and back[1] == 0x58, "un coup d'épée terrasse le Lynel %d (retour à l'enclos)" % out[0])

# La peur passe ; un Lynel attrape Link : un cœur, tous à l'enclos
m[POWER] = 0
w(300)
check(m[LINK_PAL] & 7 == 0, 'Link ne brille plus')
m[HEALTH] = 12
red = [l for l in lynels() if l[0] == 3][0]
m[INVINCIBLE] = 0
m[LINK_Y], m[LINK_X] = red[1], red[2]
w(8)
check(m[HEALTH] == 4, "attrapé : il ne reste qu'un cœur (12 -> %d)" % m[HEALTH])
ls = lynels()
check(all(l[3] == 0 and l[1] == 0x58 for l in ls if l[0] != 3) and
      [abs(l[2] - 0x78) < 9 and abs(l[1] - 0x38) < 9 for l in ls if l[0] == 3] == [True], 'tous à l\'enclos ' + str(ls))

# Tous les rubis : gagné ; le forain envoie Link dans le 2e labyrinthe (5:ee), plus dur
m[LINK_Y], m[LINK_X] = 0x78, 0x78
w(150)
m[LEFT] = 1
m[LINK_Y], m[LINK_X] = 0x38, 0x18
w(10)
check(m[STATE] == 2, 'gagné')
w(30)
check(len(lynels()) == 0, 'les Lynels s\'en vont')
w(30)
shot('gagne')
pieces = m[0xc6ac]
for _ in range(3):
    text_through()
    w(60)
w(150)
check(m[0xcc30] == 0xee, 'le 2e labyrinthe (5:%02x)' % m[0xcc30])
check(m[0xc6ac] == pieces, 'pas encore de quart de cœur (il est au bout du 2e)')
check(not m[0xc616] & 0x02, "le 1er gagné : pas encore l'Anneau de Force (au 2e, Denis)")
w(150)
shot('labyrinthe2')
# Le 2e gagné : 50 rubis, un quart de cœur, retour chez le forain
m[LINK_Y], m[LINK_X] = 0x78, 0x78
w(60)
m[LEFT] = 1
m[INVINCIBLE] = 0x7f
m[LINK_Y], m[LINK_X] = 0x18, 0x28
w(10)
check(m[STATE] == 2, 'le 2e labyrinthe : gagné')
w(60)
for _ in range(4):
    text_through()
    w(60)
check(m[0xc6ac] != pieces, 'le 2e gagné : un quart de cœur (%d -> %d)' % (pieces, m[0xc6ac]))
for _ in range(6):
    w(60)
    text_through()
check(bool(m[0xc616] & 0x02) and 0x01 in [m[0xc6c6 + i] for i in range(5)],
      "le 2e gagné : l'Anneau de Force, dans la boîte")
w(200)
check(m[0xcc30] == 0xac, 'retour chez le forain (1:%02x)' % m[0xcc30])
check(m[INV_A] == ITEM_SWORD and m[INV_B] == ITEM_BOMBS, 'ses objets reviennent (A %02x, B %02x)' % (m[INV_A], m[INV_B]))

# Une défaite : attrapé avec un seul cœur
warp(5, 0xe9, 0x77)
w(300)
m[HEALTH] = 4
m[INVINCIBLE] = 0
red = [l for l in lynels() if l[0] == 3][0]
m[LINK_Y], m[LINK_X] = red[1], red[2]
w(8)
check(m[STATE] == 3 and m[HEALTH] == 4, 'perdu (un seul cœur) sans mourir')
w(60)
text_through()
w(200)
check(m[0xcc30] == 0xac, 'retour chez le forain')

print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
