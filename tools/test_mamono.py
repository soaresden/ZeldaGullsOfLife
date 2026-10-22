"""Test du Mamono (le 2e jeu du forain, plage 1:ac) : une partie Facile gagnée (le test connaît les
monstres : il creuse les cases vides, puis les monstres du plus faible au plus fort, quand Link a
le niveau), les chiffres dans le sable, les monstres vaincus, la montée de niveau ; une partie
Moyen gagnée (le quart de cœur) ; puis un monstre trop fort découvert à l'aveugle (il frappe fort).

Usage : python tools/test_mamono.py DOSSIER_CAPTURES
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
RUPEES, HEART_PIECES = 0xc6ad, 0xc6ac
STATE, LEVEL, DUG, LEFT = 0xcdf5, 0xcdf6, 0xcdfa, 0xcdfd
LEVELS, P_LEVEL, P_XP, PLACED, MODE = 0xc580, 0xc598, 0xc599, 0xc59a, 0xc59b
ROOM_FLAGS = 0xc800 + 0xac
ROOM_LAYOUT = 0xcf00
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
    """Passe les textes ; choose : l'option à prendre (ou une liste, une par menu)."""
    choices = list(choose) if isinstance(choose, (list, tuple)) else [choose]
    for _ in range(n):
        if not m[0xcba0]:
            w(20)
            if not m[0xcba0]:
                return
        if m[0xcba1] == 1 and choices:
            w(40)
            for _ in range(choices.pop(0)):
                walk('right', 6)
                w(16)
            press('a', 20)
            w(20)
            continue
        press('a', 20)


def cell_pos(i):
    return 2 + i // 6, 1 + i % 6


def neighbours(i):
    r, c = divmod(i, 6)
    return [nr * 6 + nc for nr in range(r - 1, r + 2) for nc in range(c - 1, c + 2)
            if (nr, nc) != (r, c) and 0 <= nr < 4 and 0 <= nc < 6]


def dig(i):
    row, col = cell_pos(i)
    if row < 5:
        stand(row + 1, col)
        walk('up', 3)
    else:
        stand(row - 1, col)
        walk('down', 3)
    press('a', 24)


def is_open(i):
    return bool(m[DUG + i // 8] & (1 << (i % 8)))


def start(level, name):
    goto(0x28, None)
    stand(2, 7)
    walk('down', 3)
    press('a', 30)
    text_through(choose=[1, level])   # le Mamono, puis le niveau
    w(30)
    check(m[STATE] == 1 and m[MODE] == 1 and m[LEVEL] == level and m[P_LEVEL] == 1,
          '%s : une partie de Mamono commence (Link niveau 1)' % name)
    text_through()                # les règles, Marine


def play_to_win(level, name):
    start(level, name)
    dig(9)                        # (1,3) : au milieu, la première case n'a jamais de monstre
    text_through()
    check(m[PLACED] == 1 and m[LEVELS + 9] == 0, '%s : les monstres sont placés, loin de la 1re case' % name)
    levels = [m[LEVELS + i] for i in range(24)]
    print('  monstres', levels, flush=True)
    s = sum(levels[j] for j in neighbours(9))
    t = m[ROOM_LAYOUT + 0x34]     # case 9 = ligne 3, colonne 4
    check(t == (0xbf if s == 0 else 0x40 + min(s, 19)), '%s : le chiffre de la 1re case (%d)' % (name, s))
    # Les cases vides d'abord, puis les monstres du plus faible au plus fort
    for i in range(24):
        if not levels[i] and not is_open(i):
            dig(i)
            text_through()
    lv_seen = []
    for lv in range(1, 6):
        for i in range(24):
            if levels[i] == lv and m[STATE] == 1:
                before = m[HEALTH]
                dig(i)
                text_through()
                lv_seen.append((lv, m[P_LEVEL]))
                m[HEALTH] = m[MAX_HEALTH]
    print('  (monstre, niveau de Link)', lv_seen, flush=True)
    shot(name)
    check(m[STATE] == 0 and m[LEFT] == 0, '%s : tous les monstres vaincus, gagné' % name)
    check(max(p for _, p in lv_seen) > 1, '%s : Link est monté de niveau' % name)
    check(all(m[ROOM_LAYOUT + (cell_pos(i)[0] << 4) + cell_pos(i)[1]] == 0x58 + levels[i]
              for i in range(24) if levels[i]), '%s : les monstres vaincus dessinés' % name)
    text_through()
    for _ in range(8):
        w(30)
        text_through()


# Nouvelle partie, la plage
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if m[0xcc8a] == 0 and i > 60:
        break
w(60)
m[RUPEES], m[RUPEES + 1] = 0x99, 0x00
for i, v in enumerate((0x81, 0xab, 0x00, 0x17, 0x03)):
    m[0xcc47 + i] = v
w(220)
for _ in range(20):
    walk('right', 20)
    if m[0xcc30] == 0xac:
        break
w(60)
check(m[0xcc30] == 0xac, 'la plage du forain')

play_to_win(0, 'facile')
pieces = m[HEART_PIECES]
m[RUPEES] = 0x99
play_to_win(1, 'moyen')
check(bool(m[ROOM_FLAGS] & 0x04), 'moyen : le quart de cœur est noté (drapeau $04)')
check(m[HEART_PIECES] != pieces, 'moyen : un quart de cœur (%d -> %d)' % (pieces, m[HEART_PIECES]))

# Un monstre trop fort, découvert à l'aveugle : il frappe de tout son niveau
m[RUPEES] = 0x99
start(2, 'dur')
dig(9)
text_through()
levels = [m[LEVELS + i] for i in range(24)]
strong = [i for i in range(24) if levels[i] >= 3 and not any(is_open(j) for j in neighbours(i))]
if strong:
    i = strong[0]
    m[HEALTH] = m[MAX_HEALTH]
    before = m[HEALTH]
    dig(i)
    w(30)
    print('  monstre de niveau %d : vie %d -> %d' % (levels[i], before, m[HEALTH]), flush=True)
    check(before - m[HEALTH] == 2 * levels[i] or levels[i] * 2 >= before, 'à l\'aveugle : un demi-cœur par niveau du monstre')
    text_through()
else:
    check(False, 'pas de monstre fort à découvrir à l\'aveugle')
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
