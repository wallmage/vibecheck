# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**AI의 매 턴마다 돈이 듭니다.** Sonnet 4.6 가격: $3/$15/MTok (입력/출력), Opus 4.6: $5/$25 — 1.67배. 세션 중반 Sonnet 턴당 비용 ~$0.038. AI가 "네, 수정하겠습니다"라고 말한 뒤 수정하면 — 그 $0.031은 낭비입니다. 게다가 매 턴마다 대화 전체를 처음부터 다시 읽습니다. 대화가 길어질수록 턴당 비용이 올라갑니다. 이것이 컨텍스트 팽창입니다.

AI 코딩 도구는 끊임없이 턴을 낭비합니다 — 실행 전에 설명하기, 파일을 하나씩 읽기, `git add`와 `git commit`을 따로 실행하기. vibecheck은 4개 계층 18가지 메커니즘을 감지하고, 설정 파일 규칙과 압축으로 수정하며, 개선을 지속 추적합니다. 사용 패턴에 따라 40-65% 절감 가능합니다. [상세 메커니즘 사양 →](SPECSHEET.md)

Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax 지원. 24+ 도구. 로컬 실행, 데이터는 외부로 전송되지 않습니다.

## 설치 방법

AI 코딩 도구에 이것을 붙여넣고 Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

끝. AI가 나머지를 처리합니다.

<details>
<summary>또는 명령줄로 수동 설치</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

아무 세션에서 `/vibecheck scan` 입력

업데이트: `cd ~/.claude/skills/vibecheck && git pull`
</details>

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

## 18가지 메커니즘

**1층 (70-80%):** 공회전 나레이션, 컨텍스트 부패, 핑퐁 디버깅
**2층 (15-20%):** 장황한 출력, 미연결 명령어, 코드베이스 방황, 미배치 편집
**3층 (5-10%):** 파일 재읽기, 슬립/폴 루프, 실패 재시도, 스키마 조회, Git 의식
**4층 — 상시 에이전트:** 유휴 하트비트, 워크스페이스 비대화, 메모리 누적

## 지원 도구

24종 이상. 모든 LLM: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7 외 40+개 모델.

macOS, Windows, Linux, iPad/모바일 via SSH. Python 3.8+, 외부 의존성 없음.
