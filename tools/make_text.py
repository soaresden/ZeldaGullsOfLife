"""Ajoute les textes du jeu (story/textes.yaml) au texte d'Oracle of Ages.

- Le groupe 0x5a (libre dans Ages) contient tous nos textes ; il est ajouté à la fin.
- Les entrées des autres groupes remplacent le texte d'Ages du même nom (ex. TX_001c, « Tu as
  trouvé l'épée ») : ainsi les objets qu'on trouve parlent français.

Le texte d'origine est relu dans git (branche hack-base) : on peut relancer le script autant de
fois qu'on veut.

Usage : python tools/make_text.py   (depuis la racine du dépôt)
"""
import os
import re
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISASM = os.path.join(ROOT, 'oracles-disasm')
YAML = 'text/ages/text.yaml'
OUR_GROUP = 0x5a


def entry_block(text):
    """Bloc YAML d'un texte, au format du fichier d'Ages."""
    lines = ['    text: |-'] + ['      ' + l if l else '' for l in text.split('\n')]
    return '\n'.join(lines) + '\n'


def main():
    base = subprocess.run(['git', 'show', 'upstream/hack-base:' + YAML], cwd=DISASM,
                          capture_output=True, check=True).stdout.decode('utf-8')
    source = open(os.path.join(ROOT, 'story', 'textes.yaml'), encoding='utf-8').read()
    doc = yaml.safe_load(source)

    # Remplacements de textes d'Ages
    for group in doc['groups']:
        if group['group'] == OUR_GROUP:
            continue
        for e in group['data']:
            m = re.search(r'(  - name: %s\n    index: [^\n]+\n)    text: [^\n]*\n((?:      [^\n]*\n|\n)*?)(?=  - name:|\n- group:|\Z)'
                          % e['name'], base)
            assert m, e['name']
            base = base[:m.start()] + m.group(1) + entry_block(e['text']) + '\n' + base[m.end():]

    # Notre groupe, à la fin (copie du texte source, commentaires compris)
    ours = source.split('\ngroups:\n', 1)[1]
    ours = ours[ours.index('- group: 0x%02x' % OUR_GROUP):]
    nxt = re.search(r'\n- group:', ours[1:])
    if nxt:
        ours = ours[:nxt.start() + 1]
    with open(os.path.join(DISASM, YAML), 'w', encoding='utf-8', newline='\n') as f:
        f.write(base.rstrip('\n') + '\n\n# ===== Gulls of Life (story/textes.yaml) =====\n')
        f.write(ours.rstrip('\n') + '\n')
    print('textes ajoutés ->', YAML)


main()
