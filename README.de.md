# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Jeder Turn, den deine KI macht, kostet Geld.** Sonnet 4.6: $3/$15 pro Million Tokens (Input/Output). Opus 4.6: $5/$25 — 1,67-mal mehr. So sieht das in der Praxis aus:

- Deine KI sagt „OK, ich beheble das" bevor sie es tatsächlich tut. Dieser Narrations-Turn: **$0.031 verschwendet.** Fünf pro Session: **$0.165 weg.**
- Dein Gespräch erreicht 40 Turns anstatt bei 20 aufgeteilt zu werden. Mehrkosten durch das Wiederlesen des gesamten Verlaufs: **$0.67 verschwendet.**
- `git add`, dann `git commit`, dann `git push` — drei Turns statt einem verketteten Befehl: **$0.098 verschwendet.**

Das sind 3 der 15 Verschwendungsmuster, die vibecheck erkennt. Jedes wird unten mit Dollarbeträgen erklärt — was schiefläuft und wie wir es beheben.

Funktioniert mit Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ Coding-Tools. Läuft lokal — deine Daten bleiben auf deinem Gerät.

## Installation

Füge das in dein KI-Coding-Tool ein und drücke Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

Das war's. Deine KI erledigt den Rest.

<details>
<summary>Oder manuell über die Kommandozeile installieren</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Dann `/vibecheck scan` in einer beliebigen Session eingeben.

Zum Aktualisieren: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Was ist ein Skill?

Eine Rezeptkarte für deine KI. Sie verändert nichts und installiert nichts. Nur eine Textdatei, die beschreibt: „So findest und behebst du Verschwendung." Jederzeit löschbar.

### Coding-Tools vs. Chat-Tools

**Coding-Tools** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder usw.) laufen auf deinem Gerät — vibecheck erkennt dein Tool automatisch und scannt deine Session-Logs.

**Chat-Tools** (Cowork, browserbasiert) laufen in einer Sandbox. vibecheck optimiert trotzdem deine Instruktionsdatei (der größte Teil des Nutzens), oder du fügst einen Terminal-Befehl ein, um 14 Tage Logs für einen vollständigen Scan zu übertragen.

### Berechtigungen

vibecheck liest und bearbeitet deine Instruktionsdatei (CLAUDE.md, .cursorrules usw.). Es fragt vor jeder Änderung.

## Datenschutz

Deine Daten verlassen dein Gerät nicht. Kein Server, keine API, kein Telemetry. Open Source.

## Befehle

- `/vibecheck scan` — erklärt, was Tokens sind, scannt deine Sessions, wendet Fixes an
- `/vibecheck explain` — nur die Erklärung, keine Änderungen
- `/vibecheck compress` — reduziert deine Instruktionsdatei um 25–50 %
- `/vibecheck monitor` — wöchentlicher Vergleich, markiert Regressionen

## Vorher / Nachher

```
                          VORHER         JETZT          ÄNDERUNG
Avg turns/session         36.8           25.9           -10.9
Avg context window        128.4K         89.9K          -30%
Wasteful turns            36.7%          8.1%           -28.6%

Avg cost/session          $2.62          $1.35          -$1.27
Monthly spend             $224           $115           -$109
```

---

## Wie Turns Geld kosten

Bei jedem Turn liest deine KI das gesamte Gespräch erneut — System-Prompt, Instruktionsdatei, alle vorherigen Nachrichten, alle Tool-Ausgaben — und generiert dann eine Antwort.

**Turn-Kosten = Input-Tokens × Input-Rate + Output-Tokens × Output-Rate**

Frühe Turns sind günstig (kleiner context). Späte Turns sind teuer (alles davor wird neu gelesen). Deshalb summiert sich Verschwendung — ein verschwendeter Turn macht jeden zukünftigen Turn teurer, weil der verschwendete Inhalt im context verbleibt.

Prompt-Caching reduziert die Input-Kosten für bereits gesehene Inhalte um den Faktor 10. Die meisten Tools nutzen es automatisch.

**Abo-Nutzer:** Du siehst API-Preise nicht direkt, aber Verschwendung verbraucht dein Nachrichtenkontingent schneller. Claude Pro ($20/Monat) deckt ~$200 an API-Wert ab. Max ($200/Monat) deckt ~$4.000 ab.

### Referenz-Szenario

Alle unten genannten Dollarbeträge verwenden diese Ausgangslage (Sonnet 4.6):

| Parameter | Wert |
|---|---|
| Session-Länge | 25 Turns |
| Startkontext | 5.000 Tokens |
| Wachstum pro Turn | ~3.000 Tokens |
| Cache-Trefferrate | 90 % |
| Mid-Session Turn-Kosten | $0.038 |
| Effiziente Session gesamt | $0.96 |

Für Opus 4.6 alle Kosten mit 1,67 multiplizieren.

---

## Die 15 Verschwendungsmuster

### Tier 1 — Die großen 3 (60–70 % der Verschwendung)

#### 1. Idle Narration

**Was es ist.** Die KI sagt „OK, ich beheble das" oder „Lass mich zuerst die Datei lesen" — und erledigt die eigentliche Arbeit erst im nächsten Turn. Der Narrations-Turn hat nichts getan: kein Tool-Aufruf, kein Code, kein Dateilesen.

**Die Verschwendung.** Jeder Narrations-Turn kostet **$0.031** (context-Wiederlesen + ~500 Tokens Statustext). Die meisten Sessions haben davon 5: **$0.165/Session verschwendet** — 17 % deiner Rechnung für nichts. Bei 10 Sessions/Tag: **$1.65/Tag ($50/Monat)** nur für Narration.

**Der Fix.** vibecheck fügt hinzu: *„Kein Turn ohne Tool-Aufruf. Keine Narration. Im selben Turn denken und handeln."* Eliminiert Narration vollständig. **Spart $0.15–0.18/Session.**

#### 2. Context Rot

**Was es ist.** Lange Gespräche werden progressiv teurer. Turn 50 liest alle 49 vorherigen Turns neu. Die gesamten Session-Kosten wachsen quadratisch mit der Länge.

**Die Verschwendung.** Eine 40-Turn-Session: **$1.89.** Zwei 20-Turn-Sessions (gleiche Arbeit): **$1.22.** Die Differenz — **$0.67** — kauft nichts. Bei 100 Turns: eine Session kostet **$5.62** vs. vier 25-Turn-Sessions zu **$3.84.** Das sind **$1.78 verschwendet** durch fehlendes Aufteilen.

**Der Fix.** Lehrt: *„/clear oder /compact zwischen unverwandten Aufgaben nutzen. Neue Gespräche starten."* **Spart $0.30–0.70/Session bei Nutzern mit Langsession-Gewohnheiten.**

#### 3. Ping-Pong-Debugging

**Was es ist.** Fixen, brechen, erneut versuchen, wieder brechen. Jeder fehlgeschlagene Versuch fügt Fehlerausgabe zum context hinzu (~4K Tokens pro Zyklus), die bei jedem zukünftigen Turn neu gelesen wird.

**Die Verschwendung.** Drei fehlgeschlagene Zyklen: 6 extra Turns ($0.252) + 12K Tokens toter Fehler ($0.036 context-Steuer). **Gesamt: ~$0.29 pro Episode.** Tritt in ~1/3 der Sessions auf. **Gewichtet: ~$0.10/Session.**

**Der Fix.** Fügt hinzu: *„Nach 2 fehlgeschlagenen Fixes an derselben Datei: stoppen, Fehler vollständig neu lesen, nachdenken, einziger gezielter Fix."* **Spart ~$0.20 pro Episode.**

### Tier 2 — Turn-Dichte (15–20 % der Verschwendung)

#### 4. Verbose Tool Output

**Was es ist.** Build/Test-Befehl gibt 500 Zeilen (~5K Tokens) ins Gespräch aus. Diese Tokens werden bei jedem zukünftigen Turn neu gelesen.

**Die Verschwendung.** 5K Tokens × 12 verbleibende Turns × $0.30/1M = **$0.018/Instanz** context-Steuer. Passiert 2–3 Mal/Session. Ohne Caching: **$0.180/Instanz** — 10-mal schlechter. **Gesamt: $0.04–0.05/Session.**

**Der Fix.** Fügt hinzu: *„Build/Test-Output nach /tmp/ pipen, --quiet-Flags nutzen, tail -50 max."* **Spart $0.03–0.05/Session.**

#### 5. Unchained Commands

**Was es ist.** `npm install` in einem Turn, `npm run build` im nächsten. Zwei context-Wiederlesungen, wenn `&&` sie in einem verkettet.

**Die Verschwendung.** Jede Aufteilung: **$0.023.** Typische Sessions haben 3–4 Aufteilungen. **Gesamt: $0.07–0.09/Session.**

**Der Fix.** Fügt hinzu: *„Befehle mit `&&` verketten, wo sicher."* **Spart $0.06–0.08/Session.**

#### 6. Codebase Wandering

**Was es ist.** Die KI öffnet Datei für Datei — README, package.json, Configs — bevor sie irgendwas tut. Fünf oder mehr aufeinanderfolgende Lesevorgänge vor der ersten Bearbeitung.

**Die Verschwendung.** Fünf unnötige Lesevorgänge: $0.190 in Turns + $0.027 context-Steuer = **$0.217/Episode.** Tritt in ~25 % der Sessions auf. **Gewichtet: ~$0.054/Session.**

**Der Fix.** Fördert gezieltes Suchen (grep/glob zuerst), mehrere Lesevorgänge pro Turn bündeln. **Spart ~$0.15 pro Episode.**

#### 7. Unbatched Edits

**Was es ist.** Datei A bearbeiten, dann B, dann C — drei Turns, wenn ein Turn mit parallelen Bearbeitungen genügen würde.

**Die Verschwendung.** 2 extra Turns × $0.038 = **$0.076/Instanz.** Passiert in ~60 % der Sessions. **Gewichtet: ~$0.046/Session.**

**Der Fix.** Fügt hinzu: *„Unabhängige Tool-Aufrufe bündeln (mehrere Reads/Edits pro Turn)."* **Spart ~$0.04/Session.**

### Tier 3 — Der Schwanz (5–10 % der Verschwendung)

#### 8. File Re-reads

**Was es ist.** Dieselbe Datei zweimal in einer Session gelesen. Der Inhalt ist nach dem ersten Lesen bereits im context.

**Die Verschwendung.** 1 verschwendeter Turn + doppelter Inhalt = **$0.043/Wiederlesen.** 1–2 pro Session. **Gewichtet: ~$0.039/Session.**

**Der Fix.** Fügt hinzu: *„Inhalt ist nach erstem Lesen im context. Nur erneut lesen, wenn Datei geändert wurde."* **Spart ~$0.03/Session.**

#### 9. Sleep/Poll Loops

**Was es ist.** `sleep 5 && check_status`, 3–5 Mal wiederholt. Jede Abfrage liest den gesamten context neu.

**Die Verschwendung.** 4 Abfragen × $0.038 = **$0.152/Episode.** Tritt in ~20 % der Sessions auf. **Gewichtet: ~$0.030/Session.**

**Der Fix.** Fügt hinzu: *„--wait-Flags oder run_in_background nutzen."* **Spart ~$0.12/Episode.**

#### 10. Failed Retries

**Was es ist.** Befehl schlägt fehl, KI führt exakt denselben Befehl erneut aus. Fehlerausgabe jetzt zweimal im context.

**Die Verschwendung.** **$0.042/Retry.** Tritt in ~30 % der Sessions auf. **Gewichtet: ~$0.013/Session.**

**Der Fix.** Gleiche Regel wie bei Ping-Pong: *„Stoppen, Fehler neu lesen, nachdenken, einziger gezielter Fix."*

#### 11. Schema Lookups

**Was es ist.** KI schlägt eigene Tool-Definitionen nach — Informationen, die sie bereits hat. Fügt 2K+ Tokens zum context hinzu.

**Die Verschwendung.** **$0.052/Lookup.** Tritt in ~40 % der Sessions auf. **Gewichtet: ~$0.021/Session.**

**Der Fix.** „Kein Turn ohne Tool-Aufruf" entmutigt Discovery-Turns. **Spart ~$0.02/Session.**

#### 12. Git Ceremony

**Was es ist.** `git add` → `git status` → `git commit` → `git push`, vier Turns. `git add -A && git commit -m "msg" && git push` ist einer.

**Die Verschwendung.** 3 extra Turns + Git-Output = **$0.098/Instanz.** Passiert in ~70 % der Sessions. **Gewichtet: ~$0.069/Session.**

**Der Fix.** Fügt hinzu: *„Git-Befehle mit `&&` verketten."* **Spart ~$0.06/Session.**

### Tier 4 — Always-On-Agents (OpenClaw usw.)

Anderes Kostenmodell: Kosten pro Aufwachen × Aufwachen pro Tag.

#### 13. Idle Heartbeats

**Was es ist.** Agent wacht alle 5 Minuten auf, liest den gesamten Workspace neu, findet nichts. 288 Aufwachen/Tag, ~97 % inaktiv.

**Die Verschwendung.** 280 inaktive Aufwachen/Tag × $0.04 = **$11.20/Tag ($336/Monat)** für nichts.

**Der Fix.** *„30 Minuten Mindest-Heartbeat. Überspringen, wenn keine Auslöser."* Reduziert auf ~48 Aufwachen/Tag. **Spart $8–10/Tag ($240–300/Monat).**

#### 14. Workspace File Bloat

**Was es ist.** 35K Tokens an Persönlichkeitsdateien (SOUL.md, AGENTS.md) werden bei jedem Aufwachen neu gelesen. Die KI braucht nur die Verhaltensregeln — Tutorials und Coaching sind für Menschen.

**Die Verschwendung.** **$5.76/Tag ($173/Monat)** nur für das Lesen von Konfigurationsdateien.

**Der Fix.** Komprimiert Workspace-Dateien: 35K → 12–15K Tokens. **Spart $3–4/Tag ($90–120/Monat).**

#### 15. Memory Accumulation

**Was es ist.** Session-Verlauf wächst ohne Bereinigung. 100+ Einträge werden bei jedem Aufwachen neu gelesen.

**Die Verschwendung.** **$3.17/Tag ($95/Monat)** für das Lesen veralteter Erinnerungen.

**Der Fix.** *„Nach 50 Turns archivieren, zusammenfassen, neu starten."* **Spart $2–3/Tag ($60–90/Monat).**

---

## Plus: Optimierungs-Tools

### Instruktionsdatei-Komprimierung

Deine Instruktionsdatei wird bei jedem Turn gelesen — eine fixe Steuer, die du unabhängig von der Aufgabe zahlst. vibecheck enthält einen verlustfreien 4-Pass-Kompressor (23 Techniken), der die Dateigröße um 25–50 % reduziert:

- **Pass 1 (Mechanisch):** Markdown entfernen, Tabellen umwandeln, Aufzählungen zusammenführen. ~10–15 %.
- **Pass 2 (Faktenerhaltend):** Fakten deduplizieren, Code-Beispiele komprimieren. ~15–25 %.
- **Pass 3 (High-Fidelity):** Tutorial- und Coaching-Text entfernen, den Menschen brauchen, die KI nicht. ~10–15 %.
- **Pass 4 (Telegramm):** Vollständige Kurzschrift-Umschreibung für KI-only-Dateien. ~15–25 % (nur mit Erlaubnis).

Eine 10K-Token-Datei, auf 6K komprimiert, spart $0.057/Session. Bei 10 Sessions/Tag: **$0.57/Tag ($17/Monat).**

### Output-Unterdrückung

Output-Tokens kosten 5-mal so viel wie Input ($15 vs. $3/MTok bei Sonnet). Die KI zeigt vollständige Code-Blöcke und Diffs, die du nicht angefordert hast, und verschwendet damit **~$0.047/Session.** vibecheck fügt hinzu: *„Kein Code/keine Diffs, außer wenn angefordert."*

### Kosten-Monitoring

`/vibecheck monitor` erstellt einen Snapshot deines Session-Profils und vergleicht ihn bei nachfolgenden Ausführungen mit dem Basiswert. Erkennt Regressionen, bevor sie Geld kosten.

---

## Einsparungs-Zusammenfassung

### Interaktive Tools (Sonnet 4.6)

| # | Muster | Durchschn. Verschwendung/Session | Durchschn. Ersparnis |
|---|---|---|---|
| 1 | Idle Narration | $0.165 | $0.155 |
| 2 | Context Rot | $0.150 | $0.120 |
| 3 | Ping-Pong-Debugging | $0.097 | $0.067 |
| 4 | Verbose Output | $0.045 | $0.035 |
| 5 | Unchained Commands | $0.080 | $0.065 |
| 6 | Codebase Wandering | $0.054 | $0.040 |
| 7 | Unbatched Edits | $0.046 | $0.038 |
| 8 | File Re-reads | $0.039 | $0.030 |
| 9 | Sleep/Poll Loops | $0.030 | $0.025 |
| 10 | Failed Retries | $0.013 | $0.010 |
| 11 | Schema Lookups | $0.021 | $0.018 |
| 12 | Git Ceremony | $0.069 | $0.058 |
| + | Komprimierung | $0.057 | $0.057 |
| + | Output-Unterdrückung | $0.047 | $0.038 |
| | **Gesamt** | **$0.913** | **$0.756** |

**Typische verschwenderische Session: $1.87. Nach vibecheck: $1.11. Ersparnis: 41 %.**

- **Geringe Verschwendung** (kurze Sessions, wenige Muster): 25–35 %
- **Moderate Verschwendung** (durchschnittlicher Nutzer): 40–50 %
- **Hohe Verschwendung** (lange Sessions, mehrere Muster): 50–65 %

### Always-On-Agents

| # | Muster | Tägliche Verschwendung | Tägliche Ersparnis |
|---|---|---|---|
| 13 | Idle Heartbeats | $11.20 | $9.70 |
| 14 | Workspace Bloat | $5.76 | $3.76 |
| 15 | Memory Accumulation | $3.17 | $2.37 |
| | **Gesamt** | **$20.13/Tag** | **$15.83/Tag** |

**Monatliche Ersparnis für Always-On-Agents: ~$475.**

---

## Unterstützte Tools

24+ Tools.

- **Vollständiger Session-Scan:** Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- **Erkennung + Instruktionsoptimierung:** Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

Alle LLMs: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, plus 40+ weitere.

macOS, Windows, Linux, iPad via SSH. Python 3.8+, keine Abhängigkeiten.

<details>
<summary>Methodik</summary>

Alle Kostenschätzungen verwenden das oben beschriebene Referenz-Szenario. Wichtige Annahmen:

- **90 % Prompt-Cache-Trefferrate** — typisch für schnelle Coding-Sessions. Langsamere Sessions haben höhere Kosten.
- **25 produktive Turns/Session** — verschwenderische Sessions fügen 8–12 extra Turns durch Narration, Retries und unkettete Befehle hinzu.
- **3.000 Tokens/Turn-Wachstum** — ausführliche Sessions können 4.000–5.000 erreichen.
- **Effektive Input-Rate: $0.57/1M** — gemischt 90 % gecacht ($0.30) + 10 % ungecacht ($3.00).
- **Context-Steuerrate: $0.30/1M** — gecachte Input-Rate für permanente context-Ergänzungen.

Schätzungen sind konservativ. Reale Einsparungen können Prognosen für Nutzer mit langen Sessions, großen Instruktionsdateien oder intensivem Debugging übertreffen.
</details>
