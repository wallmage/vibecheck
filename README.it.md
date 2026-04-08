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

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | Italiano | [Português](README.pt-BR.md)

Ogni pomeriggio esaurivo la quota di Claude senza capire perché. Poi ho scoperto che il 70% delle mie sessioni di coding con IA era spreco — l'IA che narrava quello che stava per fare, comandi divisi in tre turni quando ne bastava uno, contesto obsoleto che si accumulava e veniva riletto a ogni turno.

vibecheck trova quello spreco. Legge i log reali delle tue sessioni su più di 24 strumenti di coding, mette cifre in dollari su 15 pattern specifici e li corregge. Tutto gira in locale. Nessun upload, nessuna telemetria, nessun server.

Nel mio caso: la spesa mensile è passata da $2,816 a $422. **Taglio dell'85%.**

## Come installare

Incolla questo nel tuo strumento di coding con IA e premi Invio:

> Help me install this skill: https://github.com/wallmage/vibecheck

Fatto. La tua IA carica lo skill e sei pronto per la scansione.

<details>
<summary>Oppure installa manualmente da riga di comando</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Poi digita `/vibecheck scan` in qualsiasi sessione.

Per aggiornare: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Cos'è esattamente uno "skill"?

Un file di testo puro che insegna alla tua IA qualcosa di nuovo. Nessun binario, nessun processo in background, nessuna modifica al sistema. Il file skill di vibecheck dice "ecco come trovare lo spreco e correggerlo". Cancella la cartella e sparisce.

### Strumenti di coding vs. strumenti di chat

**Gli strumenti di coding** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, ecc.) girano sulla tua macchina e lasciano log di sessione. vibecheck rileva automaticamente quelli installati e scansiona direttamente i log.

**Gli strumenti di chat** (Cowork, Claude nel browser) girano in un sandbox senza log locali. vibecheck ottimizza comunque i tuoi file di istruzioni — è da lì che proviene la maggior parte del risparmio. Puoi anche incollare un comando terminale per esportare 14 giorni di log e fare una scansione completa.

### Permessi

vibecheck legge i log di sessione locali e ispeziona i file di istruzioni (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) e le impostazioni globali degli strumenti. Se il tuo strumento ha una configurazione globale — un singolo file per tutti i progetti — l'ottimizzatore parte da lì, perché una correzione ti fa risparmiare ovunque. Chiede conferma prima di modificare qualsiasi cosa.

## Privacy

Tutto resta sulla tua macchina. L'analisi è un insieme di script Python che parsano i log di sessione locali. Nessun server, nessuna chiamata API, nessun analytics. Open source — leggi ogni riga se vuoi.

## Comandi

| Comando | Cosa fa |
|---|---|
| `/vibecheck scan` | Scansiona tutti gli strumenti rilevati sulla tua macchina. Un report unificato con indicatori di salute, statistiche ordinate, principali pattern di spreco e roadmap di ottimizzazione |
| `/vibecheck explain` | Ti insegna i pattern di spreco senza modificare nulla. Pura formazione |
| `/vibecheck compress` | Riduce i tuoi file di istruzioni del 25-50% con un compressore lossless a 4 passaggi |
| `/vibecheck monitor` | Confronto settimanale con la tua baseline. Rileva regressioni di costo prima che si accumulino |

La scansione è discreta: un indicatore di progresso compatto, poi un riepilogo pulito. `Good` significa spreco misurato sotto il 10%, `Waste` significa sopra. Log grezzi e output degli strumenti restano dietro le quinte a meno che qualcosa non vada storto.

### Mantenere le sessioni fresche

Le conversazioni lunghe costano più di quelle corte — ogni nuovo turno rilegge tutti quelli precedenti, e un contesto sovraccarico rende l'IA meno precisa, il che significa più botta e risposta.

Regola pratica: 5-10 minuti attivi per sessione, 30-40 turni prima che la tassa sul contesto inizi a pesare. Quando inizi una nuova sessione, mantieni le regole permanenti nei file di istruzioni (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) e il background del progetto in piccoli documenti locali. Nuova sessione non significa partire da zero — solo un contesto pulito con tutta la tua conoscenza ancora presente.

---

## Prima / Dopo

Misurato su sessioni reali:

```
                          BEFORE         NOW            CHANGE
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## Come i turni dell'IA costano denaro

Breve introduzione per chi non ha mai pensato all'economia dei token. Nessuna conoscenza pregressa sui prezzi dell'IA necessaria.

### Cosa succede a ogni turno

Ogni volta che la tua IA risponde, rilegge l'intera conversazione dall'inizio. System prompt, file di istruzioni, ogni messaggio che hai inviato, ogni risposta che ha dato, tutti gli output degli strumenti — contenuti di file, risultati del terminale, log di errore — tutto. Poi genera una nuova risposta.

**Costo del turno = token letti x prezzo di input + token generati x prezzo di output**

I primi turni sono economici. Il turno 1 potrebbe leggere 5,000 token. Al turno 40, rilegge più di 40,000 token di conversazione accumulata — ogni messaggio precedente, ogni snippet di codice, ogni traccia di errore. Quel turno tardivo costa 8 volte il primo.

Il punto chiave: lo spreco si **compone**. Un turno sprecato non costa solo i propri token. Resta nel contesto per il resto della sessione, riletto a ogni turno futuro. Un messaggio di narrazione inutile al turno 10 viene riletto altre 30 volte prima della fine.

### La cache del prompt aiuta, ma non risolve

La maggior parte dei provider ora mette in cache il contenuto già visto e addebita 10 volte meno. Il costo effettivo di input scende da $3.00/milione di token a $0.30/milione.

Aiuta. Ma il nuovo contenuto — output freschi degli strumenti, nuovi messaggi di errore, ogni nuova risposta dell'IA — entra sempre a prezzo pieno prima di essere messo in cache. E lo spreco si compone anche alla tariffa cached.

### Gli abbonamenti soffrono lo stesso problema

Se hai un abbonamento, potresti pensare che i prezzi API non ti riguardino. Invece sì — li senti solo in modo diverso. Gli abbonamenti comprano un pool fisso di calcolo, e lo spreco consuma quel pool più velocemente. Quando raggiungi la quota e vieni limitato alle 15, non è perché hai lavorato troppo — è perché gran parte di quel lavoro era spreco.

Claude Pro ($20/mese) copre circa $200 di valore API equivalente. Claude 20x Max ($200/mese) copre circa $4,000. Più spreco = muro raggiunto prima.

<details>
<summary><strong>Approfondimento: quanto vale davvero il tuo abbonamento in token</strong></summary>

### Come ho misurato

Avevo il piano Claude 20x Max da $200/mese e la quota si esauriva costantemente. Abbastanza curioso da passare alla fatturazione API e tracciare la spesa reale su 100+ punti dati — registrando ogni attività di coding, verificando il consumo subito dopo. Questo mi ha permesso di calcolare la relazione tra prezzo dell'abbonamento e valore reale in token.

### I moltiplicatori

| Piano | Prezzo | Valore API | Moltiplicatore | Finestra 5h | Totale settimanale |
|---|---|---|---|---|---|
| Claude Pro | $20/mese | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mese | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mese | ~$4,000 | 20x | $133.33 | $933.31 |

Il tier 20x Max è l'unico con un vero salto di moltiplicatore — 20x il valore nominale contro 10x per i tier inferiori.

### Nella pratica

- **$20 Claude Pro** — lavoro di sviluppo serio (implementare funzionalità, ricerca, documentazione) esaurisce la quota di 5 ore in meno di un'ora. Capacità settimanale sotto le 7 ore. Stretto per qualsiasi uso professionale.
- **$100 5x Max** — circa 4 ore prima di raggiungere la finestra di 5 ore. 30-35 ore/settimana in totale. Praticabile per uso regolare.
- **$200 20x Max** — pensato per chi lavora 80-100+ ore/settimana, spesso con più sessioni in parallelo.

### Perché Anthropic ha limitato l'uso degli abbonamenti da parte di terzi

A 10-20x il valore nominale, ogni dollaro di abbonamento compra molto più calcolo della tariffa API. Strumenti di terze parti che lo consumavano alla velocità API equivalente rendevano i conti insostenibili.

### L'alternativa Codex

Al tier $20, Codex Plus offre circa **3 volte l'utilizzo coding** di Claude Pro. Le conversazioni ChatGPT — anche GPT-5.4 Extended Thinking e ricerca approfondita — non contano nella quota coding di Codex. Quindi ottieni 3x la capacità coding più GPT-5.4 gratis.

**Se il tuo budget è $20/mese, Codex Plus ti dà più tempo di coding di Claude Pro.** Se puoi spendere di più, i tier Claude 5x e 20x offrono una proposta di valore diversa.

</details>

### Scenario di riferimento

Tutti gli importi in questo documento usano questa baseline (prezzi Sonnet 4.6):

| Parametro | Valore |
|---|---|
| Durata sessione | 25 turni |
| Contesto iniziale | 21,000 token |
| Crescita per turno | ~600 token |
| Tasso di cache hit | 95% |
| Costo per turno (metà sessione) | $0.017 |
| Totale sessione efficiente | $0.41 |

Per Opus 4.6, moltiplica tutti i costi per 1.67x.

---

## I 15 pattern di spreco

Organizzati per impatto economico. I primi tre da soli rappresentano il 60-70% di tutto lo spreco.

### Tier 1 — I tre grandi (60-70% dello spreco)

#### 1. Narrazione a vuoto

La tua IA dice "OK, adesso correggo" o "Fammi leggere prima il file" — poi fa il lavoro al turno successivo. Quel turno di narrazione non ha fatto nulla. Nessuna chiamata a strumenti, nessun codice, nessuna lettura di file. Solo un annuncio.

Ciascuno costa circa **$0.017** — e peggio, quei 300-500 token di testo di stato restano nel contesto, riletti a ogni turno futuro. Su 428 sessioni misurate: **$1.03/sessione sprecati**, 30% di tutto lo spreco. A 10 sessioni/giorno: **$309/mese solo di narrazione.**

Regola vibecheck: *"Nessun turno senza chiamata a strumento. Pensa e agisci nello stesso turno."* **Risparmio di ~$0.88/sessione.**

#### 2. Degrado del contesto

Il costo della sessione cresce quadraticamente, non linearmente. Il turno 50 rilegge tutti i 49 turni precedenti.

Confronto concreto: una sessione di 40 turni costa **$0.70**. Lo stesso lavoro diviso in due sessioni da 20 turni: **$0.60**. Quei $0.10 di differenza sono puro spreco per mantenere una conversazione gonfia. Le sessioni reali hanno in media 74 turni — **$0.46/sessione sprecati**, 13% di tutto lo spreco.

vibecheck insegna: *"Lavori non correlati in sessioni separate. Nei thread lunghi, resta compatto."* **Risparmio di ~$0.37/sessione.**

#### 3. Debug ping-pong

Correggi, rompi, riprova, rompi ancora. Ogni tentativo fallito inietta ~4,000 token di errore nel contesto, e quel testo morto viene riletto a ogni turno successivo. Tre cicli: 6 turni extra ($0.102) + 12K token di errori obsoleti ($0.036) = **~$0.14 per episodio**. Si verifica nel ~10% delle sessioni. **Ponderato: $0.015/sessione.**

Interruttore vibecheck: *"Dopo 2 correzioni fallite sullo stesso file — fermati, rileggi l'errore completo, pensa, una correzione mirata."* **Risparmio di ~$0.01/sessione.**

### Tier 2 — Densità dei turni (15-20% dello spreco)

Fare in tre turni quello che dovrebbe richiederne uno.

#### 4. Output degli strumenti verboso

Un comando di build o test scarica 500 righe (~5,000 token) nella conversazione. Quei token vengono riletti a ogni turno rimanente. 5K token x 12 turni rimanenti a tariffa cached = **$0.018/istanza**. Senza cache: **$0.180** — 10 volte peggio.

È il pattern più costoso singolarmente. Log di build, output npm, dump dei test — invadono quasi ogni sessione. **$1.05/sessione**, 31% di tutto lo spreco.

Correzione: *"Reindirizzare l'output su /tmp/. Usare flag --quiet. tail -50 massimo."* **Risparmio di ~$0.89/sessione.**

#### 5. Comandi non concatenati

`npm install` in un turno. `npm run build` nel successivo. Due riletture del contesto per quello che `npm install && npm run build` fa in uno. Ogni divisione: **$0.010**. Totalizza **$0.14/sessione** nelle sessioni intensive di comandi.

Correzione: *"Concatenare i comandi con `&&` quando è sicuro."* **Risparmio di ~$0.11/sessione.**

#### 6. Esplorazione del codebase

L'IA apre README, package.json, tre config e due moduli non correlati prima di scrivere una singola riga di codice. Cinque letture consecutive, nessuna modifica, nessuna decisione. $0.085 in turni sprecati + $0.027 tassa sul contesto = **$0.112/episodio.** Media: **$0.09/sessione.**

Correzione: prima grep o glob, leggere solo il rilevante, raggruppare più letture per turno. **Risparmio di ~$0.07/sessione.**

#### 7. Modifiche non raggruppate

Modificare il file A, poi B, poi C — tre turni. Un turno con modifiche parallele fa la stessa cosa. Due turni extra a $0.017 = **$0.034/istanza.** Media: **$0.058/sessione.**

Correzione: *"Raggruppare le chiamate a strumenti indipendenti."* **Risparmio di ~$0.05/sessione.**

### Tier 3 — La coda (5-10% dello spreco)

Piccoli singolarmente. Si accumulano.

#### 8. Riletture di file

Lo stesso file letto due volte in una sessione — il contenuto è già nel contesto, ma l'IA lo recupera di nuovo. **$0.019/rilettura**, i file vengono riletti 3-4 volte in media. **$0.066/sessione.** Correzione: *"Già nel contesto. Rileggere solo se il file è cambiato."* **Risparmio di ~$0.05/sessione.**

#### 9. Loop sleep/poll

`sleep 5 && check_status`, ripetuto 3-5 volte. Ogni poll = rilettura completa del contesto per verificare se un processo in background è finito. 4 poll x $0.017 = **$0.068/episodio**, **$0.043/sessione.** Correzione: *"Usare --wait o run_in_background."* **Risparmio di ~$0.034/sessione.**

#### 10. Tentativi falliti

Comando fallisce, l'IA esegue lo stesso comando senza modifiche. L'output di errore è ora duplicato nel contesto. **$0.019/tentativo**, **$0.080/sessione.** Correzione: come il ping-pong — *"Fermati, leggi l'errore, prova qualcosa di diverso."*

#### 11. Consultazioni dello schema

L'IA consulta le proprie definizioni degli strumenti — informazioni che possiede già. Aggiunge 2K+ token inutilmente. **$0.023/sessione.** La regola "nessun turno senza chiamata a strumento" risolve questo. **Risparmio di ~$0.02/sessione.**

#### 12. Cerimonia Git

`git add` → `git status` → `git commit` → `git push`. Quattro turni. `git add -A && git commit -m "msg" && git push` è uno. **$0.044/istanza** ma più raro di quanto si pensi — **$0.003/sessione.** Correzione: concatenare con `&&`.

### Tier 4 — Agenti sempre attivi

Modello di costo diverso. Agenti come OpenClaw si svegliano periodicamente, e lo spreco si misura al giorno, non per sessione.

#### 13. Heartbeat a vuoto

L'agente si sveglia ogni 5 minuti, rilegge tutto il workspace, non trova nulla, torna a dormire. 288 risvegli/giorno, ~97% a vuoto. Sono 280 risvegli a vuoto a $0.04 ciascuno = **$11.20/giorno ($336/mese)** senza fare nulla.

Correzione: *"Heartbeat minimo di 30 minuti. Saltare se non ci sono trigger in attesa."* Ridotto a ~48 risvegli/giorno. **Risparmio di $8-10/giorno ($240-300/mese).**

#### 14. Gonfiamento del workspace

35,000 token di file di personalità (SOUL.md, AGENTS.md, ecc.) riletti a ogni risveglio. Tutorial, coaching, filosofia — scritti per esseri umani, non per un'IA che esegue task. **$5.76/giorno ($173/mese)** solo per file di configurazione.

vibecheck li comprime: 35K → 12-15K token. Stesse regole comportamentali, senza il riempitivo per umani. **Risparmio di $3-4/giorno ($90-120/mese).**

#### 15. Accumulo di memoria

La cronologia delle sessioni cresce senza limiti. 100+ voci di memoria rilette a ogni risveglio, incluse cose di settimane fa che non contano più. **$3.17/giorno ($95/mese)** in memorie obsolete.

Correzione: *"Archiviare dopo 50 voci, riassumere, ricominciare."* **Risparmio di $2-3/giorno ($60-90/mese).**

---

## Il toolkit di ottimizzazione

vibecheck non si limita a indicare i problemi — li corregge.

### Compressione dei file di istruzioni

Il tuo file di istruzioni (`CLAUDE.md`, `AGENTS.md`, `Memory.md`, come lo chiama il tuo strumento) viene letto a ogni turno. È una tassa fissa su tutto quello che fai. Un file di istruzioni gonfio è un pedaggio su ogni strada della città.

vibecheck ha un compressore lossless a 4 passaggi — 23 tecniche, e "lossless" significa letteralmente che nessun fatto viene rimosso. Stesse informazioni, meno token.

| Passaggio | Cosa fa | Quanto risparmia |
|---|---|---|
| **Passaggio 1 — Meccanico** | Rimuove la formattazione markdown, converte le tabelle in forma compatta, unisce gli elenchi puntati | 10-15% |
| **Passaggio 2 — Preservazione dei fatti** | Deduplica i fatti ripetuti, comprime gli esempi di codice, riduce le descrizioni verbose | 15-25% |
| **Passaggio 3 — Alta fedeltà** | Rimuove tutorial e testi di coaching necessari agli umani ma non all'IA | 10-15% |
| **Passaggio 4 — Telegramma** | Riscrittura completa in forma abbreviata per file solo-IA. Denso, compresso — solo con il tuo permesso esplicito | 15-25% |

Un file di istruzioni da 10,000 token compresso a 6,000 risparmia $0.044 per sessione. A 10 sessioni al giorno: **$0.44/giorno ($13/mese)** solo dalla compressione.

### Soppressione dell'output

I token di output costano 5 volte quelli di input ($15 vs. $3/milione su Sonnet 4.6). L'IA stampa blocchi di codice o diff che non hai chiesto? Costoso. vibecheck aggiunge: *"Nessun codice o diff a meno che non venga chiesto."* **Risparmio di ~$0.047/sessione.**

### Monitoraggio dei costi

`/vibecheck monitor` scatta un'istantanea del tuo profilo di sessione e la confronta con la baseline nelle esecuzioni future. Un nuovo file di istruzioni ha introdotto verbosità? Progetto diverso, abitudini diverse? Il monitor rileva le regressioni prima che si accumulino.

---

## Riepilogo dei risparmi

### Strumenti interattivi (prezzi Sonnet 4.6)

| # | Pattern | Spreco medio/sessione | Risparmio medio |
|---|---|---|---|
| 1 | Narrazione a vuoto | $1.03 | $0.88 |
| 2 | Degrado del contesto | $0.46 | $0.37 |
| 3 | Debug ping-pong | $0.015 | $0.01 |
| 4 | Output verboso | $1.05 | $0.89 |
| 5 | Comandi non concatenati | $0.14 | $0.11 |
| 6 | Esplorazione del codebase | $0.09 | $0.07 |
| 7 | Modifiche non raggruppate | $0.058 | $0.05 |
| 8 | Riletture di file | $0.066 | $0.05 |
| 9 | Loop sleep/poll | $0.043 | $0.034 |
| 10 | Tentativi falliti | $0.08 | $0.06 |
| 11 | Consultazioni dello schema | $0.023 | $0.02 |
| 12 | Cerimonia Git | $0.003 | $0.003 |
| + | Compressione | $0.044 | $0.044 |
| + | Soppressione dell'output | $0.047 | $0.038 |
| | **Totale** | **$3.15*** | **$2.61** |

*I pattern individuali possono coesistere nello stesso turno — i totali riflettono misurazioni per pattern. Aggregato reale: $3.07 a $0.46 (vedi Prima / Dopo).

**Sessione tipica con spreco: $3.07. Dopo vibecheck: $0.46. Risparmio: 85%.**

- **Spreco lieve** (sessioni brevi, pochi pattern): riduzione del 40-55%
- **Spreco moderato** (utente medio): riduzione del 55-70%
- **Spreco elevato** (sessioni lunghe, pattern multipli): riduzione del 70-85%

### Agenti sempre attivi

| # | Pattern | Spreco giornaliero | Risparmio giornaliero |
|---|---|---|---|
| 13 | Heartbeat a vuoto | $11.20 | $9.70 |
| 14 | Gonfiamento del workspace | $5.76 | $3.76 |
| 15 | Accumulo di memoria | $3.17 | $2.37 |
| | **Totale** | **$20.13/giorno** | **$15.83/giorno** |

**Risparmio mensile per agenti sempre attivi: ~$475.**

---

## Strumenti supportati

Più di 24 strumenti. Nessun lock-in — vibecheck è un file di testo, qualsiasi IA che legge istruzioni può usarlo. Gli script di scansione sono Python puro, senza dipendenze.

**Scansione completa della sessione** (legge i log, mette cifre sullo spreco):
Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity

**Rilevamento + ottimizzazione delle istruzioni** (nessun parsing completo dei log ancora, ma rileva lo strumento e ottimizza i file di configurazione):
Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

**LLM con dati sui prezzi:** Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, più 40+.

**Piattaforme:** macOS, Windows, Linux, iPad via SSH. Python 3.8+.

---

<details>
<summary><strong>Metodologia</strong></summary>

Tutte le stime dei costi usano lo scenario di riferimento sopra. Assunzioni chiave:

- **95% di tasso di cache hit del prompt** — tipico per sessioni di coding rapide. Sessioni più lente con pause più lunghe tra i turni avranno tassi di cache inferiori e costi superiori.
- **25 turni produttivi/sessione** — le sessioni con spreco aggiungono 8-12 turni extra per narrazione, tentativi e comandi non concatenati.
- **600 token/turno di crescita** — sessioni verbose possono raggiungere 1,000-2,000 token per turno.
- **Tariffa di input effettiva: $0.435/1M** — tariffa ponderata di 95% cached ($0.30/1M) + 5% non cached ($3.00/1M).
- **Aliquota tassa sul contesto: $0.30/1M** — tariffa di input cached per aggiunte permanenti al contesto.

Stime conservative. I risparmi reali spesso superano queste cifre, specialmente con sessioni lunghe, file di istruzioni grandi o debug intensivo.
</details>

## Autore

[Wallny](https://github.com/wallmage)
