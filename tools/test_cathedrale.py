"""Test de la Cathédrale des Échos (donjon 5), jouée de bout en bout depuis le menu de test caché
(5. Donjon) : la carte, la chapelle des cierges (le premier Veilleur) et la petite clé 1, la nef
basse (le Veilleur qui tourne), la porte à clé, la nef (deux Veilleurs) et le Grappin-Écho, le
Gardien des Cloches, les gouffres et les diamants (la petite clé 2, la tribune est, la clé du
chœur), le déambulatoire, le chœur, le souvenir (Tarkin, la maison de Marine à Mabe), l'essence,
la fin du chapitre 5.

Les Veilleurs (les gardes d'Ambi) : on lit leur position et leur regard dans la mémoire, et on
passe quand ils regardent ailleurs. Un Veilleur qui voit Link le renvoie à l'entrée de la salle :
le test le vérifie aussi une fois (exprès).

Seule triche : le Gardien des Cloches et les ennemis sont retirés (leur vie mise à zéro), et Link
garde sa vie pleine.

Usage : python tools/test_cathedrale.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import (BOSS_KEYS, ESSENCES, HEALTH, INV_A, INV_B, MAX_HEALTH, TEXT_ACTIVE,
                        TREASURES, Game, sheet)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_SWITCH_HOOK = 0x0a
ENEMY_AMBI_GUARD = 0x54
RIGHT, DOWN, LEFT, UP = 0x08, 0x10, 0x18, 0x00
GLOBALFLAG_BALLADE_ISLAND6 = 0x55
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe(), 'clés', g.small_keys(5), 'veilleurs', guards())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def obtained(t):
    return bool(g.m[TREASURES + t // 8] & (1 << (t % 8)))


def full_life():
    g.m[HEALTH] = g.m[MAX_HEALTH]


def guards():
    """Les Veilleurs de la salle : (sous-type, y, x, regard)."""
    return [(g.m[b + 2], g.m[b + 0x0b], g.m[b + 0x0d], g.m[b + 9]) for b in g.enemies(ENEMY_AMBI_GUARD)]


def wait_guard(cond, which=0, limit=2000):
    """Attendre que le Veilleur (le n-ième de la salle) soit comme on veut : cond(y, x, regard)."""
    for _ in range(limit):
        gs = guards()
        if len(gs) > which and cond(*gs[which][1:]):
            return True
        g.w(1)
    return False


def away_from_col(x0):
    """Le Veilleur d'une ligne regarde ailleurs que la colonne x0 (il s'en éloigne)."""
    return lambda y, x, a: (a == RIGHT and x > x0 + 20) or (a == LEFT and x < x0 - 20)


def door(direction, room, row=None, col=None, y_first=False):
    """Se placer face à la porte (haut, bas : colonne 7 ; gauche, droite : ligne 5) et passer."""
    r, c = {'up': (1, 7), 'down': (9, 7), 'left': (5, 1), 'right': (5, 13)}[direction]
    g.stand(r if row is None else row, c if col is None else col, y_first)
    return g.go(direction, room)


def hook(facing, wait=70):
    """Le Grappin-Écho (sur B), tourné vers facing : Link échange sa place avec un diamant."""
    g.m[INV_B] = TREASURE_SWITCH_HOOK
    g.face(facing)
    g.press('b', 10)
    g.w(wait)


def near(row, col):
    y, x = g.link()
    return abs(y - (row * 16 + 8)) <= 4 and abs(x - (col * 16 + 8)) <= 4


def chest(row, col):
    """Ouvrir le coffre (row, col) par en dessous (il ne s'ouvre pas des autres cotés)."""
    g.stand(row + 1, col, y_first=True)
    g.hold('up', 10)
    g.press('a', 60)
    g.text_through(10)
    g.w(40)
    return g.tile(row * 16 + col) == 0xf0


def key_door(room):
    """Pousser la porte à clé du haut (Link en (1, 7)) puis passer."""
    g.hold('up', 40)
    g.w(40)
    return g.go('up', room)


# --- Le portail ---
g.level(5, 'Donjon')
g.m[INV_A], g.m[INV_B] = 0x05, 0x00
full_life()
check(g.where() == (5, 0xaa), "l'entrée de la Cathédrale des Échos (5:aa)")
check(g.wait_text(200), 'le nom du donjon')
g.w(30)
shoot('c01_entree', "L'entrée")
for _ in range(4):
    if not g.m[TEXT_ACTIVE]:
        break
    g.press('a', 20)
check(g.wait_text(120), 'Marine : les Veilleurs')
g.w(40)
shoot('c02_marine', 'Marine : les Veilleurs')
g.text_through()

# --- À l'ouest : la carte ; la chapelle des cierges ; la sacristie (la petite clé 1) ---
g.route((7, 7), (7, 2), (5, 2))   # l'arche de l'entrée bouche le bas
check(g.go('left', (5, 0x92)), 'le bas-côté sud-ouest (5:92)')
g.clear_enemies()
check(chest(5, 3), 'le coffre de la carte')
check(door('up', (5, 0x8f), 6, 7), 'la chapelle des cierges (5:8f)')
check(len(guards()) == 1, 'le premier Veilleur')
g.stand(9, 6)
# Exprès : traverser sous ses yeux -> Link se réveille à l'entrée de la salle
wait_guard(lambda y, x, a: a == RIGHT and x < 70)
g.stand(5, 6)
g.w(200)
g.settled()
shoot('c03_vu', 'Vu ! Link se réveille à l\'entrée')
check(g.where() == (5, 0x8f) and g.link()[0] > 0x80, 'vu : Link se réveille à l\'entrée de la salle')
g.stand(9, 6)
check(wait_guard(away_from_col(104)), 'le Veilleur regarde ailleurs')
g.route((3, 6), (1, 6), (1, 7))
check(g.go('up', (5, 0x8b)), 'passé dans son dos : la sacristie (5:8b)')
check(chest(3, 7), 'le coffre de la petite clé 1')
check(g.small_keys(5) == 1, 'la petite clé 1 (%d)' % g.small_keys(5))
check(door('down', (5, 0x8f)), 'retour à la chapelle des cierges')
g.stand(1, 6)
check(wait_guard(away_from_col(104)), 'le Veilleur regarde ailleurs (retour)')
g.route((7, 6), (9, 6), (9, 7))
check(g.go('down', (5, 0x92)), 'retour au bas-côté sud-ouest')
check(door('right', (5, 0xaa), 5, 12), 'retour au portail')

# --- La nef basse : le Veilleur qui tourne ; la porte à clé ---
g.route((7, 1), (7, 7), (1, 7))
check(g.go('up', (5, 0x90)), 'la nef basse (5:90)')
g.route((9, 3), (1, 3), (1, 7))
shoot('c04_nefbasse', 'La nef basse : derrière les statues')
check(key_door((5, 0x8d)), 'la porte à clé : la nef (5:8d)')

# --- La nef : deux Veilleurs ; le Grappin-Écho ---
check(len(guards()) == 2, 'les deux Veilleurs de la nef')
g.stand(9, 6)
check(wait_guard(away_from_col(104), 1), 'le Veilleur du bas regarde ailleurs')
g.stand(5, 6)
# Attendre au milieu (à deux cases de chaque ronde : leur regard de près porte à une case)
check(wait_guard(lambda y, x, a: a == RIGHT and 125 < x < 170, 0), 'le Veilleur du haut regarde ailleurs')
g.route((1, 6), (1, 3), (2, 3), (2, 2))
shoot('c05_nef', 'La nef : passé entre les Veilleurs')
g.hold('up', 10)
g.press('a', 60)
g.w(30)
shoot('c06_grappin', 'Le Grappin-Écho')
g.text_through(10)
check(obtained(TREASURE_SWITCH_HOOK), 'le Grappin-Écho')
check(g.where() == (5, 0x8d), 'toujours dans la nef (pas vu)')
g.route((2, 3), (1, 3), (1, 7))
check(g.go('up', (5, 0x83)), 'la croisée (5:83)')

# --- La croisée : le Gardien des Cloches ---
g.w(120)
shoot('c07_gardien', 'Le Gardien des Cloches')
check(g.tile(0xa7) == 0x7a, 'les volets fermés')
g.clear_enemies()
g.w(240)
full_life()
check(g.tile(0xa7) != 0x7a, 'le Gardien battu : les volets ouverts')
g.route((6, 7), (6, 1), (5, 1))   # des statues dans les coins
check(g.go('left', (5, 0x82)), 'le croisillon ouest (5:82)')

# --- À l'ouest : les gouffres, les diamants ; la petite clé 2 ---
g.stand(3, 7)
hook('left')
check(near(3, 2), 'le Grappin-Écho : de l\'autre coté du gouffre')
shoot('c08_diamant', 'Le Grappin-Écho : échange avec le diamant')
check(door('left', (5, 0x81), 5, 1), 'la galerie des échos (5:81)')
check(len(guards()) == 1, 'le Veilleur de la galerie')
g.stand(3, 13)   # on vise avec une case libre devant soi : au bord d'un trou, Link glisse
check(wait_guard(lambda y, x, a: y < 40 or y > 120), 'le Veilleur loin de la ligne 3')
hook('left')
check(near(3, 9), "sur l'île")
check(wait_guard(lambda y, x, a: a == UP and y < 100), 'le Veilleur remonte')
g.route((7, 9), (7, 6))
hook('left')
check(near(7, 2), "à l'ouest de la galerie")
check(door('left', (5, 0x80), 5, 1), 'le bout ouest (5:80)')
g.clear_enemies()
check(chest(5, 4), 'le coffre de la petite clé 2')
check(g.small_keys(5) == 1, 'la petite clé 2 (%d)' % g.small_keys(5))
check(door('right', (5, 0x81)), 'retour à la galerie')
g.stand(5, 1)
check(wait_guard(lambda y, x, a: y > 130 or y < 30), 'le Veilleur loin du diamant')
hook('right')
check(near(5, 6), "sur l'île (retour)")
g.stand(5, 5)   # pas à coté de sa colonne : il voit à une case autour de lui
check(wait_guard(lambda y, x, a: a == UP and y < 80), 'le Veilleur remonte (retour)')
g.route((7, 5), (7, 8))
hook('right')
check(near(7, 12), "à l'est de la galerie")
check(door('right', (5, 0x82), 5, 13), 'retour au croisillon ouest')
g.stand(7, 1)
hook('right')
check(near(7, 6), 'le diamant de l\'est')
check(door('right', (5, 0x83), 5, 13), 'retour à la croisée')

# --- À l'est : la tribune est, la chapelle des cloches, la clé du chœur ---
g.route((6, 1), (6, 13), (5, 13))
check(g.go('right', (5, 0x85)), 'le croisillon est (5:85)')
g.stand(6, 6)
hook('up')
check(near(1, 6), 'au-dessus du gouffre')
g.route((1, 7))
check(g.go('up', (5, 0x7f)), 'la tribune est (5:7f)')
g.clear_enemies()
r0 = g.rupees()
check(chest(3, 7), 'le coffre de la tribune est')
check(g.rupees() > r0, 'des rubis (%d -> %d)' % (r0, g.rupees()))
check(door('down', (5, 0x85)), 'retour au croisillon est')
g.stand(1, 8)
hook('down')
check(near(6, 8), 'redescendu par le diamant')
check(door('right', (5, 0x86), 5, 13), 'la chapelle des cloches (5:86)')
g.stand(2, 4, y_first=True)
hook('right')
check(near(2, 9), "de l'autre coté du gouffre")
g.route((1, 9), (1, 13), (5, 13))
check(g.go('right', (5, 0x89)), 'le bout est (5:89)')
g.clear_enemies()
check(chest(5, 10), 'le coffre de la clé du chœur')
check(g.m[BOSS_KEYS] & 0x20, 'la clé du chœur')
check(door('left', (5, 0x86), 5, 1), 'retour à la chapelle des cloches')
check(wait_guard(lambda y, x, a: a == LEFT), 'le Veilleur regarde à gauche')
g.route((8, 13), (8, 10))
shoot('c09_cloches', 'La chapelle des cloches')
hook('left')
check(near(8, 5), "le diamant de l'ouest")
g.route((8, 1), (5, 1))
check(g.go('left', (5, 0x85)), 'retour au croisillon est')
check(door('left', (5, 0x83), 5, 1), 'retour à la croisée')

# --- Le déambulatoire, le chœur ---
g.route((1, 13), (1, 7))
check(key_door((5, 0x7d)), 'la porte à clé : le déambulatoire (5:7d)')
g.stand(1, 7)
check(key_door((5, 0x7b)), 'la porte du chœur (la clé du chœur) : le chœur (5:7b)')
check(g.wait_text(120), "Marine : l'escalier")
g.w(40)
shoot('c10_choeur', 'Le chœur : Marine')
g.text_through()
g.stand(3, 7)
g.hold('up', 40)
g.settled()
g.w(60)
check(g.where() == (3, 0x26), 'le souvenir : la maison de Marine à Mabe (3:26)')

# --- Le souvenir : Tarkin (assis de dos sous la table, en (6,8) ; il connaît Link : quand Link
# approche, il se retourne de lui-même, « OH ! LINK ! Quel plaisir ! ») ---
g.route((6, 4), (6, 6))
check(g.wait_text(60), 'Tarkin : « OH ! LINK ! Quel plaisir ! »')
g.w(40)
shoot('c11_tarkin', 'Tarkin')
g.text_through()
g.w(60)
g.text_through()
g.w(60)
g.text_through()
check(g.room_flags(3, 0x26) & 0x80, 'le souvenir est fini')
g.route((6, 4))
check(g.go('down', (5, 0x7b)), 'retour au chœur')
g.w(120)
shoot('c12_essence', "L'essence apparaît dans le chœur")
# Le piédestal (ligne 6, colonne 7) barre la colonne : le contourner, le toucher par en dessous
g.route((3, 5), (8, 5), (8, 7))
for _ in range(8):
    if g.m[ESSENCES] & 0x10:
        break
    g.hold('up', 40)
    g.w(30)
    if g.m[TEXT_ACTIVE]:
        shoot('c13_couplet', 'Le cinquième couplet')
    g.text_through()
    g.press('a', 30)
check(g.m[ESSENCES] & 0x10, "l'essence (le cinquième couplet)")
g.w(200)
g.settled()

# --- La fin du chapitre 5 : la place du silence ---
g.wait_until(lambda: g.where() == (1, 0x62), 600)
check(g.where() == (1, 0x62), 'la place du silence (1:62)')
check(g.wait_text(400), 'les cloches chantent')
g.w(40)
shoot('c14_cloches', 'Les cloches chantent')
g.text_through()
check(g.wait_text(200), 'Marine lit le vent')
g.w(40)
shoot('c15_vent', 'Marine lit le vent')
g.text_through(60)
check(g.global_flag(GLOBALFLAG_BALLADE_ISLAND6), 'le Nid des Vents est repéré')

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
