"""Test du bisou de Marine (balladeMarine.kissCheck) : presque plus de vie, ça bippe ; Link ne fait
rien pendant 15 secondes : Marine dit « C'est chiant ce bruit !? Tiens, un bisou ! » et Link a juste
assez de vie pour que ça ne bippe plus. Pas avant 15 secondes.

Usage : python tools/test_bisou.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import HEALTH, MAX_HEALTH, TEXT_ACTIVE, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
errors = []


def check(ok, what, g=None):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        if g:
            print('     ', g.describe())
            g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


g = Game()
g.level(1, 'Ville')
g.text_through()
g.w(60)
g.m[MAX_HEALTH] = 12
g.m[HEALTH] = 2                 # un demi-cœur : ça bippe
g.w(60 * 12)
check(not g.m[TEXT_ACTIVE] and g.m[HEALTH] == 2, 'après 12 secondes : rien encore', g)
ok = g.wait_until(lambda: g.m[TEXT_ACTIVE], 60 * 6)
check(ok, 'vers 15 secondes : Marine parle', g)
g.w(40)
g.shot(os.path.join(OUT, 'bisou.png'))
check(g.m[HEALTH] == 4, 'juste assez de vie pour ne plus bipper (%d quarts)' % g.m[HEALTH], g)
g.text_through()
g.w(60 * 20)
check(not g.m[TEXT_ACTIVE] and g.m[HEALTH] == 4, 'et ça ne recommence pas', g)
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
