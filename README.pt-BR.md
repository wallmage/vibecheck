# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Cada turno da sua IA tem um custo.** Sonnet 4.6: $3/$15 por milhão de tokens (entrada/saída). Opus 4.6: $5/$25 — 1,67x mais caro. Veja como isso se manifesta na prática:

- Sua IA diz "Ok, vou corrigir isso" antes de efetivamente corrigir. Dados reais de 428 sessões: narração custa **$1,03/sessão desperdiçados.**
- Sua conversa chega a 74 turnos em vez de ser dividida em 20. Custo extra por reler todo esse histórico: **$0,46 desperdiçados.**
- `git add`, depois `git commit`, depois `git push` — três turnos em vez de um único comando encadeado: **$0,044 desperdiçados.**

Esses são 3 dos 15 padrões de desperdício que o vibecheck identifica. Cada um explicado abaixo com valores em dólares, o que dá errado e como corrigir.

Funciona com Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. Mais de 24 ferramentas de programação. Roda localmente — seus dados ficam na sua máquina.

## Como instalar

Cole isso na sua ferramenta de programação com IA e pressione Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

Pronto. Sua IA faz o resto.

<details>
<summary>Ou instale manualmente via linha de comando</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Depois digite `/vibecheck scan` em qualquer sessão.

Para atualizar: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### O que é uma skill?

Uma receita para sua IA. Não modifica nada nem instala nada. É apenas um arquivo de texto que diz "veja como encontrar desperdícios e corrigi-los." Delete quando quiser.

### Ferramentas de programação vs. ferramentas de chat

**Ferramentas de programação** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, etc.) rodam na sua máquina — o vibecheck detecta automaticamente sua ferramenta e varre os logs da sua sessão.

**Ferramentas de chat** (Cowork, baseadas em navegador) rodam em sandbox. O vibecheck ainda otimiza seu arquivo de instruções (a maior parte do benefício), ou você cola um único comando no terminal para copiar 14 dias de logs e fazer uma varredura completa.

### Permissões

O vibecheck lê e edita seu arquivo de instruções (CLAUDE.md, .cursorrules, etc.). Ele pede confirmação antes de cada alteração.

## Privacidade

Seus dados não saem da sua máquina. Sem servidor, sem API, sem telemetria. Código aberto.

## Comandos

- `/vibecheck scan` — ensina o que são tokens, varre suas sessões, aplica correções
- `/vibecheck explain` — só a explicação, sem alterações
- `/vibecheck compress` — reduz seu arquivo de instruções em 25-50%
- `/vibecheck monitor` — comparação semanal, sinaliza regressões

## Antes / Depois

```
                          ANTES          AGORA          VARIAÇÃO
Média de turnos/sessão    73,9           21,1           -52,8
Média do context window   65,6K          33,7K          -49%
Turnos desperdiçados      73,7%          8,0%           -65,7%

Custo médio/sessão        $3,07          $0,46          -$2,61
Gasto mensal              $2.816         $422           -$2.394
```

---

## Como os turnos custam dinheiro

A cada turno, sua IA relê toda a conversa — system prompt, arquivo de instruções, todas as mensagens anteriores, toda a saída das ferramentas — e então gera uma resposta.

**Custo por turno = tokens de entrada x taxa de entrada + tokens de saída x taxa de saída**

Os primeiros turnos são baratos (context pequeno). Os turnos tardios são caros (tudo o que veio antes é relido). Por isso o desperdício se multiplica — um turno desperdiçado torna todos os turnos futuros mais caros, pois o conteúdo inútil permanece no context.

O prompt caching reduz o custo de entrada em 10x para conteúdo já visto. A maioria das ferramentas o usa automaticamente.

**Usuários com assinatura:** Você não vê os preços de API diretamente, mas o desperdício consome sua cota de mensagens mais rápido. Claude Pro ($20/mês) cobre ~$200 em valor de API. Max ($200/mês) cobre ~$4.000.

<details>
<summary><strong>Pesquisa: Quanto vale de verdade sua assinatura em tokens</strong></summary>

### Como eu medi

Tenho o plano Claude 20x Max de $200/mês e vivia estourando a cota. Então fiquei curioso: quanto de uso de API cada tier realmente compra?

Mudei para cobrança por API e rastreei o gasto real em dólares em mais de 100 pontos de dados — cada atividade seguida de uma atualização do consumo. O suficiente para calcular a relação linear entre preço da assinatura e valor em tokens.

### Os multiplicadores

| Plano | Preço | Valor API | Multiplicador | Janela 5h | Total semanal |
|---|---|---|---|---|---|
| Claude Pro | $20/mês | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mês | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mês | ~$4,000 | 20x | $133.33 | $933.31 |

Só o tier 20x Max oferece um salto real de multiplicador (20x vs. 10x nos tiers mais baratos).

### Horas reais de uso

- **$20 Claude Pro** — trabalho sério (dev, pesquisa, redação) dura menos de 1 hora antes da cota de 5h acabar. Total semanal abaixo de 7 horas. Limitado demais para qualquer profissional.
- **$100 5x Max** — dá para trabalhar umas 4 horas antes de bater na janela de 5h. 30-35 horas/semana no total. Aceitável para uso normal.
- **$200 20x Max** — para quem trabalha 80-100+ horas/semana, geralmente com múltiplas sessões em paralelo.

### Por que o Claude proibiu o uso de assinaturas por terceiros

Esses multiplicadores explicam. Com 10-20x o valor de face, cada dólar de assinatura compra muito mais computação do que os preços de API oferecem. Ferramentas de terceiros consumindo cotas de assinatura a taxas equivalentes à API tornaram o modelo econômico insustentável.

### A alternativa Codex

Ainda não medi completamente o valor em dólares do Codex, mas no tier de $20, Codex Plus entrega aproximadamente **3x o uso de código** do Claude Pro.

Por quê: conversas no ChatGPT — incluindo GPT-5.4 Extended Thinking e deep research — não contam na sua cota do Codex. Só o coding já é 3x Claude Pro, e o chat Pro vem de graça por cima.

**Se você não pretende comprar pelo menos o tier de $100 do Claude, pegue $20 Codex Plus.** 3x o uso de código do Claude Pro, mais GPT-5.4 Extended Thinking e deep research grátis.

</details>

### Cenário de referência

Todos os valores em dólares abaixo usam esta base de cálculo (Sonnet 4.6):

| Parâmetro | Valor |
|---|---|
| Duração da sessão | 25 turnos |
| Context inicial | 21.000 tokens |
| Crescimento por turno | ~600 tokens |
| Taxa de cache hit | 95% |
| Custo de turno no meio da sessão | $0,017 |
| Total de uma sessão eficiente | $0,41 |

Para Opus 4.6, multiplique todos os custos por 1,67x.

---

## Os 15 padrões de desperdício

### Tier 1 — Os 3 Grandes (60-70% do desperdício)

#### 1. Narração Ociosa

**O que é.** A IA diz "Ok, vou corrigir isso" ou "Deixa eu ler o arquivo primeiro" — e só então faz o trabalho no turno seguinte. O turno de narração não fez nada: nenhuma chamada de ferramenta, nenhum código, nenhuma leitura de arquivo.

**O desperdício.** Dados reais de 428 sessões: **$1,03/sessão — 30% de todo o desperdício.** Em 10 sessões/dia: **$10,30/dia ($309/mês)** só em narração.

**A correção.** O vibecheck adiciona: *"Nenhum turno sem chamada de ferramenta. Sem narração. Pense e aja no mesmo turno."* Elimina a narração por completo. **Economiza ~$0,88/sessão.**

#### 2. Podridão de Context

**O que é.** Conversas longas ficam progressivamente mais caras. O turno 50 relê todos os 49 turnos anteriores. O custo total da sessão cresce quadraticamente com o tamanho.

**O desperdício.** Uma sessão de 40 turnos: **$0,70.** Duas sessões de 20 turnos (o mesmo trabalho): **$0,60.** A diferença — **$0,10** — não compra nada. Em 100 turnos: uma única sessão custa **$2,53** vs. quatro sessões de 25 turnos por **$1,64.** Dados reais de 428 sessões: **$0,46/sessão — 13%** do desperdício total.

**A correção.** Ensina: *"Use /clear ou /compact entre tarefas não relacionadas. Comece conversas novas."* **Economiza ~$0,37/sessão.**

#### 3. Debugging Ping-Pong

**O que é.** Corrige, quebra, tenta de novo, quebra de novo. Cada tentativa fracassada adiciona a saída de erro ao context (~4K tokens por ciclo), relidos em todos os turnos futuros.

**O desperdício.** Três ciclos fracassados: 6 turnos extras ($0,102) + 12K tokens de erros mortos ($0,036 de taxa de context). **Total: ~$0,14 por episódio.** Frequência ~10%. **Ponderado: $0,015/sessão.**

**A correção.** Adiciona: *"Após 2 correções fracassadas no mesmo arquivo: pare, releia o erro por completo, pense, faça uma única correção direcionada."* **Economiza ~$0,01/sessão.**

### Tier 2 — Densidade de Turnos (15-20% do desperdício)

#### 4. Saída Verbosa de Ferramentas

**O que é.** O comando de build/teste despeja 500 linhas (~5K tokens) na conversa. Esses tokens são relidos em todos os turnos futuros.

**O desperdício.** 5K tokens x 12 turnos restantes x $0,30/1M = **$0,018/instância** de taxa de context. Acontece 2-3 vezes/sessão. Sem cache: **$0,180/instância** — 10x pior. Dados reais: **$1,05/sessão** — 31% do desperdício.

**A correção.** Adiciona: *"Redirecione a saída de build/teste para /tmp/, use flags --quiet, tail -50 no máximo."* **Economiza ~$0,89/sessão.**

#### 5. Comandos Desencadeados

**O que é.** `npm install` em um turno, `npm run build` no seguinte. Duas releituras de context quando `&&` os encadearia em uma só.

**O desperdício.** Cada divisão: **$0,010.** Sessões típicas têm 3-4 divisões. Dados reais: **$0,14/sessão.**

**A correção.** Adiciona: *"Encadeie comandos com `&&` quando seguro."* **Economiza ~$0,11/sessão.**

#### 6. Vagabundagem no Codebase

**O que é.** A IA abre arquivo após arquivo — README, package.json, configs — antes de fazer qualquer trabalho. Cinco ou mais leituras consecutivas antes da primeira edição.

**O desperdício.** Cinco leituras desnecessárias: $0,085 em turnos + $0,027 de taxa de context = **$0,112/episódio.** Ponderado: **$0,09/sessão.**

**A correção.** Incentiva buscas direcionadas (grep/glob primeiro), agrupando múltiplas leituras por turno. **Economiza ~$0,07/sessão.**

#### 7. Edições Não Agrupadas

**O que é.** Edita o arquivo A, depois B, depois C — três turnos quando um único turno com edições paralelas resolveria.

**O desperdício.** 2 turnos extras x $0,017 = **$0,034/instância.** Ponderado: **$0,058/sessão.**

**A correção.** Adiciona: *"Agrupe chamadas de ferramenta independentes (múltiplos Reads/Edits por turno)."* **Economiza ~$0,05/sessão.**

### Tier 3 — A Cauda (5-10% do desperdício)

#### 8. Releituras de Arquivo

**O que é.** O mesmo arquivo lido duas vezes na mesma sessão. O conteúdo já está no context após a primeira leitura.

**O desperdício.** 1 turno desperdiçado + conteúdo duplicado = **$0,019/releitura.** Ponderado: **$0,066/sessão.**

**A correção.** Adiciona: *"Conteúdo está no context após a primeira leitura. Releia apenas se o arquivo foi alterado."* **Economiza ~$0,05/sessão.**

#### 9. Loops de Sleep/Poll

**O que é.** `sleep 5 && check_status`, repetido 3-5 vezes. Cada poll relê o context completo.

**O desperdício.** 4 polls x $0,017 = **$0,068/episódio.** Ponderado: **$0,043/sessão.**

**A correção.** Adiciona: *"Use flags --wait ou run_in_background."* **Economiza ~$0,034/sessão.**

#### 10. Tentativas Repetidas com Falha

**O que é.** O comando falha, a IA executa exatamente o mesmo comando novamente. A saída de erro agora está no context duas vezes.

**O desperdício.** **$0,019/tentativa.** Ponderado: **$0,080/sessão.**

**A correção.** Mesma regra do ping-pong: *"Pare, releia o erro, pense, faça uma única correção direcionada."*

#### 11. Consultas de Schema

**O que é.** A IA consulta suas próprias definições de ferramenta — informação que ela já tem. Adiciona 2K+ tokens ao context.

**O desperdício.** **$0,023/consulta.** Ponderado: **$0,023/sessão.**

**A correção.** "Nenhum turno sem chamada de ferramenta" desestimula turnos de descoberta. **Economiza ~$0,02/sessão.**

#### 12. Cerimônia do Git

**O que é.** `git add` → `git status` → `git commit` → `git push`, quatro turnos. `git add -A && git commit -m "msg" && git push` é apenas um.

**O desperdício.** 3 turnos extras + saída do git = **$0,044/instância.** Ponderado: **$0,003/sessão.**

**A correção.** Adiciona: *"Encadeie comandos git com `&&`."* **Economiza ~$0,003/sessão.**

### Tier 4 — Agentes Sempre Ativos (OpenClaw, etc.)

Modelo de custo diferente: custo por ativação x ativações por dia.

#### 13. Heartbeats Ociosos

**O que é.** O agente acorda a cada 5 minutos, relê o workspace completo e não encontra nada. 288 ativações/dia, ~97% ociosas.

**O desperdício.** 280 ativações ociosas/dia x $0,04 = **$11,20/dia ($336/mês)** sem fazer nada.

**A correção.** *"Intervalo mínimo de 30min entre heartbeats. Pule se não houver gatilhos."* Reduz para ~48 ativações/dia. **Economiza $8-10/dia ($240-300/mês).**

#### 14. Inchaço de Arquivos do Workspace

**O que é.** 35K tokens de arquivos de personalidade (SOUL.md, AGENTS.md) relidos a cada ativação. A IA precisa apenas das regras de comportamento — tutoriais e coaching são para humanos.

**O desperdício.** **$5,76/dia ($173/mês)** só lendo arquivos de configuração.

**A correção.** Comprime os arquivos do workspace: 35K → 12-15K tokens. **Economiza $3-4/dia ($90-120/mês).**

#### 15. Acúmulo de Memória

**O que é.** O histórico de sessão cresce sem poda. Mais de 100 entradas relidas a cada ativação.

**O desperdício.** **$3,17/dia ($95/mês)** lendo memória obsoleta.

**A correção.** *"Archive após 50 turnos, faça um resumo, comece do zero."* **Economiza $2-3/dia ($60-90/mês).**

---

## Mais: Ferramentas de Otimização

### Compressão do Arquivo de Instruções

Seu arquivo de instruções é lido a cada turno — uma taxa fixa que você paga independentemente da tarefa. O vibecheck inclui um compressor lossless de 4 etapas (23 técnicas) que reduz o tamanho do arquivo em 25-50%:

- **Etapa 1 (Mecânica):** Remove markdown, converte tabelas, mescla bullets. ~10-15%.
- **Etapa 2 (Preservação de fatos):** Deduplica fatos, comprime exemplos de código. ~15-25%.
- **Etapa 3 (Alta fidelidade):** Remove textos de tutoriais e coaching que humanos precisam mas a IA não. ~10-15%.
- **Etapa 4 (Telegrama):** Reescrita completa em shorthand para arquivos exclusivos da IA. ~15-25% (somente com permissão).

Um arquivo de 10K tokens comprimido para 6K economiza $0,044/sessão. Em 10 sessões/dia: **$0,44/dia ($13/mês).**

### Supressão de Saída

Tokens de saída custam 5x mais que os de entrada ($15 vs $3/MTok no Sonnet). A IA exibindo blocos de código completos e diffs que você não pediu desperdiça **~$0,047/sessão.** O vibecheck adiciona: *"Nenhum código/diff a menos que solicitado."*

### Monitoramento de Custos

`/vibecheck monitor` tira um snapshot do seu perfil de sessão e compara com a linha de base nas execuções seguintes. Detecta regressões antes que custam dinheiro.

---

## Resumo de Economias

### Ferramentas interativas (Sonnet 4.6)

| # | Padrão | Desperdício médio/sessão | Economia média |
|---|---|---|---|
| 1 | Narração ociosa | $1,03 | $0,88 |
| 2 | Podridão de context | $0,46 | $0,37 |
| 3 | Debugging ping-pong | $0,015 | $0,01 |
| 4 | Saída verbosa | $1,05 | $0,89 |
| 5 | Comandos desencadeados | $0,14 | $0,11 |
| 6 | Vagabundagem no codebase | $0,09 | $0,07 |
| 7 | Edições não agrupadas | $0,058 | $0,05 |
| 8 | Releituras de arquivo | $0,066 | $0,05 |
| 9 | Loops de sleep/poll | $0,043 | $0,034 |
| 10 | Tentativas repetidas com falha | $0,08 | $0,06 |
| 11 | Consultas de schema | $0,023 | $0,02 |
| 12 | Cerimônia do git | $0,003 | $0,003 |
| + | Compressão | $0,044 | $0,044 |
| + | Supressão de saída | $0,047 | $0,038 |
| | **Total** | **$3,15*** | **$2,61** |

*Padrões individuais podem se sobrepor no mesmo turno — os totais refletem medição por padrão. Economia real agregada: $3,07 → $0,46 (ver linha final).

**Sessão tipicamente desperdiçadora: $3,07. Após o vibecheck: $0,46. Economia: 85%.**

- **Desperdício leve** (sessões curtas, poucos padrões): 40-55%
- **Desperdício moderado** (usuário médio): 55-70%
- **Desperdício intenso** (sessões longas, múltiplos padrões): 70-85%

### Agentes sempre ativos

| # | Padrão | Desperdício diário | Economia diária |
|---|---|---|---|
| 13 | Heartbeats ociosos | $11,20 | $9,70 |
| 14 | Inchaço do workspace | $5,76 | $3,76 |
| 15 | Acúmulo de memória | $3,17 | $2,37 |
| | **Total** | **$20,13/dia** | **$15,83/dia** |

**Economia mensal para agentes sempre ativos: ~$475.**

---

## Ferramentas suportadas

Mais de 24 ferramentas.

- **Varredura completa de sessão:** Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- **Detecção + otimização de instruções:** Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

Todos os LLMs: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, e mais 40+.

macOS, Windows, Linux, iPad via SSH. Python 3.8+, sem dependências.

<details>
<summary>Metodologia</summary>

Todas as estimativas de custo usam o cenário de referência acima. Premissas principais:

- **95% de taxa de cache hit** — típico para sessões de programação rápida. Sessões mais lentas terão custos mais altos.
- **25 turnos produtivos/sessão** — sessões desperdiçadoras acrescentam 8-12 turnos extras de narração, tentativas repetidas e comandos desencadeados.
- **600 tokens/turno de crescimento** — sessões verbosas podem chegar a 1.000-2.000.
- **Taxa efetiva de entrada: $0,435/1M** — média ponderada de 95% com cache ($0,30) + 5% sem cache ($3,00).
- **Taxa de context tax: $0,30/1M** — taxa de entrada com cache para adições permanentes ao context.

As estimativas são conservadoras. Economias reais podem superar as projeções para usuários com sessões longas, arquivos de instruções grandes ou debugging intenso.
</details>
