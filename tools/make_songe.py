"""Prépare les décors du Songe : copies bleutées des décors du Réel.

- décor $7d : village du Songe (copie du $10, village du passé)
- décor $7e : plage du Songe (copie du $18, plage de l'île Croissant)
- décor $7f : auberge du Songe (copie du $2b, intérieur)
- décor $7c : Hameau-Grelot du Songe (copie du $00, la ville de Lynna du présent)
- décor $06 : Mont-Braise du Songe (copie du $1e, la Crête Roulante du passé ; à la place de la
  ville de Symétrie en ruine, qu'on ne visite pas)
- décor $07 : l'île des Échos du Songe (copie du $13, le cimetière de Yoll du passé ; à la place de
  la ville de Symétrie restaurée) : couleur sépia, pas bleutée (une île de souvenirs)

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
# décor du Songe -> décor du Réel copié (0x3b : la Spirale Céleste, pas un Songe : le Donjon des
# Ailes recopié à l'index de donjon 6, en bleuté)
COPIES = {0x7d: 0x10, 0x7e: 0x18, 0x7f: 0x2b, 0x7c: 0x00, 0x7b: 0x00, 0x06: 0x1e, 0x07: 0x13, 0x08: 0x1a,
          0x3b: 0x37, 0x0d: 0x10, 0x0e: 0x10, 0x0f: 0x02, 0x0c: 0x02, 0x67: 0x3d, 0x68: 0x18,
          0x69: 0x59, 0x6a: 0x18}

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
    (0x07, 'PALH_TILESET_YOLL_GRAVEYARD_ALTERNATE', 0xd2, 'PALH_SONGE_ECHOS',
     '$0f, $01, UNIQUE_GFXH_YOLL_GRAVEYARD, GFXH_TILESET_OVERWORLD_PAST, PALH_SONGE_ECHOS, $01, $00, $01'),
    (0x08, 'PALH_TILESET_TALUS_PEAKS_PAST', 0xd3, 'PALH_SONGE_NID',
     '$0f, $01, UNIQUE_GFXH_TALUS_PEAKS, GFXH_TILESET_OVERWORLD_PAST, PALH_SONGE_NID, $06, $00, $01'),
    # La Spirale Céleste (donjon 6) : le Donjon des Ailes (déjà pris par le Coffre à Jouets, donjon
    # 2) recopié à l'index de donjon 6, aux couleurs (bleutées) du ciel
    (0x3b, 'PALH_TILESET_WING_DUNGEON', 0xd4, 'PALH_SPIRALE',
     '$26, $88, UNIQUE_GFXH_NONE, GFXH_TILESET_WING_DUNGEON, PALH_SPIRALE, $22, $04, $10'),
    # L'île du Grand Sommeil (île 7) : le village du passé (décor $10) sous la neige, à la place des
    # Hautes Terres de Nuun ($0d, $0e : on ne les visite pas) ; le $0d est le Réel (glace), le $0e
    # son Songe (glace bleutée)
    (0x0d, 'PALH_TILESET_LYNNA_VILLAGE', 0xd6, 'PALH_GIVRE',
     '$0f, $81, UNIQUE_GFXH_LYNNA_CITY_2, GFXH_TILESET_OVERWORLD_PAST, PALH_GIVRE, $0f, $02, $00'),
    (0x0e, 'PALH_TILESET_LYNNA_VILLAGE', 0xd7, 'PALH_SONGE_GIVRE',
     '$0f, $01, UNIQUE_GFXH_LYNNA_CITY_2, GFXH_TILESET_OVERWORLD_PAST, PALH_SONGE_GIVRE, $0f, $00, $00'),
    # Le Palais Givré (donjon 7) : la Grotte Lunaire d'Ages ($38, ses cristaux), passée à l'index
    # de donjon 7 et en glace (pas de copie : les salles de la Grotte Lunaire ne servent plus)
    (0x38, 'PALH_TILESET_MOONLIT_GROTTO', 0xd8, 'PALH_PALAIS',
     '$27, $08, UNIQUE_GFXH_NONE, GFXH_TILESET_MOONLIT_GROTTO, PALH_PALAIS, $23, $04, $10'),
    # L'Œil de l'Insomnis (île 8) : la Tour Noire d'Ages, dehors, côté présent ($02) ; le Réel en
    # est une copie au $0f (REEL) ; son Songe au $0c (on ne visite pas les Hautes Terres de Nuun)
    (0x0c, 'PALH_TILESET_BLACK_TOWER_OUTSIDE_PRESENT', 0xda, 'PALH_SONGE_TOUR',
     '$0f, $01, UNIQUE_GFXH_BLACK_TOWER_OUTSIDE, GFXH_TILESET_OVERWORLD_PRESENT, PALH_SONGE_TOUR, $02, $00, $01'),
    # La Tour Sans-Nuit (donjon 8) : le Donjon du Crâne d'Ages ($39), à l'index de donjon 8, de nuit
    (0x39, 'PALH_TILESET_SKULL_DUNGEON', 0xdb, 'PALH_TOUR',
     '$28, $08, UNIQUE_GFXH_NONE, GFXH_TILESET_SKULL_DUNGEON, PALH_TOUR, $24, $04, $10'),
]
SEPIA = (0x07,)   # ces Songes-là sont sépia (voir sepia())
ICE = (0x0d, 0x38)        # en glace (voir ice()) ; le $0e : la glace, puis le Songe
ICE_DREAM = (0x0e,)
NIGHT = (0x39,)           # de nuit (voir night()) : la Tour Sans-Nuit
# (décor, brique, 4 tuiles + 4 attributs) : la glace = le sol du village (9e) aux couleurs de l'eau
# (palette 6) ; dans le Palais, le dallage f8 (80) aux couleurs du f9 (palette 2). Et le cristal du
# Songe (PART_SWITCH dehors = la brique 9e, 9f une fois frappé) : le losange db (éteint), le carreau
# da (allumé), aux couleurs de l'eau ; solides. Dernier nombre : la collision
PATCHES = [(0x0d, 0xea, '9e9e9e9e0e0e0e0e', 0), (0x0e, 0xea, '9e9e9e9e0e0e0e0e', 0),
           (0x38, 0x8a, '808080800a0a0a0a', 0),
           (0x0e, 0x9e, 'e6e8e7e90e0e0e0e', 0x0f), (0x0e, 0x9f, 'bebebebe0e2e4e6e', 0x0f)]
# Copies du Réel : (décor, octets du décor) ; mêmes palettes, drapeau « passé » ($80)
REEL = [
    (0x7b, '$0f, $81, UNIQUE_GFXH_LYNNA_CITY_1, GFXH_TILESET_OVERWORLD_PRESENT, PALH_TILESET_LYNNA_CITY, $00, $02, $00'),
    # L'Œil de l'Insomnis (île 8) : la Tour Noire (copie du $02, présent)
    (0x0f, '$0f, $81, UNIQUE_GFXH_BLACK_TOWER_OUTSIDE, GFXH_TILESET_OVERWORLD_PRESENT, PALH_TILESET_BLACK_TOWER_OUTSIDE_PRESENT, $02, $02, $01'),
    # La Fosse de Bulle (la plongée, au large de la Lagune) : le Récif sous l'eau (3d), à l'index
    # de donjon 9 (à la place du Chemin du Maku d'Ages, qu'on ne visite pas)
    (0x67, '$29, $c8, UNIQUE_GFXH_NONE, GFXH_TILESET_MERMAIDS_CAVE, PALH_TILESET_MERMAIDS_CAVE_PAST_UNDERWATER, $26, $05, $13'),
    # La plage du forain (1:ac) : la plage ($18), avec les chiffres et les monstres du Mamono
    # (tools/make_mamono.py)
    (0x68, '$0f, $81, UNIQUE_GFXH_CRESCENT_ISLAND, GFXH_TILESET_OVERWORLD_PAST, PALH_TILESET_CRESCENT_ISLAND_PAST, $04, $02, $01'),
    # Le Labyrinthe des Lynels (5:e9, le 3e jeu du forain) : une grande salle de grotte ($59, sans
    # donjon), redessinée par tools/make_pacman.py, aux couleurs de PALH_LABYRINTHE, sans animation
    (0x69, '$2f, $10, UNIQUE_GFXH_NONE, GFXH_TILESET_CAVE, PALH_LABYRINTHE, $16, $05, $ff'),
    # L'arène du Mamono (5:ea) : une grande salle (groupe 5) avec le sable et la mer de la plage
    # ($18), les chiffres de 1 à 40 (tools/make_mamono.py) ; collisions du dehors, époque « Réel » ;
    # sans animation (celle de la mer réécrirait des tuiles des chiffres)
    (0x6a, '$0f, $90, UNIQUE_GFXH_CRESCENT_ISLAND, GFXH_TILESET_OVERWORLD_PAST, PALH_TILESET_CRESCENT_ISLAND_PAST, $04, $05, $ff'),
]
# En-têtes de palette écrits à la main dans paletteHeaders.s (hors du bloc du Songe) : à compter
# dans NUM_PALETTE_HEADERS. $d5 PALH_OMBRE : l'Ombre de Marine (le Swoop, palette 6 des sprites) ;
# $d9 PALH_GIVROLIN : Givrolin (le Ramrock, palette 6 des sprites) ; $dc PALH_PHOTO : les photos ;
# $dd PALH_FANTOME : les fantômes du 4F de la Tour ; $de PALH_LABYRINTHE : le Labyrinthe des Lynels
OTHER_HEADERS = (0xd5, 0xd9, 0xdc, 0xdd, 0xde)
BEGIN, END = '; BALLADE-SONGE-DEBUT (tools/make_songe.py)', '; BALLADE-SONGE-FIN'


def dream(r, g, b):
    """Couleur du Songe : la même lumière, tirée vers un bleu-violet pâle."""
    lum = 0.30 * r + 0.59 * g + 0.11 * b
    tr, tg, tb = lum * 0.55 + 2, lum * 0.75 + 3, min(31, lum * 0.85 + 9)
    k = 0.35  # part de la couleur d'origine
    return tuple(max(0, min(31, round(o * k + t * (1 - k)))) for o, t in ((r, tr), (g, tg), (b, tb)))


def ice(r, g, b):
    """Couleur de l'île du Grand Sommeil : la même lumière, en neige et en glace (blanc bleuté)."""
    lum = 0.30 * r + 0.59 * g + 0.11 * b
    light = min(31, lum * 1.3 + 3)      # plus clair : le sol devient de la neige
    tr, tg, tb = light * 0.9, light * 0.95, min(31, light * 0.85 + 6)
    k = 0.12
    return tuple(max(0, min(31, round(o * k + t * (1 - k)))) for o, t in ((r, tr), (g, tg), (b, tb)))


def night(r, g, b):
    """Couleur de la Tour Sans-Nuit : la même lumière, plus sombre, en violet de nuit."""
    lum = 0.30 * r + 0.59 * g + 0.11 * b
    tr, tg, tb = lum * 0.75 + 1, lum * 0.5 + 1, min(31, lum * 0.95 + 4)
    k = 0.15
    return tuple(max(0, min(31, round(o * k + t * (1 - k)))) for o, t in ((r, tr), (g, tg), (b, tb)))


def recolor(tileset, c):
    if tileset in NIGHT:
        return night(*c)
    if tileset in SEPIA:
        return sepia(*c)
    if tileset in ICE:
        return ice(*c)
    if tileset in ICE_DREAM:
        return dream(*ice(*c))
    return dream(*c)


def sepia(r, g, b):
    """Couleur d'un Songe-souvenir : la même lumière, en sépia (une vieille photo)."""
    lum = 0.30 * r + 0.59 * g + 0.11 * b
    tr, tg, tb = min(31, lum * 1.0 + 4), lum * 0.82 + 2, lum * 0.55 + 1
    k = 0.25
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
            pal_lines.append('\tm_RGB16 $%02x $%02x $%02x' % recolor(tileset, c))
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

    # (l'en-tête PALH_TITLE est le $cf, entre deux décors du Songe ; les en-têtes écrits à la main
    # hors du bloc, comme PALH_OMBRE, sont dans OTHER_HEADERS)
    count = max(max(s[2] for s in SONGE), 0xcf, *OTHER_HEADERS) + 1
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
    # La glace (TILETYPE_ICE : $ea dehors, $8a dans les donjons) n'est dessinée dans aucun de ces
    # décors : on lui donne des tuiles (4 tuiles + 4 attributs) et sa collision
    for tileset, tile, mapping, collision in PATCHES:
        d = os.path.join(DISASM, 'tileset_layouts_expanded', 'ages', 'tileset%s%02x.bin')
        with open(d % ('Mappings', tileset), 'r+b') as f:
            f.seek(tile * 8)
            f.write(bytes.fromhex(mapping))
        with open(d % ('Collisions', tileset), 'r+b') as f:
            f.seek(tile)
            f.write(bytes([collision]))
    print('décors du Songe : %s' % ', '.join('$%02x' % s[0] for s in SONGE))


main()
