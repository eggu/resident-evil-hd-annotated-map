# RE1 HD Annotated Map - Survivor's Notes 1.0.0

First public release. An ASI mod for Resident Evil / Biohazard HD REMASTER (Steam or GOG) that adds annotations to the game's own map screen.

## English

- Shows room names, locked doors and their keys, key items (weapons included), files and maps, puzzles, events, common items, typewriters and item boxes, and enemies.
- Annotations follow your progress: picked-up items, opened doors, solved puzzles and defeated enemies disappear. Crimson Heads stay grey until they can revive, and you can show the time left.
- Events are marks for story scenes, shown as a purple `?` with no name (hidden at first because they are spoilers). A mark sits where the scene starts when that spot is known; otherwise there is one mark per room beside the room name. It disappears once the scenes have played.
- Choose how much to reveal: visited rooms (default), rooms revealed by a map, or all rooms.
- English and Korean. Number keys 0-9 switch each category, `\` (`₩` on Korean keyboards) switches the language, and a legend on the map shows the current state.
- Adjust name size and opacity, icon size and opacity, item names (H) and fold the legend (~). Settings are saved to `scripts/RE1HD.AnnotatedMap.ini`, including optional per-category colours.
- Zoom the map 2x with the Attack button and move it with the direction input.
- Room names are placed on each room's real shape, and names stay clear of markers where possible.
- Installation: copy `dinput8.dll` ([Ultimate ASI Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader), included) and `scripts/` into the folder with `bhd.exe`. If you already have a `dinput8.dll`, copy `scripts/` only. Close the game first.
- The executable and saves are not modified.

Known limits: enemies appear only in rooms you have entered; the layout was tuned at 1440p, so names can overlap at other resolutions.

## 한국어

첫 공개 버전입니다. Steam·GOG판 Resident Evil / Biohazard HD REMASTER의 지도 화면에 주석을 더하는 ASI 모드입니다.

- 방 이름, 잠긴 문과 열쇠, 핵심 아이템(무기 포함), 문서·지도, 퍼즐, 이벤트, 일반 아이템, 타자기·아이템 상자, 적을 표시합니다.
- 진행에 따라 표시가 바뀝니다. 주운 아이템, 열린 문, 푼 퍼즐, 쓰러뜨린 적은 사라집니다. 크림슨 헤드는 부활 전까지 회색이며 남은 시간도 볼 수 있습니다.
- 이벤트는 이야기 장면의 표시로, 이름 없는 보라색 `?`입니다(스포일러라 처음에는 숨김). 장면이 시작되는 위치를 알면 그 자리에, 모르면 방마다 하나를 방 이름 옆에 표시하며 장면을 보면 사라집니다.
- 표시 범위를 고릅니다: 방문한 방(기본), 지도로 공개된 방, 모든 방.
- 한국어/영어를 지원합니다. 숫자 키 0–9로 분류별로 켜고 끄고, `\`(한국 키보드에서는 `₩`)로 언어를 바꾸며, 지도의 범례에 현재 상태가 표시됩니다.
- 이름 크기·불투명도, 아이콘 크기·불투명도, 아이템 이름(H), 범례 접기(~)를 조절할 수 있습니다. 설정은 `scripts/RE1HD.AnnotatedMap.ini`에 저장되며 분류별 색도 바꿀 수 있습니다.
- 공격 버튼으로 지도를 2배 확대하고 방향 입력으로 움직입니다.
- 방 이름을 각 방의 실제 모양 위에 배치하고, 이름이 표시와 겹치지 않도록 자리를 고릅니다.
- 설치: 게임을 종료한 뒤 `dinput8.dll`([Ultimate ASI Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader), 포함)과 `scripts/`를 `bhd.exe`가 있는 폴더에 복사합니다. 이미 `dinput8.dll`이 있으면 `scripts/`만 복사하세요.
- EXE와 세이브는 수정하지 않습니다.

알려진 한계: 적은 들어가 본 방에서만 표시됩니다. 화면 배치는 1440p 기준이라 해상도에 따라 이름이 겹칠 수 있습니다.
