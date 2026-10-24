"""Test de l'île 8 (l'Œil de l'Insomnis) et de la Tour Sans-Nuit (donjon 8), depuis le menu de test
caché (8. Plage) :
- arrivée au ponton ; la porte de la tour : Marine chante les sept couplets, elle s'ouvre ;
- 1F la Lune qui tombe : quatre torches allumées en même temps (le Lance-Graines, quatre
  directions) : le Sablier, l'escalier ;
- 2F le cristal de l'autre coté de la lave, un saut ; Dark Link (un seul, en duel) ;
- 3F le bouton de l'îlot (le Grappin-Écho, un bloc de la Canne) ; Ganon : sans l'Épée de Légende,
  ses coups ne comptent pas (Marine parle de la Fosse) ; avec elle, il tombe ;
- 4F Ghost Babel (deux fantômes : vu, « LIIINK! », retour à l'escalier) ; la Cape de Roc, un garde
  endormi (la Clochette d'Aube) ; le Cauchemar (l'œil) ;
- 5F l'Insomnis : le boss en rythme commence (il a son propre test, tools/test_rythme.py).

Seule triche : les ennemis des cauchemars sont retirés (leur vie mise à zéro), et Link garde sa
vie pleine.

Usage : python tools/test_tour.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import HEALTH, INV_A, INV_B, MAX_HEALTH, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_CANE, TREASURE_SWITCH_HOOK, TREASURE_FLUTE, TREASURE_SHOOTER, TREASURE_FEATHER = 0x04, 0x0a, 0x0e, 0x0f, 0x17
DISABLED_OBJECTS = 0xcc8a
GROUP5_FLAGS = 0xca00          # wGroup5RoomFlags
SWORD_LEVEL = 0xc6b2
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def full_life():
    g.m[HEALTH] = g.m[MAX_HEALTH]


def at(row, col, tol=8):
    y, x = g.link()
    return abs(y - (row * 16 + 8)) <= tol and abs(x - (col * 16 + 8)) <= tol


def wait_intro():
    for _ in range(60):
        g.text_through()
        g.w(10)
        if not g.m[DISABLED_OBJECTS] and not g.m[TEXT_ACTIVE]:
            return True
    return False


def use(item, facing, wait=40):
    g.m[INV_B] = item
    g.face(facing)
    g.press('b', 10)
    g.w(wait)


def jump(row, col, direction, double=False, back=0, run=2):
    g.stand(row, col)
    g.m[INV_B] = TREASURE_FEATHER
    if back:
        g.hold({'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}[direction], back)
    g.pb.button_press(direction)
    g.w(run + back)
    g.pb.button('b', 3)
    g.w(3)
    if double:
        g.w(19)
        g.pb.button('b', 3)
        g.w(3)
    for i in range(70):
        g.w(1)
        if i > (30 if double else 4) and g.m[0xd00f] == 0:
            break
    g.pb.button_release(direction)
    g.w(20)


def bell():
    g.m[INV_B] = TREASURE_FLUTE
    g.press('b', 10)
    for _ in range(40):
        g.w(10)
        if g.m[TEXT_ACTIVE]:
            return True
    return False


def stairs(row, col, room):
    """L'escalier (row, col) : on marche dessus (depuis la case de gauche)."""
    g.stand(row, col - 1)
    g.hold('right', 30)
    g.settled()
    g.w(40)
    return g.where() == room


def nightmare(room, flag_room):
    """Un cauchemar : sa présentation, puis on le retire ; l'escalier apparaît."""
    wait_intro()
    full_life()
    # (une seule fois : un boss qui meurt, comme Ganon, repasserait sinon par le début de sa mort)
    hit = set()
    for _ in range(40):
        for b in g.enemies():
            if b not in hit and g.m[b + 1] != 0x01:      # (pas les explosions)
                g.m[b + 0x29] = 0
                hit.add(b)
        full_life()
        g.text_through()
        g.w(60)
        if g.m[GROUP5_FLAGS + flag_room] & 0x80:
            break
    g.w(120)
    # (Marine félicite Link après un boss : INTERAC_MARINE $08)
    for _ in range(3):
        g.text_through()
        g.w(40)
    return bool(g.m[GROUP5_FLAGS + flag_room] & 0x80)


# --- L'île : le ponton, la porte de la tour
g.level(8, 'Plage')
g.m[INV_A] = 0x05
full_life()
check(g.where() == (1, 0xd9), "le ponton de l'Œil de l'Insomnis (1:d9)")
check(g.wait_text(200), 'Marine : une tour noire')
g.w(40)
shoot('t01_arrivee', "L'Œil de l'Insomnis")
g.text_through()

# Le Bateau-Rondin à huit îles : trois pages (Brume Grelot Lagune Suite / Braise Échos Nid Suite /
# Sommeil Œil) : vers le Grand Sommeil, et retour
def raft(*options):
    g.stand(6, 4)
    g.face('right')
    g.press('a', 20)
    for opt, count in options:
        g.choose(opt, count)
    g.w(30)
    g.settled()
    g.w(60)
    g.text_through()


raft((3, 4), (3, 4), (0, 2))
check(g.where() == (1, 0xd1), 'le Bateau-Rondin, 3e page : le Grand Sommeil (1:d1)')
raft((3, 4), (3, 4), (1, 2))
check(g.where() == (1, 0xd9), "et retour à l'Œil (1:d9)")
# Le soleil et la lune déjà allumés (les vasques des paupières : tools/test_oeil.py les allume)
g.m[0xc800 + 0xc8] |= 0x40
g.m[0xc700 + 0xca] |= 0x40
g.route((4, 4))
check(g.go('up', (1, 0xc9)), 'le parvis de la tour (1:c9)')
g.route((6, 4))
check(g.wait_text(200), 'Marine : sept marques, sept couplets')
g.w(30)
shoot('t02_porte', 'Marine chante les sept couplets')
for _ in range(10):
    g.text_through()
    g.w(30)
check(g.tile(0x44) == 0xdf, 'la porte de la tour est ouverte')
g.route((5, 4))
g.hold('up', 40)
g.settled()
check(g.where() == (5, 0xc0), "l'entrée de la Tour Sans-Nuit (5:c0)")
check(g.wait_text(200), 'le nom du donjon')
g.w(30)
shoot('t03_entree', "L'entrée : Niveau 8, Tour Sans-Nuit")
for _ in range(6):
    g.text_through()
    g.w(20)

# --- 1F : la Lune qui tombe
g.route((5, 7), (5, 1))
check(g.go('left', (5, 0xc1)), '1F : la Lune qui tombe (5:c1)')
check(g.wait_text(120), 'Marine : la lune tombe')
g.text_through()
g.route((5, 12), (4, 12), (4, 7), (5, 7))     # autour de la torche de l'est (5,9)
g.m[INV_B] = TREASURE_SHOOTER
for facing in ('up', 'right', 'down', 'left'):
    g.face(facing)
    g.press('b', 4)
    g.w(14)
g.w(40)
shoot('t04_lune', 'La Lune qui tombe : les quatre feux')
for _ in range(12):          # Marine, puis le Sablier (tools/test_sablier.py)
    g.text_through()
    g.w(20)
check(g.tile(0x87) == 0x45, "les quatre feux ensemble : le Sablier, l'escalier")
check(stairs(8, 7, (5, 0xc2)), "l'escalier : 2F (5:c2)")

# --- 2F : le cristal de l'autre coté de la lave ; Dark Link
g.route((5, 7), (5, 13))
check(g.go('right', (5, 0xc3)), '2F : la lave, le cristal (5:c3)')
g.stand(2, 4)
use(TREASURE_SHOOTER, 'right', 60)
check(g.tile(0x5e) != 0x79, 'le cristal frappé : le volet de l\'est ouvert')
g.route((5, 4), (5, 6))
jump(5, 6, 'right', double=True, back=6)
check(g.link()[1] > 9 * 16, 'la lave sautée')
g.route((5, 13))
check(g.go('right', (5, 0xc4)), '2F : Dark Link (5:c4)')
g.w(60)
shoot('t05_dark_link', 'Dark Link')
# Un seul, et un vrai duel (balladeDarkLink.s) : Link immobile, il bouge et se fend tout seul
dark = g.enemies(0x64)
check(len(dark) == 1, 'un seul Dark Link (%d)' % len(dark))
if dark:
    wait_intro()                # (Marine parle en entrant : tout est figé)
    full_life()
    moves, lunges, last, pos = 0, 0, None, (g.m[dark[0] + 0x0b], g.m[dark[0] + 0x0d])
    for _ in range(600):
        g.w(1)
        p = (g.m[dark[0] + 0x0b], g.m[dark[0] + 0x0d])
        moves += p != pos
        pos = p
        ph = g.m[dark[0] + 0x31]
        lunges += ph == 2 and last != 2
        last = ph
    full_life()
    check(moves > 100 and lunges >= 2, 'Dark Link se bat seul (%d pas, %d fentes)' % (moves, lunges))
check(nightmare(0xc4, 0xc4), 'Dark Link vaincu')
check(g.tile(0x57) == 0x45, "l'escalier")
check(stairs(5, 7, (5, 0xc5)), "l'escalier : 3F (5:c5)")

# --- 3F : le bouton de l'îlot ; Ganon
g.route((5, 7), (5, 1))
check(g.go('left', (5, 0xc6)), "3F : le bouton de l'îlot (5:c6)")
g.route((9, 13), (9, 2), (5, 2))      # autour du gouffre
use(TREASURE_SWITCH_HOOK, 'right', 120)
check(at(5, 6), "le Grappin-Écho : sur l'îlot")
use(TREASURE_CANE, 'right', 40)
check(g.tile(0x50) != 0x7b, 'un bloc de la Canne sur le bouton : le volet de l\'ouest')
shoot('t06_bouton', "Le bouton de l'îlot")
use(TREASURE_SWITCH_HOOK, 'left', 120)
check(at(5, 2), 'le Grappin-Écho : retour')
g.route((5, 1))
g.go('left', (5, 0xc7))
check(g.where() == (5, 0xf5), '3F : Ganon pose son arène (5:c7 devient 5:f5)')
for _ in range(40):          # Marine, le crâne qui gronde, Ganon apparaît
    g.text_through()
    g.w(20)
    if any(g.m[b + 1] == 0x04 and g.m[b + 4] >= 0x07 for b in g.enemies()):
        break
shoot('t07_ganon', 'Ganon')
# Sans l'Épée de Légende (la Fosse de Bulle, tools/test_fosse.py), ses coups ne comptent pas
ganon = [b for b in g.enemies() if g.m[b + 1] == 0x04]
check(len(ganon) == 1, 'Ganon est là')
if ganon:
    life = g.m[ganon[0] + 0x29]
    g.m[ganon[0] + 0x29] = life - 8
    g.w(4)
    check(g.m[ganon[0] + 0x29] == life, "sans l'Épée de Légende, Ganon ne perd rien (vie %d)" % life)
    check(g.wait_text(60), "Marine : « Bulle parlait d'une épée, au fond de la Fosse... »")
    shoot('t07b_ganon_marine', "Sans l'Épée de Légende")
# Puis « On sort d'ici ? On reviendra avec l'épée ! » : Oui, le parvis de la tour
for _ in range(30):
    if g.where()[0] == 1:
        break
    g.press('a', 15)
g.settled()
check(g.where() == (1, 0xc9), "Marine : « On sort d'ici ? » Oui : le parvis de la tour (1:c9)")
# Revenu avec l'Épée de Légende : « Maintenant, tu n'as aucune chance ! »
g.m[SWORD_LEVEL] = 3          # (l'Épée de Légende)
g.warp(5, 0xc7, 0x5d)
g.settled()
check(g.wait_text(300), "Marine : « Maintenant, tu n'as aucune chance ! »")
shoot('t07c_chance', "Maintenant, tu n'as aucune chance !")
g.text_through()
check(nightmare(0xc7, 0xc7), "avec l'Épée de Légende : Ganon vaincu")
shoot('t08_ganon_fin', 'Ganon vaincu')
check(stairs(5, 7, (5, 0xc8)), "l'escalier : 4F (5:c8)")

# --- 4F : Ghost Babel (deux fantômes font leur ronde) ; la Cape, un garde endormi ; le Cauchemar
check(g.wait_text(200), 'Marine : « Passe dans leur dos... Comme un serpent ! »')
g.text_through()
g.w(30)
ghosts = g.enemies(0x54)
check(len(ghosts) == 2, 'deux fantômes (les Veilleurs)')
check(all(g.m[b + 0x1b] & 7 == 6 for b in ghosts), 'en fantômes (la palette 6, PALH_FANTOME)')
shoot('t08b_fantomes', 'Ghost Babel : les fantômes du 4F')
g.stand(5, 7)                 # au milieu, sous leurs yeux
check(g.wait_text(600), 'vu : « Link? Link?! LIIINK! »')
shoot('t08c_liiink', 'Link? Link?! LIIINK!')
g.text_through()
g.wait_until(lambda: abs(g.link()[0] - 0x88) < 6 and abs(g.link()[1] - 0x78) < 6, 600)
g.settled()
g.w(30)
check(g.where() == (5, 0xc8) and abs(g.link()[0] - 0x88) < 6, "Link se réveille à l'escalier")
for b in g.enemies(0x54):     # (le test ne s'y cache pas : les fantômes retirés)
    g.m[b] = 0
g.route((5, 7), (5, 13))
check(g.go('right', (5, 0xc9)), '4F : la Cape, un garde endormi (5:c9)')
jump(5, 4, 'right', double=True, back=6)
check(g.link()[1] > 7 * 16, 'la Cape : le gouffre de trois cases')
g.stand(5, 11)
check(bell(), 'la Clochette : le garde se réveille')
g.text_through()
g.w(60)
g.route((5, 13))
check(g.go('right', (5, 0xca)), '4F : le Cauchemar (5:ca)')
g.w(60)
shoot('t09_cauchemar', '« Tu me reconnais ? »')
check(nightmare(0xca, 0xca), 'le Cauchemar vaincu')
check(stairs(8, 7, (5, 0xcb)), "l'escalier : 5F (5:cb)")

# --- 5F : l'Insomnis
g.route((5, 7), (5, 1))
check(g.go('left', (5, 0xcc)), "5F : l'Insomnis (5:cc)")
g.w(200)
check(g.m[0xcdec] >= 1, "l'Insomnis : le boss en rythme commence (étape %d)" % g.m[0xcdec])   # wBalladeRhythmStage
shoot('t10_insomnis', "L'Insomnis : le boss en rythme")

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
