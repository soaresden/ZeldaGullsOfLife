"""Test du Songe de Hameau-Grelot (île 2), par le menu de test caché :

- Tic et Tac (1:20) ne savent plus se cacher : leur parler lance le cache-cache ;
- le vieux cerf-volant (1:01) : coincé et muet dans le Réel ; dans le Songe (0:01), il parle et dit
  où sont les jumeaux ;
- les cinq cachettes du Songe (0:10, 0:02, 0:23, 0:01, 0:13), trouvées une à une ;
- le pont-levis : il n'existe que dans le Songe (0:13) ; on traverse, la Lanterne ramène dans le
  Réel sur l'îlot : le coffre du château de sable (50 rubis) ;
- la place est un jeu de l'oie géant dans le Songe (0:11), Marine le remarque ;
- les cinq trouvés : Tic donne un quart de cœur.

Usage : python tools/test_songe_grelot.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, INV_A, INV_B, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_HARP = 0x11
TEXT_INDEX = 0xcba2            # wTextIndex (L, puis H = le groupe)
NOCTAMBULE = 0xcde6            # wBalladeNoctambule (images qui restent dans le Songe)
HEART_PIECES = 0xc6ac          # wNumHeartPieces
FLAG_CACHE = 0x63              # GLOBALFLAG_BALLADE_CACHE
errors = []
shots = []


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


def text_is(index):
    ok = g.m[TEXT_INDEX] == index
    if not ok:
        print('      (texte %02x%02x)' % (g.m[TEXT_INDEX + 1], g.m[TEXT_INDEX]))
    return ok


def found(room):
    """Le nombre de cachettes trouvées, après avoir vérifié celle de room (drapeau $40 du Songe)."""
    g.text_through()
    g.w(20)
    if not g.room_flags(0, room) & 0x40:
        return -1
    return sum(1 for r in (0x10, 0x02, 0x23, 0x01, 0x13) if g.room_flags(0, r) & 0x40)


def say(face, label=None, name=None):
    """Se tourner, A, attendre le texte ; la capture quand il est écrit ; vrai si un texte s'ouvre."""
    g.face(face)
    g.press('a', 10)
    ok = g.wait_text(90)
    if ok and name:
        g.w(70)
        shoot(name, label)
    return ok


def dream(room, pos):
    """Aller dans une salle du Songe (le temps du noctambule repart de zéro : triche du test)."""
    g.m[NOCTAMBULE], g.m[NOCTAMBULE + 1] = 0, 0
    g.warp(0, room, pos)
    g.settled()
    g.w(40)


g = Game()
g.level(2, 'Ville')
g.m[INV_A], g.m[INV_B] = 0x00, TREASURE_HARP
g.text_through()

# --- Tic et Tac, au terrain de jeu (1:20) : Tic (4,4), Tac (4,6) ---
g.warp(1, 0x20, 0x54)
g.settled()
g.stand(5, 4)
check(say('up', 'Tic et Tac ne savent plus se cacher', 'g01_tic'), 'Tic : « On joue à cache-cache ! »')
g.text_through()
check(g.global_flag(FLAG_CACHE), 'le cache-cache commence (GLOBALFLAG_BALLADE_CACHE)')
g.stand(5, 6)
check(say('up') and text_is(0x53), 'Tac parle aussi')
g.text_through()

# --- Le cerf-volant dans le Réel (1:01) : coincé dans l'arbre ---
g.warp(1, 0x01, 0x44)
g.settled()
g.goto(0x48, 0x30)
check(say('up', 'Le vieux cerf-volant, coincé', 'g02_cerf_reel') and text_is(0x57), 'le cerf-volant du Réel ne parle pas')
g.text_through()

# --- Le Songe : la colline (0:01) : le cerf-volant parle ; un jumeau sous son arbre ---
dream(0x01, 0x44)
check(g.where() == (0, 0x01), 'dans le Songe de la colline (0:01)')
g.goto(0x48, 0x30)
check(say('up', 'Dans le Songe, le cerf-volant parle', 'g03_cerf_songe') and text_is(0x59), 'le cerf-volant dit où sont les jumeaux')
g.text_through()
g.goto(0x58, 0x38)
shoot('g04_cachette', 'Un jumeau caché sous l\'arbre')
check(say('left', 'Trouvé !', 'g05_trouve') and found(0x01) == 1, 'trouvé sous l\'arbre (1 sur 5)')
g.text_through()
g.w(30)
check(g.room_flags(0, 0x01) & 0x40, 'la cachette de la colline est trouvée')

# --- Le bois (0:10) : derrière le buisson ---
dream(0x10, 0x44)
g.goto(0x48, 0x08)
g.goto(0x58, 0x08)
check(say('right') and found(0x10) == 2, 'trouvé dans le bois (2 sur 5)')
g.text_through()

# --- Le manège (0:02) : derrière le plateau ---
dream(0x02, 0x54)
g.goto(0x48, 0x48)
check(say('up') and found(0x02) == 3, 'trouvé au manège (3 sur 5)')
g.text_through()

# --- Le jardin des toupies (0:23) : dans les fleurs ---
dream(0x23, 0x33)
g.goto(0x28, 0x38)
check(say('up') and found(0x23) == 4, 'trouvé dans les toupies (4 sur 5)')
g.text_through()

# --- La plage (0:13) : Marine remarque le pont-levis ; on traverse jusqu'à l'îlot ---
dream(0x13, 0x32)
check(g.wait_text(120) and text_is(0x5c), 'Marine : le pont-levis est baissé')
g.w(80)
shoot('g05_pont_levis', 'Le pont-levis, dans le Songe')
g.text_through()
g.route((3, 3), (3, 5), (4, 5), (4, 6))
check(abs(g.link()[0] - 0x48) <= 2 and abs(g.link()[1] - 0x68) <= 2, "sur l'îlot, par le pont-levis (4,6)")
check(say('up', 'La dernière cachette', 'g06_derniere') and found(0x13) == 5, 'trouvé derrière le château : la dernière (5 sur 5)')
g.text_through()

# --- La Lanterne sur l'îlot : le Réel ; le coffre du château de sable ---
g.press('b', 10)
g.wait_until(lambda: g.where() == (1, 0x13), 400)
g.settled()
g.w(150)
check(g.where() == (1, 0x13) and abs(g.link()[1] - 0x68) <= 2, "la Lanterne : dans le Réel, sur l'îlot")
check(g.tile(0x31 + 0x05) == 0xf1, 'le coffre est là (Réel, 3,6)')
shoot('g07_ilot_reel', "Dans le Réel, sur l'îlot")
r0 = g.rupees()
check(g.open_chest(3, 6), 'le coffre du château de sable s\'ouvre')
check(g.rupees() == r0 + 50 or g.rupees() > r0, 'des rubis (%d -> %d)' % (r0, g.rupees()))

# --- La place du Grelot dans le Songe (0:11) : un jeu de l'oie géant ---
dream(0x11, 0x44)
check(g.wait_text(120) and g.room_flags(0, 0x11) & 0x80, 'Marine : un jeu de l\'oie géant')
g.w(80)
shoot('g08_jeu_oie', 'La place, un jeu de l\'oie (Songe)')
g.text_through()
g.w(20)
shoot('g09_jeu_oie_vide', 'Le jeu de l\'oie')

# --- Le cerf-volant, quand tout est trouvé ---
dream(0x01, 0x44)
g.goto(0x48, 0x30)
check(say('up') and text_is(0x5a), 'le cerf-volant : bravo')
g.text_through()

# --- Tic : le quart de cœur ---
g.warp(1, 0x20, 0x54)
g.settled()
hp = g.m[HEART_PIECES]
g.stand(5, 4)
check(say('up') and text_is(0x51), 'Tic : tu nous as trouvés partout')
g.text_through()
g.w(60)
g.text_through()
check(g.m[HEART_PIECES] != hp, 'le quart de cœur de Tic et Tac')
shoot('g10_quart', 'Le quart de cœur')
check(say('up') and text_is(0x52), 'Tic : maintenant on se cache pour de vrai')
g.text_through()
g.stand(5, 6)
check(say('up') and text_is(0x54), 'Tac : le château, c\'était sa cachette')
g.text_through()

sheet(shots, os.path.join(OUT, 'planche.png'))
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
