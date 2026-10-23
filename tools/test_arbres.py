"""Test des Arbres-Passages (INTERAC_BALLADE_OBJECT $3a, code/ages/balladeObjects.s) : un arbre au
cœur de chaque île ; A devant lui, Marine propose les îles repérées (comme le Bateau-Rondin), et
Link arrive sous l'arbre de l'île choisie, qui dit son numéro et son nom.

- île 8 (8 îles repérées) : de l'arbre de l'Œil, on fait le tour de toutes les îles par les arbres ;
- « on y est déjà » ; après la fin, l'île de Marine (9) aussi.

Usage : python tools/test_arbres.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
GLOBALFLAG_BALLADE_FIN = 0x5d
TREE_ARRIVAL = 0xc59d
# L'arbre de chaque île : salle, ligne, colonne (Link arrive juste dessous)
TREES = [(0x9b, 1, 4), (0x11, 2, 3), (0x07, 4, 2), (0x2a, 5, 2), (0x52, 5, 7), (0x67, 2, 1),
         (0xb1, 2, 7), (0xd9, 2, 2), (0x6c, 3, 3)]
NAMES = ['Brume', 'Grelot', 'Lagune', 'Braise', 'Échos', 'Nid', 'Sommeil', 'Œil', 'Mouette']
errors, shots = [], []


def check(ok, what, g=None):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        if g:
            print('     ', g.describe())
            g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(g, name, label=None):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label or name))


def use_tree(g, here):
    room, row, col = TREES[here]
    g.stand(row + 1, col)
    g.face('up')
    g.press('a', 20)


def choose_island(g, k, fin=False):
    """Le menu des îles (8 repérées ; 9 après la fin) : trois pages."""
    if k < 3:
        g.choose(k, 4)
        return
    g.choose(3, 4)
    if k < 6:
        g.choose(k - 3, 4)
        return
    g.choose(3, 4)
    if not fin:
        g.choose(k - 6, 2)
        return
    # La 3e page après la fin (Sommeil, Œil, Mouette) : comme test_epilogue.py
    g.wait_text()
    for _ in range(30):
        g.w(30)
        if g.options_shown() >= 3:
            break
        if g.options_shown() == 0:
            g.press('a', 4)
    g.w(60)
    for _ in range(k - 6):
        g.hold('right', 6)
        g.w(16)
    g.press('a', 10)


def travel(g, here, k, fin=False):
    use_tree(g, here)
    choose_island(g, k, fin)
    g.wait_until(lambda: g.where() == (1, TREES[k][0]), 300)
    # Le nom de l'île, en arrivant
    ok = g.wait_text(200)
    g.w(40)
    return ok


g = Game()
g.level(8, 'Plage')
check(g.where() == (1, 0xd9), "le ponton de l'Œil (1:d9)", g)
g.text_through()
g.w(30)
shoot(g, 'a00_oeil', "L'arbre de l'Œil")

here = 7
for k in (1, 2, 3, 4, 5, 6, 0, 7):
    ok = travel(g, here, k)
    room, row, col = TREES[k]
    y, x = g.link()
    check(g.where() == (1, room) and ok, "l'arbre -> %s (1:%02x), son nom s'affiche" % (NAMES[k], room), g)
    check(abs(y - ((row + 1) * 16 + 8)) < 6 and abs(x - (col * 16 + 8)) < 6,
          '  Link sous l\'arbre (%02x, %02x)' % (y, x), g)
    shoot(g, 'a%02d_%s' % (k + 1, NAMES[k]), 'Île %d : %s' % (k + 1, NAMES[k]))
    g.text_through()
    check(not g.m[TREE_ARRIVAL], '  le nom ne revient pas', g)
    here = k

# On y est déjà
use_tree(g, here)
choose_island(g, here)
check(g.wait_text(60), '« on y est déjà »', g)
g.text_through()
check(g.where() == (1, TREES[here][0]), '  on reste', g)

# Après la fin : l'île de Marine
g.m[GLOBAL_FLAGS + GLOBALFLAG_BALLADE_FIN // 8] |= 1 << (GLOBALFLAG_BALLADE_FIN % 8)
ok = travel(g, here, 8, fin=True)
check(g.where() == (1, 0x6c) and ok, "après la fin : l'île de Marine (1:6c)", g)
shoot(g, 'a09_Mouette', 'Île 9 : Mouette')
g.text_through()
ok = travel(g, 8, 0, fin=True)
check(g.where() == (1, 0x9b) and ok, 'et retour à la Brume', g)

sheet(shots, os.path.join(OUT, 'planche.png'))
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
