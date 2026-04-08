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

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | Português

Toda tarde minha cota do Claude esgotava e eu não entendia por quê. Descobri que 70% das minhas sessões de coding com IA eram desperdício — a IA narrando o que ia fazer, comandos divididos em três turnos quando um bastava, contexto obsoleto se acumulando e sendo relido a cada turno.

vibecheck encontra esse desperdício. Lê os logs reais das suas sessões em mais de 24 ferramentas de coding, coloca valores em dólares em 15 padrões específicos e os corrige. Tudo roda localmente. Sem upload, sem telemetria, sem servidores.

No meu caso: o gasto mensal caiu de $2,816 para $422. **Redução de 85%.**

## Como instalar

Cole isso na sua ferramenta de coding com IA e pressione Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

Pronto. Sua IA carrega o skill e você está pronto para escanear.

<details>
<summary>Ou instale manualmente pela linha de comando</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Depois digite `/vibecheck scan` em qualquer sessão.

Para atualizar: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### O que exatamente é um "skill"?

Um arquivo de texto puro que ensina sua IA a fazer algo novo. Sem binários, sem processos em segundo plano, sem modificações no sistema. O arquivo skill do vibecheck diz "veja como encontrar desperdício e corrigi-lo". Delete a pasta e ele desaparece.

### Ferramentas de coding vs. ferramentas de chat

**Ferramentas de coding** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, etc.) rodam na sua máquina e deixam logs de sessão. vibecheck detecta automaticamente quais você tem e escaneia esses logs diretamente.

**Ferramentas de chat** (Cowork, Claude no navegador) rodam em sandbox sem logs locais. vibecheck ainda otimiza seus arquivos de instruções — é de lá que vem a maior parte da economia, de qualquer forma. Você também pode colar um comando de terminal para exportar 14 dias de logs e fazer um scan completo.

### Permissões

vibecheck lê seus logs de sessão locais e inspeciona arquivos de instruções (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) e configurações globais das ferramentas. Se sua ferramenta tem uma configuração global — um arquivo que cobre todos os projetos — o otimizador vai lá primeiro, porque uma correção economiza em todos os lugares. Pede confirmação antes de mudar qualquer coisa.

## Privacidade

Tudo fica na sua máquina. A análise é um conjunto de scripts Python que fazem parse dos seus logs de sessão locais. Sem servidor, sem chamadas de API, sem analytics. Código aberto — leia cada linha se quiser.

## Comandos

| Comando | O que faz |
|---|---|
| `/vibecheck scan` | Escaneia todas as ferramentas detectadas na sua máquina. Um relatório unificado com indicadores de saúde, estatísticas ranqueadas, principais padrões de desperdício e roteiro de otimização |
| `/vibecheck explain` | Ensina os padrões de desperdício sem mudar nada. Pura educação |
| `/vibecheck compress` | Reduz seus arquivos de instruções em 25-50% com um compressor lossless de 4 passos |
| `/vibecheck monitor` | Comparação semanal com sua baseline. Detecta regressões de custo antes que se acumulem |

O scan é discreto: um indicador de progresso compacto, depois um resumo limpo. `Good` significa desperdício medido abaixo de 10%, `Waste` significa acima. Logs brutos e saída de ferramentas ficam nos bastidores a menos que algo dê errado.

### Manter as sessões frescas

Conversas longas custam mais que curtas — cada novo turno relê todos os anteriores, e contexto sobrecarregado torna a IA menos precisa, o que gera mais vai-e-vem.

Regra prática: 5-10 minutos ativos por sessão, 30-40 turnos antes que o imposto de contexto comece a pesar. Ao iniciar uma nova sessão, mantenha suas regras permanentes nos arquivos de instruções (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) e o contexto do projeto em documentos locais pequenos. Nova sessão não significa começar do zero — apenas um contexto limpo com todo o seu conhecimento intacto.

---

## Antes / Depois

Medido em sessões reais:

```
                          BEFORE         NOW            CHANGE
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## Como os turnos da IA custam dinheiro

Introdução rápida para quem nunca pensou sobre economia de tokens. Nenhum conhecimento prévio sobre precificação de IA necessário.

### O que acontece a cada turno

Toda vez que sua IA responde, ela relê a conversa inteira desde o início. System prompt, arquivo de instruções, cada mensagem que você enviou, cada resposta que ela deu, toda saída de ferramentas — conteúdo de arquivos, resultados do terminal, logs de erro — tudo. Depois gera uma nova resposta.

**Custo do turno = tokens lidos x preço de entrada + tokens gerados x preço de saída**

Os primeiros turnos são baratos. O turno 1 pode ler 5.000 tokens. No turno 40, relê mais de 40.000 tokens de conversa acumulada — cada mensagem anterior, cada snippet de código, cada trace de erro. Esse turno tardio custa 8x o primeiro.

O ponto-chave: o desperdício tem **efeito composto**. Um turno desperdiçado não custa apenas seus próprios tokens. Ele permanece no contexto pelo resto da sessão, sendo relido a cada turno futuro. Uma mensagem de narração desnecessária no turno 10 é relida mais 30 vezes antes do fim.

### Cache de prompt ajuda, mas não resolve

A maioria dos provedores agora faz cache de conteúdo já visto e cobra 10x menos. O custo efetivo de entrada cai de $3.00/milhão de tokens para $0.30/milhão.

Ajuda. Mas conteúdo novo — saída fresca de ferramentas, novas mensagens de erro, cada nova resposta da IA — sempre entra a preço cheio antes de ser cacheado. E o desperdício se compõe mesmo na tarifa cacheada.

### Assinaturas sentem a mesma dor

Se você tem assinatura, pode achar que preços de API não se aplicam. Aplicam — você só sente de forma diferente. Assinaturas compram um pool fixo de computação, e o desperdício consome esse pool mais rápido. Quando você atinge sua cota e é limitado às 15h, não é porque trabalhou demais — é porque boa parte desse trabalho foi desperdício.

Claude Pro ($20/mês) cobre aproximadamente $200 em valor API equivalente. Claude 20x Max ($200/mês) cobre aproximadamente $4.000. Mais desperdício = muro mais rápido.

<details>
<summary><strong>Análise detalhada: quanto vale sua assinatura realmente em tokens</strong></summary>

### Como eu medi

Eu tinha o plano Claude 20x Max de $200/mês e vivia ficando sem cota. Curioso o bastante para mudar para cobrança API e rastrear o gasto real em mais de 100 pontos de dados — registrando cada atividade de coding, verificando o consumo logo depois. Isso me permitiu calcular a relação entre o preço da assinatura e o valor real em tokens.

### Os multiplicadores

| Plano | Preço | Valor API | Multiplicador | Janela 5h | Total semanal |
|---|---|---|---|---|---|
| Claude Pro | $20/mês | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mês | ~$1.000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mês | ~$4.000 | 20x | $133.33 | $933.31 |

O tier 20x Max é o único com salto real de multiplicador — 20x o valor nominal contra 10x nos tiers inferiores.

### Na prática

- **$20 Claude Pro** — trabalho de desenvolvimento sério (implementar features, pesquisa, documentação) consome sua cota de 5 horas em menos de uma hora. Capacidade semanal abaixo de 7 horas. Apertado para qualquer uso profissional.
- **$100 5x Max** — cerca de 4 horas até atingir a janela de 5 horas. 30-35 horas/semana no total. Viável para uso regular.
- **$200 20x Max** — projetado para quem trabalha 80-100+ horas/semana, frequentemente rodando múltiplas sessões em paralelo.

### Por que a Anthropic restringiu o uso de assinaturas por terceiros

A 10-20x o valor nominal, cada dólar de assinatura compra muito mais computação que a tarifa API. Ferramentas de terceiros consumindo isso na velocidade API equivalente tornaram as contas insustentáveis.

### A alternativa Codex

No tier de $20, Codex Plus oferece aproximadamente **3x o uso de coding** do Claude Pro. Conversas no ChatGPT — mesmo GPT-5.4 Extended Thinking e pesquisa profunda — não contam na cota de coding do Codex. Então você ganha 3x a capacidade de coding mais GPT-5.4 grátis.

**Se seu orçamento é $20/mês, Codex Plus te dá mais tempo de coding que Claude Pro.** Se pode gastar mais, os tiers Claude 5x e 20x oferecem uma proposta de valor diferente.

</details>

### Cenário de referência

Todos os valores neste documento usam esta baseline (preços do Sonnet 4.6):

| Parâmetro | Valor |
|---|---|
| Duração da sessão | 25 turnos |
| Contexto inicial | 21.000 tokens |
| Crescimento por turno | ~600 tokens |
| Taxa de cache hit | 95% |
| Custo por turno (meio da sessão) | $0.017 |
| Total sessão eficiente | $0.41 |

Para Opus 4.6, multiplique todos os custos por 1.67x.

---

## Os 15 padrões de desperdício

Organizados pelo quanto queimam de dinheiro. Os três primeiros sozinhos representam 60-70% de todo o desperdício.

### Tier 1 — Os três grandes (60-70% do desperdício)

#### 1. Narração ociosa

Sua IA diz "OK, vou corrigir isso" ou "Deixa eu ler o arquivo primeiro" — e faz o trabalho no turno seguinte. Esse turno de narração não fez nada. Sem chamada de ferramenta, sem código, sem leitura de arquivo. Apenas um anúncio.

Cada um custa cerca de **$0.017** — e pior, esses 300-500 tokens de texto de status permanecem no contexto, relidos a cada turno futuro. Em 428 sessões medidas: **$1.03/sessão desperdiçados**, 30% de todo o desperdício. A 10 sessões/dia: **$309/mês só de narração.**

Regra vibecheck: *"Nenhum turno sem chamada de ferramenta. Pense e aja no mesmo turno."* **Economia de ~$0.88/sessão.**

#### 2. Degradação do contexto

O custo da sessão cresce quadraticamente, não linearmente. O turno 50 relê todos os 49 turnos anteriores.

Comparação concreta: uma sessão de 40 turnos custa **$0.70**. O mesmo trabalho dividido em duas sessões de 20 turnos: **$0.60**. Essa diferença de $0.10 é puro desperdício de manter uma conversa inchada. Sessões reais têm em média 74 turnos — **$0.46/sessão desperdiçados**, 13% de todo o desperdício.

vibecheck ensina: *"Trabalhos não relacionados vão em sessões separadas. Em threads longos, fique compacto."* **Economia de ~$0.37/sessão.**

#### 3. Debug ping-pong

Corrigir, quebrar, tentar de novo, quebrar de novo. Cada tentativa falha injeta ~4.000 tokens de erro no contexto, e esse texto morto é relido a cada turno seguinte. Três ciclos: 6 turnos extras ($0.102) + 12K tokens de erros obsoletos ($0.036) = **~$0.14 por episódio**. Ocorre em ~10% das sessões. **Ponderado: $0.015/sessão.**

Disjuntor vibecheck: *"Após 2 correções falhas no mesmo arquivo — pare, releia o erro completo, pense, uma correção certeira."* **Economia de ~$0.01/sessão.**

### Tier 2 — Densidade de turnos (15-20% do desperdício)

Fazer em três turnos o que deveria levar um.

#### 4. Saída de ferramenta verbosa

Um comando de build ou teste despeja 500 linhas (~5.000 tokens) na conversa. Esses tokens são relidos a cada turno restante. 5K tokens x 12 turnos restantes na tarifa cached = **$0.018/instância**. Sem cache: **$0.180** — 10x pior.

Este é o padrão mais caro individualmente. Logs de build, saída npm, dumps de teste — inundam quase toda sessão. **$1.05/sessão**, 31% de todo o desperdício.

Correção: *"Redirecionar saída para /tmp/. Usar flags --quiet. tail -50 no máximo."* **Economia de ~$0.89/sessão.**

#### 5. Comandos sem encadear

`npm install` em um turno. `npm run build` no seguinte. Duas releituras de contexto para o que `npm install && npm run build` faz em um. Cada divisão: **$0.010**. Soma **$0.14/sessão** em sessões intensivas de comandos.

Correção: *"Encadear comandos com `&&` quando seguro."* **Economia de ~$0.11/sessão.**

#### 6. Exploração do codebase

A IA abre README, package.json, três configs e dois módulos não relacionados antes de escrever uma única linha de código. Cinco leituras consecutivas, sem edições, sem decisões. $0.085 em turnos desperdiçados + $0.027 imposto de contexto = **$0.112/episódio.** Média: **$0.09/sessão.**

Correção: grep ou glob primeiro, ler apenas o relevante, agrupar múltiplas leituras por turno. **Economia de ~$0.07/sessão.**

#### 7. Edições sem agrupar

Editar arquivo A, depois B, depois C — três turnos. Um turno com edições paralelas faz a mesma coisa. Dois turnos extras a $0.017 = **$0.034/instância.** Média: **$0.058/sessão.**

Correção: *"Agrupar chamadas de ferramentas independentes."* **Economia de ~$0.05/sessão.**

### Tier 3 — A cauda (5-10% do desperdício)

Pequenos individualmente. Se acumulam.

#### 8. Releituras de arquivos

O mesmo arquivo lido duas vezes em uma sessão — o conteúdo já está no contexto, mas a IA busca de novo. **$0.019/releitura**, arquivos são relidos 3-4 vezes em média. **$0.066/sessão.** Correção: *"Já está no contexto. Reler apenas se o arquivo mudou."* **Economia de ~$0.05/sessão.**

#### 9. Loops sleep/poll

`sleep 5 && check_status`, repetido 3-5 vezes. Cada poll = releitura completa do contexto para verificar se um processo em background terminou. 4 polls x $0.017 = **$0.068/episódio**, **$0.043/sessão.** Correção: *"Usar --wait ou run_in_background."* **Economia de ~$0.034/sessão.**

#### 10. Tentativas falhas

Comando falha, IA executa o mesmo comando sem alteração. A saída de erro agora está duplicada no contexto. **$0.019/tentativa**, **$0.080/sessão.** Correção: mesmo que o ping-pong — *"Pare, leia o erro, tente algo diferente."*

#### 11. Consultas de schema

A IA consulta suas próprias definições de ferramentas — informação que já possui. Adiciona 2K+ tokens à toa. **$0.023/sessão.** A regra "nenhum turno sem chamada de ferramenta" resolve isso. **Economia de ~$0.02/sessão.**

#### 12. Cerimônia Git

`git add` → `git status` → `git commit` → `git push`. Quatro turnos. `git add -A && git commit -m "msg" && git push` é um. **$0.044/instância** mas mais raro do que se pensa — **$0.003/sessão.** Correção: encadear com `&&`.

### Tier 4 — Agentes sempre ativos

Modelo de custo diferente. Agentes como OpenClaw acordam periodicamente, e o desperdício é medido por dia, não por sessão.

#### 13. Heartbeats ociosos

O agente acorda a cada 5 minutos, relê todo o workspace, não encontra nada, volta a dormir. 288 despertares/dia, ~97% ociosos. São 280 despertares ociosos a $0.04 cada = **$11.20/dia ($336/mês)** sem fazer nada.

Correção: *"Heartbeat mínimo de 30 minutos. Pular se não houver triggers pendentes."* Reduz para ~48 despertares/dia. **Economia de $8-10/dia ($240-300/mês).**

#### 14. Inchaço do workspace

35.000 tokens de arquivos de personalidade (SOUL.md, AGENTS.md, etc.) relidos a cada despertar. Tutoriais, coaching, filosofia — escritos para humanos, não para uma IA executando tarefas. **$5.76/dia ($173/mês)** só em arquivos de configuração.

vibecheck os comprime: 35K → 12-15K tokens. Mesmas regras de comportamento, sem preenchimento para humanos. **Economia de $3-4/dia ($90-120/mês).**

#### 15. Acúmulo de memória

O histórico de sessões cresce indefinidamente. Mais de 100 entradas de memória relidas a cada despertar, incluindo coisas de semanas atrás que não importam mais. **$3.17/dia ($95/mês)** em memórias obsoletas.

Correção: *"Arquivar após 50 entradas, resumir, recomeçar."* **Economia de $2-3/dia ($60-90/mês).**

---

## O toolkit de otimização

vibecheck não só aponta problemas — corrige-os.

### Compressão de arquivos de instruções

Seu arquivo de instruções (`CLAUDE.md`, `AGENTS.md`, `Memory.md`, como quer que sua ferramenta o chame) é lido a cada turno. É um imposto fixo sobre tudo que você faz. Um arquivo de instruções inchado é um pedágio em cada estrada da cidade.

vibecheck tem um compressor lossless de 4 passos — 23 técnicas, e "lossless" significa literalmente que nenhum fato é removido. Mesma informação, menos tokens.

| Passo | O que faz | Quanto economiza |
|---|---|---|
| **Passo 1 — Mecânico** | Remove formatação markdown, converte tabelas para forma compacta, mescla bullets | 10-15% |
| **Passo 2 — Preservação de fatos** | Deduplica fatos repetidos, comprime exemplos de código, condensa descrições verbosas | 15-25% |
| **Passo 3 — Alta fidelidade** | Remove tutoriais e textos de coaching que humanos precisam mas a IA não | 10-15% |
| **Passo 4 — Telegrama** | Reescrita completa em taquigrafia para arquivos somente-IA. Denso, comprimido — apenas com sua permissão explícita | 15-25% |

Um arquivo de instruções de 10.000 tokens comprimido para 6.000 economiza $0.044 por sessão. A 10 sessões por dia: **$0.44/dia ($13/mês)** só de compressão.

### Supressão de saída

Tokens de saída custam 5x os de entrada ($15 vs. $3/milhão no Sonnet 4.6). A IA imprimindo blocos de código ou diffs que você não pediu? Caro. vibecheck adiciona: *"Sem código ou diffs a menos que pedido."* **Economia de ~$0.047/sessão.**

### Monitoramento de custos

`/vibecheck monitor` tira um snapshot do seu perfil de sessão e compara com a baseline em execuções futuras. Um novo arquivo de instruções introduziu verbosidade? Projeto diferente, hábitos diferentes? O monitor detecta regressões antes que se acumulem.

---

## Resumo de economias

### Ferramentas interativas (preços Sonnet 4.6)

| # | Padrão | Desperdício médio/sessão | Economia média |
|---|---|---|---|
| 1 | Narração ociosa | $1.03 | $0.88 |
| 2 | Degradação do contexto | $0.46 | $0.37 |
| 3 | Debug ping-pong | $0.015 | $0.01 |
| 4 | Saída verbosa | $1.05 | $0.89 |
| 5 | Comandos sem encadear | $0.14 | $0.11 |
| 6 | Exploração do codebase | $0.09 | $0.07 |
| 7 | Edições sem agrupar | $0.058 | $0.05 |
| 8 | Releituras de arquivos | $0.066 | $0.05 |
| 9 | Loops sleep/poll | $0.043 | $0.034 |
| 10 | Tentativas falhas | $0.08 | $0.06 |
| 11 | Consultas de schema | $0.023 | $0.02 |
| 12 | Cerimônia Git | $0.003 | $0.003 |
| + | Compressão | $0.044 | $0.044 |
| + | Supressão de saída | $0.047 | $0.038 |
| | **Total** | **$3.15*** | **$2.61** |

*Padrões individuais podem coexistir no mesmo turno — totais refletem medição por padrão. Agregado real: $3.07 para $0.46 (ver Antes / Depois).

**Sessão típica com desperdício: $3.07. Após vibecheck: $0.46. Economia: 85%.**

- **Desperdício leve** (sessões curtas, poucos padrões): redução de 40-55%
- **Desperdício moderado** (usuário médio): redução de 55-70%
- **Desperdício alto** (sessões longas, múltiplos padrões): redução de 70-85%

### Agentes sempre ativos

| # | Padrão | Desperdício diário | Economia diária |
|---|---|---|---|
| 13 | Heartbeats ociosos | $11.20 | $9.70 |
| 14 | Inchaço do workspace | $5.76 | $3.76 |
| 15 | Acúmulo de memória | $3.17 | $2.37 |
| | **Total** | **$20.13/dia** | **$15.83/dia** |

**Economia mensal para agentes sempre ativos: ~$475.**

---

## Ferramentas suportadas

Mais de 24 ferramentas. Sem lock-in — vibecheck é um arquivo de texto, qualquer IA que lê instruções pode usá-lo. Os scripts de scan são Python puro, sem dependências.

**Scan completo de sessão** (lê seus logs, coloca valores no desperdício):
Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity

**Detecção + otimização de instruções** (sem parse completo de logs ainda, mas detecta a ferramenta e otimiza seus arquivos de configuração):
Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

**LLMs com dados de preços:** Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, mais 40+.

**Plataformas:** macOS, Windows, Linux, iPad via SSH. Python 3.8+.

---

<details>
<summary><strong>Metodologia</strong></summary>

Todas as estimativas de custo usam o cenário de referência acima. Premissas-chave:

- **95% de taxa de cache hit do prompt** — típico para sessões de coding rápidas. Sessões mais lentas com pausas mais longas entre turnos terão taxas de cache menores e custos maiores.
- **25 turnos produtivos/sessão** — sessões com desperdício adicionam 8-12 turnos extras por narração, tentativas e comandos sem encadear.
- **600 tokens/turno de crescimento** — sessões verbosas podem atingir 1.000-2.000 tokens por turno.
- **Tarifa de entrada efetiva: $0.435/1M** — tarifa ponderada de 95% cached ($0.30/1M) + 5% não cached ($3.00/1M).
- **Taxa de imposto de contexto: $0.30/1M** — tarifa de entrada cached para adições permanentes ao contexto.

Estimativas conservadoras. As economias reais frequentemente superam esses números, especialmente com sessões longas, arquivos de instruções grandes ou debugging intensivo.
</details>

## Autor

[Wallny](https://github.com/wallmage)
