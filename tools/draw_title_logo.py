"""Dessine (une fois) les lettres du logo « Gulls of Life » dans art/titre_logo.txt.

Les mots sont tracés avec la police Palatino gras italique de Windows, sans lissage, puis enregistrés en
dessin texte (# = lettre) : la compilation (tools/make_title.py) n'a plus besoin de la police.
À relancer seulement pour changer le texte ou la taille du logo.

Usage : python tools/draw_title_logo.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = 'C:/Windows/Fonts/palabi.ttf'   # Palatino gras italique : plus doux, c'est Marine !
WORDS = (('Gulls', 42), ('of Life', 25))


def mask(text, size):
    font = ImageFont.truetype(FONT, size)
    left, top, right, bottom = font.getbbox(text)
    im = Image.new('1', (right - left, bottom - top), 0)
    draw = ImageDraw.Draw(im)
    draw.fontmode = '1'
    draw.text((-left, -top), text, font=font, fill=1)
    return im


def main():
    out = ['# Lettres du logo de l\'écran titre (tools/draw_title_logo.py, police Palatino gras italique).',
           '# # = lettre ; tools/make_title.py ajoute le contour et le dégradé rose.']
    for text, size in WORDS:
        im = mask(text, size)
        px = im.load()
        out.append('@%s' % text)
        for y in range(im.size[1]):
            out.append(''.join('#' if px[x, y] else '.' for x in range(im.size[0])))
    path = os.path.join(ROOT, 'art', 'titre_logo.txt')
    open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('->', os.path.relpath(path, ROOT))


main()
