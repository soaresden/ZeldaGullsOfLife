"""Test de l'île 7, l'île du Grand Sommeil, par le menu de test caché (tools/debug_menu.py).
- arrivée au ponton (Marine : toute l'île dort) ; le roi d'une nuit dort (branche sud) ;
- la maison du veilleur : le Lance-Graines (et la sacoche, 20 graines de feu) ;
- le Palais Givré : la porte est prise dans la glace ;
- la Lanterne : dans le Songe, l'étang n'est pas gelé ; le cristal de l'îlot, frappé en biais d'une
  graine du Lance-Graines, dégèle la porte du Réel ;
- le roi dans le Songe (il dit où frapper) ; la maison de la famille : la petite sœur, la mère et
  le père endormis ;
- la porte dégelée : l'entrée du Palais Givré.
Usage : python tools/test_sommeil.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, TEXT_ACTIVE, TREASURES, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_SHOOTER, TREASURE_HARP, TREASURE_SEED_SATCHEL = 0x0f, 0x11, 0x19
EMBER_SEEDS = 0xc6b9          # wNumEmberSeeds (BCD)
SWITCH_STATE = 0xcdd3         # wSwitchState
GROUP1_FLAGS = 0xc800         # wGroup1RoomFlags
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
    g.face(facing)
    g.press('a', 20)
    ok = g.wait_text(60)
    g.w(30)
    return ok


def door(g, direction, room):
    row, col = {'up': (1, 4), 'down': (6, 4), 'left': (4, 1), 'right': (4, 8)}[direction]
    g.stand(row, col, y_first=direction in ('left', 'right'))
    return g.go(direction, room)


def enter(g, row, col, room):
    """Entrer par la porte (row, col) : depuis la case du dessous, vers le haut."""
    g.stand(row + 1, col)
    return g.go('up', room)


def lantern(g, group):
    g.m[INV_B] = TREASURE_HARP
    g.press('b', 10)
    g.wait_until(lambda: g.where()[0] == group and g.m[0xd004] == 0x0a, 600)   # le rayon de lumière
    g.wait_until(lambda: g.m[0xd004] == 0x01, 600)                              # Link a la main


g = Game()
g.level(7, 'Plage')
g.m[INV_A], g.m[INV_B] = 0x05, TREASURE_HARP
check(g.where() == (1, 0xd1), "le ponton de l'île du Grand Sommeil (1:d1)", g)
check(g.wait_text(200), 'Marine : toute l\'île dort', g)
g.w(60)
shoot(g, 's01_arrivee', 'Arrivée : toute l\'île dort')
g.text_through()

# La branche sud : le roi d'une nuit dort
check(door(g, 'right', (1, 0xd2)), 'la branche sud (1:d2)', g)
check(talk(g, 4, 6, 'down'), "le roi d'une nuit (endormi)", g)
shoot(g, 's02_roi', "Le roi d'une nuit dort")
g.text_through()

# La maison du veilleur : le Lance-Graines
check(door(g, 'up', (1, 0xc2)), 'la maison du veilleur, dehors (1:c2)', g)
check(enter(g, 2, 7, (3, 0x27)), 'la maison du veilleur (3:27)', g)
g.settled()
check(talk(g, 5, 3), 'le veilleur', g)
shoot(g, 's03_veilleur', 'Le veilleur')
for _ in range(12):
    g.text_through()
    g.w(40)
check(obtained(g, TREASURE_SHOOTER), 'le Lance-Graines', g)
check(obtained(g, TREASURE_SEED_SATCHEL) and g.m[EMBER_SEEDS] == 0x20, 'la sacoche, 20 graines de feu', g)
check(talk(g, 5, 3), 'le veilleur, ensuite : « dans les rêves, pas de glace »', g)
g.text_through()
g.route((6, 3), (6, 4))
check(g.go('down', (1, 0xc2)), 'ressorti (1:c2)', g)

# Le Palais Givré : la porte gelée
check(door(g, 'up', (1, 0xb2)), 'le Palais Givré (1:b2)', g)
check(g.wait_text(200), 'Marine : la porte est gelée', g)
g.text_through()
check(g.tile(0x25) == 0xf6, 'la porte prise dans la glace (un mur)', g)
check(talk(g, 3, 5), 'A devant : « prise dans une glace épaisse »', g)
shoot(g, 's04_porte', 'La porte gelée du Palais Givré')
g.text_through()

# Le Songe : l'étang n'est pas gelé ; le cristal frappé en biais
g.stand(3, 2)
g.face('down')
lantern(g, 0)
check(g.where() == (0, 0xb2), 'la Lanterne : le palais dans le Songe (0:b2)', g)
check(g.tile(0x54) == 0x9e, "le cristal sur l'îlot", g)
shoot(g, 's05_songe', 'Dans le Songe, l\'étang n\'est pas gelé')
g.m[INV_B] = TREASURE_SHOOTER
g.face('down')
g.pb.button_press('b')
g.w(10)
g.pb.button_press('right')       # le Lance-Graines tourne : en bas à droite
g.w(16)
g.pb.button_release('right')
g.pb.button_release('b')         # on tire
g.wait_until(lambda: g.m[TEXT_ACTIVE], 120)
g.w(20)
check(bool(g.m[GROUP1_FLAGS + 0xb2] & 0x80), 'le cristal frappé en biais : la porte du Réel dégèle', g)
shoot(g, 's06_cristal', 'Le cristal a chanté')
g.text_through()
lantern(g, 1)
check(g.where() == (1, 0xb2), 'retour au Réel (1:b2)', g)
g.w(30)
check(g.tile(0x25) == 0xde, 'la porte du palais est dégelée', g)
shoot(g, 's07_porte_ouverte', 'La porte dégelée')

# Le roi dans le Songe (on descend par le chemin de pavés qui traverse l'étang gelé)
g.route((3, 5), (6, 5))
check(g.go('down', (1, 0xc2)), 'la maison du veilleur (1:c2)', g)
check(door(g, 'down', (1, 0xd2)), 'la branche sud (1:d2)', g)
g.stand(3, 6)
lantern(g, 0)
check(g.where() == (0, 0xd2), 'la Lanterne : la branche sud dans le Songe (0:d2)', g)
check(talk(g, 4, 6, 'down'), 'le roi dans le Songe', g)
shoot(g, 's08_roi_songe', 'Dans le Songe, il est roi')
g.text_through()
g.stand(3, 6)
lantern(g, 1)
check(g.where() == (1, 0xd2), 'retour au Réel', g)

# La maison de la famille : la petite sœur, la mère et le père endormis
check(door(g, 'up', (1, 0xc2)), 'la maison du veilleur (1:c2)', g)
check(door(g, 'up', (1, 0xb2)), 'le palais (1:b2)', g)
g.route((3, 5), (3, 1))      # au nord de l'étang gelé
check(g.go('left', (1, 0xb1)), 'le village gelé (1:b1)', g)
check(enter(g, 2, 2, (3, 0x28)), 'la maison de la famille (3:28)', g)
g.settled()
check(talk(g, 5, 3), 'la petite sœur', g)
shoot(g, 's09_famille', 'La petite sœur, la famille endormie')
g.text_through()
check(talk(g, 4, 5), 'la mère endormie', g)
g.text_through()
g.route((6, 3), (6, 4))
check(g.go('down', (1, 0xb1)), 'ressorti (1:b1)', g)

# La porte dégelée : le Palais Givré
check(door(g, 'right', (1, 0xb2)), 'le palais (1:b2)', g)
check(enter(g, 2, 5, (4, 0x55)), 'la porte dégelée : le Palais Givré (4:55)', g)
g.settled()
g.w(60)
shoot(g, 's10_palais', 'Le Palais Givré')

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
