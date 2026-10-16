"""Ajoute les textes du jeu (story/textes.yaml) au texte d'Oracle of Ages.

Le texte d'origine est relu dans git (branche hack-base) : on peut relancer
le script autant de fois qu'on veut.

Usage : python tools/make_text.py   (depuis la racine du dépôt)
"""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
YAML = 'text/ages/text.yaml'


def main():
    base = subprocess.run(['git', 'show', 'upstream/hack-base:' + YAML], cwd=DISASM,
                          capture_output=True, check=True).stdout.decode('utf-8')
    ours = open(os.path.join(ROOT, 'story', 'textes.yaml'), encoding='utf-8').read()
    # Nos groupes à la suite de ceux du jeu (on retire la ligne "groups:")
    ours = ours.split('\ngroups:\n', 1)[1]
    with open(os.path.join(DISASM, YAML), 'w', encoding='utf-8', newline='\n') as f:
        f.write(base.rstrip('\n') + '\n\n# ===== La Ballade de la Mouette (story/textes.yaml) =====\n')
        f.write(ours)
    print('textes ajoutés ->', YAML)


main()
