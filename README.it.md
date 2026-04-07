# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Il tuo strumento di coding IA sta bruciando soldi che non vedi.**

Ogni messaggio che invii, la tua IA rilegge *tutta* la conversazione dall'inizio. Il messaggio #50 costa 50 volte il messaggio #1. Quella narrazione "OK, ora sistemo questo"? Ti è costata soldi senza fare nulla. Quelle 500 righe di log di build? Rilette ad ogni. singolo. futuro. messaggio.

La maggior parte dei vibe coder spreca **oltre il 50%** del proprio budget token IA senza saperlo.

vibecheck risolve il problema. Scansiona gli ultimi 14 giorni di sessioni, trova esattamente dove si spreca, lo spiega in linguaggio semplice (niente gergo — ti insegniamo cosa sono i token), e applica correzioni di un paragrafo al tuo file di configurazione. Stesso lavoro. Metà costo.

**Risparmio medio: 50%+ della tua bolletta token.** Supporta tutti i modelli LLM. Funziona con Claude Code, OpenClaw, Codex, OpenCode e 24+ strumenti di coding IA. 100% locale — i tuoi dati non lasciano mai il tuo computer.

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## Privacy

**I tuoi dati non lasciano mai il tuo computer.** Nessun server, nessuna API, nessuna telemetria. È tecnicamente impossibile per l'autore raccogliere i tuoi dati. Il codice è completamente open source.

## Installazione

**Strumenti di coding IA (esperienza completa):** `claude install-skill https://github.com/wallmage/vibecheck`, poi `/vibecheck scan`.

**Ambienti sandbox (Cowork, ecc.):** Anche senza scansionare i log ottieni l'80% dei benefici — compressione del file di config, regole di risparmio. Per la scansione completa, incolla un comando nel tuo terminale (solo ultimi 14 giorni, ~20-50 MB).

## Comandi

- `/vibecheck scan` — Educazione interattiva + diagnosi completa + correzioni
- `/vibecheck explain` — Solo educazione
- `/vibecheck compress` — Comprimi file di config (25-50% più piccolo)
- `/vibecheck monitor` — Confronto settimanale + avvisi

## 15 pattern di spreco

Narrazione a vuoto, deterioramento del contesto, debugging ping-pong, output verboso, comandi non concatenati, esplorazione del codebase, edit non raggruppati, riletture file, loop sleep/poll, retry falliti, ricerche schema, cerimonia Git, e per agenti 24/7: heartbeat inattivi, bloat del workspace, accumulo memoria.

## Strumenti supportati

24+: Claude Code, Cursor, Codex, Windsurf, Cline, OpenClaw, CodeBuddy, TRAE, Kimi Code e altri.

Tutti i LLM: Claude (Opus/Sonnet/Haiku), GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.
