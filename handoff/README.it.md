# handoff

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | Italiano | [Português](README.pt-BR.md)

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

**Le tue conversazioni si degradano. Questo strumento mantiene vivo il segnale.**

Ogni chat IA ha un tempo di dimezzamento. Piu un thread si allunga, piu il modello rilegge contesto obsoleto, meno preciso diventa l'output e piu token sprechi in rumore. La soluzione la conosci: avviare una nuova sessione. Ma cosi perdi tutte le decisioni prese, i bug gia tracciati, l'architettura definita. Quindi continui nel vecchio thread e la qualita continua a scendere.

`handoff` spezza questo circolo vizioso. Di' `handoff` in qualsiasi sessione e viene generato un blocco di trasferimento unico -- compressione lossless, 2-4K token -- che cattura tutto cio che conta: decisioni, scoperte, fallimenti, stato attuale, problemi aperti e prossimi passi. Incollalo in una nuova chat e torni a piena velocita senza dover riscoprire nulla.

Nessun file. Nessun plugin. Nessun database. Solo copia e incolla.

## Come funziona

**Modalita generazione** -- nella vecchia sessione, di' `handoff`. Lo skill comprime l'intera conversazione in un blocco di trasferimento strutturato tramite compressione lossless. Non e un riassunto superficiale. Preserva i risultati concreti -- cosa e stato deciso, cosa e fallito, cosa e a meta, cosa viene dopo -- eliminando saluti, chiacchiere, spiegazioni ripetute e trascrizioni grezze.

**Modalita ripresa** -- incolla il blocco in una nuova sessione. Lo skill lo analizza, ti fornisce un riepilogo compatto dello stato attuale e attende la tua prossima istruzione.

Il blocco di trasferimento punta a **2-4K token**. Abbastanza piccolo da usare spesso. Abbastanza denso da non perdere nulla di importante.

## Trigger naturali

Non serve ricordare un comando speciale. Qualsiasi di questi funziona:

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## Cosa viene preservato

- Decisioni e le loro motivazioni
- Scoperte tecniche e meccanismi
- Esperimenti falliti e perche sono falliti
- Numeri importanti, limiti, versioni, tempi, costi
- Branch / commit / stato dirty attuale
- Lavoro non committato o parzialmente completato
- Problemi aperti e bloccanti
- La migliore prossima azione

Cosa viene eliminato: saluti, incoraggiamenti, scambi ripetitivi, dump di codice grezzo, discussioni laterali che non hanno cambiato nulla, narrazione su cosa l'assistente stava per fare. Il segnale resta. Il rumore scompare.

## Funziona ovunque

`handoff` funziona con testo semplice. E compatibile con:

- Strumenti di coding (Claude Code, Cursor, Copilot, Windsurf)
- Strumenti CLI (assistenti IA da terminale)
- Strumenti di chat GUI (ChatGPT, Claude chat, Gemini)
- Qualsiasi prodotto in cui puoi incollare testo in una nuova conversazione

Nessuna integrazione speciale richiesta.

## Quando usarlo

- La chat attuale si allunga e il modello diventa lento
- Hai completato una parte del lavoro e vuoi una sessione pulita
- Ti stai avvicinando al limite di contesto
- Vuoi preservare le decisioni senza mantenere vivo l'intero vecchio thread
- Stai passando a un'altra macchina o strumento

## Installazione

Copia questo nel tuo strumento IA:

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## Utilizzo

Nella vecchia chat:

```text
handoff
```

Copia il blocco generato. Apri una nuova sessione. Incolla.

Tutto qui.

---

Autore: [Wallny](https://github.com/wallmage)
