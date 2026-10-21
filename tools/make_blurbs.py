"""Le nom des donjons sur la carte (le cartouche en haut à gauche : « L-1 / Spirit's Grave »).

Ce nom est une image par donjon (gfx_compressible/ages/gfx_blurb_dN.png, 128 x 24) : la moitié
gauche (24 lignes) est le haut du cartouche (« L-1 » puis la 1re ligne du nom), la moitié droite
(16 premières lignes) le bas (la 2e ligne du nom et le bord). Les lettres sont reprises des noms
d'origine d'Ages (Dungeon, Moonlit, Grotto, Skull, Crown, Path, Spirit's, Grave), dans le même
style ; le L, le E, le P (celui de « Path » est coupé en haut dans l'image d'origine), le T, le J,
le f, le y, le R, le c, le m et les accents de É, à et é sont dessinés ici, à leur image, et le h est fait d'un n et de
la hampe du l.

Écrit gfx_blurb_dN.png (anglais) et gfx_blurb_dN_fr.png (français : « N-1 », choisi au chargement
selon la langue, voir balladeLangGfxHeaders dans data/ages/gfxHeaders.s). Les images d'origine sont
relues dans git (upstream/hack-base) : on peut relancer le script.

Usage : python tools/make_blurbs.py
"""
import io
import os
import shutil
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
GFX = os.path.join(DISASM, 'gfx_compressible', 'ages')

# Le nom de chaque donjon : (1re ligne, 2e ligne) en anglais et en français
NAMES = {
    1: {'en': ('Dark', 'Lighthouse'), 'fr': ('Phare', 'Éteint')},
    2: {'en': ('Toy', 'Chest'), 'fr': ('Coffre à', 'Jouets')},
    3: {'en': ('Murmuring', 'Reef'), 'fr': ('Récif', 'Murmurant')},
}

# Lettres dessinées à la main (. vide, : contour clair, o ombre, # trait) ; la dernière ligne est
# posée sur la ligne de base
DRAWN = {
    'L': ['#o....', '#o....', '#o....', '#o....', '#o....', '#o....', '#####:'],
    'E': ['#####:', '#o....', '#o....', '####:.', '#o....', '#o....', '#####:'],
    'P': ['#####:', '#o.:##', '#o..#o', '#o##o:', '#o....', '#o....', '#o....'],
    'T': ['######', '..#o..', '..#o..', '..#o..', '..#o..', '..#o..', '..#o..'],
    'J': ['...##', '...#o', '...#o', '...#o', '#o.#o', '#o:#o', ':##o:'],
    'R': ['#####:', '#o.:##', '#o..#o', '#o##o:', '#o.#o.', '#o..#o', '#o..#o'],
    'c': ['....', '....', ':##:', '#o.#', '#o..', '#o.#', ':##:'],
    'm': ['.......', '.......', '##:##:.', '#o##o##', '#o.#o#o', '#o.#o#o', '#o.#o#o'],
    # 11 lignes : le f monte comme le l, le y descend sous la ligne de base
    'f': ['....', '.:##', '.#o.', '.#o.', '##o#', '.#o.', '.#o.', '.#o.', '.#o.', '....', '....'],
    'y': ['.....', '.....', '.....', '.....', '##.##', '#o.#o', '#o.#o', ':###o', '...#o', '...#o', ':##o:'],
}
GRAVE = ['.#o..', '..:#.']        # l'accent grave, au-dessus d'une minuscule (à)
ACUTE = ['..:#.', '.#o..']        # l'accent aigu, au-dessus d'une minuscule (é)
ACCENT = ['...:#', '..#o.']        # l'accent aigu, au-dessus d'une majuscule
SMALL_N = ['##o.#o', '#o#o#o', '#o.##o', '#o..#o', '#o..#o']   # « N » de « N-1 », petite police


def original(name):
    png = subprocess.run(['git', 'show', 'upstream/hack-base:gfx_compressible/ages/gfx_blurb_%s.png' % name],
                         cwd=DISASM, capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png))
    im.load()
    return im


def runs(px, x0, x1, y0, y1):
    """Les lettres d'une ligne : colonnes non vides séparées par une colonne vide."""
    out, cur = [], None
    for x in range(x0, x1):
        full = any(px[x, y] for y in range(y0, y1))
        if full and cur is None:
            cur = x
        if not full and cur is not None:
            out.append((cur, x))
            cur = None
    if cur is not None:
        out.append((cur, x1))
    return out


def font():
    """Lettre -> lignes de pixels (de 9 lignes au-dessus de la ligne de base à 2 en dessous)."""
    glyphs = {}
    # (image, moitié, lignes, mot, lettres à ignorer)
    sources = [('d2', 1, (1, 10), 'Dungeon'), ('d3', 0, (13, 24), 'Moonlit'), ('d3', 1, (1, 10), 'Grotto'),
               ('d4', 0, (13, 24), 'Skull'), ('d5', 0, (13, 24), 'Crown'), ('makupath', 1, (0, 10), '?a??'),
               ('d1', 1, (1, 10), 'G?ve'), ('d1', 0, (13, 24), 'Spiri?s')]
    for name, half, (y0, y1), word in sources:
        im = original(name)
        px = im.load()
        x0, x1 = 3 + 64 * half, 61 + 64 * half
        found = runs(px, x0, x1, y0, y1)
        assert len(found) == len(word), (name, word, found)
        # ligne de base : la dernière ligne de la majuscule (jamais de jambage)
        first = found[0] if word[0] != '|' else found[1]
        base = max(y for y in range(y0, y1) for x in range(*first) if px[x, y])
        for letter, (a, b) in zip(word, found):
            if letter in '|?' or letter in glyphs:
                continue
            glyphs[letter] = [[px[x, y] if 0 <= y < 24 else 0 for x in range(a, b)] for y in range(base - 8, base + 3)]
    code = {'.': 0, ':': 1, 'o': 2, '#': 3}
    for letter, rows in DRAWN.items():
        w = len(rows[0])
        pad = [[0] * w] * ((11 - len(rows)) // 2)
        glyphs[letter] = pad + [[code[c] for c in r] for r in rows] + pad
    # h : le n, avec la hampe du l au-dessus
    h = [list(r) for r in glyphs['n']]
    for y, row in enumerate(glyphs['l']):
        if not any(h[y]) and any(row):
            h[y] = row[:2] + [0] * (len(h[y]) - 2)
    glyphs['h'] = h
    e = [list(r) for r in glyphs['E']]
    for i, r in enumerate(ACCENT):
        e[i] = [code[c] for c in r.ljust(len(e[i]), '.')]
    glyphs['É'] = e
    a = [list(r) for r in glyphs['a']]
    for i, r in enumerate(GRAVE):
        a[1 + i] = [code[c] for c in r.ljust(len(a[1 + i]), '.')]
    glyphs['à'] = a
    e = [list(r) for r in glyphs['e']]
    for i, r in enumerate(ACUTE):
        e[1 + i] = [code[c] for c in r.ljust(len(e[1 + i]), '.')]
    glyphs['é'] = e
    return glyphs


def write_line(px, glyphs, text, x0, x1, base):
    letters = [glyphs[c] if c != ' ' else [[0] * 3] * 11 for c in text]
    width = sum(len(g[0]) for g in letters) + len(letters) - 1
    assert width <= x1 - x0, (text, width, x1 - x0)
    x = x0 + (x1 - x0 - width) // 2
    for g in letters:
        for dy, row in enumerate(g):
            for dx, v in enumerate(row):
                if v:
                    px[x + dx, base - 8 + dy] = v
        x += len(g[0]) + 1


def make(n, lang, glyphs):
    im = original('d%d' % n)
    px = im.load()
    # Effacer l'ancien nom (on garde le cadre et « L-n »)
    for y in range(13, 24):
        for x in range(3, 61):
            px[x, y] = 0
    for y in range(0, 11):
        for x in range(67, 125):
            px[x, y] = 0
    line1, line2 = NAMES[n][lang]
    write_line(px, glyphs, line1, 3, 61, 21)
    write_line(px, glyphs, line2, 67, 125, 8)
    if lang == 'fr':
        # « L-1 » -> « N-1 » (le L de la petite police est en x 21-26, lignes 2-7)
        for y in range(2, 8):
            for x in range(20, 28):
                px[x, y] = 0
        code = {'.': 0, ':': 1, 'o': 2, '#': 3}
        for dy, row in enumerate(SMALL_N):
            for dx, c in enumerate(row):
                px[20 + dx, 3 + dy] = code[c]
    suffix = '_fr' if lang == 'fr' else ''
    dst = os.path.join(GFX, 'gfx_blurb_d%d%s.png' % (n, suffix))
    im.save(dst)
    shutil.copyfile(os.path.join(GFX, 'gfx_blurb_d%d.properties' % n),
                    os.path.join(GFX, 'gfx_blurb_d%d%s.properties' % (n, suffix))) if suffix else None
    print('->', os.path.relpath(dst, ROOT))


def main():
    glyphs = font()
    for n in NAMES:
        for lang in ('en', 'fr'):
            make(n, lang, glyphs)


main()
