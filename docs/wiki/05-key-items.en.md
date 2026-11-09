# Key items

[한국어](05-key-items.md) | [English](05-key-items.en.md) · [Index](README.en.md)

Spoilers. Rows are conditional variants from current src/labels.h, not unique item counts or simultaneous spawns. Additional runtime gates apply; see the notes and [Data and table notation](02-data-pipeline.en.md).

`Room` is the map section that owns the marker; `Physical room` is the room holding the item when it differs. `flag` is the pickup bit (bank 3); 514 is an internal number with no real bit.

| Map | Room ID | Room | Physical room | Marker | x,y | Character | Difficulty | Condition | flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0:2 | 106 | Main Hall | — | Handgun | 521.4,552.6 | Chris | — | — | 18 |
| 0:2 | 116 | Living Room | — | Shotgun | 808.98,406.53 | — | — | conditional (Jill) | 207 |
| 0:1 | 210 | Attic | — | Assault Shotgun | 833.7,585.9 | Jill | — | Jill only, bank 0 flag 7 set | 23 |
| 0:1 | 212 | Outside Patio | — | Grenade Launcher | 824.7,616.5 | Jill | — | — | 334 |
| 4:2 | 303 | Heliport | — | Rocket Launcher | 492.6,468 | — | — | — | 368 |
| 1:3 | 30b | Boulder Passage 1 | — | Flamethrower | 437.48,427.83 | Chris | — | — | 144 |
| 1:3 | 30d | Straight Passage | — | Flamethrower | 503.55,581.62 | Chris | — | — | 146 |
| 1:2 | 312 | Small Headstone Area | — | Magnum Revolver | 675.3,575.1 | — | — | — | 109 |
| 2:2 | 401 | Room 001 | — | Self Defense Gun | 237,374.4 | — | — | — | 339 |
| 2:4 | 412 | Aqua Ring Water Tank | — | Assault Shotgun | 683.4,482.4 | Chris | — | Chris only, bank 0 flag 98 set | 401 |
| 3:4 | 315 | Jessica's Tomb | — | Barry's 44 Magnum | 354,435.6 | Jill | — | Jill only, bank 0 flag 37 set | 123 |
| 0:2 | 100 | Medical Storage Room | — | Serum | 214.58,384.12 | — | — | conditional | 128 |
| 0:2 | 100 | Medical Storage Room | — | Serum | 214.58,384.12 | — | — | conditional | 129 |
| 0:2 | 102 | Small Storeroom | — | Broken Shotgun | 254.1,360 | — | — | — | 64 |
| 0:2 | 105 | Dining Room | — | Blue Jewel | 293.7,565.2 | — | — | conditional | 130 |
| 0:2 | 105 | Dining Room | — | Shield Key | 353.1,506.7 | — | — | conditional | 131 |
| 0:2 | 113 | Bathroom | 109 Winding Corridor | Old Key | 813.9,347.4 | Chris | — | After the bathtub is drained (bank 1 flag 37) | 77 |
| 0:3 | 201 | Crypt | 10b Graveyard | Book of Curses | 627.6,260.1 | — | — | — | 106 |
| 0:3 | 201 | Crypt | 10b Graveyard | Stone & Metal Object | 609.6,259.2 | — | — | conditional | 107 |
| 0:2 | 10c | Greenhouse | — | Mask without eyes | 354.9,389.7 | — | — | conditional | 199 |
| 0:2 | 10d | Tiger Statue Room | — | Red Gemstone | 306.3,380.7 | — | — | conditional | 347 |
| 0:2 | 10d | Tiger Statue Room | — | MO Disk | 291.9,382.5 | — | — | conditional | 345 |
| 0:2 | 10e | Researcher's Bedroom | — | Old Key | 206.4,466.2 | Chris | — | — | 342 |
| 0:2 | 10f | Bar | — | Missing Music | 399,418.5 | — | — | — | 133 |
| 0:2 | 11d | Mirror Room | 111 Large Art & Mirror Rooms | Jewelry Box (2) | 757.2,504 | — | — | — | 206 |
| 0:2 | 114 | Outside Boiler | — | Herbicide | 829.2,323.1 | — | — | — | 136 |
| 0:2 | 116 | Living Room | — | Broken Shotgun | 808.98,406.53 | — | — | Never shown (spent rack item) | 208 |
| 0:2 | 121 | Large Gallery | 117 Large Gallery | Mask without a mouth | 557.4,447.3 | — | — | conditional | 323 |
| 0:2 | 118 | East Wing Storeroom | — | Fuel Canteen | 676.2,350.1 | — | — | — | 68 |
| 0:2 | 118 | East Wing Storeroom | — | Old Key | 676.2,330.3 | Chris | — | — | 70 |
| 0:2 | 119 | Courtyard Study | — | Metal Object | 624.9,355.5 | — | — | conditional | 137 |
| 0:2 | 11a | Roofed Passage | — | Stone & Metal Object | 581.05,196.78 | — | — | Bank 1 flag 139 set | 320 |
| 0:1 | 203 | Outside Balcony | — | Collar | 309.82,588.67 | — | — | — | 215 |
| 0:1 | 204 | 'C' Corridor | — | Wooden Mount | 683.4,400.5 | — | — | — | 38 |
| 0:1 | 205 | Armor Room | — | Jewelry Box (1) | 605.1,452.7 | — | — | conditional | 322 |
| 0:1 | 206 | Small Library | — | Dog Whistle | 623.1,378.9 | — | — | — | 124 |
| 0:1 | 206 | Small Library | — | Lighter | 616.8,330.3 | Jill | — | — | 81 |
| 0:1 | 209 | Bedroom | — | Old Key | 697.8,343.8 | Chris | — | — | 189 |
| 0:1 | 20a | Fish Tank Room | — | Wind Crest | 809.2,336.36 | — | — | conditional | 138 |
| 0:2 | 110 | Secret Passage | 20c Sliding Trap Room | Last Book Vol. 1 | 712.2,497.7 | — | — | conditional | 34 |
| 0:1 | 211 | Small Dining Room | 20f Small Dining Room | Music, mid-pages | 687,526.5 | — | — | conditional | 65 |
| 0:1 | 210 | Attic | — | Mask without a nose | 802.2,457.2 | — | — | — | 17 |
| 0:1 | 214 | Mirror Corridor | — | Golden Arrow | 255.9,453.6 | — | — | — | 105 |
| 0:1 | 219 | Materials Room | — | Battery | 321.6,484.2 | — | — | — | 30 |
| 0:3 | 21c | Kitchen | — | Old Key | 298.2,513.9 | Chris | — | — | 100 |
| 4:2 | 303 | Heliport | — | Signal Rockets | 379.2,383.4 | — | — | — | 325 |
| 1:3 | 306 | Underground Statue Room | — | Cylinder | 230.17,648.16 | — | — | conditional | 391 |
| 1:3 | 30a | Enrico Room | — | Hex Crank | 758.1,504 | — | — | — | 224 |
| 1:2 | 312 | Small Headstone Area | — | Star Crest | 660.9,574.2 | — | — | conditional | 110 |
| 1:2 | 312 | Small Headstone Area | — | Moon Crest | 660.9,574.2 | — | — | conditional | 111 |
| 1:2 | 312 | Small Headstone Area | — | Sun Crest | 660.9,574.2 | — | — | conditional | 112 |
| 1:2 | 314 | Cabin | — | Square Crank | 584.4,269.1 | — | — | — | 96 |
| 1:4 | 317 | Winding Underground | — | Broken Flamethrower | 439.37,406.36 | — | — | — | 365 |
| 1:4 | 31d | Lisa's Room | 319 Lisa's Room | Jewelry Box (3) | 509.7,309.6 | — | — | — | 388 |
| 2:2 | 402 | Room 001 Bathroom | — | Control Room Key | 191.1,402.3 | — | — | — | 340 |
| 2:2 | 404 | Rec Room | — | Red Book | 352.2,321.3 | — | — | — | 235 |
| 2:2 | 407 | Room 002 Bathroom | — | Key for Room 001 | 485.78,385.89 | — | — | — | 366 |
| 2:2 | 408 | Gallery | — | Key for Room 003 | 412.5,337.5 | — | — | conditional | 355 |
| 2:2 | 408 | Gallery | — | Insecticide Spray | 570,335.7 | — | — | — | 354 |
| 2:2 | 409 | Medical Room | — | 4 Empty Bottles | 438.6,444.6 | — | — | — | 72 |
| 2:2 | 409 | Medical Room | — | 4 Empty Bottles | 440.4,459 | — | — | — | 73 |
| 2:2 | 409 | Medical Room | — | 4 Empty Bottles | 436.8,468.9 | — | — | — | 74 |
| 2:2 | 409 | Medical Room | — | 4 Empty Bottles | 459.3,469.8 | — | — | — | 75 |
| 2:2 | 40c | Plant 42 Room | — | Helmet Key | 836.22,540.88 | — | — | Bank 1 flag 62 set | 69 |
| 2:4 | 412 | Aqua Ring Water Tank | — | Gallery Key | 528.6,578.7 | — | — | conditional | 384 |
| 4:3 | 501 | Passage to Heliport | — | Fuse Unit | 321.6,380.7 | — | — | — | 241 |
| 4:4 | 503 | Stairway | — | MODisk2 | 311.7,323.1 | — | — | — | 385 |
| 4:4 | 504 | Visual Data Room | — | MODisk3 | 390,347.4 | — | — | — | 406 |
| 4:4 | 504 | Visual Data Room | — | Key for the Power Area | 266.97,433.7 | — | — | conditional | 400 |
| 4:5 | 509 | X-Ray Room A | — | X-Ray of CLARK | 402.6,363.6 | — | — | Bank 1 flag 205 or 206 set | 392 |
| 4:5 | 509 | X-Ray Room A | — | X-Ray of GAIL | 402.6,363.6 | — | — | Bank 1 flag 207 or 208 set | 393 |
| 4:5 | 509 | X-Ray Room A | — | X-Ray of GAIL | 418.8,376.2 | — | — | — | 386 |
| 4:5 | 509 | X-Ray Room A | — | X-Ray of CLARK | 437.7,369.9 | — | — | — | 407 |
| 4:5 | 50a | X-Ray Room B | — | Slide Filter | 407.1,293.4 | — | — | — | 247 |
| 4:5 | 50f | Power Maze A | — | Fuel Supply Capsule (Empty) | 548.4,528.3 | — | — | — | 114 |
| 4:6 | 513 | Main Laboratory | — | Master Key | 512.4,453.6 | — | — | After the companion's death (Chris: bank 0 flag 34, Jill: bank 0 flag 37) and bank 1 flag 216 set | 405 |
| 0:1 | 216 | Library | — | Last Book Vol2 | 330.6,436.5 | — | — | — | 364 |
| 0:0 | 220 | 'Death' Passage | 217 'Death' Passage | Armor Key | 397.2,365.4 | — | — | conditional | 341 |
| 0:0 | 220 | 'Death' Passage | 217 'Death' Passage | Imitation of a key | 397.2,365.4 | — | — | conditional | 357 |
| 1:3 | 309 | Generator Room | — | Cylinder Shaft | 781.23,339.07 | — | — | conditional | 344 |
| 1:3 | 309 | Generator Room | — | Shaft | 781.23,339.07 | — | — | — | 343 |
| 1:4 | 316 | Garbage Compactor Room | — | Broken Flamethrower | 298.27,590.29 | — | — | conditional | 338 |
| 0:2 | 11e | Bar | 10f Bar | Gold Emblem | 327.9,380.7 | — | — | conditional | 135 |
| 0:2 | 105 | Dining Room | — | Emblem | 213.47,546.56 | — | — | — | 132 |
| 0:1 | 20a | Fish Tank Room | — | Fishhook | 830.25,359.91 | — | — | — | 141 |
| 4:5 | 50f | Power Maze A | — | Fuel Supply Capsule (Full) | 548.4,528.3 | — | — | Capsule inserted, power not on | 514 |
