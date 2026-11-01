"""Test du Sablier (idée de Denis : « un sablier oui, et les dégâts en crescendo ») :
- la Lune qui tombe (1F, 5:c1) donne le Sablier : c'est dans tools/test_prison.py (le donjon entier) ;
- 5F, Dark Link (5:c4), par le menu de test (île 8, M-boss) : on retourne le Sablier, les ennemis
  sont figés (wDisabledObjects) et ne
  blessent pas Link ; on frappe un Link de l'ombre plusieurs fois : les coups sont comptés ;
- à la fin, les coups éclatent : la vie de l'ennemi baisse en plus (1 + 2 + ... + n-1), le temps
  repart ; le Sablier ne se retourne plus tant que le sable n'est pas retombé.
Usage : python tools/test_sablier.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import HEALTH, LINK_X, LINK_Y, INV_A, INV_B, MAX_HEALTH, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_SABLIER = 0x14
DISABLED_OBJECTS = 0xcc8a
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


def sablier():
    """L'interaction du Sablier retourné (INTERAC_BALLADE_OBJECT $33), ou None."""
    for d in range(0xd0, 0xe0):
        base = (d << 8) + 0x40
        if g.m[base] and g.m[base + 1] == 0xed and g.m[base + 2] == 0x33:
            return base
    return None


# --- 5F, Dark Link : le temps arrêté (le menu de test donne le Sablier, jalon 35)
g.level(8, 'M-boss')
g.m[INV_A] = 0x05
g.m[HEALTH] = g.m[MAX_HEALTH]
check(g.has(TREASURE_SABLIER), 'le Sablier (TREASURE_14)')
g.route((5, 7), (5, 1))
check(g.go('left', (5, 0xc4)), '5F : Dark Link (5:c4)')
g.w(60)
for _ in range(60):
    g.text_through()
    g.w(10)
    if not g.m[DISABLED_OBJECTS] and not g.m[TEXT_ACTIVE]:
        break
g.w(30)
foes = g.enemies()
check(len(foes) > 0, 'des Link de l\'ombre (%d)' % len(foes))
target = foes[0]
for b in foes:
    print('   ennemi %02x vie %d en %02x,%02x' % (g.m[b + 1], g.m[b + 0x29], g.m[b + 0x0b], g.m[b + 0x0d]))
g.m[INV_B] = TREASURE_SABLIER
g.press('b', 10)
g.w(20)
check(g.m[DISABLED_OBJECTS] & 0x0c == 0x0c, 'le Sablier retourné : ennemis et tirs figés')
check(sablier() is not None, "l'interaction du Sablier")
pos = (g.m[target + 0x0b], g.m[target + 0x0d])
g.w(30)
check((g.m[target + 0x0b], g.m[target + 0x0d]) == pos, 'un Link de l\'ombre ne bouge plus')
shoot('s02_fige', 'Le temps arrêté : le décor assombri')
life0 = g.m[target + 0x29]
health0 = g.m[HEALTH]
# Link va au contact et frappe (épée en A)
y, x = pos
g.m[LINK_Y], g.m[LINK_X] = y + 14, x
g.w(2)
g.face('up')
for _ in range(4):
    g.press('a', 14)
s = sablier()
hits = g.m[s + 0x30 + (target >> 8) - 0xd0] if s else 0
print('   coups comptés : %d, vie %d -> %d' % (hits, life0, g.m[target + 0x29]))
check(hits >= 2, 'plusieurs coups comptés pendant le temps arrêté (%d)' % hits)
check(g.m[HEALTH] == health0, 'les ennemis figés ne blessent pas Link')
shoot('s03_coups', 'Les coups donnés pendant le temps arrêté')
# la fin : le crescendo
for i in range(400):
    g.w(1)
    if i % 20 == 0 and g.m[0xcc8a] & 0x0c == 0x0c and s and g.m[s + 4] == 2 and len(shots) < 4:
        shoot('s04_crescendo', 'Le crescendo : la terre tremble')
    if not g.m[DISABLED_OBJECTS] & 0x0c:
        break
    before = g.m[target + 0x29]
check(not g.m[DISABLED_OBJECTS] & 0x0c, 'le temps repart')
hits = g.m[s + 0x30 + (target >> 8) - 0xd0]
bonus = hits * (hits - 1) // 2
after = g.m[target + 0x29] if g.m[target] else 0
print('   vie avant l\'éclat %d, après %d (bonus attendu %d)' % (before, after, bonus))
check(after <= max(0, before - bonus), 'les coups éclatent : %d de dégâts en plus' % bonus)
shoot('s05_eclat', "L'éclat final")
g.w(30)
g.press('b', 10)
g.w(10)
check(sablier() is not None and g.m[sablier() + 4] == 3 and not g.m[DISABLED_OBJECTS] & 0x0c,
      'le sable retombe : pas de second retournement tout de suite')
g.w(9 * 60)
check(sablier() is None, 'le sable est retombé (8 secondes)')

sheet(shots, os.path.join(OUT, 'sablier.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
