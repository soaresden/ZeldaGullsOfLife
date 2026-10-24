"""Test de l'Œil de l'Insomnis (île 8) : le soleil et la lune, par le menu de test caché.

- devant la tour, avec les sept essences : l'Œil reste fermé, Marine dit qu'il faut le soleil et la
  lune ensemble ;
- la vasque du soleil (paupière ouest, 1:c8) : une graine de feu du Lance-Graines l'allume, dans le
  Réel ;
- la vasque de la lune (paupière est, 1:ca) : dans le Réel, la flamme s'éteint (Marine : « dans un
  rêve, peut-être ? ») ; la Lanterne, le Songe (0:ca) : elle s'allume ; Marine : les deux brillent ;
- devant la tour : Marine chante les sept couplets, la porte s'ouvre.

Usage : python tools/test_oeil.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, INV_A, INV_B, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_SHOOTER, TREASURE_HARP = 0x0f, 0x11
errors, shots = [], []


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


def fire(face):
    """Le Lance-Graines (graines de feu) : se tourner, B, tirer droit devant."""
    g.m[INV_B] = TREASURE_SHOOTER
    g.face(face)
    g.pb.button_press('b')
    g.w(10)
    g.pb.button_release('b')
    return g.wait_until(lambda: g.m[TEXT_ACTIVE], 120)


def lantern(group):
    g.m[INV_B] = TREASURE_HARP
    g.press('b', 10)
    g.wait_until(lambda: g.where()[0] == group and g.m[0xd004] == 0x0a, 600)   # le rayon de lumière
    g.wait_until(lambda: g.m[0xd004] == 0x01, 600)                              # Link a la main


def sun():
    return bool(g.room_flags(1, 0xc8) & 0x40)


def moon():
    return bool(g.room_flags(0, 0xca) & 0x40)


g = Game()
g.level(8, 'Ville')
g.m[INV_A] = 0x05
# (Marine a déjà demandé à revenir à l'auberge : sinon sa réplique, dehors, arrive au milieu)
g.m[GLOBAL_FLAGS + 0x64 // 8] |= 1 << (0x64 % 8)
for _ in range(4):
    g.text_through()
    g.w(30)
check(g.where() == (1, 0xc9), 'le parvis de la tour (1:c9)')
g.route((6, 4))
check(g.wait_text(200), "Marine : l'Œil reste fermé, il faut le soleil et la lune")
g.w(60)
shoot('o01_ferme', "L'Œil reste fermé")
g.text_through()
g.w(60)
check(g.tile(0x44) == 0x82, 'la porte de la tour est encore un mur')

# --- La paupière ouest (1:c8) : la vasque du soleil, dans le Réel ---
g.stand(6, 1)
check(g.go('left', (1, 0xc8)), 'la paupière ouest (1:c8)')
g.stand(4, 3)
shoot('o02_soleil_eteint', 'La vasque du soleil (paupière ouest)')
check(fire('right'), 'une graine de feu sur la vasque du soleil : un texte')
g.w(40)
check(sun(), 'le soleil brille (drapeau $40 de 1:c8)')
shoot('o03_soleil', 'Le soleil brille')
g.text_through()

# --- La paupière est (1:ca) : la lune ne s'allume pas dans le Réel ---
g.stand(6, 8)
check(g.go('right', (1, 0xc9)), 'retour au parvis')
g.text_through()
g.stand(6, 8)
check(g.go('right', (1, 0xca)), 'la paupière est (1:ca)')
g.stand(4, 2)
check(fire('right'), 'une graine de feu sur la vasque de la lune (Réel) : Marine parle')
g.w(60)
shoot('o04_lune_reel', 'Dans le Réel, la flamme s\'éteint')
g.text_through()
check(not moon(), 'dans le Réel, la lune ne brille pas')

# --- Le Songe (0:ca) : la lune s'allume ---
lantern(0)
check(g.where() == (0, 0xca), 'la Lanterne : la paupière est dans le Songe (0:ca)')
check(fire('right'), 'une graine de feu sur la vasque de la lune (Songe)')
g.w(60)
check(moon(), 'la lune brille (drapeau $40 de 0:ca)')
shoot('o05_lune_songe', 'Dans le Songe, la lune brille')
g.text_through()
g.text_through()
lantern(1)
check(g.where() == (1, 0xca), 'retour au Réel (1:ca)')
g.w(40)
shoot('o06_lune_reel_allumee', 'La lune brille aussi dans le Réel')

# --- La tour : Marine chante, la porte s'ouvre ---
g.stand(6, 1)
check(g.go('left', (1, 0xc9)), 'le parvis')
g.route((6, 4))
check(g.wait_text(200), 'Marine : sept marques, sept couplets')
g.w(30)
shoot('o07_chante', 'Marine chante les sept couplets')
for _ in range(10):
    g.text_through()
    g.w(30)
check(g.tile(0x44) == 0xdf, 'la porte de la tour est ouverte')
shoot('o08_porte', 'La porte de la tour est ouverte')

sheet(shots, os.path.join(OUT, 'planche.png'))
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
sys.exit(1 if errors else 0)
