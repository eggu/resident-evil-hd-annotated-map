# Changelog

## 1.0.3

- Supports the earlier bhd.exe build that many players roll back to (the version before the 2026 Steam update), as well as the current one. On it the map previously showed nothing ("bhd.exe layout mismatch" in the log).
- The log now names the detected bhd.exe build. Any other build is left untouched and logged as unsupported.

- 많은 사용자가 롤백해서 쓰는 이전 bhd.exe 빌드(2026 Steam 업데이트 이전 버전)를 현재 빌드와 함께 지원합니다. 이전에는 이 빌드에서 지도에 아무것도 표시되지 않았습니다(로그에 "bhd.exe layout mismatch").
- 인식한 bhd.exe 빌드를 로그에 남깁니다. 그 밖의 빌드는 건드리지 않고 지원하지 않는 빌드로 기록합니다.

## 1.0.2

- Fixed the map annotations not appearing for some players: the Direct3D device is now recognised even when another overlay or mod has hooked part of it.
- The log now records which module the Direct3D device comes from, to help diagnose setups where the map still shows nothing.

- 일부 환경에서 지도 표시가 나오지 않던 문제 수정: 다른 오버레이나 모드가 Direct3D 장치 일부를 후킹해도 인식합니다.
- 그래도 지도에 아무것도 나오지 않는 환경을 진단할 수 있도록 Direct3D 장치가 어느 모듈에서 오는지 로그에 남깁니다.

## 1.0.1

- Fewer antivirus false positives: the mod file now carries version information and no debug data. No gameplay changes.

- 백신 오탐 감소: 모드 파일에 버전 정보를 넣고 디버그 정보를 뺐습니다. 게임 내 동작은 바뀌지 않았습니다.

## 1.0.0

First public release.

- Room names, locked doors and keys, key items, files and maps, puzzles, events, common items, typewriters and item boxes, and enemies on the game's map; items, doors, puzzles and enemies disappear as you progress.
- Events (spoiler story scenes) as a purple `?`, hidden at first.
- Visited / revealed / all rooms scope, English and Korean, name and icon size and opacity, item names, per-category colours in the INI.
- 2x map zoom with panning.
- Includes Ultimate ASI Loader as `dinput8.dll`.

- 게임 지도에 방 이름, 잠긴 문과 열쇠, 핵심 아이템, 문서·지도, 퍼즐, 이벤트, 일반 아이템, 타자기·아이템 상자, 적을 표시하며, 아이템·문·퍼즐·적은 진행에 따라 사라집니다.
- 이벤트(스포일러가 되는 이야기 장면)는 보라색 `?`로 표시하며 처음에는 숨겨져 있습니다.
- 방문한 방/공개된 방/모든 방 범위, 한국어·영어, 이름·아이콘 크기와 불투명도, 아이템 이름, INI의 분류별 색.
- 지도 2배 확대와 이동.
- Ultimate ASI Loader를 `dinput8.dll`로 포함.
