"""Test de la carte au trésor (code/ages/balladeTresor.s), par le menu de test caché.

- le facteur des bouteilles (la Lagune, 1:35) donne la carte : une croix entre deux rochers, au large
  de l'île des Échos ;
- au rocher de la veuve (1:74), la crique : sans les Écailles de Sirène, Link remonte du chenal au
  bout de 2 secondes et Marine dit qu'il faut rester plus de 10 secondes ;
- avec les Écailles, 10 secondes sous l'eau : un quart de cœur (drapeau $40 de la salle).

Usage : python tools/test_tresor.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, ROOM_FLAGS, TREASURES, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_FLIPPERS, TREASURE_MERMAID_SUIT = 0x2e, 0x4a
HEART_PIECES = 0xc6ac
SWIMMING = 0xcc5d            # wLinkSwimmingState (bit 7 : sous l'eau)
errors = []


def check(ok, what, g=None):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        if g:
            print('     ', g.describe())
            g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def give(g, t, on=True):
    if on:
        g.m[TREASURES + t // 8] |= 1 << (t % 8)
    else:
        g.m[TREASURES + t // 8] &= ~(1 << (t % 8)) & 0xff


def to_channel(g):
    g.warp(1, 0x74, 0x44)
    g.settled()
    g.w(60)
    g.text_through()
    g.goto(None, 0x48)
    g.goto(0x58, None)
    g.goto(0x68, None)
    g.goto(None, 0x48)
    g.w(20)


g = Game()
g.level(5, 'Plage')
g.m[INV_A], g.m[INV_B] = 0x00, 0x00
g.text_through()
give(g, TREASURE_FLIPPERS)

# Le facteur des bouteilles (1:35, y $28 x $68) : la carte
g.warp(1, 0x35, 0x48)
g.settled()
g.w(60)
g.text_through()
g.stand(3, 6)
g.hold('up', 8)
g.press('a', 20)
check(g.wait_text(60), 'le facteur parle (la carte au trésor)', g)
g.shot(os.path.join(OUT, 't01_facteur.png'))
g.text_through()

# Sans les Écailles : Link remonte au bout de 2 secondes, Marine prévient
give(g, TREASURE_MERMAID_SUIT, False)
to_channel(g)
check(g.where() == (1, 0x74) and g.m[0xd00b] & 0xf0 == 0x60, 'Link nage dans le chenal (1:74)', g)
g.press('b', 10)
check(bool(g.m[SWIMMING] & 0x80), 'il plonge', g)
g.shot(os.path.join(OUT, 't02_plonge.png'))
g.w(200)
check(not g.m[SWIMMING] & 0x80, 'sans les Écailles, il remonte', g)
check(g.wait_text(60), 'Marine : plus de 10 secondes !', g)
g.text_through()

# Avec les Écailles : 10 secondes sous l'eau, un quart de cœur
give(g, TREASURE_MERMAID_SUIT)
pieces = g.m[HEART_PIECES]
g.press('b', 10)
g.w(400)
check(bool(g.m[SWIMMING] & 0x80), 'avec les Écailles, il reste sous l\'eau', g)
g.w(260)
g.w(60)
g.shot(os.path.join(OUT, 't03_tresor.png'))
check(bool(g.m[ROOM_FLAGS[1] + 0x74] & 0x40), 'le trésor : drapeau $40 de la salle', g)
for _ in range(6):
    g.w(30)
    g.text_through()
check(g.m[HEART_PIECES] != pieces, 'un quart de cœur (%d -> %d)' % (pieces, g.m[HEART_PIECES]), g)
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
