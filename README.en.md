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

![Map of the Sleepless Archipelago and plan of Mist Island](docs/carte_archipel.png)

![Opening film: the seagull lands on Link's log](docs/film_ouverture.png)

![Chapter 1: Marin wakes Link up on the beach](docs/chapitre1_plage.png)

![The inn, sleep, the Dream World and the dream bridge](docs/auberge_songe.png)

![The Dark Lighthouse: the sword, the entrance, the small key, the Lantern, the Hollow Keeper](docs/phare.png)

## Status

| Part | Status |
| --- | --- |
| New game: no *Ages* intro, Link wakes up on a beach | ✅ |
| Marin as a seagull (sprite drawn for the game, with her hibiscus flower) | ✅ |
| Chapter 1: Link lies unconscious, Marin flies in, lands and talks to him (with a choice), then snuggles into Link's tunic | ✅ |
| French text, with accents (the game is in French first) | ✅ |
| Opening film before the title screen: at dawn, Link drifts on his log and looks up; Marin's face appears in the clouds (like *Link's Awakening*'s secret ending) and fades away; a seagull flies out of it and lands, "?", a wink, "!", they both jump for joy and their hearts fly up | ✅ |
| *Gulls of Life* title screen (currently *Ages*') | to do |
| Talking to Marin: a short press on **Select** (a line for the current place, otherwise a random one); holding Select opens the map | ✅ |
| Marin's lines and hints for every place in the adventure | to do |
| Mist Island (16 screens): beach, fishing port, Port-Veille and its inn, path with a broken bridge, woods, rocks, cliffs, Lighthouse Cape | ✅ |
| Port-Veille's people and their dialogue: the innkeeper, the old fisherman, the children who no longer play, the sleepless lady, the old man counting sheep, the teen who dreams of sailing | ✅ |
| The inn: push the bed, Link falls asleep and wakes up in the **Dream World** | ✅ |
| The Dream World: the island in blue tones, the screen gently waving like underwater, human Marin (the hands scene); Select in the Dream World = wake up at the same spot | ✅ |
| First puzzle: the path's broken bridge is whole in the Dream World; cross it in a dream and wake up on the other side | ✅ |
| The showman's games: Rupee Dig and Mamono (minesweepers, heart pieces on the hardest levels) | to do |
| The old fisherman gives Link his sword back (fished out after the shipwreck) | ✅ |
| The Dark Lighthouse, on 2 floors: small key, locked door, boss key, the **Lantern of Dreams**, the stairs, the boss door and the **Hollow Keeper** | ✅ |
| After the boss: the first verse (text ready, full fight not tested yet), the Lantern switching to the Dream World anywhere | to do |
| The reunion in the Dream World: Marin throws herself into Link's arms (hearts fly up) | ✅ |
| Music: Marin's song | to do |

## How it's made

The game runs on the **Oracle of Ages engine**, thanks to Stewmath's complete
disassembly [oracles-disasm](https://github.com/Stewmath/oracles-disasm)
(`hack-base` branch, meant for hacks). The present/past switch of *Ages* will
become the Real World / Dream World switch.

| What | Where |
| --- | --- |
| Code, scripts, data | [`hack/gulls-of-life`](https://github.com/soaresden/oracles-disasm/tree/hack/gulls-of-life) branch of the fork (additions tagged `BALLADE`): `scripts/ages/ballade.s`, `object_code/ages/interactions/marine.s` |
| Dialogue | `story/textes.yaml`, plain French; `tools/make_text.py` adds it to the game, `tools/check_text.py` checks line width (16 characters) |
| Sprites | Text drawings in `art/`; `tools/make_sprites.py` converts them |
| Opening film | `code/ages/cutscenes/film.s` (fork); background and sprites made by `tools/make_film.py` (sky and clouds, sun, sea, log, Link poses taken from the game, Marin's face); `tools/preview_film.py` previews it without building |
| Rooms | Text plans in `story/salles/` (10 x 8 metatiles per screen) and their objects in `story/salles/objets.txt`; `tools/make_rooms.py` puts them in the game; `tools/catalog.py` photographs a tileset's metatiles or rooms with their numbers |
| Map | `tools/make_map.py` draws `docs/carte_archipel.png` (the 8 islands, the Log-Boat routes, the plan of Mist Island) |
| Tests | `tools/play.py` plays the ROM in PyBoy and takes screenshots |

No ROM is distributed here: there will be a patch to apply to your own
*Oracle of Ages* (USA) ROM.

## Building (Windows)

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

## Credits

- Engine and disassembly: [oracles-disasm](https://github.com/Stewmath/oracles-disasm) by Stewmath and contributors.
- Human Marin: graphics from oracles-disasm's `sprites/marin` branch.
- *The Legend of Zelda* belongs to Nintendo; this is a fan-made hack, with no ROM.
