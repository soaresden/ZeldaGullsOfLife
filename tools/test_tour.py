"""Test de l'île 8 (l'Œil de l'Insomnis) et de l'entrée de la Tour Sans-Nuit (donjon 8), depuis le
menu de test caché (8. Plage) :
- arrivée au ponton ; le Bateau-Rondin (trois pages) ;
- la porte de la tour : Marine chante les sept couplets, elle s'ouvre ; l'entrée, le nom du donjon.

La tour elle-même (Link prisonnier, du cachot à Ganon) a son propre test : tools/test_prison.py.

Usage : python tools/test_tour.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import HEALTH, INV_A, MAX_HEALTH, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def full_life():
    g.m[HEALTH] = g.m[MAX_HEALTH]


# --- L'île : le ponton, la porte de la tour
g.level(8, 'Plage')
g.m[INV_A] = 0x05
full_life()
check(g.where() == (1, 0xd9), "le ponton de l'Œil de l'Insomnis (1:d9)")
check(g.wait_text(200), 'Marine : une tour noire')
g.w(40)
shoot('t01_arrivee', "L'Œil de l'Insomnis")
g.text_through()

# Le Bateau-Rondin à huit îles : trois pages (Brume Grelot Lagune Suite / Braise Échos Nid Suite /
# Sommeil Œil) : vers le Grand Sommeil, et retour
def raft(*options):
    g.stand(6, 4)
    g.face('right')
    g.press('a', 20)
    for opt, count in options:
        g.choose(opt, count)
    g.w(30)
    g.settled()
    g.w(60)
    g.text_through()


raft((3, 4), (3, 4), (0, 2))
check(g.where() == (1, 0xd1), 'le Bateau-Rondin, 3e page : le Grand Sommeil (1:d1)')
raft((3, 4), (3, 4), (1, 2))
check(g.where() == (1, 0xd9), "et retour à l'Œil (1:d9)")
# Le soleil et la lune déjà allumés (les vasques des paupières : tools/test_oeil.py les allume)
g.m[0xc800 + 0xc8] |= 0x40
g.m[0xc700 + 0xca] |= 0x40
g.route((4, 4))
check(g.go('up', (1, 0xc9)), 'le parvis de la tour (1:c9)')
g.route((6, 4))
check(g.wait_text(200), 'Marine : sept marques, sept couplets')
g.w(30)
shoot('t02_porte', 'Marine chante les sept couplets')
for _ in range(10):
    g.text_through()
    g.w(30)
check(g.tile(0x44) == 0xdf, 'la porte de la tour est ouverte')
g.route((5, 4))
g.hold('up', 40)
g.settled()
check(g.where() == (5, 0xc0), "l'entrée de la Tour Sans-Nuit (5:c0)")
check(g.wait_text(200), 'le nom du donjon')
g.w(30)
shoot('t03_entree', "L'entrée : Niveau 8, Tour Sans-Nuit")
for _ in range(6):
    g.text_through()
    g.w(20)

# La tour elle-même (Link assommé, le cachot, les étages, Dark Link, l'Insomnis, Ganon) :
# tools/test_prison.py

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
