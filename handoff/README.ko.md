# handoff

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | 한국어 | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

[![GitHub stars](https://img.shields.io/github/stars/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/watchers)
[![GitHub last commit](https://img.shields.io/github/last-commit/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff)
[![Top language](https://img.shields.io/github/languages/top/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff)
[![Workflow](https://img.shields.io/badge/workflow-copy%20%26%20paste-111827?style=flat-square)](https://github.com/wallmage/handoff)
[![Works in](https://img.shields.io/badge/works%20in-CLI%20%7C%20GUI%20%7C%20chat-0f766e?style=flat-square)](https://github.com/wallmage/handoff)
[![Storage](https://img.shields.io/badge/storage-no%20files-4f46e5?style=flat-square)](https://github.com/wallmage/handoff)
[![Focus](https://img.shields.io/badge/focus-context%20transfer-b45309?style=flat-square)](https://github.com/wallmage/handoff)
[![Use case](https://img.shields.io/badge/use%20case-context%20rot%20recovery-2563eb?style=flat-square)](https://github.com/wallmage/handoff)

**대화는 부패한다. 이 도구는 신호를 살려둔다.**

모든 AI 채팅에는 반감기가 있다. 스레드가 길어질수록 모델은 낡은 컨텍스트를 반복해서 읽고, 출력은 둔해지며, 노이즈에 토큰을 낭비하게 된다. 해결책은 알고 있다: 새 세션을 시작하면 된다. 하지만 그러면 내린 결정, 추적한 버그, 확정한 아키텍처를 모두 잃는다. 그래서 낡은 스레드에서 계속하게 되고, 품질은 계속 떨어진다.

`handoff`는 이 악순환을 끊는다. 아무 세션에서나 `handoff`라고 말하면 하나의 전송 블록이 생성된다 -- 무손실 압축, 2-4K 토큰 -- 중요한 모든 것을 담는다: 결정, 발견, 실패, 현재 상태, 미해결 이슈, 다음 단계. 새 채팅에 붙여넣으면 재발견 없이 바로 전속력으로 복귀한다.

파일 없음. 플러그인 없음. 데이터베이스 없음. 복사해서 붙여넣기만 하면 된다.

## 작동 방식

**생성 모드** -- 이전 세션에서 `handoff`라고 말한다. 스킬이 무손실 압축으로 전체 대화를 구조화된 전송 블록으로 압축한다. 가벼운 요약이 아니다. 구체적인 결과를 보존한다 -- 무엇을 결정했는지, 무엇이 실패했는지, 무엇이 절반만 되었는지, 다음은 무엇인지 -- 인사, 잡담, 반복 설명, 원시 로그는 제거된다.

**재개 모드** -- 전송 블록을 새 세션에 붙여넣는다. 스킬이 이를 파싱하고 현재 상황의 간결한 요약을 제공한 뒤 다음 지시를 기다린다.

전송 블록 목표 크기는 **2-4K 토큰**. 자주 사용할 수 있을 만큼 작고, 중요한 정보를 잃지 않을 만큼 밀도가 높다.

## 자연스러운 트리거

특별한 명령을 외울 필요가 없다. 다음 중 아무거나 사용하면 된다:

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## 보존되는 내용

- 결정과 그 이유
- 기술적 발견과 메커니즘
- 실패한 실험과 실패 원인
- 중요한 숫자, 제한, 버전, 타이밍, 비용
- 현재 브랜치 / 커밋 / 더티 상태
- 커밋되지 않았거나 부분적으로 완료된 작업
- 미해결 이슈와 블로커
- 최선의 다음 행동

제거되는 내용: 인사, 격려, 반복적인 주고받기, 원시 코드 덤프, 아무것도 바꾸지 않은 잡담, 어시스턴트가 다음에 할 일에 대한 서술. 신호는 남는다. 노이즈는 사라진다.

## 어디서든 작동

`handoff`는 일반 텍스트로 작동한다. 다음에서 사용 가능:

- 코딩 도구 (Claude Code, Cursor, Copilot, Windsurf)
- CLI 도구 (터미널 기반 AI 어시스턴트)
- GUI 채팅 도구 (ChatGPT, Claude chat, Gemini)
- 새 대화에 텍스트를 붙여넣을 수 있는 모든 제품

특별한 연동 불필요.

## 사용 시점

- 현재 채팅이 길어져서 모델이 느려질 때
- 작업 한 구간을 마치고 깨끗한 새 세션을 원할 때
- 컨텍스트 제한에 가까워질 때
- 결정은 보존하되 전체 이전 스레드는 유지하고 싶지 않을 때
- 다른 기기나 도구로 전환할 때

## 설치

AI 도구에 다음을 복사하세요:

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## 사용법

이전 채팅에서:

```text
handoff
```

생성된 블록을 복사. 새 세션을 열기. 붙여넣기.

끝.

---

저자: [Wallny](https://github.com/wallmage)
