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
    ('rythme.txt', 'musBalladeRythme'),        # $47, le boss de fin en rythme (prototype)
    ('rythme_fin.txt', 'musBalladeRythmeFin'),  # $48, sa fin : Marine chante
    # Les niveaux 2 à 5 (la montée en puissance, comme les 5 étapes de Lorule Castle)
    ('rythme2.txt', 'musBalladeRythme2'),      # $49, + la basse
    ('rythme3.txt', 'musBalladeRythme3'),      # $4b, + la batterie
    ('rythme4.txt', 'musBalladeRythme4'),      # $37, + les cuivres et les cymbales
    ('rythme5.txt', 'musBalladeRythme5'),      # $3a, tout, épique
    ('grelot.txt', 'musBalladeGrelot'),        # $3d, Hameau-Grelot (île 2)
    ('coffre.txt', 'musBalladeCoffre'),        # $3b, le Coffre à Jouets (donjon 2)
    ('lagune.txt', 'musBalladeLagune'),        # $25 (au lieu de Symétrie, passé), la Lagune (île 3)
    ('recif.txt', 'musBalladeRecif'),          # $18 (au lieu de la Grotte des Sirènes), le Récif Murmurant
    ('braise.txt', 'musBalladeBraise'),        # $26 (au lieu de la maison des Tokays), Mont-Braise (île 4)
    ('forge.txt', 'musBalladeForge'),          # $17 (au lieu du Donjon de la Couronne), la Forge Endormie
    ('echos.txt', 'musBalladeEchos'),          # $13 (au lieu du Tombeau des Esprits), l'île des Échos (île 5)
    ('cathedrale.txt', 'musBalladeCathedrale'),  # $1a (au lieu du Tombeau Ancien), la Cathédrale des Échos
    ('tarkin.txt', 'musBalladeTarkin'),        # $19 (au lieu du Ventre de Jabu-Jabu), la maison de Tarkin (LADX)
    ('nid.txt', 'musBalladeNid'),              # $15 (au lieu de la Grotte Lunaire), le Nid des Vents (île 6)
    ('spirale.txt', 'musBalladeSpirale'),      # $14 (au lieu du Donjon des Ailes), la Spirale Céleste
    ('sommeil.txt', 'musBalladeSommeil'),      # $1c (au lieu du Château d'Onox), l'île du Grand Sommeil (île 7)
    ('palais.txt', 'musBalladePalais'),        # $16 (au lieu du Donjon du Crâne), le Palais Givré
    ('tempetes.txt', 'musBalladeTempetes'),    # $2b (au lieu du thème de Maple), le Chant des Tempêtes
    ('gerudo.txt', 'musBalladeGerudo'),        # $0b (au lieu du village de Lynna), la Vallée Gerudo du forain
    ('quiz.txt', 'musBalladeQuiz'),            # $0a (au lieu de la ville de Lynna), le quiz de Marine
    ('lynels.txt', 'musBalladeLynels'),        # $0c (au lieu du village zora), le Labyrinthe des Lynels (Euro-Mir)
]
# Niveaux du boss en rythme : mêmes notes à frapper que rythme.txt (vérifié)
RHYTHM_LEVELS = ['rythme2.txt', 'rythme3.txt', 'rythme4.txt', 'rythme5.txt']
# Boss en rythme : les notes de la mélodie à frapper (INTERAC_BALLADE_RHYTHM)
OUT_RHYTHM = os.path.join(ROOT, 'oracles-disasm', 'data', 'ages', 'balladeRhythmNotes.s')

# (groupe, musique, salles) : le Phare Éteint (donjon 1) -> MUS_BALLADE_PHARE ($41)
ILE_BRUME = [0x79, 0x7a, 0x7b, 0x7c, 0x89, 0x8a, 0x8b, 0x8c,
             0x99, 0x9a, 0x9b, 0x9c, 0xa9, 0xaa, 0xab, 0xac]
# Hameau-Grelot (île 2) : 1:01-02, 10-13, 20-23, 31-32 (les coins sont la mer)
ILE_GRELOT = [0x00, 0x01, 0x02, 0x03, 0x10, 0x11, 0x12, 0x13,
              0x20, 0x21, 0x22, 0x23, 0x30, 0x31, 0x32, 0x33]
# La Lagune des Serments (île 3) : 1:04-37
ILE_LAGUNE = [0x04, 0x05, 0x06, 0x07, 0x14, 0x15, 0x16, 0x17,
              0x24, 0x25, 0x26, 0x27, 0x34, 0x35, 0x36, 0x37]
# Mont-Braise (île 4) : 1:08-3c
ILE_BRAISE = [r + d for r in range(0x08, 0x0d) for d in (0x00, 0x10, 0x20, 0x30)]
# L'île des Échos (île 5) : 1:40-74
ILE_ECHOS = [r + d for r in range(0x40, 0x45) for d in (0x00, 0x10, 0x20, 0x30)]
# La Cathédrale des Échos (donjon 5, groupe 5 : la croix)
# Le Nid des Vents (île 6) : 1:45-78
ILE_NID = [r + d for r in range(0x45, 0x49) for d in (0x00, 0x10, 0x20, 0x30)]
# La Spirale Céleste (donjon 6, groupe 4)
# L'île du Grand Sommeil (île 7) : 1:a0-d4 (la carte s'arrête à la ligne d)
ILE_SOMMEIL = [r + d for r in range(0xa0, 0xa5) for d in (0x00, 0x10, 0x20, 0x30)]
# Le Palais Givré (donjon 7) : 4:55-64
PALAIS = list(range(0x55, 0x65))
# L'Œil de l'Insomnis (île 8) : 1:b8-da
ILE_OEIL = [0xb8, 0xb9, 0xba, 0xc8, 0xc9, 0xca, 0xd8, 0xd9, 0xda]
SPIRALE = [0x3c, 0x3d, 0x3e, 0x3f, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x4b,
           0x4c, 0x4d, 0x4e, 0x4f, 0x50, 0x51, 0x52, 0x53, 0x54]
CATHEDRALE = [0x7b, 0x7c, 0x7d, 0x7f, 0x80, 0x81, 0x82, 0x83, 0x85, 0x86, 0x89, 0x8b, 0x8d, 0x8e,
              0x8f, 0x90, 0x91, 0x92, 0x93, 0xaa]
ROOM_MUSIC = [
    # le Phare / temple (plan d'un seul étage : pied 1b-14-15, tour 16-18-17, galerie 19-12-1a,
    # Jack 13 avant le combat ; 24 et 1c de l'ancien plan)
    (4, 0x41, [0x24, 0x1b, 0x1c, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x12, 0x13]),
    (1, 0x42, ILE_BRUME),   # l'île de la Brume dans le Réel (Port-Veille compris)
    (0, 0x42, ILE_BRUME),   # et dans le Songe
    (3, 0x43, [0x9e]),      # l'auberge de Port-Veille
    (2, 0x43, [0x9e]),      # et celle du Songe
    (1, 0x3d, ILE_GRELOT),  # Hameau-Grelot dans le Réel
    (0, 0x3d, ILE_GRELOT),  # et dans le Songe
    (3, 0x3d, [0x21, 0x22]),  # la maison de Lila, l'école
    (2, 0x3d, [0x21]),      # le rêve de Lila
    (1, 0x25, ILE_LAGUNE),  # la Lagune des Serments dans le Réel
    (0, 0x25, ILE_LAGUNE),  # et dans le Songe
    (3, 0x25, [0x23, 0x24]),  # la maison d'Héloïse et Gaspard, le club de plongée
    # le Récif Murmurant (donjon 3 ; la Murène lance la musique du boss)
    (5, 0x18, [0x44, 0x3f, 0x3e, 0x3b, 0x3a, 0x37, 0x38, 0x40, 0x3c, 0x3d, 0x39, 0x30, 0x2e, 0x35, 0x36, 0x2d]),
    # le Coffre à Jouets (donjon 2 ; Pantin-Sans-Fil lance la musique du boss en se réveillant)
    (4, 0x3b, [0x39, 0x37, 0x3a, 0x3b, 0x33, 0x32, 0x31, 0x34, 0x2d, 0x2c, 0x2e, 0x2b]),
    (1, 0x26, ILE_BRAISE),  # Mont-Braise dans le Réel
    (0, 0x26, ILE_BRAISE),  # et dans le Songe
    (5, 0x26, [0xb2]),      # la mine abandonnée
    # la Forge Endormie (donjon 4 ; Copiator lance la musique du boss)
    (4, 0x17, [0xae, 0xaf, 0xb0, 0xb1, 0xb2, 0xb6, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe, 0xbf]),
    (1, 0x13, ILE_ECHOS),   # l'île des Échos dans le Réel
    (0, 0x13, ILE_ECHOS),   # et dans le Songe
    (3, 0x13, [0x25]),      # la cabane du fossoyeur
    (5, 0x1a, CATHEDRALE),  # la Cathédrale des Échos (donjon 5)
    (3, 0x19, [0x26]),      # le souvenir : la maison de Marine à Mabe (Tarkin)
    (1, 0x15, ILE_NID),     # le Nid des Vents dans le Réel
    (0, 0x15, ILE_NID),     # et dans le Songe
    (4, 0x14, SPIRALE),     # la Spirale Céleste (donjon 6 ; l'Ombre de Marine lance la musique du boss)
    (1, 0x1c, ILE_SOMMEIL),  # l'île du Grand Sommeil dans le Réel
    (0, 0x1c, ILE_SOMMEIL),  # et dans le Songe
    (3, 0x1c, [0x27, 0x28, 0x29]),  # les maisons du veilleur, de la famille, de la chanteuse
    (4, 0x16, PALAIS),      # le Palais Givré (donjon 7 ; Givrolin lance la musique du boss)
    (1, 0x0b, [0xac]),      # la plage du forain (le Creuse-Rubis) : la Vallée Gerudo au violon
    (5, 0x18, [0xd0, 0xd1, 0xd2, 0xd3, 0xd4]),  # la Fosse de Bulle (sous l'eau) : la musique du Récif
    (0, 0x0b, [0xac]),      # et dans le Songe
    (5, 0x0c, [0xe9]),      # le Labyrinthe des Lynels (le 3e jeu du forain) : « Lift Off! » (Project Euro Mir)
    (5, 0x0b, [0xea]),      # l'arène du Mamono : la Vallée Gerudo, comme chez le forain
    (4, 0x1a, [0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7]),  # le Terrier des Serpents : la musique de la Cathédrale
    (1, 0x28, ILE_OEIL),    # l'Œil de l'Insomnis : la Tour Noire d'Ages (MUS_BLACK_TOWER)
    (0, 0x28, ILE_OEIL),    # et dans le Songe
    # La Tour Sans-Nuit (donjon 8) : la musique gagne un instrument à chaque étage (les cinq niveaux
    # du boss en rythme) ; l'Insomnis : silence en entrant, le boss lance son morceau
    (5, 0x47, [0xc0, 0xc1]),
    (5, 0x49, [0xc2, 0xc3, 0xc4]),
    (5, 0x4b, [0xc5, 0xc6, 0xc7]),
    (5, 0x37, [0xc8, 0xc9, 0xca]),
    (5, 0x3a, [0xcb]),
    (5, 0xf0, [0xcc]),
    # salle de test du boss en rythme (l'arène de l'ancien donjon 3 d'Ages) : silence en entrant
    # (SNDCTRL_STOPMUSIC) ; le boss lance son morceau quand Marine a parlé
    (4, 0xf0, [0x4a]),
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


def rhythm_notes(path, fin_intro):
    """Boss en rythme : la table des notes de la mélodie dans la boucle (celles qu'il faut frapper),
    pour code/ages/balladeRhythm.s. Temps en images depuis le début de la boucle ; l'horloge
    (wBalladeRhythmClock, comptée par le moteur son) vaut 1 au premier pas du morceau, d'où le +1."""
    tempo, bar, sections, (intro, loop) = parse(path)

    def croches(names):
        return sum(sum(e[2] for e in events(s, 'melodie', 'carre', sections[s]['melodie'],
                                            bar, tempo)[0] if e[0] == 'note') for s in names)

    intro_frames = round(croches(intro) * tempo)
    loop_frames = round(croches(loop) * tempo)
    lines = ['; Généré par tools/make_music.py depuis music/%s : ne pas éditer à la main.'
             % os.path.basename(path), '',
             '; Horloge au début du premier tour de la boucle (pas du moteur son)',
             '.define BALLADE_RHYTHM_INTRO $%04x' % (intro_frames + 1),
             '; Durée d\'un tour (la section A de la boucle)',
             '.define BALLADE_RHYTHM_LOOP $%04x' % loop_frames,
             '; Fin du chant de Marine (MUS_BALLADE_RYTHME_FIN) : le boss meurt',
             '.define BALLADE_RHYTHM_FIN_INTRO $%04x' % (fin_intro + 1), '',
             '; .dw début de la note (images depuis le début du tour), .db durée ; $ffff = fin du tour',
             'balladeRhythmNotes:']
    notes = loop_notes(path)
    for start, dur, p in notes:
        lines.append('\t.dw $%04x\n\t.db $%02x ; %s' % (start, dur, note_name(p)))
    lines += ['\t.dw $ffff', '']
    # Les niveaux 2 et 3 : la même phrase à frapper, sans intro (le jeu y passe au début d'un tour)
    for level in RHYTHM_LEVELS:
        lp = os.path.join(os.path.dirname(path), level)
        if [n[:2] for n in loop_notes(lp)] != [n[:2] for n in notes]:
            sys.exit('music/%s : la mélodie doit avoir exactement le rythme de music/%s'
                     % (level, os.path.basename(path)))
        if parse(lp)[3][0]:
            sys.exit('music/%s : pas d\'intro (le jeu y passe au début d\'un tour)' % level)
    with open(OUT_RHYTHM, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print('boss en rythme : %d notes à frapper par tour' % len(notes))


def loop_notes(path):
    """Les notes de la mélodie dans la boucle : [(début en images, durée, hauteur)]."""
    tempo, bar, sections, (intro, loop) = parse(path)
    pos, notes = 0.0, []
    for s in loop:
        for e in events(s, 'melodie', 'carre', sections[s]['melodie'], bar, tempo)[0]:
            if e[0] != 'note':
                continue
            start = round(pos * tempo)
            pos += e[2]
            if e[1] is not None:
                notes.append((start, round(pos * tempo) - start, e[1]))
    return notes


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
    intros = {}
    for fname, label in SONGS:
        try:
            lines, intro, loop = build_song(os.path.join(ROOT, 'music', fname), label)
        except ScoreError as e:
            sys.exit('music/%s : %s' % (fname, e))
        intros[fname] = intro
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
    rhythm_notes(os.path.join(ROOT, 'music', 'rythme.txt'), intros['rythme_fin.txt'])


if __name__ == '__main__':
    main()
