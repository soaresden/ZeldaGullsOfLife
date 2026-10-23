"""Test du contre parfait (comme dans Onimusha ; code/ages/balladeParry.s), dans une salle de la
Spirale Céleste avec des Stalfos (4:41) :
- sans rien faire, le Stalfos touche Link : il perd de la vie ;
- même partie, Link sort l'épée (dos à l'ennemi : l'épée ne le touche pas) trois images avant le
  choc : pas de dégâts, le Stalfos meurt d'un coup, Link passe de l'autre coté de l'ennemi ;
- mais seulement une fois que Bulle le lui a appris (la Fosse, GLOBALFLAG_BALLADE_CONTRE $61) ;
- et c'est difficile : huit images avant, c'est trop tôt (BALLADE_PARRY_WINDOW = 6).
L'émulation est la même d'une partie à l'autre : on rejoue la même scène en appuyant au bon moment.
Usage : python tools/test_contre.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, HEALTH, INV_A, MAX_HEALTH, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
PARRY_ARMED = 0xcde4        # wcde3+1 : l'épée est sortie (remis à 0 par le contre)
FLAG_CONTRE = 0x61
errors, shots = [], []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)


def scene(press_at=None, name=None, learned=True):
    """La même scène : Link attend au milieu de 4:41 ; press_at : l'image où il sort l'épée (tourné
    vers le haut, dos au Stalfos qui arrive)."""
    g = Game()
    g.level(6, 'Donjon')
    for _ in range(6):
        g.text_through()
        g.w(20)
    g.m[INV_A] = 0x05
    if learned:
        g.m[GLOBAL_FLAGS + FLAG_CONTRE // 8] |= 1 << (FLAG_CONTRE % 8)
    else:
        g.m[GLOBAL_FLAGS + FLAG_CONTRE // 8] &= ~(1 << (FLAG_CONTRE % 8)) & 0xff
    g.warp(4, 0x41, 0x57)
    g.w(30)
    g.m[HEALTH] = g.m[MAX_HEALTH]
    h0, n0, link0 = g.m[HEALTH], len(g.enemies()), g.link()
    hit = None
    for f in range(600):
        if f == press_at:
            g.pb.button('up', 1)
            g.pb.button('a', 2)
        g.w(1)
        if g.m[HEALTH] < h0:
            hit = f
            break
        if press_at is not None and f > press_at + 90:
            break
    g.w(10)
    if name:
        path = os.path.join(OUT, name + '.png')
        g.shot(path)
        shots.append((path, name))
    res = dict(hit=hit, damage=h0 - g.m[HEALTH], killed=n0 - len(g.enemies()), moved=g.link() != link0,
               armed=g.m[PARRY_ARMED])
    g.stop()
    return res


base = scene(name='sans_contre')
check(base['hit'] is not None and base['damage'] > 0, 'sans rien faire : le Stalfos touche Link (%s)' % base)
r = scene(base['hit'] - 3, learned=False)
check(r['damage'] > 0 and r['killed'] == 0, 'pas encore appris (la Fosse) : pas de contre, Link est touché')
r = scene(base['hit'] - 8)
check(r['armed'] == 1 and not r['moved'], "l'épée sortie 8 images avant : trop tôt, pas de contre (%s)" % r)
r = scene(base['hit'] - 3, 'contre_parfait')
check(r['damage'] == 0, "l'épée sortie 3 images avant : pas de dégâts")
check(r['killed'] == 1, "le Stalfos meurt d'un coup")
check(r['armed'] == 0 and r['moved'], "c'est bien le contre : Link est passé de l'autre coté (%s)" % r)

sheet(shots, os.path.join(OUT, 'planche.png'))
print()
print('Tout est bon.' if not errors else '%d problème(s) : %s' % (len(errors), '; '.join(errors)))
sys.exit(1 if errors else 0)
