"""Test des photos de Cocolint (idée de Denis) : une fois le chapitre 5 fini, à l'auberge (3:9e),
Marine trouve les photos dans la poche de Link ; les trois vraies photos de Link's Awakening DX
(la chute, Tarkin et Bow Wow, la falaise), en plein écran avec sa réplique ; puis retour à
l'auberge, une seule fois (GLOBALFLAG_BALLADE_PHOTOS).
Usage : python tools/test_photos.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
CUTSCENE_INDEX = 0xc2ef
GLOBALFLAG_BALLADE_PHOTOS = 0x5b
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


g.level(5, 'Fin')
for _ in range(20):
    g.text_through()
    g.w(20)
check(not g.global_flag(GLOBALFLAG_BALLADE_PHOTOS), 'pas encore de photos')
g.warp(3, 0x9e, 0x57)
check(g.wait_text(200), "l'auberge : Marine fouille la poche de Link")
g.w(30)
shoot('p00_poche', 'Oh ! Nos photos !')
g.text_through()
check(g.wait_until(lambda: g.m[CUTSCENE_INDEX] == 0x22, 300), 'la cinématique des photos')
for n, (name, label) in enumerate((('p01_chute', 'On ne parle PAS de celle-là'),
                                   ('p02_tarkin', 'Papa ! Et Bow Wow !'),
                                   ('p03_falaise', 'Qui a pris cette photo ?!'))):
    check(g.wait_text(400), 'photo %d : la réplique de Marine' % (n + 1))
    g.w(150)
    shoot(name, label)
    g.text_through()
check(g.wait_until(lambda: g.m[CUTSCENE_INDEX] == 0x01 and g.where() == (3, 0x9e), 600),
      "retour à l'auberge (3:9e)")
g.settled()
g.w(60)
shoot('p04_retour', "Retour à l'auberge")
check(g.global_flag(GLOBALFLAG_BALLADE_PHOTOS), 'les photos ont été vues (GLOBALFLAG_BALLADE_PHOTOS)')
# Une seule fois
g.warp(3, 0x9e, 0x57)
g.w(200)
check(not g.m[TEXT_ACTIVE], 'une seule fois')

sheet(shots, os.path.join(OUT, 'photos.png'), cols=3)
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
