🇬🇧 [English version](README.en.md)

**▶ [La page du jeu](https://soaresden.github.io/ZeldaGullsOfLife/)**

# The Legend of Zelda: Gulls of Life

*La Ballade de la Mouette* : la suite de **Link's Awakening**, en ROM hack
Game Boy Color.

Le Poisson-Rêve s'est réveillé et l'île Cocolint a disparu… mais pas tout à
fait. Marine a fait un vœu : avoir des ailes pour partir au-delà de la mer. Elle
revient en **mouette**, et elle accompagne Link dans un archipel où plus
personne ne rêve.

*Gulls of Life* : *gulls* (les mouettes) sonne comme *goals* (les buts). C'est
la morale du jeu : on réalise ses rêves, on n'y reste pas, et on avance malgré
les obstacles.

<p align="center"><img src="docs/shots/v02_1.png" width="480" alt="Écran titre de Gulls of Life"></p>

![Carte de l'archipel des Sans-Sommeil](docs/carte_archipel.png)

![Le film d'ouverture](docs/film_ouverture.png)

Pourquoi les rêves se sont-ils éteints ? Et que reste-t-il de Cocolint… quand
on ferme les yeux ? Le reste, c'est à vous de le découvrir.

## Jouer

**[▶ Démo v0.2](https://github.com/soaresden/ZeldaGullsOfLife/releases/tag/v0.2)**
(tout le premier chapitre) : un patch `gulls_of_life.bps` à appliquer sur sa
propre ROM *The Legend of Zelda: Oracle of Ages* (USA). Aucune ROM n'est fournie.

En **français ou en anglais** : on choisit en se réveillant sur la plage, et la
sauvegarde s'en souvient. Dans la v0.2, les menus (choix du fichier, sauvegarde)
sont encore en anglais ; dans la prochaine version ils suivent la langue (choix du
fichier, sauvegarde, Game Over, inventaire), sauf au tout premier démarrage.

| Touche | |
| --- | --- |
| **Select** | la carte |
| **Select** maintenu | Marine a son mot à dire |
| **A** devant un lit | dormir |

<details>
<summary><b>Comment appliquer le patch</b></summary>

1. Télécharger `gulls_of_life.bps` dans la [version v0.2](https://github.com/soaresden/ZeldaGullsOfLife/releases/tag/v0.2).
2. Avoir sa propre ROM *Oracle of Ages* version **USA** (CRC32 `3800a387`).
3. Appliquer le patch avec un outil BPS, par exemple [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) en ligne.
4. Jouer le fichier obtenu (CRC32 `2d2973ff`) dans n'importe quel émulateur Game Boy Color.

</details>

<details>
<summary><b>Quoi de neuf dans la v0.2</b></summary>

- L'écran titre *Gulls of Life*, juste après le film d'ouverture
- Le jeu en français et en anglais
- Select : un appui pour la carte, maintenu pour parler à Marine
- Corrections : plus de gel entre deux écrans, plus de tuiles blanches ni de murs invisibles, plus de blocage au bord de l'île, et la Lanterne a sa vraie icône

</details>

## Où on en est

- ✅ Le film d'ouverture
- ✅ Chapitre 1 : l'île de la Brume
- ✅ Le premier donjon
- ✅ L'écran titre *Gulls of Life*
- ✅ Français et anglais
- ✅ Démo jouable v0.2
- ⬜ Les sept autres îles
- ⬜ Des jeux, des secrets et des quarts de cœur
- ⬜ La musique
- ⬜ Et la suite de l'histoire…

<details>
<summary><b>Comment c'est fait</b></summary>

Le jeu repose sur le **moteur d'Oracle of Ages**, grâce au désassemblage
complet [oracles-disasm](https://github.com/Stewmath/oracles-disasm) de
Stewmath (branche `hack-base`, prévue pour les hacks). Le passage
présent/passé d'*Ages* sert au Réel et au Songe.

| Quoi | Où |
| --- | --- |
| Code, scripts, données | Branche [`hack/gulls-of-life`](https://github.com/soaresden/oracles-disasm/tree/hack/gulls-of-life) du fork (ajouts marqués `BALLADE`) : `scripts/ages/ballade.s`, `object_code/ages/interactions/marine.s` |
| Dialogues | `story/textes.yaml` en français normal, `story/textes.en.yaml` en anglais ; `tools/make_text.py` les ajoute au jeu, `tools/check_text.py` vérifie la largeur des lignes (16 caractères) |
| Sprites | Dessins en texte dans `art/` ; `tools/make_sprites.py` les convertit |
| Film d'ouverture | `code/ages/cutscenes/film.s` (fork) ; décor et sprites fabriqués par `tools/make_film.py` (ciel et nuages, soleil, mer, rondin, poses de Link prises dans le jeu, visage de Marine) ; `tools/preview_film.py` en donne un aperçu sans compiler |
| Salles | Plans texte dans `story/salles/` (10 x 8 briques par écran) et leurs objets dans `story/salles/objets.txt` ; `tools/make_rooms.py` les met dans le jeu ; `tools/catalog.py` photographie les briques d'un décor ou des salles avec leurs numéros |
| Carte | `tools/make_map.py` dessine `docs/carte_archipel.png` (les 8 îles, les routes du Bateau-Rondin, le plan de l'île de la Brume) |
| Tests | `tools/play.py` joue la ROM dans PyBoy et prend des captures ; `tools/test_phare.py`, `tools/test_lanterne.py`, `tools/test_fin.py` |
| Patch | `tools/make_patch.py` fabrique `out/gulls_of_life.bps` à partir de la ROM *Ages* (USA) |

Aucune ROM n'est distribuée ici : seulement le patch, à appliquer sur sa propre
ROM *Oracle of Ages* (USA).

</details>

<details>
<summary><b>Compiler (Windows)</b></summary>

Prérequis : [MSYS2](https://www.msys2.org/) dans `C:\msys64` (avec `cmake`,
`make`, `mingw-w64-x86_64-gcc`) et Python 3 avec
`pip install pyyaml pillow pyboy`. Depuis Git Bash :

```bash
./setup.sh
```

```bash
./build.sh
```

La ROM sort dans `out/gulls_of_life.gbc`.

</details>

## Crédits

- Moteur et désassemblage : [oracles-disasm](https://github.com/Stewmath/oracles-disasm) de Stewmath et ses contributeurs.
- Sprites de Marine : branche `sprites/marin` d'oracles-disasm.
- *The Legend of Zelda* appartient à Nintendo ; ce projet est un hack fait par des fans, sans ROM.
