"""Test du Creuse-Rubis (la plage du forain, 1:ac) : une partie Facile gagnée (le test connaît les
bombes et ne creuse que les cases sûres ; chaque case creusée montre le nombre de bombes autour),
une partie Difficile gagnée (le quart de cœur), puis une bombe (BOUM, perdu). Deux niveaux.

Usage : python tools/test_creuse.py DOSSIER_CAPTURES
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
HEART_PIECES = 0xc6ac
INV_B, INV_A = 0xc688, 0xc689
ITEM_SWORD, ITEM_BOMBS, ITEM_SHOVEL = 0x05, 0x03, 0x15
STATE, LEVEL, MINES, DUG, LEFT = 0xcdf5, 0xcdf6, 0xcdf7, 0xcdfa, 0xcdfd
ROOM_FLAGS = 0xc800 + 0xac
errors = []


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
    pb.screen.image.save(os.path.join(OUT, name + '.png'))


def rupees():
    bcd = lambda v: (v >> 4) * 10 + (v & 15)
    return bcd(m[RUPEES]) + 100 * bcd(m[RUPEES + 1])


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        shot('rate_%02d' % len(errors))


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


def stand(row, col):
    goto(None, col * 16 + 8)
    goto(row * 16 + 8, None)


def text_through(n=40, choose=0):
    """Faire défiler un texte ; à chaque question, choisir l'option (ou une liste, une par menu)."""
    choices = list(choose) if isinstance(choose, (list, tuple)) else [choose]
    for _ in range(n):
        if not m[0xcba0]:
            w(20)
            if not m[0xcba0]:
                return
        if m[0xcba1] == 1 and choices:      # wTextDisplayMode : on choisit une option
            w(40)
            for _ in range(choices.pop(0)):
                walk('right', 6)
                w(16)
            press('a', 20)
            w(20)
            continue
        press('a', 20)


def bit(mask_addr, i):
    return bool(m[mask_addr + i // 8] & (1 << (i % 8)))


def play(level, name, dig_mine=False):
    """Parler au forain (case 3,7, Link au-dessus), choisir le niveau, creuser."""
    goto(0x28, None)
    stand(2, 7)
    walk('down', 3)
    money = rupees()
    press('a', 30)
    text_through(choose=[0, level])   # le Creuse-Rubis, puis le niveau
    w(30)
    check(m[STATE] == 1 and m[LEVEL] == level, '%s : la partie commence' % name)
    check(money - rupees() == (10, 30)[level], '%s : le prix' % name)
    check(m[INV_A] == ITEM_SHOVEL and m[INV_B] == 0, '%s : rien que la Pelle (A %02x, B %02x)' % (name, m[INV_A], m[INV_B]))
    check(not any(bit(MINES, i) for i in range(24)), '%s : pas encore de bombes' % name)
    text_through()       # Marine explique le chiffre
    # Le premier coup, dans le coin (2, 1) : les bombes se placent, jamais là ni autour, ni dans
    # les coins ; s'il n'y a rien autour, les cases vides s'ouvrent toutes seules
    left0 = m[LEFT]
    stand(3, 1)
    walk('up', 3)
    press('a', 20)
    w(60)
    mines = [i for i in range(24) if bit(MINES, i)]
    check(len(mines) == (4, 8)[level], '%s : %d bombes' % (name, len(mines)))
    check(not any(i in mines for i in (0, 1, 6, 7, 5, 18, 23)), '%s : ni au 1er coup, ni autour, ni dans les coins %s' % (name, mines))
    opened = left0 - m[LEFT]
    print('  %s : %d cases ouvertes au 1er coup' % (name, opened))
    check(opened >= 1 and bit(DUG, 0), '%s : le 1er coup' % name)
    cells = [i for i in range(24) if (i in mines) == dig_mine and not bit(DUG, i)]
    for i in cells[:1] if dig_mine else cells:
        if bit(DUG, i):
            continue
        row, col = 2 + i // 6, 1 + i % 6
        if row < 5:
            stand(row + 1, col)
            walk('up', 3)
        else:
            stand(row - 1, col)
            walk('down', 3)
        press('a', 20)
        if not dig_mine:
            # le chiffre sur la case : le nombre de bombes autour (sable lisse si aucune)
            around = sum(1 for j in mines if j != i and abs(j // 6 - i // 6) <= 1 and abs(j % 6 - i % 6) <= 1)
            pos = (row << 4) | col
            want = 0x40 + around if around else 0xbf
            if m[0xcf00 + pos] != want:
                numbers_ok[0] = False
                print('  case', i, 'tuile %02x' % m[0xcf00 + pos], 'attendu %02x' % want)
        if m[0xcba0]:
            break
    w(30)
    shot(name)
    for r in range(1, 7):
        print('   ', ' '.join('%02x' % m[0xcf00 + (r << 4) + c] for c in range(10)))


# Nouvelle partie, la plage
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if m[0xcc8a] == 0 and i > 60:
        break
w(60)
m[RUPEES], m[RUPEES + 1] = 0x99, 0x00      # 99 rubis

# Par le sable du port de pêche (1:ab, lignes 1-2) jusqu'à la plage du forain
for i, v in enumerate((0x81, 0xab, 0x00, 0x17, 0x03)):
    m[0xcc47 + i] = v
w(220)
for _ in range(20):
    walk('right', 20)
    if m[0xcc30] == 0xac:
        break
w(60)
check(m[0xcc30] == 0xac, 'le port de pêche mène à la plage du forain (1:ac)')
shot('plage')
m[INV_A], m[INV_B] = ITEM_SWORD, ITEM_BOMBS

numbers_ok = [True]
play(0, 'facile')
check(numbers_ok[0], 'facile : chaque case creusée montre le nombre de bombes autour')
check(m[STATE] == 0 and m[LEFT] == 0, 'facile : toutes les cases sûres creusées, gagné')
check(m[0xcba0] != 0, 'facile : le forain le dit')
text_through()
check(m[INV_A] == ITEM_SWORD and m[INV_B] == ITEM_BOMBS, 'facile : ses objets reviennent (A %02x, B %02x)' % (m[INV_A], m[INV_B]))
w(120)
print('rubis après la partie facile :', rupees())

pieces = m[HEART_PIECES]
m[RUPEES] = 0x99
play(1, 'difficile')
check(m[STATE] == 0 and m[LEFT] == 0, 'difficile : gagné')
text_through()
for _ in range(10):
    w(30)
    text_through()
check(bool(m[ROOM_FLAGS] & 0x80), 'difficile : le quart de cœur est noté')
check(m[HEART_PIECES] != pieces, 'difficile : un quart de cœur (%d -> %d)' % (pieces, m[HEART_PIECES]))

m[RUPEES] = 0x99
life = m[HEALTH]
play(0, 'bombe', dig_mine=True)
check(m[STATE] == 0 and m[LEFT] != 0, 'une bombe : la partie est perdue')
w(60)
check(m[HEALTH] < life, 'une bombe : Link perd des cœurs (%d -> %d)' % (life, m[HEALTH]))
text_through()
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
