🇫🇷 [Version française](README.md)

**▶ [The game's page](https://soaresden.github.io/ZeldaGullsOfLife/)**

# The Legend of Zelda: Gulls of Life

*The Ballad of the Seagull*: the sequel to **Link's Awakening**, as a Game Boy
Color ROM hack.

The Wind Fish woke up and Koholint Island vanished… but not entirely. Marin
made a wish: to have wings and fly beyond the sea. She comes back as a
**seagull**, and joins Link on an archipelago where nobody dreams anymore.

*Gulls of Life*: *gulls* sounds like *goals*. That's the moral of the game:
you make your dreams come true instead of staying in them, and you keep going
no matter what.

![Map of the Sleepless Archipelago](docs/carte_archipel.png)

![The opening film](docs/film_ouverture.png)

Why did the dreams go out? And what is left of Koholint… when you close your
eyes? The rest is for you to find.

## Play

**[▶ Demo v0.1](https://github.com/soaresden/ZeldaGullsOfLife/releases/tag/v0.1)**
(the whole first chapter): a `gulls_of_life.bps` patch to apply to your own
*The Legend of Zelda: Oracle of Ages* (USA) ROM. No ROM is provided. The game's
text is in French.

| Button | |
| --- | --- |
| **Select** | the map |
| Hold **Select** | Marin has something to say |

*(In demo v0.1 it's still the other way round.)*

<details>
<summary><b>How to apply the patch</b></summary>

1. Download `gulls_of_life.bps` from the [v0.1 release](https://github.com/soaresden/ZeldaGullsOfLife/releases/tag/v0.1).
2. Have your own *Oracle of Ages* ROM, **USA** version (CRC32 `3800a387`).
3. Apply the patch with a BPS patcher, for example [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) online.
4. Play the result in any Game Boy Color emulator.

</details>

## Status

- ✅ The opening film
- ✅ Chapter 1: Mist Island
- ✅ The first dungeon
- ✅ Playable demo v0.1
- ⬜ The *Gulls of Life* title screen
- ⬜ The other seven islands
- ⬜ Games, secrets and heart pieces
- ⬜ The music
- ⬜ And the rest of the story…

<details>
<summary><b>How it's made</b></summary>

The game runs on the **Oracle of Ages engine**, thanks to Stewmath's complete
disassembly [oracles-disasm](https://github.com/Stewmath/oracles-disasm)
(`hack-base` branch, meant for hacks). The present/past switch of *Ages* is
the Real World / Dream World switch.

| What | Where |
| --- | --- |
| Code, scripts, data | [`hack/gulls-of-life`](https://github.com/soaresden/oracles-disasm/tree/hack/gulls-of-life) branch of the fork (additions tagged `BALLADE`): `scripts/ages/ballade.s`, `object_code/ages/interactions/marine.s` |
| Dialogue | `story/textes.yaml`, plain French; `tools/make_text.py` adds it to the game, `tools/check_text.py` checks line width (16 characters) |
| Sprites | Text drawings in `art/`; `tools/make_sprites.py` converts them |
| Opening film | `code/ages/cutscenes/film.s` (fork); background and sprites made by `tools/make_film.py` (sky and clouds, sun, sea, log, Link poses taken from the game, Marin's face); `tools/preview_film.py` previews it without building |
| Rooms | Text plans in `story/salles/` (10 x 8 metatiles per screen) and their objects in `story/salles/objets.txt`; `tools/make_rooms.py` puts them in the game; `tools/catalog.py` photographs a tileset's metatiles or rooms with their numbers |
| Map | `tools/make_map.py` draws `docs/carte_archipel.png` (the 8 islands, the Log-Boat routes, the plan of Mist Island) |
| Tests | `tools/play.py` plays the ROM in PyBoy and takes screenshots; `tools/test_phare.py`, `tools/test_lanterne.py`, `tools/test_fin.py` |
| Patch | `tools/make_patch.py` makes `out/gulls_of_life.bps` from the *Ages* (USA) ROM |

No ROM is distributed here: only the patch, to apply to your own
*Oracle of Ages* (USA) ROM.

</details>

<details>
<summary><b>Building (Windows)</b></summary>

Requirements: [MSYS2](https://www.msys2.org/) in `C:\msys64` (with `cmake`,
`make`, `mingw-w64-x86_64-gcc`) and Python 3 with
`pip install pyyaml pillow pyboy`. From Git Bash:

```bash
./setup.sh
```

```bash
./build.sh
```

The ROM is written to `out/gulls_of_life.gbc`.

</details>

## Credits

- Engine and disassembly: [oracles-disasm](https://github.com/Stewmath/oracles-disasm) by Stewmath and contributors.
- Marin's sprites: oracles-disasm's `sprites/marin` branch.
- *The Legend of Zelda* belongs to Nintendo; this is a fan-made hack, with no ROM.
