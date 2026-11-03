"""Test du Terrier des Serpents (donjon facultatif, 4:d0-d7 ; code/ages/balladeTerrier.s), par le menu
de test caché :

- le cimetière de l'ouest (île des Échos, 1:60) : la pancarte ; la tombe-chapelle de travers,
  poussée vers le haut, découvre l'escalier -> l'entrée (4:d0) ;
- le Gantelet des âmes, sur son socle (4:d1) : A devant ; la jarre des âmes apparaît ;
- les serpents (4:d2) : gris (palette 6), quatre coups d'épée ; chaque ennemi battu laisse une âme
  qui vole jusqu'à Link ; ils reviennent ;
- la porte des âmes s'ouvre à 4 âmes ;
- l'arène (4:d7) : à 16 âmes, le boss (la machine possédée, en grand dans le décor) sort de l'ombre ;
  elle danse (la dernière manche seulement : tools/test_danse.py teste tout) ; elle explose : le
  Bracelet des Âmes, puis retour à l'entrée du Terrier ; l'épée ne lance pas de rayon (le Bracelet
  n'agit que sur l'attaque tourbillon : il aspire les âmes, Denis).

Usage : python tools/test_terrier.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, Game
from danse_bot import play_round, ram

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
g.w(80)
check([g.tile(0x14 + r * 16 + c) for r in range(5) for c in range(7)] == list(range(0xc0, 0xc0 + 35)),
      "elle sort de l'ombre : ses 35 briques au fond de l'arène")
check(g.m[0xd00b] >= 0x70, 'Link devant elle, pas dedans (y %02x)' % g.m[0xd00b])
g.shot(os.path.join(OUT, 'r04_boss.png'))
if boss:
    # Elle danse (tools/test_danse.py teste les cinq manches) : ici, directement la dernière
    b = boss[0]
    check(g.wait_text(200), 'Marine explique la danse')
    g.m[1, obj(b, 0x30)] = 1
    g.text_through()
    hits, judged = play_round(g, b)
    check(hits == judged and judged > 0, 'la dernière manche dansée (%d/%d)' % (hits, judged))
    g.w(20)
    check(ram(g, obj(b, 0x04)) >= 3, 'elle explose')
    for _ in range(400):
        g.w(1)
        if g.m[SOUL_STATE] & 2:
            break
    check(g.tile(0x14) == 0xa0 and g.tile(0x56) == 0xa0, 'elle a disparu : le sol')
    g.shot(os.path.join(OUT, 'r07_explosee.png'))
check(g.m[SOUL_STATE] & 2 == 2, 'le gantelet absorbe son âme : le Bracelet des Âmes')
check(g.wait_text(120), 'la relique')
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

# Plus de rayon des âmes (Denis : le Bracelet n'agit que sur le tourbillon) : l'épée en B, un coup
g.m[INV_B] = 0x05
g.w(10)
g.press('b', 4)
beam = False
for _ in range(30):
    g.w(1)
    if any(g.m[(s << 8)] and g.m[(s << 8) + 1] == 0x27 for s in range(0xd6, 0xe0)):
        beam = True
        break
check(not beam, "l'épée ne lance pas de rayon")
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
