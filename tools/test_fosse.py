"""Test de la Fosse de Bulle (la plongée, idée de Denis), en vue de côté comme les salles sous l'eau
de Link's Awakening DX, et de l'Épée de Légende :
- Bulle (3:24) : la planche de surf, puis « On plonge ? » ; tant que le quart de cœur de 3 m est là,
  Marine le signale (TX_5be5) -> la Fosse (5:d0 = 1 m), les cœurs pleins ;
- sous l'eau, les cœurs se vident (le souffle) ; la barre d'état montre la profondeur (« 1m »...) ;
- on remonte par la surface de 1 m ;
- avec trois couplets (après le Récif), on descend jusqu'à 3 m : les rubis de 2 m, le quart de cœur
  de 3 m (il scintille) ; plus bas, « l'eau est noire » (TX_5ae7) : pas de passage ; à bout de
  souffle, Bulle tire sur la corde ; le contre parfait ;
- avec sept couplets, on descend jusqu'au fond (7 m) : l'Épée de Légende, puis Bulle remonte Link.
Usage : python tools/test_fosse.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import ESSENCES, HEALTH, INV_A, MAX_HEALTH, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SWORD_LEVEL = 0xc6b2
TEXT_INDEX = 0xcba2           # wTextIndex (l'octet bas du numéro du texte)
DISABLE_TRANSITIONS = 0xcc91  # wDisableScreenTransitions
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


def swim(direction, n):
    g.pb.button_press(direction)
    g.w(n)
    g.pb.button_release(direction)
    g.w(2)


def swim_to(row, col, limit=80):
    """Nager jusqu'au centre d'une case (en x, puis en y ; à quelques pixels près : Link glisse)."""
    y, x = row * 16 + 8, col * 16 + 8
    for axis, target, minus, plus in (('x', x, 'left', 'right'), ('y', y, 'up', 'down')):
        for _ in range(limit):
            ly, lx = g.link()
            cur = lx if axis == 'x' else ly
            if abs(cur - target) <= 3:
                break
            swim(minus if cur > target else plus, 4 if abs(cur - target) > 10 else 1)


def down_to(room, limit=40):
    """Nager vers le bas jusqu'à la salle suivante."""
    for _ in range(limit):
        swim('down', 6)
        if g.where() == (5, room):
            break
    g.w(30)
    return g.where() == (5, room)


# Le chemin de chaque salle (ligne, colonne ; story/salles/fosse.txt), jusqu'au passage du bas
ROUTE = {0xd0: [(1, 12), (9, 12)],
         0xd1: [(1, 12), (1, 3), (6, 3), (6, 12), (8, 12), (9, 2)],
         0xd2: [(1, 2), (1, 11), (6, 11), (6, 12), (9, 12)],
         0xd3: [(1, 12), (7, 12), (7, 7)],
         0xd4: [(1, 7), (3, 7), (3, 12), (8, 12), (8, 2)],
         0xd5: [(1, 2), (7, 2), (7, 12)],
         0xd6: [(1, 12), (8, 12), (9, 9)]}


def cross(room):
    for cell in ROUTE[room]:
        swim_to(*cell)
        if g.where() != (5, room):
            return False
    return True


def bulle():
    """Parler à Bulle (3:24) jusqu'à « On plonge ? » ; renvoie l'octet bas du numéro du texte."""
    g.stand(5, 3)
    g.face('up')
    g.press('a', 20)
    index = g.m[TEXT_INDEX]
    for _ in range(40):
        g.w(10)
        if g.options_shown():
            break
        if g.m[TEXT_ACTIVE]:
            g.press('a', 4)
    return index if g.options_shown() else None


def dive(hearts):
    g.m[MAX_HEALTH] = hearts * 4
    g.m[HEALTH] = 4
    g.warp(3, 0x24, 0x53)
    g.w(40)
    g.text_through()
    index = bulle()
    if index is None:
        return None
    g.choose(0, 2)
    g.w(60)
    g.settled()
    g.w(40)
    return index


def surface():
    """Faire défiler les textes jusqu'au retour au club."""
    for _ in range(40):
        g.text_through()
        g.w(30)
        if g.where() == (3, 0x24):
            break
    g.settled()
    g.w(20)
    return g.where() == (3, 0x24)


g.level(3, 'Fin')
g.m[INV_A] = 0x05
for _ in range(10):
    g.text_through()
    g.w(20)
check(bin(g.m[ESSENCES]).count('1') == 3, 'après le Récif : trois couplets')
# (la planche de surf d'abord : la 1re fois, Bulle la donne)
g.warp(3, 0x24, 0x53)
g.w(40)
g.text_through()
g.stand(5, 3)
g.face('up')
g.press('a', 20)
for _ in range(10):
    g.text_through()
    g.w(30)

# --- La surface de 1 m ---
check(dive(8) == 0xe5, 'Bulle propose la plongée ; Marine signale le quart de cœur (TX_5be5)')
check(g.where() == (5, 0xd0), 'la Fosse : 1 m (5:d0)')
check(g.m[HEALTH] == 32, 'on part le souffle plein (8 cœurs)')
shoot('f01_1m', 'La Fosse, vue de côté : 1 m')
h0 = g.m[HEALTH]
g.w(120)
check(g.m[HEALTH] < h0, "sous l'eau, les cœurs se vident (%d -> %d quarts)" % (h0, g.m[HEALTH]))
swim_to(1, 7)
for _ in range(20):
    swim('up', 6)
    if g.where() != (5, 0xd0):
        break
check(surface(), 'par la surface de 1 m, on remonte au club')
check(g.m[DISABLE_TRANSITIONS] == 0, "au club, les transitions d'écran marchent")

# --- Trois couplets : jusqu'à 3 m ---
check(dive(8) == 0xe5, 'on replonge')
check(cross(0xd0) and down_to(0xd1), '1 m -> 2 m (on nage vers le bas)')
shoot('f02_2m', '2 m : les rubis flottent')
rupees = g.rupees()
for cell in ((1, 12), (1, 3), (6, 3), (6, 13)):
    swim_to(*cell)
g.w(30)
g.text_through()
check(g.rupees() > rupees, 'les rubis de 2 m (%d -> %d)' % (rupees, g.rupees()))
swim_to(8, 12)
swim_to(9, 2)
check(down_to(0xd2), '2 m -> 3 m')
check(g.global_flag(0x62), 'à 3 m, Link a trouvé le calme (le contre parfait sera appris)')
swim_to(1, 2)
swim_to(1, 11)
swim_to(6, 11)
swim_to(6, 3)
swim_to(6, 2)
g.w(12)
shoot('f03_3m', '3 m : le quart de cœur scintille dans son trou')
swim_to(8, 2)
for _ in range(60):
    g.w(5)
    if g.m[TEXT_ACTIVE]:
        break
shoot('f04_quart', 'Le quart de cœur')
check(g.m[TEXT_ACTIVE] != 0, 'le quart de cœur : son texte')
g.text_through()
check(g.room_flags(5, 0xd2) & 0x20, 'le quart de cœur est pris (drapeau $20 de 5:d2)')
# Plus bas que 3 m : l'eau est noire
swim_to(6, 2)
swim_to(6, 12)
for _ in range(30):
    swim('down', 6)
    if g.m[TEXT_ACTIVE]:
        break
g.w(60)
# (wTextIndex n'est pas fiable pendant l'affichage d'un long texte : le souffle n'est pas épuisé,
# c'est donc TX_5ae7 ; la planche le montre)
check(g.m[TEXT_ACTIVE] and g.m[HEALTH] > 2 and g.link()[0] >= 0x90,
      "plus bas que 3 m : « l'eau est noire » (TX_5ae7)")
shoot('f05_noire', 'Trois couplets : pas plus bas que 3 m')
g.text_through()
for _ in range(10):
    swim('down', 6)
check(g.where() == (5, 0xd2), 'pas de passage vers 4 m')
# À bout de souffle
for _ in range(1500):
    g.w(5)
    if g.m[TEXT_ACTIVE]:
        break
g.w(30)     # (le numéro du texte s'écrit quand la boîte s'ouvre)
shoot('f05b_souffle', 'À bout de souffle')
check(g.m[TEXT_ACTIVE] and g.m[HEALTH] <= 2, "à bout de souffle : Bulle tire sur la corde (« Plus d'air ! »)")
check(surface(), 'retour au club (3:24)')
check(g.m[DISABLE_TRANSITIONS] == 0, "les transitions d'écran remarchent")
check(g.wait_text(120) and g.m[TEXT_INDEX] == 0x34, 'Bulle apprend le contre parfait')
g.text_through()
check(g.global_flag(0x61), 'le contre parfait est appris')
check(g.m[HEALTH] == g.m[MAX_HEALTH], 'les cœurs pleins en remontant')
check(bulle() == 0xe1, 'le quart de cœur pris : Bulle seule (TX_5ae1)')
g.choose(1, 2)
g.text_through()

# --- Sept couplets : jusqu'au fond ---
g.m[ESSENCES] = 0x7f
check(dive(15) == 0xe1, 'sept couplets : on replonge')
left = {}
for room in range(0xd0, 0xd6):
    left['%d m' % (room - 0xcf)] = g.m[HEALTH]
    if not (cross(room) and down_to(room + 1)):
        check(False, 'descendre de 5:%02x' % room)
        break
    if room + 1 == 0xd3:
        shoot('f06_4m', '4 m')
    if room + 1 == 0xd5:
        shoot('f07_6m', '6 m')
print('   souffle (quarts) en arrivant à chaque mètre :', left, flush=True)
check(g.where() == (5, 0xd6), 'le fond : 7 m (5:d6)')
swim_to(1, 12)
swim_to(8, 12)
g.w(20)
shoot('f08_7m', "7 m : l'Épée de Légende, plantée dans le sable")
swim_to(9, 9)
for _ in range(60):
    g.w(5)
    if g.m[TEXT_ACTIVE]:
        break
g.w(30)
shoot('f09_epee', "L'Épée de Légende")
check(g.m[SWORD_LEVEL] == 3, "l'Épée de Légende (l'épée niveau 3), il restait %d quarts" % g.m[HEALTH])
check(surface(), 'Bulle remonte Link au club')

sheet(shots, os.path.join(OUT, 'fosse.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
