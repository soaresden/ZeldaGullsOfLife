"""Fabrique le zip du jeu complet (privé, pas pour la page publique) : le patch BPS et les readme.

On ne distribue jamais la ROM : le zip ne contient que le patch, à appliquer sur Oracle of Ages
(USA). Par défaut la barre d'état est en bas de l'écran (comme Link's Awakening) ; hud=haut la
laisse en haut, comme Ages.

Usage : python tools/make_zip.py ["chemin/ROM Ages (USA).gbc"] [hud=bas|haut] [perso]
Sortie : out/livraisons/GullsOfLife-v1.0-8-complet[-barre-en-bas].zip
Avec « perso » : le zip de Denis, pour lui seul, à la racine du dépôt (ignoré par git) :
« Legend of Zelda, The - Gulls of Life.zip », avec la ROM prête à jouer (à ne pas partager).
(la ROM Ages (USA) est par défaut dans D:\\DOCS\\Documents\\GitHub\\ZeldaOracleCombinedFR)
"""
import os
import sys
import zipfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bps  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGES_USA = r'D:\DOCS\Documents\GitHub\ZeldaOracleCombinedFR\Legend of Zelda, The - Oracle of Ages (USA).gbc'
AGES_USA_CRC = 0x3800a387
VERSION = 'v1.0-8'
SIGNATURE = b'GULLSOPT'      # les options (tools/options.py) : la barre d'état, à $10 de la signature

LISEZMOI = """The Legend of Zelda: Gulls of Life - {version} (le jeu complet)
==========================================================
« La Ballade de la Mouette »
Un hack Game Boy Color de The Legend of Zelda: Oracle of Ages, par soaresden
https://github.com/soaresden/ZeldaGullsOfLife

Version privée : le jeu en entier, encore en test (pas pour la page publique).
{hud_fr}

Comment jouer
-------------
1. Il faut sa propre ROM de The Legend of Zelda: Oracle of Ages (USA) :
     Legend of Zelda, The - Oracle of Ages (USA).gbc
     CRC32  3800a387
   Aucune ROM n'est fournie.
2. Appliquer gulls_of_life.bps avec un outil BPS, par exemple Rom Patcher JS
   (https://www.marcrobledo.com/RomPatcher.js/), Flips ou beat.
3. Jouer la ROM obtenue (CRC32 {crc}) dans un émulateur Game Boy Color.

Commandes
---------
  Select            la carte
  Select maintenu   Marine a quelque chose à dire
  A près d'un lit   dormir
  Le reste : les commandes habituelles d'Oracle of Ages.

Menu de test caché : à l'écran titre, tenir HAUT 5 secondes (petit son), puis
Start et un fichier : on choisit l'île et le moment (plage, ville, donjon...).

Crédits
-------
  Histoire, conception, direction   soaresden
  Code, musiques, dessins           soaresden, avec Claude (Anthropic)
  Moteur                            oracles-disasm de Stewmath et ses
                                    contributeurs (branche hack-base)
  Outils                            LynnaLab, WLA-DX, PyBoy

The Legend of Zelda, Link's Awakening et Oracle of Ages appartiennent à
Nintendo (Oracle of Ages a été développé par Flagship / Capcom). Projet de fan
gratuit, sans lien avec Nintendo ni Capcom. Ne le vendez pas.
"""

README = """The Legend of Zelda: Gulls of Life - {version} (full game)
=======================================================
"The Ballad of the Seagull"
A Game Boy Color hack of The Legend of Zelda: Oracle of Ages, by soaresden
https://github.com/soaresden/ZeldaGullsOfLife

Private build: the whole game, still being tested (not for the public page).
{hud_en}

How to play
-----------
1. You need your own ROM of The Legend of Zelda: Oracle of Ages (USA):
     Legend of Zelda, The - Oracle of Ages (USA).gbc
     CRC32  3800a387
   No ROM is included.
2. Apply gulls_of_life.bps with a BPS tool, for example Rom Patcher JS
   (https://www.marcrobledo.com/RomPatcher.js/), Flips or beat.
3. Play the resulting ROM (CRC32 {crc}) in a Game Boy Color emulator.

Controls
--------
  Select            the map
  Hold Select       Marin has something to say
  A near a bed      sleep
  Everything else: the usual Oracle of Ages controls.

Hidden test menu: on the title screen, hold UP for 5 seconds (small sound),
then Start and a file: pick the island and the moment (beach, town, dungeon...).

Credits
-------
  Story, design, direction   soaresden
  Code, music, art           soaresden, with Claude (Anthropic)
  Engine                     oracles-disasm by Stewmath and contributors
                             (hack-base branch)
  Tools                      LynnaLab, WLA-DX, PyBoy

The Legend of Zelda, Link's Awakening and Oracle of Ages belong to Nintendo
(Oracle of Ages was developed by Flagship / Capcom). Free fan project, not
affiliated with Nintendo or Capcom. Do not sell it.
"""


def main():
    args = sys.argv[1:]
    hud = 'bas'
    perso = 'perso' in args
    if perso:
        args.remove('perso')
    for a in list(args):
        if a.startswith('hud='):
            hud = a[4:]
            args.remove(a)
    assert hud in ('bas', 'haut'), hud
    source = open(args[0] if args else AGES_USA, 'rb').read()
    if zlib.crc32(source) != AGES_USA_CRC:
        sys.exit('ROM inattendue (CRC32 %08x) : il faut Oracle of Ages (USA), CRC32 %08x'
                 % (zlib.crc32(source), AGES_USA_CRC))

    # La ROM compilée (build.sh), avec l'option de la barre d'état
    target = bytearray(open(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), 'rb').read())
    sig = target.find(SIGNATURE)
    assert sig >= 0, 'signature GULLSOPT introuvable'
    target[sig + 0x10] = 1 if hud == 'bas' else 0
    # Les sommes de contrôle de l'en-tête (la globale : comme tools/options.py)
    target[0x14e:0x150] = b'\0\0'
    total = sum(target) & 0xffff
    target[0x14e:0x150] = bytes((total >> 8, total & 0xff))
    target = bytes(target)

    patch = bps.encode(source, target)
    assert bps.decode(source, patch) == target
    crc = '%08x' % zlib.crc32(target)
    if hud == 'bas':
        hud_fr = ('La barre d\'état (les cœurs, les objets) est en bas de l\'écran, comme dans\n'
                  'Link\'s Awakening.')
        hud_en = 'The status bar (hearts, items) is at the bottom of the screen, as in\nLink\'s Awakening.'
    else:
        hud_fr = 'La barre d\'état est en haut de l\'écran, comme dans Oracle of Ages.'
        hud_en = 'The status bar is at the top of the screen, as in Oracle of Ages.'

    if perso:
        # Pour Denis seul : la ROM prête à jouer (le zip est ignoré par git : *.zip)
        name = 'Legend of Zelda, The - Gulls of Life'
        path = os.path.join(ROOT, name + '.zip')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr(name + '.gbc', target)
            z.writestr('gulls_of_life.bps', patch)
            z.writestr('LISEZMOI.txt', LISEZMOI.format(version=VERSION, hud_fr=hud_fr, crc=crc).replace('\n', '\r\n'))
        print("%s : la ROM (CRC32 %s, barre d'état en %s), le patch, le LISEZMOI" % (path, crc, hud))
        return

    out_dir = os.path.join(ROOT, 'out', 'livraisons')
    os.makedirs(out_dir, exist_ok=True)
    name = 'GullsOfLife-%s-complet%s.zip' % (VERSION, '-barre-en-bas' if hud == 'bas' else '')
    path = os.path.join(out_dir, name)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('gulls_of_life.bps', patch)
        z.writestr('LISEZMOI.txt', LISEZMOI.format(version=VERSION, hud_fr=hud_fr, crc=crc).replace('\n', '\r\n'))
        z.writestr('README.txt', README.format(version=VERSION, hud_en=hud_en, crc=crc).replace('\n', '\r\n'))
    print('%s : patch %d octets, ROM obtenue CRC32 %s (barre d\'état en %s)' % (path, len(patch), crc, hud))


if __name__ == '__main__':
    main()
