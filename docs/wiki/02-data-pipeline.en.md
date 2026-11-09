# Data and table notation

[한국어](02-data-pipeline.md) | [English](02-data-pipeline.en.md) · [Index](README.en.md)

Spoilers. Rows are conditional variants from current src/labels.h, not unique item counts or simultaneous spawns. Additional runtime gates apply; see the notes below.

Coordinates, room mappings, pickup flags and appearance conditions were derived from a legally owned copy of the game. Room names and contents were cross-checked against [Evil Resource](https://www.evilresource.com/).

| Data | File |
| --- | --- |
| Markers and text rasters | `src/labels.h` |
| Appearance rules and item gates | `src/item_state.h` |
| Puzzle reward rules | `src/reward_rules.h`, `src/reward_state.h` |
| Rebecca rescue | `src/rescue_state.h` |
| Same-floor expanded and combined sections | `src/section_rules.h` |
| Crimson Head art and fallback table | `src/crimson_data.h` |
| Enemy records | `src/enemy_rec.h` |
| Readable room and marker metadata | `data/rooms.json`, `data/labels.json` |
| Icons | `assets/icons/` |

Builds compile pinned headers. Editing the JSON does not regenerate them. The generators for coordinates and markers read game files and are not part of this repository, so those rows are changed in the headers directly. `tools/render_labels.py` redraws the text rasters. Regenerate these wiki tables with `python tools/gen_wiki.py`; no game files or network are needed.

`item_gates` in `src/item_state.h` comes from the game's per-room "all items taken" predicates. `tools/item_gates.py` prints that table from an analysis memory image derived from a legally owned copy of the game. These are necessary conditions rather than full spawn rules, so the hand-verified rules stay beside them. Helper-call literals count as true and unreachable results add no gate, so unresolved items stay visible.

## Reading the tables

- `Map` is `area:floor`, not a floor name or a display resolution.
- `Cell` is the game's room index 0–153 and `Room ID` is the room code.
- `x,y` are map coordinates. The game applies zoom, pan and screen size to them. Korean and English markers can differ, and items in the current room can move to their exact position at runtime.
- `Character` and `Difficulty` appear only when they restrict a row; `—` means no restriction. The difficulty classes are Very Easy/Easy, Normal and Hard.
- In `Condition`, `conditional` means the game checks further conditions that have no hand-written description. `—` means no condition beyond scope and pickup state.
- Bank and flag numbers are the game's raw values. No story meaning is given for numbers without a name.
- A row must also pass scope, floor and pickup or unlock state to appear.

[Development guide](../DEVELOPMENT.md)
