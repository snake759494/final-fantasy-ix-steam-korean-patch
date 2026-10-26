# 파이널 판타지 IX (Steam) 한글패치

Steam PC판 **FINAL FANTASY IX (AppID 377840)** 용 비공식 한국어 패치입니다. 대사·메뉴·아이템·어빌리티·지명·몬스터·전투 메시지·시스템 문구 전체와 타이틀·메뉴·엔딩 자막의 글자 그림을 한국어로 바꿨습니다. 현재 배포판은 **v1.0.1 (2026-10-26)** 입니다.

[패치 다운로드](https://github.com/snake759494/final-fantasy-ix-steam-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 **FF9_Steam_KO_v1.0.1.zip 하나**입니다. zip 안에는 설치 프로그램(`FF9_KorPatcher.exe`), `xdelta.exe`, 원본 게임 파일이 있어야만 쓸 수 있는 차분 파일(xdelta) 6개가 들어 있습니다. 저장소에는 제작 도구와 기술 문서만 공개합니다. 원본 및 패치된 게임 파일, 글꼴 파일, 영어 원문, 번역 대본은 포함하지 않습니다. GitHub 가 자동 생성하는 Source code ZIP/TAR 는 저장소 소스의 압축본이며 게임 파일이 아닙니다.

## 대상 버전

이 패치는 **Steam 판 FINAL FANTASY IX (빌드 5378074)** 의 x64·x86 데이터에 적용합니다. Memoria 등 다른 모드가 설치된 파일에는 적용할 수 없습니다.

| 파일 | 원본 크기 | 원본 SHA-256 | 결과 SHA-256 |
| --- | --- | --- | --- |
| `x64/FF9_Data/resources.assets` | 590,057,040 | `4dbd0b3fe547406884d7d3a79471c5fc7c34756940ede1515c6afe4de116532d` | `7c563f87ad5f9dca4039b53215f49a7fdccabed33f963de62a6e20b70402fd40` |
| `x64/FF9_Data/sharedassets2.assets` | 198,981,708 | `5fbfd206b0f358542c887410d695d161a66c5ea9e3e0cf7f57742aab5433d666` | `d949836a3b5cd5edfbc1ceed9f8bdbd223fa7e399ee0e801dd5dab092ee0704a` |
| `x64/FF9_Data/Managed/Assembly-CSharp.dll` | 4,036,608 | `2fd5a4b7300a2806b875a9913e9001ed970c2ce4e449938a00d142fd1339b8d2` | `c4b2cea3d99fd42c42e320b353b940a3d85f8be02a7952646703aaa7981b6c81` |
| `x86/FF9_Data/resources.assets` | 590,057,040 | `725f6f1ca9d026370b6553a8c817c725090adceeba2080d4f639e374287846b6` | `932bf0f1b20ccee4255d6b14299fbbe135cc3e1d0f441948b4513c176c47ae38` |
| `x86/FF9_Data/sharedassets2.assets` | 198,981,708 | `94c59ab70de49b6595b8e5c6493a3ec0c98d42a85494976ddbdc9c6c3a2c8d7f` | `e46c417f055216a1d442e86c8c720ad9dd8bc349f6b65c41e4afa0339b2863f5` |
| `x86/FF9_Data/Managed/Assembly-CSharp.dll` | 4,036,608 | `55fbcaa4e74ac3456d517b816050c3e63a7cddcac033dadeae17b9af0daec557` | `f24e4a449007781245e7a13336746eebfdde0a6bcdda35c9782ec0249e42b170` |

| 항목 | 값 |
| --- | --- |
| 첨부 파일 | `FF9_Steam_KO_v1.0.1.zip` (17,310,708 바이트) |
| zip SHA-256 | `129f407f91c6f1152c847f7a26a6f0df34ffa1a3351307efe2c6a05e43a4dc98` |

xdelta 파일별 크기·해시는 [release_manifest.json](release_manifest.json) 에 있습니다.

## 패치 적용 방법

### 설치 프로그램 사용 (권장)

1. 게임을 종료합니다.
2. 릴리즈에서 `FF9_Steam_KO_v1.0.1.zip` 을 받아 아무 폴더에 압축을 풉니다.
3. `FF9_KorPatcher.exe` 를 실행하고 `1) 한글패치 설치` 를 고릅니다.
   - Steam 레지스트리와 `libraryfolders.vdf` 에서 FF9 설치 폴더를 자동으로 찾습니다. 못 찾으면 경로를 직접 입력받습니다.
   - 대상 파일 6개의 MD5 를 먼저 모두 확인하고, 하나라도 버전이 다르면 아무 파일도 바꾸지 않습니다. 이전 버전 패치가 적용된 파일은 원본 백업에서 다시 패치합니다.
   - 원본은 게임 폴더의 `_original_backup` 에 백업하고, 임시 파일에 패치한 뒤 결과 해시가 맞을 때만 교체합니다.
4. 게임을 실행해 언어 설정에서 **한국어** (기존 English (US) 자리)를 고릅니다.

원래대로 되돌리려면 `FF9_KorPatcher.exe` 에서 `2) 원본으로 복원` 을 고르거나, Steam 의 **게임 파일 무결성 확인** 을 쓰면 됩니다.

명령줄 옵션: `-y` (묻지 않고 설치), `-restore` (묻지 않고 복원), 첫 인자로 게임 폴더 경로 지정.

### xdelta 수동 적용

```powershell
.\xdelta.exe -d -s '원본\x64\FF9_Data\resources.assets' '.\patch\x64_resources.assets.xdelta' '.\resources.assets'
```

6개 파일 모두 같은 방식으로 적용한 뒤 결과 해시를 위 표와 비교하세요.

## 한글화 범위

- 텍스트 파일 650개, 고유 문자열 16,863개 (약 103만 자): 대사 전체, 아이템·장비·중요 아이템 이름과 설명, 어빌리티·명령어, 지명 389개, 몬스터·적 기술 이름과 전투 메시지, 메뉴·옵션·도움말 문자열(Localization), 시작 시 건강 경고문
- 한글 글꼴: 원본 글꼴 TBUDGoStd-Bold 에 서울한강체 EB 의 한글 11,172자와 자모를 합쳐 넣음 (영문·숫자는 원본 글꼴 유지)
- 대화창 폭: 원문의 창 폭 값(`[STRT=폭,줄수]`)을 글꼴 너비로 역산해 한글 길이에 맞게 다시 계산
- 글자 그림: 타이틀 메뉴(이어하기·새로 시작·불러오기·클라우드 데이터), 언어 선택 "한국어", 돌아가기·정보·일시정지·레벨 업·이름 표제, 언어 선택·무비 갤러리 제목, 독·석화·도움말·ATE 안내, 튜토리얼 안내, 엔딩 자막 8장, 타이틀 문구, "안개 대륙" 지역명
- 이름 입력: 기본 이름을 한글(지탄·비비·대거·스타이너 등)로 바꾸고, 이름 입력에서 한글을 쓸 수 있게 함

## 알려진 한계

- 한국어는 English (US) 언어 자리에 들어갑니다. 여러 언어가 함께 쓰는 일부 글자 그림(일시정지·레벨 업 등)은 English (UK)·일본어 등에서도 한글로 보입니다.
- 대화창 폭과 줄바꿈은 계산으로 맞췄기 때문에 일부 창에서 여백이 넓거나 좁을 수 있습니다.
- 바꿀 수 있는 캐릭터 이름 뒤의 조사는 받침을 알 수 없어 `을(를)` 형식으로 썼습니다.
- 타이틀 로고, 스태프롤, 동영상 속 글자, 모바일판 전용 그림, 테트라 마스터 카드 글자 그림은 원본 그대로입니다.
- Steam 업데이트나 무결성 확인을 하면 패치가 풀립니다. 다시 설치하세요.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `tools/segment.py` | 텍스트 파일을 번역 단위로 나누고 중복 제거 |
| `tools/build.py` | 번역 적용, 창 폭 재계산, 글꼴 번들 암호화·삽입, 에셋 재저장 |
| `tools/images.py` | NGUI 아틀라스 스프라이트 좌표 기준 글자 그림 재작성 |
| `tools/mergefont.py`, `tools/buildfont.py` | 한글 글리프 병합, 글꼴 에셋번들 재생성 |
| `tools/check.py` | 번역 태그·줄 수·줄 길이 검사 |
| `tools/dllpatch/` | Assembly-CSharp.dll 패치(기본 이름, 한글 입력 허용, Mono.Cecil) |
| `tools/patcher/` | 설치 프로그램 소스 (C#, .NET 6) |
| `tools/gamectl.ps1` | 검증용 게임 실행·창 캡처 보조 스크립트 |
| `tools/data/` | 리소스 경로 표, 아틀라스 스프라이트 좌표 |
| `docs/TECHNICAL.md` | 데이터 형식과 한글화 방식 |
| `docs/BUILD.md` | 재빌드 절차 |
| `docs/TRANSLATION_RULES.md`, `docs/glossary.json` | 번역 규칙과 핵심 용어집 |
| `docs/FONT_CREDITS.md` | 글꼴 출처 |
