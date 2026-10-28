"""Test de la fin du jeu et de l'après-jeu (code/ages/balladeFin.s), par le menu de test caché :

- en haut de la Tour (5:cc), l'Insomnis battu : Zelda apparaît, en rêve ; Marine lui chante sa
  chanson ; Zelda s'endort ; fondu : la plage du réveil (1:aa) ;
- l'épilogue : Marine humaine, le générique ; le jeu continue (GLOBALFLAG_BALLADE_FIN) ;
- l'île de Marine : le coquillage appelle Zelda ; la maison ; Marine et le volley (le ballon tombe
  chez Link : point pour Marine ; Link sous le ballon : il le renvoie).

Usage : python tools/test_epilogue.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import GLOBAL_FLAGS, INV_A, INV_B, Game

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
RHYTHM_STAGE = 0xcdec
EPILOGUE = 0xc5ab
VOLLEY_STATE, VOLLEY_SCORE = 0xc5ac, 0xc5ad
FLAG_FIN = 0x5d
INTERAC = 0xeb
errors = []


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        print('     ', g.describe())
        g.shot(os.path.join(OUT, 'rate_%02d.png' % len(errors)))


def objects(subid):
    return [s for s in range(0xd0, 0xe0)
            if g.m[(s << 8) + 0x40] and g.m[(s << 8) + 0x41] == INTERAC and g.m[(s << 8) + 0x42] == subid]


def obj(slot, field):
    return (slot << 8) + 0x40 + field


def follow(shots, until, limit=60):
    """Les textes l'un après l'autre (A) ; une capture du texte dont le numéro est dans shots."""
    seen = []
    for _ in range(limit):
        if g.m[0xcba0]:
            idx = g.m[0xcba2]
            if not seen or seen[-1] != idx:
                seen.append(idx)
                g.w(50)
                if idx in shots:
                    g.shot(os.path.join(OUT, shots[idx] + '.png'))
            g.press('a', 20)
        else:
            g.w(20)
        if until():
            break
    return seen


def flag(f):
    return bool(g.m[GLOBAL_FLAGS + f // 8] & (1 << (f % 8)))


g = Game()
g.level(8, 'Boss')
g.m[INV_A], g.m[INV_B] = 0x00, 0x00
g.text_through()
g.warp(5, 0xcc, 0x97)
g.settled()
g.w(60)
g.text_through()
check(g.where() == (5, 0xcc), 'le sommet de la Tour (5:cc)')

# L'Insomnis battu
g.m[RHYTHM_STAGE] = 3
g.w(200)
check(len(objects(0x11)) == 1, 'Zelda apparaît, en rêve')
g.w(70)
check(g.wait_text(120), 'Zelda : « Link... ? C\'est toi... ? »')
g.shot(os.path.join(OUT, 'f01_zelda.png'))
seen = follow({0x03: 'f02_couplet'}, lambda: g.where()[0] != 5)
check(all(i in seen for i in range(0x01, 0x04)), 'les textes de la fin, Zelda puis Marine (%s)' % [hex(i) for i in seen])
g.wait_until(lambda: g.where() == (1, 0xaa), 900)
g.settled()
g.w(60)
check(g.where() == (1, 0xaa), 'fondu : la plage du réveil (1:aa)')

# L'épilogue et le générique
g.w(120)
check(len(objects(0x13)) == 1, 'Marine, humaine, le matin')
check(g.wait_text(200), 'l\'épilogue : « Cette nuit-là... »')
g.shot(os.path.join(OUT, 'f03_epilogue.png'))
# Le générique : 20 cartons (TX_5c14-5c27) qui se ferment seuls (\wait) ; d'abord on lit l'épilogue
seen = follow({0x07: 'f04_marine'}, lambda: g.m[EPILOGUE] == 4, 60)
check(0x07 in seen and 0x08 in seen, "l'épilogue : Marine (%s)" % [hex(i) for i in seen])
check(g.m[EPILOGUE] == 4, 'le générique commence (Marine chante)')
g.w(80)
g.shot(os.path.join(OUT, 'f05_generique.png'))
# un carton se ferme tout seul (sans A) et le suivant s'ouvre
closed = g.wait_until(lambda: not g.m[0xcba0], 400)
reopened = g.wait_until(lambda: g.m[0xcba0], 60)
check(closed and reopened, "le générique défile tout seul (un carton se ferme, le suivant s'ouvre)")
seen = follow({}, lambda: flag(FLAG_FIN), 200)
g.shot(os.path.join(OUT, 'f05d_fin.png'))
check(flag(FLAG_FIN), 'le jeu est fini : GLOBALFLAG_BALLADE_FIN')
g.w(60)
check(len(objects(0x13)) == 0 and g.m[EPILOGUE] == 0, 'Marine part vers son île')

# L'île de Marine : le Bateau-Rondin des Échos (1:70) a une 3e page avec « Mouette »
g.warp(1, 0x70, 0x44)
g.settled()
g.w(60)
g.text_through()
g.stand(6, 4)
g.face('right')
g.press('a', 20)
g.choose(3, 4)
g.choose(3, 4)
g.wait_text()
for _ in range(30):
    g.w(30)
    if g.options_shown() >= 3:
        break
    if g.options_shown() == 0:
        g.press('a', 4)
g.w(60)
g.hold('right', 6)
g.w(16)
g.hold('right', 6)
g.w(16)
g.press('a', 10)
g.w(30)
g.settled()
g.w(60)
check(g.where() == (1, 0x6b), "le Bateau-Rondin : « Mouette », l'île de Marine (1:6b)")
g.shot(os.path.join(OUT, 'f06_ponton.png'))
g.warp(1, 0x5b, 0x45)
g.settled()
g.w(60)
check(len(objects(0x15)) == 1, 'le téléphone (Zelda)')
g.stand(4, 3)
g.face('down')
g.press('a', 30)
check(g.wait_text(60), '« Appeler Zelda ? »')
g.shot(os.path.join(OUT, 'f07_telephone.png'))
# « Oui » (la première option) ; ça sonne ; Zelda parle ; « je peux venir ? » : « Oui »
for _ in range(6):
    g.text_through()
    g.w(70)
check(flag(0x66), "Zelda invitée sur l'île (GLOBALFLAG_BALLADE_ZELDA)")
g.warp(1, 0x5b, 0x45)
g.settled()
g.w(60)
check(len(objects(0x24)) == 1, "Zelda est venue sur l'île")
g.shot(os.path.join(OUT, 'f07b_zelda_ile.png'))

# La maison de Marine
g.stand(4, 5)
for _ in range(6):
    g.hold('up', 8)
    if g.where()[0] == 3:
        break
g.settled()
g.w(40)
check(g.where() == (3, 0x2a), 'la maison de Marine (3:2a)')
g.shot(os.path.join(OUT, 'f08_maison.png'))

# Le volley : Marine (1:5c)
g.warp(1, 0x5c, 0x55)
g.settled()
g.w(60)
check(len(objects(0x14)) == 1, 'Marine, sur la plage du volley')
g.stand(3, 7)
g.face('up')
g.press('a', 30)
check(g.wait_text(60), 'Marine : « On fait quoi ? »')
g.w(40)
g.text_through()        # « Volley »
g.w(30)
g.text_through()        # les règles
g.w(30)
check(g.m[VOLLEY_STATE] == 2, 'la partie commence')
check(len(objects(0x17)) == 1 and len(objects(0x18)) == 1, 'le ballon, Marine sur le terrain')
g.shot(os.path.join(OUT, 'f09_volley.png'))
# Link sous le ballon (il sert) : il le renvoie
ball = objects(0x17)[0] if objects(0x17) else None
if ball:
    g.m[0xd00d] = g.m[obj(ball, 0x0d)]
    sent = False
    for _ in range(120):
        g.w(1)
        g.m[0xd00d] = min(g.m[obj(ball, 0x0d)], 0x40) if objects(0x17) else g.m[0xd00d]
        if objects(0x17) and g.m[obj(ball, 0x33)] in (2, 3):
            sent = True
            break
    check(sent, 'Link renvoie le ballon')
# Puis Link s'écarte : le ballon finit par tomber, un point est marqué
before = g.m[VOLLEY_SCORE] + g.m[VOLLEY_SCORE + 1]
g.wait_until(lambda: g.m[VOLLEY_STATE] == 3, 1200)
check(g.m[VOLLEY_SCORE] + g.m[VOLLEY_SCORE + 1] > before, 'un point (Link %d, Marine %d)' % (g.m[VOLLEY_SCORE], g.m[VOLLEY_SCORE + 1]))
g.shot(os.path.join(OUT, 'f10_score.png'))
# Les habitants ont compris : la veuve Marée (1:74, y $28 x $68)
g.warp(1, 0x74, 0x44)
g.settled()
g.w(60)
g.text_through()
g.stand(3, 6)
g.face('up')
g.press('a', 30)
check(g.wait_text(60), 'la veuve Marée parle')
g.w(40)
check(g.m[0xcba3] != 0 and g.m[0xcba2] == 0x21, 'après la fin : son texte change (TX_5b21 ; %02x%02x)' % (g.m[0xcba3], g.m[0xcba2]))
g.shot(os.path.join(OUT, 'f11_maree.png'))
g.text_through()
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
