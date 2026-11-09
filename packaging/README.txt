RE1 HD Annotated Map - Survivor's Notes - Resident Evil HD REMASTER
상세 지도: 생존자의 메모

지원: Steam·GOG판 Resident Evil / Biohazard HD REMASTER(bhd.exe) + Ultimate ASI Loader(포함).
1996년 원작용이 아닙니다.
게임 지도에 방 이름, 잠긴 문과 열쇠, 핵심 아이템, 문서·지도, 퍼즐·이벤트, 일반 아이템, 타자기·아이템 상자, 적을 표시합니다.

설치
1. 게임을 종료합니다.
2. ZIP의 내용을 bhd.exe가 있는 게임 폴더에 폴더 구조 그대로 복사합니다.
   (dinput8.dll, scripts/RE1HD.AnnotatedMap.asi, scripts/RE1HD.AnnotatedMap.ini)
   Fusion Fix 등으로 dinput8.dll이 이미 있으면 dinput8.dll은 건너뛰고 scripts만 복사하세요.
3. 게임을 실행하고 지도를 엽니다.
업그레이드할 때는 기존 scripts/RE1HD.AnnotatedMap.ini를 건너뛰거나 백업 후 복원하세요.

사용 (지도 화면에서만 작동)
- 숫자 키: 0 전체 표시, 1 방 이름, 2 잠긴 문·열쇠, 3 핵심 아이템, 4 문서·지도,
  5 퍼즐, 6 이벤트(스포일러), 7 일반 아이템, 8 적, 9 표시 범위(방문한 방 → 공개된 방 → 모든 방),
  \(₩) 한국어 / English.
- 이름 크기: - · + (숫자패드 포함), 불투명도: [ · ]
- 아이콘 크기: Shift + - · +, 불투명도: Shift + [ · ] (INI의 Modifier=Ctrl이면 Ctrl)
- 아이템 이름: H (모두 → 일반 아이템 제외 → 끔, 처음에는 끔). 범례 접기: ~
- 크림슨 헤드 부활까지 남은 시간: 적 표시 중 8번을 길게 눌러 켜고 끕니다.
- 지도 2배 확대: 공격 버튼. 확대 중에는 방향 입력으로 지도를 옮기며, 지도를 다시 열면 1배로 돌아옵니다.
- 기본값: 영어, 이름 100%, 불투명도 70%, 아이콘 100%, 아이콘 불투명도 80%, 방문한 방만 표시, 방 이름만 켬.
- 무기는 핵심 아이템으로, 잠긴 문의 열쇠는 문 가운데에 표시합니다(INI의 DoorKey=Unvisited이면 아직 가 보지 않은 쪽 방).
- 설정은 scripts/RE1HD.AnnotatedMap.ini에 저장됩니다. [Colors]에서 분류별 색을 #RRGGBB로 바꿀 수 있습니다(저장해도 그대로 남습니다).

제거
scripts의 RE1HD.AnnotatedMap으로 시작하는 파일을 지웁니다. 다른 ASI 모드가 없으면 dinput8.dll도 지웁니다.
EXE와 세이브는 수정하지 않습니다. 지원 대상이 아닌 실행 파일에서는 아무것도 패치하지 않고 로그만 남깁니다.

제작: 커트씨. 비공식 팬 모드입니다. Capcom과 관련이 없으며 게임 파일을 포함하지 않습니다.
소스 라이선스는 LICENSE.txt(MIT), 참고 자료와 글꼴 출처는 NOTICE.md에 있습니다.
https://github.com/eggu/resident-evil-hd-annotated-map

================================================================
English
================================================================

Supported: Resident Evil / Biohazard HD REMASTER on Steam or GOG (bhd.exe) + Ultimate ASI Loader (included).
This is not for the 1996 original.
Shows room names, locked doors and required keys, key items, files and maps, puzzles and events,
common items, typewriters and item boxes, and enemies on the game's map.

Installation
1. Close the game.
2. Copy the ZIP contents into the folder containing bhd.exe, keeping the folder structure
   (dinput8.dll, scripts/RE1HD.AnnotatedMap.asi and scripts/RE1HD.AnnotatedMap.ini).
   If you already have a dinput8.dll, for example from Fusion Fix, skip it and copy scripts only.
3. Launch the game and open the map.
When upgrading, skip scripts/RE1HD.AnnotatedMap.ini or back it up and restore it.

Controls (on the map screen only)
- Number keys: 0 all annotations, 1 room names, 2 doors/keys, 3 key items, 4 files/maps,
  5 puzzles, 6 events (spoilers), 7 common items, 8 enemies, 9 scope (visited -> revealed -> all rooms),
  \ (won sign on Korean keyboards) Korean / English.
- Name size: - · + (numpad too). Opacity: [ · ]
- Icon size: Shift + - · +. Icon opacity: Shift + [ · ] (Ctrl with Modifier=Ctrl in the INI).
- Item names: H (all → all except common items → off; off at first). Fold the legend: ~
- Time left until a Crimson Head revives: hold 8 while enemies are on to switch it on or off.
- Map zoom 2x: Attack button. Use directions to move while zoomed. Reopening the map returns to 1x.
- Defaults: English, name size 100%, opacity 70%, icon size 100%, icon opacity 80%, visited rooms, room names only.
- Weapons are key items, and a locked door's key is shown on the door (with DoorKey=Unvisited in the INI, in the room not visited yet).
- Settings are saved in scripts/RE1HD.AnnotatedMap.ini. [Colors] sets a colour per category as #RRGGBB (saving keeps it).

Uninstall
Delete the files in scripts that start with RE1HD.AnnotatedMap. If you have no other ASI mods, delete dinput8.dll too.
The EXE and saves are not modified. On an unsupported executable nothing is patched and only a log is written.

Created by 커트씨. Unofficial fan mod, not affiliated with Capcom. No game files are included.
Source license: LICENSE.txt (MIT). References and font credits: NOTICE.md.
https://github.com/eggu/resident-evil-hd-annotated-map
