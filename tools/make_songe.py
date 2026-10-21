"""Prépare les décors du Songe : copies bleutées des décors du Réel.

- décor $7d : village du Songe (copie du $10, village du passé)
- décor $7e : plage du Songe (copie du $18, plage de l'île Croissant)
- décor $7f : auberge du Songe (copie du $2b, intérieur)
- décor $7c : Hameau-Grelot du Songe (copie du $00, la ville de Lynna du présent)
- décor $06 : Mont-Braise du Songe (copie du $1e, la Crête Roulante du passé ; à la place de la
  ville de Symétrie en ruine, qu'on ne visite pas)

Et des copies du Réel, quand le décor d'origine est un décor du « présent » d'Ages (le Réel est
le « passé » : TILESETFLAG_PAST, pour le symbole de l'époque, la carte...) :
- décor $7b : Hameau-Grelot (copie du $00, mêmes couleurs)

Les salles du Songe sont dans le groupe 0 (le « présent » d'Ages) et le groupe 2 pour les
intérieurs : mêmes numéros que dans le Réel, si bien qu'on passe de l'un à l'autre au même
endroit, comme avec la harpe d'Ages. Les décors du Songe lisent leurs salles dans le groupe de
disposition 0 (room00SS.bin) ; l'auberge garde le 3 (même salle que dans le Réel).

Dans hack-base, chaque décor a aussi ses propres images de briques (gfx/ages/gfx_tilesetXX.png),
leur disposition (tileset_layouts_expanded/ages/tilesetMappingsXX.bin) et leurs collisions
(tilesetCollisionsXX.bin) : on les recopie depuis le décor du Réel.

Écrit dans oracles-disasm : data/ages/tilesets.s, paletteHeaders.s, paletteData.s, et les fichiers
du décor ci-dessus.
Usage : python tools/make_songe.py
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
DATA = os.path.join(DISASM, 'data', 'ages')
COPIES = {0x7d: 0x10, 0x7e: 0x18, 0x7f: 0x2b, 0x7c: 0x00, 0x7b: 0x00, 0x06: 0x1e}   # décor du Songe -> décor du Réel copié

# (décor, copie de, en-tête de palette d'origine, nouvel en-tête, octets du décor)
SONGE = [
    (0x7d, 'PALH_TILESET_LYNNA_VILLAGE', 0xcc, 'PALH_SONGE_VILLAGE',
     '$0f, $01, UNIQUE_GFXH_LYNNA_CITY_2, GFXH_TILESET_OVERWORLD_PAST, PALH_SONGE_VILLAGE, $0f, $00, $00'),
    (0x7e, 'PALH_TILESET_CRESCENT_ISLAND_PAST', 0xcd, 'PALH_SONGE_PLAGE',
     '$0f, $01, UNIQUE_GFXH_CRESCENT_ISLAND, GFXH_TILESET_OVERWORLD_PAST, PALH_SONGE_PLAGE, $04, $00, $01'),
    (0x7f, 'PALH_TILESET_INDOORS_PRESENT', 0xce, 'PALH_SONGE_AUBERGE',
     '$1f, $04, UNIQUE_GFXH_NONE, GFXH_TILESET_INDOORS, PALH_SONGE_AUBERGE, $15, $03, $10'),
    # (en-tête $d0 : le $cf est celui de l'écran titre, PALH_TITLE)
    (0x7c, 'PALH_TILESET_LYNNA_CITY', 0xd0, 'PALH_SONGE_GRELOT',
     '$0f, $01, UNIQUE_GFXH_LYNNA_CITY_1, GFXH_TILESET_OVERWORLD_PRESENT, PALH_SONGE_GRELOT, $00, $00, $00'),
    (0x06, 'PALH_TILESET_ROLLING_RIDGE_PAST', 0xd1, 'PALH_SONGE_BRAISE',
     '$0f, $01, UNIQUE_GFXH_ROLLING_RIDGE_PAST, GFXH_TILESET_OVERWORLD_PAST, PALH_SONGE_BRAISE, $09, $00, $02'),
]
# Copies du Réel : (décor, octets du décor) ; mêmes palettes, drapeau « passé » ($80)
REEL = [
    (0x7b, '$0f, $81, UNIQUE_GFXH_LYNNA_CITY_1, GFXH_TILESET_OVERWORLD_PRESENT, PALH_TILESET_LYNNA_CITY, $00, $02, $00'),
]
BEGIN, END = '; BALLADE-SONGE-DEBUT (tools/make_songe.py)', '; BALLADE-SONGE-FIN'


def dream(r, g, b):
    """Couleur du Songe : la même lumière, tirée vers un bleu-violet pâle."""
    lum = 0.30 * r + 0.59 * g + 0.11 * b
    tr, tg, tb = lum * 0.55 + 2, lum * 0.75 + 3, min(31, lum * 0.85 + 9)
    k = 0.35  # part de la couleur d'origine
    return tuple(max(0, min(31, round(o * k + t * (1 - k)))) for o, t in ((r, tr), (g, tg), (b, tb)))


# Décors du Songe qui auraient leur propre palette 0 (toits) : aucun, car la barre d'état (cœurs, fond
# des cases B et A) utilise aussi cette palette et doit rester la même partout.
OUTDOOR = ()


def palette(data, label):
    """Couleurs (r, g, b) d'une étiquette de paletteData.s."""
    colors = re.search(r'^%s:\n((?:\tm_RGB16 .*\n|\n)+)' % label, data, re.M).group(1)
    return [tuple(int(v[1:], 16) for v in l.split()[1:4]) for l in colors.split('\n') if 'm_RGB16' in l]


def replace_block(text, block):
    if BEGIN in text:
        a, b = text.index(BEGIN), text.index(END) + len(END)
        return text[:a] + block + text[b:]
    return text.rstrip('\n') + '\n\n' + block + '\n'


def main():
    headers = open(os.path.join(DATA, 'paletteHeaders.s'), encoding='utf-8').read()
    data = open(os.path.join(DATA, 'paletteData.s'), encoding='utf-8').read()
    tilesets = open(os.path.join(DATA, 'tilesets.s'), encoding='utf-8').read()

    hdr_lines, pal_lines = [BEGIN], [BEGIN]
    for tileset, orig, idx, name, line in SONGE:
        m = re.search(r'm_PaletteHeaderStart \$[0-9a-f]+, %s\n\tm_PaletteHeaderBg  (\d), (\d), (\w+)' % orig, headers)
        first, count, label = int(m.group(1)), int(m.group(2)), m.group(3)
        rgb = palette(data, label)[:count * 4]
        short = name[5:].title().replace('_', '')
        hdr_lines += ['m_PaletteHeaderStart $%02x, %s' % (idx, name),
                      '\tm_PaletteHeaderBg  %d, %d, paletteData%s' % (first, count, short)]
        if tileset in OUTDOOR:
            # Dehors, la palette 0 (les toits rouges...) est commune à tout le jeu : le Songe a la
            # sienne, et le décor du Réel remet celle d'origine en revenant du Songe
            hdr_lines.append('\tm_PaletteHeaderBg  0, 1, paletteData%s0' % short)
            start = m.group(0) + '\n'
            restore = '\tm_PaletteHeaderBg  0, 1, paletteData48e0 ; BALLADE: après le Songe\n'
            if start + restore not in headers:
                headers = headers.replace(start, start + restore, 1)
        hdr_lines += ['\tm_PaletteHeaderEnd', '']
        pal_lines.append('paletteData%s: ; Songe : %s en bleuté' % (short, label))
        for i, c in enumerate(rgb):
            pal_lines.append('\tm_RGB16 $%02x $%02x $%02x' % dream(*c))
            if i % 4 == 3:
                pal_lines.append('')
        if tileset in OUTDOOR:
            pal_lines.append('paletteData%s0: ; Songe : la palette 0 (paletteData48e0) en bleuté' % short)
            # sauf la couleur 2, la crème de la barre d'état : elle sert aussi de fond derrière
            # l'objet des cases B et A (sinon l'épée a un fond coloré dans le Songe)
            for i, c in enumerate(palette(data, 'paletteData48e0')[:4]):
                pal_lines.append('\tm_RGB16 $%02x $%02x $%02x' % (c if i == 2 else dream(*c)))
            pal_lines.append('')
        tilesets = re.sub(r'\t\.db [^\n]*; Tileset 0x%02x\n' % tileset,
                          '\t.db %s ; Tileset 0x%02x BALLADE: Songe\n' % (line, tileset), tilesets)
    for tileset, line in REEL:
        tilesets = re.sub(r'\t\.db [^\n]*; Tileset 0x%02x[^\n]*\n' % tileset,
                          '\t.db %s ; Tileset 0x%02x BALLADE: Réel\n' % (line, tileset), tilesets)
    hdr_lines.append(END)
    pal_lines.append(END)

    # Les autres décors où l'on peut arriver depuis le Songe remettent aussi la palette 0
    # (le Phare Éteint : on y entre par sa porte du Songe)
    for orig in ('PALH_TILESET_SPIRITS_GRAVE',):
        m = re.search(r'm_PaletteHeaderStart \$[0-9a-f]+, %s\n\tm_PaletteHeaderBg  [^\n]+' % orig, headers)
        start = m.group(0) + '\n'
        restore = '\tm_PaletteHeaderBg  0, 1, paletteData48e0 ; BALLADE: après le Songe\n'
        if start + restore not in headers:
            headers = headers.replace(start, start + restore, 1)

    # (l'en-tête PALH_TITLE est le $cf, entre deux décors du Songe)
    count = max(max(s[2] for s in SONGE), 0xcf) + 1
    headers = re.sub(r'\.define NUM_PALETTE_HEADERS \$[0-9a-f]+[^\n]*',
                     '.define NUM_PALETTE_HEADERS $%02x ; BALLADE: + film, Songe, titre' % count, headers)
    headers = replace_block(headers, '\n'.join(hdr_lines))
    data = replace_block(data, '\n'.join(pal_lines))
    for name, text in (('paletteHeaders.s', headers), ('paletteData.s', data), ('tilesets.s', tilesets)):
        with open(os.path.join(DATA, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
    for dst, src in COPIES.items():
        shutil.copyfile(os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % src),
                        os.path.join(DISASM, 'gfx', 'ages', 'gfx_tileset%02x.png' % dst))
        for kind in ('Mappings', 'Collisions'):
            d = os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tileset%s%%02x.bin' % kind)
            shutil.copyfile(d % src, d % dst)
    print('décors du Songe : %s' % ', '.join('$%02x' % s[0] for s in SONGE))


main()
