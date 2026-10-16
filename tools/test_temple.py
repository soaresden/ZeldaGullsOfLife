"""Test du temple du Phare : la Lanterne allume les torches des salles sombres (le volet de la tour
s'ouvre, le coffre de la clé du boss apparaît), puis Jack : sa citrouille tombe, la Lanterne la
brûle et son fantôme est à découvert.

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
TORCHES = 0xcc8f
ENEMY = {'id': 0x81, 'subid': 0x82, 'state': 0x84, 'yh': 0x8b, 'xh': 0x8d,
         'collision': 0xa4, 'health': 0xa9}


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


def where(t):
    print(t, 'groupe', m[0xcc2d], 'salle', hex(m[0xcc30]), 'y', hex(m[0xd00b]), 'x', hex(m[0xd00d]))


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


def warp(g, r, pos):
    for i, v in enumerate((0x80 | g, r, 0x00, pos, 0x03)):
        m[0xcc47 + i] = v
    w(220)


def tile(pos):
    return m[ROOM_LAYOUT + pos]


def light(y, x, face):
    """Link se place sous/à côté d'une torche, se tourne vers elle et sort la Lanterne."""
    goto(y, x)
    walk(face, 3)
    press('b', 10)
    w(80)


def enemies():
    out = []
    for d in range(0xd0, 0xe0):
        base = d << 8
        if m[base + 0x80] and m[base + ENEMY['id']] == 0x78:
            out.append(base)
    return out


def text_through(n=40):
    for _ in range(n):
        press('a', 20)


# Nouvelle partie, scène de la plage
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if m[0xcc8a] == 0 and i > 60:
        break
w(60)

# La Lanterne (4:15, coffre en ligne 5 colonne 7)
warp(4, 0x15, 0x67)
walk('up', 8)
press('a', 60)
for i in range(8):
    press('a', 30)
print('bouton B', hex(m[0xc688]))

# La tour, bas : sombre, 2 torches -> le volet du haut
warp(4, 0x16, 0x97)
w(30)
shot('tour_bas_noir')
print('tour bas : torches', m[TORCHES], 'volet', hex(tile(0x07)))
light(0x28, 0x58, 'up')
print('1 torche :', m[TORCHES], hex(tile(0x15)))
shot('tour_bas_1')
light(0x28, 0x98, 'up')
w(120)
print('2 torches :', m[TORCHES], hex(tile(0x19)), 'volet', hex(tile(0x07)))
shot('tour_bas_2')

# La tour, haut : sombre, 3 torches -> le coffre de la clé du boss
warp(4, 0x17, 0x97)
w(30)
shot('tour_haut_noir')
light(0x98, 0x78, 'up')
light(0x38, 0x28, 'up')
light(0x38, 0xc8, 'up')
w(120)
print('tour haut : torches', m[TORCHES], 'coffre', hex(tile(0x57)))
shot('tour_haut_coffre')

# La clé du boss, puis on monte : la galerie, la porte du boss
goto(0x68, 0xa8)
goto(None, 0x78)
where('devant le coffre')
walk('up', 10)
where('contre le coffre')
print('direction', m[0xd008], 'objets bloqués', hex(m[0xcca4]) if False else '')
press('a', 60)
for i in range(6):
    press('a', 30)
print('clé du boss', hex(m[0xc682]), hex(m[0xc683]), 'coffre', hex(tile(0x57)))
shot('cle_boss')
goto(None, 0xa8)
goto(0x18, None)
goto(None, 0x78)
for room in (0x12, 0x13):
    for i in range(40):
        walk('up', 30)
        if m[0xcc30] == room:
            break
    w(60)
    where('montée')
    shot('montee_%02x' % room)
w(40)
for i in range(30):
    if m[0xcba0]:
        shot('jack_%02d' % i)
    press('a', 30)
print('volets', hex(m[0xcc93]))
walk('up', 30)
w(200)
print('volets', hex(m[0xcc93]))
bosses = enemies()
print('Jack :', [(hex(b), m[b + ENEMY['subid']], hex(m[b + ENEMY['state']])) for b in bosses])
shot('jack_combat')
body = [b for b in bosses if m[b + ENEMY['subid']] == 1]
ghost = [b for b in bosses if m[b + ENEMY['subid']] == 2]
head = [b for b in bosses if m[b + ENEMY['subid']] == 3]
if body and head and ghost:
    body, ghost, head = body[0], ghost[0], head[0]
    # On abrège : le corps n'a plus de vie, la citrouille tombe
    m[body + ENEMY['health']] = 0
    for i in range(300):
        w(1)
        if m[head + ENEMY['state']] == 0x12:
            break
    print('tête par terre ?', hex(m[head + ENEMY['state']]), 'y', hex(m[head + ENEMY['yh']]),
          'x', hex(m[head + ENEMY['xh']]))
    shot('jack_tete')
    # Link juste sous la citrouille, tourné vers elle : la Lanterne
    goto(m[head + ENEMY['yh']] + 14, m[head + ENEMY['xh']])
    walk('up', 2)
    press('b', 6)
    for i in range(60):
        w(1)
        if m[head + ENEMY['state']] == 0x17:
            break
    print('tête', hex(m[head + ENEMY['state']]), 'fantôme', hex(m[ghost + ENEMY['state']]),
          'touchable', bool(m[ghost + ENEMY['collision']] & 0x80))
    shot('jack_brule')
    w(30)
    shot('jack_fantome')
    # Le fantôme à découvert : (Link n'a pas d'épée dans ce test) on lui retire sa vie
    m[ghost + ENEMY['health']] = 0
    w(600)
    print('salle du boss : drapeau', hex(m[0xc900 + 0x13]), 'volet du haut', hex(tile(0x07)))
    shot('jack_vaincu')
    w(300)
    for i in range(3):
        goto(0x98, 0x78)
        text_through(8)
    goto(None, 0x58)
    goto(0x18, None)
    goto(None, 0x78)
    for i in range(30):
        walk('up', 30)
        if m[0xcc30] == 0x11:
            break
    w(120)
    where('la lumière')
    shot('lumiere')
    for i in range(10):
        walk('up', 30)
    text_through(20)
    w(600)
    where("après l'essence")
    shot('essence')
where('fin')
