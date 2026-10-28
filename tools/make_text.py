"""Prépare les textes du jeu dans les deux langues, à partir du texte (anglais) d'Oracle of Ages.

- text/ages/text.yaml    : anglais (langue 0), avec story/textes.en.yaml
- text/ages/text_fr.yaml : français (langue 1), avec story/textes.yaml

Dans chaque fichier de story/ :
- les groupes 0x5a et 0x5b (libres dans Ages) contiennent tous nos textes ; ils sont ajoutés à la
  fin (le 0x5b : la fin du jeu et l'après-jeu, le 0x5a étant plein) ;
- les entrées des autres groupes remplacent le texte d'Ages du même nom (ex. TX_001c, « Tu as
  retrouvé ton épée ») ; les textes d'Ages qu'on ne remplace pas restent en anglais.

Les deux langues ont les mêmes numéros de textes (le jeu choisit la table selon wActiveLanguage).
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
BASE = 'text/ages/text.yaml'
OUR_GROUPS = (0x5a, 0x5b, 0x5c)    # le 0x5b : la fin du jeu et l'après-jeu (le 0x5a est plein) ; le 0x5c : la suite
LANGUAGES = (('textes.en.yaml', 'text/ages/text.yaml'), ('textes.yaml', 'text/ages/text_fr.yaml'))


def entry_block(text):
    """Bloc YAML d'un texte, au format du fichier d'Ages."""
    # Un texte qui commence par des espaces (un nom centré) : indentation donnée (« |2- »), sinon
    # YAML la déduirait de la première ligne
    head = '    text: |2-' if text.startswith(' ') else '    text: |-'
    lines = [head] + ['      ' + l if l else '' for l in text.split('\n')]
    return '\n'.join(lines) + '\n'


def build(base, source_name, out_name):
    source = open(os.path.join(ROOT, 'story', source_name), encoding='utf-8').read()
    doc = yaml.safe_load(source)

    # Remplacements de textes d'Ages
    for group in doc['groups']:
        if group['group'] in OUR_GROUPS:
            continue
        for e in group['data']:
            # Le nom seul (« - name: TX_0002 ») ou dans une liste (« - name: » puis « - TX_0000 »)
            head = (re.search(r'^  - name: %s\n' % e['name'], base, re.M)
                    or re.search(r'^    - %s\n' % e['name'], base, re.M))
            assert head, e['name']
            start = base.index('\n    text: ', head.start()) + 1
            m = re.compile(r'    text: [^\n]*\n((?:      [^\n]*\n|\n)*?)(?=  - name:|  #|    \w+:|\n- group:|\Z)').match(base, start)
            assert m, e['name']
            # (une propriété comme « null_terminator: False » reste à sa place, après le texte)
            base = base[:start] + entry_block(e['text']) + base[m.end():]

    # Nos groupes, à la fin (copie du texte source, commentaires compris)
    body = source.split('\ngroups:\n', 1)[1]
    blocks = []
    for g in OUR_GROUPS:
        tag = '- group: 0x%02x' % g
        if tag not in body:
            continue
        block = body[body.index(tag):]
        nxt = re.search(r'\n- group:', block[1:])
        if nxt:
            block = block[:nxt.start() + 1]
        blocks.append(block.rstrip('\n'))
    ours = '\n\n'.join(blocks)
    with open(os.path.join(DISASM, out_name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(base.rstrip('\n') + '\n\n# ===== Gulls of Life (story/%s) =====\n' % source_name)
        f.write(ours.rstrip('\n') + '\n')
    print('textes ->', out_name)


def main():
    base = subprocess.run(['git', 'show', 'upstream/hack-base:' + BASE], cwd=DISASM,
                          capture_output=True, check=True).stdout.decode('utf-8')
    for source_name, out_name in LANGUAGES:
        build(base, source_name, out_name)


main()
