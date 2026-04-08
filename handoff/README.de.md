# handoff

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | Deutsch | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

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

**Deine Konversationen verfallen. Dieses Tool haelt das Signal am Leben.**

Jeder AI-Chat hat eine Halbwertszeit. Je laenger ein Thread laeuft, desto mehr veralteten Kontext liest das Modell erneut, desto unschaerfer wird die Ausgabe und desto mehr Tokens verschwendest du fuer Rauschen. Du kennst die Loesung: eine neue Session starten. Aber dann verlierst du alle Entscheidungen, die du getroffen hast, die Bugs, die du bereits verfolgt hast, die Architektur, auf die du dich geeinigt hast. Also machst du im alten Thread weiter und die Qualitaet sinkt immer weiter.

`handoff` durchbricht diesen Kreislauf. Sag `handoff` in einer beliebigen Session und es generiert einen einzelnen Transfer-Block -- verlustfrei komprimiert, 2-4K Tokens -- der alles Wichtige erfasst: Entscheidungen, Erkenntnisse, Fehlschlaege, aktueller Stand, offene Probleme und naechste Schritte. Fuege ihn in einen neuen Chat ein und du bist sofort wieder auf voller Geschwindigkeit, ohne irgendetwas erneut herausfinden zu muessen.

Keine Dateien. Keine Plugins. Keine Datenbanken. Nur Copy & Paste.

## Wie es funktioniert

**Generierungsmodus** -- Sag in der alten Session `handoff`. Der Skill komprimiert die gesamte Konversation durch verlustfreie Kompression in einen strukturierten Transfer-Block. Das ist keine oberflaechliche Zusammenfassung. Es werden konkrete Ergebnisse bewahrt -- was entschieden wurde, was fehlgeschlagen ist, was halb fertig ist, was als Naechstes kommt -- waehrend Begruessung, Smalltalk, wiederholte Erklaerungen und Roh-Transkripte entfernt werden.

**Wiederaufnahme-Modus** -- Fuege den Block in eine neue Session ein. Der Skill parst ihn, gibt dir eine kompakte Zusammenfassung des aktuellen Stands und wartet auf deine naechste Anweisung.

Der Transfer-Block zielt auf **2-4K Tokens** ab. Klein genug fuer haeufige Nutzung. Dicht genug, um nichts Wichtiges zu verlieren.

## Natuerliche Trigger

Du musst dir keinen speziellen Befehl merken. Jeder dieser Ausdruecke funktioniert:

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## Was erhalten bleibt

- Entscheidungen und ihre Begruendungen
- Technische Erkenntnisse und Mechanismen
- Fehlgeschlagene Experimente und Ursachen
- Wichtige Zahlen, Limits, Versionen, Zeitmessungen, Kosten
- Aktueller Branch / Commit / Dirty State
- Nicht committete oder teilweise fertige Arbeit
- Offene Probleme und Blocker
- Die beste naechste Aktion

Was entfernt wird: Begruessung, Aufmunterung, wiederholtes Hin-und-Her, rohe Code-Dumps, Nebendiskussionen ohne Ergebnis, Erzaehlungen darueber was der Assistent als Naechstes tun wollte. Das Signal bleibt. Das Rauschen verschwindet.

## Funktioniert ueberall

`handoff` basiert auf reinem Text. Es funktioniert in:

- Coding-Tools (Claude Code, Cursor, Copilot, Windsurf)
- CLI-Tools (terminalbasierte AI-Assistenten)
- GUI-Chat-Tools (ChatGPT, Claude chat, Gemini)
- Jedem Produkt, in dem du Text in eine neue Konversation einfuegen kannst

Keine spezielle Integration erforderlich.

## Wann verwenden

- Der aktuelle Chat wird lang und das Modell wird traege
- Du hast einen Arbeitsabschnitt abgeschlossen und willst eine saubere neue Session
- Du naeherst dich dem Kontext-Limit
- Du willst Entscheidungen bewahren, ohne den gesamten alten Thread am Leben zu halten
- Du wechselst zwischen Rechnern oder Tools

## Installation

Kopiere dies in dein AI-Tool:

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## Verwendung

Im alten Chat:

```text
handoff
```

Kopiere den generierten Block. Oeffne eine neue Session. Einfuegen.

Das war's.

---

Autor: [Wallny](https://github.com/wallmage)
