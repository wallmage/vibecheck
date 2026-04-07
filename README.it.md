# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Il tuo strumento di coding IA sta bruciando soldi che non vedi.**

Ogni messaggio che invii, la tua IA rilegge *tutta* la conversazione dall'inizio. Il messaggio #50 costa 50 volte il #1. Quella narrazione "OK, ora sistemo questo"? Ti è costata soldi senza fare nulla. Quelle 500 righe di log? Rilette ad ogni futuro messaggio.

La maggior parte dei vibe coder spreca **oltre il 50%** del proprio budget token senza saperlo.

vibecheck risolve il problema. Scansiona gli ultimi 14 giorni, trova lo spreco, lo spiega in linguaggio semplice, e applica correzioni di un paragrafo. Stesso lavoro. Metà costo.

**Risparmio medio: 50%+ della tua bolletta token.** Supporta tutti i modelli LLM (Claude, GPT, Gemini, DeepSeek). Funziona con Claude Code, OpenClaw, Codex, OpenCode, Cursor, Windsurf e 24+ strumenti. 100% locale — i tuoi dati non lasciano mai il tuo computer.

## Inizia subito — niente da scaricare

vibecheck è uno **skill** — un insieme di istruzioni che il tuo strumento di coding IA impara. Non scarichi né installi nessun software. Dai un link alla tua IA e impara da sola a ottimizzare i tuoi costi. Un messaggio e basta.

**Copia questo nel tuo strumento di coding IA** (Claude Code, Cursor, Codex, Windsurf, Cline):

> Installa lo skill vibecheck da https://github.com/wallmage/vibecheck e lancia /vibecheck scan

Tutto qui. La tua IA legge lo skill, scansiona 14 giorni e ti spiega tutto.

**Oppure da CLI:**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

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

## 15 pattern di spreco

**Livello 1 (70-80%):** Narrazione a vuoto, deterioramento contesto, debugging ping-pong
**Livello 2 (15-20%):** Output verboso, comandi non concatenati, esplorazione codebase, edit non raggruppati
**Livello 3 (5-10%):** Riletture, loop sleep/poll, retry falliti, ricerche schema, cerimonia Git
**Livello 4 — Agenti 24/7:** Heartbeat inattivi, bloat workspace, accumulo memoria

## Strumenti supportati

24+. Tutti i LLM: Claude, GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.

macOS, Windows, Linux, iPad/mobile via SSH. Python 3.8+, nessuna dipendenza esterna.
