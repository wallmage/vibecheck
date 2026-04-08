# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Jeder Turn deiner KI kostet Geld.** Sonnet 4.6: $3/$15 pro MTok (Input/Output). Opus 4.6: $5/$25 — 1,67x teurer. Ein Turn zur Session-Mitte kostet auf Sonnet ~$0.038. Wenn deine KI erst sagt „OK, ich fixe das jetzt" und es dann fixt — diese $0.031 waren reine Verschwendung. Und es wird schlimmer: Jeder Turn liest die gesamte Konversation von Anfang an neu. Je länger das Gespräch, desto teurer jeder Turn. Das ist Kontext-Aufblähung.

KI-Coding-Tools verschwenden ständig Turns — erst erzählen statt handeln, Dateien einzeln lesen statt alle auf einmal, `git add` und `git commit` als getrennte Turns ausführen. vibecheck erkennt 18 Mechanismen in 4 Stufen, behebt sie durch Regeln in der Konfigurationsdatei und Komprimierung und verfolgt Verbesserungen kontinuierlich. Reduziert deine Rechnung um 40-65% je nach Nutzungsmuster. [Detaillierte Spezifikation →](SPECSHEET.md)

Unterstützt Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ Tools. Läuft lokal, deine Daten verlassen nie deinen Rechner.

## Installation

Füge dies in dein KI-Coding-Tool ein und drücke Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

Fertig. Deine KI erledigt den Rest.

<details>
<summary>Oder manuell per Kommandozeile</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Dann `/vibecheck scan` in einer beliebigen Session eingeben

Update: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Was ist ein „Skill"?

Ein Skill ist wie ein Rezept für deine KI. Er verändert deine KI nicht und installiert nichts auf deinem Computer. Er gibt deiner KI nur Anweisungen — „so findest du Verschwendungsmuster, so erklärst du sie, so behebst du sie." Jederzeit entfernbar.

### Coding-Tools vs Chat-Tools

**Coding-Tools** (Claude Code CLI, Cursor, Codex etc.) laufen direkt auf deinem Rechner. Voller Scan mit echten Zahlen.

**Chat/Sandbox-Tools** (Claude Cowork etc.) laufen in einer Sandbox — Projektdateien sichtbar, Chatverlauf nicht.

1. **Ohne Scan (80% Nutzen):** Konfigurationsdatei optimieren. Kein Log-Zugriff nötig.
2. **Mit Scan (voller Nutzen):** Ein Befehl im Terminal — nur die letzten 14 Tage (~20-50 MB).

### Berechtigungen

Zugriff auf deinen **Projektordner** zum Lesen/Bearbeiten der Konfigurationsdatei. Fragt vor jeder Änderung.

## Datenschutz

**Deine Daten verlassen niemals deinen Rechner.** Kein Server, keine API, keine Telemetrie. Code ist komplett Open Source.

## Befehle

- `/vibecheck scan` — Interaktive Schulung + Diagnose + Fixes
- `/vibecheck explain` — Nur Schulung
- `/vibecheck compress` — Konfigurationsdatei komprimieren (25-50%)
- `/vibecheck monitor` — Woche-zu-Woche Vergleich + Warnungen

## 18 Mechanismen

**Stufe 1 (70-80%):** Leerlauf-Erzählung, Kontext-Verfall, Ping-Pong-Debugging
**Stufe 2 (15-20%):** Ausführliche Ausgaben, unverkettete Befehle, Codebase-Wandern, ungebündelte Edits
**Stufe 3 (5-10%):** Datei-Neulesen, Sleep/Poll-Schleifen, fehlgeschlagene Retries, Schema-Abfragen, Git-Zeremonie
**Stufe 4 — Immer-An Agenten:** Leerlauf-Heartbeats, Workspace-Aufblähung, Speicher-Ansammlung

## Unterstützte Tools

24+. Alle LLMs: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7 und 40+ weitere.

macOS, Windows, Linux, iPad/Mobil via SSH. Python 3.8+, keine externen Abhängigkeiten.
