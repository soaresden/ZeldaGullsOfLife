"""Test de l'île 5, l'île des Échos, par le menu de test caché (tools/debug_menu.py).

- arrivée au ponton (Marine parle) ; le Bateau-Rondin à deux pages (« Suite » : Mont-Braise, retour) ;
- la cabane du fossoyeur : Bêche prête la Pelle ;
- la place du silence : Noé ne se souvient plus de la voix de sa grand-mère ; la Lanterne : dans
  le Songe (sépia), Mamie Rose dit où est enterrée la clé de la cathédrale ;
- la chapelle (le sonneur), le cimetière de l'est : la Pelle déterre la clé devant la tombe fleurie
  (dans le Songe : elle y est aussi) ;
- Mamie Rose donne le quart de cœur de sa boîte à couture ;
- le parvis, la cathédrale : la clé ouvre la grille ; la veuve Marée sur son rocher.

Usage : python tools/test_echos.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, TREASURES, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_HARP, TREASURE_SHOVEL, TREASURE_GRAVEYARD_KEY = 0x11, 0x15, 0x42
HEART_PIECES = 0xc6ac       # wNumHeartPieces
errors, shots = [], []


def check(ok, what, g=None):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        if g:
            print('     ', g.describe())
            g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(g, name, label=None):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label or name))


def obtained(g, t):
    return bool(g.m[TREASURES + t // 8] & (1 << (t % 8)))


def talk(g, row, col, facing='up'):
    g.stand(row, col)
    g.hold(facing, 8)
    g.press('a', 20)
    ok = g.wait_text(60)
    g.w(30)
    return ok


def door(g, direction, room):
    row, col = {'up': (1, 4), 'down': (6, 4), 'left': (4, 1), 'right': (4, 8)}[direction]
    g.stand(row, col, y_first=direction in ('left', 'right'))
    return g.go(direction, room)


def lantern(g, group):
    g.m[INV_B] = TREASURE_HARP
    g.press('b', 10)
    g.wait_until(lambda: g.where()[0] == group, 600)
    g.settled()
    g.w(160)


g = Game()
g.level(5, 'Plage')
g.m[INV_A], g.m[INV_B] = 0x00, TREASURE_HARP
check(g.where() == (1, 0x70), "le ponton de l'île des Échos (1:70)", g)
check(g.wait_text(200), 'Marine parle en arrivant', g)
g.w(60)
shoot(g, 'e01_arrivee', 'Arrivée au ponton')
g.text_through()

# Le Bateau-Rondin (y $68, x $58) : 5 îles repérées, deux pages (« Suite », puis Mont-Braise) ; et
# retour par la deuxième page
g.stand(6, 4)
g.face('right')
g.press('a', 20)
g.choose(3, 4)
g.choose(0, 2)
g.w(30)
g.settled()
g.w(60)
check(g.where() == (1, 0x38), 'le Bateau-Rondin : « Suite », Mont-Braise', g)
g.text_through()
g.stand(6, 4)
g.face('right')
g.press('a', 20)
g.choose(3, 4)
g.choose(1, 2)
g.w(30)
g.settled()
g.w(60)
check(g.where() == (1, 0x70), 'et retour aux Échos', g)
g.text_through()

check(door(g, 'right', (1, 0x71)), 'la plage grise (1:71)', g)
check(door(g, 'up', (1, 0x61)), 'devant la cabane du fossoyeur (1:61)', g)
g.stand(2, 4)
check(g.go('up', (3, 0x25)), 'la cabane (3:25)', g)
check(talk(g, 5, 3), 'Bêche parle', g)
shoot(g, 'e02_beche', 'Bêche, le fossoyeur')
g.text_through()
g.w(60)
g.text_through()
check(obtained(g, TREASURE_SHOVEL), 'la Pelle', g)
g.stand(6, 4)
check(g.go('down', (1, 0x61)), 'on ressort', g)

check(door(g, 'right', (1, 0x62)), 'la place du silence (1:62)', g)
check(talk(g, 4, 6), 'Noé', g)
shoot(g, 'e03_noe', 'Noé')
g.text_through()
lantern(g, 0)
check(g.where() == (0, 0x62), 'la Lanterne : le Songe sépia (0:62)', g)
check(talk(g, 4, 6), 'Mamie Rose, dans le Songe', g)
shoot(g, 'e04_mamie', 'Mamie Rose')
g.text_through()
lantern(g, 1)
check(g.where() == (1, 0x62), 'retour au Réel', g)

check(door(g, 'right', (1, 0x63)), 'la chapelle (1:63)', g)
check(talk(g, 4, 4), 'le sonneur', g)
g.text_through()
check(door(g, 'right', (1, 0x64)), "le cimetière de l'est (1:64)", g)
check(g.wait_text(200), 'Marine : la tombe fleurie', g)
g.text_through()
# La Pelle sur B : creuser devant la tombe fleurie (ligne 5, colonne 5), Link en dessous. Dans le
# Songe, là où Mamie Rose en parle (Denis y a creusé : la clé y est aussi)
lantern(g, 0)
check(g.where() == (0, 0x64), "le cimetière de l'est, dans le Songe (0:64)", g)
g.route((4, 1), (6, 1), (6, 5))   # les fleurs bordent la tombe : on passe par en dessous
g.face('up')
g.m[INV_B] = TREASURE_SHOVEL
g.press('b', 40)
g.w(60)
shoot(g, 'e05_cle', 'La clé déterrée (dans le Songe)')
g.text_through()
g.w(60)
g.text_through()
check(obtained(g, TREASURE_GRAVEYARD_KEY), 'la clé de la cathédrale', g)
lantern(g, 1)
check(g.where() == (1, 0x64), 'retour au Réel', g)

# Mamie Rose : le quart de cœur
g.route((6, 1), (4, 1))
check(g.go('left', (1, 0x63)) and door(g, 'left', (1, 0x62)), 'retour à la place', g)
h0 = g.m[HEART_PIECES]
lantern(g, 0)
check(talk(g, 4, 6), 'Mamie Rose, encore', g)
g.text_through()
g.w(60)
g.text_through()
check(g.m[HEART_PIECES] != h0, 'le quart de cœur de la boîte à couture', g)
lantern(g, 1)

# Le parvis, la cathédrale : la grille
check(door(g, 'up', (1, 0x52)), 'le parvis (1:52)', g)
check(door(g, 'up', (1, 0x42)), 'la cathédrale (1:42)', g)
g.stand(5, 4)
g.face('up')
g.press('a', 40)
g.w(60)
check(g.tile(0x44) == 0xdd, 'la clé ouvre la grille', g)
shoot(g, 'e06_cathedrale', 'La cathédrale des Échos')

# La veuve Marée (1:74)
g.warp(1, 0x74, 0x34)
check(talk(g, 3, 6), 'la veuve Marée', g)
shoot(g, 'e07_maree', 'La veuve Marée')
g.text_through()

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
