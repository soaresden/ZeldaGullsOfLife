"""Test de l'île 3, la Lagune des Serments, par le menu de test caché (tools/debug_menu.py).

- arrivée au ponton (Marine parle), le Bateau-Rondin : aller à la Brume et revenir ;
- le tour de l'anneau de sable jusqu'à la maison d'Héloïse et Gaspard : Gaspard parle de sa
  bouteille, restée sur l'îlot de la lagune (trop profonde) ;
- la Lanterne : dans le Songe, la lagune s'ouvre en deux depuis l'ouest ; la bouteille ;
- Gaspard reprend sa bouteille, se souvient d'Héloïse et donne les Palmes de Zora ;
- à la nage : la lagune jusqu'à l'îlot du sud (le Récif Murmurant : Marine reste dehors), la
  plage des bouteilles (le facteur) ;
- la grotte des amoureux (Marine lit les cœurs, un coffre), le club de plongée (Bulle).

Usage : python tools/test_lagune.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, TREASURES, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_HARP, TREASURE_FLIPPERS, TREASURE_TRADEITEM = 0x11, 0x2e, 0x41
TRADE_ITEM = 0xc6c0          # wTradeItem
INTERAC_BALLADE_OBJECT = 0xed
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


def interaction_present(g, ident, subid=None):
    for h in range(0xd2, 0xe0):
        if g.m[h * 256 + 0x40] and g.m[h * 256 + 0x41] == ident:
            if subid is None or g.m[h * 256 + 0x42] == subid:
                return True
    return False


def run(g, direction, room, extra=0):
    """Courir sans s'arrêter jusqu'à la salle voisine (le temps du Songe est compté)."""
    g.pb.button_press(direction)
    g.wait_until(lambda: g.where() == room, 200)
    g.wait_until(lambda: g.m[0xcd00] & 1, 200)   # wScrollMode : l'écran a fini de défiler
    g.w(extra)
    g.pb.button_release(direction)


def talk(g, row, col, facing='up'):
    """Se placer sur une case, se tourner, A, et lire jusqu'au bout."""
    g.stand(row, col)
    g.face(facing)
    g.press('a', 20)
    ok = g.wait_text(60)
    g.w(30)
    return ok


g = Game()
g.level(3, 'Plage')
# A ne sert qu'à parler (sinon A allume la Lanterne quand Link n'est pas tout à fait face à
# quelqu'un) ; la Lanterne sur B
g.m[INV_A], g.m[INV_B] = 0x00, TREASURE_HARP
check(g.where() == (1, 0x24), 'le ponton de la Lagune (1:24)', g)
check(g.wait_text(200), 'Marine parle en arrivant', g)
g.w(60)
shoot(g, 'l01_arrivee', 'Arrivée au ponton')
g.text_through()

# Le Bateau-Rondin (y $38, x $18) : Link sur les planches, tourné vers l'ouest
g.goto(0x38, 0x30)
g.face('left')
g.press('a', 20)
g.choose(0, 3)
g.w(30)
g.settled()
g.w(60)
check(g.where() == (1, 0x99), 'le Bateau-Rondin mène à la Brume', g)
g.goto(0x48, 0x30)
g.face('left')
g.press('a', 20)
g.choose(2, 3)
g.w(30)
g.settled()
g.w(60)
check(g.where() == (1, 0x24), 'et ramène à la Lagune', g)

# Le tour de l'anneau : 24 -> 14 -> 04 (colonne 6), puis 05 -> 06 (ligne 4)
g.stand(3, 6)
check(g.go('up', (1, 0x14)), 'au nord : les rochers aux coquillages (1:14)', g)
shoot(g, 'l02_coquillages', 'Les rochers aux coquillages')
check(g.go('up', (1, 0x04)), 'le récif nord (1:04)', g)
g.stand(4, 6)
check(g.go('right', (1, 0x05)), 'la plage des serments (1:05)', g)
shoot(g, 'l03_plage', 'La plage des serments')
check(g.go('right', (1, 0x06)), "devant la maison d'Héloïse et Gaspard (1:06)", g)
shoot(g, 'l04_maison', 'La maison')
g.stand(4, 4)
check(g.go('up', (3, 0x23)), 'on entre (3:23)', g)
shoot(g, 'l05_interieur', 'Héloïse et Gaspard')

# Gaspard (ligne 4, colonne 3) : Link en dessous
check(talk(g, 5, 3), 'Gaspard parle', g)
shoot(g, 'l06_gaspard', 'Gaspard et sa bouteille')
g.text_through()
check(not obtained(g, TREASURE_FLIPPERS), 'sans la bouteille, pas de Palmes', g)
# Héloïse (ligne 4, colonne 6)
check(talk(g, 5, 6), 'Héloïse parle', g)
g.text_through()

# On sort par la porte (un saut de g.warp depuis un intérieur laisse la Lanterne muette : défaut
# du test, pas du jeu), puis à l'ouest de la lagune : 06 -> 05 -> 04 -> 14
g.stand(6, 4)
check(g.go('down', (1, 0x06)), 'on ressort', g)
g.stand(4, 4)
check(g.go('left', (1, 0x05)) and g.go('left', (1, 0x04)), "retour vers l'ouest", g)
g.stand(4, 6)
check(g.go('down', (1, 0x14)), 'la côte ouest de la lagune (1:14)', g)
# La Lanterne, au bord de l'eau (on n'a que 7 secondes dans le Songe, sans compter les textes) :
# le Songe ; on court jusqu'à la bouteille
g.stand(3, 7)
g.m[INV_B] = TREASURE_HARP
g.press('b', 10)
g.wait_until(lambda: g.where() == (0, 0x14), 300)
g.settled()
check(g.where() == (0, 0x14), 'la Lanterne : le Songe (0:14) ; 7 secondes pour revenir', g)
run(g, 'right', (0, 0x15))
check(g.where() == (0, 0x15), 'dans le Songe, la lagune s\'ouvre en deux (0:15)', g)
check(interaction_present(g, INTERAC_BALLADE_OBJECT, 0x12), 'la bouteille, sur l\'îlot', g)
shoot(g, 'l07_songe', 'La lagune s\'ouvre')
g.goto(None, 0x28)
g.face('right')
g.press('a', 30)
check(g.wait_text(120), 'la bouteille : un texte', g)
shoot(g, 'l08_bouteille', 'La bouteille à la mer')
g.text_through()
check(obtained(g, TREASURE_TRADEITEM) and g.m[TRADE_ITEM] == 1, 'la bouteille est l\'objet d\'échange 1', g)
check(not interaction_present(g, INTERAC_BALLADE_OBJECT, 0x12), 'elle n\'est plus sur l\'îlot', g)

# Retour au Réel (depuis la côte), puis chez Gaspard
run(g, 'left', (0, 0x14), 40)
check(g.where() == (0, 0x14), 'retour sur la côte (0:14)', g)
g.goto(None, 0x68)
g.text_through()   # Marine prévient : « Tu vas te réveiller ! »
g.press('b', 10)
g.wait_until(lambda: g.where() == (1, 0x14), 600)
g.settled()
check(g.where() == (1, 0x14), 'la Lanterne : le Réel', g)
g.stand(1, 6)
check(g.go('up', (1, 0x04)), 'vers le nord (1:04)', g)
g.stand(4, 6)
check(g.go('right', (1, 0x05)) and g.go('right', (1, 0x06)), 'la maison', g)
g.stand(4, 4)
check(g.go('up', (3, 0x23)), 'chez Gaspard', g)
check(talk(g, 5, 3), 'Gaspard reconnaît sa bouteille', g)
shoot(g, 'l09_lettre', 'La lettre')
g.text_through()
g.w(60)
g.text_through()
check(obtained(g, TREASURE_FLIPPERS), 'Gaspard donne les Palmes de Zora', g)
check(g.m[TRADE_ITEM] != 1 or not obtained(g, TREASURE_TRADEITEM), 'il a gardé la bouteille', g)
check(talk(g, 5, 3), 'Gaspard, après', g)
g.text_through()

# À la nage : depuis la plage de la maison, vers le sud, jusqu'à l'îlot du Récif Murmurant
g.stand(6, 4)
check(g.go('down', (1, 0x06)), 'on ressort', g)
g.stand(5, 4)
check(g.go('down', (1, 0x16)), 'à l\'eau : la lagune (1:16)', g)
shoot(g, 'l10_nage', 'À la nage')
g.goto(None, 0x48)
check(g.go('down', (1, 0x26)), 'toujours à la nage (1:26)', g)
check(g.go('down', (1, 0x36)), 'l\'îlot du Récif Murmurant (1:36)', g)
check(g.wait_text(200), 'Marine : elle ne peut pas suivre sous l\'eau', g)
g.w(60)
shoot(g, 'l11_recif', 'Le Récif Murmurant')
g.text_through()
g.stand(2, 2)
check(g.go('left', (1, 0x35)), 'la plage des bouteilles (1:35)', g)
check(talk(g, 2, 7, 'left'), 'le facteur des bouteilles', g)
shoot(g, 'l12_facteur', 'Le facteur')
g.text_through()

# La grotte des amoureux (1:27, entrée en ligne 3, colonne 6)
g.warp(1, 0x27, 0x46)
check(g.go('up', (5, 0xb1)), 'la grotte des amoureux (5:b1)', g)
check(g.wait_text(200), 'Marine lit les cœurs gravés', g)
g.w(40)
shoot(g, 'l13_grotte', 'La grotte des amoureux')
g.text_through()
r0 = g.rupees()
g.open_chest(1, 7)
g.text_through()
check(g.rupees() > r0, 'le coffre : des rubis (%d -> %d)' % (r0, g.rupees()), g)

# Le club de plongée (1:17, porte en ligne 2, colonne 6) : Bulle
g.warp(1, 0x17, 0x36)
check(g.go('up', (3, 0x24)), 'le club de plongée (3:24)', g)
check(talk(g, 5, 3), 'Bulle parle', g)
shoot(g, 'l14_bulle', 'Bulle')
g.text_through()

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
