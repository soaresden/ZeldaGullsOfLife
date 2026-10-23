"""Test de l'île 4, Mont-Braise, par le menu de test caché (tools/debug_menu.py).

- arrivée au ponton (Marine parle), le Bateau-Rondin : aller à la Lagune et revenir ;
- la plage, les lacets, l'atelier : Pinceau ne peint que le volcan ;
- la Lanterne : dans le Songe, Pinceau voit la mer et donne le tableau (l'objet d'échange 2) ;
- le village goron : Brasia voit le tableau, a une idée, donne le Bracelet de force ;
- les rochers du nord du village se soulèvent : les lacets jusqu'au cratère ;
- la mine abandonnée (un coffre), le marché des copies, les Cuivres, le belvédère, la source.

Usage : python tools/test_braise.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, TREASURES, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_HARP, TREASURE_BRACELET, TREASURE_TRADEITEM = 0x11, 0x16, 0x41
TRADE_ITEM = 0xc6c0          # wTradeItem
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
    g.hold(facing, 8)     # un vrai appui : à l'arrivée dans le Songe, un appui bref ne le tourne pas
    g.press('a', 20)
    ok = g.wait_text(60)
    g.w(30)
    return ok


def door(g, direction, room):
    """Passer par le passage d'un côté (nord / sud colonnes 4-5, est / ouest lignes 3-4)."""
    row, col = {'up': (1, 4), 'down': (6, 4), 'left': (4, 1), 'right': (4, 8)}[direction]
    # vers l'est ou l'ouest : d'abord sur la ligne du passage (des rochers dans les coins)
    g.stand(row, col, y_first=direction in ('left', 'right'))
    return g.go(direction, room)


g = Game()
g.level(4, 'Plage')
g.m[INV_A], g.m[INV_B] = 0x00, TREASURE_HARP
check(g.where() == (1, 0x38), 'le ponton de Mont-Braise (1:38)', g)
check(g.wait_text(200), 'Marine parle en arrivant', g)
g.w(60)
shoot(g, 'b01_arrivee', 'Arrivée au ponton')
g.text_through()

# Le Bateau-Rondin (y $68, x $58) : Link au bout des planches (ligne 6, colonne 4), vers l'est
g.stand(6, 4)
g.face('right')
g.press('a', 20)
g.choose(2, 4)
g.w(30)
g.settled()
g.w(60)
check(g.where() == (1, 0x24), 'le Bateau-Rondin mène à la Lagune', g)
g.text_through()     # Marine, la première fois à la Lagune
g.goto(0x38, 0x30)
g.face('left')
g.press('a', 20)
g.choose(3, 4)
g.w(30)
g.settled()
g.w(60)
check(g.where() == (1, 0x38), 'et ramène à Mont-Braise', g)

# La plage, les lacets de l'ouest, l'atelier
check(door(g, 'right', (1, 0x39)), 'la plage noire (1:39)', g)
check(door(g, 'up', (1, 0x29)), "les lacets de l'ouest (1:29)", g)
check(door(g, 'up', (1, 0x19)), "l'atelier des peintres (1:19)", g)
check(talk(g, 4, 5), 'Pinceau ne peint que le volcan', g)
shoot(g, 'b02_pinceau', 'Pinceau')
g.text_through()

# La Lanterne : dans le Songe, Pinceau voit la mer
g.press('b', 10)
g.wait_until(lambda: g.where() == (0, 0x19), 300)
g.settled()
g.w(160)   # l'arrivée dans le Songe : le rayon de lumière (Link ne bouge pas avant)
check(g.where() == (0, 0x19), 'la Lanterne : le Songe (0:19)', g)
check(talk(g, 4, 5), 'Pinceau voit la mer', g)
shoot(g, 'b03_songe', 'Pinceau dans le Songe')
g.text_through()
g.w(60)
g.text_through()
check(obtained(g, TREASURE_TRADEITEM) and g.m[TRADE_ITEM] == 2, 'le tableau de la mer (objet d\'échange 2)', g)
shoot(g, 'b04_tableau', 'Le tableau de la mer')
g.press('b', 10)
g.wait_until(lambda: g.where() == (1, 0x19), 600)
g.settled()
check(g.where() == (1, 0x19), 'retour au Réel', g)

# Le village goron : Brasia
check(door(g, 'down', (1, 0x29)), 'retour aux lacets', g)
check(door(g, 'right', (1, 0x2a)), 'le village goron (1:2a)', g)
shoot(g, 'b05_village', 'Le village goron')
check(talk(g, 4, 2), 'Brasia voit le tableau', g)
shoot(g, 'b06_brasia', 'Brasia a une idée')
g.text_through()
g.w(60)
g.text_through()
check(obtained(g, TREASURE_BRACELET), 'le Bracelet de force', g)

# Les rochers du nord (ligne 0, colonnes 4-5) : on les soulève et on les jette
g.m[INV_A] = 0x16    # le Bracelet de force sur A
for col in (4, 5):
    g.stand(1, col)
    g.hold('up', 8)
    # le Bracelet : garder le bouton enfoncé face au rocher, et tirer (vers le bas)
    g.pb.button_press('a')
    g.w(10)
    g.hold('down', 16)
    g.pb.button_release('a')
    g.w(40)
    g.press('a', 40)     # on le jette
    g.w(40)
check(g.tile(0x04) != 0xc0 and g.tile(0x05) != 0xc0, 'les rochers sont soulevés', g)
g.m[INV_A] = 0x00
check(door(g, 'up', (1, 0x1a)), 'les lacets du cratère (1:1a)', g)
g.route((5, 4), (5, 2), (3, 2), (3, 7), (1, 7), (1, 4))
check(g.go('up', (1, 0x0a)), 'le cratère (1:0a)', g)
shoot(g, 'b07_cratere', 'Le cratère')

# La mine abandonnée (1:28, entrée ligne 1, colonne 3)
g.warp(1, 0x28, 0x23)
check(g.go('up', (5, 0xb2)), 'la mine abandonnée (5:b2)', g)
g.w(60)
r0 = g.rupees()
g.stand(2, 11)       # par la droite : des rochers au milieu de la mine
g.hold('up', 12)
g.press('a', 60)
g.text_through(10)
g.w(60)
check(g.tile(0x1b) == 0xf0, 'le coffre de la mine', g)
check(g.rupees() > r0, 'des rubis (%d -> %d)' % (r0, g.rupees()), g)

# Le marché des copies, les Cuivres
g.warp(1, 0x3a, 0x34)
g.w(60)              # (Link ne bouge pas tout de suite en arrivant)
check(talk(g, 3, 4), 'le marchand de copies', g)
shoot(g, 'b08_marchand', 'Le marchand de copies')
g.text_through()
g.warp(1, 0x2a, 0x57)
check(talk(g, 4, 7), 'les Cuivres', g)
g.text_through()

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
