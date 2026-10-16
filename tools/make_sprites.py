"""Fabrique les sprites du jeu à partir des dessins texte du dossier art/.

Marine en mouette (art/marine_mouette.txt) remplace les 3 images du perroquet
« je-sais-tout » dans une copie de spr_bunny_parrot.png : on garde ainsi la
même disposition de tuiles et on peut réutiliser ses animations.

Couleurs des sprites (fichiers spr_*, couleurs inversées par gfx.py) :
noir = transparent, gris foncé = couleur 1, gris clair = couleur 2, blanc = couleur 3.

Usage : python tools/make_sprites.py   (depuis la racine du dépôt)
"""
import io
import os
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
GREY = {'.': 0, 'k': 85, 'r': 170, 'w': 255}


def read_frames(path):
    rows = [l.rstrip('\n') for l in open(path, encoding='utf-8')
            if l.strip() and not l.startswith('#')]
    assert len(rows) % 16 == 0 and all(len(r) == 16 for r in rows), path
    return [rows[i:i + 16] for i in range(0, len(rows), 16)]


def main():
    src = os.path.join(DISASM, 'gfx_compressible', 'ages', 'spr_bunny_parrot.png')
    im = Image.open(src).convert('L')
    frames = read_frames(os.path.join(ROOT, 'art', 'marine_mouette.txt'))
    # Images du perroquet : colonnes 80-127 (tuiles $14-$1f)
    for n, frame in enumerate(frames):
        for y, row in enumerate(frame):
            for x, c in enumerate(row):
                im.putpixel((80 + n * 16 + x, y), GREY[c])
    out = im.convert('P', palette=Image.ADAPTIVE)
    pal = [0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255]
    out = Image.new('P', im.size)
    out.putpalette(pal + [0] * (768 - len(pal)))
    out.putdata([{0: 0, 85: 1, 170: 2, 255: 3}[v] for v in im.getdata()])
    dst = os.path.join(DISASM, 'gfx_compressible', 'ages', 'spr_marine_gull.png')
    out.save(dst)
    print('->', os.path.relpath(dst, ROOT))

    # Marine humaine (le Songe) : ses 4 poses de villageoise (face, dos, profil x2), d'après la
    # branche sprites/marin d'oracles-disasm (Marine dessinée au format Oracle par ses auteurs)
    sheet = Image.new('P', (128, 16), 0)
    sheet.putpalette(pal + [0] * (768 - len(pal)))
    index = {'.': 0, 'k': 1, 'r': 2, 'w': 3}
    for n, frame in enumerate(read_frames(os.path.join(ROOT, 'art', 'marine_humaine.txt'))):
        for y, row in enumerate(frame):
            for x, c in enumerate(row):
                sheet.putpixel((n * 16 + x, y), index[c])
    dst = os.path.join(DISASM, 'gfx_compressible', 'ages', 'spr_marine_human.png')
    sheet.save(dst)
    print('->', os.path.relpath(dst, ROOT))

    # La Lanterne des Songes (la harpe d'Ages) : à la place de l'icône de l'air des Âges,
    # dans l'image d'origine relue dans git (on peut relancer le script)
    png = subprocess.run(['git', 'show', 'upstream/hack-base:gfx/common/spr_item_icons_3.png'],
                         cwd=DISASM, capture_output=True, check=True).stdout
    icons = Image.open(io.BytesIO(png))
    icons.load()
    # x = 88 : inventaire et coffre (demi-tuiles $ab-$ac) ; x = 104 : la case du bouton B ou A
    # (le jeu y prend la « petite version » de l'icône de la harpe, demi-tuiles $ad-$ae)
    big, small = read_frames(os.path.join(ROOT, 'art', 'lanterne.txt'))
    for left, frame in ((88, big), (104, small)):
        for y, row in enumerate(frame):
            for x, c in enumerate(row):
                icons.putpixel((left + x, y), index[c])
    dst = os.path.join(DISASM, 'gfx', 'common', 'spr_item_icons_3.png')
    icons.save(dst)
    print('->', os.path.relpath(dst, ROOT))


main()
