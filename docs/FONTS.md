# 웹폰트 출처와 검증

확인일: 2026-11-07. 기준 main: `e9c238f6c50607ea49e027517969122a3d0d12f7`.

## 적용과 배포

- h1/h2/h3, 챕터 라벨, 리포트 소제목: BM JUA 400.
- 본문, 설명, 입력, 선택, 버튼, 리포트 본문: NanumSquareRound. 공식 Regular/Bold/ExtraBold를 400/700/800–900에 대응한다. 중간 굵기는 CSS 표준의 가장 가까운 제공 굵기를 사용한다.
- 원본 파일을 변환·서브셋·수정하지 않고 `/assets/fonts/`에서 자체 제공한다. 외부 요청 없이 같은 출처에서 로딩하므로 외부 CDN 가용성이나 CORS에 의존하지 않는다.
- 모든 face에 `font-display:swap`. 실패 시 system-ui → Apple SD Gothic Neo → Malgun Gothic → sans-serif 순의 대체 글꼴을 사용한다. 제목은 NanumSquareRound도 먼저 대체 후보로 사용한다.
- 주아체 공식 TTF는 약 1.53 MB다. 변환에 따른 원본/예약 이름 문제를 피하기 위해 그대로 사용했다. 나눔스퀘어라운드 WOFF2 세 개는 총 약 0.71 MB다. 현재 서버의 기존 no-cache 정책은 유지했다.
- 서버는 폰트 4개와 라이선스 2개의 정확한 경로만 추가 허용한다. MIME은 `font/ttf`, `font/woff2`, 라이선스는 UTF-8 text/plain이다.

## 공식 제공처와 실제 다운로드 URL

### 배달의민족 주아체

- 소개/다운로드: https://www.woowahan.com/fonts
- 이용 조건 및 OFL 전문: https://www.woowahan.com/fonts/license
- 원본: https://woowahan-cdn.woowahan.com/static/fonts/BMJUA_ttf.ttf?7dbe95a7
- 공식 사이트의 Fonts 화면이 참조하는 다운로드 모듈에서 위 주소를 확인했다. 저장 이름은 `BMJUA.ttf`이며 바이너리는 그대로다.
- 저작권자: Woowa Brothers Corporation. SIL OFL 1.1. 상업적 사용·웹 임베딩·소프트웨어와 함께 재배포 가능. 글꼴 자체 단독 판매 금지, 저작권/라이선스 동봉, 수정본의 예약 이름 제한, 저작권자 보증/추천 오인 금지. 전문은 [OFL-BM-JUA.txt](../assets/fonts/OFL-BM-JUA.txt)에 포함한다.

### 나눔스퀘어라운드

- 공식 나눔글꼴 안내: https://hangeul.naver.com/2017/nanum
- 공식 웹폰트 CSS: https://hangeul.pstatic.net/hangeul_static/css/nanum-square-round.css
- Regular: https://hangeul.pstatic.net/hangeul_static/webfont/NanumSquareRound/NanumSquareRoundR.woff2
- Bold: https://hangeul.pstatic.net/hangeul_static/webfont/NanumSquareRound/NanumSquareRoundB.woff2
- ExtraBold: https://hangeul.pstatic.net/hangeul_static/webfont/NanumSquareRound/NanumSquareRoundEB.woff2
- 공식 라이선스: https://help.naver.com/service/30016/contents/18088?osType=PC&lang=ko
- 네이버/네이버 문화재단의 공식 안내에서 상업 사용 및 저작권 안내와 라이선스 전문을 동봉한 재배포를 허용한다. SIL OFL 1.1, 글꼴 자체 단독 판매 금지, 수정본 예약 이름 제한. 전문은 [OFL-NanumSquareRound.txt](../assets/fonts/OFL-NanumSquareRound.txt)에 포함한다.

공식 원본 URL 네 개의 다운로드가 성공했으며, 로컬 실제 Chromium에서 각 파일이 FontFace `loaded` 상태로 파싱·표시됨을 확인했다.

## 검증 결과

- `python -X utf8 -m unittest test_v67.py test_c06_report.py test_report_paths.py test_fonts.py`: 20개 통과. Windows 기본 cp949 대신 UTF-8 및 로컬 HTTP 연결 가능한 환경에서 실행했다.
- 기존 12개 유형의 시간 입력/미입력, 미리보기와 테스트 언락 HTTP 검사 통과. 다른 11개 전체 리포트는 기존 fixture와 정확히 일치한다.
- 기존 서버 전체 해시 보호는 새 정적 폰트 분기만 제거한 뒤 원래 CRLF 기준 해시를 비교한다. 나머지 서버 코드와 PNG/계산 파일/미리보기 fixture는 그대로 보호한다. 새 테스트는 실제 폰트·라이선스 HTTP 응답의 MIME과 원본 바이트, 미허용 경로 404를 확인한다.
- Chromium 151 모바일 에뮬레이션: 390×844, 360×844. c06 실제 기본 입력으로 입력 → 미리보기 → 테스트 언락 → 5장 리포트 → 마지막 장 스크롤 → 다시 입력을 확인했다.
- 같은 두 크기에서 `/assets/fonts/*` 요청을 강제로 차단했다. 모든 face가 `error`인 상태에서도 대체 글꼴로 동일한 흐름과 스크롤이 동작하고 가로 넘침이 없었다.
- c11 실제 입력(a: 1992-03-18 16:00, b: 1988-01-05 01:00, 양력)도 두 크기·정상/차단 조건에서 미리보기 → 언락 → 6장 → 마지막 장 → 다시 입력이 동작했다. c06는 5장, c11은 6장으로 표시되고 두 조건 모두 가로 넘침과 JavaScript 오류가 없었다.
- 폰트 정상/차단 조건 모두 입력/버튼 15px 유지, 리포트 일반 본문 16px 유지. 한글 표시·줄바꿈, 입력과 버튼, 리포트 시작/끝의 스크린샷을 시각 확인했다. 360px 기존 한 열 입력 배치를 유지한다.
- 한계: 실제 iOS/Android 기기와 Safari는 실행하지 않았다. main 병합·실서비스 배포는 하지 않았다.

## 변경 범위

화면 동작 변경은 글꼴 지정과 그에 필요한 표시용 구분뿐이다. 기존 renderProse가 소제목과 다음 본문을 한 span에 묶기 때문에, 첫 줄에 subhead-title span만 추가해 제목과 본문 글꼴을 구분했다. 텍스트·줄바꿈·강조·기존 크기와 여백은 유지한다. PNG 두 개·사주 계산·매칭·리포트 생성·5장/6장 구성·테스트 언락 정책은 수정하지 않았다. 그 외에는 폰트 정적 제공, 라이선스와 출처 기록, 보호 테스트 보완만 포함한다.
