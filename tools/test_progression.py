"""Test de l'écran de progression vers le 100 % (balladeTracker.s, CUTSCENE_BALLADE_PROGRESS) : menu,
3e page, B ; un écran comme les secrets d'Ages : les couplets, les cœurs (et les quarts), les
objets, les anneaux, les coffres, le total ; A : retour au jeu.

Depuis le menu de test caché (6. Ville) ; puis un coffre de la Spirale marqué ouvert (drapeau $20 de
4:3f) et un anneau : les compteurs bougent.

Usage : python tools/test_progression.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
CUTSCENE, CUTSCENE_STATE = 0xc2ef, 0xcc03   # wCutsceneIndex, wCutsceneState
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
    """Le menu, 3e page, B : l'écran de la progression (CUTSCENE_BALLADE_PROGRESS $24) ; rend ses
    nombres (wTmpcbb6-cbbc : couplets, cœurs, quarts, objets, anneaux, coffres, pour cent) ; A : on
    revient où on était."""
    room = g.where()
    g.press('start', 6)
    g.w(60)
    for _ in range(2):
        g.press('select', 6)
        g.w(40)
    if tag == 'a':
        shoot('p01_menu', 'Le menu, 3e page : B')
    g.press('b', 6)
    g.wait_until(lambda: g.m[CUTSCENE] == 0x24 and g.m[CUTSCENE_STATE] == 2, 400)
    check(g.m[CUTSCENE] == 0x24, "%s : l'écran de la progression s'ouvre" % tag)
    got = [g.m[0xcbb6 + i] for i in range(7)]
    g.w(60)
    shoot('p02_%s' % tag, "L'écran de la progression (%s)" % tag)
    g.press('a', 8)
    g.wait_until(lambda: g.m[CUTSCENE] != 0x24, 400)
    g.settled()
    g.w(40)
    check(g.where() == room and g.m[CUTSCENE] != 0x24, '%s : A, retour au jeu (%d:%02x)' % ((tag,) + g.where()))
    return got


g.level(6, 'Ville')
g.text_through()
g.w(30)
a = tracker('a')
print('     ', a)
verses, hearts, pieces, items, rings, chests, pct = a
check(verses == bin(g.m[0xc6bf]).count('1'), 'les couplets (%d)' % verses)
check(hearts == g.m[0xc6ab] // 4, 'les cœurs (%d)' % hearts)
check(0 < pct < 100, 'le pour cent (%d)' % pct)

# Un coffre (la petite clé 1 de la Spirale, 4:3f) et un anneau (Force) de plus
g.m[0xc900 + 0x3f] |= 0x20
g.m[0xc616] |= 0x02               # wRingsObtained : POWER_RING_L1 ($01, le bit 1)
b = tracker('b')
print('     ', b)
check(b[5] == chests + 1, 'un coffre ouvert de plus (%s)' % b)
check(b[4] == rings + 1, 'un anneau de plus (%s)' % b)
check(b[6] > pct, 'le pour cent monte (%d -> %d)' % (pct, b[6]))

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
