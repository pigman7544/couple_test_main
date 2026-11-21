# 연연 B·C 후속 집필 실험

**하이브리드 설계는 다음 시제품의 편집 경로로 채택한다.** 검증 계산 → 관계 구조 종합 분석 → AI 집필 → 근거·표현 검수 순서다. 기존 B보다 C가 같은 계산에서 어떤 논지를 골랐고 어디서 멈췄는지 추적하기 쉽다. 생활 장면의 설득력은 표본마다 달랐다. 제품 채택은 독립 평가와 자동 집필 검증 후 결정한다.

- [관계 구조 종합 분석·고정 표본 03](synthesis.md)
- [B·C 전문 나란히 보기](comparison.md)
- [C01](01-C.md) · [C02](02-C.md) · [C04](04-C.md)
- [근거 ID 검토 기록](decisions.json) · [평가와 편집 검토](review.md)
- [이전 실험과 A·B 원고](../rs-ab-20261121/README.md) · [이전 근거표](../rs-ab-20261121/evidence-guide.md) · [독립 채점 루브릭](../rs-ab-20261121/rubric.md)

공식 「RS2 시제품 — 두 사람의 궁합」 전체 원문은 미확보 상태다. C는 확인 가능한 ‘명리 근거 → 전통 해석 → 가상 장면’ 흐름을 활용한 잠정 실험 원고다. 공식 RS 충실도는 채점 보류했다. 종합 분석은 수동으로 적용했으며, 검증 코드는 원장과 참조를 시험한다. 자동 집필 품질, 지연, 비용, 실패 시 처리, 공식 RS 적합도는 남은 검증 항목이다.

## 재현

저장소 루트, Python 3.11.9와 저장소의 기존 의존성에서 확인했다.

```sh
python docs/rs-synthesis-20261121/verify_experiment.py
python -m unittest test_compatibility_v14 test_compatibility_v13 test_compatibility_v12 test_compatibility_v11 test_v67
```

실험 검증 3건, 기존 로컬 회귀 25건 통과. 실험 검증은 01·02·04의 원장 전체(12+14+14 ID), B·C 문단의 ID 참조, 고정 03, 전문의 포함과 완전 동일 문장을 확인한다. 계산 주장의 의미 대조와 편집 평가는 수동 검토다. 역법 자체의 독립 감수 및 실제 운영 서버 확인은 이번 범위에 포함되지 않았다.

## 버전 영향과 복원

실험 기준은 이전 실험 브랜치의 `7f997f6a9f75cfc6365e7b74b83b28c3e10971dc`다. 기존 계산 기준은 PR #32의 `d08125d72d33a4440073c848a5dc598e25b0471d`다. 실험 자료를 되돌려 비교하려면 이전 실험 SHA를 열면 된다. 아래는 이전 실험에 기록된 제품 보존 지점이며, 영역별 공식 번호는 미확인 상태로 유지했다.

| 영역 | 버전 영향과 보존 지점 |
| --- | --- |
| UI | 변경 없음. 제품 기준 [bone1](https://github.com/pigman7544/couple_test_main/commit/860c11decd27dccb9fbf6c88edf6645246a41344) |
| PV | 변경 없음. 미리보기1 승인 원본 위치·대응 SHA 확인 필요. 미리보기2 로컬 PDF SHA-256 `50ee3c5895e1c24f6b2fc0f2e82c92a16ee371547e409d8540fb2fef2a5cceb4`. 승인·배포 연결 미확인 |
| IL | 변경 없음. 승인 IL1. 원본 PDF 위치와 대응 구현 SHA 확인 필요 |
| SA | 변경 없음. 제품 bone1, 본 실험 계산 [PR #32 기준](https://github.com/pigman7544/couple_test_main/commit/d08125d72d33a4440073c848a5dc598e25b0471d) |
| RS | 별도 실험 원고 C 3편. 공식 버전 변경 없음. 공식 RS 원문과 구현 SHA 확인 필요. 이전 실험 SHA에서 B 복원 |
| SYS | 변경 없음. bone1 및 종전 배포 기록 `dep-dc06o2om7kps73bi9gfg` |

[기준점 등록 PR #31](https://github.com/pigman7544/couple_test_main/pull/31) · [기존 엔진 PR #32](https://github.com/pigman7544/couple_test_main/pull/32)
