"""Test du Terrier des Serpents (donjon facultatif, 4:d0-d7 ; code/ages/balladeTerrier.s), par le menu
de test caché :

- le cimetière de l'ouest (île des Échos, 1:60) : la pancarte ; la tombe-chapelle de travers,
  poussée vers le haut, découvre l'escalier -> l'entrée (4:d0) ;
- le Gantelet des âmes, sur son socle (4:d1) : A devant ; la jarre des âmes apparaît ;
- les serpents (4:d2) : gris (palette 6), quatre coups d'épée ; chaque ennemi battu laisse une âme
  qui vole jusqu'à Link ; ils reviennent ;
- la porte des âmes s'ouvre à 4 âmes ;
- l'arène (4:d7) : à 16 âmes, le boss (la machine possédée), qui marche (son dessin change) et va
  jusqu'au mur de droite ; à moitié, son blindage tombe ; à zéro, le fantôme s'échappe ; battu : le
  Bracelet des Âmes, puis retour à l'entrée du Terrier ; l'épée lance alors toujours un rayon.

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
ENEMY_ROPE = 0x10
HEALTH = 0xc6aa
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

# Le cimetière de l'ouest (1:60) : la pancarte (2,8), la tombe-chapelle de travers (3,7)
g.warp(1, 0x60, 0x48)
g.settled()
g.w(60)
g.text_through()
check(g.tile(0x37) == 0xd9 and g.tile(0x04) != 0xdd, "la tombe de travers ; plus d'ouverture dans la falaise")
g.stand(3, 8)
g.hold('up', 10)
g.press('a', 10)
check(g.wait_text(60), "la pancarte : une tombe n'est pas à sa place")
g.text_through()
g.stand(4, 8, y_first=True)
g.stand(4, 7)
for _ in range(6):
    g.hold('up', 40)    # (il faut pousser un moment, sans lâcher)
    if g.tile(0x37) == 0xdc:
        break
g.w(60)
check(g.tile(0x37) == 0xdc and g.tile(0x27) == 0x02, "poussée : l'escalier sous la tombe")
g.shot(os.path.join(OUT, 'r00_tombe.png'))
for _ in range(12):
    g.hold('up', 8)
    if g.where()[0] == 4:
        break
g.settled()
g.w(60)
check(g.where() == (4, 0xd0), "l'escalier -> le Terrier (4:d0)")
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

# Les serpents (4:d2) : gris, quatre coups ; leurs âmes
g.route((5, 7), (5, 1))
check(g.go('left', (4, 0xd2)), 'les serpents (4:d2)')
g.text_through()
g.w(30)
snakes = g.enemies(ENEMY_ROPE)
check(len(snakes) == 3, 'trois serpents')
check(all(g.m[b + 0x1b] & 7 == 6 and g.m[b + 0x29] == 8 for b in snakes),
      "gris (palette 6), 8 de vie : quatre coups d'épée L-1")
g.shot(os.path.join(OUT, 'r02b_serpents.png'))
before = g.m[SOULS]
for b in snakes:
    g.m[b + 0x29] = 0
g.w(4)
check(len(objects(0x0b)) >= 1, 'des âmes s\'échappent')
g.shot(os.path.join(OUT, 'r03_ames.png'))
g.w(200)
check(g.m[SOULS] == before + 3, 'le gantelet absorbe trois âmes (%d -> %d)' % (before, g.m[SOULS]))
g.w(400)
check(len(g.enemies(ENEMY_ROPE)) >= 1, 'les serpents reviennent')
check(g.tile(0x07) == 0x78, 'la porte des âmes est fermée (3 âmes)')
g.m[SOULS] = 4
g.w(30)
check(g.tile(0x07) == 0xa0, 'à 4 âmes, la porte des âmes s\'ouvre')

# L'arène (4:d7) : à 16 âmes, le boss
g.m[SOULS] = 15
g.warp(4, 0xd7, 0x97)
g.settled()
g.w(60)
g.text_through()
check(g.where() == (4, 0xd7), "l'arène (4:d7)")
check(len(objects(0x0c)) == 0, 'pas encore de boss (15 âmes)')
g.m[SOULS] = 16
g.w(30)
check(g.wait_text(200), 'le boss apparaît : Marine')
g.text_through()
g.w(30)
boss = objects(0x0c)
check(len(boss) == 1, 'la machine possédée')
g.shot(os.path.join(OUT, 'r04_boss.png'))
if boss:
    b = boss[0]
    poses = set()
    for _ in range(60):
        g.w(1)
        poses.add(g.m[obj(b, 0x1e)] | g.m[obj(b, 0x1f)] << 8)
    check(len(poses) == 2, 'il marche : deux images de pattes (%d)' % len(poses))
    # Link tout à droite : il vient jusqu'à lui (avant, il s'arrêtait à 32 pixels du mur)
    g.m[obj(b, 0x0b)], g.m[obj(b, 0x0d)] = 0x58, 0x80
    hearts = g.m[HEALTH]
    for _ in range(150):
        g.m[0xd00b], g.m[0xd00d] = 0x68, 0xd8
        g.w(1)
    check(g.m[obj(b, 0x0d)] >= 0xc8, 'Link à droite : il le rattrape (x %02x)' % g.m[obj(b, 0x0d)])
    check(g.m[HEALTH] < hearts, 'et il le touche')
    g.m[HEALTH] = hearts
    g.m[obj(b, 0x0b)], g.m[obj(b, 0x0d)] = 0x48, 0x78
    g.m[0xd00b], g.m[0xd00d] = 0x88, 0x78
    g.w(2)
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
for _ in range(300):
    g.w(1)
    if g.where() == (4, 0xd0):
        break
g.settled()
g.w(40)
check(g.where() == (4, 0xd0), "puis retour à l'entrée du Terrier")
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
