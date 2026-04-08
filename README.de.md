# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Jeder Turn, den deine KI macht, kostet Geld.** Sonnet 4.6: $3/$15 pro Million Tokens (Input/Output). Opus 4.6: $5/$25 — 1,67-mal mehr. So sieht das in der Praxis aus:

- Deine KI sagt „OK, ich beheble das" bevor sie es tatsächlich tut. Dieser Narrations-Turn: **$0.017 verschwendet.** Reale Daten aus 428 Sessions: **$1.03 pro Session weg.**
- Dein Gespräch erreicht 74 Turns anstatt bei 20 aufgeteilt zu werden. Mehrkosten durch das Wiederlesen des gesamten Verlaufs: **$0.46 verschwendet.**
- `git add`, dann `git commit`, dann `git push` — drei Turns statt einem verketteten Befehl: **$0.044 verschwendet.**

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
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## Wie Turns Geld kosten

Bei jedem Turn liest deine KI das gesamte Gespräch erneut — System-Prompt, Instruktionsdatei, alle vorherigen Nachrichten, alle Tool-Ausgaben — und generiert dann eine Antwort.

**Turn-Kosten = Input-Tokens × Input-Rate + Output-Tokens × Output-Rate**

Frühe Turns sind günstig (kleiner context). Späte Turns sind teuer (alles davor wird neu gelesen). Deshalb summiert sich Verschwendung — ein verschwendeter Turn macht jeden zukünftigen Turn teurer, weil der verschwendete Inhalt im context verbleibt.

Prompt-Caching reduziert die Input-Kosten für bereits gesehene Inhalte um den Faktor 10. Die meisten Tools nutzen es automatisch.

**Abo-Nutzer:** Du siehst API-Preise nicht direkt, aber Verschwendung verbraucht dein Nachrichtenkontingent schneller. Claude Pro ($20/Monat) deckt ~$200 an API-Wert ab. Max ($200/Monat) deckt ~$4.000 ab.

<details>
<summary><strong>Recherche: Was dein Abo wirklich an Tokens wert ist</strong></summary>

### Wie ich das gemessen habe

Ich nutze den $200/Monat Claude 20x Max Plan und habe regelmäßig mein Kontingent aufgebraucht. Also wollte ich wissen: Wie viel API-Nutzung kauft man mit jedem Tier eigentlich?

Ich bin auf API-Abrechnung umgestiegen und habe über 100 Datenpunkte bei echtem Dollar-Verbrauch erfasst — nach jeder Aktion die Nutzung aktualisiert. Genug um die lineare Beziehung zwischen Abo-Preis und Token-Wert zu berechnen.

### Die Multiplikatoren

| Plan | Preis | API-Wert | Multiplikator | 5h-Fenster | Wöchentlich |
|---|---|---|---|---|---|
| Claude Pro | $20/Monat | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/Monat | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/Monat | ~$4,000 | 20x | $133.33 | $933.31 |

Nur das 20x Max Tier bietet tatsächlich einen höheren Multiplikator (20x vs. 10x bei den günstigeren Tiers).

### Reale Nutzungsdauer

- **$20 Claude Pro** — ernsthafte Arbeit (Entwicklung, Recherche, Schreiben) hält weniger als 1 Stunde, dann ist das 5h-Kontingent weg. Wöchentlich unter 7 Stunden insgesamt. Zu wenig für jeden Profi.
- **$100 5x Max** — man kann etwa 4 Stunden arbeiten, bevor das 5h-Fenster erreicht ist. 30-35 Stunden/Woche insgesamt. Für normale Nutzer gerade so ausreichend.
- **$200 20x Max** — für Leute die 80-100+ Stunden/Woche arbeiten, oft mit mehreren Sessions parallel.

### Warum Claude die Drittanbieter-Nutzung von Abos verboten hat

Diese Multiplikatoren erklären es. Bei 10-20x Nennwert kauft jeder Abo-Dollar weit mehr Rechenleistung als die API-Preise hergeben. Drittanbieter-Tools, die Abo-Kontingente mit API-äquivalenten Raten verbrauchen, machten das Geschäftsmodell unhaltbar.

### Die Codex-Alternative

Ich habe den Dollar-Wert von Codex noch nicht vollständig gemessen, aber im $20-Tier liefert Codex Plus ungefähr **3x so viel Coding-Nutzung** wie Claude Pro.

Warum: ChatGPT-Gespräche — auch GPT-5.4 Extended Thinking und Deep Research — zählen nicht gegen dein Codex-Kontingent. Allein das Coding ist 3x Claude Pro, und Pro-Chat gibt's kostenlos obendrauf.

**Wenn du nicht mindestens das Claude $100-Tier kaufen willst, hol dir stattdessen $20 Codex Plus.** 3x die Coding-Nutzung von Claude Pro, plus kostenloses GPT-5.4 Extended Thinking und Deep Research.

</details>

### Referenz-Szenario

Alle unten genannten Dollarbeträge verwenden diese Ausgangslage (Sonnet 4.6):

| Parameter | Wert |
|---|---|
| Session-Länge | 25 Turns |
| Startkontext | 21.000 Tokens |
| Wachstum pro Turn | ~600 Tokens |
| Cache-Trefferrate | 95 % |
| Mid-Session Turn-Kosten | $0.017 |
| Effiziente Session gesamt | $0.41 |

Für Opus 4.6 alle Kosten mit 1,67 multiplizieren.

---

## Die 15 Verschwendungsmuster

### Tier 1 — Die großen 3 (60–70 % der Verschwendung)

#### 1. Idle Narration

**Was es ist.** Die KI sagt „OK, ich beheble das" oder „Lass mich zuerst die Datei lesen" — und erledigt die eigentliche Arbeit erst im nächsten Turn. Der Narrations-Turn hat nichts getan: kein Tool-Aufruf, kein Code, kein Dateilesen.

**Die Verschwendung.** Jeder Narrations-Turn kostet **$0.017** (context-Wiederlesen + ~500 Tokens Statustext). Reale Daten aus 428 Sessions: **$1.03/Session — 30 % des gesamten Waste**. Bei 10 Sessions/Tag: **$10.30/Tag ($309/Monat)** nur für Narration.

**Der Fix.** vibecheck fügt hinzu: *„Kein Turn ohne Tool-Aufruf. Keine Narration. Im selben Turn denken und handeln."* Eliminiert Narration vollständig. **Spart ~$0.88/Session.**

#### 2. Context Rot

**Was es ist.** Lange Gespräche werden progressiv teurer. Turn 50 liest alle 49 vorherigen Turns neu. Die gesamten Session-Kosten wachsen quadratisch mit der Länge.

**Die Verschwendung.** Reale Daten aus 428 Sessions: **$0.46/Session — 13 %**. Eine 40-Turn-Session: **$0.70.** Zwei 20-Turn-Sessions (gleiche Arbeit): **$0.60.** Die Differenz — **$0.10** — kauft nichts. Bei 100 Turns: eine Session kostet **$2.53** vs. vier 25-Turn-Sessions zu **$1.64.** Das sind **$0.89 verschwendet** durch fehlendes Aufteilen.

**Der Fix.** Lehrt: *„/clear oder /compact zwischen unverwandten Aufgaben nutzen. Neue Gespräche starten."* **Spart ~$0.37/Session.**

#### 3. Ping-Pong-Debugging

**Was es ist.** Fixen, brechen, erneut versuchen, wieder brechen. Jeder fehlgeschlagene Versuch fügt Fehlerausgabe zum context hinzu (~4K Tokens pro Zyklus), die bei jedem zukünftigen Turn neu gelesen wird.

**Die Verschwendung.** Drei fehlgeschlagene Zyklen: 6 extra Turns ($0.102) + 12K Tokens toter Fehler ($0.036 context-Steuer). **Gesamt: ~$0.14 pro Episode.** Häufigkeit ~10 %. Reale Daten: **$0.015/Session**.

**Der Fix.** Fügt hinzu: *„Nach 2 fehlgeschlagenen Fixes an derselben Datei: stoppen, Fehler vollständig neu lesen, nachdenken, einziger gezielter Fix."* **Spart ~$0.01/Session.**

### Tier 2 — Turn-Dichte (15–20 % der Verschwendung)

#### 4. Verbose Tool Output

**Was es ist.** Build/Test-Befehl gibt 500 Zeilen (~5K Tokens) ins Gespräch aus. Diese Tokens werden bei jedem zukünftigen Turn neu gelesen.

**Die Verschwendung.** 5K Tokens × 12 verbleibende Turns × $0.30/1M = **$0.018/Instanz** context-Steuer. Passiert 2–3 Mal/Session. Ohne Caching: **$0.180/Instanz** — 10-mal schlechter. Reale Daten: **$1.05/Session** — 31 % des gesamten Waste.

**Der Fix.** Fügt hinzu: *„Build/Test-Output nach /tmp/ pipen, --quiet-Flags nutzen, tail -50 max."* **Spart ~$0.89/Session.**

#### 5. Unchained Commands

**Was es ist.** `npm install` in einem Turn, `npm run build` im nächsten. Zwei context-Wiederlesungen, wenn `&&` sie in einem verkettet.

**Die Verschwendung.** Jede Aufteilung: **$0.010.** Typische Sessions haben 3–4 Aufteilungen. Reale Daten: **$0.14/Session**.

**Der Fix.** Fügt hinzu: *„Befehle mit `&&` verketten, wo sicher."* **Spart ~$0.11.**

#### 6. Codebase Wandering

**Was es ist.** Die KI öffnet Datei für Datei — README, package.json, Configs — bevor sie irgendwas tut. Fünf oder mehr aufeinanderfolgende Lesevorgänge vor der ersten Bearbeitung.

**Die Verschwendung.** Fünf unnötige Lesevorgänge: $0.085 in Turns + $0.027 context-Steuer = **$0.112/Episode.** Reale Daten: **$0.09/Session**.

**Der Fix.** Fördert gezieltes Suchen (grep/glob zuerst), mehrere Lesevorgänge pro Turn bündeln. **Spart ~$0.07.**

#### 7. Unbatched Edits

**Was es ist.** Datei A bearbeiten, dann B, dann C — drei Turns, wenn ein Turn mit parallelen Bearbeitungen genügen würde.

**Die Verschwendung.** 2 extra Turns × $0.017 = **$0.034/Instanz.** Reale Daten: **$0.058/Session**.

**Der Fix.** Fügt hinzu: *„Unabhängige Tool-Aufrufe bündeln (mehrere Reads/Edits pro Turn)."* **Spart ~$0.05.**

### Tier 3 — Der Schwanz (5–10 % der Verschwendung)

#### 8. File Re-reads

**Was es ist.** Dieselbe Datei zweimal in einer Session gelesen. Der Inhalt ist nach dem ersten Lesen bereits im context.

**Die Verschwendung.** 1 verschwendeter Turn + doppelter Inhalt = **$0.019/Wiederlesen.** Reale Daten: **$0.066/Session**.

**Der Fix.** Fügt hinzu: *„Inhalt ist nach erstem Lesen im context. Nur erneut lesen, wenn Datei geändert wurde."* **Spart ~$0.05.**

#### 9. Sleep/Poll Loops

**Was es ist.** `sleep 5 && check_status`, 3–5 Mal wiederholt. Jede Abfrage liest den gesamten context neu.

**Die Verschwendung.** 4 Abfragen × $0.017 = **$0.068/Episode.** Reale Daten: **$0.043/Session**.

**Der Fix.** Fügt hinzu: *„--wait-Flags oder run_in_background nutzen."* **Spart ~$0.034.**

#### 10. Failed Retries

**Was es ist.** Befehl schlägt fehl, KI führt exakt denselben Befehl erneut aus. Fehlerausgabe jetzt zweimal im context.

**Die Verschwendung.** **$0.019/Retry.** Reale Daten: **$0.080/Session**.

**Der Fix.** Gleiche Regel wie bei Ping-Pong: *„Stoppen, Fehler neu lesen, nachdenken, einziger gezielter Fix."*

#### 11. Schema Lookups

**Was es ist.** KI schlägt eigene Tool-Definitionen nach — Informationen, die sie bereits hat. Fügt 2K+ Tokens zum context hinzu.

**Die Verschwendung.** **$0.023/Lookup.** Reale Daten: **$0.023/Session**.

**Der Fix.** „Kein Turn ohne Tool-Aufruf" entmutigt Discovery-Turns. **Spart ~$0.02.**

#### 12. Git Ceremony

**Was es ist.** `git add` → `git status` → `git commit` → `git push`, vier Turns. `git add -A && git commit -m "msg" && git push` ist einer.

**Die Verschwendung.** 3 extra Turns + Git-Output = **$0.044/Instanz.** Reale Daten: **$0.003/Session**.

**Der Fix.** Fügt hinzu: *„Git-Befehle mit `&&` verketten."* **Spart ~$0.003.**

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

Eine 10K-Token-Datei, auf 6K komprimiert, spart $0.044/Session. Bei 10 Sessions/Tag: **$0.44/Tag ($13/Monat).**

### Output-Unterdrückung

Output-Tokens kosten 5-mal so viel wie Input ($15 vs. $3/MTok bei Sonnet). Die KI zeigt vollständige Code-Blöcke und Diffs, die du nicht angefordert hast, und verschwendet damit **~$0.047/Session.** vibecheck fügt hinzu: *„Kein Code/keine Diffs, außer wenn angefordert."*

### Kosten-Monitoring

`/vibecheck monitor` erstellt einen Snapshot deines Session-Profils und vergleicht ihn bei nachfolgenden Ausführungen mit dem Basiswert. Erkennt Regressionen, bevor sie Geld kosten.

---

## Einsparungs-Zusammenfassung

### Interaktive Tools (Sonnet 4.6)

| # | Muster | Durchschn. Verschwendung/Session | Durchschn. Ersparnis |
|---|---|---|---|
| 1 | Idle Narration | $1.03 | $0.88 |
| 2 | Context Rot | $0.46 | $0.37 |
| 3 | Ping-Pong-Debugging | $0.015 | $0.01 |
| 4 | Verbose Output | $1.05 | $0.89 |
| 5 | Unchained Commands | $0.14 | $0.11 |
| 6 | Codebase Wandering | $0.09 | $0.07 |
| 7 | Unbatched Edits | $0.058 | $0.05 |
| 8 | File Re-reads | $0.066 | $0.05 |
| 9 | Sleep/Poll Loops | $0.043 | $0.034 |
| 10 | Failed Retries | $0.08 | $0.06 |
| 11 | Schema Lookups | $0.023 | $0.02 |
| 12 | Git Ceremony | $0.003 | $0.003 |
| + | Komprimierung | $0.044 | $0.044 |
| + | Output-Unterdrückung | $0.047 | $0.038 |
| | **Gesamt** | **$3.15*** | **$2.61** |

*Einzelne Muster können sich im selben Turn überlappen — Summen spiegeln Einzelmuster-Messung wider. Tatsächliche Gesamtersparnis: $3.07 → $0.46 (siehe Fazit).

**Typische verschwenderische Session: $3.07. Nach vibecheck: $0.46. Ersparnis: 85 %.**

- **Geringe Verschwendung** (kurze Sessions, wenige Muster): 40–55 %
- **Moderate Verschwendung** (durchschnittlicher Nutzer): 55–70 %
- **Hohe Verschwendung** (lange Sessions, mehrere Muster): 70–85 %

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

- **95 % Prompt-Cache-Trefferrate** — typisch für schnelle Coding-Sessions. Langsamere Sessions haben höhere Kosten.
- **25 produktive Turns/Session** — verschwenderische Sessions fügen 8–12 extra Turns durch Narration, Retries und unkettete Befehle hinzu.
- **600 Tokens/Turn-Wachstum** — ausführliche Sessions können 1.000–2.000 erreichen.
- **Effektive Input-Rate: $0.435/1M** — gemischt 95 % gecacht ($0.30) + 5 % ungecacht ($3.00).
- **Context-Steuerrate: $0.30/1M** — gecachte Input-Rate für permanente context-Ergänzungen.

Schätzungen sind konservativ. Reale Einsparungen können Prognosen für Nutzer mit langen Sessions, großen Instruktionsdateien oder intensivem Debugging übertreffen.
</details>
