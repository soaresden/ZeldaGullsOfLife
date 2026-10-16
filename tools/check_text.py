"""Vérifie les textes du jeu (story/textes.yaml en français, story/textes.en.yaml en anglais) :

- chaque ligne tient dans la boîte (16 caractères) ;
- les deux langues ont exactement les mêmes textes dans notre groupe ($5a) ;
- pas de caractère absent de la police du jeu.

Usage : python tools/check_text.py
"""
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMANDS = re.compile(r'\\(stop|opt|col|pos|sfx|wait|speed|slow|heartpiece|jump|n\b)(\([^)]*\))?')
# Lettres accentuées de la police du jeu (version US). Les autres (ô...) ne s'affichent pas :
# écrire sans l'accent (« coté »).
FONT_EXTRA = set('ÀÂÄÆÇÈÉÊËÎÏÑÖŒÙÛÜàâäæçèéêëîïñöœùûü')
FILES = ('textes.yaml', 'textes.en.yaml')


def ours(doc):
    return {e['name'] for g in doc['groups'] if g['group'] == 0x5a for e in g['data']}


def main():
    bad = 0
    docs = {}
    for name in FILES:
        doc = docs[name] = yaml.safe_load(open(os.path.join(ROOT, 'story', name), encoding='utf-8'))
        for group in doc['groups']:
            for entry in group['data']:
                for line in entry['text'].split('\n'):
                    visible = COMMANDS.sub('', line).replace('\\Link', 'X' * 5)
                    # Les boutons A et B font 2 caractères à l'écran
                    visible = visible.replace('\\abtn', 'AA').replace('\\bbtn', 'BB')
                    if len(visible) > 16:
                        print('%s %s : %d caractères : %s' % (name, entry['name'], len(visible), line))
                        bad += 1
                    odd = {c for c in visible if ord(c) > 126 and c not in FONT_EXTRA}
                    if odd:
                        print('%s %s : pas dans la police : %s' % (name, entry['name'], ''.join(odd)))
                        bad += 1
    fr, en = (ours(docs[n]) for n in FILES)
    for n in sorted(fr ^ en):
        print('%s : seulement en %s' % (n, 'français' if n in fr else 'anglais'))
        bad += 1
    print('ok' if not bad else '%d problème(s)' % bad)
    sys.exit(1 if bad else 0)


main()
