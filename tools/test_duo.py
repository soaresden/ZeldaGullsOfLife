"""Test de Marine qui suit Link après la fin (code/ages/balladeFin.s), par le menu de test caché :

- sur son île (1:5c), « Viens ! » : elle suit Link d'écran en écran, et sur une autre île ;
- quand l'épée de Link sort, elle frappe aussi (son coup d'épée blesse les ennemis tout près) ;
- quand Link ne fait rien, elle chante la Ballade du Poisson-Rêve ; dès qu'il bouge, elle s'arrête ;
- en revenant dans un donjon (le Phare), il est comme neuf : ses salles perdent leurs drapeaux (la
  salle du boss garde son réceptacle).

Usage : python tools/test_duo.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, INV_A, INV_B, ROOM_FLAGS, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
FOLLOW = 0xc4bf
ACTIVE_MUSIC = 0xcc35
INTERAC = 0xeb
ENEMY_OCTOROK = 0x09
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


g = Game()
g.level(8, 'Plage')
g.m[INV_A], g.m[INV_B] = 0x00, 0x05        # l'épée en B
g.text_through()
g.m[GLOBAL_FLAGS + 0x5d // 8] |= 1 << (0x5d % 8)

# Sur son île : « Viens ! » (la 3e option)
g.warp(1, 0x5c, 0x55)
g.settled()
g.w(60)
g.text_through()
g.stand(3, 7)
g.face('up')
g.press('a', 30)
check(g.wait_text(60), 'Marine : « On fait quoi ? »')
g.choose(2, 4)
g.w(30)
g.text_through()
g.w(30)
g.text_through()
check(g.m[FOLLOW] == 1 and len(objects(0x19)) == 1, 'Marine prend son épée et suit Link')
g.shot(os.path.join(OUT, 'd01_viens.png'))

# Elle le suit : la plage aux palmiers (1:6c, au sud)
g.warp(1, 0x6c, 0x15)
g.settled()
g.w(90)
check(g.where() == (1, 0x6c) and len(objects(0x19)) == 1, 'elle suit Link sur la plage aux palmiers (1:6c)')
g.shot(os.path.join(OUT, 'd02_plage.png'))

# Son épée : un Octorok tout près d'elle perd des points de vie
octo = g.enemies(ENEMY_OCTOROK)
check(len(octo) >= 1, 'des monstres sur la plage')
if octo and objects(0x19):
    m = objects(0x19)[0]
    b = octo[0]
    g.m[(m << 8) + 0x40 + 0x0b] = g.m[b + 0x0b]
    g.m[(m << 8) + 0x40 + 0x0d] = g.m[b + 0x0d] - 0x0e
    g.m[(m << 8) + 0x40 + 0x31] = 3            # elle regarde à droite
    life = g.m[b + 0x29]
    g.press('b', 4)
    hit = False
    for k in range(20):
        g.w(1)
        if k < 3:
            print('  épée de Link', g.m[0xd600], 'Marine état', g.m[(m << 8) + 0x44], 'attente', g.m[(m << 8) + 0x70])
        if objects(0x1b):
            hit = True
    g.w(10)
    check(hit, 'quand Link frappe, Marine frappe aussi')
    check(g.m[b + 0x29] < life or not g.m[b], "son coup d'épée blesse l'Octorok (%d -> %d)" % (life, g.m[b + 0x29]))
    g.shot(os.path.join(OUT, 'd03_epee.png'))

# Link ne fait rien : elle chante ; il bouge : elle s'arrête (au calme, sur le ponton)
g.warp(1, 0x6b, 0x24)
g.w(150)
music = g.m[ACTIVE_MUSIC]
g.w(660)
check(g.m[ACTIVE_MUSIC] == 0x01, 'Link ne fait rien : Marine chante la Ballade (musique %02x)' % g.m[ACTIVE_MUSIC])
g.shot(os.path.join(OUT, 'd04_chante.png'))
g.hold('left', 10)
g.w(20)
check(g.m[ACTIVE_MUSIC] == music, 'Link bouge : elle s\'arrête (musique %02x)' % g.m[ACTIVE_MUSIC])

# Sur une autre île : Port-Veille (1:9a)
g.warp(1, 0x9a, 0x55)
g.w(150)
check(len(objects(0x19)) == 1, 'elle vient aussi sur les autres îles (1:9a)')
g.shot(os.path.join(OUT, 'd05_port.png'))

# Un donjon comme neuf : le Phare (on entre par sa porte du Songe, 0:7b)
flags = ROOM_FLAGS[4]
g.m[flags + 0x1e] = 0x30 | 0x01      # visitée, coffre ouvert, une porte à clé
g.m[flags + 0x13] = 0xb0             # la salle du boss : visitée, réceptacle pris, boss battu
g.warp(0, 0x7b, 0x54)
g.w(150)
for _ in range(8):
    g.text_through()
    g.hold('up', 12)
    if g.where()[0] == 4:
        break
g.settled()
g.w(60)
check(g.where()[0] == 4, 'dans le Phare (%d:%02x)' % g.where())
check(g.m[flags + 0x1e] == 0x10, 'les salles du Phare sont comme neuves (4:1e : %02x)' % g.m[flags + 0x1e])
check(g.m[flags + 0x13] == 0x30, 'la salle du boss : le boss revient, pas le réceptacle (4:13 : %02x)' % g.m[flags + 0x13])
check(len(objects(0x19)) == 1, 'Marine entre dans le donjon avec Link')
g.shot(os.path.join(OUT, 'd06_phare.png'))

# Chez elle (sa maison, 3:2a) : elle reste là, et Link reviendra la chercher sur la plage
g.warp(3, 0x2a, 0x55)
g.settled()
check(g.wait_text(90), 'chez elle : « Je reste un peu ici »')
g.text_through()
g.w(30)
check(g.m[FOLLOW] == 0 and len(objects(0x19)) == 1, 'elle reste chez elle (elle ne suit plus Link)')
g.shot(os.path.join(OUT, 'd07_maison.png'))
g.warp(1, 0x5c, 0x55)
g.settled()
g.w(60)
check(len(objects(0x14)) == 1 and not objects(0x19), 'elle est de nouveau sur la plage de son île')
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
