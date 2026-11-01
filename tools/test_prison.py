"""Test de la Tour Sans-Nuit, Link prisonnier (idée de Denis, 01/11/2026 ; code/ages/balladePrison.s),
depuis le menu de test caché (8. Plage) :
- la porte de la tour : Marine chante les sept couplets ; passé l'arche, BONK : Link tombe, Marine
  crie son nom, écran noir ; il se réveille au cachot (5:a0), sans aucun objet ;
- le bloc de la cellule se pousse ; B1 le couloir : un garde le voit, retour au cachot ; le coffre
  du bouclier, l'escalier ;
- 1F l'entrée : la herse sous l'arche, le coffre des graines ; la Lune qui tombe ;
- 2F le coffre du Boomerang, des bombes et de la Cape ; pris par un garde : le passage du cachot
  ramène à l'arrivée du 2F ; la lave, le coffre de la Canne...
- 3F, 4F : les coffres, l'épée en dernier ;
- 5F Dark Link, Marine en cage : battu, la cage s'ouvre, la 8e essence (Link reste dans la tour) ;
- 6F l'Insomnis (son test : tools/test_rythme.py ; ici son étape mise à 3), la porte de Ganon ;
  Ganon sans l'Épée de Légende : Marine casse le 4e mur (Sauvegarder et Quitter : le retour à
  l'entrée) ; l'escalier direct de l'entrée au 6F ; avec l'Épée de Légende, Ganon tombe.

Triches : les gardes retirés une fois qu'on a vu qu'ils attrapent, les ennemis des cauchemars
retirés (leur vie mise à zéro), la vie de Link pleine.

Usage : python tools/test_prison.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import HEALTH, INV_A, INV_B, MAX_HEALTH, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_CANE, TREASURE_SWITCH_HOOK, TREASURE_FLUTE, TREASURE_SHOOTER, TREASURE_FEATHER = 0x04, 0x0a, 0x0e, 0x0f, 0x17
ITEM_SHIELD, ITEM_SWORD, ITEM_BOOMERANG = 0x01, 0x05, 0x06
DISABLED_OBJECTS = 0xcc8a
GROUP5_FLAGS = 0xca00          # wGroup5RoomFlags
INVENTORY = 0xc688             # wInventoryB, wInventoryA, wInventoryStorage (16)
BACKUP = GROUP5_FLAGS + 0xd7   # PRISON_BACKUP
CHECKPOINT = GROUP5_FLAGS + 0xa9
RESPAWN = 0xc62b               # wDeathRespawnBuffer
SWORD_LEVEL = 0xc6b2
RHYTHM_STAGE = 0xcdec          # wBalladeRhythmStage
FLAG_PRISON, FLAG_ASSOMME = 0x6a, 0x6b
AMBI_GUARD, LINK_MIMIC = 0x54, 0x64
errors, shots = [], []
g = Game()


def save(name):
    """Un état PyBoy (pour reprendre un essai : tools/test_prison.py n'en relit pas)."""
    with open(os.path.join(OUT, name + '.state'), 'wb') as f:
        g.pb.save_state(f)


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))
        if len(errors) >= 4:      # (la suite ne voudrait plus rien dire)
            print('%d problème(s) : %s' % (len(errors), '; '.join(errors)))
            sys.exit(1)


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def full_life():
    g.m[HEALTH] = g.m[MAX_HEALTH]


def items():
    return [g.m[INVENTORY + i] for i in range(18) if g.m[INVENTORY + i]]


def owns(item):
    return item in items()


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


def stairs(row, col, room, side='left'):
    """L'escalier (row, col) : on marche dessus (depuis la case de gauche, ou de droite)."""
    if side == 'left':
        g.stand(row, col - 1)
        g.hold('right', 30)
    else:
        g.stand(row, col + 1)
        g.hold('left', 30)
    g.settled()
    g.w(40)
    return g.where() == room


def remove(b):
    """Retirer un ennemi comme le jeu (tout l'objet à zéro : un ennemi créé ensuite à sa place
    hériterait sinon de son état, et le jeu planterait)."""
    for k in range(0x40):
        g.m[b + k] = 0


def no_guards():
    for b in g.enemies(AMBI_GUARD):
        remove(b)
    g.w(2)


def chest(row, col, label, name, y_first=False):
    """Un coffre des objets confisqués : on l'ouvre (par en dessous), le texte, l'escalier."""
    no_guards()
    g.stand(row + 1, col, y_first)
    g.hold('up', 12)
    g.press('a', 30)
    ok = g.wait_text(200)
    g.w(20)
    shoot(name, label)
    g.text_through()
    g.w(60)
    return ok and g.tile(row * 16 + col) == 0xf0


def nightmare(flag_room):
    wait_intro()
    full_life()
    hit = set()
    for _ in range(40):
        for b in g.enemies():
            if b not in hit and g.m[b + 1] != 0x01:
                g.m[b + 0x29] = 0
                hit.add(b)
        full_life()
        g.text_through()
        g.w(60)
        if g.m[GROUP5_FLAGS + flag_room] & 0x80:
            break
    return bool(g.m[GROUP5_FLAGS + flag_room] & 0x80)


def caught_by_guard():
    """Link se met devant un garde (sans les boîtes, sans bouger) : vu, retour au cachot."""
    guards = g.enemies(AMBI_GUARD)
    if not guards:
        return False
    if not g.wait_text(900):
        return False
    g.w(20)
    shoot('p_vu_%02x' % g.where()[1], 'Vu : « AU CACHOT! »')
    g.text_through()
    ok = g.wait_until(lambda: g.where() == (5, 0xa0), 600)
    g.settled()
    g.w(30)
    return ok


# --- L'île, la porte de la tour (comme tools/test_tour.py)
g.level(8, 'Plage')
g.m[INV_A] = ITEM_SWORD
# (le menu de test ne donne pas le bouclier de bois : dans le jeu, Link l'a depuis le début)
if ITEM_SHIELD not in [g.m[INVENTORY + i] for i in range(18)]:
    g.m[INVENTORY + 2 + [g.m[INVENTORY + 2 + i] for i in range(16)].index(0)] = ITEM_SHIELD
full_life()
check(g.where() == (1, 0xd9), "le ponton de l'Œil de l'Insomnis (1:d9)")
g.wait_text(200)
g.text_through()
g.m[0xc800 + 0xc8] |= 0x40
g.m[0xc700 + 0xca] |= 0x40
g.route((4, 4))
check(g.go('up', (1, 0xc9)), 'le parvis de la tour (1:c9)')
g.route((6, 4))
check(g.wait_text(200), 'Marine : sept marques, sept couplets')
for _ in range(10):
    g.text_through()
    g.w(30)
check(g.tile(0x44) == 0xdf, 'la porte de la tour est ouverte')
before = items()
g.route((5, 4))
g.hold('up', 40)
g.settled()
check(g.where() == (5, 0xc0), "l'entrée de la Tour Sans-Nuit (5:c0)")
for _ in range(6):
    g.text_through()
    g.w(20)

# --- BONK
for _ in range(10):
    g.hold('up', 10)
    if g.m[DISABLED_OBJECTS]:
        break
check(g.m[DISABLED_OBJECTS] and g.link()[0] > 0x60, 'quelques pas : le coup sur la tête')
g.w(40)
shoot('p01_bonk', 'BONK : Link assommé')
check(g.wait_text(300), 'Marine crie : « Link?! Link! ... Liiiink!!! »')
g.w(90)
shoot('p02_cris', 'Marine emportée crie son nom')
g.text_through()
check(g.wait_until(lambda: g.where() == (5, 0xa0), 600), 'écran noir : le cachot (5:a0)')
check(g.global_flag(FLAG_PRISON) and g.global_flag(FLAG_ASSOMME), 'Link prisonnier (les drapeaux)')
check(items() == [], 'plus rien : ses objets confisqués (%s)' % items())
check(sorted(g.m[BACKUP + i] for i in range(18) if g.m[BACKUP + i]) == sorted(before),
      'ses objets gardés dans la sauvegarde (%d)' % len(before))
check(g.wait_text(400), "le réveil : « Aïe... Ta tête! »")
g.w(20)
shoot('p03_cachot', 'Le réveil au cachot, sans rien')
g.text_through()
check(at(2, 2), 'dans la cellule')
check(bytes(g.m[RESPAWN + i] for i in range(2)) == b'\x05\xa0', 'le point de retour : le cachot')

# La cellule : la statue du mur (2,4) se pousse, deux fois
def out_of_cell():
    g.wait_no_text()
    g.w(30)
    g.stand(2, 3)
    g.hold('right', 120)
    g.w(20)
    ok = g.tile(0x24) == 0xa0 and g.tile(0x25) == 0xa0 and g.link()[1] >= 0x50
    g.route((2, 5), (5, 5), (5, 13))
    return ok


check(out_of_cell(), 'la statue de la cellule poussée : dehors')
check(g.go('right', (5, 0xa1)), 'B1 : le couloir (5:a1)')

# Un garde voit Link : retour au cachot
g.w(30)
guards = g.enemies(AMBI_GUARD)
check(len(guards) == 1, 'un garde dans le couloir (%d)' % len(guards))
check(all(g.m[b + 0x1b] & 7 == 6 for b in guards), 'en fantôme (la palette 6)')
shoot('p04_garde', 'B1 : un garde')
g.stand(5, 9)
check(caught_by_guard(), 'vu par le garde : « Hé! Le prisonnier! AU CACHOT! », le cachot')
g.text_through()
check(g.m[CHECKPOINT] == 0, 'pris au sous-sol : pas de passage (%d)' % g.m[CHECKPOINT])
g.w(60)
out_of_cell()                  # (la salle est revenue : la statue aussi)
check(g.go('right', (5, 0xa1)), 'de nouveau le couloir')
check(chest(2, 11, 'B1 : le bouclier', 'p05_bouclier'), 'le coffre du bouclier')
check(owns(ITEM_SHIELD) and len(items()) == 1, 'le bouclier rendu, seul (%s)' % items())
check(g.tile(0x8b) == 0x45, "l'escalier")
check(stairs(8, 11, (5, 0xc0)), "l'escalier : 1F, l'entrée (5:c0)")

# --- 1F
g.w(30)
check(g.tile(0x97) == 0x1d, "la herse sous l'arche")
check(chest(1, 12, '1F : les graines', 'p06_graines'), 'le coffre des graines')
check(owns(TREASURE_SHOOTER), 'le Lance-Graines rendu')
g.route((5, 12), (5, 7), (5, 1))
check(g.go('left', (5, 0xc1)), '1F : la Lune qui tombe (5:c1)')
g.text_through()
g.route((5, 12), (4, 12), (4, 7), (5, 7))
g.m[INV_B] = TREASURE_SHOOTER
for facing in ('up', 'right', 'down', 'left'):
    g.face(facing)
    g.press('b', 4)
    g.w(14)
g.w(40)
for _ in range(12):
    g.text_through()
    g.w(20)
check(g.tile(0x87) == 0x45, "les quatre feux : le Sablier, l'escalier")
check(stairs(8, 7, (5, 0xc2)), "l'escalier : 2F (5:c2)")

# --- 2F : pris, le passage du cachot ramène ici
g.w(30)
check(len(g.enemies(AMBI_GUARD)) == 2, 'deux gardes au 2F')
g.stand(5, 7)
check(caught_by_guard(), 'vu au 2F : le cachot')
g.text_through()
check(g.m[CHECKPOINT] == 2, "l'étage retenu : 2F (%d)" % g.m[CHECKPOINT])
g.w(60)
check(g.tile(0x11) == 0x17, 'le passage au fond de la cellule')
shoot('p07_passage', 'Le passage de la cellule')
g.stand(1, 1)
g.w(20)
g.settled()
g.w(30)
check(g.where() == (5, 0xc2) and at(8, 7), "le passage : l'arrivée du 2F")
check(chest(1, 7, '2F : le Boomerang, les bombes, la Cape', 'p08_boomerang'), 'le coffre du Boomerang')
check(owns(ITEM_BOOMERANG) and owns(TREASURE_FEATHER), 'le Boomerang et la Cape rendus')
g.route((5, 7), (5, 13))
save('c2')
check(g.go('right', (5, 0xc3)), '2F : la lave, le cristal (5:c3)')
g.stand(2, 4)
use(TREASURE_SHOOTER, 'right', 60)
check(g.tile(0x5e) != 0x79, "le cristal frappé : le volet de l'est ouvert")
g.route((5, 4), (5, 6))
jump(5, 6, 'right', double=True, back=6)
check(g.link()[1] > 9 * 16, 'la lave sautée (la Cape)')
g.route((5, 13))
check(g.go('right', (5, 0xa2)), '2F : le coffre du bout (5:a2)')
check(chest(2, 11, '2F : la Canne, le Grappin...', 'p09_canne'), 'le coffre de la Canne')
check(owns(TREASURE_CANE) and owns(TREASURE_SWITCH_HOOK), 'la Canne et le Grappin rendus')
check(stairs(8, 11, (5, 0xc5)), "l'escalier : 3F (5:c5)")

# --- 3F
save('c5')
no_guards()
g.route((5, 7), (5, 1))
check(g.go('left', (5, 0xc6)), "3F : le bouton de l'îlot (5:c6)")
g.route((9, 13), (9, 2), (5, 2))
use(TREASURE_SWITCH_HOOK, 'right', 120)
check(at(5, 6), "le Grappin-Écho : sur l'îlot")
use(TREASURE_CANE, 'right', 40)
check(g.tile(0x50) != 0x7b, "un bloc de la Canne sur le bouton : le volet de l'ouest")
use(TREASURE_SWITCH_HOOK, 'left', 120)
g.route((5, 1))
check(g.go('left', (5, 0xa5)), '3F : le coffre du bout (5:a5)')
check(chest(2, 3, '3F : la Clochette, le reste', 'p10_reste'), 'le coffre du reste')
check(owns(TREASURE_FLUTE), "la Clochette d'Aube rendue")
check(not owns(ITEM_SWORD), "pas encore l'épée")
check(stairs(8, 3, (5, 0xc8), side='right'), "l'escalier : 4F (5:c8)")

# --- 4F
g.text_through()
no_guards()
g.route((5, 7), (5, 13))
check(g.go('right', (5, 0xc9)), '4F : la Cape, un garde endormi (5:c9)')
jump(5, 4, 'right', double=True, back=6)
g.stand(5, 11)
g.m[INV_B] = TREASURE_FLUTE
g.press('b', 10)
g.wait_text(400)
g.text_through()
g.w(60)
g.route((5, 13))
check(g.go('right', (5, 0xca)), "4F : l'épée (5:ca)")
check(chest(5, 12, "4F : l'épée", 'p11_epee', y_first=True), "le coffre de l'épée")
check(owns(ITEM_SWORD) and all(not g.m[BACKUP + i] for i in range(18)), 'tout est rendu (%s)' % items())
check(stairs(8, 7, (5, 0xcb)), "l'escalier : 5F (5:cb)")

# --- 5F : Dark Link, Marine en cage
save('cb')
g.route((5, 7), (5, 1))
check(g.go('left', (5, 0xc4)), '5F : Dark Link, Marine en cage (5:c4)')
check(g.wait_text(300), 'Marine : « Link! Je suis là, dans la cage! »')
g.w(20)
shoot('p12_cage', 'Marine en cage encourage Link')
g.text_through()
check(len(g.enemies(LINK_MIMIC)) == 1, 'Dark Link')
check(nightmare(0xc4), 'Dark Link vaincu')
check(g.wait_text(400), 'la cage s\'ouvre : « Tu l\'as eu! »')
g.w(20)
shoot('p13_libre', 'Marine libre')
g.text_through()
check(g.tile(0x37) == 0xa0, 'la cage ouverte')
check(not g.global_flag(FLAG_PRISON), 'Link libre')
check(bytes(g.m[RESPAWN + i] for i in range(2)) == b'\x05\xc0', "le point de retour : l'entrée")
essence = g.wait_until(lambda: any(g.m[(d << 8) + 0x41] == 0x7f for d in range(0xd2, 0xe0) if g.m[(d << 8) + 0x40]), 300)
check(essence, 'la 8e essence apparaît')
g.w(60)
shoot('p14_essence', 'La 8e essence')
g.route((7, 10), (9, 10), (9, 7))       # (sous l'essence, par en dessous : elle tombe vers Link ; pas par l'escalier du milieu)
g.hold('up', 40)
for _ in range(30):
    g.text_through()
    g.w(30)
    if g.where() != (5, 0xc4) or (g.m[0xc6bf] & 0x80 and not g.m[DISABLED_OBJECTS] and not g.m[TEXT_ACTIVE]):
        break
check(g.where() == (5, 0xc4), "l'essence prise : Link reste dans la tour")
check(g.m[0xc6bf] & 0x80, 'la 8e essence (bit 7)')
shoot('p14b_essence_prise', 'Le huitième couplet')
check(g.tile(0x57) == 0x45, "l'escalier")
check(stairs(5, 7, (5, 0xcc)), "l'escalier : 6F, l'Insomnis (5:cc)")

# --- 6F : l'Insomnis, la porte de Ganon
save('cc')
g.w(200)
check(g.tile(0x50) == 0xb3, "la porte de l'ouest murée")
g.m[RHYTHM_STAGE] = 3
g.w(60)
check(g.tile(0x50) == 0xa0, "l'Insomnis battu : la porte de l'ouest")
for _ in range(6):
    g.text_through()
    g.w(20)
full_life()
g.route((5, 7), (5, 1))
check(g.go('left', (5, 0xc7)), '6F : Ganon (5:c7)')
for _ in range(40):
    g.text_through()
    g.w(20)
    if any(g.m[b + 1] == 0x04 and g.m[b + 4] >= 0x07 for b in g.enemies()):
        break
ganon = [b for b in g.enemies() if g.m[b + 1] == 0x04]
check(len(ganon) == 1, 'Ganon est là')
if ganon:
    life = g.m[ganon[0] + 0x29]
    g.m[ganon[0] + 0x29] = life - 8
    g.w(4)
    check(g.wait_text(60), "Marine : « Ton épée... elle pue »")
    for _ in range(4):
        g.w(30)
        shoot('p15_mur', 'Marine casse le 4e mur')
        g.press('a', 20)
    g.text_through()
g.w(60)
check(g.where() == (5, 0xc7), 'pas de sortie : Link reste devant Ganon (Sauvegarder et Quitter)')
check(g.m[GROUP5_FLAGS + 0xc7] & 0x20, 'la tour retient l\'essai (bit 5 de 5:c7)')

# Sauvegarder et Quitter : le retour (wDeathRespawnBuffer) à l'entrée ; l'escalier direct
g.warp(5, 0xc0, 0x97)
g.w(30)
check(g.tile(0x57) == 0x45, "l'entrée : l'escalier direct du 6F")
check(g.tile(0x97) != 0x1d, 'la herse levée')
shoot('p16_raccourci', "L'escalier direct")
check(stairs(5, 7, (5, 0xcc)), "l'escalier : 6F (5:cc)")
check(g.tile(0x50) == 0xa0, "la porte de Ganon reste ouverte")
g.m[SWORD_LEVEL] = 3
g.route((5, 7), (5, 1))
check(g.go('left', (5, 0xc7)), '6F : Ganon, avec l\'Épée de Légende')
# (après l'arrivée de Ganon et ses textes ; ganonGuard efface le bit 5 de 5:c7 en lançant TX_5b17)
chance = False
for _ in range(80):
    if not g.m[GROUP5_FLAGS + 0xc7] & 0x20:
        chance = True
        g.wait_text(60)
        g.w(30)
        shoot('p16b_chance', "Maintenant, tu n'as aucune chance !")
        g.text_through()
        break
    if g.m[TEXT_ACTIVE]:
        g.press('a', 20)
    else:
        g.w(20)
check(chance, "Marine : « Maintenant, tu n'as aucune chance ! »")
check(nightmare(0xc7), "Ganon vaincu")
shoot('p17_fin', 'Ganon vaincu : la fin')

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
