# Story events (spoiler scenes)

Generated from `data/story-events.json` (`tools/build_events.py`). Markers are the purple `?` of the [6] Events toggle (off by default). Position = the room anchor: the scene's trigger area is not tied to the scene call in the game code, so each mark sits inside its room, spread apart and off the room name. Done-flag `bank:bit` is set by the scene's own code; the mark is hidden once it is 1. Character: shown only in that character's game (from the scene's cast). Event marks have no name on the map (the ? diamond only); `id` is internal.

| 방 / Room | 캐릭터 / Character | 장면 / Scenes | 완료 플래그 / Done-flag | 근거 / Evidence | id |
|---|---|---|---|---|---|
| 의약품 창고 / Medical Storage Room | chris | e100_05,05,05,01 (499 KB) | 0:77 | set after the scene call (0x5f7162, 0x5f71cf, 0x5f738f, 0x5f7862) | 0 |
| 의약품 창고 / Medical Storage Room | chris | e100_06 (122 KB) | 0:69 | set before the scene call (0x5f7423) | 1 |
| 의약품 창고 / Medical Storage Room | chris | e100_00 (703 KB) | 0:64 | set before the scene call (0x5f771d) | 2 |
| 의약품 창고 / Medical Storage Room | chris | e100_02 (74 KB) | 0:67 | set before the scene call (0x5f78ef) | 3 |
| 의약품 창고 / Medical Storage Room | jill | e100_10 (164 KB) | 0:69 | set before the scene call (0x5f7bfe) | 4 |
| 식당 / Dinning Room | jill | e105_00 (2149 KB) | 0:65 | set before the scene call (0x5fcdd0) | 5 |
| 식당 / Dinning Room | jill | e105_01,02 (1362 KB) | 0:71 | set after the scene call, also tested there (0x5fceff, 0x5fd00a) | 6 |
| 식당 / Dinning Room | jill | e105_03 (1347 KB) | 0:66 | set before the scene call (0x5fd182) | 7 |
| 식당 / Dinning Room | jill | e105_04 (5810 KB) | 0:67 | set before the scene call (0x5fd2dd) | 8 |
| 식당 / Dinning Room | jill | e105_05 (1186 KB) | 0:70 | set before the scene call, also tested there (0x5fd6ac) | 9 |
| 식당 / Dinning Room | jill | e105_06,07 (5825 KB) | 0:68 | set before the scene call, also tested there (0x5fd7ff, 0x5fd96f) | 10 |
| 중앙 홀 / Main Hall | chris | e106_01 (1118 KB) | 0:1 | set before the scene call (0x5ff954) | 11 |
| 중앙 홀 / Main Hall | chris | e106_02 (827 KB) | 0:4 | set before the scene call (0x5ff9f1) | 12 |
| 중앙 홀 / Main Hall | chris | e106_03 (663 KB) | 0:3 | set before the scene call (0x5ffade) | 13 |
| 중앙 홀 / Main Hall | jill | e106_05 (2938 KB) | 0:2 | set before the scene call (0x5ffbdd) | 14 |
| 중앙 홀 / Main Hall | jill | e106_07 (1242 KB) | 0:3 | set before the scene call (0x5ffd38) | 15 |
| 중앙 홀 / Main Hall | jill | e106_10,11,17 (1082 KB) | 0:5 | set after the scene call (0x5fffab, 0x60010b, 0x60032b) | 16 |
| 굽은 복도 / Winding Corridor | jill | e109_01 (5638 KB) | 1:37 | set before the scene call (0x601e73) | 17 |
| 굽은 복도 / Winding Corridor | chris | e109_00 (5031 KB) | 2:132 | set after the scene call (0x601ed8) | 18 |
| 굽은 복도 / Winding Corridor | jill | e109_02 (1631 KB) | 0:32 | set before the scene call (0x6026d8) | 19 |
| 바 / Bar | chris | e10f_05 (604 KB) | 0:71 | set before the scene call (0x60c2b6) | 20 |
| 바 / Bar | chris | e10f_07 (73 KB) | 0:72 | set before the scene call (0x60c465) | 21 |
| 대리석 방 / Marble Room | chris | e115_00 (430 KB) | 0:96 | set before the scene call, also tested there (0x60dbb1) | 22 |
| 대리석 방 / Marble Room | jill | e115_01 (440 KB) | 0:97 | set before the scene call, also tested there (0x60e183) | 23 |
| 대리석 방 / Marble Room | jill | e115_02 (2914 KB) | 1:246 | set before the scene call (0x60e41a) | 24 |
| 정원 서재 / Courtyard Study | chris | e119_00 (97 KB) | 0:76 | set before the scene call (0x610f99) | 25 |
| 지붕 통로 / Roofed Passage | jill | e11a_00 (550 KB) | 3:335 | set after the scene call (0x611762) | 26 |
| 작은 서재 / Small Library | chris | e206_02 (77 KB) | 0:41 | set before the scene call, also tested there (0x619423) | 27 |
| 작은 서재 / Small Library | chris | e206_03 (1896 KB) | 0:34 | set after the scene call (0x6194a8) | 28 |
| 작은 서재 / Small Library | chris | e206_04,05 (153 KB) | 0:38 | set before the scene call, also tested there (0x619708, 0x619848) | 29 |
| 어항실 / Fish Tank Room | jill | e20a_00 (1304 KB) | 0:64 | set before the scene call (0x61b844) | 30 |
| 어항실 / Fish Tank Room | jill | e20a_01 (1368 KB) | 1:79 | set after the scene call (0x61b8a5) | 31 |
| 기둥 방 / Pillar Room | chris | e20d_00 (1360 KB) | 1:116 | set before the scene call (0x61f792) | 32 |
| 기둥 방 / Pillar Room | chris | e20d_01 (542 KB) | 0:100 | set before the scene call (0x61f865) | 33 |
| 기둥 방 / Pillar Room | chris | e20d_02 (1349 KB) | 0:98 | set before the scene call (0x61f9a0) | 34 |
| 기둥 방 / Pillar Room | chris | e20d_03 (504 KB) | 0:99 | set before the scene call (0x61fb1a) | 35 |
| 기둥 방 / Pillar Room | jill | e20d_04 (875 KB) | 1:116 | set before the scene call (0x61fd02) | 36 |
| 기둥 방 / Pillar Room | jill | e20d_05 (524 KB) | 0:101 | set before the scene call (0x61fdd5) | 37 |
| 기둥 방 / Pillar Room | jill | e20d_06 (1140 KB) | 0:99 | set before the scene call (0x61ff61) | 38 |
| 기둥 방 / Pillar Room | jill | e20d_07 (475 KB) | 0:100 | set before the scene call (0x6200da) | 39 |
| 기둥 방 / Pillar Room | jill | e20d_08 (544 KB) | 0:102 | set before the scene call (0x6201a7) | 40 |
| 다락 입구 / Attic Entry | chris | e20e_00,01 (163 KB) | 1:41 | set before the scene call (0x6203e7, 0x6205d4) | 41 |
| 다락 입구 / Attic Entry | chris | e20e_03 (90 KB) | 0:42 | set before the scene call, also tested there (0x6207e3) | 42 |
| 다락 입구 / Attic Entry | jill | e20e_05 (158 KB) | 1:41 | set before the scene call (0x620b04) | 43 |
| 다락 입구 / Attic Entry | jill | e20e_06 (1520 KB) | 0:34 | set before the scene call (0x620c13) | 44 |
| 야외 테라스 / Outside Patio | chris | e212_00 (2075 KB) | 0:128 | set before the scene call (0x622dec) | 45 |
| 야외 테라스 / Outside Patio | jill | e212_01 (3531 KB) | 1:162 | set after the scene call (0x622ea1) | 46 |
| 야외 테라스 / Outside Patio | jill | e212_03 (2062 KB) | 0:128 | set before the scene call (0x62314b) | 47 |
| 야외 테라스 / Outside Patio | jill | e212_02 (2253 KB) | 0:140 | set before the scene call, also tested there (0x62320a) | 48 |
| 중앙 정원 / Main Garden | chris | e300_00 (574 KB) | 1:165 | set before the scene call (0x62ad40) | 49 |
| 중앙 정원 / Main Garden | jill | e300_01 (535 KB) | 1:165 | set before the scene call, also tested there (0x62b551) | 50 |
| 발전기실 / Generator Room | jill | e309_00 (813 KB) | 0:131 | set after the scene call (0x6334a8) | 51 |
| 엔리코의 방 / Enrico Room | chris | e30a_00 (1666 KB) | 0:101 | set before the scene call (0x636215) | 52 |
| 엔리코의 방 / Enrico Room | chris | e30a_01 (785 KB) | 0:102 | set before the scene call (0x636280) | 53 |
| 엔리코의 방 / Enrico Room | jill | e30a_02 (997 KB) | 0:103 | set before the scene call (0x63670a) | 54 |
| 엔리코의 방 / Enrico Room | jill | e30a_03 (772 KB) | 0:104 | set before the scene call (0x636770) | 55 |
| 제시카의 무덤 / Jessica's Tomb | chris | e315_00 (856 KB) | 1:264 | set before the scene call (0x640b9d) | 56 |
| 제시카의 무덤 / Jessica's Tomb | chris | e315_01 (853 KB) | 0:43 | set before the scene call (0x640ed4) | 57 |
| 제시카의 무덤 / Jessica's Tomb | jill | e315_02 (5741 KB) | 1:264 | set before the scene call (0x641d31) | 58 |
| 제시카의 무덤 / Jessica's Tomb | jill | e315_05 (1222 KB) | 0:38 | set before the scene call, also tested there (0x64263f) | 59 |
| 쓰레기 압축실 / Garbage Compactor Room | jill | e316_02 (1748 KB) | 0:141 | set before the scene call (0x64366d) | 60 |
| 쓰레기 압축실 / Garbage Compactor Room | jill | e316_01 (1153 KB) | 0:138 | set after the scene call, also tested there (0x6436ff) | 61 |
| 쓰레기 압축실 / Garbage Compactor Room | jill | e316_00 (1315 KB) | 0:137 | set after the scene call (0x643be3) | 62 |
| 중앙 복도 / Central Corridor | jill | e405_01 (804 KB) | 0:133 | set at 0x64a000; trigger tests it at 0x4c0ced (0x649fa4) | 63 |
| 중앙 복도 / Central Corridor | chris | e405_00 (1429 KB) | 0:131 | set before the scene call (0x64a184) | 64 |
| 중앙 복도 / Central Corridor | jill | e405_02 (1527 KB) | 0:132 | set before the scene call (0x64a704) | 65 |
| 002호실 / Room 002 | jill | e406_00 (2688 KB) | 0:135 | set before the scene call (0x64b00c) | 66 |
| 미술관 / Gallery | chris | e408_00,01 (877 KB) | 0:130 | set before the scene call (0x64be36, 0x64bf98) | 67 |
| 의무실 / Medical Room | chris | e409_09,00 (98 KB) | 0:37 | set before the scene call (0x64d26f, 0x64d54f) | 68 |
| 경비실 / Guard Room | chris | e40f_00,01 (47 KB) | 0:103 | set before the scene call (0x653281, 0x653318) | 69 |
| 헬기장 통로 / Passage to Heliport | chris | e501_00 (483 KB) | 1:325 | set before the scene call (0x659d07) | 70 |
| 헬기장 통로 / Passage to Heliport | jill | e501_05 (496 KB) | 1:325 | set before the scene call (0x65a54a) | 71 |
| 감방 입구 / Cell Entrance | both | e50b_01 (289 KB) | 1:224 | set after the scene call, also tested there (0x662a60) | 72 |
| 승강기 입구 / Elevator Entry | chris | e50c_01 (293 KB) | 1:334 | set before the scene call (0x663020) | 73 |
| 승강기 입구 / Elevator Entry | jill | e50c_02,03 (1196 KB) | 1:334 | set after the scene call (0x663098, 0x663105) | 74 |
| 감방 / Cell | both | e512_00,01,02,03 (122 KB) | 1:332 | set before the scene call (0x665252, 0x6652d3, 0x665413, 0x665493) | 75 |

## Found but not placed

| 방 / Room | 장면 / Scene | 호출 / Call | 이유 / Reason |
|---|---|---|---|
| 의약품 창고 / Medical Storage Room | e100_03 | 0x5f7638 | the scene sets no flag, so it cannot be hidden once played |
| 의약품 창고 / Medical Storage Room | e100_04 | 0x5f792a | the scene sets no flag, so it cannot be hidden once played |
| 의약품 창고 / Medical Storage Room | e100_11 | 0x5f79c5 | the scene sets no flag, so it cannot be hidden once played |
| 의약품 창고 / Medical Storage Room | - | 0x5f80af | scene number computed at run time |
| 중앙 홀 / Main Hall | e106_00 | 0x5ff86c | no characters in the scene (camera/object only) |
| 중앙 홀 / Main Hall | e106_04 | 0x5ffb5b | no characters in the scene (camera/object only) |
| 중앙 홀 / Main Hall | e106_08 | 0x5ffd8f | the scene sets no flag, so it cannot be hidden once played |
| 중앙 홀 / Main Hall | e106_09 | 0x5ffdff | the scene sets no flag, so it cannot be hidden once played |
| 중앙 홀 / Main Hall | e106_13 | 0x60015c | the scene sets no flag, so it cannot be hidden once played |
| 중앙 홀 / Main Hall | e106_12 | 0x6001fd | the scene sets no flag, so it cannot be hidden once played |
| 중앙 홀 / Main Hall | e106_19 | 0x60037c | the scene sets no flag, so it cannot be hidden once played |
| 중앙 홀 / Main Hall | e106_18 | 0x60041d | the scene sets no flag, so it cannot be hidden once played |
| 바 / Bar | - | 0x60be5e | scene number computed at run time |
| 바 / Bar | - | 0x60bfec | scene number computed at run time |
| 바 / Bar | e10f_04 | 0x60c145 | the scene sets no flag, so it cannot be hidden once played |
| 바 / Bar | e10f_06 | 0x60c38c | the scene sets no flag, so it cannot be hidden once played |
| 바 / Bar | e10f_08 | 0x60c537 | the scene sets no flag, so it cannot be hidden once played |
| 작은 서재 / Small Library | e206_00 | 0x61909f | the scene sets no flag, so it cannot be hidden once played |
| 작은 서재 / Small Library | e206_01 | 0x6191d4 | the scene sets no flag, so it cannot be hidden once played |
| 다락 입구 / Attic Entry | e20e_02 | 0x620758 | the scene sets no flag, so it cannot be hidden once played |
| 다락 입구 / Attic Entry | e20e_04 | 0x62093e | the scene sets no flag, so it cannot be hidden once played |
| 다락 / Attic | e210_00 | 0x6219e2 | entering the Attic starts the Yawn fight (boss room rule) |
| 다락 / Attic | e210_01 | 0x622068 | entering the Attic starts the Yawn fight (boss room rule) |
| 야외 테라스 / Outside Patio | e212_04 | 0x6235de | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_00 | 0x62d65d | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_02 | 0x62d82f | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_04 | 0x62d981 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_10 | 0x62da31 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_12 | 0x62da92 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_12 | 0x62dca9 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_05 | 0x62eb7e | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_07 | 0x62ece8 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_09 | 0x62ee31 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_11 | 0x62eede | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 / Heliport | e303_13 | 0x62ef42 | the scene sets no flag, so it cannot be hidden once played |
| 지그재그 길 / Zigzag Path | - | 0x62fcbf | scene number computed at run time |
| 바위 통로 1 / Boulder Passage 1 | - | 0x6371dd | scene number computed at run time |
| 진흙길 / Muddy Path | - | 0x63a341 | scene number computed at run time |
| 제시카의 무덤 / Jessica's Tomb | - | 0x641fe8 | scene number computed at run time |
| 의무실 / Medical Room | e409_04 | 0x64d302 | the scene sets no flag, so it cannot be hidden once played |
| 의무실 / Medical Room | e409_05 | 0x64d32b | the scene sets no flag, so it cannot be hidden once played |
| 의무실 / Medical Room | e409_11 | 0x64d3f5 | the scene sets no flag, so it cannot be hidden once played |
| 의무실 / Medical Room | e409_01 | 0x64d5e2 | the scene sets no flag, so it cannot be hidden once played |
| 의무실 / Medical Room | e409_02 | 0x64d60b | the scene sets no flag, so it cannot be hidden once played |
| 의무실 / Medical Room | e409_10 | 0x64d6d5 | the scene sets no flag, so it cannot be hidden once played |
| 의무실 / Medical Room | e409_03 | 0x64d84a | the scene sets no flag, so it cannot be hidden once played |
| 의무실 / Medical Room | e409_06 | 0x64d8e3 | the scene sets no flag, so it cannot be hidden once played |
| 의무실 / Medical Room | - | 0x64d986 | scene number computed at run time |
| 식물 42 방 / Plant 42 Room | e40c_00 | 0x650ab0 | entering starts the Plant 42 fight (boss room rule) |
| 식물 42 방 / Plant 42 Room | e40c_01 | 0x650b8c | entering starts the Plant 42 fight (boss room rule) |
| 식물 42 방 / Plant 42 Room | e40c_02 | 0x650c41 | entering starts the Plant 42 fight (boss room rule) |
| 식물 42 방 / Plant 42 Room | e40c_03 | 0x650e45 | entering starts the Plant 42 fight (boss room rule) |
| 식물 42 방 / Plant 42 Room | e40c_04 | 0x650f11 | entering starts the Plant 42 fight (boss room rule) |
| 식물 42 방 / Plant 42 Room | e40c_05 | 0x651001 | entering starts the Plant 42 fight (boss room rule) |
| 대형 수조 통로 / Aqua Ring Walkway | e40e_00 | 0x652e9f | the scene sets no flag, so it cannot be hidden once played |
| 입구 / Entrance | e500_00 | 0x6599ab | the scene sets no flag, so it cannot be hidden once played |
| 입구 / Entrance | e500_01 | 0x6599fc | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 통로 / Passage to Heliport | e501_01 | 0x659e44 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 통로 / Passage to Heliport | e501_02 | 0x65a051 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 통로 / Passage to Heliport | e501_03 | 0x65a171 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 통로 / Passage to Heliport | e501_04 | 0x65a238 | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 통로 / Passage to Heliport | e501_06 | 0x65a69d | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 통로 / Passage to Heliport | e501_07 | 0x65a8ac | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 통로 / Passage to Heliport | e501_08 | 0x65aabc | the scene sets no flag, so it cannot be hidden once played |
| 헬기장 통로 / Passage to Heliport | e501_09 | 0x65ac78 | the scene sets no flag, so it cannot be hidden once played |
| O자 통로 / 'O' Room | e505_00 | 0x65cd8a | the scene sets no flag, so it cannot be hidden once played |
| 암호 복도 / Pass Code Corridor | e508_00 | 0x65ef6b | the scene sets no flag, so it cannot be hidden once played |
| 암호 복도 / Pass Code Corridor | e508_02 | 0x65efbc | the scene sets no flag, so it cannot be hidden once played |
| 암호 복도 / Pass Code Corridor | e508_01 | 0x65f00c | the scene sets no flag, so it cannot be hidden once played |
| 암호 복도 / Pass Code Corridor | e508_03 | 0x65f05c | the scene sets no flag, so it cannot be hidden once played |
| 감방 입구 / Cell Entrance | e50b_00 | 0x6629b0 | the scene sets no flag, so it cannot be hidden once played |
| 승강기 입구 / Elevator Entry | e50c_00 | 0x662f88 | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_00 | 0x66567a | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_01 | 0x6656fb | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_02 | 0x6657b0 | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_03 | 0x665821 | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_04 | 0x665889 | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_05 | 0x66590b | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_06 | 0x66598b | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_07 | 0x665a71 | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_08 | 0x665af1 | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_09 | 0x665bb0 | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 / Main Laboratory | e513_00 | 0x665c2a | the scene sets no flag, so it cannot be hidden once played |
| 중앙 연구실 입구 / Main Laboratory Entrance | e514_00 | 0x6674bb | the scene sets no flag, so it cannot be hidden once played |

## Native trigger corrections (2026-11-08)

The scene cast does not establish the playable character: the Main Hall's e106_01 and e106_02 belong to the Chris initialization method (0x4a3f60, vtable 0xc28614 +0x24); Jill uses +0x28 / 0x4a43b0. Dining's alternative scenes 1/2 stop registering after bank0[66], and scene5 after bank0[68] (0x4a3aa1..0x4a3b6d). Medical Storage's Jill scene10 additionally requires bank0[34] (0x4a0f88..0x4a0fdc). These predicates are applied by synth_marks.h.

Residence e405_01 completes bank0[133], tested by its room init; bank1[188] belongs to the separate insecticide routine. They differ in real saves, so one must never substitute for the other. The wasp suppression continues to read bank1[188].
