"""Test de la Forge Endormie (donjon 4), jouée de bout en bout depuis le menu de test caché
(4. Donjon) : la petite clé 1, la porte à clé, la Suie (le mini-boss : une vraie flamme de la
Lanterne la brûle) et la Canne des Songes, la carte, le bouton (un bloc de la Canne : la petite clé
2), les deux boutons (un bloc poussé, un bloc de la Canne : la clé du boss), la boussole,
l'antichambre, Grisaille (Smog d'Ages), l'essence, la fin du chapitre 4.

Seule triche : les ennemis, le mini-boss (après une flamme qui le touche) et le boss sont retirés
(leur vie mise à zéro), et Link garde sa vie pleine.

Usage : python tools/test_forge.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import BOSS_KEYS, ESSENCES, HEALTH, INV_A, INV_B, MAX_HEALTH, TREASURES, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_CANE = 0x04
ENEMY_SHADOW_HAG, ENEMY_SMOG = 0x7a, 0x7c
TREASURE_HARP = 0x11
INTERAC_ESSENCE = 0x7f
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe(), 'clés', g.small_keys(4))
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def obtained(t):
    return bool(g.m[TREASURES + t // 8] & (1 << (t % 8)))


def full_life():
    g.m[HEALTH] = g.m[MAX_HEALTH]


def door(direction, room, y_first=False):
    """Se placer face à la porte (haut, bas : colonne 7 ; gauche, droite : ligne 5) et passer."""
    row, col = {'up': (2, 7), 'down': (8, 7), 'left': (5, 2), 'right': (5, 12)}[direction]
    g.stand(row, col, y_first)
    return g.go(direction, room)


def cane(row, col, facing):
    """Un bloc de la Canne des Songes (sur B) sur la case (row, col), Link à coté."""
    dy, dx = {'up': (1, 0), 'down': (-1, 0), 'left': (0, 1), 'right': (0, -1)}[facing]
    g.stand(row + dy, col + dx, y_first=True)
    g.face(facing)       # un appui bref : sans avancer sur le bouton
    g.press('b', 30)
    g.w(30)


g.level(4, 'Donjon')
g.m[INV_A], g.m[INV_B] = 0x05, 0x00
check(g.where() == (4, 0xbb), "l'entrée de la Forge Endormie (4:bb)")
check(g.wait_text(200), 'le nom du donjon')
shoot('f01_entree', "L'entrée")
g.text_through()

check(door('right', (4, 0xbc)), "à l'est de l'entrée (4:bc)")
g.clear_enemies()
check(door('right', (4, 0xbd)), "l'enclume froide (4:bd)")
g.clear_enemies()
g.w(120)
g.route((7, 7), (5, 7))   # la clé tombe au creux des blocs : par en dessous
g.w(60)
check(g.small_keys(4) == 1, 'la petite clé 1 (%d)' % g.small_keys(4))
g.route((7, 7), (7, 2))   # ressortir du creux par en dessous
check(door('left', (4, 0xbc)), 'retour')
check(door('up', (4, 0xb6)), 'la porte à clé mène au couloir (4:b6)')
g.clear_enemies()
check(door('up', (4, 0xb1)), 'la Suie (4:b1)')
check(bool(g.enemies(ENEMY_SHADOW_HAG)), 'la Suie est là')
# Elle surgit derrière Link (4 cases) et le charge ; s'il la regarde, elle s'enfuit. Link au milieu,
# tourné vers le haut : quand elle arrive (à trois cases), la flamme de la Lanterne devant lui, et il
# avance ; elle passe dans la flamme
g.m[INV_B] = TREASURE_HARP
hag = g.enemies(ENEMY_SHADOW_HAG)[0]
life = g.m[hag + 0x29]
shot_taken = False
for _ in range(2000):
    full_life()
    if not g.m[hag] or g.m[hag + 0x29] < life:
        break
    if g.m[0xcba0]:
        if not shot_taken:
            g.w(30)
            shoot('f02_suie', 'La Suie')
            shot_taken = True
        g.press('a', 10)
        continue
    # (la flamme brûle une demi-seconde : la poser quand la Suie n'est plus qu'à trois cases)
    if g.m[hag + 4] == 0x12 and g.m[hag + 0x0b] - g.link()[0] <= 0x30:
        g.press('b', 2)
        g.hold('up', 40)
        g.w(30)
        continue
    ly, lx = g.link()
    if abs(ly - 0x58) > 6 or abs(lx - 0x78) > 6:
        g.stand(5, 7)
        g.stand(4, 7)
        g.hold('up', 3)
    g.w(4)
check(g.m[hag + 0x29] < life, 'la flamme de la Lanterne brûle la Suie (%d -> %d)' % (life, g.m[hag + 0x29]))
g.m[INV_B] = 0x00
for _ in range(4):
    full_life()
    g.clear_enemies()
    g.text_through()
g.w(200)
check(not g.enemies(ENEMY_SHADOW_HAG), 'la Suie est battue')
check(g.open_chest(5, 7), 'le coffre apparaît : la Canne des Songes')
check(obtained(TREASURE_CANE), 'la Canne des Songes')
shoot('f03_canne', 'La Canne des Songes')
g.m[INV_B] = TREASURE_CANE

check(door('right', (4, 0xb2)), "l'est : la carte (4:b2)")
g.clear_enemies()
check(g.open_chest(5, 11), 'coffre ouvert : la carte')
check(door('left', (4, 0xb1)), 'retour chez la Suie')
g.route((7, 12), (7, 2))   # le coffre de la Canne est au milieu de la salle
check(door('left', (4, 0xb0)), 'le bouton (4:b0)')
# Un bloc de la Canne sur le bouton (ligne 8, colonne 3) : le coffre de la petite clé 2 (2, 2)
g.route((9, 13), (9, 3))   # le gouffre du milieu : par le bas
cane(8, 3, 'up')
shoot('f04_bouton', 'Un bloc sur le bouton')
g.wait_until(lambda: g.tile(0x22) == 0xf1, 120)
check(g.tile(0x22) == 0xf1, 'le coffre apparaît')
g.route((8, 1), (3, 1))
g.stand(3, 2)
g.hold('up', 12)
g.press('a', 60)
g.text_through(10)
g.w(60)
check(g.small_keys(4) == 0 and g.tile(0x22) == 0xf0, 'le coffre : des rubis (la petite clé 2 ne sert plus)')
check(door('left', (4, 0xaf)), "à l'ouest (4:af)")
g.clear_enemies()
check(g.open_chest(2, 7), 'coffre ouvert : des rubis')
check(door('left', (4, 0xae)), 'les deux boutons (4:ae)')
# Le bloc (ligne 4, colonne 4) poussé vers le haut sur le bouton (3, 4) ; un bloc de la Canne sur
# l'autre (3, 10)
g.stand(5, 4, y_first=True)
g.hold('up', 40)
g.w(30)
check(g.tile(0x34) != 0x0c, 'le bloc est sur le premier bouton')
cane(3, 10, 'up')
g.wait_until(lambda: g.tile(0x77) == 0xf1, 120)
shoot('f05_boutons', 'Les deux boutons')
check(g.tile(0x77) == 0xf1, 'le coffre de la clé du boss apparaît')
check(g.open_chest(7, 7), 'coffre ouvert : la clé du boss')
check(bool(g.m[BOSS_KEYS] & 0x10), 'la clé du boss')

# Retour à l'entrée, puis l'ouest : la boussole, la porte à clé de l'antichambre
check(door('right', (4, 0xaf)) and door('right', (4, 0xb0)), 'retour vers le bouton')
g.route((9, 1), (9, 13))   # le gouffre : par le bas
check(door('right', (4, 0xb1)), 'retour vers la Suie')
g.route((7, 2), (7, 7))
check(door('down', (4, 0xb6)) and door('down', (4, 0xbc)) and door('left', (4, 0xbb)), "retour à l'entrée")
check(door('left', (4, 0xba)), "à l'ouest de l'entrée (4:ba)")
g.clear_enemies()
check(door('left', (4, 0xb9)), 'la boussole (4:b9)')
g.clear_enemies()
check(g.open_chest(5, 3), 'coffre ouvert : la boussole')
check(door('right', (4, 0xba)), 'retour')
check(door('up', (4, 0xbe)), "la porte du boss (la clé du boss) mène à l'antichambre (4:be)")
shoot('f06_antichambre', "L'antichambre")
check(door('right', (4, 0xbf)), 'la porte du boss : Grisaille (4:bf)')
g.w(60)
check(g.wait_text(300), 'Grisaille parle, Marine chante')
shoot('f07_grisaille', 'Grisaille')
for _ in range(10):
    g.text_through()
    g.w(30)
check(bool(g.enemies(ENEMY_SMOG)), 'Grisaille est là')
for _ in range(12):
    full_life()
    g.clear_enemies()
    g.text_through()
g.w(300)
g.text_through()
check(not g.enemies(ENEMY_SMOG), 'Grisaille est battu')
check(g.room_flags(4, 0xbf) & 0x80, 'drapeau de sa salle ($80)')
g.w(200)
shoot('f08_essence', "L'essence")
check(any(g.m[h * 256 + 0x40] and g.m[h * 256 + 0x41] == INTERAC_ESSENCE for h in range(0xd2, 0xe0)),
      "l'essence apparaît")
for _ in range(8):
    if g.where() != (4, 0xbf):
        break
    # l'essence (ligne 7, colonne 3 : à l'écart des blocs du combat) : la toucher par en dessous
    g.goto(None, 0x18)   # le piédestal barre la colonne : par la gauche
    g.goto(0x98, None)
    g.goto(None, 0x38)
    g.hold('up', 40)
    g.w(30)
    g.text_through()
    g.press('a', 30)
g.w(200)
g.settled()
check(bool(g.m[ESSENCES] & 0x08), "l'essence de la Forge (le quatrième couplet)")
check(g.where() == (1, 0x2a), 'retour au village goron (1:2a)')
check(g.wait_text(300), 'la fin du chapitre 4')
shoot('f09_village', 'Le village fête la Forge')
for _ in range(10):
    g.text_through()
    g.w(120)
check(g.global_flag(0x54), "l'île des Échos repérée (GLOBALFLAG_BALLADE_ISLAND5)")

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
