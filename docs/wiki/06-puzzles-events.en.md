# Puzzles and events

[한국어](06-puzzles-events.md) | [English](06-puzzles-events.en.md) · [Index](README.en.md)

Spoilers. Rows are conditional variants from current src/labels.h, not unique item counts or simultaneous spawns. Additional runtime gates apply; see the notes and [Data and table notation](02-data-pipeline.en.md).

An orange ! is a puzzle and a purple ? is an event. Positions are approximate. `step` is the number of inputs done so far in a multi-step puzzle, and numbers such as `(0)` are part of the marker name. Fuel tanks show the refills left, turn grey when empty and follow the room name key `1`. `flag` is the pickup bit (bank 3) of the puzzle's reward; 900–904, 512, 513 and 515 are internal numbers with no real bit.

| Map | Room ID | Room | Type | Marker | x,y | Character | Difficulty | Condition | flag | step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0:2 | 102 | Small Storeroom | Fuel tank | Fuel Tank | 242.4,383.4 | — | — | — | 900 | — |
| 0:2 | 114 | Outside Boiler | Fuel tank | Fuel Tank | 799.5,317.7 | — | — | — | 901 | — |
| 0:2 | 118 | East Wing Storeroom | Fuel tank | Fuel Tank | 685.2,330.3 | — | — | — | 902 | — |
| 2:2 | 403 | Storeroom | Fuel tank | Fuel Tank | 203.7,541.8 | — | — | — | 903 | — |
| 4:4 | 503 | Stairway | Fuel tank | Fuel Tank | 642,475.2 | — | — | — | 904 | — |
| 0:1 | 206 | Small Library | Event | Rescue Rebecca | 618.05,352.06 | Chris | — | Chris only, while the rescue event is active | — | — |
| 0:3 | 201 | Crypt | Puzzle | (0) Stone & Metal Object | 560.21,242.46 | — | — | conditional | 107 | 0 |
| 0:3 | 201 | Crypt | Puzzle | (1) Stone & Metal Object | 560.21,242.46 | — | — | conditional | 107 | 1 |
| 0:3 | 201 | Crypt | Puzzle | (2) Stone & Metal Object | 560.21,242.46 | — | — | conditional | 107 | 2 |
| 0:3 | 201 | Crypt | Puzzle | (3) Stone & Metal Object | 560.21,242.46 | — | — | conditional | 107 | 3 |
| 0:3 | 201 | Crypt | Puzzle | (4) Stone & Metal Object | 560.21,242.46 | — | — | conditional | 107 | 4 |
| 0:2 | 105 | Dining Room | Puzzle | Shield Key | 219,546.3 | — | — | conditional | 131 | 0 |
| 0:1 | 202 | Dining Room | Puzzle | Blue Jewel | 341.4,573.3 | — | — | conditional | 130 | 0 |
| 1:3 | 306 | Underground Statue Room | Puzzle | Cylinder | 258.6,598.5 | — | — | conditional | 391 | 0 |
| 0:2 | 10d | Tiger Statue Room | Puzzle | MO Disk | 292.07,395.84 | — | — | conditional | 345 | 0 |
| 0:0 | 220 | 'Death' Passage | Puzzle | Armor Key | 398.1,366.3 | — | — | conditional | 341 | 0 |
| 0:2 | 10c | Greenhouse | Puzzle | Mask without eyes | 431.4,392.4 | — | — | conditional | 199 | 0 |
| 0:1 | 205 | Armor Room | Puzzle | Jewelry Box (1) | 655.5,451.8 | — | — | conditional | 322 | 0 |
| 0:2 | 117 | Large Gallery | Puzzle | Mask without a mouth | 595.15,450.57 | — | — | conditional | 323 | 0 |
| 0:1 | 20a | Fish Tank Room | Puzzle | Wind Crest | 807.52,336.36 | — | — | conditional | 138 | 0 |
| 0:1 | 20f | Small Dining Room | Puzzle | (0) Music, mid-pages | 728.4,557.1 | — | — | conditional | 65 | 0 |
| 0:1 | 20f | Small Dining Room | Puzzle | (1) Music, mid-pages | 728.4,557.1 | — | — | conditional | 65 | 1 |
| 0:1 | 20f | Small Dining Room | Puzzle | (2) Music, mid-pages | 728.4,557.1 | — | — | conditional | 65 | 2 |
| 0:2 | 119 | Courtyard Study | Puzzle | Metal Object | 636.6,342 | — | — | conditional | 137 | 0 |
| 1:2 | 312 | Small Headstone Area | Puzzle | Sun, Moon & Star Crests | 660.9,574.2 | — | — | conditional | 110 | 0 |
| 1:4 | 316 | Garbage Compactor Room | Puzzle | Broken Flamethrower | 294.6,644.4 | — | — | conditional | 338 | 0 |
| 4:4 | 504 | Visual Data Room | Puzzle | Key for the Power Area | 345.9,416.7 | — | — | conditional | 400 | 0 |
| 2:2 | 405 | Central Corridor | Puzzle | Key for Room 003 | 423.45,359.36 | — | — | conditional | 355 | 0 |
| 2:4 | 412 | Aqua Ring Water Tank | Puzzle | Gallery Key | 502.5,578.7 | — | — | conditional | 384 | 0 |
| 0:2 | 10f | Bar | Puzzle | Gold Emblem | 352.2,448.2 | — | — | conditional | 135 | 0 |
| 0:1 | 215 | Trophy Room | Puzzle | Red Gemstone | 182.1,405.9 | — | — | conditional | 143 | 0 |
| 0:1 | 215 | Trophy Room | Puzzle | Yellow Gemstone | 178.5,350.1 | — | — | conditional | 142 | 0 |
| 4:5 | 50a | X-Ray Room B | Puzzle | Refill Fuel Capsule | 409.8,294.3 | — | — | Capsule not charged or inserted, power not on | 512 | — |
| 4:5 | 50f | Power Maze A | Puzzle | Insert Fuel Capsule | 548.4,528.3 | — | — | Capsule charged, not inserted, power not on | 513 | — |
| 0:2 | 116 | Living Room | Puzzle | Shotgun | 808.98,433.97 | — | — | Bank 1 flag 110 clear, bank 3 flag 207 clear | 515 | — |
