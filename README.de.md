# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Dein KI-Coding-Tool verbrennt Geld, das du nicht siehst.**

Jede Nachricht, die du sendest, liest deine KI den *gesamten* Gesprächsverlauf von vorne. Nachricht #50 kostet 50x so viel wie Nachricht #1. Diese Ansage "OK, jetzt werde ich das fixen"? Hat dich Geld gekostet und nichts gebracht. Die 500 Zeilen Build-Logs? Werden bei jeder zukünftigen Nachricht nochmal gelesen.

Die meisten Vibe-Coder verschwenden **über 50%** ihres KI-Token-Budgets, ohne es zu wissen.

vibecheck behebt das. Es scannt deine letzten 14 Tage, findet genau wo die Verschwendung liegt, erklärt es in einfacher Sprache (kein Fachjargon), und wendet Ein-Absatz-Fixes auf deine Konfigurationsdatei an. Gleiche Arbeit. Halbe Kosten.

**Durchschnittliche Ersparnis: 50%+ deiner Token-Rechnung.** Unterstützt alle LLM-Modelle (Claude, GPT, Gemini, DeepSeek). Funktioniert mit Claude Code, OpenClaw, Codex, OpenCode, Cursor, Windsurf und 24+ KI-Coding-Tools. 100% lokal — deine Daten verlassen niemals deinen Rechner.

## Sofort loslegen — kein Download nötig

vibecheck ist ein **Skill** — ein Satz Anweisungen, den dein KI-Coding-Tool lernt. Du musst keine Software herunterladen oder installieren. Gib deiner KI einfach einen Link, und sie bringt sich selbst bei, wie sie deine Kosten optimiert. Eine Nachricht, fertig.

**Kopiere das in dein KI-Coding-Tool** (Claude Code, Cursor, Codex, Windsurf, Cline — egal welches):

> Installiere den vibecheck Skill von https://github.com/wallmage/vibecheck und führe /vibecheck scan aus

Das war's. Deine KI liest den Skill, scannt deine letzten 14 Tage und erklärt dir alles.

**Oder per CLI:**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

**Sandbox-Tools (Cowork etc.):**
> Klone https://github.com/wallmage/vibecheck nach /tmp/vibecheck, lies SKILL.md, und führe /vibecheck scan aus

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

## 15 Verschwendungsmuster

**Stufe 1 (70-80%):** Leerlauf-Erzählung, Kontext-Verfall, Ping-Pong-Debugging
**Stufe 2 (15-20%):** Ausführliche Ausgaben, unverkettete Befehle, Codebase-Wandern, ungebündelte Edits
**Stufe 3 (5-10%):** Datei-Neulesen, Sleep/Poll-Schleifen, fehlgeschlagene Retries, Schema-Abfragen, Git-Zeremonie
**Stufe 4 — Immer-An Agenten:** Leerlauf-Heartbeats, Workspace-Aufblähung, Speicher-Ansammlung

## Unterstützte Tools

24+. Alle LLMs: Claude, GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.

macOS, Windows, Linux, iPad/Mobil via SSH. Python 3.8+, keine externen Abhängigkeiten.
