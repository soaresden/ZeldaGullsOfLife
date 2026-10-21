"""Test de l'île 6, le Nid des Vents, par le menu de test caché (tools/debug_menu.py).

- arrivée au courant ascendant (Marine parle) ; le Bateau-Rondin à deux pages (6 îles : « Suite »,
  les Échos, puis retour au Nid) ; tomber dans le ciel ramène sur le dernier sol ;
- la prairie suspendue : le Rito égaré ; les moulins arrêtés (un meunier) ; le village : Zéphyr et
  ses ailes ; la Lanterne : dans le Songe, Zéphyr vole (« les nuages tiennent ») ;
- le pont de nuages : des trous dans le Réel ; dans le Songe, les planches tiennent : on passe
  avant que le noctambule réveille Link, et on revient au Réel de l'autre coté ;
- le Nid : Mère Plume donne la Plume de Roc ; retour : on saute les trous du pont dans le Réel.

Usage : python tools/test_nid.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import HEALTH, INV_A, INV_B, MAX_HEALTH, TREASURES, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
TREASURE_HARP, TREASURE_FEATHER = 0x11, 0x17
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
    g.hold(facing, 8)
    g.press('a', 20)
    ok = g.wait_text(60)
    g.w(30)
    return ok


def door(g, direction, room):
    row, col = {'up': (1, 4), 'down': (6, 4), 'left': (4, 1), 'right': (4, 8)}[direction]
    g.stand(row, col, y_first=direction in ('left', 'right'))
    return g.go(direction, room)


def lantern(g, group):
    g.m[INV_B] = TREASURE_HARP
    g.press('b', 10)
    g.wait_until(lambda: g.where()[0] == group and g.m[0xd004] == 0x0a, 600)   # le rayon de lumière
    g.wait_until(lambda: g.m[0xd004] == 0x01, 600)                              # Link a la main


def raft(g, *options):
    """Le Bateau-Rondin (y $68, x $58) : Link au bout des planches (6, 4), vers l'est."""
    g.stand(6, 4)
    g.face('right')
    g.press('a', 20)
    for opt, count in options:
        g.choose(opt, count)
    g.w(30)
    g.settled()
    g.w(60)


g = Game()
g.level(6, 'Plage')
g.m[INV_A], g.m[INV_B] = 0x05, TREASURE_HARP
check(g.where() == (1, 0x75), 'le courant ascendant du Nid des Vents (1:75)', g)
check(g.wait_text(200), 'Marine parle en arrivant', g)
g.w(60)
shoot(g, 'n01_arrivee', 'Arrivée : le courant ascendant')
g.text_through()

# Le Bateau-Rondin : 6 îles, la deuxième page (Mont-Braise, les Échos, le Nid)
raft(g, (3, 4), (1, 3))
check(g.where() == (1, 0x70), 'le Bateau-Rondin : « Suite », les Échos', g)
g.text_through()
raft(g, (3, 4), (2, 3))
check(g.where() == (1, 0x75), 'et retour au Nid des Vents', g)
g.text_through()

# Tomber dans le ciel : retour sur le dernier sol
g.m[HEALTH] = g.m[MAX_HEALTH]
h0 = g.m[HEALTH]
g.stand(5, 5)
g.hold('down', 60)
g.w(200)
g.settled()
check(g.where() == (1, 0x75) and g.m[HEALTH] < h0, 'tomber dans le ciel : retour au sol (un peu de vie en moins)', g)
g.m[HEALTH] = g.m[MAX_HEALTH]

check(door(g, 'right', (1, 0x76)), 'la prairie suspendue (1:76)', g)
check(talk(g, 4, 7), 'le Rito égaré', g)
shoot(g, 'n02_rito', 'Le Rito égaré')
g.text_through()
check(door(g, 'up', (1, 0x66)), 'les moulins à vent (1:66)', g)
g.route((4, 4), (4, 1))   # autour : le ciel
check(talk(g, 3, 1), 'un meunier', g)
shoot(g, 'n03_meunier', 'Les moulins arrêtés')
g.text_through()
check(door(g, 'right', (1, 0x67)), 'le village des plumes (1:67)', g)
check(talk(g, 4, 7, 'down'), 'Zéphyr', g)
shoot(g, 'n04_zephyr', 'Zéphyr et ses ailes')
g.text_through()
g.stand(3, 7)   # pas collé à Zéphyr : dans le Songe, il est au même endroit (Link serait renvoyé)
lantern(g, 0)
check(g.where() == (0, 0x67), 'la Lanterne : le Songe (0:67)', g)
check(talk(g, 4, 7, 'down'), 'Zéphyr dans le Songe', g)
shoot(g, 'n05_zephyr_songe', 'Dans le Songe, Zéphyr vole')
g.text_through()
g.stand(3, 7)
lantern(g, 1)
check(g.where() == (1, 0x67), 'retour au Réel', g)

# Le pont de nuages : des trous dans le Réel ; dans le Songe, les planches tiennent
check(door(g, 'up', (1, 0x57)), 'le pont de nuages (1:57)', g)
check(g.wait_text(200), 'Marine : dans le Songe, rien ne tombe', g)
g.text_through()
shoot(g, 'n06_pont', 'Le pont de nuages (Réel)')
g.route((5, 4), (5, 3), (4, 3))
# Pas de temps à perdre : le noctambule réveille Link ~190 images après qu'il a la main
g.m[INV_B] = TREASURE_HARP
g.press('b', 10)
g.wait_until(lambda: g.where()[0] == 0 and g.m[0xd004] == 0x0a, 600)   # le rayon de lumière
g.wait_until(lambda: g.m[0xd004] == 0x01, 600)                          # Link a la main
check(g.where() == (0, 0x57), 'le Songe : les planches tiennent', g)
g.pb.button_press('right')
g.wait_until(lambda: g.link()[1] >= 9 * 16 + 4, 300)
g.pb.button_release('right')
shoot(g, 'n07_pont_songe', 'Le pont de nuages (Songe)')
g.stand(3, 9)
lantern(g, 1)
check(g.where() == (1, 0x57) and g.link()[1] > 0x80, "revenu au Réel de l'autre coté du pont", g)
check(door(g, 'right', (1, 0x58)), 'la corniche (1:58)', g)
check(door(g, 'up', (1, 0x48)), 'le Nid (1:48)', g)
g.route((5, 4), (5, 6))
check(talk(g, 5, 6), 'Mère Plume', g)
shoot(g, 'n08_mere_plume', 'Mère Plume')
g.text_through()
g.w(60)
g.text_through()
check(obtained(g, TREASURE_FEATHER), 'la Plume de Roc', g)

# Retour par le pont du Réel : sauter les trous avec la Plume de Roc
check(door(g, 'down', (1, 0x58)), 'retour à la corniche', g)
check(door(g, 'left', (1, 0x57)), 'retour au pont de nuages', g)
g.m[INV_B] = TREASURE_FEATHER
g.stand(4, 8, y_first=True)
for col in (6, 4):
    g.pb.button_press('left')
    g.w(2)
    g.press('b', 4)
    g.w(30)
    g.pb.button_release('left')
    g.w(10)
    g.goto(None, col * 16 + 8)
check(g.where() == (1, 0x57) and g.link()[1] < 0x50, 'les trous sautés avec la Plume de Roc', g)
shoot(g, 'n09_saut', 'La Plume de Roc : les trous du pont')
check(door(g, 'down', (1, 0x67)), 'retour au village', g)

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
