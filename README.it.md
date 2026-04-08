# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Ogni turno che la tua AI esegue costa denaro.** Sonnet 4.6: $3/$15 per milione di token (input/output). Opus 4.6: $5/$25 — 1.67x in più. Ecco cosa significa nella pratica:

- La tua AI dice "OK, lo sistemo" prima di fare il lavoro. Quel turno di narrazione: **$0.031 sprecati.** Cinque per sessione: **$0.165 buttati.**
- La tua conversazione arriva a 40 turni invece di dividersi a 20. Costo extra dalla rilettura di tutta quella cronologia: **$0.67 sprecati.**
- `git add`, poi `git commit`, poi `git push` — tre turni invece di un comando concatenato: **$0.098 sprecati.**

Questi sono 3 dei 15 pattern di spreco che vibecheck individua. Ognuno spiegato qui sotto con importi in dollari, cosa va storto, e come lo correggiamo.

Funziona con Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ strumenti di coding. Gira in locale — i tuoi dati restano sulla tua macchina.

## Come installarlo

Incolla questo nel tuo strumento AI di coding e premi Invio:

> Help me install this skill: https://github.com/wallmage/vibecheck

Tutto qui. Il resto lo fa la tua AI.

<details>
<summary>Oppure installa manualmente da riga di comando</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Poi digita `/vibecheck scan` in qualsiasi sessione.

Per aggiornare: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Cos'è una skill?

Una scheda ricetta per la tua AI. Non modifica nulla né installa nulla. È solo un file di testo che dice "ecco come trovare gli sprechi e correggerli." Eliminala quando vuoi.

### Strumenti di coding vs strumenti di chat

**Strumenti di coding** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, ecc.) girano sulla tua macchina — vibecheck rileva automaticamente il tuo strumento e analizza i log di sessione.

**Strumenti di chat** (Cowork, basati su browser) girano in una sandbox. vibecheck ottimizza comunque il tuo file di istruzioni (la maggior parte del beneficio), oppure incolli un comando terminale per copiare 14 giorni di log per un'analisi completa.

### Permessi

vibecheck legge e modifica il tuo file di istruzioni (CLAUDE.md, .cursorrules, ecc.). Chiede conferma prima di ogni modifica.

## Privacy

I tuoi dati non lasciano la tua macchina. Nessun server, nessuna API, nessuna telemetria. Open source.

## Comandi

- `/vibecheck scan` — spiega cos'è un token, analizza le tue sessioni, applica le correzioni
- `/vibecheck explain` — solo la lezione, nessuna modifica
- `/vibecheck compress` — riduce il tuo file di istruzioni del 25-50%
- `/vibecheck monitor` — confronto settimanale, segnala regressioni

## Prima / Dopo

```
                          PRIMA          ORA            VARIAZIONE
Turni medi/sessione       36.8           25.9           -10.9
Context window medio      128.4K         89.9K          -30%
Turni sprecati            36.7%          8.1%           -28.6%

Costo medio/sessione      $2.62          $1.35          -$1.27
Spesa mensile             $224           $115           -$109
```

---

## Come i turni costano denaro

A ogni turno, la tua AI rilegge l'intera conversazione — system prompt, file di istruzioni, tutti i messaggi precedenti, tutto l'output degli strumenti — e poi genera una risposta.

**Costo turno = token input x tariffa input + token output x tariffa output**

I turni iniziali sono economici (context piccolo). I turni tardivi sono costosi (tutto ciò che precede viene riletto). Ecco perché lo spreco si accumula — un turno sprecato rende ogni turno futuro più costoso perché il contenuto sprecato rimane nel context.

Il prompt caching riduce il costo input di 10x per i contenuti già visti. La maggior parte degli strumenti lo usa automaticamente.

**Utenti con abbonamento:** Non vedi direttamente i prezzi API, ma lo spreco consuma la tua quota messaggi più in fretta. Claude Pro ($20/mese) copre ~$200 di valore API. Max ($200/mese) copre ~$4.000.

### Scenario di riferimento

Tutti gli importi in dollari qui sotto usano questa baseline (Sonnet 4.6):

| Parametro | Valore |
|---|---|
| Lunghezza sessione | 25 turni |
| Context iniziale | 5.000 token |
| Crescita per turno | ~3.000 token |
| Cache hit rate | 90% |
| Costo turno a metà sessione | $0.038 |
| Totale sessione efficiente | $0.96 |

Per Opus 4.6, moltiplica tutti i costi per 1.67x.

---

## I 15 pattern di spreco

### Tier 1 — I Grandi 3 (60-70% dello spreco)

#### 1. Narrazione oziosa

**Cos'è.** La AI dice "OK, lo sistemo" o "Leggo prima il file" — poi fa il lavoro vero al turno successivo. Il turno di narrazione non ha fatto nulla: nessuna chiamata a strumenti, nessun codice, nessuna lettura di file.

**Lo spreco.** Ogni turno di narrazione costa **$0.031** (rilettura context + ~500 token di testo di stato). La maggior parte delle sessioni ne ha 5: **$0.165/sessione sprecati** — il 17% del conto che non produce nulla. Su 10 sessioni/giorno: **$1.65/giorno ($50/mese)** solo in narrazione.

**La correzione.** vibecheck aggiunge: *"Nessun turno senza chiamata a strumenti. Nessuna narrazione. Pensa e agisci nello stesso turno."* Elimina completamente la narrazione. **Risparmia $0.15-0.18/sessione.**

#### 2. Context rot

**Cos'è.** Le conversazioni lunghe diventano progressivamente più costose. Il turno 50 rilegge tutti i 49 turni precedenti. Il costo totale della sessione cresce quadraticamente con la lunghezza.

**Lo spreco.** Una sessione da 40 turni: **$1.89.** Due sessioni da 20 turni (stesso lavoro): **$1.22.** La differenza — **$0.67** — non compra nulla. A 100 turni: una sessione costa **$5.62** contro quattro sessioni da 25 turni a **$3.84.** Sono **$1.78 sprecati** per non aver diviso.

**La correzione.** Insegna: *"Usa /clear o /compact tra task non correlati. Inizia conversazioni nuove."* **Risparmia $0.30-0.70/sessione per gli utenti abituati a sessioni lunghe.**

#### 3. Debug ping-pong

**Cos'è.** Correggi, rompi, riprova, rompi ancora. Ogni tentativo fallito aggiunge output di errore al context (~4K token per ciclo), riletto a ogni turno futuro.

**Lo spreco.** Tre cicli falliti: 6 turni extra ($0.252) + 12K token di errori morti ($0.036 di tassa context). **Totale: ~$0.29 per episodio.** Si verifica in ~1/3 delle sessioni. **Ponderato: ~$0.10/sessione.**

**La correzione.** Aggiunge: *"Dopo 2 correzioni fallite sullo stesso file: fermati, rileggi l'errore per intero, pensa, singola correzione mirata."* **Risparmia ~$0.20 per episodio.**

### Tier 2 — Densità di turni (15-20% dello spreco)

#### 4. Output verboso degli strumenti

**Cos'è.** Il comando build/test scarica 500 righe (~5K token) nella conversazione. Quei token vengono riletti a ogni turno futuro.

**Lo spreco.** 5K token x 12 turni rimanenti x $0.30/1M = **$0.018/istanza** di tassa context. Accade 2-3 volte/sessione. Senza caching: **$0.180/istanza** — 10x peggio. **Totale: $0.04-0.05/sessione.**

**La correzione.** Aggiunge: *"Reindirizza output build/test su /tmp/, usa flag --quiet, tail -50 al massimo."* **Risparmia $0.03-0.05/sessione.**

#### 5. Comandi non concatenati

**Cos'è.** `npm install` in un turno, `npm run build` nel successivo. Due riletture del context quando `&&` li concatena in uno.

**Lo spreco.** Ogni separazione: **$0.023.** Le sessioni tipiche ne hanno 3-4. **Totale: $0.07-0.09/sessione.**

**La correzione.** Aggiunge: *"Concatena i comandi con `&&` quando è sicuro."* **Risparmia $0.06-0.08/sessione.**

#### 6. Vagabondaggio nel codebase

**Cos'è.** La AI apre file dopo file — README, package.json, config — prima di fare qualsiasi lavoro. Cinque o più letture consecutive prima della prima modifica.

**Lo spreco.** Cinque letture non necessarie: $0.190 in turni + $0.027 di tassa context = **$0.217/episodio.** Si verifica nel ~25% delle sessioni. **Ponderato: ~$0.054/sessione.**

**La correzione.** Incoraggia ricerca mirata (grep/glob prima), raggruppando più letture per turno. **Risparmia ~$0.15 per episodio.**

#### 7. Modifiche non raggruppate

**Cos'è.** Modifica il file A, poi il B, poi il C — tre turni quando un turno con modifiche parallele sarebbe sufficiente.

**Lo spreco.** 2 turni extra x $0.038 = **$0.076/istanza.** Accade nel ~60% delle sessioni. **Ponderato: ~$0.046/sessione.**

**La correzione.** Aggiunge: *"Raggruppa le chiamate a strumenti indipendenti (più Read/Edit per turno)."* **Risparmia ~$0.04/sessione.**

### Tier 3 — La coda (5-10% dello spreco)

#### 8. Riletture di file

**Cos'è.** Lo stesso file viene letto due volte in una sessione. Il contenuto è già nel context dopo la prima lettura.

**Lo spreco.** 1 turno sprecato + contenuto duplicato = **$0.043/rilettura.** 1-2 per sessione. **Ponderato: ~$0.039/sessione.**

**La correzione.** Aggiunge: *"Il contenuto è nel context dopo la prima lettura. Rileggi solo se il file è cambiato."* **Risparmia ~$0.03/sessione.**

#### 9. Loop sleep/poll

**Cos'è.** `sleep 5 && check_status`, ripetuto 3-5 volte. Ogni poll rilegge l'intero context.

**Lo spreco.** 4 poll x $0.038 = **$0.152/episodio.** Si verifica nel ~20% delle sessioni. **Ponderato: ~$0.030/sessione.**

**La correzione.** Aggiunge: *"Usa flag --wait o run_in_background."* **Risparmia ~$0.12/episodio.**

#### 10. Retry falliti

**Cos'è.** Il comando fallisce, la AI esegue esattamente lo stesso comando di nuovo. L'output di errore è ora nel context due volte.

**Lo spreco.** **$0.042/retry.** Si verifica nel ~30% delle sessioni. **Ponderato: ~$0.013/sessione.**

**La correzione.** Stessa regola del ping-pong: *"Fermati, rileggi l'errore, pensa, singola correzione mirata."*

#### 11. Ricerche schema

**Cos'è.** La AI consulta le proprie definizioni degli strumenti — informazioni che già possiede. Aggiunge 2K+ token al context.

**Lo spreco.** **$0.052/ricerca.** Si verifica nel ~40% delle sessioni. **Ponderato: ~$0.021/sessione.**

**La correzione.** "Nessun turno senza chiamata a strumenti" scoraggia i turni di discovery. **Risparmia ~$0.02/sessione.**

#### 12. Cerimonia git

**Cos'è.** `git add` → `git status` → `git commit` → `git push`, quattro turni. `git add -A && git commit -m "msg" && git push` è uno solo.

**Lo spreco.** 3 turni extra + output git = **$0.098/istanza.** Accade nel ~70% delle sessioni. **Ponderato: ~$0.069/sessione.**

**La correzione.** Aggiunge: *"Concatena i comandi git con `&&`."* **Risparmia ~$0.06/sessione.**

### Tier 4 — Agenti sempre attivi (OpenClaw, ecc.)

Modello di costo diverso: costo per risveglio x risvegli al giorno.

#### 13. Heartbeat ozioso

**Cos'è.** L'agente si sveglia ogni 5 minuti, rilegge l'intero workspace, non trova nulla. 288 risvegli/giorno, ~97% inattivi.

**Lo spreco.** 280 risvegli inattivi/giorno x $0.04 = **$11.20/giorno ($336/mese)** senza fare nulla.

**La correzione.** *"Heartbeat minimo 30min. Salta se non ci sono trigger."* Riduce a ~48 risvegli/giorno. **Risparmia $8-10/giorno ($240-300/mese).**

#### 14. Bloat dei file workspace

**Cos'è.** 35K token di file di personalità (SOUL.md, AGENTS.md) riletti a ogni risveglio. La AI ha bisogno solo delle regole comportamentali — tutorial e coaching sono per gli esseri umani.

**Lo spreco.** **$5.76/giorno ($173/mese)** solo per leggere file di configurazione.

**La correzione.** Comprime i file workspace: da 35K a 12-15K token. **Risparmia $3-4/giorno ($90-120/mese).**

#### 15. Accumulo della memoria

**Cos'è.** La cronologia delle sessioni cresce senza potatura. Oltre 100 voci rilette a ogni risveglio.

**Lo spreco.** **$3.17/giorno ($95/mese)** a leggere memoria obsoleta.

**La correzione.** *"Archivia dopo 50 turni, riassumi, ricomincia da capo."* **Risparmia $2-3/giorno ($60-90/mese).**

---

## In più: Strumenti di ottimizzazione

### Compressione del file di istruzioni

Il tuo file di istruzioni viene letto a ogni turno — una tassa fissa che paghi indipendentemente dal task. vibecheck include un compressore lossless a 4 passaggi (23 tecniche) che riduce la dimensione del file del 25-50%:

- **Passaggio 1 (Meccanico):** Rimuove il markdown, converte le tabelle, unisce i punti elenco. ~10-15%.
- **Passaggio 2 (Preservazione dei fatti):** Deduplica i fatti, comprime gli esempi di codice. ~15-25%.
- **Passaggio 3 (Alta fedeltà):** Rimuove tutorial e testo di coaching utile agli esseri umani ma non alla AI. ~10-15%.
- **Passaggio 4 (Telegrafic):** Riscrittura completa in forma abbreviata per file destinati solo alla AI. ~15-25% (solo con permesso).

Un file da 10K token compresso a 6K risparmia $0.057/sessione. A 10 sessioni/giorno: **$0.57/giorno ($17/mese).**

### Soppressione dell'output

I token output costano 5x quelli input ($15 vs $3/MTok su Sonnet). La AI che mostra blocchi di codice completi e diff che non hai richiesto spreca **~$0.047/sessione.** vibecheck aggiunge: *"Nessun codice/diff se non richiesto."*

### Monitoraggio dei costi

`/vibecheck monitor` fotografa il profilo della tua sessione e lo confronta con la baseline alle esecuzioni successive. Individua le regressioni prima che costino denaro.

---

## Riepilogo dei risparmi

### Strumenti interattivi (Sonnet 4.6)

| # | Pattern | Spreco medio/sessione | Risparmio medio |
|---|---|---|---|
| 1 | Narrazione oziosa | $0.165 | $0.155 |
| 2 | Context rot | $0.150 | $0.120 |
| 3 | Debug ping-pong | $0.097 | $0.067 |
| 4 | Output verboso | $0.045 | $0.035 |
| 5 | Comandi non concatenati | $0.080 | $0.065 |
| 6 | Vagabondaggio nel codebase | $0.054 | $0.040 |
| 7 | Modifiche non raggruppate | $0.046 | $0.038 |
| 8 | Riletture di file | $0.039 | $0.030 |
| 9 | Loop sleep/poll | $0.030 | $0.025 |
| 10 | Retry falliti | $0.013 | $0.010 |
| 11 | Ricerche schema | $0.021 | $0.018 |
| 12 | Cerimonia git | $0.069 | $0.058 |
| + | Compressione | $0.057 | $0.057 |
| + | Soppressione output | $0.047 | $0.038 |
| | **Totale** | **$0.913** | **$0.756** |

**Sessione tipicamente sprecata: $1.87. Dopo vibecheck: $1.11. Risparmio: 41%.**

- **Spreco leggero** (sessioni brevi, pochi pattern): 25-35%
- **Spreco moderato** (utente medio): 40-50%
- **Spreco pesante** (sessioni lunghe, più pattern): 50-65%

### Agenti sempre attivi

| # | Pattern | Spreco giornaliero | Risparmio giornaliero |
|---|---|---|---|
| 13 | Heartbeat ozioso | $11.20 | $9.70 |
| 14 | Bloat workspace | $5.76 | $3.76 |
| 15 | Accumulo memoria | $3.17 | $2.37 |
| | **Totale** | **$20.13/giorno** | **$15.83/giorno** |

**Risparmio mensile per agenti sempre attivi: ~$475.**

---

## Strumenti supportati

24+ strumenti.

- **Analisi completa sessione:** Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- **Rilevamento + ottimizzazione istruzioni:** Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

Tutti gli LLM: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, più altri 40+.

macOS, Windows, Linux, iPad via SSH. Python 3.8+, nessuna dipendenza.

<details>
<summary>Metodologia</summary>

Tutte le stime di costo usano lo scenario di riferimento sopra. Assunzioni principali:

- **90% prompt cache hit rate** — tipico per sessioni di coding rapido. Le sessioni più lente avranno costi più alti.
- **25 turni produttivi/sessione** — le sessioni sprecate aggiungono 8-12 turni extra da narrazione, retry e comandi non concatenati.
- **3.000 token/turno di crescita** — le sessioni verbose possono arrivare a 4.000-5.000.
- **Tariffa input effettiva: $0.57/1M** — miscelata 90% con cache ($0.30) + 10% senza cache ($3.00).
- **Tariffa tassa context: $0.30/1M** — tariffa input con cache per aggiunte permanenti al context.

Le stime sono conservative. I risparmi reali possono superare le proiezioni per gli utenti con sessioni lunghe, file di istruzioni grandi, o molto debugging.
</details>
