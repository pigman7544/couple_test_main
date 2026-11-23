# 연연 GPT 실시간 집필 실험

기존 비교 화면은 고정 명식의 기준 원고와 목업을 표시합니다. 관리자 화면 `/rs-gpt/admin`에서는 양력 생년월일과 선택 출생시간을 받아 GPT-6.2 Sol에 한 번 요청합니다. 결과에 1~3장 전문, 문단별 근거 ID, 응답 모델, 토큰, 지연과 표준 요율 기준 비용 추정치를 표시합니다. 공급자의 캐시 기록 요금 등 별도 항목으로 인해 실제 청구액이 달라질 수 있습니다.

**고정 검토 명식 입력**은 첫째 남성 1992-03-18, 둘째 여성 1992-04-30, 출생시간 모두 미상을 사용합니다. 첫째 일지 巳의 본기 丙은 둘째 일간 丙과, 둘째 일지 子의 본기 癸는 첫째 일간 癸와 일치합니다. 서버는 기존 엔진이 확정한 명식·명리 근거만 전달하고 원래 생년월일과 출생시간은 요청에서 제외합니다. 미확정 시주와 절기 경계의 미확정 기둥은 보류합니다.

## 호출 보호

관리자 토큰은 32자 이상이며 OpenAI 키와 별개입니다. 브라우저는 관리자 토큰을 현재 페이지 메모리에서만 사용합니다. OpenAI 키는 서버 환경 변수로만 전달합니다. 익명 요청과 기존 공개 비교 화면을 통한 실호출을 차단합니다.

UTC 달 기준 3회, 한 번에 1개, 시작 간격 최소 5분, 요청 본문 최대 32 KiB, 모델 출력 최대 5,500토큰입니다. 모델 요청 전에 영속 원장에 예약을 확정합니다. 실패하거나 응답을 받지 못한 호출도 예약에 포함됩니다. 월간 예약 예산은 7달러이며 현재 설정의 회당 보수적 예약액은 0.343달러입니다. 영속 원장을 열 수 없으면 호출을 차단합니다.

## 구매 없이 내 PC에서 실행

Python 3.11 환경에서 프로젝트 폴더를 열어 의존성을 설치합니다. 원장은 OneDrive 동기화 폴더 밖의 로컬 디스크에 두고 최초 한 번 초기화합니다.

```powershell
python -m pip install -r requirements.txt
$env:RS_GPT_LOCAL_LEDGER = Join-Path $env:LOCALAPPDATA "yeonyeon-rs-gpt.sqlite"
python rs_gpt_server.py --init-ledger $env:RS_GPT_LOCAL_LEDGER
$env:OPENAI_API_KEY = Read-Host "OpenAI API 키" -MaskInput
$env:RS_GPT_ADMIN_TOKEN = Read-Host "32자 이상의 임의 관리자 토큰" -MaskInput
$env:RS_GPT_LIVE = "1"
python rs_gpt_server.py
```

위 비밀값 입력 명령은 PowerShell 7.2 이상을 사용합니다. 두 번째 실행부터는 같은 원장 경로를 지정하고 초기화 명령을 생략합니다. 브라우저에서 http://127.0.0.1:8766/rs-gpt/admin 을 열고, 같은 관리자 토큰으로 인증한 다음 **고정 검토 명식 입력** 또는 직접 입력 후 **리포트 생성**을 누릅니다.

## Render

실험 서비스 `srv-dc23purl550s7381llg0`에만 연결합니다. 무료 Render 웹 서비스의 로컬 파일은 재시작과 배포 후 보존되지 않으므로 SQLite 방식은 내 PC의 주소에서만 허용합니다. Render 실시간 집필을 사용하려면 이미 확보한 영속 PostgreSQL 원장의 연결 문자열을 `RS_GPT_BUDGET_DSN`으로, 별도 관리자 토큰과 API 키를 각각 `RS_GPT_ADMIN_TOKEN`, `OPENAI_API_KEY`로 등록하고 `RS_GPT_LIVE=1`을 설정합니다. 원장이 준비될 때까지 실시간 호출을 차단합니다.

```sh
python -m unittest test_v67 test_compatibility_v14 test_rs_preview test_rs_gpt
```

