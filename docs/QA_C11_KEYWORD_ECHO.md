# c11 1장 키워드 본문 강조 검수

2026-11-13. 대상: `feat/selective-body-emphasis` / `yeonyeon-preview-pr17`만. 시작 커밋 `0140306`.

- 인물별 소제목 아래 명식별 키워드 두 개를 그대로 유지하고, 각각 원작 행동 뒤 닮은 이유 문장에서 같은 표현으로 한 번씩 강조했다. 기존 문장을 다듬어 연결했으며 별도 반복 문단을 추가하지 않았다.
- c11 roles의 명시된 키워드만 재강조를 허용했다. c06 및 다른 유형의 강조 규칙은 동일하다. 문단당 강조 최대 두 곳 유지.
- A/B에서 키워드별 본문 등장·strong 횟수와 위치, 개인화 차이 검증. 시작 커밋 대비 c11 roles 외 전체 응답·무료 응답 동일성 검증. 기존 다른 11종 전체 리포트 보존 검사 통과.
- 전체 unittest 62개 통과(기본 test_v67.py 5개 포함). 최초 제한 환경에서는 HTTP 소켓 연결이 차단되어 실패했고 연결 가능한 환경에서 전체 재실행해 통과했다.
- 로컬 c11 A/B × 360·390·1440px × 3장 = 18개 화면 통과. API/DOM 동일, 각 인물 본문에 동일 키워드 strong 한 번씩, 실제 굵기, 점수 비노출·넘침·페이지 오류 없음. 실제 입력→무료→언락·모달 키보드/닫기/초점 복귀·카드 다운로드 각 6회. 다른 11종 표시 호환성 통과. [결과](qa-c11-keyword-echo-local.json).
- 모바일 B 1장 캡처를 직접 열어 키워드 문맥·강조·줄바꿈 확인. 기존 레이아웃 전환 검사 통과.
- 운영 main 시작 SHA `9a8e43dca8ac6399058e71b0710ab24f78d53e1e`. 운영 Render `srv-dbmu4pijnfac73bfmqq0` 시작 updatedAt `2026-11-09T10:16:50.59908Z`. 운영 쓰기 없음.
- 실제 휴대전화·Safari·화면낭독기는 미검증.

## 배포

- 실행 커밋 `87d58d2649a72dfea3ff4be9fa026297a23f1cf2`, 배포 `dep-dbra0f61egvs73fiq670`, **live**. 완료 2026-11-13 14:30:12 KST. 지정 브랜치 자동 배포만 사용.
- 로컬 c06 A/B × 390·1440px × 5장 = 20개 화면, match/unlock 전체 응답 기존 fixture와 동일, 일반 입력·무료·언락·카드 검증 통과. [결과](qa-c06-keyword-echo-local.json).
- 배포 후 운영 Render updatedAt 동일. 미리보기 앱 로그에서 `Unhandled match error` 없음.

## 원격 재검증 완료

- c11 A/B × 360·390·1440px × 3장 = 18개 화면 통과.각 인물의 두 키워드가 본문에 정확히 한 번씩 strong으로 재등장하며 API/DOM 일치·실제 굵기·절제된 강조·점수 비노출·넘침 없음 확인. 실제 입력→무료→언락, 모달 키보드·닫기·초점 복귀, 카드 다운로드 각 6회, 다른 11종 표시 호환성 및 health 200 통과. [원격 c11](qa-c11-keyword-echo-remote.json).
- c06 A/B × 390·1440px × 5장 = 20개 화면 및 기존 fixture와 match/unlock 전체 응답 동일, 일반 입력·무료·언락·카드 검증 통과. [원격 c06](qa-c06-keyword-echo-remote.json).
- 원격 모바일 B 1장 캡처를 직접 열어 확인했다. 페이지 오류 없음.
- 원격 운영 main SHA가 시작과 동일하다. 운영 main·Render 변경 없음.
- [A 보기](https://yeonyeon-preview-pr17.onrender.com/?sample=c11-A) · [B 보기](https://yeonyeon-preview-pr17.onrender.com/?sample=c11-B).

최종 검수 기록은 `[skip render]` 문서 커밋으로 저장한다.
