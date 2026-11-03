"""Le robot danseur des tests du boss du Terrier (code/ages/balladeTerrier.s, rex : la danse) : il lit
les flèches de chaque manche dans oracles-disasm/data/ages/balladeDanseCharts.s (écrit par
tools/make_music.py) et appuie sur la croix au bon moment, en lisant l'horloge de la machine.

    from danse_bot import play_round, rex_var
    hits, judged = play_round(g, boss_slot, miss_every=0)   # 0 : parfait ; n : une flèche sur n ratée
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS = os.path.join(ROOT, 'oracles-disasm', 'data', 'ages', 'balladeDanseCharts.s')
BUTTONS = ('left', 'down', 'up', 'right')
NR51 = 0xff25


def charts():
    """[[(temps, flèche 0-3, durée de la voix)], ...] : une liste par manche."""
    out, cur = [], None
    lines = open(CHARTS, encoding='utf-8').read().splitlines()
    for i, line in enumerate(lines):
        if re.match(r'balladeDanseChart\d+:', line):
            cur = []
            out.append(cur)
        m = re.match(r'\t\.dw \$([0-9a-f]{4})$', line)
        if m and cur is not None and m.group(1) != 'ffff':
            lane, opn = re.match(r'\t\.db (\d+), \$([0-9a-f]{2})', lines[i + 1]).groups()
            cur.append((int(m.group(1), 16), int(lane), int(opn, 16)))
    return out


CHARTS_DATA = charts()


def ram(g, addr):
    """La RAM des objets ($d000-$dfff) est la banque 1 : pendant un texte, le jeu en affiche une
    autre ; on lit toujours la banque 1."""
    return g.m[1, addr] if addr >= 0xd000 else g.m[addr]


def rex_var(g, slot, var):
    return ram(g, (slot << 8) + 0x40 + var)


def now(g, slot):
    t = rex_var(g, slot, 0x3e) + 256 * rex_var(g, slot, 0x3f)
    return t - 0x10000 if t >= 0x8000 else t


def play_round(g, slot, miss_every=0, wrong=False, limit=60 * 60, log=None, shots=None):
    """Joue la manche en cours (depuis l'annonce) ; rend (coups justes, flèches jugées) quand la
    manche est finie (la machine passe au résultat). miss_every = n : la n-ième flèche est laissée
    passer ; wrong : la mauvaise direction à chaque fois. shots : {nombre d'images: chemin}.
    log : liste où noter (temps, NR51) après chaque coup."""
    rnd = 5 - rex_var(g, slot, 0x30)
    chart = CHARTS_DATA[rnd]
    pressed = set()
    frames = 0
    started = False
    while frames < limit:
        g.w(1)
        frames += 1
        if shots and frames in shots:
            g.shot(shots[frames])
        if g.m[0xc6aa] < 4:
            g.m[0xc6aa] = 12      # (Link reste en vie pendant le test)
        phase = rex_var(g, slot, 0x32)
        if phase in (2, 3):
            started = True
        if started and phase not in (2, 3, 4):
            break
        if phase not in (2, 3):
            continue
        idx = rex_var(g, slot, 0x3a)
        if idx >= len(chart) or idx in pressed:
            continue
        t, lane, _ = chart[idx]
        d = t - now(g, slot)
        if d <= 1:
            pressed.add(idx)
            if miss_every and idx % miss_every == miss_every - 1:
                continue
            b = BUTTONS[(lane + 1) % 4] if wrong else BUTTONS[lane]
            g.pb.button(b, 1)
            if log is not None:
                g.w(2)
                frames += 2
                log.append((now(g, slot), g.m[NR51]))
    return rex_var(g, slot, 0x39), rex_var(g, slot, 0x3a)
