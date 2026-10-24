"""Marine humaine avec ses vrais sprites de Link's Awakening DX (Denis : « même Marine, elle a des
poses pour chanter et plein d'animations : profites-en »). Les poses de Marin dans le désassemblage
de DX (LADX-Disassembly-main/src/gfx/characters ; une bande = 8 sprites de 8 x 16, deux voisins font
un 16 x 16 ; pixels 0 transparent, 85/170/255 = couleurs 1/2/3, comme nos feuilles) :
- oam_npc_1.cgb.png, bande 15 : de face, de dos, de profil, de profil en marchant (MarinIndoor) ;
- oam_npc_3.cgb.png, bande 38 : elle chante (les mains jointes, les yeux fermés) et, au milieu de
  son balancement, de face (le sprite 2 et son reflet : MarinCreditsSpriteVariants 8-10,
  src/code/entities/05_marin.asm ; elle se balance 8, 8, 8, 9, 10, 10, 10, 9, 10 = 8 à l'envers).

Écrit oracles-disasm/gfx_compressible/ages/spr_marine_human.png (8 images de 16 x 16 ; l'image n
prend les tuiles 4n à 4n+3), dans l'ordre des villageois d'Ages (face, dos, profil, profil un pas :
les animations des habitants retournent les images pour l'autre côté), et l'aperçu
art/marine_dx.png. Le jeu retourne lui-même les images vers la droite (balladeFin.humanShow). Sans
le désassemblage de DX, l'ancienne Marine (art/marine_humaine.txt, tools/make_sprites.py) reste.

Usage : python tools/make_marine_dx.py   (après tools/make_sprites.py)
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DX = os.path.join(ROOT, 'LADX-Disassembly-main', 'src', 'gfx', 'characters')
OUT = os.path.join(ROOT, 'oracles-disasm', 'gfx_compressible', 'ages', 'spr_marine_human.png')
PREVIEW = os.path.join(ROOT, 'art', 'marine_dx.png')
# (fichier, bande, sprite de gauche, sprite de droite, le droit retourné)
POSES = [
    ('oam_npc_1.cgb.png', 15, 0, 1, False),  # 0. de face
    ('oam_npc_1.cgb.png', 15, 2, 3, False),  # 1. de dos
    ('oam_npc_1.cgb.png', 15, 4, 5, False),  # 2. de profil (vers la gauche)
    ('oam_npc_1.cgb.png', 15, 6, 7, False),  # 3. de profil, un pas
    ('oam_npc_3.cgb.png', 38, 0, 1, False),  # 4. elle chante (penchée)
    ('oam_npc_3.cgb.png', 38, 2, 2, True),   # 5. elle chante (droite, au milieu du balancement)
]
# PAL1 de DX (noir, orange, peau), pour l'aperçu
PREVIEW_PAL = [(255, 255, 255), (0, 0, 0), (248, 120, 8), (248, 184, 136)]


def main():
    if not os.path.isdir(DX):
        print('marine DX : pas de désassemblage de DX, spr_marine_human.png reste tel quel')
        return
    sheets = {}
    out = Image.new('P', (128, 16), 0)
    out.putpalette([0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255] + [0] * 756)
    for n, (name, band, left, right, flip) in enumerate(POSES):
        im = sheets.setdefault(name, Image.open(os.path.join(DX, name)).convert('L'))
        for half, sprite in enumerate((left, right)):
            for x in range(8):
                sx = 7 - x if (half and flip) else x
                for y in range(16):
                    v = im.getpixel((sprite * 8 + sx, band * 16 + y))
                    out.putpixel((n * 16 + half * 8 + x, y), {0: 0, 85: 1, 170: 2, 255: 3}[v])
    out.save(OUT)
    prev = Image.new('RGB', (128, 16))
    for x in range(128):
        for y in range(16):
            prev.putpixel((x, y), PREVIEW_PAL[out.getpixel((x, y))])
    prev.resize((512, 64), Image.NEAREST).save(PREVIEW)
    print('marine DX : %d poses -> %s' % (len(POSES), os.path.relpath(OUT, ROOT)))


if __name__ == '__main__':
    main()
