"""Test de la Spirale Céleste (donjon 6), jouée de bout en bout depuis le menu de test caché (6.
Donjon). Chaque énigme est résolue comme un joueur :
- 3d le premier saut (la Plume de Roc) ;
- 3e le bouton de l'îlot : un saut, un bloc de la Canne dessus, le volet de l'ouest s'ouvre ;
- 3f trois cases de gouffre : le Grappin-Écho (l'îlot, la petite clé 1, puis la rive ouest) ;
- 40 le cristal de la rive d'en face au Boomerang : le pont se pose case par case ;
- 41 le mur fissuré : une bombe, la salle secrète (49, 100 rubis) ;
- 42 le carrelage bleu peint d'un seul trait (la carte) ;
- 43 les chauves-souris (la boussole) ; le cristal au Boomerang-Toupie (le volet du nord) ;
- 44 le cristal emmuré de statues : Marine porte la bombe (Select), le volet de l'est s'ouvre ;
- 45 les deux ponts : le cristal frappé depuis l'îlot, un pont se replie, l'autre se déploie ;
- 46 le Grappin-Écho puis un saut (la petite clé 2), et le retour par deux sauts ;
- 47 le Fouisseur battu : le coffre de la Cape de Roc ;
- 48 le premier vol ; 4b la Cape puis le Grappin-Écho ; 4c la Cape et le mur à bombarder ;
- 4d la Cape jusqu'à l'îlot, Marine et la bombe : la clé du boss ; 4f de pilier en pilier ;
- 50 deux torches sur deux îlots (la Cape, la Lanterne) ; 51 le double saut ; 52 l'embuscade ;
  53 le gouffre de trois colonnes ; l'Ombre de Marine ; l'essence ; la fin du chapitre 6.

Seule triche : les ennemis, le mini-boss et le boss sont retirés (leur vie mise à zéro), et Link
garde sa vie pleine.

Usage : python tools/test_spirale.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import (BOSS_KEYS, ESSENCES, HEALTH, INV_A, INV_B, MAX_HEALTH, TEXT_ACTIVE,
                        Game, sheet)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_CANE, TREASURE_BOOMERANG, TREASURE_SWITCH_HOOK, TREASURE_FEATHER = 0x04, 0x06, 0x0a, 0x17
TREASURE_BOMBS, TREASURE_HARP = 0x03, 0x11
TORCHES = 0xcc8f            # wNumTorchesLit
FEATHER_LEVEL = 0xc6f8      # wFeatherLevel
GLOBALFLAG_BALLADE_ISLAND7 = 0x56
INTERAC_ESSENCE = 0x7f
DISABLED_OBJECTS = 0xcc8a  # wDisabledObjects
# Le carrelage bleu de 4:42 : un chemin qui passe une fois par chaque case (spirale_gen, hamilton)
TILE_PATH = [(8, 6), (7, 6), (6, 6), (5, 6), (4, 6), (3, 6), (2, 6), (2, 5), (3, 5), (4, 5), (5, 5),
             (6, 5), (6, 4), (5, 4), (5, 3), (4, 3), (3, 3), (3, 4), (2, 4), (2, 3), (2, 2), (3, 2),
             (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (8, 3), (7, 3), (7, 4), (8, 4), (8, 5)]
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe(), 'clés', g.small_keys(6))
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def wait_intro():
    """La présentation d'un boss gèle Link (wDisabledObjects) : la laisser finir, textes compris
    (tué pendant sa présentation, le boss laisserait Link gelé)."""
    for _ in range(60):
        g.text_through()
        g.w(10)
        if not g.m[DISABLED_OBJECTS] and not g.m[TEXT_ACTIVE]:
            return True
    return False


def full_life():
    g.m[HEALTH] = g.m[MAX_HEALTH]


def at(row, col, tol=8):
    y, x = g.link()
    return abs(y - (row * 16 + 8)) <= tol and abs(x - (col * 16 + 8)) <= tol


def jump(row, col, direction, double=False, back=0, run=2):
    """Depuis (row, col), sauter vers direction (Plume de Roc ; double : la Cape). back : reculer pour
    prendre de l'élan ; run : images de course avant le saut. On lâche la direction à l'atterrissage
    (sinon Link continue de marcher, vers le trou suivant)."""
    g.stand(row, col)
    g.m[INV_B] = TREASURE_FEATHER
    if back:
        g.hold({'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}[direction], back)
    g.pb.button_press(direction)
    g.w(run + back)
    g.pb.button('b', 3)
    g.w(3)
    if double:
        g.w(19)          # le second appui de la Cape : ~20 images après le premier (avant, il ne compte pas)
        g.pb.button('b', 3)
        g.w(3)
    for i in range(70):
        g.w(1)
        if i > (30 if double else 4) and g.m[0xd00f] == 0:      # w1Link.zh : de retour au sol
            break
    g.pb.button_release(direction)
    g.w(20)


def use(item, facing, wait=60):
    g.m[INV_B] = item
    g.face(facing)
    g.press('b', 10)
    g.w(wait)


def hook(facing):
    use(TREASURE_SWITCH_HOOK, facing, 120)   # le diamant reprend sa place ~70 images après


def chest_up(row, col):
    """Le coffre (row, col), Link juste en dessous : on l'ouvre."""
    g.hold('up', 10)
    g.press('a', 60)
    g.text_through(10)
    g.w(40)
    return g.tile(row * 16 + col) == 0xf0


def bomb(facing, away):
    """Une bombe posée devant Link, puis s'éloigner jusqu'à la case away et attendre l'explosion."""
    g.m[INV_B] = TREASURE_BOMBS
    g.face(facing)
    g.tap('b', 30)              # au-dessus de la tête
    g.tap('b', 10)              # posée
    g.route(away)
    g.w(150)


def marine_bomb(facing, wait=250):
    """Une bombe au-dessus de la tête, Select : Marine l'emporte cinq cases plus loin."""
    g.m[INV_B] = TREASURE_BOMBS
    g.face(facing)
    g.tap('b', 30)
    g.press('select', 10)
    g.w(wait)


def lantern(facing):
    use(TREASURE_HARP, facing, 90)


def key_door(direction, room):
    g.hold(direction, 40)
    g.w(40)
    return g.go(direction, room)


def clear():
    g.clear_enemies()
    full_life()


# --- L'entrée
g.level(6, 'Donjon')
g.m[INV_A], g.m[INV_B] = 0x05, TREASURE_FEATHER
full_life()
check(g.where() == (4, 0x3c), "l'entrée de la Spirale Céleste (4:3c)")
check(g.wait_text(200), 'le nom du donjon')
g.w(30)
shoot('s01_entree', "L'entrée")
for _ in range(4):
    if not g.m[TEXT_ACTIVE]:
        break
    g.press('a', 20)
check(g.wait_text(120), 'Marine : ne regarde pas en bas')
g.text_through()
g.route((7, 7), (5, 7), (5, 1))
check(g.go('left', (4, 0x3d)), 'le premier saut (4:3d)')

# --- 3d : la Plume de Roc, sans danger
clear()
jump(5, 8, 'left')
check(g.link()[1] < 7 * 16, 'la tranchée sautée')
g.route((5, 1))
check(g.go('left', (4, 0x3e)), "le bouton de l'îlot (4:3e)")

# --- 3e : un saut, un bloc de la Canne sur le bouton, le volet de l'ouest
check(g.tile(0x50) == 0x7b, "le volet de l'ouest fermé")
jump(5, 10, 'left')
g.stand(5, 6)
use(TREASURE_CANE, 'right', 40)
check(g.tile(0x50) != 0x7b, "un bloc de la Canne sur le bouton : le volet s'ouvre")
shoot('s02_bouton', "Le bouton de l'îlot : un bloc de la Canne")
jump(5, 6, 'left')
g.route((5, 1))
check(g.go('left', (4, 0x3f)), "l'îlot de la petite clé 1 (4:3f)")

# --- 3f : trois cases de gouffre : le Grappin-Écho
g.stand(5, 12)
hook('left')
check(at(5, 7), "le Grappin-Écho : sur l'îlot")
check(chest_up(4, 7), 'le coffre de la petite clé 1')
check(g.small_keys(6) == 1, 'la petite clé 1 (%d)' % g.small_keys(6))
shoot('s03_ilot', "L'îlot : le Grappin-Écho")
hook('left')
check(at(5, 2), 'le Grappin-Écho : la rive ouest')
g.route((5, 1))
check(g.go('left', (4, 0x40)), 'le coin sud-ouest (4:40)')
# --- 40 : le cristal de la rive nord, le Boomerang : le pont se pose case par case
check(g.tile(0x27) == 0xf4, 'pas encore de pont')
g.stand(5, 3)
use(TREASURE_BOOMERANG, 'up', 30)
g.w(10)
shoot('s04a_pont', 'Le pont du cristal se pose')
g.w(40)
check(all(g.tile(p) == 0xa0 for p in (0x47, 0x37, 0x27)), 'le cristal au Boomerang : le pont (colonne 7)')
g.route((5, 7), (1, 7))
check(key_door('up', (4, 0x41)), 'la porte à clé : 4:41')

# --- 41 : le mur fissuré, la salle secrète
clear()
check(g.tile(0x5e) == 0x31, "le mur fissuré de l'est")
g.route((5, 13))
bomb('right', (5, 9))
check(g.tile(0x5e) != 0x31, 'une bombe : le mur saute')
r0 = g.rupees()
g.route((5, 13))
check(g.go('right', (4, 0x49)), 'la salle secrète (4:49)')
g.text_through()
g.route((5, 2), (6, 2), (6, 7))
check(chest_up(5, 7), 'le coffre de la salle secrète')
check(g.rupees() >= r0 + 100, 'cent rubis (%d -> %d)' % (r0, g.rupees()))
shoot('s04b_secrete', 'La salle secrète')
g.route((6, 2), (5, 2), (5, 1))
check(g.go('left', (4, 0x41)), 'retour à 4:41')
g.route((5, 7), (1, 7))
check(g.go('up', (4, 0x42)), 'le carrelage bleu (4:42)')

# --- 42 : tout peindre d'un seul trait
g.route((8, 7))
for (y, x) in TILE_PATH:
    cy, cx = g.link()
    if x * 16 + 8 != cx:
        g.goto(None, x * 16 + 8)
    if y * 16 + 8 != cy:
        g.goto(y * 16 + 8, None)
g.w(60)
shoot('s04_carrelage', 'Le carrelage peint : la carte')
check(g.tile(0x5a) == 0xf1, 'tout est peint : le coffre de la carte apparaît')
g.route((8, 7), (6, 7), (6, 10))
check(chest_up(5, 10), 'le coffre de la carte')
g.route((6, 7), (1, 7))
check(g.go('up', (4, 0x43)), 'le cristal (4:43)')

# --- 43 : la boussole, le cristal au Boomerang
clear()
g.w(120)
g.stand(9, 5)
check(chest_up(8, 5), 'le coffre de la boussole (les chauves-souris battues)')
check(g.tile(0x07) == 0x78, 'le volet du nord fermé')
g.stand(5, 7)
use(TREASURE_BOOMERANG, 'right', 90)
check(g.tile(0x07) != 0x78, "le cristal au Boomerang-Toupie : le volet s'ouvre")
shoot('s05_cristal', 'Le cristal au Boomerang-Toupie')
g.route((1, 7))
check(g.go('up', (4, 0x44)), 'le cristal emmuré (4:44)')

# --- 44 : le cristal emmuré : Marine porte la bombe par-dessus les statues
check(g.wait_text(120), 'Marine : moi, je vole')
g.text_through()
check(g.tile(0x5e) == 0x79, "le volet de l'est fermé")
g.route((9, 7), (9, 2), (5, 2))
marine_bomb('right', 30)
shoot('s05b_marine', 'Marine porte la bombe par-dessus les statues')
g.w(220)
check(g.tile(0x5e) != 0x79, "la bombe sur le cristal emmuré : le volet de l'est s'ouvre")
g.route((9, 2), (9, 12), (5, 12), (5, 13))
check(g.go('right', (4, 0x45)), 'les deux ponts (4:45)')

# --- 45 : les deux ponts
WEST, EAST = (0x53, 0x54, 0x55), (0x59, 0x5a, 0x5b, 0x5c)
check(all(g.tile(p) == 0xa0 for p in WEST) and all(g.tile(p) == 0xf4 for p in EAST),
      "le pont de l'ouest posé, pas celui de l'est")
g.route((5, 2), (5, 7), (4, 7))
use(TREASURE_BOOMERANG, 'up', 30)
g.w(10)
shoot('s05c_ponts', 'Un pont se replie, l\'autre se déploie')
g.w(60)
check(all(g.tile(p) == 0xf4 for p in WEST) and all(g.tile(p) == 0xa0 for p in EAST),
      "le cristal depuis l'îlot : un pont se replie, l'autre se déploie")
g.route((5, 7), (5, 13))
check(g.go('right', (4, 0x46)), 'la petite clé 2 (4:46)')

# --- 46 : le Grappin-Écho, puis un saut ; retour par deux sauts
g.route((6, 1), (6, 3))
hook('up')
check(at(2, 3), "le Grappin-Écho : l'îlot du diamant")
jump(2, 3, 'right')
g.stand(2, 5)
check(chest_up(1, 5), 'le coffre de la petite clé 2')
check(g.small_keys(6) == 1, 'la petite clé 2 (%d)' % g.small_keys(6))
shoot('s06_cle2', 'Le Grappin-Écho, puis un saut')
jump(2, 5, 'left')
check(g.where() == (4, 0x46) and g.link()[0] < 0x30 and g.link()[1] < 0x40, "le retour : la corniche")
g.route((2, 1), (5, 1), (7, 1), (7, 13), (5, 13))   # le diamant est resté en (6,3)
check(g.go('right', (4, 0x47)), 'le Fouisseur (4:47)')

# --- 47 : le Fouisseur ; battu, le coffre de la Cape de Roc
check(wait_intro(), 'le Fouisseur se présente')
shoot('s07_fouisseur', 'Le Fouisseur')
check(g.tile(0x50) == 0x7b and g.tile(0x5e) == 0x79, 'les volets fermés')
g.clear_enemies()
g.w(240)
full_life()
check(g.tile(0x5e) != 0x79, 'le Fouisseur battu : les volets ouverts')
check(g.tile(0x37) == 0xf1, 'le coffre de la Cape apparaît')
g.route((5, 7), (4, 7))
check(chest_up(3, 7), 'le coffre de la Cape de Roc')
check(g.m[FEATHER_LEVEL] == 2, 'la Cape de Roc (plume niveau %d)' % g.m[FEATHER_LEVEL])
shoot('s08_cape', 'Le Fouisseur battu : la Cape de Roc')
g.route((5, 7), (5, 13))
check(g.go('right', (4, 0x48)), 'le premier vol (4:48)')

# --- 48 : le premier vol, sans danger
g.route((5, 7))
jump(5, 7, 'down', double=True, back=6)
check(g.where() == (4, 0x48) and g.link()[0] > 0x88, 'la Cape : trois lignes de gouffre')
g.route((9, 7))
check(key_door('down', (4, 0x4b)), 'la porte à clé (petite clé 2) : 4:4b')

# --- 4b : la Cape jusqu'à l'îlot, puis le Grappin-Écho
clear()
g.route((1, 7), (1, 3))
jump(1, 3, 'down', double=True, run=14)   # (de l'élan : au bord du trou, la Plume ne part plus)
check(g.where() == (4, 0x4b) and at(6, 3, 12), "la Cape : l'îlot")
g.stand(6, 5)
hook('right')
check(at(6, 10), "le Grappin-Écho : la rive est")
shoot('s09_grappin', 'La Cape, puis le Grappin-Écho')
g.route((6, 13), (9, 13), (9, 7))
check(g.go('down', (4, 0x4c)), 'le mur à bombarder (4:4c)')

# --- 4c : la Cape, une bombe contre le mur fissuré
g.route((4, 7))
jump(4, 7, 'down', double=True, run=12)
check(g.where() == (4, 0x4c) and g.link()[0] > 0x88, 'la Cape : la rive du bas')
check(g.tile(0xa7) == 0x32, 'le mur fissuré du sud')
g.stand(9, 7)
bomb('down', (9, 3))
check(g.tile(0xa7) != 0x32, 'une bombe : le passage vers 4d')
g.route((9, 7))
check(g.go('down', (4, 0x4d)), 'le cristal du vide (4:4d)')

# --- 4d : la Cape jusqu'à l'îlot ; de là, Marine porte la bombe
g.route((1, 7), (1, 5))
jump(1, 5, 'down', double=True, run=14)
check(g.where() == (4, 0x4d) and at(6, 5, 12), "la Cape : l'îlot")
g.stand(7, 6)
marine_bomb('right', 30)
shoot('s10_vide', 'Depuis l\'îlot, Marine porte la bombe')
g.w(220)
check(g.tile(0x65) == 0xf1, "le cristal du vide : le coffre de la clé du boss apparaît sur l'îlot")
g.stand(7, 5)
check(chest_up(6, 5), 'le coffre de la clé du boss')
check(g.m[BOSS_KEYS] & 0x40, 'la clé du boss')
jump(7, 5, 'left', double=True, back=6)
check(g.where() == (4, 0x4d) and g.link()[1] < 0x20, 'la Cape : la rive ouest')
g.route((5, 1))
check(g.go('left', (4, 0x4e)), '4:4e')
clear()
g.route((5, 7), (1, 7))
check(g.go('up', (4, 0x4f)), 'les piliers (4:4f)')

# --- 4f : de pilier en pilier
clear()
jump(9, 7, 'up', double=True, back=6)
check(g.where() == (4, 0x4f) and g.link()[0] < 0x60, 'la Cape : le pilier')
g.stand(5, 7)
jump(5, 7, 'left', double=True)
check(g.where() == (4, 0x4f) and g.link()[1] < 0x40, "la Cape : la rive de l'ouest")
g.route((5, 1))
check(g.go('left', (4, 0x50)), 'le cœur de la spirale (4:50)')

# --- 50 : deux torches sur deux îlots
check(g.tile(0x50) == 0x7b, "le volet de l'ouest fermé")
g.route((4, 13))
jump(4, 13, 'left', double=True)
check(at(4, 9, 12), "la Cape : l'îlot de l'est")
g.stand(4, 9)
lantern('down')
check(g.m[TORCHES] == 1, 'la Lanterne : une torche (%d)' % g.m[TORCHES])
jump(4, 8, 'left')
check(at(4, 6, 12), "la Plume : l'îlot de l'ouest")
g.stand(4, 5)
lantern('down')
g.w(60)
check(g.m[TORCHES] == 2 and g.tile(0x50) != 0x7b, "les deux torches : le volet de l'ouest s'ouvre")
shoot('s11_torches', 'Le cœur : les deux torches')
jump(4, 5, 'left', double=True)
check(g.link()[1] < 0x20, "la Cape : l'anneau")
g.route((5, 1))
check(g.go('left', (4, 0x51)), 'le gouffre de trois lignes (4:51)')
jump(5, 7, 'up', double=True, back=6)
check(g.link()[0] < 0x20, 'la Cape : le double saut')
g.route((1, 7))
check(g.go('up', (4, 0x52)), "l'embuscade (4:52)")

# --- 52 : l'embuscade (les portes se ferment quand Link s'en écarte)
g.route((7, 7))
g.w(60)
check(g.tile(0xa7) == 0x7a or g.tile(0x5e) == 0x79, 'les portes se ferment')
shoot('s12_embuscade', "L'embuscade")
g.clear_enemies()
g.w(120)
full_life()
check(g.tile(0x5e) != 0x79, "les ennemis battus : la porte de l'est s'ouvre")
g.route((8, 7), (8, 13), (5, 13))
check(g.go('right', (4, 0x53)), 'le gouffre de trois cases (4:53)')
jump(5, 4, 'right', double=True, back=6)
check(g.link()[1] > 0x80, 'la Cape : le gouffre de trois cases')
g.route((5, 13))
check(key_door('right', (4, 0x54)), "la porte du boss : l'Ombre de Marine (4:54)")

# --- 54 : l'Ombre de Marine
check(g.wait_text(200), "l'Ombre parle, Marine répond")
g.w(40)
shoot('s10_ombre', "L'Ombre de Marine")
check(wait_intro(), "l'Ombre se présente")
g.w(30)
shoot('s11_combat', "L'Ombre de Marine (le combat)")
g.clear_enemies()
g.w(300)
full_life()
g.route((6, 7))
g.w(60)
g.text_through()
g.w(120)
check(any(g.m[h * 256 + 0x40] and g.m[h * 256 + 0x41] == INTERAC_ESSENCE for h in range(0xd2, 0xe0)),
      "l'essence apparaît")
shoot('s12_essence', "L'essence")
for _ in range(8):
    if g.where() != (4, 0x54):
        break
    g.route((5, 7), (4, 7))
    g.hold('up', 40)
    g.w(30)
    if g.m[TEXT_ACTIVE] and g.where() == (4, 0x54) and not any('couplet' in l for _, l in shots):
        shoot('s13_couplet', 'Le sixième couplet')
    g.text_through()
    g.press('a', 30)
g.w(200)
g.settled()
check(bool(g.m[ESSENCES] & 0x20), "l'essence (le sixième couplet)")
check(g.where() == (1, 0x67), 'retour au village des plumes (1:67)')
check(g.wait_text(400), 'la fin du chapitre 6 : le vent revient')
g.w(40)
shoot('s14_vent', 'Le vent revient')
for _ in range(10):
    g.text_through()
    g.w(120)
check(g.global_flag(GLOBALFLAG_BALLADE_ISLAND7), "l'île du Grand Sommeil repérée")

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
