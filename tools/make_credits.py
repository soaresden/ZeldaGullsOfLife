"""Le générique de fin qui défile, comme celui de Link's Awakening (Denis : « pas de barre de
texte ! ») : story/generique.txt -> les tuiles et la carte de CUTSCENE_BALLADE_GENERIQUE
(code/ages/cutscenes/generique.s).

- Les lettres : la police du jeu (oracles-disasm/gfx/common/gfx_font.png, 8 x 16 : deux tuiles,
  le haut et le bas), une lettre par colonne de 8 pixels, chaque ligne centrée sur les 20
  colonnes de l'écran. Les tuiles sans doublons, à partir de $80 ($8800 : 128 au plus ; la $80 est
  vide).
- La carte : une rangée de 32 tuiles par rangée de l'écran (les colonnes 20-31 vides, pour copier
  une rangée entière d'un coup), d'abord 18 rangées vides (le texte arrive par le bas) ; à la fin,
  assez de rangées vides pour que la carte ne s'épuise pas. Une palette par rangée (0 blanc, 1 or).
- Le défilement : « FIN » s'arrête au milieu de l'écran (son haut à y = 64) à l'image STOP_FRAME
  de la musique ; la vitesse (en 1/256 de pixel par image) en découle.

Usage : python tools/make_credits.py   (lancé par build.sh)
Sortie : oracles-disasm/code/ages/balladeCreditsData.s (les palettes des rangées, les constantes),
balladeCreditsTiles.s (les tuiles), balladeCreditsMapFr.s, balladeCreditsMapEn.s (les cartes) : ces
trois-là en sections alignées sur 16 octets (la copie DMA du GBC ignore les 4 bits bas de la source).
"""
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
OUT = os.path.join(DISASM, 'code', 'ages')
# music/generique.txt : INTRO (4 mesures de 8) A (8) PONT (2 de 6) ZELDA (23 de 6) B (8) A2 (8)
# croches, à 15 images la croche
MUSIC_FRAMES = (4 * 8 + 8 * 8 + 2 * 6 + 23 * 6 + 8 * 8 + 8 * 8) * 15
STOP_FRAME = MUSIC_FRAMES - 300       # FIN reste 5 s au milieu avant la fin de la musique
SCREEN_ROWS, WIDTH = 18, 20
# Les lettres spéciales (oracles-disasm/tools/build/parseText.py, US_available)
SPECIAL = dict(zip("ÀÂÄÆÇÈÉÊËÎÏÑÖŒÙÛÜàâäæçèéêëîïñöœùûü",
                   [0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d,
                    0x8e, 0x8f, 0x90, 0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa,
                    0xab, 0xac, 0xad, 0xae, 0xaf, 0xb0]))


def read_credits():
    langs, cur = {}, None
    for line in open(os.path.join(ROOT, 'story', 'generique.txt'), encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('#'):
            continue
        m = re.match(r'== (\w+) ==$', line)
        if m:
            cur = langs.setdefault(m.group(1), [])
            continue
        if cur is not None:
            title = line.startswith('* ')
            cur.append((line[2:] if title else line).strip() and ((line[2:] if title else line).strip(), title))
    for lines in langs.values():
        while lines and not lines[-1]:
            lines.pop()
    return langs


def glyph(font, ch):
    code = SPECIAL.get(ch, ord(ch))
    assert ch in SPECIAL or 0x20 <= code < 0x7f, 'lettre absente de la police : %r' % ch
    x0, y0 = (code % 16) * 8, (code // 16) * 16
    return [tuple(1 if font.getpixel((x0 + x, y0 + y)) >= 128 else 0 for y in range(r, r + 8) for x in range(8))
            for r in (0, 8)]


def main():
    font = Image.open(os.path.join(DISASM, 'gfx', 'common', 'gfx_font.png')).convert('L')
    blank = (0,) * 64
    tiles = [blank]
    index = {blank: 0}

    def tile(t):
        if t not in index:
            index[t] = len(tiles)
            tiles.append(t)
        return 0x80 + index[t]

    out = {}
    for lang, lines in read_credits().items():
        rows, pals = [[0x80] * 32 for _ in range(SCREEN_ROWS)], [0] * SCREEN_ROWS
        for entry in lines:
            top, bottom = [0x80] * 32, [0x80] * 32
            pal = 0
            if entry:
                text, title = entry
                assert len(text) <= WIDTH, 'trop long (%d) : %s' % (len(text), text)
                x = (WIDTH - len(text)) // 2
                for i, ch in enumerate(text):
                    t, b = glyph(font, ch)
                    top[x + i], bottom[x + i] = tile(t), tile(b)
                pal = 1 if title else 0
            rows += [top, bottom]
            pals += [pal, pal]
        fin_row = len(rows) - 2
        end = fin_row * 8 - 64
        step = round(end * 256 / STOP_FRAME)
        assert 0 < step < 256, step
        # assez de rangées pour la dernière position (le haut de l'écran + 32 rangées chargées)
        while len(rows) < end // 8 + 34:
            rows.append([0x80] * 32)
            pals.append(0)
        out[lang] = (rows, pals, end, step)
    assert len(tiles) <= 128, 'trop de tuiles : %d' % len(tiles)
    # (generique.s prend la vitesse du français pour les deux langues)
    assert len({v[3] for v in out.values()}) == 1, 'les deux langues doivent défiler à la même vitesse'

    head = ['; Généré par tools/make_credits.py depuis story/generique.txt (ne pas modifier à la main) :',
            '; le générique qui défile (code/ages/cutscenes/generique.s).',
            '.define CREDITS_TILES %d' % len(tiles),
            '.define CREDITS_FADE_FRAME %d ; la musique finit : fondu' % (MUSIC_FRAMES - 60),
            '.define CREDITS_END_FRAME %d ; puis le retour au jeu' % (MUSIC_FRAMES + 60)]
    for lang, (rows, pals, end, step) in out.items():
        L = lang.upper()
        head += ['.define CREDITS_SCROLL_END_%s %d ; FIN au milieu de l\'écran (en pixels)' % (L, end),
                 '.define CREDITS_STEP_%s $%02x ; la vitesse, en 1/256 de pixel par image' % (L, step)]
    lines = head
    tl = ['; Généré par tools/make_credits.py (ne pas modifier à la main) : les tuiles du générique, dans',
          '; une section alignée sur 16 octets (la copie DMA du GBC ignore les 4 bits bas de la source)',
          '', '; Les tuiles (2 bits par pixel ; la lettre en couleur 3), à copier en $8800', 'creditsTiles:']
    for t in tiles:
        data = []
        for y in range(8):
            row = t[y * 8:y * 8 + 8]
            byte = sum(v << (7 - x) for x, v in enumerate(row))
            data += [byte, byte]
        tl.append('\t.db ' + ' '.join('$%02x' % b for b in data))
    tl += ['', '; Les attributs d\'une rangée (palette 0 : blanc ; palette 1 : or)', 'creditsAttr0:',
           '\t.dsb 32 $00', 'creditsAttr1:', '\t.dsb 32 $01']
    open(os.path.join(OUT, 'balladeCreditsTiles.s'), 'w', encoding='utf-8', newline='\n').write('\n'.join(tl) + '\n')
    for lang, (rows, pals, end, step) in out.items():
        lines += ['', '; La palette de chaque rangée (%s)' % lang, 'creditsPalettes%s:' % lang.capitalize()]
        for i in range(0, len(pals), 32):
            lines.append('\t.db ' + ' '.join(str(p) for p in pals[i:i + 32]))
        m = ['; Généré par tools/make_credits.py (ne pas modifier à la main) : la carte du générique (%s),' % lang,
             '; 32 tuiles par rangée', 'creditsMap%s:' % lang.capitalize()]
        for r in rows:
            m.append('\t.db ' + ' '.join('$%02x' % b for b in r))
        open(os.path.join(OUT, 'balladeCreditsMap%s.s' % lang.capitalize()), 'w', encoding='utf-8',
             newline='\n').write('\n'.join(m) + '\n')
    open(os.path.join(OUT, 'balladeCreditsData.s'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('générique : %d tuiles ; %s' % (len(tiles), ', '.join(
        '%s %d rangées, FIN à %d px, vitesse %d/256' % (k, len(v[0]), v[2], v[3]) for k, v in out.items())))


if __name__ == '__main__':
    main()
