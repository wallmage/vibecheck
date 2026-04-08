# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Ogni turno della tua IA costa soldi.** Sonnet 4.6: $3/$15 per MTok (input/output). Opus 4.6: $5/$25 — 1,67x più costoso. Un turno a metà sessione su Sonnet costa ~$0.038. Quando l'IA dice "OK, ora sistemo questo" prima di sistemare — quei $0.031 sono spreco puro. E peggiora: ogni turno rilegge l'intera conversazione dall'inizio. Più lunga la conversazione, più costoso ogni turno. Questa è l'inflazione di contesto.

Gli strumenti di coding IA sprecano turni costantemente — narrare invece di agire, leggere i file uno alla volta, eseguire `git add` e `git commit` separatamente. vibecheck rileva 18 meccanismi su 4 livelli, li corregge con regole nel file di config e compressione, e monitora i miglioramenti. Riduce la tua bolletta del 40-65% secondo il tuo pattern di utilizzo. [Specifiche dettagliate →](SPECSHEET.md)

Supporta Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ strumenti. Esecuzione locale, i tuoi dati non lasciano mai il tuo computer.

## Come installare

Incolla questo nel tuo strumento di coding IA e premi Invio:

> Help me install this skill: https://github.com/wallmage/vibecheck

Fatto. La tua IA fa il resto.

<details>
<summary>Oppure installazione manuale da riga di comando</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Poi digita `/vibecheck scan` in qualsiasi sessione

Aggiornare: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Cos'è uno "skill"?

Uno skill è come una scheda ricetta per la tua IA. Non modifica la tua IA e non installa nulla. Le dà solo istruzioni — "come trovare pattern di spreco, spiegarli e correggerli." Rimovibile in qualsiasi momento.

### Strumenti di coding vs strumenti di chat

**Strumenti di coding** (Claude Code CLI, Cursor, Codex etc.): accesso diretto ai log. Scansione completa personalizzata.

**Strumenti chat/sandbox** (Cowork etc.): vedono i file di progetto ma non la cronologia chat.

1. **Senza scansione (80% del beneficio):** Ottimizza il file di config. Nessun accesso ai log necessario.
2. **Con scansione (100%):** Un comando nel terminale — solo gli ultimi 14 giorni (~20-50 MB).

### Permessi

Necessita accesso alla **cartella progetto** per leggere/editare il file di configurazione. Chiede prima di ogni modifica.

## Privacy

**I tuoi dati non lasciano mai il tuo computer.** Nessun server, nessuna API, nessuna telemetria. Codice completamente open source.

## Comandi

- `/vibecheck scan` — Educazione interattiva + diagnosi + correzioni
- `/vibecheck explain` — Solo educazione
- `/vibecheck compress` — Comprimi file di config (25-50%)
- `/vibecheck monitor` — Confronto settimanale + avvisi

## 18 meccanismi

**Livello 1 (70-80%):** Narrazione a vuoto, deterioramento contesto, debugging ping-pong
**Livello 2 (15-20%):** Output verboso, comandi non concatenati, esplorazione codebase, edit non raggruppati
**Livello 3 (5-10%):** Riletture, loop sleep/poll, retry falliti, ricerche schema, cerimonia Git
**Livello 4 — Agenti 24/7:** Heartbeat inattivi, bloat workspace, accumulo memoria

## Strumenti supportati

24+. Tutti i LLM: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7 e 40+ altri.

macOS, Windows, Linux, iPad/mobile via SSH. Python 3.8+, nessuna dipendenza esterna.
