"""Test de la Fosse de Bulle (la plongée, idée de Denis) et de l'Épée de Légende :
- Bulle (3:24) : la planche de surf, puis « On plonge ? » -> la Fosse (5:d0), les cœurs pleins ;
- sous l'eau, les cœurs se vident (le souffle) ;
- avec 8 cœurs (avant le donjon 7), on atteint le fond (5:d4), mais l'épée est prise dans le
  sable (il faut neuf cœurs de souffle) ; on remonte à bout de souffle ;
- avec 9 cœurs, on atteint l'Épée de Légende (le niveau 3 de l'épée), puis Bulle remonte Link ;
- Ganon ne craint qu'elle : sans elle sa vie revient et Marine parle de la Fosse.
Usage : python tools/test_fosse.py DOSSIER_CAPTURES [mesure]   (ROM=chemin pour une autre ROM)
« mesure » : le souffle remis à plein à chaque étape, pour mesurer le temps de la descente.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import HEALTH, INV_A, INV_B, MAX_HEALTH, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
MEASURE = len(sys.argv) > 2 and sys.argv[2] == 'mesure'
os.makedirs(OUT, exist_ok=True)
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


frames = [0]


def w(n):
    g.w(n)
    frames[0] += n


def swim_to(row, col, limit=60):
    """Sous l'eau, Link glisse : des coups de nage (4 images appuyé, 3 relâché), x puis y (à
    quelques pixels près : il glisse)."""
    y, x = row * 16 + 8, col * 16 + 8
    for axis, target, minus, plus in (('x', x, 'left', 'right'), ('y', y, 'up', 'down')):
        for _ in range(limit):
            ly, lx = g.link()
            cur = lx if axis == 'x' else ly
            if abs(cur - target) <= 3:
                break
            b = minus if cur > target else plus
            g.pb.button_press(b)
            w(4 if abs(cur - target) > 10 else 1)
            g.pb.button_release(b)
            w(3)
            if MEASURE:
                g.m[HEALTH] = g.m[MAX_HEALTH]


def down_to(room):
    """Nager vers le bas jusqu'à la salle suivante."""
    for _ in range(80):
        g.pb.button_press('down')
        w(4)
        g.pb.button_release('down')
        w(3)
        if g.where() == (5, room):
            break
    w(30)
    return g.where() == (5, room)


ROUTE = {0xd0: [(4, 7), (4, 2), (9, 2)],
         0xd1: [(1, 2), (1, 11), (4, 11), (4, 2), (6, 2), (6, 12), (9, 12)],
         0xd2: [(1, 12), (4, 12), (4, 2), (6, 2), (6, 12), (9, 12), (9, 2)],
         0xd3: [(1, 2), (4, 2), (4, 12), (6, 12), (6, 7), (9, 7)],
         0xd4: [(4, 7)]}


def dive_down(stop_at=None):
    """De 5:d0 à l'épée ; renvoie le nombre d'images depuis le départ à chaque salle."""
    times = {}
    for room in (0xd0, 0xd1, 0xd2, 0xd3, 0xd4):
        if g.where() != (5, room):
            return times
        times[room] = frames[0]
        for cell in ROUTE[room]:
            swim_to(*cell)
            if g.where() != (5, room):
                return times
        if room != 0xd4:
            if not down_to(room + 1):
                return times
    times['epee'] = frames[0]
    return times


def bulle(answer_yes=True):
    """Parler à Bulle (3:24) ; « On plonge ? » : Oui."""
    g.stand(5, 3)
    g.face('up')
    g.press('a', 20)
    for _ in range(30):
        g.w(10)
        if g.options_shown():
            break
        if g.m[TEXT_ACTIVE]:
            g.press('a', 4)
    if not g.options_shown():
        return False
    g.choose(0 if answer_yes else 1, 2)
    g.w(60)
    g.settled()
    g.w(40)
    return True


def start(hearts):
    g.m[MAX_HEALTH] = hearts * 4
    g.m[HEALTH] = 4
    g.warp(3, 0x24, 0x53)
    g.w(40)
    g.text_through()
    frames[0] = 0
    return bulle()


g.level(3, 'Fin')
g.m[INV_A] = 0x05
for _ in range(10):
    g.text_through()
    g.w(20)
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

if MEASURE:
    check(start(14), 'Bulle : « On plonge ? » Oui')
    t = dive_down()
    print('temps (images) :', {('%02x' % k if isinstance(k, int) else k): v for k, v in t.items()})
    sys.exit(0)

# 8 cœurs : on voit le fond, mais pas l'épée
check(start(8), 'Bulle : « On plonge ? » Oui')
check(g.where() == (5, 0xd0), 'la Fosse (5:d0)')
check(g.m[HEALTH] == 32, 'on part le souffle plein (8 cœurs)')
shoot('f01_fosse', 'La Fosse de Bulle')
h0 = g.m[HEALTH]
w(120)
check(g.m[HEALTH] < h0, 'sous l\'eau, les cœurs se vident (%d -> %d quarts)' % (h0, g.m[HEALTH]))
t = dive_down()
print('   8 cœurs :', {('%02x' % k if isinstance(k, int) else k): v for k, v in t.items()})
check(0xd4 in t, 'avec 8 cœurs, on voit le fond (5:d4)')
if 'epee' in t:
    shoot('f02_fond', 'Le fond : l\'Épée de Légende')
    g.press('a', 20)        # (Link arrive par le haut : il la regarde)
    check(g.wait_text(60), "avec 8 cœurs : l'épée est prise dans le sable")
    w(20)
    shoot('f03_sable', 'Prise dans le sable : il faut plus de souffle')
    g.text_through()
for _ in range(400):
    w(2)
    if g.m[TEXT_ACTIVE]:
        break
check(g.m[TEXT_ACTIVE] != 0, 'à bout de souffle : Bulle tire sur la corde')
g.text_through()
w(120)
g.settled()
check(g.where() == (3, 0x24), 'retour au club (3:24)')
# Descendu à la 3e profondeur : Bulle apprend le contre parfait (TX_5b34, wTextIndex $cba2)
check(g.wait_text(120) and g.m[0xcba2] == 0x34, 'Bulle apprend le contre parfait')
shoot('f03b_contre', 'Bulle : le contre parfait')
g.text_through()
check(g.global_flag(0x61), 'le contre parfait est appris')
check(g.m[SWORD_LEVEL] < 3, 'avec 8 cœurs, pas d\'épée')
check(g.m[HEALTH] == g.m[MAX_HEALTH], 'les cœurs pleins en remontant')

# 9 cœurs : l'Épée de Légende
check(start(9), 'Bulle : on replonge avec 9 cœurs')
t = dive_down()
print('   9 cœurs :', {('%02x' % k if isinstance(k, int) else k): v for k, v in t.items()})
check('epee' in t, 'avec 9 cœurs, on atteint l\'épée (il reste %d quarts)' % g.m[HEALTH])
g.press('a', 20)
for _ in range(60):
    w(5)
    if g.m[TEXT_ACTIVE]:
        break
w(30)
shoot('f04_epee', "L'Épée de Légende")
check(g.m[SWORD_LEVEL] == 3, "l'Épée de Légende (l'épée niveau 3)")
for _ in range(20):
    g.text_through()
    w(30)
    if g.where() == (3, 0x24):
        break
g.settled()
check(g.where() == (3, 0x24), 'Bulle remonte Link au club')

sheet(shots, os.path.join(OUT, 'fosse.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
