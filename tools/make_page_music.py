"""Enregistre la musique de l'écran titre depuis la ROM et en fait une boucle pour la page du jeu.

La musique est jouée dans PyBoy (comme tools/record_music.py). L'enregistrement commence avec la
musique de l'écran titre ($01) et s'arrête quand le jeu la coupe : au bout d'une quarantaine de
secondes sans appui, l'écran titre relance le film d'ouverture et sa musique, qu'il ne faut pas
garder. La période du morceau est cherchée en comparant ses spectres avec lui-même un tour plus
tard, puis un seul tour est gardé (avec un court fondu enchaîné à la jointure, pour une boucle sans
à-coup) et écrit en Ogg Vorbis : docs/titre.ogg.

Usage : python tools/make_page_music.py
"""
import os

import numpy as np
import soundfile
from pyboy import PyBoy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAY_SOUND = 0x0c09      # playSound (banque 0, voir oracles-disasm/ages.sym)
MUS_TITLE = 0x01         # la musique de l'écran titre
MAX_SECONDS = 90         # garde-fou
FADE = 0.05              # fondu enchaîné à la jointure (secondes)


def record():
    """Le son de l'écran titre, du lancement de sa musique jusqu'au son suivant que le jeu demande."""
    pb = PyBoy(os.path.join(ROOT, 'out', 'gulls_of_life.gbc'), window='null', sound_emulated=True)
    pb.set_emulation_speed(0)
    state = {'title': False, 'end': False}

    def on_play_sound(_):
        a = pb.register_file.A
        if a == MUS_TITLE:
            state['title'] = True
        elif state['title']:
            state['end'] = True   # le film d'ouverture repart : on s'arrête avant sa musique

    pb.hook_register(0, PLAY_SOUND, on_play_sound, None)
    while not state['title']:
        pb.tick(1, False)
    rec = []
    for _ in range(MAX_SECONDS * 60):
        pb.tick(1, False)
        if state['end']:
            break
        rec.append(pb.sound.ndarray.copy())
    rate = pb.sound.sample_rate
    pb.stop(save=False)
    data = np.concatenate(rec).astype(np.float32)
    return data - data.mean(axis=0), rate


def spectra(mono, start, count, hop=1200, size=1024):
    win = np.hanning(size)
    return np.array([np.log1p(np.abs(np.fft.rfft(mono[start + i * hop:start + i * hop + size] * win))[:200])
                     for i in range(count)])


def period(mono, rate):
    """Le décalage (en échantillons) pour lequel le morceau se ressemble le plus à lui-même."""
    a, count = 1 * rate, 160                       # 4 s comparées, à partir de la 1re seconde
    ref = spectra(mono, a, count)

    def err(p):
        return float(np.mean((ref - spectra(mono, a + p, count)) ** 2))

    # D'abord grossièrement (tous les dixièmes de seconde, à partir de 15 s), puis finement
    last = len(mono) - a - count * 1200 - 1024 - rate // 10
    coarse = min(range(15 * rate, last, rate // 10), key=err)
    return min(range(coarse - rate // 10, coarse + rate // 10, 25), key=err)


def main():
    data, rate = record()
    mono = data.mean(axis=1)
    p = period(mono, rate)
    print('période : %.3f s' % (p / rate))
    loop = data[:p].copy()
    # La fin du tour s'enchaîne sur data[p:], qui ressemble au début : on fond le début dedans
    n = int(FADE * rate)
    ramp = np.linspace(0, 1, n)[:, None]
    loop[:n] = data[p:p + n] * (1 - ramp) + data[:n] * ramp
    loop /= max(1.0, float(np.abs(loop).max())) / 0.9
    dst = os.path.join(ROOT, 'docs', 'titre.ogg')
    # Par petits blocs : libsndfile plante si on lui donne tout le morceau d'un coup en Vorbis
    with soundfile.SoundFile(dst, 'w', rate, loop.shape[1], format='OGG', subtype='VORBIS') as f:
        for i in range(0, len(loop), 4096):
            f.write(loop[i:i + 4096])
    print('->', os.path.relpath(dst, ROOT), '%d Ko' % (os.path.getsize(dst) // 1024))


main()
