# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**당신의 AI 코딩 도구가 보이지 않는 돈을 태우고 있습니다.**

메시지를 보낼 때마다 AI는 *전체* 대화 기록을 처음부터 다시 읽습니다. 50번째 메시지는 1번째의 50배 비용. AI가 "네, 이제 수정하겠습니다"라고 한 그 말? 돈만 들고 아무것도 안 했습니다. 500줄 빌드 로그? 이후 모든 메시지에서 매번 다시 읽힙니다.

대부분의 바이브 코더는 모르는 사이에 AI 토큰 예산의 **50% 이상**을 낭비합니다.

vibecheck이 해결합니다. 최근 14일 세션을 스캔하고, 낭비를 정확히 찾고, 쉬운 말로 설명하고, 설정 파일에 한 문단만 추가. 같은 작업, 절반의 비용.

**평균 절약: 토큰 비용의 50% 이상.** 모든 LLM 모델(Claude, GPT, Gemini, DeepSeek) 지원. Claude Code, OpenClaw, Codex, OpenCode, Cursor, Windsurf 등 24+ 도구 호환. 100% 로컬 실행 — 데이터는 절대 외부로 전송되지 않습니다.

## 바로 시작 — 다운로드 필요 없음

vibecheck은 **스킬**입니다 — AI 코딩 도구가 배울 수 있는 지침 세트입니다. 소프트웨어를 다운로드하거나 설치할 필요 없습니다. AI에 링크를 주면 스스로 비용 최적화 방법을 배웁니다. 메시지 하나면 끝.

**AI 코딩 도구에 이것을 복사하세요** (Claude Code, Cursor, Codex, Windsurf, Cline — 아무거나):

> https://github.com/wallmage/vibecheck 에서 vibecheck 스킬을 설치하고 /vibecheck scan 을 실행해주세요

이게 전부입니다. AI가 스킬을 읽고, 14일을 스캔하고, 모든 것을 설명해줍니다.

**CLI의 경우:**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

**샌드박스 도구 (Cowork 등):**
> https://github.com/wallmage/vibecheck 를 /tmp/vibecheck 에 클론하고, SKILL.md를 읽고, /vibecheck scan 을 실행해주세요

### "스킬"이란?

스킬은 AI를 위한 레시피 카드와 같습니다. AI를 변경하거나 컴퓨터에 아무것도 설치하지 않습니다. "낭비 패턴 찾는 법, 설명하는 법, 고치는 법"이라는 지침을 줄 뿐. 언제든 제거 가능.

### 코딩 도구 vs 채팅 도구

**코딩 도구** (Claude Code CLI, Cursor, Codex 등): 직접 실행, 로그 접근 가능, 완전한 맞춤 스캔.

**채팅/샌드박스 도구** (Cowork 등): 프로젝트 파일은 보이지만 채팅 기록은 안 보임.

1. **스캔 없이 (80% 효과):** 설정 파일 최적화. 로그 불필요.
2. **스캔 포함 (완전한 효과):** 터미널에서 명령어 한 줄 — 최근 14일분만 (~20-50 MB).

### 권한

**프로젝트 폴더** 접근이 필요합니다. 변경 전 반드시 확인을 요청합니다.

## 개인정보 보호

**데이터는 절대 컴퓨터 밖으로 나가지 않습니다.** 서버 없음, API 없음, 텔레메트리 없음. 코드는 완전 오픈소스.

## 명령어

- `/vibecheck scan` — 대화형 교육 + 전체 진단 + 수정
- `/vibecheck explain` — 교육만
- `/vibecheck compress` — 설정 파일 압축 (25-50%)
- `/vibecheck monitor` — 주간 비교 + 알림

## 15가지 낭비 패턴

**1층 (70-80%):** 공회전 나레이션, 컨텍스트 부패, 핑퐁 디버깅
**2층 (15-20%):** 장황한 출력, 미연결 명령어, 코드베이스 방황, 미배치 편집
**3층 (5-10%):** 파일 재읽기, 슬립/폴 루프, 실패 재시도, 스키마 조회, Git 의식
**4층 — 상시 에이전트:** 유휴 하트비트, 워크스페이스 비대화, 메모리 누적

## 지원 도구

24종 이상. 모든 LLM: Claude, GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.

macOS, Windows, Linux, iPad/모바일 via SSH. Python 3.8+, 외부 의존성 없음.
