"""Test du Mamono (le 2e jeu du forain, dans son arène 5:ea) : le forain y envoie Link ; une partie
Facile gagnée (le test connaît les monstres : il creuse les cases vides, puis les monstres du plus
faible au plus fort, quand Link a le niveau) : les chiffres dans le sable, les cases sans rien
autour qui découvrent leurs voisines toutes seules, les vrais ennemis figés sur leur case puis en
fumée (leur case montre alors la somme des niveaux autour, comme les autres), la montée de
niveau ; les notes du joueur (B : 1 à 5 puis rien ; une case notée se creuse quand même) ; une partie Dur sans une
égratignure (le gros lot : un quart de cœur) ; puis un monstre trop fort découvert à l'aveugle (il
frappe fort) ; on ressort par le haut. Deux niveaux : Facile, Dur.

Usage : python tools/test_mamono.py DOSSIER_CAPTURES
"""
import os
import sys

from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
pb = PyBoy(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), window='null', sound_emulated=True)
pb.set_emulation_speed(0)
m = pb.memory
HEALTH, MAX_HEALTH = 0xc6aa, 0xc6ab
RUPEES, HEART_PIECES = 0xc6ad, 0xc6ac
CREUSE_LEVEL = 0xcdf6
P_LEVEL, P_XP, PLACED, LEFT, STATE, SHOW, SHOW_SLOT, SLOTS = 0xc580, 0xc581, 0xc582, 0xc583, 0xc584, 0xc585, 0xc586, 0xc587
HURT, FLOOD = 0xc599, 0xc59a
LEVELS = 0xcfc0
LAYOUT = 0xcf00
ROWS, COLS = 8, 13
errors = []


def w(n):
    pb.tick(n, True)


def press(b, n=4):
    pb.button(b, 3)
    w(n)


def walk(b, n):
    pb.button_press(b)
    w(n)
    pb.button_release(b)
    w(4)


def shot(name, scale=3):
    im = pb.screen.image
    im.resize((im.size[0] * scale, im.size[1] * scale)).save(os.path.join(OUT, name + '.png'))


def check(ok, what):
    print(('ok   ' if ok else 'RATÉ ') + what, flush=True)
    if not ok:
        errors.append(what)
        shot('rate_%02d' % len(errors))


def goto(y=None, x=None, limit=400):
    for axis, target, minus, plus in (('x', x, 'left', 'right'), ('y', y, 'up', 'down')):
        if target is None:
            continue
        addr = 0xd00d if axis == 'x' else 0xd00b
        for _ in range(limit):
            cur = m[addr]
            if abs(cur - target) <= 1:
                break
            b = minus if cur > target else plus
            pb.button_press(b)
            w(2)
            pb.button_release(b)


def text_through(n=40, choose=0):
    choices = list(choose) if isinstance(choose, (list, tuple)) else [choose]
    for _ in range(n):
        if not m[0xcba0]:
            w(20)
            if not m[0xcba0]:
                return
        if m[0xcba1] == 1 and choices:
            w(40)
            for _ in range(choices.pop(0)):
                walk('right', 6)
                w(16)
            press('a', 20)
            w(20)
            continue
        press('a', 20)


def level(i):
    b = m[LEVELS + i // 2]
    return (b >> 4) if i & 1 else (b & 0x0f)


def pos(i):
    r, c = divmod(i, COLS)
    return ((r + 2) << 4) | (c + 1)


def neighbours(i):
    r, c = divmod(i, COLS)
    return [nr * COLS + nc for nr in range(r - 1, r + 2) for nc in range(c - 1, c + 2)
            if (nr, nc) != (r, c) and 0 <= nr < ROWS and 0 <= nc < COLS]


def dug(i):
    return m[LAYOUT + pos(i)] != 0x12


def wait_flood():
    """Les cases vides découvrent leurs voisines (quelques-unes par image) : attendre la fin."""
    for _ in range(300):
        if not m[FLOOD]:
            return
        w(1)


def face(i):
    """Link se met au-dessus de la case, tourné vers elle."""
    wait_flood()
    r, c = divmod(i, COLS)
    row, col = r + 2, c + 1
    goto(None, col * 16 + 8)
    goto((row - 1) * 16 + 8, None)
    goto(None, col * 16 + 8)
    walk('down', 2)


def dig(i):
    """Link se met au-dessus de la case et creuse vers le bas."""
    face(i)
    press('a', 30)


def wait_show():
    for _ in range(40):
        if not m[SHOW] and not m[0xcba0]:
            return
        text_through()
        w(10)


def arena(lvl, name):
    """Chez le forain : le Mamono, le niveau, payer ; Link arrive dans l'arène."""
    m[RUPEES] = 0x99
    goto(0x28, None)
    goto(None, 0x78)
    goto(0x28, None)
    walk('down', 3)
    press('a', 30)
    text_through(choose=[1, lvl])
    w(250)
    check(m[0xcc30] == 0xea and m[CREUSE_LEVEL] == lvl, '%s : le forain envoie Link dans l\'arène (5:%02x)' % (name, m[0xcc30]))
    w(30)
    text_through()                    # les règles
    check(m[STATE] == 1 and m[P_LEVEL] == 1, '%s : la partie commence (Link niveau 1)' % name)
    check(m[0xc689] == 0x15 and m[0xc688] == 0, '%s : rien que la Pelle (A %02x, B %02x)' % (name, m[0xc689], m[0xc688]))
    slots = [m[SLOTS + k] for k in range(5)]
    check(all(slots), '%s : les cinq ennemis modèles %s' % (name, [hex(s) for s in slots]))
    check(all(not (m[(s << 8) + 0x9a] & 0x80) for s in slots if s), '%s : cachés' % name)


def leave(name):
    goto(None, 0x78)
    goto(0x18, None)
    for _ in range(10):
        walk('up', 8)
        if m[0xcc30] == 0xac:
            break
    w(200)
    check(m[0xcc30] == 0xac, '%s : retour chez le forain' % name)
    check(m[0xc689] == 0x05 and m[0xc688] == 0x03, '%s : ses objets reviennent (A %02x, B %02x)' % (name, m[0xc689], m[0xc688]))


def play_to_win(lvl, name, perfect=False):
    arena(lvl, name)
    first = 3 * COLS + 6
    dig(first)
    wait_show()
    levels = [level(i) for i in range(ROWS * COLS)]
    counts = [levels.count(k) for k in range(1, 6)]
    print('  monstres par niveau', counts, flush=True)
    check(m[PLACED] == 1 and all(levels[j] == 0 for j in neighbours(first) + [first]),
          '%s : les monstres sont cachés, loin de la 1re case' % name)
    check(m[LAYOUT + pos(first)] == 0xbf, '%s : la 1re case : rien autour' % name)
    wait_flood()
    auto = sum(1 for i in range(ROWS * COLS) if dug(i))
    check(auto > 1, '%s : les cases vides découvrent leurs voisines toutes seules (%d cases)' % (name, auto))
    # Les notes du joueur (B) : sur une case pas creusée dont la case du dessus est creusée
    spot = next(i for i in range(COLS, ROWS * COLS) if not dug(i) and dug(i - COLS) and not levels[i])
    face(spot)
    notes = []
    for _ in range(6):
        press('b', 12)
        notes.append(m[LAYOUT + pos(spot)])
    check(notes == [0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x12], '%s : B, les notes 1 à 5 puis rien %s' % (
        name, ['%02x' % t for t in notes]))
    press('b', 12)
    press('a', 30)
    # (Denis : « mettre un chiffre ça doit pas nous empêcher de creuser »)
    check(m[LAYOUT + pos(spot)] != 0x69, '%s : une case notée se creuse quand même' % name)
    # Les cases vides
    for i in range(ROWS * COLS):
        if not levels[i] and not dug(i):
            dig(i)
            wait_show()
    expect = {i: sum(levels[j] for j in neighbours(i)) for i in range(ROWS * COLS)}
    bad = [i for i in range(ROWS * COLS) if not levels[i] and
           m[LAYOUT + pos(i)] != (0xbf if expect[i] == 0 else 0x40 + expect[i])]
    check(not bad, '%s : les chiffres dans le sable %s' % (name, bad[:5]))
    shot(name + '_chiffres')
    # Les monstres, du plus faible au plus fort
    seen, shown = [], False
    for lv in range(1, 6):
        for i in range(ROWS * COLS):
            if levels[i] == lv and m[STATE] == 1:
                m[HEALTH] = m[MAX_HEALTH]
                if perfect:
                    m[HURT] = 0         # (le test joue le « perfect »)
                dig(i)
                if not shown and lv >= 2:
                    w(4)
                    slot = m[SHOW_SLOT]
                    visible = slot and m[(slot << 8) + 0x9a] & 0x80
                    shot(name + '_monstre')
                    check(bool(visible), '%s : le monstre de niveau %d apparaît, figé' % (name, lv))
                    shown = True
                wait_show()
                seen.append((lv, m[P_LEVEL]))
    print('  (monstre, niveau de Link)', seen, flush=True)
    check(m[STATE] == 2 and m[LEFT] == 0, '%s : tous les monstres, gagné' % name)
    check(bool(seen) and max(p for _, p in seen) >= 3, '%s : Link est monté de niveau' % name)
    boxed = [i for i in range(ROWS * COLS) if levels[i] and
             m[LAYOUT + pos(i)] != (0xbf if expect[i] == 0 else 0x40 + expect[i])]
    check(not boxed, '%s : la case d\'un monstre vaincu montre la somme autour (Denis) %s' % (name, boxed[:5]))
    shot(name + '_fin')
    for _ in range(6):
        w(30)
        text_through()



def ring(r):
    """Un de nos anneaux est eu (wRingsObtained) et rangé dans la boîte (wRingBoxContents)."""
    return bool(m[0xc616 + r // 8] & (1 << (r % 8))) and r in [m[0xc6c6 + i] for i in range(5)]

# Nouvelle partie, la plage du forain
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if m[0xcc8a] == 0 and i > 60:
        break
w(60)
m[MAX_HEALTH] = 12
m[HEALTH] = 12
m[0xc689], m[0xc688] = 0x05, 0x03   # l'épée sur A, les bombes sur B
for i, v in enumerate((0x81, 0xac, 0x00, 0x27, 0x03)):
    m[0xcc47 + i] = v
w(250)
check(m[0xcc30] == 0xac, 'la plage du forain')

play_to_win(0, 'facile')
leave('facile')
pieces = m[HEART_PIECES]
play_to_win(1, 'dur', perfect=True)
check(m[HEART_PIECES] != pieces, 'dur sans une égratignure : le gros lot, un quart de cœur (%d -> %d)' % (pieces, m[HEART_PIECES]))
check(ring(0x16), "et l'Anneau Tornade, dans la boîte")
leave('dur')

# Un monstre trop fort, découvert à l'aveugle : il frappe de tout son niveau
arena(1, 'dur')
first = 3 * COLS + 6
dig(first)
wait_show()
levels = [level(i) for i in range(ROWS * COLS)]
strong = [i for i in range(ROWS * COLS) if levels[i] >= 3 and not any(dug(j) for j in neighbours(i))]
if strong:
    i = strong[0]
    m[HEALTH] = m[MAX_HEALTH]
    before = m[HEALTH]
    dig(i)
    w(30)
    print('  monstre de niveau %d : vie %d -> %d' % (levels[i], before, m[HEALTH]), flush=True)
    check(before - m[HEALTH] == 2 * levels[i], 'à l\'aveugle : un demi-cœur par niveau du monstre')
    wait_show()
else:
    check(False, 'pas de monstre fort à découvrir à l\'aveugle')
# Pendant la partie, on ne s'en va pas (Denis)
goto(None, 0x78)
goto(0x18, None)
for _ in range(6):
    walk('up', 8)
w(100)
check(m[0xcc30] == 0xea and m[0xc689] == 0x15, "pendant la partie, on ne s'en va pas (salle 5:%02x)" % m[0xcc30])
print('\nTout est bon.' if not errors else '\n%d problème(s)' % len(errors))
