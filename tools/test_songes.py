"""Test des Songes des Héros et du Sifflet de Marine (code/ages/balladeSonges.s), par le menu de test.

- au Nid des Vents, dans le Songe (0:48) : Marine explique ; une bulle de rêve ;
- 1er rêve (5:eb) : une fée suit Link et l'interrompt sans arrêt ; en haut de la forêt, Marine :
  « Elle te parlait comme ça TOUT le temps ?! » ; retour au Nid ;
- 2e rêve (5:ec) : trois masques ; Link met chacun (A) et Marine commente ; retour au Nid ;
- 3e rêve (5:ed) : Célesbourg ; la princesse pousse Link dans le vide ; Marine plonge et le
  rattrape (pas de cœur perdu) ; le Sifflet de Marine ;
- ensuite, partout : tomber dans le ciel du Nid ne coûte plus de cœur, Marine le rattrape. Avant le
  Sifflet, une chute coûte toujours un peu de vie.

Usage : python tools/test_songes.py DOSSIER_CAPTURES   (ROM=chemin pour une autre ROM)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from debug_menu import HEALTH, MAX_HEALTH, TEXT_ACTIVE, Game, sheet

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
FLAG_SIFFLET, FLAG_SONGE1, FLAG_SONGE2 = 0x5e, 0x5f, 0x60
CATCH, MASKS, WORN = 0xc595, 0xc596, 0xc597
INTERAC_MARINE, INTERAC_CREUSE = 0xe7, 0xeb
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


def objects(ident, subid):
    return [s for s in range(0xd0, 0xe0)
            if g.m[(s << 8) + 0x40] and g.m[(s << 8) + 0x41] == ident and g.m[(s << 8) + 0x42] == subid]


inside = [False]


def walk(row, col, texts=None, limit=400):
    """Comme stand (d'abord x, puis y), mais en fermant les textes qui interrompent Link."""
    y, x = row * 16 + 8, col * 16 + 8
    room = g.where()
    for target, addr, minus, plus in ((x, 0xd00d, 'left', 'right'), (y, 0xd00b, 'up', 'down')):
        for _ in range(limit):
            if g.where() != room:
                return
            if g.m[TEXT_ACTIVE]:
                if texts is not None and g.m[0xd00b] < 0x20:
                    return      # (en haut de la forêt : c'est Marine, le rêve finit)
                if texts is not None and not inside[0]:
                    texts.append(1)
                inside[0] = True
                g.press('a', 20)
                continue
            inside[0] = False
            cur = g.m[addr]
            if abs(cur - target) <= 1:
                break
            b = minus if cur > target else plus
            g.pb.button_press(b)
            g.w(2)
            g.pb.button_release(b)


def close_one():
    """Fermer la boîte de texte ouverte (et pas la suivante)."""
    while g.m[TEXT_ACTIVE]:
        g.press('a', 20)


def to_bubble():
    """Au Nid du Songe : toucher la bulle (ligne 4, colonne 6)."""
    bubbles = objects(INTERAC_CREUSE, 0x1d)
    check(len(bubbles) == 1, 'une bulle de rêve au Nid')
    walk(4, 6)
    g.w(60)
    g.settled()
    g.w(30)


def fall_test(label):
    """Tomber dans le ciel du courant ascendant (1:75), comme tools/test_nid.py."""
    g.warp(1, 0x75, 0x55)
    g.text_through()
    g.m[HEALTH] = g.m[MAX_HEALTH]
    h0 = g.m[HEALTH]
    g.stand(5, 5)
    g.hold('down', 60)
    gull = False
    for _ in range(200):
        g.w(1)
        if objects(INTERAC_MARINE, 0x07) and g.m[0xd01a] & 0x80:
            if not gull:
                gull = True
                g.w(8)
                shoot('chute_' + label, 'Sifflet : elle le rattrape (1:75)' if label == 'apres' else label)
    g.settled()
    g.w(30)
    return h0, g.m[HEALTH], gull


g = Game()
g.level(6, 'Ville')
g.text_through()

# Avant le Sifflet : une chute coûte de la vie, pas de mouette
h0, h1, gull = fall_test('avant')
check(h1 < h0 and not gull, 'avant le Sifflet : une chute coûte de la vie (%d -> %d), pas de mouette' % (h0, h1))

# Au Nid, dans le Songe : Marine explique
g.warp(0, 0x48, 0x54)
check(g.wait_text(120), 'au Nid du Songe : Marine explique les Songes des Héros')
shoot('s01_nid', 'Le Nid du Songe : « Touche une bulle ! »')
g.text_through()
g.w(20)
shoot('s02_bulle', 'La bulle de rêve')
to_bubble()
check(g.where() == (5, 0xeb), '1er rêve : la forêt (5:eb)')

# 1er rêve : la fée qui parle tout le temps
g.w(60)
fairy = objects(INTERAC_CREUSE, 0x1f)
check(len(fairy) == 1, 'une fée suit Link')
check(g.wait_text(150), 'la fée interrompt Link')
shoot('s03_fee', '1er rêve : la fée qui parle tout le temps')
g.text_through()
texts = []
walk(9, 2, texts)
walk(2, 2, texts)
walk(2, 7, texts)
walk(1, 7, texts)
check(len(texts) >= 2, 'la fée l\'interrompt encore en chemin (%d fois)' % len(texts))
check(g.wait_text(60), 'en haut de la forêt : Marine')
shoot('s04_marine', 'Marine : « TOUT le temps ?! »')
g.text_through()
g.w(60)
g.settled()
g.w(30)
check(g.where() == (0, 0x48) and g.global_flag(FLAG_SONGE1), 'retour au Nid, le 1er rêve est vu')
g.text_through()

# 2e rêve : les masques
to_bubble()
check(g.where() == (5, 0xec), '2e rêve : la clairière des masques (5:ec)')
check(g.wait_text(120), 'Marine : « Des masques ! »')
g.text_through()
check(len(objects(INTERAC_CREUSE, 0x21)) == 3, 'trois masques posés')
for k, col in enumerate((4, 7, 10)):
    walk(5, col)
    g.face('up')
    g.press('a', 10)
    ok = g.wait_text(60)
    check(ok and g.m[WORN] == k + 1, 'Link met le masque %d ; Marine commente' % (k + 1))
    if k == 2:
        break
    close_one()
    g.w(10)
    if k == 1:
        g.hold('down', 12)
        shoot('s05_masque', '2e rêve : le masque du Roc')
check(g.m[MASKS] == 7, 'les trois masques essayés')
# Le dernier commentaire, puis « rends-les ! » (TX_5b30 : wTextIndex $cba2)
seen = False
for _ in range(40):
    if g.where() != (5, 0xec):
        break
    if g.m[TEXT_ACTIVE]:
        seen = seen or g.m[0xcba2] == 0x30
        g.press('a', 20)
    else:
        g.w(20)
check(seen, 'Marine : « rends-les ! »')
g.w(60)
g.settled()
g.w(30)
check(g.where() == (0, 0x48) and g.global_flag(FLAG_SONGE2), 'retour au Nid, le 2e rêve est vu')
g.text_through()

# 3e rêve : Célesbourg
to_bubble()
check(g.where() == (5, 0xed), '3e rêve : Célesbourg (5:ed)')
check(len(objects(INTERAC_CREUSE, 0x11)) == 1, 'la princesse attend au bord')
g.m[HEALTH] = g.m[MAX_HEALTH]
h0 = g.m[HEALTH]
walk(4, 2)
walk(4, 7)
check(g.wait_text(60), 'la princesse : « Allez, saute ! »')
shoot('s06_zelda', '3e rêve : « Ton oiseau te rattrapera ! »')
g.text_through()
gull = caught = False
for _ in range(300):
    g.w(1)
    if objects(INTERAC_MARINE, 0x07) and not gull:
        gull = True
    if gull and objects(INTERAC_MARINE, 0x07) and g.m[0xd01a] & 0x80 and not caught:
        caught = True      # (Link réapparu sous elle)
        g.w(8)
        shoot('s07_rattrape', 'Marine plonge et le rattrape')
    if g.m[TEXT_ACTIVE]:
        break
check(gull and caught, 'poussé dans le vide, Marine plonge et le rattrape')
check(g.m[HEALTH] == h0, 'pas de cœur perdu (%d -> %d)' % (h0, g.m[HEALTH]))
check(g.wait_text(60), 'Marine : « Si tu tombes encore, siffle. »')
shoot('s08_siffle', '« Si tu tombes encore, siffle. »')
g.text_through()
g.w(60)
g.settled()
g.w(30)
check(g.where() == (0, 0x48) and g.global_flag(FLAG_SIFFLET), 'retour au Nid : le Sifflet de Marine')
check(not objects(INTERAC_CREUSE, 0x1d), 'plus de bulle : les trois rêves sont vus')

# Le Sifflet, partout : tomber dans le ciel ne coûte plus de cœur
h0, h1, gull = fall_test('apres')
check(gull and h1 == h0, 'avec le Sifflet : Marine le rattrape, pas de vie en moins (%d -> %d)' % (h0, h1))
check(g.where() == (1, 0x75), 'il revient sur le dernier sol')

sheet(shots, os.path.join(OUT, 'planche.png'))
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
