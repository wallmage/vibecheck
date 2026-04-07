# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Dein KI-Coding-Tool verbrennt Geld, das du nicht siehst.**

Jede Nachricht, die du sendest, liest deine KI den *gesamten* Gesprächsverlauf von vorne. Nachricht #50 kostet 50x so viel wie Nachricht #1. Diese Ansage "OK, jetzt werde ich das fixen"? Hat dich Geld gekostet und nichts gebracht. Die 500 Zeilen Build-Logs? Werden bei jeder. einzelnen. zukünftigen. Nachricht. nochmal gelesen.

Die meisten Vibe-Coder verschwenden **über 50%** ihres KI-Token-Budgets, ohne es zu wissen.

vibecheck behebt das. Es scannt deine letzten 14 Tage, findet genau wo die Verschwendung liegt, erklärt es in einfacher Sprache (kein Fachjargon — wir erklären dir was Tokens sind), und wendet Ein-Absatz-Fixes auf deine Konfigurationsdatei an. Gleiche Arbeit. Halbe Kosten.

**Durchschnittliche Ersparnis: 50%+ deiner Token-Rechnung.** Unterstützt alle LLM-Modelle (Claude, GPT, Gemini, DeepSeek). Funktioniert mit Claude Code, OpenClaw, Codex, OpenCode, Cursor, Windsurf und 24+ KI-Coding-Tools. 100% lokal — deine Daten verlassen niemals deinen Rechner.

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## Datenschutz

**Deine Daten verlassen niemals deinen Rechner.** vibecheck besteht aus Python-Skripten, die 100% lokal laufen. Kein Server, keine API, keine Telemetrie, keine Analytik, kein Nach-Hause-Telefonieren. Der Autor kann deine Daten nicht sammeln — es ist technisch unmöglich. Der Code ist Open Source; du kannst jede Zeile lesen.

Der Scan liest deine lokalen Sitzungsprotokolle (JSONL-Dateien auf deiner Festplatte), analysiert sie im Arbeitsspeicher und gibt die Ergebnisse auf deinem Bildschirm aus. Nichts wird hochgeladen, nichts wird irgendwohin gesendet, nichts wird außerhalb deines Rechners gespeichert — nur eine kleine Snapshot-Datei in `~/.vibecheck/` um deinen Fortschritt zu verfolgen.

## Installation

### Option A: KI-Coding-Tools (volles Erlebnis)

Wenn du ein KI-Coding-Tool wie **Claude Code CLI**, **Cursor**, **Windsurf**, **Codex** oder ähnliches nutzt — installiere vibecheck als Skill. Diese Tools laufen direkt auf deinem Rechner und können deine Sitzungsprotokolle lesen, also bekommst du den vollen personalisierten Scan.

**Claude Code CLI:**
```bash
claude install-skill https://github.com/wallmage/vibecheck
```

**Claude Code in der Desktop-App (Builder/Code-Modus):**
Gleicher Installationsbefehl. Die Coding-Modi der Desktop-App (Builder, Code) laufen mit vollem Dateizugriff, genau wie die CLI. Du bekommst das gleiche volle Scan-Erlebnis.

**Andere KI-Coding-Tools (Cursor, Codex, Windsurf, Cline, etc.):**
Sage deiner KI:
> Installiere den vibecheck Skill von https://github.com/wallmage/vibecheck und führe `/vibecheck scan` aus

Dann starte:
```
/vibecheck scan
```

### Option B: Nicht-Coding-Umgebungen (Cowork, Chat-Modi)

Tools wie **Claude Cowork**, Chat-Modi oder browserbasierte KI-Tools laufen in einer Sandbox — sie können deine Projektdateien sehen, aber nicht deinen Chatverlauf. Stell es dir vor wie ein Gast, der dein Wohnzimmer sehen kann, aber nicht dein Schlafzimmer — deine Gespräche sind im privaten Bereich.

**vibecheck funktioniert trotzdem auf zwei Arten:**

1. **Ohne Scan (80% des Nutzens):** Auch ohne deine Logs zu lesen kann vibecheck deine Konfigurationsdatei optimieren — CLAUDE.md trimmen, kostensparende Regeln hinzufügen, aufgeblähte Prompts komprimieren. Diese Fixes allein reduzieren 20-40% der Verschwendung, weil sie die Menge reduzieren, die die KI bei jeder einzelnen Nachricht neu liest. Starte einfach `/vibecheck compress` oder sage der KI, sie soll die Optimierungsregeln anwenden.

2. **Mit Scan (voller Nutzen):** Für eine personalisierte Analyse mit deinen echten Zahlen wird vibecheck dich bitten, einen Befehl in dein normales Terminal einzufügen. Dieser kopiert nur die letzten 14 Tage (~20-50 MB) in einen sichtbaren Ordner:

   ```
   python3 pfad/zu/vibecheck/scripts/export_logs.py
   ```

   vibecheck gibt dir den genauen Befehl — einfach einfügen. Dauert 5 Sekunden. Dann zeige dem Tool `~/vibecheck-logs` und du bekommst den vollen Scan.

### Berechtigungen

vibecheck braucht Zugriff auf deinen **Projektordner** um deine Konfigurationsdatei zu lesen und zu bearbeiten (CLAUDE.md, AGENTS.md, .cursorrules, SOUL.md, etc.). Es fragt vor jeder Änderung um Erlaubnis. Du kannst jeden vorgeschlagenen Edit einzeln annehmen oder ablehnen.

Für den vollen Scan liest es auch deine Sitzungsprotokolle (die JSONL-Dateien, in denen dein KI-Tool den Gesprächsverlauf speichert). Diese bleiben auf deinem Rechner — siehe [Datenschutz](#datenschutz).

## Befehle

- `/vibecheck` oder `/vibecheck scan` — Interaktive Schulung + vollständige Diagnose + Fixes
- `/vibecheck explain` — Nur die Schulung (Rechnung verstehen, keine Änderungen)
- `/vibecheck compress` — Konfigurationsdatei komprimieren (25-50% kleiner)
- `/vibecheck monitor` — Woche-zu-Woche Vergleich mit Warnungen

## So funktioniert's

Die meisten wissen nicht, wofür sie bezahlen. Ein $20/Monat-Abo kann $200+ an echtem KI-Verbrauch verstecken. Aber wohin geht das Geld?

vibecheck startet mit einer interaktiven Lektion — mit DEINEN echten Daten — die es Stück für Stück erklärt:
1. Was sind Tokens? (Hinweis: ungefähr ein Wort)
2. Warum liest die KI bei jeder Nachricht dein ganzes Gespräch neu?
3. Wo geht DEIN Geld hin? (Spoiler: 50-65% ist das Neu-Lesen alter Nachrichten)

Dann findet es deine Verschwendungsmuster und behebt sie mit einem Absatz in deiner Konfigurationsdatei. Gleiche Arbeit, weniger verschwendete Nachrichten.

### Auch ohne Scan

Wenn du deine Logs nicht scannen kannst oder willst, hilft vibecheck trotzdem. Die Installation fügt Optimierungsregeln hinzu. Deine KI lernt:
- Aufhören zu erzählen, was sie gleich tun wird (einfach machen)
- Mehrere Edits in einer Nachricht zusammenfassen
- Befehle verketten statt einzeln auszuführen
- Gespräche kürzer halten um Context-Aufblähung zu vermeiden
- Ausführliche Ausgaben in Dateien umleiten statt den Chat zu fluten

Diese Regeln allein bringen dir ~80% der Ersparnis. Der Scan findet die restlichen 20% und zeigt dir genau, wo dein Geld geblieben ist.

## Vorher / Nachher

vibecheck verfolgt deinen Fortschritt. Erster Lauf zeigt Prognosen, weitere Läufe zeigen echte Ersparnisse:

```
                              VORHER         JETZT          ÄNDERUNG
  Ø Turns/Sitzung             36.8           25.9           -10.9 ✅
  Ø Sub-Agents/Sitzung        3.2            2.9            -0.3 ✅
  Ø Kontextfenster            128.4K         89.9K          -30% ✅
  Verschwendete Turns         36.7%          8.1%           -28.6% ✅

  Ø Kosten/Sitzung            $2.62          $1.35          -$1.27 ✅
  Monatliche Ausgaben         $224           $115           -$109 ✅
```

## Die 15 Verschwendungsmuster

**Stufe 1 — Die großen 3 (70-80% der Verschwendung)**
1. Leerlauf-Erzählung — KI sagt "Jetzt werde ich…" bevor sie es tut
2. Kontext-Verfall — Gespräche die zu lange laufen ohne Reset
3. Ping-Pong-Debugging — Fixen, kaputt machen, fixen, kaputt machen

**Stufe 2 — Die Mechanik (15-20%)**
4. Ausführliche Ausgaben — Build-Logs die das Gespräch fluten
5. Unverkettete Befehle — Befehle einzeln statt zusammen ausführen
6. Codebase-Wandern — 8 Dateien lesen bevor 1 bearbeitet wird
7. Ungebündelte Edits — Ein Edit pro Nachricht statt viele auf einmal

**Stufe 3 — Der Rest (5-10%)**
8. Datei-Neulesen — Gleiche Datei zweimal lesen
9. Sleep/Poll-Schleifen — "Ist es schon fertig?" wiederholt prüfen
10. Fehlgeschlagene Wiederholungen — Kaputte Befehle die im Kontext bleiben
11. Schema-Abfragen — Tools nachschlagen die die KI schon kennt
12. Git-Zeremonie — Git-Befehle einzeln statt verkettet ausführen

**Stufe 4 — Immer-An Agenten (OpenClaw, etc.)**
13. Leerlauf-Heartbeats — Agent wacht alle 5min auf, nichts zu tun, zahlt trotzdem
14. Workspace-Aufblähung — 35K Tokens Persönlichkeit bei jedem Aufwachen neu gelesen
15. Speicher-Ansammlung — Sitzungsverlauf wächst endlos ohne Bereinigung

## Unterstützte Tools (Auto-Erkennung)

24+ Tools: Claude Code, Cursor, Codex, Windsurf, Cline, Roo Code, Aider, Gemini CLI, Copilot, OpenClaw, CodeBuddy, TRAE, Qoder, Kimi Code und mehr.

## Mehrsprachig

Erkennt automatisch deine Systemsprache. Antwortet in deiner Sprache. Jederzeit wechselbar.

## Läuft auf

- macOS (Apple Silicon + Intel), Windows, Linux
- iPad/Mobilgeräte via SSH

Python 3.8+. Keine externen Abhängigkeiten.
