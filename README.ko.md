# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**당신의 AI 코딩 도구가 보이지 않는 돈을 태우고 있습니다.**

메시지를 보낼 때마다 AI는 *전체* 대화 기록을 처음부터 다시 읽습니다. 50번째 메시지는 1번째 메시지의 50배 비용이 듭니다. AI가 "네, 이제 수정하겠습니다"라고 한 그 말? 돈만 들고 아무것도 안 했습니다. 500줄짜리 빌드 로그? 이후 모든 메시지에서 매번 다시 읽힙니다.

대부분의 바이브 코더는 모르는 사이에 AI 토큰 예산의 **50% 이상**을 낭비하고 있습니다.

vibecheck이 해결합니다. 최근 14일간의 세션을 스캔하고, 낭비가 정확히 어디서 발생하는지 찾아내고, 쉬운 말로 설명하고(전문 용어 없이 — 토큰이 뭔지부터 알려드립니다), 설정 파일에 한 문단만 추가하면 끝. 같은 작업, 절반의 비용.

**평균 절약: 토큰 비용의 50% 이상.** 모든 LLM 모델 지원. Claude Code, OpenClaw, Codex, OpenCode 등 24개 이상의 AI 코딩 도구와 호환. 100% 로컬 실행 — 데이터는 절대 외부로 전송되지 않습니다.

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## 개인정보 보호

**데이터는 절대 컴퓨터 밖으로 나가지 않습니다.** 서버 없음, API 없음, 텔레메트리 없음. 작성자가 데이터를 수집하는 것은 기술적으로 불가능합니다. 코드는 완전 오픈소스입니다.

## 설치

**AI 코딩 도구 (전체 경험):** `claude install-skill https://github.com/wallmage/vibecheck`, 그 다음 `/vibecheck scan`.

**샌드박스 환경 (Cowork 등):** 로그를 스캔하지 않아도 80% 효과 — 설정 파일 압축, 비용 절감 규칙 추가. 전체 스캔은 터미널에서 명령어 한 줄만 붙여넣기 (최근 14일분만, ~20-50 MB).

## 명령어

- `/vibecheck scan` — 대화형 교육 + 전체 진단 + 수정
- `/vibecheck explain` — 교육만
- `/vibecheck compress` — 설정 파일 압축 (25-50% 축소)
- `/vibecheck monitor` — 주간 비교 + 알림

## 15가지 낭비 패턴

공회전 나레이션, 컨텍스트 부패, 핑퐁 디버깅, 장황한 출력, 미연결 명령어, 코드베이스 방황, 미배치 편집, 파일 재읽기, 슬립/폴 루프, 실패 재시도, 스키마 조회, Git 의식, 그리고 상시 에이전트의 유휴 하트비트·워크스페이스 비대화·메모리 누적.

## 지원 도구

24종 이상: Claude Code, Cursor, Codex, Windsurf, Cline, OpenClaw, CodeBuddy, TRAE, Kimi Code 등.

모든 LLM 지원: Claude (Opus/Sonnet/Haiku), GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.
