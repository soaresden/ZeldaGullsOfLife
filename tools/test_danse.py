"""Test du boss du Terrier en rythme (code/ages/balladeTerrier.s, rex : la danse ; Denis, 03/11/2026),
directement dans l'arène (4:d7) avec 16 âmes :

- la machine sort de l'ombre ; Marine explique (TX_5c40) ; Link figé face à elle, les quatre cibles ;
- manche 1 (la Berceuse) jouée parfaitement par le robot : les flèches montent, chaque coup juste
  fait entendre la mélodie (NR51 = $ff), puis elle se tait ; la machine a mal (TX_5c46) ;
- manche 2 ratée exprès (rien n'est joué) : Link perd un cœur, la manche recommence (TX_5c47) ;
- une flèche sur trois ratée : encore gagnée (les deux tiers) ; la mauvaise direction : ratée ;
- les manches 2 à 5 gagnées : elle explose, Link est libre, plus de flèches ni de cibles ;
  le Bracelet des Âmes.

Usage : python tools/test_danse.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import INV_A, INV_B, Game, sheet
from danse_bot import CHARTS_DATA, NR51, now, play_round, ram, rex_var

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SOULS, SOUL_STATE = 0xc6c4, 0xc6c5
HEALTH, MAX_HEALTH = 0xc6aa, 0xc6ab
INTERAC = 0xeb
TEXT = 0xcba0
errors, shots = [], []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def objects(subid):
    return [s for s in range(0xd0, 0xe0)
            if ram(g, (s << 8) + 0x40) and ram(g, (s << 8) + 0x41) == INTERAC and ram(g, (s << 8) + 0x42) == subid]


def shot(name, label):
    p = os.path.join(OUT, name)
    g.shot(p)
    shots.append((p, label))


def to_round(n, name=None, label=None):
    """Les textes (le résultat, puis l'annonce : pendant l'annonce, l'étape vaut déjà 2), jusqu'au
    début de l'avance de la manche n."""
    seen = False
    for _ in range(1500):
        if g.m[TEXT]:
            if rex_var(g, b, 0x32) == 2 and not seen:
                seen = True
                g.w(30)
                if name:
                    shot(name, label)
            g.press('a', 6)
        elif seen and rex_var(g, b, 0x32) == 2:
            break
        else:
            g.w(1)
    check(seen and 5 - rex_var(g, b, 0x30) == n - 1, "la manche %d s'annonce" % n)


g = Game()
g.level(5, 'Ville')
g.m[INV_A], g.m[INV_B] = 0x05, 0x00
g.text_through()
g.m[SOUL_STATE] = 0x01 | 0x08     # le gantelet ; le texte de l'arène déjà dit
g.m[SOULS] = 16
g.warp(4, 0xd7, 0x97)
g.settled()
g.w(30)
check(g.wait_text(200), 'le boss apparaît : Marine')
g.text_through()
boss = objects(0x0c)
check(len(boss) == 1, 'la machine possédée')
b = boss[0]
g.w(60)
check(g.wait_text(200), 'Marine explique la danse (TX_5c40)')
g.w(60)
shot('d01_explique.png', 'Marine explique')
check(ram(g, 0xd00b) == 0x80 and ram(g, 0xd00d) == 0x78, 'Link figé face à la machine')
check(g.m[0xcc8a] & 1 == 1 and g.m[0xcc02] == 1, 'Link et le menu bloqués')
check(len(objects(0x28)) == 1, 'les quatre cibles')
to_round(1, 'd02_manche1.png', 'Manche 1 : la Berceuse')

# Manche 1, parfaite
log = []
hits, judged = play_round(g, b, log=log, shots={420: os.path.join(OUT, 'd03_fleches.png'),
                                                  520: os.path.join(OUT, 'd04_fleches.png')})
shots += [(os.path.join(OUT, 'd03_fleches.png'), 'Les flèches montent'),
          (os.path.join(OUT, 'd04_fleches.png'), 'Les flèches (2)')]
print('     manche 1 : %d/%d' % (hits, judged))
check(judged == len(CHARTS_DATA[0]) and hits == judged, 'manche 1 : toutes justes (%d/%d)' % (hits, judged))
check(log and all(v == 0xff for _, v in log), "chaque coup juste : la mélodie s'entend (NR51 = $ff)")
check(g.wait_text(200), 'la machine a mal (TX_5c46)')
shot('d05_touchee.png', 'Touchée !')
check(rex_var(g, b, 0x30) == 4, 'une manche de moins (4)')
check(not objects(0x27), 'plus de flèches entre deux manches')

# Manche 2, ratée exprès (rien) : un cœur de moins, la manche recommence
to_round(2, 'd05b_manche2.png', 'Manche 2 : la Ballade de la Déesse')
muted = []
for _ in range(400):
    g.w(1)
    if rex_var(g, b, 0x32) == 3 and now(g, b) > 2:   # (le moteur rouvre tout au début du morceau)
        muted.append(g.m[NR51])
check(muted and all(v == 0xff ^ 0x22 for v in muted), 'sans coup juste, la mélodie se tait (NR51 = $dd)')
health = g.m[HEALTH]
hits, judged = play_round(g, b, miss_every=1)
check(hits == 0, 'manche 2 laissée passer : 0/%d' % judged)
check(g.wait_text(200), 'ratée : on recommence (TX_5c47)')
shot('d06_ratee.png', 'Ratée : un cœur de moins')
check(g.m[HEALTH] == health - 4, 'Link perd un cœur (%d -> %d)' % (health, g.m[HEALTH]))
check(rex_var(g, b, 0x30) == 4, 'toujours 4 manches')

# La mauvaise direction : ratée
to_round(2)
hits, judged = play_round(g, b, wrong=True)
check(hits == 0 and rex_var(g, b, 0x30) == 4, 'la mauvaise direction à chaque fois : ratée (%d/%d)' % (hits, judged))
g.m[HEALTH] = g.m[MAX_HEALTH]

# Une flèche sur trois ratée : encore gagnée
to_round(2)
hits, judged = play_round(g, b, miss_every=3)
check(rex_var(g, b, 0x30) == 3, 'une sur trois ratée : gagnée quand même (%d/%d)' % (hits, judged))

# Les manches 3 à 5
names = {3: 'le Chant des Tempêtes', 4: 'la Vallée Gerudo', 5: 'le Château de Lorule'}
for rnd in (3, 4, 5):
    to_round(rnd, 'd%02d_annonce%d.png' % (rnd + 4, rnd), 'Manche %d : %s' % (rnd, names[rnd]))
    p = os.path.join(OUT, 'd%02db_manche%d.png' % (rnd + 4, rnd))
    hits, judged = play_round(g, b, shots={250: p})
    shots.append((p, 'Manche %d' % rnd))
    print('     manche %d : %d/%d' % (rnd, hits, judged))
    check(hits == judged == len(CHARTS_DATA[rnd - 1]), 'manche %d : toutes justes' % rnd)

g.w(20)
check(rex_var(g, b, 0x04) >= 3, 'cinq manches : elle explose')
check(g.m[0xcc8a] & 1 == 0 and g.m[0xcc02] == 0, 'Link libre')
check(not objects(0x27) and not objects(0x28), 'plus de flèches ni de cibles')
g.w(30)
shot('d10_explose.png', 'Elle explose')
for _ in range(400):
    g.w(1)
    if g.m[SOUL_STATE] & 2:
        break
check(g.m[SOUL_STATE] & 2 == 2, 'le gantelet absorbe son âme : le Bracelet des Âmes')
sheet(shots, os.path.join(OUT, 'planche_danse.png'))
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
