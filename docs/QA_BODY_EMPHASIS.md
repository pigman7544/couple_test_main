# 본문 핵심 구절 강조 복원

PR17 `3ecf4ed` 위의 후속 수정. 제목만 남던 일괄 제거 후처리를 편집자가 고른 문자 그대로의 구절 목록으로 교체했다. 문장 위치·첫 문장 추출·사주 용어 탐지로 강조하지 않는다. 유형별 관계 메시지와 공통 해설·개인화 문구를 골라 단락당 최대 한 구절을 강조한다. 나머지 단락은 그대로 읽히도록 남긴다. 사주 글자 대신 바라는 배려를 강조하는 인물 소개도 포함한다.

예: c06 `일상의 약속을 통해`, `듣고 싶은 말과 건네는 말`, `다시 이야기할 시간을`; c11 `잘못 알았던 부분을 인정`; c18 `지금 서로가 원하는 삶`; f03 `스스로 다시 선택하는 과정`. 강조 표시를 제외한 모든 문자는 유지한다.

## 보존 검증

- Python 전체 41개 통과. 기본 `test_v67` 포함. [실행 로그](../tests/emphasis-test-log.txt).
- 12종 × 원점수 30/55/75에서 모든 문자열의 강조 제거 후 완전 일치 및 나머지 필드 완전 일치, 결정론, 단락당 강조 0~1개, 문장·문단 전체 강조 없음, 사주 기호 강조 없음 검사.
- PR16 대비 원전·장 구조·점수 해설 보존 검사는 강조 표시를 제외하고 비교한다. 기존 원전/장면 보호 검사는 원문을 유지하고 표시만 무시하도록 수정했다. 보호 fixture 및 c01/c06 원전 모듈 수정 없음.
- `engine.py`, `matcher.py`, `relationship_v08.py`, `couples.json`, `narrative.py`, `c01_report.py`, `c06_report.py`, `other_reports.py`, `reading_voice.py`, `personalized_reading.py`, `editorial_readings.py`, `individual_scenes.py`, `report_display.py`, `index.html`은 PR17 기준 변경 없음.
- 테스트가 저장하는 [전후 본문](qa-emphasis-examples.json) 및 [전체 렌더 입력](../tests/browser-reports.json) 제공.

## 실제 Chrome 화면 QA

- 12종 × 360/390/1440px = 36개 실제 렌더. 각 5장, 정수 6축, 가로 넘침 및 페이지 오류 없음.
- 제목 목록이 원본 제목 한 줄과 정확히 일치: `.subhead` 본문 전체 포장 버그 재발 방지. `**핵심 구절**` → `<strong>` 변환 및 HTML 이스케이프 검사.
- 각 장에 본문 강조 존재, 본문 기본 굵기 400 / 소제목 750 분리 확인. 전체 리포트 본문 강조 구절 30~36개, 장별 본문 문자 대비 강조 비율 약 2.7~20.0%. 비율은 합격 목표가 아닌 관찰값이다. 원전 서사·설명 주석이 긴 장은 낮으며 조언은 높다. 모든 문단에 같은 밀도를 강요하지 않는다.
- 390px의 12종 × 5장 전체 캡처 60개: `tests/qa-emphasis-<id>-390-ch<1~5>.png`. 장 상단 60개를 모은 [1](../tests/qa-emphasis-sheet-1.png), [2](../tests/qa-emphasis-sheet-2.png), [3](../tests/qa-emphasis-sheet-3.png), [4](../tests/qa-emphasis-sheet-4.png)를 육안 검수했다. 제목 줄바꿈과 본문 강조가 분리되며 긴 본문 전체가 굵어지지 않는다. 전체 하단은 캡처와 DOM 검사로 보완했다. 실제 모바일 기기 테스트를 의미하지 않는다.
- c06 실제 입력 → 무료 미리보기 → 테스트 언락 → 카드 → 다시 입력 흐름 확인. `node tests/test_c06_layout.cjs` 반복 유형 전환 검사 통과.
- [화면별 강조 목록·밀도·검사 결과](qa-emphasis-browser.json).

## 프리뷰와 언락

지정 프리뷰만 배포 대상으로 사용한다: https://yeonyeon-preview-pr17.onrender.com/ . 운영 서비스 변경 및 PR 병합 없음.

기존 프리뷰 3ecf4ed에서 기본 가상 입력의 언락 10회가 모두 200 / c06 5장으로 응답했다. 오류는 이번 조사에서 재현되지 않아 해결했다고 주장하지 않는다. 프런트의 JSON 선파싱 및 호스팅 재기동 가능성은 원인이 아닌 조사 후보다. [별도 이슈 #18](https://github.com/pigman7544/couple_test_main/issues/18)에 근거와 후속 진단 항목을 기록했다. [요청 로그](qa-emphasis-preview-unlock.json).

## 재현

```text
python -X utf8 -m unittest discover
python -X utf8 tests/export_browser_reports.py
python -X utf8 server.py
node tests/qa_emphasis_browser.cjs
node tests/test_c06_layout.cjs
python -X utf8 tests/emphasis_contact_sheet.py
python -X utf8 tests/check_preview_unlock.py
```

서버와 브라우저는 별도 프로세스에서 실행한다. 로컬 실행 환경의 `PLAYWRIGHT_MODULE`, `BROWSER_PATH`를 지정할 수 있다. 12종은 기존 가상 입력에 유형을 고정한 실제 렌더 검사이며 같은 입력으로 모든 유형이 자동 선택된다는 뜻은 아니다. 최초 제한 환경에서 HTTP 연결 차단이 있었고, 연결 가능한 환경에서 41개 전체 검사를 재실행했다.
