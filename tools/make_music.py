"""Musiques et bruitages originaux de Gulls of Life -> assembleur du moteur d'Ages.

Usage : python tools/make_music.py   (lancé par build.sh)

Lit les partitions music/*.txt (notation expliquée en tête de music/phare.txt) et écrit
oracles-disasm/audio/ages/mus/ballade.s : données des canaux (carré 1 = canal 0,
carré 2 = canal 1, onde = canal 4, bruit = canal 6) et le cri de mouette de LADX (bruitage, canal 2).
Les tables (soundPointers.s, soundChannelPointers.s, constants/common/music.s) pointent
dessus : MUS_BALLADE_PHARE ($41), SND_BALLADE_GULL ($d6).

Moteur : une durée = un nombre d'images (60 par seconde) ; `note X N`, `rest N` (N <= 255).
Les carrés jouent les notes à partir de c2, l'onde dès c1 (même nom = même hauteur).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'oracles-disasm', 'audio', 'ages', 'mus', 'ballade.s')
# Tables des canaux : dans la banque du code audio (incluses par soundChannelPointers.s)
OUT_PTR = os.path.join(ROOT, 'oracles-disasm', 'audio', 'ages', 'balladeChannelPointers.s')

# (fichier, nom des étiquettes) ; numéros dans audio/ages/soundPointers.s et
# constants/common/music.s : Phare $41, île $42, auberge $43, thème $44 (aussi MUS_BOSS $2e),
# Veilleur Creux $45 (boss.txt, pour un autre boss), miniboss $2d (MUS_MINIBOSS),
# écran titre $01 (MUS_TITLESCREEN, titre.txt)
SONGS = [
    ('auberge.txt', 'musBalladeAuberge'),
    ('phare.txt', 'musBalladePhare'),
    ('ile.txt', 'musBalladeIle'),
    ('boss.txt', 'musBalladeBoss'),
    ('miniboss.txt', 'musBalladeMiniboss'),
    ('theme.txt', 'musBalladeTheme'),
    ('titre.txt', 'musBalladeTitre'),
]

# (groupe, musique, salles) : le Phare Éteint (donjon 1) -> MUS_BALLADE_PHARE ($41)
ILE_BRUME = [0x79, 0x7a, 0x7b, 0x7c, 0x89, 0x8a, 0x8b, 0x8c,
             0x99, 0x9a, 0x9b, 0x9c, 0xa9, 0xaa, 0xab, 0xac]
ROOM_MUSIC = [
    # le Phare / temple (plan d'un seul étage : pied 1b-14-15, tour 16-18-17, galerie 19-12-1a,
    # Jack 13 avant le combat ; 24 et 1c de l'ancien plan)
    (4, 0x41, [0x24, 0x1b, 0x1c, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x12, 0x13]),
    (1, 0x42, ILE_BRUME),   # l'île de la Brume dans le Réel (Port-Veille compris)
    (0, 0x42, ILE_BRUME),   # et dans le Songe
    (3, 0x43, [0x9e]),      # l'auberge de Port-Veille
    (2, 0x43, [0x9e]),      # et celle du Songe
]

VOICES = {  # voix -> (canal du moteur, genre)
    'accordeon': (0, 'carre'),
    'melodie': (1, 'carre'),
    'basse': (4, 'onde'),
    'batterie': (6, 'bruit'),
}
NOISE = {'h': 0x2a, 's': 0x2e}
SEMI = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
NAMES = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']
TOKEN = re.compile(r'\[[^\]]*\]|\(|\)x\d+|\||\S+')


class ScoreError(Exception):
    pass


def strip_comment(line):
    # « # » commence un commentaire en début de ligne ou après un espace (pas dans c#5)
    m = re.search(r'(^|\s)#', line)
    return line[:m.start()] if m else line


def pitch(tok):
    m = re.fullmatch(r'([a-g])(#|s|b)?(\d)', tok)
    if not m:
        raise ScoreError('note inconnue : ' + tok)
    n = SEMI[m.group(1)] + {'#': 1, 's': 1, 'b': -1, None: 0}[m.group(2)]
    return 12 * (int(m.group(3)) - 1) + n


def note_name(n):
    return '%s%d' % (NAMES[n % 12], n // 12 + 1)


def expand(tokens):
    """Déplie les ( ... )xN."""
    out, stack = [], []
    for t in tokens:
        if t == '(':
            stack.append(out)
            out = []
        elif re.fullmatch(r'\)x\d+', t):
            if not stack:
                raise ScoreError('« ) » sans « ( »')
            body, out = out, stack.pop()
            out.extend(body * int(t[2:]))
        else:
            out.append(t)
    if stack:
        raise ScoreError('« ( » sans « ) »')
    return out


def parse(path):
    tempo, bar = 9, 6
    sections, order, cur = {}, None, None
    with open(path, encoding='utf-8') as f:
        for num, raw in enumerate(f, 1):
            line = strip_comment(raw).strip()
            if not line:
                continue
            m = re.fullmatch(r'==\s*(\S+)\s*==', line)
            if m:
                cur = sections.setdefault(m.group(1), {v: [] for v in VOICES})
                continue
            m = re.fullmatch(r'(\w+)\s*:\s*(.*)', line)
            if m and m.group(1) == 'ordre':
                intro, _, loop = m.group(2).partition('|')
                order = (intro.split(), loop.split())
                continue
            if m and m.group(1) in VOICES:
                if cur is None:
                    raise ScoreError('ligne %d : voix hors section' % num)
                cur[m.group(1)].extend(TOKEN.findall(m.group(2)))
                continue
            m = re.fullmatch(r'(tempo|mesure)\s+(\d+(?:\.\d+)?)', line)
            if m:
                if m.group(1) == 'tempo':
                    tempo = float(m.group(2))
                else:
                    bar = int(m.group(2))
                continue
            raise ScoreError('ligne %d illisible : %s' % (num, line))
    if not order or not order[1]:
        raise ScoreError('il manque « ordre: INTRO | A B ... »')
    return tempo, bar, sections, order


def events(name, voice, kind, tokens, bar, tempo):
    """Jetons d'une voix -> [('cmd', nom, valeur) | ('note', hauteur|None, croches)]."""
    evs, in_bar, bars = [], 0.0, 0
    for t in expand(tokens):
        if t == '|':
            # Une barre peut fermer plusieurs mesures d'un coup (notes liées d'une mesure à l'autre)
            n = round(in_bar / bar)
            if n < 1 or abs(in_bar - n * bar) > 1e-6:
                raise ScoreError('%s/%s : mesure %d = %g croches au lieu de %d'
                                 % (name, voice, bars + 1, in_bar, bar))
            in_bar, bars = 0.0, bars + n
        elif t.startswith('['):
            parts = t[1:-1].split()
            m = re.fullmatch(r'v(\d+)', parts[0])
            if m:
                evs.append(('cmd', 'vol', int(m.group(1))))
            elif parts[0] == 'chant':
                evs.append(('cmd', 'chant', parts[1] == 'mouette'))
            elif parts[0] in ('duty', 'onde', 'vib', 'detune', 'gate'):
                v = parts[1]
                if parts[0] in ('onde', 'vib'):
                    v = int(v, 16)
                elif parts[0] == 'gate':
                    v = float(v)
                else:
                    v = int(v)
                evs.append(('cmd', parts[0], v))
            else:
                raise ScoreError('commande inconnue : ' + t)
        else:
            what, _, dur = t.partition(':')
            if not dur:
                raise ScoreError('%s/%s : durée manquante dans « %s »' % (name, voice, t))
            if dur.endswith('f'):
                dur = float(dur[:-1]) / tempo
            elif '/' in dur:  # triolets : 2/3 de croche
                a, b = dur.split('/')
                dur = float(a) / float(b)
            else:
                dur = float(dur)
            if what == '-':
                p = None
            elif what == 'mouette':
                if kind != 'carre':
                    raise ScoreError('%s/%s : la mouette crie sur un carré' % (name, voice))
                p = 'mouette'
            elif kind == 'bruit':
                p = NOISE.get(what)
                if p is None:
                    if not re.fullmatch(r'n[0-9a-f]{2}', what):
                        raise ScoreError('bruit inconnu : ' + what)
                    p = int(what[1:], 16)
            else:
                p = pitch(what)
                if kind == 'carre' and p < 12:
                    raise ScoreError('%s : trop grave pour un carré (c2 minimum)' % t)
            evs.append(('note', p, dur))
            in_bar += dur
    if in_bar > 1e-6:
        raise ScoreError('%s/%s : dernière mesure sans « | »' % (name, voice))
    return evs, bars


ECHO = re.compile(r'<(\w+)\+(\d+(?:\.\d+)?)>')


def echo_events(s, v, toks, tok, parsed, bar, tempo):
    """<melodie+2> : les notes d'une autre voix, retardées de 2 croches (écho), coupées à la fin
    de la section. Les commandes écrites avant (volume, timbre...) restent celles de cette voix."""
    src, delay = ECHO.fullmatch(tok).groups()
    if (s, src) not in parsed:
        raise ScoreError('%s/%s : écho d\'une voix inconnue ou elle-même en écho : %s' % (s, v, src))
    src_evs, bars = parsed[s, src]
    i = toks.index(tok)
    before, _ = events(s, v, VOICES[v][1], toks[:i], bar, tempo)
    after, _ = events(s, v, VOICES[v][1], toks[i + 1:], bar, tempo)
    left = bars * bar - float(delay)
    evs = before + [('note', None, float(delay))]
    for e in src_evs:
        if e[0] != 'note' or left <= 1e-6:
            continue
        evs.append(('note', e[1], min(e[2], left)))
        left -= min(e[2], left)
    return evs + after, bars


class Channel:
    def __init__(self, kind, tempo):
        self.kind, self.tempo = kind, tempo
        self.lines, self.pos, self.frames = [], 0.0, 0
        self.state = {'gate': 1.0}
        self.pending_rest = 0

    def flush_rest(self):
        n = self.pending_rest
        while n > 0:
            self.lines.append('\trest $%02x' % min(n, 255))
            n -= min(n, 255)
        self.pending_rest = 0

    def cmd(self, name, value, record=True):
        if record:
            self.state[name] = value
        if name in ('gate', 'chant'):
            return
        self.flush_rest()
        if name == 'vol':
            if self.kind != 'onde':  # le moteur ignore le volume sur l'onde
                self.lines.append('\tvol $%x' % min(value, 15))
        elif name == 'duty':
            self.lines.append('\tduty $%02x' % value)
        elif name == 'onde':
            self.lines.append('\tduty $%02x' % value)
        elif name == 'vib':
            self.lines.append('\tvibrato $%02x' % value)
        elif name == 'detune':
            self.lines.append('\tcmdfd $%02x' % (value & 0xff))

    def note(self, p, dur):
        start = round(self.pos * self.tempo)
        self.pos += dur
        total = round(self.pos * self.tempo) - start
        self.frames += total
        if p is None:
            self.pending_rest += total
            return
        if p == 'mouette':
            self.gull(total)
            return
        play = total if self.state['gate'] >= 1 else max(1, round(total * self.state['gate']))
        if play > 255:
            raise ScoreError('note trop longue (%d images)' % play)
        if self.state.get('chant') and self.kind == 'carre':
            self.sung(p, total, play)
            return
        self.flush_rest()
        name = note_name(p) if self.kind != 'bruit' else '$%02x' % p
        self.lines.append('\tnote %-4s $%02x' % (name, play))
        self.pending_rest += total - play

    def sung(self, p, total, play):
        """Une note « chantée par la mouette » : attaque qui plonge d'un ton au-dessus vers la
        note en gonflant (comme le début du cri de LADX), la note tenue, puis une fin qui retombe
        d'un demi-ton en s'éteignant (« kyaaa »). Hauteurs par le décalage cmdfd, une image par
        entrée au début et à la fin seulement (sinon la musique prendrait trop de place)."""
        x = FREQ[p - 12]
        room = 2048 - x

        def units(semis):  # décalage du registre pour monter de « semis » demi-tons
            return round(room * (1 - 2 ** (-semis / 12)))

        vol = self.state.get('vol', 6)
        name = note_name(p)
        attack = min(5, play)
        tail = min(4, (play - attack) // 2)
        hold = play - attack - tail
        self.flush_rest()
        cur = None
        for k in range(attack):
            off = round(units(2) * (attack - 1 - k) / max(1, attack - 1))
            v = max(1, round(vol * (k + 1) / attack))
            self.lines.append('\tcmdfd $%02x' % (off & 0xff))
            if v != cur:
                self.lines.append('\tvol $%x' % v)
                cur = v
            self.lines.append('\tnote %-4s $01' % name)
        if hold > 0:
            self.lines += ['\tcmdfd $00', '\tvol $%x' % vol, '\tnote %-4s $%02x' % (name, hold)]
            cur = vol
        for k in range(tail):
            off = -round(units(1) * (k + 1) / tail)
            v = max(1, round(vol * (tail - k) / (tail + 1)))
            self.lines.append('\tcmdfd $%02x' % (off & 0xff))
            if v != cur:
                self.lines.append('\tvol $%x' % v)
                cur = v
            self.lines.append('\tnote %-4s $01' % name)
        self.lines.append('\tcmdfd $%02x' % (self.state.get('detune', 0) & 0xff))
        self.lines.append('\tvol $%x' % vol)
        self.pending_rest += total - play

    def gull(self, total):
        """Le cri de mouette de LADX (voir gull_cry) joué dans la musique : sol#6 ($7b1), abaissé
        image par image avec le décalage de hauteur (cmdfd), le volume refait à chaque image ;
        puis on rend au canal son volume, son timbre, son vibrato et son décalage."""
        if total < len(GULL_FRAMES):
            raise ScoreError('mouette : il faut au moins %d images' % len(GULL_FRAMES))
        self.flush_rest()
        self.lines += ['\tduty $00', '\tvibrato $00']
        for x, v in GULL_FRAMES:
            self.lines += ['\tcmdfd $%02x' % ((x - 0x7b1) & 0xff), '\tvol $%x' % v, '\tnote gs6  $01']
        self.pending_rest += total - len(GULL_FRAMES)
        self.flush_rest()
        for k in ('vol', 'duty', 'vib', 'detune'):
            self.cmd(k, self.state.get(k, {'vol': 0, 'duty': 2, 'vib': 0, 'detune': 0}[k]), record=False)

    def snapshot(self):
        """Réécrit l'état courant (début de boucle : identique au 1er passage et aux suivants)."""
        for k in ('vol', 'duty', 'onde', 'vib', 'detune'):
            if k in self.state:
                self.cmd(k, self.state[k], record=False)


def build_song(path, label):
    tempo, bar, sections, (intro, loop) = parse(path)
    for s in intro + loop:
        if s not in sections:
            raise ScoreError('section inconnue dans ordre : ' + s)
    parsed = {}
    for s, voices in sections.items():
        lengths = set()
        echoes = []
        for v, toks in voices.items():
            echo = [t for t in toks if ECHO.fullmatch(t)]
            if echo:
                echoes.append((v, toks, echo[0]))
                continue
            parsed[s, v] = events(s, v, VOICES[v][1], toks, bar, tempo)
            lengths.add(parsed[s, v][1])
        for v, toks, tok in echoes:
            parsed[s, v] = echo_events(s, v, toks, tok, parsed, bar, tempo)
            lengths.add(parsed[s, v][1])
        if len(lengths) > 1:
            raise ScoreError('section %s : les voix n\'ont pas le même nombre de mesures %s'
                             % (s, sorted(lengths)))

    out = ['%sStart:' % label, '']
    report = []
    for v, (chan, kind) in sorted(VOICES.items(), key=lambda x: x[1][0]):
        ch = Channel(kind, tempo)
        ch.lines.append('%sChannel%d:' % (label, chan))
        if kind == 'carre':
            ch.lines += ['\tvibrato $00', '\tenv $0 $00', '\tduty $02', '\tcmdfd $00']
        elif kind == 'onde':
            ch.lines += ['\tvibrato $00', '\tcmdfd $00']
        for part in ('intro', 'loop'):
            if part == 'loop':
                ch.flush_rest()
                ch.lines.append('%sChannel%dLoop:' % (label, chan))
                ch.snapshot()
                loop_start = ch.frames
            for s in (intro if part == 'intro' else loop):
                for e in parsed[s, v][0]:
                    if e[0] == 'cmd':
                        ch.cmd(e[1], e[2])
                    else:
                        ch.note(e[1], e[2])
        ch.flush_rest()
        ch.lines += ['\tgoto %sChannel%dLoop' % (label, chan), '\tcmdff', '']
        out += ch.lines
        report.append((v, loop_start, ch.frames - loop_start))
    if len({(a, b) for _, a, b in report}) != 1:
        raise ScoreError('les canaux n\'ont pas la même durée : %s' % report)
    return out, report[0][1], report[0][2]


def gull_frames():
    """Le cri de LADX image par image : (registre de fréquence, volume)."""
    frames = []
    for k in range(9):  # attaque : volume 1, +1 tous les 1/64 s
        frames.append((0x7b0 - k, 1 + int(k * 64 / 60)))
    for k in range(11):  # le cri : volume 6, -1 tous les 2/64 s
        frames.append((0x7a7 - k, 6 - int(k * 64 / 120)))
    for k in range(11):  # l'écho
        frames.append((0x7a7 - k, 1))
    return frames


GULL_FRAMES = gull_frames()


def freq_table():
    """soundFrequencyTable du moteur (registre de fréquence des carrés, à partir de c2)."""
    s = open(os.path.join(ROOT, 'oracles-disasm', 'code', 'audio.s'), encoding='utf-8').read()
    vals = []
    for line in s[s.index('soundFrequencyTable:'):].splitlines()[1:]:
        line = line.strip()
        if not line.startswith('.dw'):
            break
        vals.append(int(line.split('$')[1], 16))
    return vals


FREQ = freq_table()


def gull_cry():
    """Cri de mouette de Link's Awakening DX (JINGLE_SEAGULL, plage de Marin), porté au moteur
    d'Ages. D'après LADX-Disassembly (src/code/audio/sfx.asm, BeginJingleSeagull) : canal 1, carré
    12,5 %, fréquence $7b0 qui descend d'un cran par image, en trois parties (attaque qui gonfle,
    NR12=$19 ; cri à $7a7 qui retombe, NR12=$62 ; écho tout bas à $7a7, NR12=$10), 31 images.
    Ici : fréquences brutes (.db poids_fort poids_faible durée), une image par entrée, l'enveloppe
    du volume recalculée à chaque image ; joué deux fois (« kyaa... kyaa »)."""
    frames = GULL_FRAMES
    lines = ['sndBalladeGullStart:', '', 'sndBalladeGullChannel2:',
             '	cmdf0 $00 ; carré 12,5 %, fréquences brutes']
    for rep in range(2):
        vol = None
        for x, v in frames:
            if v != vol:
                lines.append('	vol $%x' % v)
                vol = v
            lines.append('	.db $%02x $%02x $01' % (x >> 8, x & 0xff))
        lines += ['	vol $0', '	.db $00 $00 $%02x' % (14 if rep == 0 else 1)]
    lines += ['	cmdff', '']
    return lines


def assign_rooms():
    """Musique de chaque salle : un octet par salle dans audio/ages/groupNIDs.bin."""
    for group, music, rooms in ROOM_MUSIC:
        path = os.path.join(ROOT, 'oracles-disasm', 'audio', 'ages', 'group%dIDs.bin' % group)
        data = bytearray(open(path, 'rb').read())
        for r in rooms:
            data[r] = music
        open(path, 'wb').write(data)


def main():
    assign_rooms()
    head = '; Généré par tools/make_music.py depuis music/*.txt : ne pas éditer à la main.'
    out, ptr = [head, ''], [head, '']
    for fname, label in SONGS:
        try:
            lines, intro, loop = build_song(os.path.join(ROOT, 'music', fname), label)
        except ScoreError as e:
            sys.exit('music/%s : %s' % (fname, e))
        # Une section par morceau : ses données restent dans la banque de son étiquette Start
        out += ['m_section_superfree Ballade_%s' % label, ''] + lines + ['.ends', '']
        ptr += ['%s:' % label]
        for chan in (0, 1, 4, 6):
            ptr += ['\t.db $%02x' % chan, '\t.dw %sChannel%d' % (label, chan)]
        ptr += ['\t.db $ff', '']
        print('music/%s : intro %.1f s, boucle %.1f s' % (fname, intro / 60, loop / 60))
    out += ['m_section_superfree Ballade_sndGull', ''] + gull_cry() + ['.ends', '']
    ptr += ['sndBalladeGull:', '\t.db $02', '\t.dw sndBalladeGullChannel2', '\t.db $ff', '']
    for path, lines in ((OUT, out), (OUT_PTR, ptr)):
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines))


if __name__ == '__main__':
    main()
