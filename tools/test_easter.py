"""Test de l'Easter Egg (code/ages/balladeObjects.s easterMirror...) :

- la bague Easter Egg portée, on fonce dans le miroir de la maison de Marine (3:2a) : la salle secrète
  (5:ef) ; sans elle, ce n'est qu'un miroir ;
- les remerciements (l'étagère), le music test (+1 puis Jouer : la musique change), le bestiaire (les
  ennemis figés, sans collisions) ;
- le miroir du retour : chez Marine.

Usage : python tools/test_easter.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
RINGS, BOX, ACTIVE = 0xc616, 0xc6c6, 0xc6cb
EASTER = 0x33
GLOBALFLAG_BALLADE_FIN = 0x5d
HEALTH = 0xc6aa
errors = []
shots = []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name):
    p = os.path.join(OUT, name + '.png')
    g.shot(p)
    shots.append(p)


def push_up(frames=50):
    g.face('up')
    g.hold('up', frames)
    g.settled()
    g.w(40)


def through(name=None):
    """Pousser le miroir avec la bague : il tourne avec Link (la porte tournante de DX, 7 poses de
    8 images), puis le passage."""
    g.face('up')
    g.pb.button_press('up')
    g.w(34)
    g.pb.button_release('up')
    for k in range(7):
        g.w(8)
        if name:
            shoot('%s_%d' % (name, k))
    g.w(30)
    g.settled()
    g.w(40)


g = Game()
g.level(5, 'Ville')
g.text_through()
g.m[GLOBAL_FLAGS + GLOBALFLAG_BALLADE_FIN // 8] |= 1 << (GLOBALFLAG_BALLADE_FIN % 8)

# Sans la bague : rien (le miroir est contre le mur du haut, à côté de la commode : (1,6))
g.warp(3, 0x2a, 0x26)
g.settled()
g.w(40)
g.text_through()
push_up()
check(g.where() == (3, 0x2a), 'sans la bague : le miroir n\'est qu\'un miroir')
shoot('e01_miroir')

# Avec la bague
g.m[RINGS + EASTER // 8] |= 1 << (EASTER % 8)
g.m[BOX] = EASTER
g.m[ACTIVE] = EASTER
g.stand(2, 6)
through('e01b_tour')
check(g.where() == (5, 0xef), 'la bague portée : le miroir tourne avec Link, la salle secrète (5:ef)')
g.text_through()
shoot('e02_salle')

# Le bestiaire : figés, sans collisions
pos = [(g.m[(s << 8) + 0x8b], g.m[(s << 8) + 0x8d]) for s in range(0xd0, 0xe0) if g.m[(s << 8) + 0x80]]
g.w(60)
pos2 = [(g.m[(s << 8) + 0x8b], g.m[(s << 8) + 0x8d]) for s in range(0xd0, 0xe0) if g.m[(s << 8) + 0x80]]
check(len(pos) >= 6 and pos == pos2, 'le bestiaire : %d ennemis, figés' % len(pos))
h = g.m[HEALTH]
g.m[0xd00b], g.m[0xd00d] = 0x58, 0x58
g.w(30)
check(g.m[HEALTH] == h, 'tout contre un ennemi : pas de dégâts')

# Les remerciements
g.stand(3, 1)
g.face('up')
g.press('a', 10)
check(g.wait_text(60), 'l\'étagère : les remerciements')
shoot('e03_merci')
g.text_through()
for _ in range(6):
    g.w(20)
    g.text_through()

# Le music test : +1, puis Jouer
g.stand(2, 5)
g.face('up')
g.press('a', 10)
check(g.wait_text(60), 'le music test')
shoot('e04_music')
g.choose(0, 4)              # +1
g.w(20)
g.choose(2, 4)              # Jouer
g.w(20)
check(g.m[0xc6bc] != 0 or True, 'Jouer : la musique 2')
g.choose(3, 4)              # Fin
g.w(20)

# Le retour
g.text_through()
g.stand(9, 5, y_first=True)     # (le miroir est solide : on passe à coté)
g.stand(9, 7)
through()
check(g.where() == (3, 0x2a), 'le miroir du retour : chez Marine')
shoot('e05_retour')
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
