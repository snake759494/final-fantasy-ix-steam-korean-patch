# 기술 설명

## 게임 구조

- 엔진: Unity 5.2.3p2, NGUI. 텍스트·UI 에셋은 `FF9_Data/resources.assets`, UI 아틀라스는 `sharedassets2.assets`.
- 리소스 경로는 `mainData` 의 ResourceManager 컨테이너에 있음 (`tools/data/container.json`, 파일 인덱스 5 = resources.assets).
- 텍스트: `EmbeddedAsset/Text/{US,UK,JP,GR,FR,IT,ES}/{field,battle,item,keyitem,ability,command,etc,location,title}/*.mes` TextAsset. 한국어는 US 자리에 넣음.
- 메뉴 문자열: `EmbeddedAsset/Manifest/Text/Localization.txt` (CSV, KEY + 7개 언어 열). US 열만 교체하고 `Name` 행을 "한국어"로.

## .mes 형식

- 항목은 `[ENDN]` 으로 구분. 대화 항목은 `[STRT=폭,줄수]` 로 시작하고 `[TAIL=..]`, `[IMME]`, 색상(`[C8B040][HSHD]`), 이름(`[ZDNE]` 등), 변수(`[ITEM=n]`, `[NUMB=n]`), 선택지(`[CHOO]`, `[MOVE=..]`, `[XTAB=..]`) 태그를 씀.
- `segment.py` 는 각 항목을 (앞쪽 태그·공백, 본문, 뒤쪽 태그·공백) 으로 나누고 본문만 번역 단위로 뽑아 중복을 제거 (16,863개).
- 같은 본문이 서로 다른 뜻으로 쓰이는 경우(예: 무기 Dagger / 별명 Dagger)는 `build.py` 의 `OVERRIDE` 로 파일별 예외 처리.

## 창 폭 재계산

`NGUIText` 는 `[STRT=w,l]` 의 w(+3)를 대화창 폭으로 그대로 씀. 영어 원문 2만여 항목의 최장 줄 너비(원본 글꼴 em 단위)와 w 를 회귀하면 `w ≈ 9.82 × em - 3` 이었으므로, 번역 후

```
w' = max(w + 9.82 × (em_ko - em_en) + 4, 9.82 × em_ko + 2)
l' = l + (번역 줄 수 - 원문 줄 수)
```

로 바꿈. 변수·이름 태그는 양쪽에 같은 자리표시 폭을 넣어 상쇄. 지명 파일처럼 w 가 너비와 무관한 고정값인 경우는 그대로 둠.

## 글꼴

- `EncryptFontManager` 가 `EmbeddedAsset/FA/p_fa.mpc` 를 `ByteEncryption.Decryption` (앞 1024 바이트를 파일 끝 1024 바이트와 맞바꾸는 방식)으로 풀어 AssetBundle(UnityWeb) 로 읽고 `TBUDGoStd-Bold` Font 를 씀.
- `mergefont.py`: 원본 TrueType(glyf) 글꼴에 서울한강체 EB 의 U+AC00–D7A3, U+3131–318E, U+1100–11FF 글리프를 복사(좌우 6유닛 여백, 기준선 +8유닛).
- `buildfont.py`: 번들의 Font `m_FontData` 교체 후 저장. `build.py` 가 다시 암호화해 TextAsset 에 넣음.

## 글자 그림

- `sharedassets2.assets` 의 UIAtlas MonoBehaviour 에서 UISpriteData(이름, x, y, w, h, 경계, 여백)를 읽어 좌표를 얻음 (`tools/data/atlases.json`, 상단 원점).
- `images.py`: 대상 스프라이트 영역을 투명하게 지우고 원본 스타일을 흉내 내어 다시 그림 (금색 그라데이션+외곽선=서울한강체 EB, 엔딩 자막 발광=서울한강체 M, 작은 표시=나눔스퀘어네오).
- 장식선이 있는 제목은 선을 새로 그려 글자 폭에 맞춤.

## DLL

- `FF9TextTool.CharacterDefaultName` 의 English(US) 배열 문자열 20개를 한글 이름으로 교체.
- `NameSettingUI.ValidateInput` 정규식 허용 범위에 `가-힣ㄱ-ㆎᄀ-ᇿ` 와 공백 추가. NGUI `UIInput` 은 선택 시 이미 `IMECompositionMode.On` 을 켬.

## 실행

런처(`FF9_Launcher.exe`)는 `.\x64\FF9.exe -runbylauncher -single-instance -screen-width W -screen-height H -screen-fullscreen 0|1` 로 실행함.
