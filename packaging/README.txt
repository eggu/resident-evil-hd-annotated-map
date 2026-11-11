RE1 HD Annotated Map - Survivor's Notes - Resident Evil HD REMASTER
상세 지도: 생존자의 메모 / 详细地图：幸存者笔记

================================================================
简体中文
================================================================

支持：Steam·GOG 版 Resident Evil / Biohazard HD REMASTER（bhd.exe）+ Ultimate ASI Loader（已附带）。
不适用于 1996 年原版。
在游戏地图上标注房间名称、上锁的门与所需钥匙、关键物品、文件·地图、谜题·事件、普通物品、打字机·物品箱和敌人。
支持英语、韩语和简体中文。物品、钥匙、文件与地点名称与常用的“扑家汉化”补丁一致。

安装
1. 关闭游戏。
2. 将 ZIP 内容按原有目录结构复制到 bhd.exe 所在的游戏文件夹
   （dinput8.dll、scripts/RE1HD.AnnotatedMap.asi、scripts/RE1HD.AnnotatedMap.ini）。
   如果已有 dinput8.dll（例如 Fusion Fix 的），请跳过 dinput8.dll，只复制 scripts。
3. 启动游戏并打开地图。
首次运行为英语：在地图画面按 \ 切换到简体中文（设置会自动保存），或把 INI 中的 Language 改为 zh。

操作（仅在地图画面有效）
- 数字键：0 全部标注开关，1 房间名称，2 上锁的门·钥匙，3 关键物品，4 文件·地图，
  5 谜题，6 事件（剧透），7 普通物品，8 敌人，9 显示范围（已访问 → 已揭示 → 全部房间），
  \（韩文键盘上为 ₩）切换语言：English → 한국어 → 简体中文。
- 名称大小：- · +（含小键盘），名称不透明度：[ · ]
- 图标大小：Shift + - · +，图标不透明度：Shift + [ · ]（INI 中 Modifier=Ctrl 时为 Ctrl）
- 物品名称：H（全部 → 不含普通物品 → 关，初始为关）。折叠图例：~
- 赤红头复活剩余时间：显示敌人时长按 8 开关（单位显示为 m，即分钟）。
- 地图放大 2 倍：攻击键。放大时用方向键移动地图，重新打开地图恢复 1 倍。
- 设置保存在 scripts/RE1HD.AnnotatedMap.ini；[Colors] 可用 #RRGGBB 修改各分类颜色。

卸载
删除 scripts 中以 RE1HD.AnnotatedMap 开头的文件。如果没有其他 ASI 模组，也删除 dinput8.dll。
不修改 EXE 和存档。

原作者：커트씨。非官方粉丝模组，与 Capcom 无关，不含游戏文件。
中文字体：思源黑体（Source Han Sans SC，Adobe，SIL OFL 1.1），以位图形式嵌入。
源代码许可：LICENSE.txt（MIT）；参考资料与字体出处：NOTICE.md。

================================================================
한국어
================================================================

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
  \(₩) 언어 전환: English → 한국어 → 简体中文.
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
  \ (won sign on Korean keyboards) language: English -> Korean -> Simplified Chinese.
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
