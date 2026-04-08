# vibecheck

[![GitHub stars](https://img.shields.io/github/stars/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/watchers)
[![GitHub last commit](https://img.shields.io/github/last-commit/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Top language](https://img.shields.io/github/languages/top/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Privacy](https://img.shields.io/badge/privacy-local%20only-111827?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Coverage](https://img.shields.io/badge/coverage-24%2B%20tools-0f766e?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Linux%20%7C%20Windows-4f46e5?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Focus](https://img.shields.io/badge/focus-cost%20optimization-b45309?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20%7C%20Codex%20%7C%20Gemini-2563eb?style=flat-square)](https://github.com/wallmage/vibecheck)

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | Deutsch | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

Mein Claude-Kontingent war regelmäßig am frühen Nachmittag aufgebraucht und ich konnte mir nicht erklären, warum. Es stellte sich heraus: 70 % meiner AI-Coding-Sessions waren reine Verschwendung — die KI hat angekündigt, was sie gleich tun würde, Befehle über drei Turns verteilt, die in einen gepasst hätten, und veralteter Kontext hat sich aufgestapelt und wurde bei jedem einzelnen Turn erneut eingelesen.

vibecheck findet diese Verschwendung. Es liest deine tatsächlichen Session-Logs aus 24+ Coding-Tools, berechnet die Kosten für 15 spezifische Muster und behebt sie. Alles läuft lokal. Kein Upload, keine Telemetrie, keine Server.

In meinem Fall: Die monatlichen Kosten sanken von $2,816 auf $422. **85 % Einsparung.**

## Installation

Füge das in dein AI-Coding-Tool ein und drücke Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

Fertig. Deine KI übernimmt den Skill und du kannst scannen.

<details>
<summary>Oder manuell über die Kommandozeile installieren</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Dann `/vibecheck scan` in einer beliebigen Session eingeben.

Update: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Was genau ist ein „Skill"?

Eine reine Textdatei, die deiner KI etwas Neues beibringt. Keine Binärdateien, keine Hintergrundprozesse, keine Systemänderungen. Die Skill-Datei von vibecheck sagt: „So findest du Verschwendung und behebst sie." Lösche den Ordner und sie ist weg.

### Coding-Tools vs. Chat-Tools

**Coding-Tools** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder usw.) laufen auf deinem Rechner und hinterlassen Session-Logs. vibecheck erkennt automatisch, welche installiert sind, und scannt die Logs direkt.

**Chat-Tools** (Cowork, browserbasiertes Claude) laufen in einer Sandbox ohne lokale Logs. vibecheck optimiert trotzdem deine Instruktionsdateien — der Großteil der Einsparungen kommt ohnehin daher. Alternativ kannst du einen Terminal-Befehl einfügen, um 14 Tage an Logs für einen vollständigen Scan zu exportieren.

### Berechtigungen

vibecheck liest deine lokalen Session-Logs und prüft Instruktionsdateien (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) sowie maschinenweite Tool-Einstellungen. Wenn dein Tool eine globale Konfiguration hat — eine Datei für alle Projekte — geht der Optimierer dort zuerst hin, denn eine Korrektur spart dir überall Geld. Vor jeder Änderung wird gefragt.

## Datenschutz

Alles bleibt auf deinem Rechner. Die Analyse besteht aus Python-Skripten, die deine lokalen Session-Logs parsen. Kein Server, keine API-Aufrufe, keine Analytics. Open Source — du kannst jede Zeile lesen.

## Befehle

| Befehl | Funktion |
|---|---|
| `/vibecheck scan` | Scannt alle erkannten Tools auf deinem Rechner. Ein einheitlicher Bericht mit Gesundheitsindikatoren, Ranking-Statistiken, Top-Verschwendungsmustern und Optimierungs-Roadmap |
| `/vibecheck explain` | Erklärt die Verschwendungsmuster, ohne etwas zu ändern. Reines Lernen |
| `/vibecheck compress` | Komprimiert deine Instruktionsdateien um 25-50 % mit einem 4-Pass-verlustfreien Kompressor |
| `/vibecheck monitor` | Wöchentlicher Vergleich mit deiner Baseline. Erkennt Kostenrückfälle, bevor sie sich summieren |

Der Scan läuft unauffällig: ein kompakter Fortschrittsindikator, dann eine saubere Zusammenfassung. `Good` bedeutet gemessene Verschwendung unter 10 %, `Waste` bedeutet darüber. Rohe Logs und Tool-Ausgaben bleiben im Hintergrund, es sei denn, etwas geht schief.

### Sessions frisch halten

Lange Gespräche kosten mehr als kurze — jeder neue Turn liest alle alten erneut ein, und überladener Kontext macht die KI ungenauer, was zu mehr Hin-und-Her führt.

Faustregel: 5-10 aktive Minuten pro Session, 30-40 Turns, bevor die Kontext-Steuer richtig zuschlägt. Bei einer neuen Session gehören dauerhafte Regeln in Instruktionsdateien (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) und Projekthintergrund in kleine lokale Dokumente. Neue Session heißt nicht Kaltstart — nur ein sauberer Kontext, in dem dein gesamtes Wissen noch vorhanden ist.

---

## Vorher / Nachher

Gemessen über reale Sessions:

```
                          BEFORE         NOW            CHANGE
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## Wie AI-Turns Geld kosten

Eine kurze Einführung für alle, die sich noch nie mit Token-Ökonomie beschäftigt haben. Kein Vorwissen zu AI-Preisen nötig.

### Was bei jedem Turn passiert

Jedes Mal, wenn deine KI antwortet, liest sie die gesamte Konversation von vorne ein. Systemprompt, Instruktionsdatei, jede Nachricht von dir, jede Antwort der KI, alle Tool-Ausgaben — Dateiinhalte, Terminal-Ergebnisse, Fehlerprotokolle — alles. Dann generiert sie eine neue Antwort.

**Turn-Kosten = gelesene Tokens x Eingabepreis + generierte Tokens x Ausgabepreis**

Frühe Turns sind günstig. Turn 1 liest vielleicht 5.000 Tokens. Bei Turn 40 werden 40.000+ Tokens der angesammelten Konversation erneut gelesen — jede vorherige Nachricht, jedes Code-Snippet, jeder Error-Trace. Dieser späte Turn kostet das 8-fache des ersten.

Das Problem: Verschwendung **akkumuliert sich**. Ein verschwendeter Turn kostet nicht nur seine eigenen Tokens. Er bleibt im Kontext und wird für den Rest der Session bei jedem zukünftigen Turn erneut gelesen. Eine überflüssige Narrations-Nachricht bei Turn 10 wird bis zum Ende noch 30 weitere Male erneut gelesen.

### Prompt-Caching hilft, löst das Problem aber nicht

Die meisten Anbieter cachen inzwischen bereits gesehene Inhalte und berechnen das 10-fache weniger dafür. Der effektive Eingabepreis sinkt von $3.00/Million Tokens auf $0.30/Million.

Das hilft. Aber neue Inhalte — frische Tool-Ausgaben, neue Fehlermeldungen, jede neue KI-Antwort — werden immer zuerst zum vollen Preis eingelesen. Und Verschwendung akkumuliert sich auch zum gecacheten Tarif.

### Abonnements haben dasselbe Problem

Wer ein Abo hat, denkt vielleicht, API-Preise spielen keine Rolle. Tun sie — man spürt es nur anders. Abonnements kaufen einen festen Compute-Pool, und Verschwendung verbraucht diesen Pool schneller. Wenn du um 15 Uhr dein Kontingent erreichst und gedrosselt wirst, liegt es nicht daran, dass du zu viel gearbeitet hast — sondern daran, dass vieles davon Verschwendung war.

Claude Pro ($20/Monat) deckt ungefähr $200 an API-Gegenwert ab. Claude 20x Max ($200/Monat) deckt ungefähr $4,000 ab. Mehr Verschwendung = schneller an der Grenze.

<details>
<summary><strong>Deep Dive: Was dein Abo tatsächlich in Tokens wert ist</strong></summary>

### Wie ich gemessen habe

Ich hatte den $200/Monat Claude 20x Max Plan und lief ständig ins Kontingent. Neugierig geworden, wechselte ich zur API-Abrechnung und verfolgte die realen Kosten über 100+ Datenpunkte — jede Coding-Aktivität protokolliert, Verbrauch direkt danach geprüft. So konnte ich das Verhältnis zwischen Abo-Preis und tatsächlichem Token-Wert ermitteln.

### Die Multiplikatoren

| Plan | Preis | API-Wert | Multiplikator | 5h-Fenster | Wöchentlich gesamt |
|---|---|---|---|---|---|
| Claude Pro | $20/Monat | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/Monat | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/Monat | ~$4,000 | 20x | $133.33 | $933.31 |

Der 20x Max Tarif ist der einzige mit echtem Multiplikator-Sprung — 20-facher Nennwert statt 10-fach bei den niedrigeren Tarifen.

### Was das in der Praxis bedeutet

- **$20 Claude Pro** — ernsthafte Entwicklungsarbeit (Features bauen, Recherche, Dokumentation) verbraucht das 5-Stunden-Kontingent in unter einer Stunde. Wöchentliche Kapazität unter 7 Stunden. Eng für jede professionelle Nutzung.
- **$100 5x Max** — ca. 4 Stunden bis zum 5-Stunden-Fenster. 30-35 Stunden/Woche gesamt. Ausreichend für reguläre Nutzung.
- **$200 20x Max** — für Leute, die 80-100+ Stunden/Woche arbeiten und oft mehrere Sessions parallel laufen lassen.

### Warum Anthropic die Nutzung von Drittanbieter-Abos eingeschränkt hat

Bei 10-20-fachem Nennwert kauft jeder Abo-Dollar weit mehr Compute als der API-Tarif hergibt. Drittanbieter-Tools, die das in API-äquivalenter Geschwindigkeit verbrauchen, machten die Rechnung nicht mehr tragfähig.

### Die Codex-Alternative

Beim $20-Tarif liefert Codex Plus etwa **3x so viel Coding-Nutzung** wie Claude Pro. ChatGPT-Konversationen — selbst GPT-5.4 Extended Thinking und Deep Research — zählen nicht gegen das Codex-Coding-Kontingent. Du bekommst also 3x Coding-Kapazität plus kostenloses GPT-5.4 obendrauf.

**Bei $20/Monat Budget bietet Codex Plus mehr Coding-Zeit als Claude Pro.** Wer mehr ausgeben kann: die Claude 5x und 20x Tarife bieten ein anderes Wertversprechen.

</details>

### Referenzszenario

Alle Beträge in diesem Dokument basieren auf diesem Szenario (Sonnet 4.6 Preise):

| Parameter | Wert |
|---|---|
| Session-Länge | 25 Turns |
| Start-Kontext | 21,000 Tokens |
| Wachstum pro Turn | ~600 Tokens |
| Cache-Trefferquote | 95 % |
| Kosten pro Turn (Session-Mitte) | $0.017 |
| Effiziente Session gesamt | $0.41 |

Für Opus 4.6 alle Kosten mit 1,67x multiplizieren.

---

## Die 15 Verschwendungsmuster

Sortiert nach Kostenauswirkung. Die drei größten allein machen 60-70 % der gesamten Verschwendung aus.

### Tier 1 — Die großen Drei (60-70 % der Verschwendung)

#### 1. Leerlauf-Narration

Die KI sagt „OK, das korrigiere ich jetzt" oder „Lass mich die Datei zuerst lesen" — und arbeitet erst im nächsten Turn. Dieser Narrations-Turn hat nichts geleistet. Kein Tool-Aufruf, kein Code, kein Dateilesen. Nur eine Ankündigung.

Jeder kostet ca. **$0.017** — und schlimmer: die 300-500 Tokens Statustext bleiben im Kontext und werden bei jedem zukünftigen Turn erneut gelesen. Über 428 gemessene Sessions: **$1.03/Session Verschwendung**, 30 % der Gesamtverschwendung. Bei 10 Sessions/Tag: **$309/Monat allein für Narration.**

vibecheck-Regel: *„Kein Turn ohne Tool-Aufruf. Denken und Handeln im selben Turn."* **Spart ca. $0.88/Session.**

#### 2. Kontext-Verfall

Session-Kosten wachsen quadratisch, nicht linear. Turn 50 liest alle 49 vorherigen Turns erneut.

Konkreter Vergleich: Eine 40-Turn-Session kostet **$0.70**. Dieselbe Arbeit auf zwei 20-Turn-Sessions verteilt: **$0.60**. Die $0.10 Differenz ist reine Verschwendung durch eine aufgeblähte Konversation. Reale Sessions haben durchschnittlich 74 Turns — **$0.46/Session Verschwendung**, 13 % der Gesamtverschwendung.

vibecheck lehrt: *„Unabhängige Arbeiten in separate Sessions. In langen Threads kompakt bleiben."* **Spart ca. $0.37/Session.**

#### 3. Pingpong-Debugging

Fix, kaputt, nochmal, wieder kaputt. Jeder fehlgeschlagene Versuch pumpt ~4.000 Tokens Fehlerausgabe in den Kontext, und dieser tote Text wird bei jedem weiteren Turn erneut gelesen. Drei Zyklen: 6 Extra-Turns ($0.102) + 12K Tokens veralteter Fehler ($0.036) = **ca. $0.14 pro Episode**. Tritt in ~10 % der Sessions auf. **Gewichtet: $0.015/Session.**

vibecheck-Sicherung: *„Nach 2 fehlgeschlagenen Fixes derselben Datei — stoppen, die vollständige Fehlermeldung lesen, nachdenken, ein gezielter Fix."* **Spart ca. $0.01/Session.**

### Tier 2 — Turn-Dichte (15-20 % der Verschwendung)

In drei Turns erledigen, was in einem hätte sein können.

#### 4. Verbose Tool-Ausgabe

Ein Build- oder Test-Befehl wirft 500 Zeilen (~5.000 Tokens) in die Konversation. Diese Tokens werden für den Rest der Session bei jedem Turn erneut gelesen. 5K Tokens x 12 verbleibende Turns zum gecacheten Tarif = **$0.018/Instanz**. Ohne Caching: **$0.180** — 10x schlimmer.

Das ist tatsächlich das teuerste Einzelmuster in der Messung. Build-Logs, npm-Ausgaben, Test-Dumps — sie überschwemmen fast jede Session. **$1.05/Session**, 31 % der Gesamtverschwendung.

Fix: *„Ausgabe nach /tmp/ pipen. --quiet-Flags verwenden. Maximal tail -50."* **Spart ca. $0.89/Session.**

#### 5. Nicht verkettete Befehle

`npm install` in einem Turn. `npm run build` im nächsten. Zwei Kontext-Neulesungen für das, was `npm install && npm run build` in einem Turn erledigt. Jede Aufteilung: **$0.010**. Summiert sich auf **$0.14/Session** in befehlsintensiven Sessions.

Fix: *„Befehle mit `&&` verketten, wenn sicher."* **Spart ca. $0.11/Session.**

#### 6. Codebase-Wanderung

Die KI öffnet README, package.json, drei Configs und zwei unbeteiligte Module, bevor sie eine einzige Zeile Code schreibt. Fünf aufeinanderfolgende Lesevorgänge, keine Edits, keine Entscheidungen. $0.085 verschwendete Turns + $0.027 Kontext-Steuer = **$0.112/Episode.** Durchschnitt: **$0.09/Session.**

Fix: Erst grep oder glob, nur Relevantes lesen, mehrere Lesevorgänge pro Turn bündeln. **Spart ca. $0.07/Session.**

#### 7. Nicht gebatchte Edits

Datei A bearbeiten, dann B, dann C — drei Turns. Ein Turn mit parallelen Edits erledigt dasselbe. Zwei Extra-Turns à $0.017 = **$0.034/Instanz.** Durchschnitt: **$0.058/Session.**

Fix: *„Unabhängige Tool-Aufrufe bündeln."* **Spart ca. $0.05/Session.**

### Tier 3 — Der Schwanz (5-10 % der Verschwendung)

Einzeln klein. In Summe relevant.

#### 8. Datei-Neulesungen

Dieselbe Datei zweimal in einer Session gelesen — Inhalt bereits im Kontext, aber die KI liest sie nochmal. **$0.019/Neulesung**, Dateien werden durchschnittlich 3-4 Mal erneut gelesen. **$0.066/Session.** Fix: *„Bereits im Kontext. Nur bei Dateiänderung erneut lesen."* **Spart ca. $0.05/Session.**

#### 9. Sleep/Poll-Schleifen

`sleep 5 && check_status`, 3-5 Mal wiederholt. Jeder Poll = vollständige Kontext-Neulesung, um zu prüfen, ob ein Hintergrundprozess fertig ist. 4 Polls x $0.017 = **$0.068/Episode**, **$0.043/Session.** Fix: *„--wait oder run_in_background verwenden."* **Spart ca. $0.034/Session.**

#### 10. Fehlgeschlagene Wiederholungen

Befehl schlägt fehl, KI führt denselben Befehl unverändert erneut aus. Fehlerausgabe ist nun zweimal im Kontext. **$0.019/Wiederholung**, **$0.080/Session.** Fix: wie bei Pingpong — *„Stoppen, Fehler lesen, etwas anderes versuchen."*

#### 11. Schema-Abfragen

Die KI ruft ihre eigenen Tool-Definitionen ab — Informationen, die sie bereits hat. Fügt 2K+ Tokens umsonst hinzu. **$0.023/Session.** Die „Kein Turn ohne Tool-Aufruf"-Regel löst das. **Spart ca. $0.02/Session.**

#### 12. Git-Zeremonie

`git add` → `git status` → `git commit` → `git push`. Vier Turns. `git add -A && git commit -m "msg" && git push` ist einer. **$0.044/Instanz**, aber seltener als gedacht — **$0.003/Session.** Fix: mit `&&` verketten.

### Tier 4 — Always-On-Agents

Anderes Kostenmodell. Agents wie OpenClaw wachen periodisch auf, und Verschwendung wird pro Tag gemessen, nicht pro Session.

#### 13. Leerlauf-Heartbeats

Agent wacht alle 5 Minuten auf, liest den gesamten Workspace neu, findet nichts, schläft wieder ein. 288 Aufwachvorgänge/Tag, ~97 % im Leerlauf. Das sind 280 Leerlauf-Wakes à $0.04 = **$11.20/Tag ($336/Monat)** für nichts.

Fix: *„Mindestens 30 Minuten Heartbeat. Überspringen wenn keine Trigger anstehen."* Reduziert auf ~48 Wakes/Tag. **Spart $8-10/Tag ($240-300/Monat).**

#### 14. Workspace-Aufblähung

35.000 Tokens an Persönlichkeitsdateien (SOUL.md, AGENTS.md usw.) werden bei jedem Aufwachen erneut gelesen. Tutorials, Coaching, Philosophie — für Menschen geschrieben, nicht für eine KI, die Aufgaben ausführt. **$5.76/Tag ($173/Monat)** allein für Konfigurationsdateien.

vibecheck komprimiert sie: 35K → 12-15K Tokens. Dieselben Verhaltensregeln, kein menschengerichteter Fülltext. **Spart $3-4/Tag ($90-120/Monat).**

#### 15. Speicher-Akkumulation

Session-Verlauf wächst endlos. 100+ Speichereinträge werden bei jedem Aufwachen erneut gelesen, darunter Dinge von vor Wochen, die nicht mehr relevant sind. **$3.17/Tag ($95/Monat)** für veraltete Erinnerungen.

Fix: *„Nach 50 Einträgen archivieren, zusammenfassen, neu anfangen."* **Spart $2-3/Tag ($60-90/Monat).**

---

## Das Optimierungs-Toolkit

vibecheck zeigt nicht nur Probleme auf — es behebt sie.

### Instruktionsdatei-Komprimierung

Deine Instruktionsdatei (`CLAUDE.md`, `AGENTS.md`, `Memory.md`, wie auch immer dein Tool sie nennt) wird bei jedem einzelnen Turn gelesen. Eine fixe Steuer auf alles, was du tust. Eine aufgeblähte Instruktionsdatei ist eine Mautstelle an jeder Straße der Stadt.

vibecheck hat einen 4-Pass verlustfreien Kompressor — 23 Techniken, und „verlustfrei" bedeutet buchstäblich: keine Fakten werden entfernt. Gleiche Information, weniger Tokens.

| Pass | Funktion | Einsparung |
|---|---|---|
| **Pass 1 — Mechanisch** | Entfernt Markdown-Formatierung, konvertiert Tabellen in kompakte Form, fasst Aufzählungen zusammen | 10-15 % |
| **Pass 2 — Faktenerhaltend** | Dedupliziert wiederholte Fakten, komprimiert Code-Beispiele, klappt ausführliche Beschreibungen ein | 15-25 % |
| **Pass 3 — Hohe Treue** | Entfernt Tutorials und Coaching-Texte, die Menschen brauchen, die KI aber nicht | 10-15 % |
| **Pass 4 — Telegramm** | Vollständige Kurzschrift-Umschreibung für reine KI-Dateien. Dicht, komprimiert — nur mit deiner ausdrücklichen Genehmigung | 15-25 % |

Eine 10.000-Token-Instruktionsdatei auf 6.000 komprimiert spart $0.044 pro Session. Bei 10 Sessions pro Tag: **$0.44/Tag ($13/Monat)** allein durch Komprimierung.

### Ausgabe-Unterdrückung

Ausgabe-Tokens kosten das 5-fache von Eingabe-Tokens ($15 vs. $3/Million bei Sonnet 4.6). Die KI gibt vollständige Code-Blöcke oder Diffs aus, die du nicht angefordert hast? Teuer. vibecheck ergänzt: *„Kein Code oder Diffs, sofern nicht angefragt."* **Spart ca. $0.047/Session.**

### Kosten-Monitoring

`/vibecheck monitor` erstellt einen Snapshot deines Session-Profils und vergleicht bei zukünftigen Läufen mit der Baseline. Neue Instruktionsdatei hat Verbosität eingeführt? Anderes Projekt, andere Gewohnheiten? Der Monitor erkennt Rückfälle, bevor sie sich summieren.

---

## Einspar-Übersicht

### Interaktive Tools (Sonnet 4.6 Preise)

| # | Muster | Ø Verschwendung/Session | Ø Einsparung |
|---|---|---|---|
| 1 | Leerlauf-Narration | $1.03 | $0.88 |
| 2 | Kontext-Verfall | $0.46 | $0.37 |
| 3 | Pingpong-Debugging | $0.015 | $0.01 |
| 4 | Verbose Ausgabe | $1.05 | $0.89 |
| 5 | Nicht verkettete Befehle | $0.14 | $0.11 |
| 6 | Codebase-Wanderung | $0.09 | $0.07 |
| 7 | Nicht gebatchte Edits | $0.058 | $0.05 |
| 8 | Datei-Neulesungen | $0.066 | $0.05 |
| 9 | Sleep/Poll-Schleifen | $0.043 | $0.034 |
| 10 | Fehlgeschlagene Wiederholungen | $0.08 | $0.06 |
| 11 | Schema-Abfragen | $0.023 | $0.02 |
| 12 | Git-Zeremonie | $0.003 | $0.003 |
| + | Komprimierung | $0.044 | $0.044 |
| + | Ausgabe-Unterdrückung | $0.047 | $0.038 |
| | **Gesamt** | **$3.15*** | **$2.61** |

*Einzelne Muster können im selben Turn gleichzeitig auftreten — Gesamtwerte spiegeln Einzelmuster-Messungen wider. Tatsächliches Aggregat: $3.07 auf $0.46 (siehe Vorher / Nachher).

**Typische verschwenderische Session: $3.07. Nach vibecheck: $0.46. Einsparung: 85 %.**

- **Geringe Verschwendung** (kurze Sessions, wenige Muster): 40-55 % Reduktion
- **Mittlere Verschwendung** (durchschnittlicher Nutzer): 55-70 % Reduktion
- **Hohe Verschwendung** (lange Sessions, mehrere Muster): 70-85 % Reduktion

### Always-On-Agents

| # | Muster | Tägliche Verschwendung | Tägliche Einsparung |
|---|---|---|---|
| 13 | Leerlauf-Heartbeats | $11.20 | $9.70 |
| 14 | Workspace-Aufblähung | $5.76 | $3.76 |
| 15 | Speicher-Akkumulation | $3.17 | $2.37 |
| | **Gesamt** | **$20.13/Tag** | **$15.83/Tag** |

**Monatliche Einsparung für Always-On-Agents: ca. $475.**

---

## Unterstützte Tools

24+ Tools. Kein Lock-in — vibecheck ist eine Textdatei, jede KI, die Instruktionen liest, kann sie verwenden. Die Scan-Skripte sind reines Python ohne Abhängigkeiten.

**Vollständiger Session-Scan** (liest deine Logs, berechnet Kosten pro Verschwendung):
Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity

**Erkennung + Instruktions-Optimierung** (noch kein vollständiges Log-Parsing, aber erkennt das Tool und optimiert deine Konfigurationsdateien):
Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

**LLMs mit Preisdaten:** Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, plus 40+ weitere.

**Plattformen:** macOS, Windows, Linux, iPad via SSH. Python 3.8+.

---

<details>
<summary><strong>Methodik</strong></summary>

Alle Kostenschätzungen verwenden das obige Referenzszenario. Zentrale Annahmen:

- **95 % Prompt-Cache-Trefferquote** — typisch für schnelle Coding-Sessions. Bei langsameren Sessions mit längeren Pausen zwischen Turns sinkt die Cache-Trefferquote und die Kosten steigen.
- **25 produktive Turns/Session** — verschwenderische Sessions erzeugen 8-12 zusätzliche Turns durch Narration, Wiederholungen und nicht verkettete Befehle.
- **600 Tokens/Turn Wachstum** — verbose Sessions können 1.000-2.000 Tokens pro Turn erreichen.
- **Effektiver Eingabetarif: $0.435/1M** — gewichteter Tarif aus 95 % gecacht ($0.30/1M) + 5 % ungecacht ($3.00/1M).
- **Kontext-Steuersatz: $0.30/1M** — gecacheter Eingabetarif für permanente Kontext-Ergänzungen.

Konservative Schätzungen. Reale Einsparungen übertreffen diese häufig — besonders bei langen Sessions, großen Instruktionsdateien oder intensivem Debugging.
</details>

## Autor

[Wallny](https://github.com/wallmage)
