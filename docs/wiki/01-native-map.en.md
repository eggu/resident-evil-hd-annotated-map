# Native map and scope

[한국어](01-native-map.md) | [English](01-native-map.en.md) · [Index](README.en.md)

Annotations overlay the native map. `8` cycles visited rooms → revealed rooms → all rooms. All rooms shows unexplored outlines and door lines, but floor tabs stay native, so you cannot switch to a floor or area you have not reached. Items you picked up and puzzles you finished disappear from the map.

The first run uses English, visited rooms and room names only. The legend shows the current state.

| Key | Action |
| --- | --- |
| `0` | All annotations on/off |
| `1` | Room names |
| `2` | Locked doors and required keys |
| `3` | Key items |
| `4` | Files and maps |
| `5` | Puzzles |
| `6` | Events (spoiler story scenes, hidden at first) |
| `7` | Common items |
| `8` | Enemies and Crimson Heads (hold while enemies are on: time left on/off) |
| `9` | Scope |
| `\` (₩) | Korean / English |
| `-` · `+` | Name size (50–150%) |
| `[` · `]` | Name opacity (10–100%) |
| `Shift` + `-` · `+` | Icon size (50–200%) |
| `Shift` + `[` · `]` | Icon opacity (10–100%) |
| `H` | Item names, 3 states: all → all except common items → off (off at first) |
| `~` | Fold the legend |
| The Attack button | Map zoom 2x on/off |
| Directions (while zoomed) | Move the map |

Reopening the map returns to 1x.

While zoomed, rooms and door marks scale 2x and the player marker moves with the map at native size. The floor name moves above the legend, the native guide UI is hidden, and every typewriter and item box is drawn as an icon at its spot in the room. Zoomed out, only those the native map does not already mark are drawn.

## Native data reference

Addresses refer to the `bhd.exe` named by `game_exe_sha256` in `verification/source-snapshot.json`.

| Address | Meaning |
| --- | --- |
| `0xc3d0f8` | Map object vtable; slots 0–9 capture the map object |
| Map object `+0x6268` / `+0x626c` | Area / floor |
| Map object `+0x629c` | Map or item box view |
| Map object `+0x6090` | Map offset |
| `[0xd5a048]` `+0xb8` / `+0xbc` | 16:9 picture size inside the back buffer |
| `0x555377` / `0x5543b1` | Bank 7 flag tests for outlines / door lines, redirected by all-rooms scope |
| `0x5561d0` | Map draw function, 39 calls sorted for zoom |
| `0x4d9230` | Pad directions (held) |

Native 2D output is `48 + .9x`, `36 + .9y`, plus the map offset.

[Installation and keys](../../README.en.md) · [Development guide](../DEVELOPMENT.md)
