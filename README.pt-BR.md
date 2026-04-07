# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Sua ferramenta de código IA está queimando dinheiro que você não vê.**

Cada mensagem que você envia, sua IA relê *toda* a conversa do zero. A mensagem #50 custa 50x a #1. Aquela narração "OK, agora vou corrigir isso"? Custou dinheiro e não fez nada. Aquelas 500 linhas de log? Relidas em cada futura mensagem.

A maioria dos vibe coders desperdiça **mais de 50%** do orçamento de tokens sem saber.

vibecheck resolve isso. Escaneia seus últimos 14 dias, encontra o desperdício, explica em linguagem simples, e aplica correções de um parágrafo. Mesmo trabalho. Metade do custo.

**Economia média: 50%+ da sua conta de tokens.** Suporta todos os modelos LLM (Claude, GPT, Gemini, DeepSeek). Funciona com Claude Code, OpenClaw, Codex, OpenCode, Cursor, Windsurf e 24+ ferramentas. 100% local — seus dados nunca saem da sua máquina.

## Comece agora — nada para baixar

vibecheck é uma **skill** — um conjunto de instruções que sua ferramenta de código IA aprende. Você não baixa nem instala nenhum software. Dê um link para sua IA e ela aprende sozinha a otimizar seus custos. Uma mensagem e pronto.

**Copie isso na sua ferramenta de código IA** (Claude Code, Cursor, Codex, Windsurf, Cline):

> Instale a skill vibecheck de https://github.com/wallmage/vibecheck e execute /vibecheck scan

É isso. Sua IA lê a skill, escaneia 14 dias e explica tudo.

**Ou pelo CLI:**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

**Ferramentas sandbox (Cowork, etc.):**
> Clone https://github.com/wallmage/vibecheck em /tmp/vibecheck, leia SKILL.md, e execute /vibecheck scan

### O que é uma "skill"?

Uma skill é como uma receita para sua IA. Não modifica sua IA nem instala nada. Só dá instruções — "como encontrar padrões de desperdício, explicar e corrigir." Removível a qualquer momento.

### Ferramentas de código vs ferramentas de chat

**Ferramentas de código** (Claude Code CLI, Cursor, Codex etc.): acesso direto aos logs. Scan completo personalizado.

**Ferramentas chat/sandbox** (Cowork etc.): veem arquivos do projeto mas não o histórico de chat.

1. **Sem scan (80% do benefício):** Otimiza o arquivo de config. Sem necessidade de logs.
2. **Com scan (100%):** Um comando no terminal — apenas os últimos 14 dias (~20-50 MB).

### Permissões

Precisa de acesso à **pasta do projeto** para ler/editar o arquivo de configuração. Pede permissão antes de cada mudança.

## Privacidade

**Seus dados nunca saem da sua máquina.** Sem servidor, sem API, sem telemetria. Código completamente open source.

## Comandos

- `/vibecheck scan` — Educação interativa + diagnóstico + correções
- `/vibecheck explain` — Apenas educação
- `/vibecheck compress` — Comprimir arquivo de config (25-50%)
- `/vibecheck monitor` — Comparação semanal + alertas

## 15 padrões de desperdício

**Nível 1 (70-80%):** Narração ociosa, deterioração de contexto, debugging ping-pong
**Nível 2 (15-20%):** Saída verbosa, comandos não encadeados, exploração do codebase, edições não agrupadas
**Nível 3 (5-10%):** Releituras, loops sleep/poll, retries falhos, buscas de schema, cerimônia Git
**Nível 4 — Agentes 24/7:** Heartbeats inativos, bloat do workspace, acúmulo de memória

## Ferramentas suportadas

24+. Todos os LLM: Claude, GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.

macOS, Windows, Linux, iPad/mobile via SSH. Python 3.8+, sem dependências externas.
