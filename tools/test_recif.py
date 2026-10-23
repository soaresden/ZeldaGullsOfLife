"""Test du Récif Murmurant (donjon 3), joué de bout en bout depuis le menu de test caché
(3. Donjon) : Marine reste dehors ; la petite clé 1 ; la boussole ; la porte à clé, Vire et les
Écailles de Sirène ; la plongée (3b -> 30 -> 2e -> 35 -> on remonte dans 3c) ; la carte, la
petite clé 2 ; les coquillages-échos et la clé du boss ; retour à la nage ; l'antichambre ; la
Murène du Silence (Octogon) et l'essence ; la fin du chapitre 3.

Seule triche : les ennemis, le mini-boss et le boss sont retirés (leur vie mise à zéro), et Link
garde sa vie pleine.

Usage : python tools/test_recif.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import BOSS_KEYS, ESSENCES, HEALTH, INV_A, INV_B, MAX_HEALTH, TREASURES, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_MERMAID_SUIT, TREASURE_COMPASS, TREASURE_MAP = 0x4a, 0x32, 0x33
ENEMY_VIRE, ENEMY_OCTOGON = 0x75, 0x7d
INTERAC_ESSENCE = 0x7f
UNDERWATER = ((5, 0x30), (5, 0x2e), (5, 0x35), (5, 0x2d))
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe(), 'clés', g.small_keys(3))
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
    if g.where() in UNDERWATER:
        swim_to(row, col)
    else:
        g.stand(row, col, y_first)
    return g.go(direction, room)


def swim_to(row, col, limit=300):
    """Sous l'eau, Link glisse : petits coups de bouton, x puis y, jusqu'à ce qu'il s'arrête sur
    la case (à 4 pixels près)."""
    y, x = row * 16 + 8, col * 16 + 8
    for _ in range(10):
        for axis, target, minus, plus in (('x', x, 'left', 'right'), ('y', y, 'up', 'down')):
            for _ in range(limit):
                ly, lx = g.link()
                cur = lx if axis == 'x' else ly
                if abs(cur - target) <= 2:
                    break
                b = minus if cur > target else plus
                g.pb.button_press(b)
                g.w(4 if abs(cur - target) > 10 else 1)
                g.pb.button_release(b)
                g.w(3)
        g.w(40)
        ly, lx = g.link()
        if abs(ly - y) <= 4 and abs(lx - x) <= 4:
            return True
    return False


def swim_chest(row, col):
    """Ouvrir un coffre de l'autre coté de l'eau (par en dessous)."""
    swim_to(row + 1, col)
    g.w(30)
    g.hold('up', 10)
    g.press('a', 60)
    g.text_through(10)
    g.w(60)
    return g.tile(row * 16 + col) == 0xf0


def dive():
    """B en nageant sur l'eau profonde : on plonge (à l'étage du dessous)."""
    g.press('b', 10)
    g.w(120)
    g.settled()
    g.w(30)


g.level(3, 'Donjon')
g.m[INV_A], g.m[INV_B] = 0x05, 0x00   # l'épée sur A ; B ne sert qu'à plonger
check(g.where() == (5, 0x44), "l'entrée du Récif Murmurant (5:44)")
check(g.wait_text(200), 'le nom du donjon')
shoot('r01_entree', "L'entrée")
g.text_through()
# Marine n'est pas là : Select maintenu ne la fait pas parler
g.hold('select', 70)
check(not g.wait_text(60), 'Select maintenu : Marine ne répond pas (elle attend dehors)')
g.text_through()

check(door('up', (5, 0x3f)), 'le hall (5:3f)')
g.clear_enemies()
check(door('left', (5, 0x3e)), "à l'ouest du hall (5:3e)")
g.clear_enemies()
g.w(120)
g.stand(5, 7)
g.w(60)
check(g.small_keys(3) == 1, 'la petite clé 1 (%d)' % g.small_keys(3))
shoot('r02_cle', 'La petite clé 1')
check(door('up', (5, 0x3b)), 'le bassin profond (5:3b)')
g.clear_enemies()
check(door('left', (5, 0x3a), True), "à l'ouest : la boussole (5:3a)")
g.clear_enemies()
full_life()   # (les gelées ont mordu)
check(g.open_chest(5, 3), 'coffre ouvert : la boussole')
check(door('right', (5, 0x3b)), 'retour au bassin')

# La porte à clé du nord de 3b : Vire
check(door('up', (5, 0x37)), 'la porte à clé mène à Vire (5:37)')
g.stand(5, 7)   # Vire apparaît quand Link s'avance au milieu
check(g.wait_text(200), 'Vire parle')
shoot('r03_vire', 'Vire')
g.text_through()
full_life()
check(bool(g.enemies(ENEMY_VIRE)), 'Vire est là')
for _ in range(4):
    g.clear_enemies()
    g.text_through()
g.w(200)
g.text_through()
check(not g.enemies(ENEMY_VIRE), 'Vire est battu')
check(g.open_chest(5, 7), 'le coffre apparaît : les Écailles de Sirène')
check(obtained(TREASURE_MERMAID_SUIT), 'les Écailles de Sirène')
shoot('r04_ecailles', 'Les Écailles de Sirène')

# La plongée : le bassin de 3b -> 30 -> 2e -> 35 -> on remonte dans 3c
check(door('down', (5, 0x3b)), 'retour au bassin')
g.stand(5, 4)
g.goto(0x78, None)
g.w(30)
dive()
check(g.where() == (5, 0x30), 'on plonge : sous le bassin (5:30)')
shoot('r05_plongee', 'Sous l\'eau')
check(door('right', (5, 0x2e)), 'le couloir sous l\'antichambre (5:2e)')
g.clear_enemies()
check(door('right', (5, 0x35)), 'sous le bassin de l\'est (5:35)')
g.clear_enemies()
swim_to(2, 12)
dive()
check(g.where() == (5, 0x3c), 'on remonte dans le bassin de l\'est (5:3c)')
swim_to(5, 12)

g.clear_enemies()
check(door('right', (5, 0x3d)), "à l'est (5:3d)")
g.clear_enemies()
check(swim_chest(5, 11), 'coffre ouvert : la petite clé 2')
check(g.small_keys(3) == 1, 'la petite clé 2')
check(door('left', (5, 0x3c)), 'retour au bassin de l\'est')
check(door('up', (5, 0x39)), 'le lobe droit : les coquillages-échos (5:39)')
# La première fois, ce que sont ces coquillages (TX_5b65)
check(g.wait_text(120), 'les coquillages-échos expliqués (la première fois)')
g.w(60)
shoot('r06_coquillages', 'Les coquillages-échos')
g.text_through()

# Le grand coquillage (ligne 2, colonne 7) chante l'ordre : Dimitri (milieu), Moosh (droite),
# Ricky (gauche). Link touche chaque coquillage par en dessous (A)
g.m[INV_A] = 0x00


def touch(row, col):
    g.stand(row + 1, col, y_first=True)
    g.face('up')
    g.press('a', 20)


touch(2, 7)
g.w(300)
for col in (7, 11, 3):
    touch(5, col)
    g.w(120)
g.w(120)
check(g.tile(0x8b) == 0xf1, 'dans le bon ordre : le coffre apparaît')
check(g.open_chest(8, 11), 'coffre ouvert : la clé du boss')
check(bool(g.m[BOSS_KEYS] & 0x08), 'la clé du boss')
g.m[INV_A] = 0x05

# Retour : on replonge dans 3c, 35 -> 2e -> 30, on remonte dans 3b
check(door('down', (5, 0x3c)), 'retour au bassin de l\'est')
g.stand(5, 12)
g.goto(0x28, None)
dive()
check(g.where() == (5, 0x35), 'on replonge (5:35)')
g.stand(5, 2)
check(door('left', (5, 0x2e)) and door('left', (5, 0x30)), 'retour sous le bassin profond')
swim_to(8, 3)
dive()
check(g.where() == (5, 0x3b), 'on remonte dans le bassin profond (5:3b)')
full_life()
swim_to(5, 7)
check(door('down', (5, 0x3e)) and door('right', (5, 0x3f)), 'retour au hall')

# La carte, à l'est du hall
g.route((2, 2), (2, 12))   # le bassin et la statue du milieu : par le haut
check(door('right', (5, 0x40)), "à l'est du hall (5:40)")
g.clear_enemies()
check(g.open_chest(2, 11), 'coffre ouvert : la carte')
check(door('left', (5, 0x3f)), 'retour au hall')
g.clear_enemies()   # les méduses du hall sont revenues
full_life()

# La porte à clé du nord du hall : l'antichambre, puis la porte du boss
g.route((2, 12), (2, 7))
check(door('up', (5, 0x38)), "la porte à clé mène à l'antichambre (5:38)")
shoot('r07_antichambre', "L'antichambre")
check(door('up', (5, 0x36)), 'la porte du boss : la Murène du Silence (5:36)')
g.w(120)
g.text_through()
shoot('r08_murene', 'La Murène du Silence')
check(bool(g.enemies(ENEMY_OCTOGON)), 'Octogon est là')
for _ in range(6):
    full_life()
    g.clear_enemies()
    g.text_through()
g.w(300)
g.text_through()
check(not g.enemies(ENEMY_OCTOGON), 'la Murène est battue')
check(g.room_flags(5, 0x36) & 0x80, 'drapeau de sa salle ($80)')
g.w(200)
shoot('r09_essence', "L'essence")
check(any(g.m[h * 256 + 0x40] and g.m[h * 256 + 0x41] == INTERAC_ESSENCE for h in range(0xd2, 0xe0)),
      "l'essence apparaît")
# Prendre l'essence (sur la plate-forme, ligne 4, colonne 7)
# (en passant, le réceptacle de cœur, juste en dessous)
for _ in range(8):
    if g.where() != (5, 0x36):
        break
    g.goto(None, 0x78)
    g.goto(0x48, None)
    g.w(30)
    g.text_through()
    g.press('a', 30)
g.w(200)
g.settled()
check(bool(g.m[ESSENCES] & 0x04), "l'essence du Récif (le troisième couplet)")
check(g.where() in ((1, 0x35), (3, 0x23)), 'retour sur la plage des bouteilles (1:35), puis chez Gaspard')
check(g.wait_text(300), 'Marine attendait')
shoot('r10_marine', 'Marine attendait')
for _ in range(6):
    g.text_through()
    g.w(120)
check(g.where() == (3, 0x23), "chez Héloïse et Gaspard (3:23)")
shoot('r11_maison', 'Héloïse se souvient')
for _ in range(8):
    g.text_through()
    g.w(120)
check(g.global_flag(0x53), 'Mont-Braise repéré (GLOBALFLAG_BALLADE_ISLAND4)')

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
