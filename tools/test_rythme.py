"""Test du boss de fin en rythme (INTERAC_BALLADE_RHYTHM) dans PyBoy, et son aperçu .wav.

Usage : python tools/test_rythme.py [DOSSIER_CAPTURES]     (ROM=chemin pour une autre ROM)

Salle de test 4:4a. Les essais (les quatre premiers depuis le même moment) :
  1. on tape A n'importe comment (toutes les 8 images) : la chanson ne revient pas, pas de niveau ;
  2. on ne tape rien : seul le métronome, aucune note ;
  3. Denis : ses vrais coups (tapés sur tools/rythme.html le 16/10), rejoués dans le jeu ;
  4. un joueur qui apprend : 1er tour raté (4 notes ratées, un coup dans le vide), puis 5 bons
     tours -> les 5 niveaux (un instrument de plus à chaque fois, Marine encourage) -> Marine
     chante -> « RETOURNE D'OÙ TU VIENS ! » -> le boss meurt.
     Enregistré dans out/apercus/rythme_apercu.wav (pour qu'on écoute avant de pousser).
  5. le code secret de l'écran titre (Select tenu + Start), comme Denis le lancera : la partie
     commence dans la salle de test, et l'écran titre revient après le boss.
Les notes à frapper sont lues dans oracles-disasm/data/ages/balladeRhythmNotes.s (make_music.py).
"""
import io
import os
import re
import sys
import wave

import numpy as np
from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROM = os.environ.get('ROM', os.path.join(ROOT, 'out', 'gulls_of_life.gbc'))
OUT = sys.argv[1] if len(sys.argv) > 1 else None
CLOCK, HITS, STAGE, NR51 = 0xcde9, 0xcdeb, 0xcdec, 0xff25
TEXT_ACTIVE, MUSIC = 0xcba0, 0xcc35
LEVEL_MUSIC = [0x47, 0x49, 0x4b, 0x37, 0x3a]

src = open(os.path.join(ROOT, 'oracles-disasm', 'data', 'ages', 'balladeRhythmNotes.s'),
           encoding='utf-8').read()
INTRO = int(re.search(r'BALLADE_RHYTHM_INTRO \$(\w+)', src).group(1), 16)
LOOP = int(re.search(r'BALLADE_RHYTHM_LOOP \$(\w+)', src).group(1), 16)
FIN = int(re.search(r'BALLADE_RHYTHM_FIN_INTRO \$(\w+)', src).group(1), 16)
NOTES = [(int(a, 16), int(b, 16)) for a, b in
         re.findall(r'\.dw \$(\w+)\n\t\.db \$(\w+)', src) if a != 'ffff']

# Les coups de Denis (tools/rythme.html, 2 tours, en images depuis la 1re mesure ; ~ = tenu)
DENIS = ('3~71 85 101 117~67 205 222 248 261~30 301~98 449 462 477~70 565 580 597~68 684 699 '
         '715~122 957~75 1042 1060 1077~68 1164 1179 1204 1221~36 1264~92 1413 1428 1443~72 1531 '
         '1544 1560~70 1648 1661 1677~122')

pb = PyBoy(ROM, window='null', sound_emulated=True)
pb.set_emulation_speed(0)
rec = None
shots = [0]
# Horloge continue : le jeu remet son horloge à zéro à chaque niveau (nouveau morceau, au début
# d'un tour) ; ABS continue à compter comme si le premier morceau jouait toujours
T = {'abs': 0, 'last': 0}


def clock():
    return pb.memory[CLOCK] | pb.memory[CLOCK + 1] << 8


def sync():
    T['abs'] = T['last'] = clock()


def w(n=1):
    for _ in range(n):
        pb.tick(1, OUT is not None)
        c = clock()
        T['abs'] += c - T['last'] if c >= T['last'] else c
        T['last'] = c
        if rec is not None:
            rec.append(pb.sound.ndarray.copy())


def press(b, n=4):
    pb.button(b, 3)
    w(n)


def swing(hold=2):
    pb.button_press('a')
    w(hold)
    pb.button_release('a')


def interaction():
    for page in range(0xd0, 0xe0):
        if pb.memory[page * 256 + 0x40] and pb.memory[page * 256 + 0x41] == 0xea:
            return page * 256
    return None


def combo():
    """Coups justes d'affilée (var35 de l'interaction $ea)."""
    p = interaction()
    return pb.memory[p + 0x75] if p else None


def level():
    p = interaction()
    return pb.memory[p + 0x7a] if p else None


def shot(t):
    if OUT:
        os.makedirs(OUT, exist_ok=True)
        pb.screen.image.save(os.path.join(OUT, '%02d_%s.png' % (shots[0], t)))
        shots[0] += 1


def save_wav(name, data):
    data = np.concatenate(data).astype(np.float32)
    data -= data.mean(axis=0)
    peak = max(1.0, float(np.abs(data).max()))
    pcm = (data / peak * 28000).astype('<i2')
    os.makedirs(os.path.join(ROOT, 'out', 'apercus'), exist_ok=True)
    path = os.path.join(ROOT, 'out', 'apercus', name)     # les aperçus à écouter, rangés à part
    with wave.open(path, 'wb') as f:
        f.setnchannels(pcm.shape[1])
        f.setsampwidth(2)
        f.setframerate(pb.sound.sample_rate)
        f.writeframes(pcm.tobytes())
    print('->', path, '%.1f s' % (len(pcm) / pb.sound.sample_rate))


def play(plan, r0, r1):
    """Joue les tours r0 à r1-1 : plan(tour, note) -> écart en images, liste d'écarts ou None.
    Renvoie [(tour, note, NR51 au milieu de la note)]."""
    heard = []
    for r in range(r0, r1):
        base = INTRO + r * LOOP
        for i, (start, dur) in enumerate(NOTES):
            offs = plan(r, i)
            offs = [] if offs is None else offs if isinstance(offs, list) else [offs]
            for off in sorted(offs):
                while T['abs'] < base + start + off:
                    w()
                swing()
            while T['abs'] < base + start + dur // 2:
                w()
            heard.append((r, i, pb.memory[NR51]))
    return heard


def started():
    """Le morceau a commencé (var37 de l'interaction : Marine a parlé)."""
    p = interaction()
    return bool(p and pb.memory[p + 0x77])


def wait_start():
    """Attend que Marine ait parlé et que le morceau commence ; l'horloge continue part de là."""
    ok = until(lambda: started() and clock() < 20, 900)
    sync()
    return ok


def until(cond, limit):
    for _ in range(limit):
        if cond():
            return True
        w()
    return cond()


errors = []


def check(ok, msg):
    print(('ok   ' if ok else 'ÉCHEC ') + msg)
    if not ok:
        errors.append(msg)


# Nouvelle partie, scène de la plage, puis la salle de test
for c in 'w900 start w150 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
w(400)
for i in range(160):
    press('a', 22)
    if pb.memory[0xcc8a] == 0 and i > 60:
        break
w(60)
for i, v in enumerate((0x84, 0x4a, 0x00, 0x57, 0x03)):
    pb.memory[0xcc47 + i] = v
start = io.BytesIO()
until(lambda: pb.memory[STAGE] == 1, 400)
pb.save_state(start)
print('salle', pb.memory[0xcc2d], hex(pb.memory[0xcc30]), 'musique', hex(pb.memory[MUSIC]),
      'étape', pb.memory[STAGE])
check(pb.memory[STAGE] == 1, 'le combat commence en entrant (étape 1)')
check(pb.memory[MUSIC] == 0xf0, 'la salle est silencieuse en entrant')

# « Allez, donne-moi le La ! » (sans appuyer sur A), puis le morceau commence
check(until(lambda: pb.memory[TEXT_ACTIVE], 120), 'Marine parle en arrivant')
w(40)
shot('donne_moi_le_la')
n = 0
while pb.memory[TEXT_ACTIVE] and n < 600:
    w()
    n += 1
print('   sa bulle reste %.1f s' % ((n + 40) / 60))
check(n < 600 and not started(), 'sa bulle se ferme toute seule')
check(wait_start(), 'le morceau commence quand elle a fini')
check(pb.memory[MUSIC] == 0x47, 'niveau 1 : MUS_BALLADE_RYTHME ($47)')
check(pb.memory[0xc689] == 5, "l'épée est sur A")
c0 = clock()
w(600)
check(abs(clock() - c0 - 600) < 15, "horloge : %d pas en 600 images" % (clock() - c0))

# 1. On tape n'importe comment
start.seek(0)
pb.load_state(start)
wait_start()
while T['abs'] < INTRO + 2 * LOOP:
    if T['abs'] % 8 == 0 and not pb.memory[TEXT_ACTIVE]:
        swing()
    w()
print('n\'importe comment : coups justes', pb.memory[HITS], 'enchaînement', combo(), 'niveau', level())
check(combo() < 6, "taper n'importe comment ne fait pas revenir la chanson")
check(level() == 0 and pb.memory[STAGE] == 1, "taper n'importe comment ne fait pas monter de niveau")

# 2. On ne tape rien
start.seek(0)
pb.load_state(start)
wait_start()
heard = play(lambda r, i: None, 0, 1)
check(pb.memory[HITS] == 0 and all(n == 0x88 for _, _, n in heard),
      'sans coup : seul le métronome (NR51 = $88)')

# 3. Denis : ses vrais coups, rejoués
start.seek(0)
pb.load_state(start)
wait_start()
for tok in DENIS.split():
    f, _, held = tok.partition('~')
    while T['abs'] < INTRO + int(f):
        w()
    swing(int(held) if held else 4)
until(lambda: T['abs'] >= INTRO + 2 * LOOP + 30, 3 * LOOP)
print('Denis : coups justes', pb.memory[HITS], 'sur 36, niveau', level() + 1, 'musique', hex(pb.memory[MUSIC]))
check(level() == 2 and pb.memory[MUSIC] == LEVEL_MUSIC[2],
      'Denis : ses 2 tours sont bons -> niveau 3 au 3e tour')

# 4. Le joueur qui apprend (enregistré)
start.seek(0)
pb.load_state(start)
wait_start()
rec = []


def learner(r, i):
    if r == 0:
        if 2 <= i <= 5:
            return None                    # 4 notes ratées
        if i == 0:
            return [0, 45]                 # + un coup dans le vide pendant la note longue
        return [1, -2, 0, 0, 0, 0, -3, 2, 0, 4, -1, 2, 0, 3, -2, 1, 4, 0][i]
    return [1, 0, -1, 2, 0, 1, -2, 0, 1, 0, 2, -1, 0, 1, 0, -1, 2, 0][(i + r) % 18]


heard = play(learner, 0, 1)
print('1er tour : coups justes', pb.memory[HITS], 'enchaînement', combo())
check(pb.memory[HITS] == 14, '1er tour : 14 coups justes sur 18 (4 ratées exprès)')
check(heard[0][2] & 0x22 and not heard[5][2] & 0x22,
      'la mélodie sonne après un coup juste, pas sur une note ratée')
check(not heard[0][2] & 0x11 and heard[17][2] & 0x11,
      'la harpe revient avec l\'enchaînement')
shot('tour1')
until(lambda: T["abs"] >= INTRO + LOOP + 4, LOOP)
check(level() == 0 and pb.memory[MUSIC] == 0x47, '1er tour raté : on reste au niveau 1')
for r in range(1, 6):
    play(learner, r, r + 1)
    check(until(lambda: pb.memory[TEXT_ACTIVE], 200), 'tour %d réussi : Marine encourage' % (r + 1))
    shot('tour%d' % (r + 1))
    until(lambda: T["abs"] >= INTRO + (r + 1) * LOOP + 4, LOOP)
    if r < 5:
        print('   tour', r + 1, ': niveau', level() + 1, 'musique', hex(pb.memory[MUSIC]), 'enchaînement', combo())
        check(level() == r and pb.memory[MUSIC] == LEVEL_MUSIC[r],
              'niveau %d : musique $%02x' % (r + 1, LEVEL_MUSIC[r]))
check(pb.memory[STAGE] == 2, 'après le niveau 5 : Marine chante (étape 2)')
check(pb.memory[MUSIC] == 0x48, 'MUS_BALLADE_RYTHME_FIN ($48)')
check(until(lambda: pb.memory[TEXT_ACTIVE], 60), 'Marine : « Je vais me le faire ! »')
shot('marine')
until(lambda: clock() >= FIN - 30 and clock() < 2000, FIN)
check(pb.memory[STAGE] == 2, 'le boss tient jusqu\'à la fin du chant')
check(until(lambda: pb.memory[TEXT_ACTIVE], 120), 'le coup de grâce : « RETOURNE D\'OÙ TU VIENS ! »')
shot('coup_de_grace')
check(until(lambda: pb.memory[STAGE] == 3, 600), 'après le coup de grâce, le boss meurt (étape 3)')
shot('fin')
w(240)
save_wav('rythme_apercu.wav', rec)
rec = None
pb.stop(save=False)

# 5. Le code secret de l'écran titre (Select tenu + Start) : nouvelle partie -> salle de test ;
# le fichier garde son vrai départ ; après le boss, retour à l'écran titre
pb = PyBoy(ROM, window='null', sound_emulated=True)
pb.set_emulation_speed(0)
w(900)
pb.button_press('select')
w(10)
press('start', 10)
pb.button_release('select')
for c in 'w140 start w60 a w60 a w80 a w10 start w20 a w60 a w60 a'.split():
    w(int(c[1:])) if c[0] == 'w' else press(c)
until(lambda: pb.memory[STAGE] == 1 and pb.memory[0xcc30] == 0x4a, 600)
wait_start()
print('code secret : salle', pb.memory[0xcc2d], hex(pb.memory[0xcc30]), 'étape', pb.memory[STAGE],
      'départ du fichier', [hex(pb.memory[0xc62b + i]) for i in range(6)])
check(pb.memory[0xcc2d] == 4 and pb.memory[0xcc30] == 0x4a and pb.memory[STAGE] == 1,
      'code secret : la partie commence dans la salle de test')
w(60)
check(pb.memory[0xc62b] == 1 and pb.memory[0xc62c] == 0xaa,
      'code secret : le fichier garde son vrai point de départ (plage 1:aa)')
shot('secret')
play(lambda r, i: 0, 0, 5)
until(lambda: pb.memory[STAGE] == 0 and pb.memory[0xcc30] != 0x4a, LOOP + FIN + 1200)
w(60)
shot('retour')
check(pb.memory[STAGE] == 0 and pb.memory[0xcc30] != 0x4a, 'après le boss : retour au début (titre)')
pb.stop(save=False)
print('\n%d échec(s)' % len(errors) if errors else '\nTout est bon.')
sys.exit(1 if errors else 0)
