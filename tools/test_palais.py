"""Test du Palais Givré (donjon 7), joué de bout en bout depuis le menu de test caché (7.
Donjon). Chaque énigme est résolue comme un joueur :
- 56 la glace : on glisse tout droit dans l'allée sûre ;
- 58 un gouffre de trois cases : la Cape de Roc ;
- 5b deux torches au-delà d'un gouffre, des piliers en face : deux graines en biais (petite clé 1) ;
- 5c le champ de glace : on glisse d'un pilier à l'autre jusqu'au coffre (la carte) ;
- 5a le Chevalier Gelé ; la Clochette d'Aube ;
- 57 et 5d les gardes endormis debout : la Clochette les réveille ;
- 60 le cristal sur l'îlot, un pilier en face : une graine en biais (petite clé 2) ;
- 61 le Grappin-Écho jusqu'à l'îlot (la boussole) ; 5f deux torches entourées de trous (la clé
  du boss) ; 62 l'allée de glace ; la porte du boss ; Givrolin ; l'essence ; la fin du chapitre 7.

Seule triche : le mini-boss et le boss sont retirés (leur vie mise à zéro), et Link garde sa vie
pleine.

Usage : python tools/test_palais.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import (BOSS_KEYS, ESSENCES, HEALTH, INV_A, INV_B, MAX_HEALTH, TEXT_ACTIVE, TREASURES,
                        Game, sheet)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_FLUTE, TREASURE_SHOOTER, TREASURE_SWITCH_HOOK, TREASURE_FEATHER = 0x0e, 0x0f, 0x0a, 0x17
DISABLED_OBJECTS = 0xcc8a   # wDisabledObjects
TORCHES_LIT = 0xcc8f        # wNumTorchesLit
GLOBALFLAG_BALLADE_ISLAND8 = 0x57
errors, shots = [], []
g = Game()


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe(), 'clés', g.small_keys(7))
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def shoot(name, label):
    path = os.path.join(OUT, name + '.png')
    g.shot(path)
    shots.append((path, label))


def full_life():
    g.m[HEALTH] = g.m[MAX_HEALTH]


def obtained(t):
    return bool(g.m[TREASURES + t // 8] & (1 << (t % 8)))


def at(row, col, tol=8):
    y, x = g.link()
    return abs(y - (row * 16 + 8)) <= tol and abs(x - (col * 16 + 8)) <= tol


def wait_intro():
    """La présentation d'un boss gèle Link (wDisabledObjects) : la laisser finir, textes compris."""
    for _ in range(60):
        g.text_through()
        g.w(10)
        if not g.m[DISABLED_OBJECTS] and not g.m[TEXT_ACTIVE]:
            return True
    return False


def jump(row, col, direction, double=False, back=0, run=2):
    """Depuis (row, col), sauter vers direction (Plume de Roc ; double : la Cape)."""
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


def shooter(facing, turn=None, wait=60):
    """Le Lance-Graines : tourné vers facing ; turn ('left' / 'right') : un huitième de tour en
    tenant B ; on lâche B : la graine part."""
    g.m[INV_B] = TREASURE_SHOOTER
    g.face(facing)
    g.pb.button_press('b')
    g.w(10)
    if turn:
        g.pb.button_press(turn)
        g.w(16)
        g.pb.button_release(turn)
    g.pb.button_release('b')
    g.w(wait)


def bell():
    """La Clochette d'Aube (la flûte d'Ages) : on en joue."""
    g.m[INV_B] = TREASURE_FLUTE
    g.press('b', 10)
    for _ in range(40):
        g.w(10)
        if g.m[TEXT_ACTIVE]:
            return True
    return False


def hook(facing):
    g.m[INV_B] = TREASURE_SWITCH_HOOK
    g.face(facing)
    g.press('b', 10)
    g.w(120)    # le diamant reprend sa place ~70 images après


def chest_up(row, col):
    """Le coffre (row, col), Link juste en dessous : on l'ouvre."""
    g.stand(row + 1, col)
    g.hold('up', 10)
    g.press('a', 60)
    g.text_through(10)
    g.w(40)
    return g.tile(row * 16 + col) == 0xf0


def key_door(direction, room):
    g.hold(direction, 40)
    g.w(40)
    return g.go(direction, room)


def slide(direction, limit=300):
    """Sur la glace : pousser dans une direction jusqu'à ce que Link ne bouge plus (un pilier, un
    mur), puis lâcher et attendre l'arrêt."""
    g.pb.button_press(direction)
    last, still = None, 0
    for _ in range(limit // 4):
        g.w(4)
        pos = g.link()
        still = still + 1 if pos == last else 0
        last = pos
        if still >= 3:
            break
    g.pb.button_release(direction)
    g.w(40)


# --- L'entrée
g.level(7, 'Donjon')
g.m[INV_A], g.m[INV_B] = 0x05, TREASURE_FEATHER
full_life()
check(g.where() == (4, 0x55), "l'entrée du Palais Givré (4:55)")
check(g.wait_text(200), 'le nom du donjon')
g.w(30)
shoot('p01_entree', "L'entrée : Niveau 7, Palais Givré")
for _ in range(4):
    if not g.m[TEXT_ACTIVE]:
        break
    g.press('a', 20)
check(g.wait_text(120), 'Marine : ça glisse')
g.text_through()
g.route((7, 7))
check(g.go('up', (4, 0x56)), 'la glace (4:56)')

# --- 56 : la glace, l'allée sûre (colonne 7)
g.stand(9, 7)
check(g.go('up', (4, 0x57)), 'glissé tout droit : le cœur du flocon (4:57)')
shoot('p02_coeur', 'Le cœur : un garde dort debout')

# --- 57 : le garde endormi devant la porte du nord ; on va à l'ouest
g.route((5, 7))
g.hold('up', 60)
check(g.where() == (4, 0x57) and g.link()[0] > 0x18, 'le garde endormi bouche la porte du nord')
g.route((5, 7), (5, 1))
check(g.go('left', (4, 0x58)), 'le gouffre de trois cases (4:58)')

# --- 58 : la Cape de Roc
jump(5, 9, 'left', double=True, back=6)
check(g.link()[1] < 6 * 16, 'la Cape : le gouffre de trois cases')
g.route((5, 1))
check(g.go('left', (4, 0x59)), "le carrefour de l'ouest (4:59)")

# --- 5b : deux torches, deux graines en biais (la petite clé 1)
g.route((3, 13), (3, 7), (1, 7))
check(g.go('up', (4, 0x5b)), 'les torches (4:5b)')
g.stand(9, 10)
shooter('up', 'left')
g.stand(9, 4)
shooter('up', 'right')
check(g.m[TORCHES_LIT] == 2, 'deux graines en biais : les deux torches (%d)' % g.m[TORCHES_LIT])
g.w(60)
check(g.tile(0x87) == 0xf1, 'le coffre apparaît')
shoot('p03_torches', 'Deux torches allumées en biais')
check(chest_up(8, 7), 'le coffre de la petite clé 1')
check(g.small_keys(7) == 1, 'la petite clé 1 (%d)' % g.small_keys(7))
g.route((9, 7))
check(g.go('down', (4, 0x59)), 'retour au carrefour')

# --- 5c : le champ de glace (la carte)
g.route((3, 7), (3, 2), (7, 2), (7, 7), (9, 7))
check(g.go('down', (4, 0x5c)), 'le champ de glace (4:5c)')
slide('down')
check(at(8, 7), 'glissé jusqu\'au pilier (8,7)')
slide('left')
check(at(8, 1, 12) or at(8, 2, 12), "glissé jusqu'à l'estrade")
check(chest_up(7, 2), 'le coffre de la carte')
shoot('p04_carte', 'Le champ de glace : la carte')
slide('right')
slide('up')
slide('left')
check(at(1, 7, 10), 'glissé jusqu\'au pilier du haut (1,7)')
check(g.go('up', (4, 0x59)), 'retour au carrefour')

# --- 5a : le Chevalier Gelé ; la Clochette d'Aube
g.route((5, 2), (5, 1))
check(g.go('left', (4, 0x5a)), 'le Chevalier Gelé (4:5a)')
check(wait_intro(), 'le Chevalier Gelé se présente')
shoot('p05_chevalier', 'Le Chevalier Gelé')
g.clear_enemies()
g.w(240)
full_life()
check(g.tile(0x5e) != 0x79, 'le Chevalier Gelé battu : la porte rouverte')
check(chest_up(3, 7), "le coffre de la Clochette d'Aube")
check(obtained(TREASURE_FLUTE), "la Clochette d'Aube")
shoot('p06_clochette', "La Clochette d'Aube")
g.route((5, 13))
check(g.go('right', (4, 0x59)), 'retour au carrefour')
g.route((5, 13))
check(g.go('right', (4, 0x58)), 'retour au gouffre')
jump(5, 5, 'right', double=True, back=6)
g.route((5, 13))
check(g.go('right', (4, 0x57)), 'retour au cœur')

# --- 57 : la Clochette réveille le garde du nord
g.route((5, 7), (3, 7))
check(bell(), 'la Clochette : le garde se réveille')
g.w(30)
shoot('p07_garde', 'La Clochette réveille le garde')
g.text_through()
g.w(60)
# --- l'est : la porte à clé (petite clé 1)
g.route((5, 13))
check(key_door('right', (4, 0x5d)), 'la porte à clé : le couloir (4:5d)')
g.stand(5, 5)
check(bell(), 'la Clochette : le garde du couloir se réveille')
g.text_through()
g.w(60)
g.route((5, 13))
check(g.go('right', (4, 0x5e)), "le carrefour de l'est (4:5e)")

# --- 60 : le cristal en biais (la petite clé 2)
g.route((3, 1), (3, 7), (1, 7))
check(g.go('up', (4, 0x60)), 'le cristal (4:60)')
g.stand(7, 3)
shooter('up', 'right')
check(g.tile(0x87) == 0xf1, 'une graine en biais : le cristal, le coffre apparaît')
shoot('p08_cristal', 'Le cristal frappé en biais')
g.route((9, 3), (9, 7))     # sous le pilier
check(chest_up(8, 7), 'le coffre du cristal')
check(g.small_keys(7) == 1, 'la petite clé 2')
g.route((9, 7))
check(g.go('down', (4, 0x5e)), 'retour au carrefour')

# --- 61 : le Grappin-Écho (la boussole)
g.route((3, 7), (3, 13), (7, 13), (7, 7), (9, 7))
check(g.go('down', (4, 0x61)), "l'îlot de la boussole (4:61)")
g.route((2, 7), (2, 6))
hook('down')
check(at(7, 6), "le Grappin-Écho : sur l'îlot")
check(chest_up(6, 7), 'le coffre de la boussole')
shoot('p09_boussole', "L'îlot : la boussole")
g.stand(7, 6)
hook('up')
check(at(2, 6), 'le Grappin-Écho : retour')
g.route((1, 7))
check(g.go('up', (4, 0x5e)), 'retour au carrefour')

# --- 5f : deux torches entourées de trous (la clé du boss)
g.route((7, 7), (7, 13), (5, 13))
check(key_door('right', (4, 0x5f)), 'la porte à clé (petite clé 2) : les torches entourées de trous (4:5f)')
check(g.small_keys(7) == 0, 'la petite clé 2 a servi')
g.stand(2, 4)
shooter('right')
g.stand(8, 4)
shooter('right')
check(g.m[TORCHES_LIT] == 2, 'les deux torches (%d)' % g.m[TORCHES_LIT])
g.w(60)
check(chest_up(5, 3), 'le coffre de la clé du boss')
check(bool(g.m[BOSS_KEYS] & 0x80), 'la clé du boss')
shoot('p10_cle_boss', 'La clé du boss')
g.route((5, 1))
check(g.go('left', (4, 0x5e)), 'retour au carrefour')
g.route((3, 13), (3, 1), (5, 1))
check(g.go('left', (4, 0x5d)), 'retour au couloir')
g.route((5, 1))
check(g.go('left', (4, 0x57)), 'retour au cœur')

# --- 62 : l'allée de glace ; la porte à clé (petite clé 2)
g.route((5, 7), (1, 7))
check(g.go('up', (4, 0x62)), "l'allée de glace (4:62)")
g.stand(9, 7)
g.hold('up', 120)
check(key_door('up', (4, 0x63)), "la porte du boss (la clé du boss) : l'antichambre (4:63)")
g.route((1, 7))
check(key_door('up', (4, 0x64)), 'la porte du boss : Givrolin (4:64)')

# --- 64 : Givrolin
check(g.wait_text(200), 'Givrolin menace, Marine répond')
g.w(40)
shoot('p11_givrolin', 'Givrolin')
check(wait_intro(), 'Givrolin se présente')
full_life()
g.w(30)
shoot('p12_combat', 'Givrolin (le combat)')
g.m[0xc6b0], g.m[0xc6b9] = 0, 0       # wNumBombs, wNumEmberSeeds : plus rien


def drops():
    return [g.m[(s << 8) + 0xc2] & 0x7f for s in range(0xd0, 0xe0)
            if g.m[(s << 8) + 0xc0] and g.m[(s << 8) + 0xc1] == 0x01]


g.w(120)
check(not drops(), 'Givrolin : rien ne traîne au sol (cachés dans les fougères)')
for x, what in ((0x18, 'des bombes'), (0xd8, 'des graines')):
    g.m[0xd00b], g.m[0xd00d] = 0x38, x
    g.face('up')
    g.press('a', 20)
    g.w(30)
g.w(20)
check(all(g.tile(p) == t for p, t in ((0x11, 0x20), (0x12, 0x21), (0x21, 0x20), (0x22, 0x21),
                                     (0x1c, 0x20), (0x1d, 0x21), (0x2c, 0x20), (0x2d, 0x21))),
      'les fougères repoussent aussitôt coupées')
# (sortis sous les pieds de Link : ramassés aussitôt)
got = (g.m[0xc6b0], g.m[0xc6b9])
check((4 in drops() or got[0]) and (5 in drops() or got[1]),
      'Givrolin : un coup d\'épée dans chaque fougère, des bombes et des graines (au sol %s, en poche %s)' % (drops(), got))
# Le Bracelet des Âmes n'aspire pas un boss (Givrolin vidé ne renvoyait plus ses bras : bloqué)
rr = next(s << 8 | 0x80 for s in range(0xd0, 0xe0) if g.m[(s << 8) + 0x80] and g.m[(s << 8) + 0x81] == 0x07)
hp = g.m[rr + 0x29]
g.m[0xc6c5] |= 0x02
g.m[0xd00b], g.m[0xd00d] = g.m[rr + 0x0b] + 20, g.m[rr + 0x0d]
g.face('up')
g.hold('a', 70)
g.w(20)
check(g.m[rr + 0x29] == hp, 'le tourbillon du Bracelet laisse Givrolin entier (%d -> %d)' % (hp, g.m[rr + 0x29]))
# Givrolin a quatre formes (l'épée, les bombes, le Lance-Graines, le bracelet) ; sa vie ne compte
# pas : on le met à la fin de la dernière (état $0c, sous-état 4, var35 = 3 coups : enemyBoss_dead)
for _ in range(12):
    if g.m[0xc900 + 0x64] & 0x80:      # wGroup4RoomFlags : le boss est vaincu
        break
    for b in g.enemies():
        if g.m[b + 1] == 0x07:         # ENEMY_RAMROCK
            g.m[b + 4], g.m[b + 5], g.m[b + 0x35] = 0x0c, 0x04, 0x03
        elif g.m[b + 1] == 0x05:       # ses mains (de la première forme, sautée ici)
            g.m[b] = 0
            g.m[0xcdd1] = max(0, g.m[0xcdd1] - 1)    # wNumEnemies
    full_life()
    g.text_through()
    g.w(60)
check(bool(g.m[0xc900 + 0x64] & 0x80), 'Givrolin vaincu')
g.w(200)
full_life()
g.route((6, 7))
g.w(60)
g.text_through()
g.w(120)
for _ in range(8):
    if g.where() != (4, 0x64):
        break
    g.route((5, 7), (4, 7))
    g.hold('up', 40)
    g.w(30)
    if g.m[TEXT_ACTIVE] and g.where() == (4, 0x64) and not any('couplet' in l for _, l in shots):
        shoot('p13_couplet', 'Le septième couplet')
    g.text_through()
    g.press('a', 30)
g.w(200)
g.settled()
check(bool(g.m[ESSENCES] & 0x40), "l'essence (le septième couplet)")
check(g.where() == (1, 0xb1), 'retour au village gelé (1:b1)')
check(g.wait_text(400), 'la fin du chapitre 7 : tout le monde se réveille')
g.w(40)
shoot('p14_reveil', 'Tout le monde se réveille')
for _ in range(10):
    g.text_through()
    g.w(120)
check(g.global_flag(GLOBALFLAG_BALLADE_ISLAND8), "l'Œil de l'Insomnis repéré")

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
