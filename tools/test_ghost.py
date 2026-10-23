"""Test de Ghost Babel au 4F de la Tour Sans-Nuit (5:c8 ; code/ages/balladeGhost.s), par le menu de
test caché : le regard des fantômes (deux points devant chacun) et le radar ; la boîte en carton
(A devant : Link entre dedans, caché) ; au milieu de la salle, sous les yeux des fantômes, Link dans
sa boîte n'est pas vu (un « ? » au-dessus d'eux, pas de « LIIINK! ») ; A : il en sort.
L'écran de Ghost Babel : la barre d'état en bas, « NO ITEM » dans les cases B et A, l'épée ne sort
pas (Link entre sans rien en main) ; en quittant la salle, tout redevient comme avant.

Usage : python tools/test_ghost.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
BOX = 0xc5a7                 # wBalladeGhostBox
GHOST_HUD, HUD_BAS = 0xc598, 0xc593   # wBalladeGhostHud, wBalladeHudBas
WEAPON = 0xd600              # w1WeaponItem.enabled (l'épée sortie)
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
g.m[INV_A], g.m[INV_B] = 0x00, 0x05     # l'épée en B
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
check(g.m[GHOST_HUD] == 1 and g.m[HUD_BAS] == 1, "l'écran de Ghost Babel : la barre d'état en bas")
check(len(objects(0x23)) == 1, '« NO ITEM » dans les cases B et A')
g.shot(os.path.join(OUT, 'g01_regard_radar.png'))
g.m[0xcc8a] |= 0x04
g.press('b', 2)
sword = False
for _ in range(12):
    g.w(1)
    sword = sword or g.m[WEAPON] != 0
check(not sword, "B : l'épée ne sort pas (rien en main)")
g.m[0xcc8a] &= ~0x04 & 0xff

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

# En quittant la salle : la barre d'état redevient comme avant, l'épée revient
g.warp(5, 0xc9, 0x51)
g.text_through()
g.w(30)
check(g.m[GHOST_HUD] == 0 and g.m[HUD_BAS] == 0, "hors de la salle : la barre d'état en haut")
g.press('b', 2)
sword = False
for _ in range(12):
    g.w(1)
    sword = sword or g.m[WEAPON] != 0
check(sword, "hors de la salle : B, l'épée sort")
g.shot(os.path.join(OUT, 'g05_apres.png'))
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
