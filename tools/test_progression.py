"""Test de l'écran de progression vers le 100 % (balladeTracker.s) : menu, 3e page, B ; Marine compte
les couplets, les cœurs (et les quarts), les objets, les anneaux, les coffres.

Depuis le menu de test caché (6. Ville) ; puis un coffre de la Spirale marqué ouvert (drapeau $20 de
4:3f) et un anneau : les compteurs bougent.

Usage : python tools/test_progression.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SUBS = 0xcbaf            # wTextSubstitutions
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def tracker(tag):
    """Le menu, 3e page, B : les deux boîtes ; rend les nombres de chacune (wTextSubstitutions)."""
    g.press('start', 6)
    g.w(60)
    for _ in range(2):
        g.press('select', 6)
        g.w(40)
    if tag == 'a':
        shoot('p01_menu', 'Le menu, 3e page : B')
    g.press('b', 6)
    got = []
    for _ in range(60):
        g.w(5)
        if g.m[TEXT_ACTIVE]:
            break
    got.append([g.m[SUBS + i] - 0x80 for i in range(4)])
    g.w(80)
    shoot('p02_%s' % tag, 'Marine compte (%s)' % tag)
    for _ in range(12):
        g.press('a', 8)
        g.w(30)
        if len(got) == 1 and g.m[TEXT_ACTIVE] and [g.m[SUBS + i] - 0x80 for i in range(4)] != got[0]:
            got.append([g.m[SUBS + i] - 0x80 for i in range(4)])
            g.w(80)
            shoot('p03_%s' % tag, 'La 2e boîte (%s)' % tag)
        if not g.m[TEXT_ACTIVE] and len(got) == 2:
            break
    return got


g.level(6, 'Ville')
g.text_through()
g.w(30)
a = tracker('a')
print('     ', a)
check(len(a) == 2, 'deux boîtes')
pct, verses, hearts, pieces = a[0]
items, rings, chests, total = a[1] if len(a) == 2 else (0, 0, 0, 0)
check(verses == bin(g.m[0xc6bf]).count('1'), 'les couplets (%d)' % verses)
check(hearts == g.m[0xc6ab] // 4, 'les cœurs (%d)' % hearts)
check(total > 40, 'le nombre de coffres (%d)' % total)
check(0 < pct < 100, 'le pour cent (%d)' % pct)

# Un coffre (la petite clé 1 de la Spirale, 4:3f) et un anneau (Force) de plus
g.m[0xc900 + 0x3f] |= 0x20
g.m[0xc616] |= 0x02               # wRingsObtained : POWER_RING_L1 ($01, le bit 1)
b = tracker('b')
print('     ', b)
check(len(b) == 2 and b[1][2] == chests + 1, 'un coffre ouvert de plus (%s)' % (b[1] if len(b) == 2 else b))
check(len(b) == 2 and b[1][1] == rings + 1, 'un anneau de plus (%s)' % (b[1] if len(b) == 2 else b))
check(len(b) == 2 and b[0][0] > pct, 'le pour cent monte (%d -> %d)' % (pct, b[0][0]))

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
