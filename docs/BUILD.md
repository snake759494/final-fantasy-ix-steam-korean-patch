# 재빌드 절차

필요: Python 3.13 (UnityPy 1.22, fontTools, Pillow, numpy, scipy, etcpak), .NET 6 SDK, xdelta 3.1.0, 서울한강체·나눔스퀘어네오 글꼴(게임 폴더에 둠).

작업 폴더는 게임 폴더 아래 `_kor_work` 를 가정합니다 (`tools/` 내용을 그 안에 복사).

1. 원본 백업: 게임 폴더의 `_original_backup/{x64,x86}/FF9_Data/` 에 `resources.assets`, `sharedassets2.assets`, `Managed/Assembly-CSharp.dll` 원본을 둡니다 (`build.py` 는 처음 실행 시 자동 백업).
2. 원본 텍스트 추출 후 `python segment.py` → `bodies.json`, `segfiles.json` (영어 원문, 배포하지 않음).
3. 번역 결과를 `trans/out/*.json` (`{"id": "한국어"}`), 메뉴·경고문을 `trans/extra/` 아래 원래 경로로, 엔딩 자막 번역을 `trans/image_text.json` 에 둡니다. `python check.py <청크>` 로 태그·줄 수 검사.
4. 원본 글꼴 `font/TBUDGoStd-Bold.otf` 를 번들에서 꺼낸 뒤:
   ```
   python mergefont.py ../SeoulHangangEB.ttf 8
   python buildfont.py
   ```
5. `python build.py all` → x64·x86 의 `resources.assets`, `sharedassets2.assets` 생성.
6. DLL: `tools/dllpatch` 에서
   ```
   dotnet run -- <원본 Assembly-CSharp.dll> <출력.dll> <게임의 Managed 폴더>
   ```
7. xdelta 생성: `xdelta.exe -e -9 -f -s <원본> <결과> <x64_파일명.xdelta>`
8. 설치 프로그램: `tools/patcher` 의 해시 표를 갱신하고
   ```
   dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:PublishTrimmed=true -o out
   ```
