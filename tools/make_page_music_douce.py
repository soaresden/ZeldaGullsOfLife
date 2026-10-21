"""Version douce de la musique de l'écran titre, pour la page web : docs/titre.ogg.

La musique du jeu (carrés de la Game Boy, batterie, basse qui balance) attaque trop pour une page
qu'on lit. Ici, la même chanson (music/titre.txt : la Ballade chantée par Marine) est rejouée
autrement, sans passer par la ROM :
- la mélodie une octave plus bas, en flûte ronde (attaque lente, léger vibrato) ;
- les arpèges en harpe pincée, plus discrets ; la basse en notes rondes et tenues ;
- pas de batterie ; à la place des cris de mouette, la mer qui respire en fond ;
- un peu plus lent, avec de la réverbération.
La fin de la réverbération est repliée sur le début : la boucle est sans couture.

Usage : python tools/make_page_music_douce.py
"""
import os
import re

import numpy as np
import soundfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATE = 44100
STEP = 0.26          # secondes par croche (le jeu : 12 images = 0,2 s)
NOTE = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}


def parse(path):
    """{section: {voix: [(note ou None, durée en croches)]}} et l'ordre des sections."""
    sections, order, cur = {}, [], None
    for line in open(path, encoding='utf8'):
        line = re.sub(r'(^|\s)#(\s.*)?$', '', line).strip()   # commentaires (pas les dièses)
        m = re.match(r'==\s*(\w+)\s*==', line)
        if m:
            cur = sections.setdefault(m.group(1), {})
            continue
        if line.startswith('ordre:'):
            order = [w for w in line[6:].replace('|', ' ').split()]
            continue
        m = re.match(r'(\w+):\s*(.*)', line)
        if not m or cur is None or m.group(1) in ('tempo', 'mesure'):
            continue
        body = re.sub(r'\[[^\]]*\]', ' ', m.group(2)).replace('|', ' ')
        while '(' in body:   # ( ... )xN
            body = re.sub(r'\(([^()]*)\)x(\d+)', lambda g: ' '.join([g.group(1)] * int(g.group(2))), body)
        for tok in body.split():
            name, dur = tok.rsplit(':', 1)
            cur.setdefault(m.group(1), []).append((name, int(dur)))
    return sections, order


def freq(name):
    m = re.match(r'([a-g])(#?)(\d)', name)
    if not m:
        return None
    n = NOTE[m.group(1)] + (1 if m.group(2) else 0) + 12 * (int(m.group(3)) + 1)
    return 440.0 * 2 ** ((n - 69) / 12)


def fftconv(a, b):
    n = len(a) + len(b) - 1
    size = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(a, size) * np.fft.rfft(b, size), size)[:n]


def env(n, a, r, sustain=1.0):
    e = np.full(n, sustain)
    a, r = min(a, n), min(r, n)
    e[:a] = np.linspace(0, sustain, a)
    e[n - r:] *= np.linspace(1, 0, r)
    return e


def flute(f, dur):
    n = int((dur + 0.35) * RATE)
    t = np.arange(n) / RATE
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) * 3, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / RATE
    w = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    return w * env(n, int(0.07 * RATE), int(0.35 * RATE)) * 0.9


def harp(f, dur):
    n = int(1.6 * RATE)
    t = np.arange(n) / RATE
    w = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6)
    return w * np.exp(-t * 3.2) * env(n, int(0.004 * RATE), int(0.05 * RATE)) * 0.32


def bass(f, dur):
    n = int((dur + 0.4) * RATE)
    t = np.arange(n) / RATE
    w = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return w * np.exp(-t * 1.1) * env(n, int(0.03 * RATE), int(0.4 * RATE)) * 0.45


VOICES = {'melodie': (flute, -12), 'accordeon': (harp, 0), 'basse': (bass, 12)}


def render():
    sections, order = parse(os.path.join(ROOT, 'music', 'titre.txt'))
    total = sum(sum(d for _, d in sections[s]['melodie']) for s in order) * STEP
    length = int(total * RATE)
    out = np.zeros(length + 3 * RATE)
    for voice, (inst, shift) in VOICES.items():
        t = 0.0
        for s in order:
            for name, d in sections[s].get(voice, []):
                f = freq(name)
                if f:
                    w = inst(f * 2 ** (shift / 12), d * STEP)
                    i = int(t * RATE)
                    out[i:i + len(w)] += w
                t += d * STEP
    # la mer : bruit filtré qui respire (deux vagues par tour, pour boucler juste)
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(length)
    k = np.exp(-np.arange(400) / 80.0); k /= k.sum()
    sea = fftconv(noise, k)[:length]
    c = np.cumsum(np.concatenate([[0], sea]))
    low = (c[4000:] - c[:-4000]) / 4000          # moyenne glissante : on garde le souffle, pas le grondement
    sea[2000:2000 + len(low)] -= low
    tt = np.arange(length) / RATE
    swell = 0.5 - 0.5 * np.cos(2 * np.pi * 4 * tt / total)
    out[:length] += sea * swell * 0.9
    # réverbération (bruit qui décroît), puis la fin repliée sur le début
    ir_t = np.arange(int(1.8 * RATE)) / RATE
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.5)
    ir[0] = 0
    wet = fftconv(out, ir / np.sqrt(np.sum(ir ** 2)) * 0.35)[:len(out)]
    mix = out + wet
    loop = mix[:length].copy()
    tail = mix[length:]
    loop[:len(tail)] += tail
    loop = np.tanh(loop / np.abs(loop).max() * 1.2) * 0.7   # rond, sans pointe
    stereo = np.stack([loop, np.roll(loop, int(0.012 * RATE))], axis=1) * 0.9
    return stereo.astype(np.float32), total


def main():
    data, total = render()
    dst = os.path.join(ROOT, 'docs', 'titre.ogg')
    with soundfile.SoundFile(dst, 'w', RATE, 2, format='OGG', subtype='VORBIS') as f:
        for i in range(0, len(data), 4096):   # par petits blocs (libsndfile plante sinon)
            f.write(data[i:i + 4096])
    print('%.1f s -> %s, %d Ko' % (total, os.path.relpath(dst, ROOT), os.path.getsize(dst) // 1024))


main()
