"""Test de la planche de surf (idée de Denis) : Bulle, au club de plongée de la Lagune (3:24), la
donne une fois le Récif Murmurant sauvé ; avec elle, Link nage bien plus vite (link.s,
linkGetSwimmingSpeed).
- la nage sans la planche (la lagune, 1:15 ; huit coups de nage) : la distance parcourue ;
- Bulle donne la planche (GLOBALFLAG_BALLADE_SURF) ;
- la même nage avec la planche : plus loin.
Usage : python tools/test_surf.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
GLOBALFLAG_BALLADE_SURF = 0x5a
errors, shots = [], []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)


def shoot(g, name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def swim(g):
    """Dans la lagune (1:15, ligne 6) : nager vers la droite avec les Écailles de Sirène (on
    tapote la direction : huit coups)."""
    g.warp(1, 0x15, 0x61)
    g.w(60)
    g.text_through()
    x0 = g.link()[1]
    for _ in range(8):
        g.pb.button('right', 4)
        g.w(8)
    return g.link()[1] - x0


g = Game()
g.level(3, 'Fin')
for _ in range(10):
    g.text_through()
    g.w(20)
d0 = swim(g)
check(d0 > 0, 'Link nage sans la planche (%d pixels en huit coups)' % d0)
g.warp(3, 0x24, 0x57)
g.w(40)
g.text_through()
g.stand(5, 3)
g.face('up')
g.press('a', 20)
check(g.wait_text(60), 'Bulle parle')
shoot(g, 's01_bulle', 'Bulle : la planche de surf')
for _ in range(8):
    g.text_through()
    g.w(30)
check(g.global_flag(GLOBALFLAG_BALLADE_SURF), 'la planche de surf (GLOBALFLAG_BALLADE_SURF)')
d1 = swim(g)
shoot(g, 's02_surf', 'Sur la planche')
check(d1 > d0 * 1.3, 'avec la planche, Link nage plus vite (%d pixels contre %d)' % (d1, d0))

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
