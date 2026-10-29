"""Test du démineur du forain (le Creuse-Rubis, à la taille du Mamono : Denis) et de ses coffres :
- la plage du forain (1:ac) : trois coffres avec leur icône (la bombe, le monstre, le Lynel),
  fermés tant que le jeu n'est pas gagné en Dur (« Fermé ») ;
- une partie Facile dans l'arène (5:ea, wBalladeCreuseMode 0) : 14 bombes de niveau 1 (le test les
  connaît et ne creuse que les cases sûres) ; chaque case montre le nombre de bombes autour ; des
  rubis ; gagné : l'Anneau Caméléon ;
- une partie Difficile gagnée : le forain permet d'ouvrir le coffre à la bombe ; sur la plage, le
  coffre s'ouvre : le quart de cœur ;
- une bombe déterrée : BOUM, perdu.

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
RUPEES, HEART_PIECES = 0xc6ad, 0xc6ac
CREUSE_LEVEL, CREUSE_MODE = 0xcdf6, 0xc590
LEFT, STATE, FLOOD = 0xc583, 0xc584, 0xc59a
LEVELS = 0xcfc0
LAYOUT = 0xcf00
GLOBAL_FLAGS = 0xc6d0
FLAG_CREUSE = 0x67
CAMELEON_RING = 0x38
ROWS, COLS = 8, 13
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


def shot(name, scale=3):
    im = pb.screen.image
    im.resize((im.size[0] * scale, im.size[1] * scale)).save(os.path.join(OUT, name + '.png'))


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        shot('rate_%02d' % len(errors))


def goto(y=None, x=None, limit=400):
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


def text_through(n=40, choose=0):
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


def flag(f):
    return bool(m[GLOBAL_FLAGS + f // 8] & (1 << (f % 8)))


def ring(r):
    return bool(m[0xc616 + r // 8] & (1 << (r % 8)))


def level(i):
    b = m[LEVELS + i // 2]
    return (b >> 4) if i & 1 else (b & 0x0f)


def pos(i):
    r, c = divmod(i, COLS)
    return ((r + 2) << 4) | (c + 1)


def neighbours(i):
    r, c = divmod(i, COLS)
    return [nr * COLS + nc for nr in range(r - 1, r + 2) for nc in range(c - 1, c + 2)
            if (nr, nc) != (r, c) and 0 <= nr < ROWS and 0 <= nc < COLS]


def dug(i):
    return m[LAYOUT + pos(i)] != 0x12


def wait_flood():
    for _ in range(300):
        if not m[FLOOD]:
            return
        w(1)


def face(i):
    wait_flood()
    r, c = divmod(i, COLS)
    row, col = r + 2, c + 1
    goto(None, col * 16 + 8)
    goto((row - 1) * 16 + 8, None)
    goto(None, col * 16 + 8)
    walk('down', 2)


def dig(i):
    face(i)
    press('a', 30)
    for _ in range(4):
        if not m[0xcba0]:
            break
        text_through()


def chests():
    return {m[(s << 8) + 0x42]: s for s in range(0xd0, 0xe0)
            if m[(s << 8) + 0x40] and m[(s << 8) + 0x41] == 0xed and m[(s << 8) + 0x42] in (0x5f, 0x60, 0x61)}


def talk_chest(x):
    """Link sous le coffre (ligne 5), tourné vers lui, A (on passe par la gauche : le forain est à
    droite, les coffres au milieu)."""
    goto(0x28, None)
    goto(None, 0x18)
    goto(0x68, None)
    goto(None, x)
    goto(0x58, None)
    walk('up', 2)
    press('a', 30)


def arena(lvl, name):
    m[RUPEES] = 0x99
    goto(None, 0x18)             # (par la gauche : les coffres sont au milieu)
    goto(0x28, None)
    goto(None, 0x78)
    goto(0x28, None)
    walk('down', 3)
    press('a', 30)
    text_through(choose=[0, lvl])
    w(250)
    check(m[0xcc30] == 0xea and m[CREUSE_LEVEL] == lvl and m[CREUSE_MODE] == 0,
          "%s : le forain envoie Link dans l'arène (5:%02x, le démineur)" % (name, m[0xcc30]))
    w(30)
    text_through()
    check(m[STATE] == 1, '%s : la partie commence' % name)


def leave(name):
    goto(None, 0x78)
    goto(0x18, None)
    for _ in range(10):
        walk('up', 8)
        if m[0xcc30] == 0xac:
            break
    w(200)
    text_through()
    check(m[0xcc30] == 0xac, '%s : retour chez le forain' % name)


def play_to_win(lvl, name):
    arena(lvl, name)
    first = 3 * COLS + 6
    dig(first)
    levels = [level(i) for i in range(ROWS * COLS)]
    bombs = [i for i in range(ROWS * COLS) if levels[i]]
    check(len(bombs) == (14, 20)[lvl] and all(levels[i] == 1 for i in bombs),
          '%s : %d bombes, toutes de niveau 1' % (name, len(bombs)))
    rupees = m[RUPEES]
    for i in range(ROWS * COLS):
        if not levels[i] and not dug(i) and m[STATE] == 1:
            dig(i)
    wait_flood()
    bad = [i for i in range(ROWS * COLS) if not levels[i] and
           m[LAYOUT + pos(i)] != (0xbf if sum(levels[j] for j in neighbours(i)) == 0
                                  else 0x40 + sum(levels[j] for j in neighbours(i)))]
    check(not bad, '%s : chaque case montre les bombes autour %s' % (name, bad[:5]))
    check(m[STATE] == 2 and m[LEFT] == 0, '%s : toutes les cases sûres, gagné' % name)
    check(m[RUPEES] != rupees, '%s : des rubis (%02x -> %02x)' % (name, rupees, m[RUPEES]))
    shot(name + '_fin')
    for _ in range(8):
        w(30)
        text_through()


# Nouvelle partie, la plage du forain
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
m[0xc689], m[0xc688] = 0x05, 0x03
for i, v in enumerate((0x81, 0xac, 0x00, 0x27, 0x03)):
    m[0xcc47 + i] = v
w(250)
check(m[0xcc30] == 0xac, 'la plage du forain')
c = chests()
check(sorted(c) == [0x5f, 0x60, 0x61], 'les trois coffres du forain %s' % [hex(k) for k in sorted(c)])
shot('plage_coffres')
pieces = m[HEART_PIECES]
talk_chest(0x28)
check(bool(m[0xcba0]), 'le coffre à la bombe : « Fermé »')
text_through()
check(m[HEART_PIECES] == pieces, 'fermé : pas de quart de cœur')

play_to_win(0, 'facile')
check(ring(CAMELEON_RING), "l'Anneau Caméléon (la première victoire)")
check(not flag(FLAG_CREUSE), 'en Facile, le coffre reste fermé')
leave('facile')

play_to_win(1, 'difficile')
check(flag(FLAG_CREUSE), "en Difficile : le forain permet d'ouvrir le coffre à la bombe")
leave('difficile')
pieces = m[HEART_PIECES]
talk_chest(0x28)
for _ in range(6):
    w(30)
    text_through()
check(m[HEART_PIECES] != pieces, "le coffre à la bombe s'ouvre : le quart de cœur (%d -> %d)" % (pieces, m[HEART_PIECES]))
shot('coffre_ouvert')

# Une bombe : BOUM
arena(0, 'boum')
first = 3 * COLS + 6
dig(first)
levels = [level(i) for i in range(ROWS * COLS)]
bomb = next(i for i in range(ROWS * COLS) if levels[i] and not dug(i))
face(bomb)
press('a', 20)
check(m[STATE] == 2, 'une bombe déterrée : BOUM, perdu')
shot('boum')
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
