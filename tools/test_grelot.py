"""Test de l'île 2, Hameau-Grelot, par le menu de test caché (tools/debug_menu.py).

- arrivée à la jetée (Marine parle), le Bateau-Rondin : aller à la Brume et revenir ;
- la boutique de Pépin : acheter 10 bombes ;
- la falaise de la grotte de la Boîte : une bombe fait sauter les rochers, on entre ;
- dans la grotte, Marine apprend à porter une bombe : Link en soulève une, Select, Marine la porte
  par-dessus le gouffre jusqu'au grelot, qui sonne : un pont apparaît.

Usage : python tools/test_grelot.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import BOMBS, INV_A, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
GLOBALFLAG_BALLADE_MARINE_BOMB = 0x58
GLOBALFLAG_BALLADE_LILA_ASLEEP = 0x59
TREASURE_TRADEITEM = 0x41
TRADE_ITEM = 0xc6c0          # wTradeItem
INTERAC_MARINE = 0xe7
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


def interaction_present(g, ident, subid=None):
    for h in range(0xd2, 0xe0):
        if g.m[h * 256 + 0x40] and g.m[h * 256 + 0x41] == ident:
            if subid is None or g.m[h * 256 + 0x42] == subid:
                return True
    return False


def raft_to(g, option, count):
    """A devant le Bateau-Rondin (Link tourné vers lui), choisir l'île."""
    g.press('a', 20)
    g.choose(option, count)
    g.w(30)
    g.settled()
    g.w(60)


g = Game()
g.level(2, 'Plage')
check(g.where() == (1, 0x31), 'la jetée de Hameau-Grelot (1:31)', g)
check(g.wait_text(200), 'Marine parle en arrivant', g)
g.w(60)
shoot(g, 'g01_arrivee', 'Arrivée à la jetée')
g.text_through()

# Le Bateau-Rondin : au bout du ponton (y $48, x $18) ; Link sur le ponton, tourné vers l'ouest
g.goto(0x48, 0x30)
g.face('left')
raft_to(g, 0, 2)
check(g.where() == (1, 0x99), 'le Bateau-Rondin mène à la Brume (le Ponton, 1:99)', g)
shoot(g, 'g02_brume', 'Le radeau : la Brume')
g.goto(0x48, 0x30)
g.face('left')
raft_to(g, 1, 2)
check(g.where() == (1, 0x31), 'et ramène à Hameau-Grelot', g)
shoot(g, 'g03_retour', 'Retour à Grelot')

# La boutique de Pépin (porte : ligne 3, colonne 4 de 1:12)
g.warp(1, 0x12, 0x44)
shoot(g, 'g04_boutique_dehors', 'La boutique de Pépin')
g.hold('up', 40)
g.settled()
g.w(30)
check(g.where() == (3, 0x20), 'la porte mène dans la boutique de Pépin (3:20)', g)
shoot(g, 'g05_boutique', 'Dedans')
money = g.rupees()
# prendre les bombes sur le comptoir (x $68), les porter au marchand
g.goto(None, 0x58)
g.goto(0x40, None)
g.goto(None, 0x68)
g.hold('up', 8)
g.press('a', 30)
g.goto(None, 0x88)
g.goto(0x48, None)
g.hold('down', 2)
g.press('a', 40)
for _ in range(4):
    g.press('a', 30)
g.text_through()
g.w(60)
check(g.m[BOMBS] == 0x10 and money - g.rupees() == 20, '10 bombes pour 20 rubis (bombes %x)' % g.m[BOMBS], g)
shoot(g, 'g06_bombes', '10 bombes')

# La falaise de la grotte : une bombe devant les rochers (ligne 2, colonne 4)
g.warp(1, 0x32, 0x34)
g.text_through()
shoot(g, 'g07_falaise', 'La falaise')
g.goto(0x36, 0x48)
g.face('up')
# les bombes sur A (à la place de la Lanterne), comme un joueur le ferait dans l'inventaire
g.m[0xc689] = 0x03
slot = 'a'
g.tap(slot, 30)            # la bombe au-dessus de la tête
g.tap(slot, 10)            # posée contre les rochers
g.hold('down', 30)         # et on s'éloigne
g.w(150)
check(g.tile(0x24) == 0xdd, 'la bombe ouvre l\'entrée de la grotte (brique %02x)' % g.tile(0x24), g)
shoot(g, 'g08_grotte_ouverte', 'La grotte ouverte')
g.goto(None, 0x48)
g.goto(0x38, None)
g.hold('up', 40)
g.settled()
g.w(30)
check(g.where() == (5, 0xb0), 'on entre dans la grotte de la Boîte (5:b0)', g)
check(g.wait_text(200), 'Marine voit le grelot', g)
g.w(60)
shoot(g, 'g09_grotte', 'Marine voit le grelot')
g.text_through()
check(g.global_flag(GLOBALFLAG_BALLADE_MARINE_BOMB), 'Marine sait maintenant porter une bombe', g)

# Le gouffre : Link au bord (ligne 7, colonne 7), une bombe, il la soulève, Select
g.goto(0x78, 0x78)
g.face('up')
g.tap(slot, 30)            # une bombe au-dessus de la tête
print('     prise :', hex(g.m[0xcc5a]))
check(g.m[0xcc5a] & 7 == 3, 'Link tient la bombe au-dessus de sa tête', g)
g.press('select', 10)
check(interaction_present(g, INTERAC_MARINE, 0x06), 'Select : Marine sort et prend la bombe', g)
g.w(20)
shoot(g, 'g10_marine_porte', 'Marine porte la bombe')
g.w(120)
shoot(g, 'g11_grelot', 'Le grelot sonne')
flags = g.room_flags(5, 0xb0)
check(flags & 0x40, 'le grelot a sonné (drapeau de la salle %02x)' % flags, g)
check(g.tile(0x37) == 0xef and g.tile(0x67) == 0xef, 'un pont traverse le gouffre', g)
g.w(60)
shoot(g, 'g12_pont', 'Le pont')
# traverser
g.goto(0x28, None)
check(g.link()[0] <= 0x2a, 'Link traverse le pont', g)
shoot(g, 'g13_traverse', "De l'autre côté")

# Le coffre (ligne 1, colonne 12) : Sire Bouchon, le jouet de Lila (objet d'échange 0)
g.m[0xc689] = 0x00         # plus rien sur A : A sert à parler, ouvrir...
g.goto(0x28, 0xc8)
g.hold('up', 10)
g.press('a', 20)
g.w(60)
shoot(g, 'g14_sire_bouchon', 'Sire Bouchon !')
g.text_through()
check(g.has(TREASURE_TRADEITEM) and g.m[TRADE_ITEM] == 0, "Sire Bouchon (objet d'échange 0) est dans l'inventaire", g)

# La maison de Lila (porte : ligne 3, colonne 4 de 1:21)
g.warp(1, 0x21, 0x44)
g.hold('up', 40)
g.settled()
g.w(30)
check(g.where() == (3, 0x21), 'la porte mène chez Lila (3:21)', g)
# Lila (y $48, x $38) : on lui parle d'en dessous
g.goto(0x58, 0x38)
g.face('up')
g.press('a', 20)
check(g.wait_text(60), 'Lila parle', g)
g.w(40)
shoot(g, 'g15_lila', 'Lila retrouve Sire Bouchon')
g.text_through()
check(g.global_flag(GLOBALFLAG_BALLADE_LILA_ASLEEP), "Lila s'endort", g)
check(not g.has(TREASURE_TRADEITEM), 'Lila a repris Sire Bouchon', g)

g.w(30)
lila = [(g.m[(sl << 8) + 0x4b], g.m[(sl << 8) + 0x4d]) for sl in range(0xd2, 0xe0)
        if g.m[(sl << 8) + 0x41] == 0xed and g.m[(sl << 8) + 0x42] == 0x04]
check(lila == [(0x1c, 0x88)], 'Lila dort dans son lit %s' % lila, g)
shoot(g, 'g15b_lila_dort', 'Lila dort')
# Le lit : tout contre, tourné vers lui (case $27, vers la droite) ; l'épée sur A (comme Denis) :
# pousser contre le lit -> « Dormir un peu ? »
g.m[INV_A] = 0x05
g.goto(None, 0x68)
g.goto(0x28, None)
g.goto(None, 0x78)
g.hold('right', 50)
g.choose(0, 2)
g.w(60)
for _ in range(400):
    g.w(1)
    if g.where() == (2, 0x21):
        break
g.settled()
g.w(60)
check(g.where() == (2, 0x21), 'en dormant, Link entre dans le rêve de Lila (2:21)', g)
shoot(g, 'g16_reve', 'Le rêve de Lila')
# Lila du rêve (Link se réveille à coté du lit, case $17 ; on descend par le tapis)
g.goto(0x38, None)
g.goto(None, 0x38)
g.face('down')             # Lila est juste en dessous
g.press('a', 20)
check(g.wait_text(60), 'Lila parle dans son rêve', g)
g.text_through()
# Le Coffre à Jouets (y $58, x $78) : « Entrer ? »
g.goto(0x58, 0x60)
g.face('right')
g.press('a', 20)
check(g.wait_text(60), "le Coffre à Jouets propose d'entrer", g)
shoot(g, 'g17_coffre', 'Le Coffre à Jouets')
g.choose(1, 2)               # « Non » (le donjon n'est pas encore là)
g.w(30)

# Le Carnet des Rêves (sur B) : la page de la Brume et de Grelot
g.m[0xc688] = 0x12
g.press('b', 20)
check(g.wait_text(60), 'le Carnet des Rêves se lit', g)
g.w(60)
shoot(g, 'g18_carnet', 'Le Carnet des Rêves')
g.text_through()
g.stop()
sheet(shots, os.path.join(OUT, 'planche.png'))

print('\n%d erreur(s)' % len(errors) if errors else '\nTout est bon.')
for e in errors:
    print('  -', e)
sys.exit(1 if errors else 0)
