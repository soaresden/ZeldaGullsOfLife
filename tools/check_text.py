"""Vérifie que chaque ligne de story/textes.yaml tient dans la boîte (16 caractères).

Usage : python tools/check_text.py
"""
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMANDS = re.compile(r'\\(stop|opt|col|pos|sfx|wait|speed|slow)(\([^)]*\))?')


def main():
    doc = yaml.safe_load(open(os.path.join(ROOT, 'story', 'textes.yaml'), encoding='utf-8'))
    bad = 0
    for group in doc['groups']:
        for entry in group['data']:
            for line in entry['text'].split('\n'):
                visible = COMMANDS.sub('', line).replace('\\Link', 'X' * 5)
                if len(visible) > 16:
                    print('%s : %d caractères : %s' % (entry['name'], len(visible), line))
                    bad += 1
    print('ok' if not bad else '%d ligne(s) trop longue(s)' % bad)
    sys.exit(1 if bad else 0)


main()
