"""Test de Ghost Babel au 4F de la Tour Sans-Nuit (5:c8 ; code/ages/balladeGhost.s), par le menu de
test caché : le regard des fantômes (deux points devant chacun) et le radar ; la boîte en carton
(A devant : Link entre dedans, caché) ; au milieu de la salle, sous les yeux des fantômes, Link dans
sa boîte n'est pas vu (un « ? » au-dessus d'eux, pas de « LIIINK! ») ; A : il en sort.

Usage : python tools/test_ghost.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
BOX = 0xc5a7                 # wBalladeGhostBox
INTERAC_BALLADE_CREUSE = 0xeb
errors = []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def objects(subid):
    """Les emplacements des objets INTERAC_BALLADE_CREUSE de ce sous-type."""
    return [s for s in range(0xd0, 0xe0)
            if g.m[(s << 8) + 0x40] and g.m[(s << 8) + 0x41] == INTERAC_BALLADE_CREUSE
            and g.m[(s << 8) + 0x42] == subid]


g = Game()
g.level(8, 'Donjon')
g.m[INV_A], g.m[INV_B] = 0x00, 0x00
g.text_through()
g.warp(5, 0xc8, 0x87)
g.settled()
g.w(60)
g.text_through()
g.w(30)
check(g.where() == (5, 0xc8), 'le 4F de la Tour (5:c8)')
check(len(g.enemies(0x54)) == 2, 'deux fantômes')
check(len(objects(6)) == 4, 'le regard : deux points devant chaque fantôme (%d)' % len(objects(6)))
check(len(objects(8)) == 1 and len(objects(9)) == 3, 'le radar et ses trois points')
check(len(objects(4)) == 2, 'deux boîtes en carton')
g.shot(os.path.join(OUT, 'g01_regard_radar.png'))

# La boîte (6,4) : Link à droite, tourné vers elle, A (les fantômes figés le temps d'y aller)
g.m[0xcc8a] |= 0x04
g.stand(6, 5, y_first=True)
g.face('left')
g.press('a', 20)
g.w(10)
check(g.m[BOX] != 0, 'Link entre dans la boîte')
check(not g.m[0xd01a] & 0x80, 'Link est caché')
g.m[0xcc8a] &= ~0x04 & 0xff
g.shot(os.path.join(OUT, 'g02_boite.png'))

# Au milieu, sous les yeux des fantômes : pas vu
g.stand(5, 7)
seen_question, spotted = False, False
for _ in range(60):
    g.w(10)
    if objects(7) and not seen_question:
        seen_question = True
        g.shot(os.path.join(OUT, 'g03_question.png'))
    if g.m[0xcba0]:
        spotted = True
        break
check(not spotted, 'dans sa boîte, les fantômes ne le voient pas')
check(seen_question, 'un « ? » au-dessus d\'un fantôme')

# A : il en sort, la boîte reste
g.press('a', 20)
g.w(10)
check(g.m[BOX] == 0 and g.m[0xd01a] & 0x80, 'A : Link sort de la boîte')
check(len(objects(4)) == 2, 'la boîte reste par terre')
g.shot(os.path.join(OUT, 'g04_sortie.png'))
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
