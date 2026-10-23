"""Test du Terrier des Serpents (donjon facultatif, 4:d0-d7 ; code/ages/balladeTerrier.s), par le menu
de test caché :

- l'ouverture dans la falaise du cimetière de l'ouest (île des Échos, 1:60) -> l'entrée (4:d0) ;
- le Gantelet des âmes, sur son socle (4:d1) : A devant ; la jarre des âmes apparaît ;
- les Stalfos (4:d2) : chaque ennemi battu laisse une âme qui vole jusqu'à Link ; ils reviennent ;
- la porte des âmes s'ouvre à 6 âmes ;
- l'arène (4:d7) : à 24 âmes, le boss (la machine possédée) ; à moitié, son blindage tombe ; à zéro,
  le fantôme s'échappe ; battu : le Bracelet des Âmes ; l'épée lance alors toujours un rayon.

Usage : python tools/test_terrier.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SOULS, SOUL_STATE = 0xc6c4, 0xc6c5
WEAPON = 0xd600
INTERAC = 0xeb
ENEMY_STALFOS = 0x31
errors = []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def objects(subid):
    return [s for s in range(0xd0, 0xe0)
            if g.m[(s << 8) + 0x40] and g.m[(s << 8) + 0x41] == INTERAC and g.m[(s << 8) + 0x42] == subid]


def obj(slot, field):
    return (slot << 8) + 0x40 + field


def hit(slot):
    """Un coup d'épée : l'épée posée sur l'objet, une image."""
    g.m[WEAPON] = 1
    g.m[WEAPON + 0x0b] = g.m[obj(slot, 0x0b)]
    g.m[WEAPON + 0x0d] = g.m[obj(slot, 0x0d)]
    g.w(1)
    g.m[WEAPON] = 0


g = Game()
g.level(5, 'Ville')
g.m[INV_A], g.m[INV_B] = 0x00, 0x00
g.text_through()
g.m[SOULS] = 0
g.m[SOUL_STATE] = 0

# L'ouverture dans la falaise (1:60, ligne 0 colonne 4)
g.warp(1, 0x60, 0x14)
g.settled()
g.w(60)
g.text_through()
g.goto(None, 0x48)
for _ in range(12):
    g.hold('up', 8)
    if g.where()[0] == 4:
        break
g.settled()
g.w(60)
check(g.where() == (4, 0xd0), "l'ouverture de la falaise -> le Terrier (4:d0)")
g.hold('up', 20)
check(g.wait_text(200), 'en entrant : le nom du donjon, Marine')
g.shot(os.path.join(OUT, 'r01_entree.png'))
for _ in range(4):
    g.text_through()
    g.w(30)

# Le Gantelet des âmes (4:d1, au milieu)
g.route((8, 7), (1, 7))
check(g.go('up', (4, 0xd1)), 'la salle du gantelet (4:d1)')
g.text_through()
g.stand(6, 7)
g.face('up')
g.press('a', 30)
check(g.wait_text(120), 'Link prend le Gantelet des âmes')
g.shot(os.path.join(OUT, 'r02_gantelet.png'))
g.text_through()
g.w(20)
check(g.m[SOUL_STATE] & 1 == 1, 'le gantelet (bit 0)')
check(len(objects(0x0e)) == 1, 'la jarre des âmes')

# Les Stalfos (4:d2) : leurs âmes
g.route((5, 7), (5, 1))
check(g.go('left', (4, 0xd2)), 'les Stalfos (4:d2)')
g.text_through()
g.w(30)
stalfos = g.enemies(ENEMY_STALFOS)
check(len(stalfos) == 3, 'trois Stalfos')
before = g.m[SOULS]
for b in stalfos:
    g.m[b + 0x29] = 0
g.w(4)
check(len(objects(0x0b)) >= 1, 'des âmes s\'échappent')
g.shot(os.path.join(OUT, 'r03_ames.png'))
g.w(200)
check(g.m[SOULS] == before + 3, 'le gantelet absorbe trois âmes (%d -> %d)' % (before, g.m[SOULS]))
g.w(400)
check(len(g.enemies(ENEMY_STALFOS)) >= 1, 'les Stalfos reviennent')
check(g.tile(0x07) == 0x78, 'la porte des âmes est fermée (3 âmes)')
g.m[SOULS] = 6
g.w(30)
check(g.tile(0x07) == 0xa0, 'à 6 âmes, la porte des âmes s\'ouvre')

# L'arène (4:d7) : à 24 âmes, le boss
g.m[SOULS] = 23
g.warp(4, 0xd7, 0x97)
g.settled()
g.w(60)
g.text_through()
check(g.where() == (4, 0xd7), "l'arène (4:d7)")
check(len(objects(0x0c)) == 0, 'pas encore de boss (23 âmes)')
g.m[SOULS] = 24
g.w(30)
check(g.wait_text(200), 'le boss apparaît : Marine')
g.text_through()
g.w(30)
boss = objects(0x0c)
check(len(boss) == 1, 'la machine possédée')
g.shot(os.path.join(OUT, 'r04_boss.png'))
if boss:
    b = boss[0]
    souls = g.m[SOULS]
    hit(b)
    g.w(10)
    check(g.m[obj(b, 0x30)] == 11, 'un coup : une âme arrachée (vie 11)')
    g.m[obj(b, 0x30)] = 7
    g.m[obj(b, 0x31)] = 0
    hit(b)
    g.w(20)
    check(g.m[obj(b, 0x32)] == 1, 'à moitié : son blindage tombe')
    g.shot(os.path.join(OUT, 'r05_blesse.png'))
    g.m[obj(b, 0x30)] = 1
    g.m[obj(b, 0x31)] = 0
    hit(b)
    g.w(20)
check(len(objects(0x0c)) == 0 and len(objects(0x0f)) == 1, 'la machine tombe : le fantôme s\'échappe')
ghost = objects(0x0f)
g.shot(os.path.join(OUT, 'r06_fantome.png'))
if ghost:
    s = ghost[0]
    g.m[obj(s, 0x30)] = 1
    g.m[obj(s, 0x31)] = 0
    hit(s)
    g.w(10)
check(g.m[SOUL_STATE] & 2 == 2, 'le fantôme battu : le Bracelet des Âmes')
check(g.wait_text(120), 'Marine... la relique')
g.text_through()
# Marine félicite Link (INTERAC_MARINE $08) : sa réplique, une fois les textes finis
check(g.wait_text(150), 'Marine félicite Link')
g.text_through()

# Le rayon des âmes : l'épée en B, un coup
g.m[INV_B] = 0x05
g.w(10)
g.press('b', 4)
beam = False
for _ in range(30):
    g.w(1)
    if any(g.m[(s << 8)] and g.m[(s << 8) + 1] == 0x27 for s in range(0xd6, 0xe0)):
        beam = True
        break
check(beam, "l'épée lance un rayon")
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
