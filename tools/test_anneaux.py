"""Test des anneaux de Gulls of Life (code/treasureAndDrops.s balladeGiveRing, code/bank2.s) :

- la boîte à anneaux de 5 places, d'office ; plus d'anneaux non identifiés ;
- l'Anneau Caméléon : A sur lui (2e page du menu), le réglage RVB (un carré de la couleur, les trois
  valeurs) ; en sortant du menu, la tunique de Link prend la couleur ;
- la bague Easter Egg : Marine sur son île, tout fini (les quatre anneaux des jeux), la donne.
(Les quatre autres : test_lynels, test_songe_grelot, test_mamono, test_creuse.)

Usage : python tools/test_anneaux.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
RINGS, BOX, BOX_LEVEL, ACTIVE, UNAPPRAISED = 0xc616, 0xc6c6, 0xc6cc, 0xc6cb, 0xc6cd
TUNIC, EDIT = 0xc5fd, 0xc59f
POWER, ARMOR, CHARGE, CAMELEON, EASTER = 0x01, 0x04, 0x16, 0x38, 0x33
GLOBALFLAG_BALLADE_FIN = 0x5d
INTERAC = 0xeb
errors = []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def give(r):
    g.m[RINGS + r // 8] |= 1 << (r % 8)
    for i in range(5):
        if g.m[BOX + i] == 0xff:
            g.m[BOX + i] = r
            return


def has(r):
    return bool(g.m[RINGS + r // 8] & (1 << (r % 8))) and r in [g.m[BOX + i] for i in range(5)]


g = Game()
g.level(5, 'Ville')
g.text_through()
g.m[0xc5c0] = 0x7f          # un vieil anneau non identifié (la sauvegarde de Denis)
g.m[UNAPPRAISED] = 0x01
g.warp(1, 0x62, 0x47)
g.settled()
g.w(30)
g.text_through()
check(g.m[BOX_LEVEL] == 3, 'la boîte à anneaux de 5 places, d\'office')
check(g.m[UNAPPRAISED] == 0 and g.m[0xc5c0] == 0xff, 'plus d\'anneaux non identifiés')

# L'Anneau Caméléon : le réglage dans le menu
give(CHARGE)
give(CAMELEON)
g.press('start', 4)
g.w(40)
g.press('select', 4)
g.w(60)
for _ in range(3):
    g.press('down', 4)
    g.w(10)
g.press('right', 4)
g.w(10)
g.press('a', 4)
g.w(40)
check(g.m[EDIT] == 1 and g.m[ACTIVE] == CAMELEON, 'A sur le Caméléon : il est porté, le réglage s\'ouvre')
mem = g.pb.memory
tiles = [mem[4, 0xd000 + 0x83 + r * 32 + c] for r in range(5) for c in range(5)]
check(tiles == [0x02] * 25, 'le carré de la couleur')
g.shot(os.path.join(OUT, 'a01_reglage.png'))
for _ in range(12):
    g.press('right', 3)
    g.w(3)
g.press('down', 4)
g.w(6)
for _ in range(25):
    g.press('left', 3)
    g.w(3)
g.press('down', 4)
g.w(6)
for _ in range(25):
    g.press('right', 3)
    g.w(3)
g.w(10)
r, v, b = [g.m[TUNIC + i] for i in range(3)]
check(r > 2 and v == 0 and b == 31, 'plus de rouge, plus de vert, bleu à fond (%d %d %d)' % (r, v, b))
COLOR = r | v << 5 | b << 10
square = mem[2, 0xdeb6] | mem[2, 0xdeb7] << 8
check(square == COLOR, 'le carré en direct (%04x)' % square)
g.shot(os.path.join(OUT, 'a02_violet.png'))
g.press('a', 4)
g.w(40)
check(g.m[EDIT] == 0, 'A : c\'est réglé')
g.press('start', 4)
g.w(90)
tunic = mem[2, 0xdec4] | mem[2, 0xdec5] << 8
check(tunic == COLOR, 'la tunique de Link, violette (%04x)' % tunic)
g.shot(os.path.join(OUT, 'a03_link.png'))

# Un autre lieu (de nouvelles palettes) : toujours violette
g.warp(1, 0x61, 0x47)
g.settled()
g.w(60)
g.text_through()
tunic = mem[2, 0xdec4] | mem[2, 0xdec5] << 8
check(tunic == COLOR, 'une autre salle : toujours violette (%04x)' % tunic)
g.warp(1, 0x62, 0x47)
g.settled()
g.w(60)
g.text_through()

# L'enlever (A dessus ; le menu se souvient de la case) : la tunique redevient verte
g.press('start', 4)
g.w(40)
g.press('select', 4)
g.w(60)
g.press('a', 4)
g.w(20)
check(g.m[ACTIVE] == 0xff and g.m[EDIT] == 0, 'A encore : il est enlevé')
g.press('start', 4)
g.w(90)
tunic = mem[2, 0xdec4] | mem[2, 0xdec5] << 8
check(tunic == 0x02 | 0x15 << 5 | 0x08 << 10, 'la tunique redevient verte (%04x)' % tunic)

# La bague Easter Egg : Marine sur son île, tout fini
g.m[GLOBAL_FLAGS + GLOBALFLAG_BALLADE_FIN // 8] |= 1 << (GLOBALFLAG_BALLADE_FIN % 8)
g.warp(1, 0x5c, 0x55)
g.settled()
g.w(60)
g.text_through()
check(not has(EASTER), 'pas encore de bague')
give(POWER)
give(ARMOR)
g.w(60)
g.stand(3, 7)
g.face('up')
g.press('a', 30)
check(g.wait_text(60), 'Marine, tout fini : sa bague')
g.shot(os.path.join(OUT, 'a04_marine.png'))
for _ in range(6):
    g.text_through()
    g.w(40)
check(has(EASTER), 'la bague Easter Egg, dans la boîte')
g.shot(os.path.join(OUT, 'a05_bague.png'))
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
