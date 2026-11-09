# Locks and keys

[한국어](04-locks-keys.md) | [English](04-locks-keys.en.md) · [Index](README.en.md)

Spoilers. Rows are conditional variants from current src/labels.h, not unique item counts or simultaneous spawns. Additional runtime gates apply; see the notes and [Data and table notation](02-data-pipeline.en.md).

The name is the key that opens the door. The marker sits on the side not yet entered (`x,y` in the room, `x2,y2` in the connected room) and disappears once the door is unlocked. `flag` is the door-unlock bit.

| Map | Room ID | Room | Connected room | Key | x,y | x2,y2 | Character | Difficulty | Condition | flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0:2 | 101 | West Wing Inner Stairway | 102 Small Storeroom | Lock Pick | 226.65,342.7 | 226.65,364.7 | Jill | — | — | 4 |
| 0:2 | 101 | West Wing Inner Stairway | 102 Small Storeroom | Old Key | 226.65,342.7 | 226.65,364.7 | Chris | — | — | 4 |
| 0:2 | 101 | West Wing Inner Stairway | 103 Northern Corridor & Tea Room | Armor Key | 247.6,339.3 | 269.6,339.3 | — | — | — | 34 |
| 0:2 | 103 | Northern Corridor & Tea Room | 10f Bar | Armor Key | 369.75,495.2 | 369.75,473.2 | — | — | — | 6 |
| 0:2 | 106 | Main Hall | 111 Large Art & Mirror Rooms | Helmet Key | 579.7,513.45 | 601.7,513.45 | — | — | — | 19 |
| 0:2 | 107 | Art Room | 108 'L' Corridor | Sword Key | 677.8,576.9 | 699.8,576.9 | — | — | — | 2 |
| 0:2 | 107 | Art Room | 11c Hidden Wardrobe | Closet Key | 733.6,549 | 755.6,549 | — | — | — | 46 |
| 0:2 | 109 | Winding Corridor | 114 Outside Boiler | Lock Pick | 834.4,392.4 | 856.4,392.4 | Jill | — | — | 18 |
| 0:2 | 109 | Winding Corridor | 114 Outside Boiler | Old Key | 834.4,392.4 | 856.4,392.4 | Chris | — | — | 18 |
| 0:2 | 10a | Dark Corridor | 117 Large Gallery | Armor Key | 602.85,394.9 | 602.85,416.9 | — | — | — | 33 |
| 0:2 | 10a | Dark Corridor | 119 Courtyard Study | Emblem Key | 628.05,385.4 | 628.05,363.4 | — | — | — | 3 |
| 0:2 | 10b | Graveyard | 117 Large Gallery | Lock Pick | 563.25,416.9 | 563.25,394.9 | Jill | — | — | 39 |
| 0:2 | 10b | Graveyard | 117 Large Gallery | Old Key | 563.25,416.9 | 563.25,394.9 | Chris | — | — | 39 |
| 0:1 | 101 | West Wing Inner Stairway | 202 Dining Room | Sword Key | 246.45,492.1 | 246.45,514.1 | — | — | — | 28 |
| 0:1 | 101 | West Wing Inner Stairway | 203 Outside Balcony | Lock Pick | 221.9,490.5 | 199.9,490.5 | Jill | — | — | 13 |
| 0:1 | 101 | West Wing Inner Stairway | 203 Outside Balcony | Old Key | 221.9,490.5 | 199.9,490.5 | Chris | — | — | 13 |
| 0:1 | 204 | 'C' Corridor | 205 Armor Room | Armor Key | 709.7,452.7 | 687.7,452.7 | — | — | — | 7 |
| 0:1 | 204 | 'C' Corridor | 20d Pillar Room | Armor Key | 671.25,507.4 | 671.25,529.4 | — | — | — | 35 |
| 0:1 | 106 | Main Hall | 204 'C' Corridor | Sword Key | 577,505.35 | 599,505.35 | — | — | — | 1 |
| 0:1 | 207 | East Wing Stairway | 208 Deer Room | Armor Key | 754.05,325.6 | 754.05,347.6 | — | — | — | 10 |
| 0:1 | 208 | Deer Room | 20a Fish Tank Room | Lock Pick | 772.3,355.95 | 794.3,355.95 | Jill | — | — | 26 |
| 0:1 | 208 | Deer Room | 20a Fish Tank Room | Old Key | 772.3,355.95 | 794.3,355.95 | Chris | — | — | 26 |
| 0:1 | 20b | Resting Room | 20c Sliding Trap Room | Helmet Key | 797.9,391.95 | 775.9,391.95 | — | — | — | 29 |
| 0:1 | 20e | Attic Entry | 210 Attic | Shield Key | 793.9,589.5 | 815.9,589.5 | — | — | — | 9 |
| 0:1 | 106 | Main Hall | 212 Outside Patio | Armor Key | 577.9,595.8 | 599.9,595.8 | — | — | — | 31 |
| 0:1 | 101 | West Wing Inner Stairway | 215 Trophy Room | Helmet Key | 221,396.45 | 199,396.45 | — | — | — | 21 |
| 0:0 | 216 | Library | 217 'Death' Passage | Helmet Key | 410.9,454.95 | 388.9,454.95 | — | — | — | 38 |
| 0:3 | 103 | Northern Corridor & Tea Room | 21c Kitchen | Sword Key | 329,450 | 307,450 | — | — | — | 15 |
| 2:2 | 400 | Entry Corridor | 401 Room 001 | Key for Room 001 | 231.15,455.6 | 231.15,433.6 | — | — | — | 27 |
| 2:2 | 405 | Central Corridor | 408 Gallery | Gallery Key | 409.6,509.85 | 431.6,509.85 | — | — | — | 25 |
| 2:2 | 408 | Gallery | 40a Room 003 | Key for Room 003 | 568,491.4 | 590,491.4 | — | — | — | 40 |
| 2:3 | 40e | Aqua Ring Walkway | 411 Control Room | Control Room Key | 457.05,585.2 | 457.05,585.2 | — | — | — | 42 |
| 4:3 | 500 | Entrance | 501 Passage to Heliport | Master Key | 545.9,454.05 | 523.9,454.05 | — | — | After the companion's death (Chris: bank 0 flag 34, Jill: bank 0 flag 37) | 45 |
| 4:5 | 505 | 'O' Room | 507 Morgue | Key for the Power Area | 505.65,396.2 | 505.65,374.2 | — | — | — | 49 |
| 4:5 | 505 | 'O' Room | 50c Elevator Entry | Key for the Power Area | 525.7,395.55 | 547.7,395.55 | — | — | — | 48 |
| 4:5 | 50b | Cell Entrance | 512 Cell | Master Key | 409.35,231.1 | 409.35,253.1 | — | — | After the companion's death (Chris: bank 0 flag 34, Jill: bank 0 flag 37) | 47 |
