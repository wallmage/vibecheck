# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Sua ferramenta de código IA está queimando dinheiro que você não vê.**

Cada mensagem que você envia, sua IA relê *toda* a conversa do zero. A mensagem #50 custa 50x o que custou a mensagem #1. Aquela narração "OK, agora vou corrigir isso"? Custou seu dinheiro e não fez nada. Aquelas 500 linhas de log de build? Relidas em cada. futura. mensagem.

A maioria dos vibe coders desperdiça **mais de 50%** do seu orçamento de tokens IA sem saber.

vibecheck resolve isso. Escaneia seus últimos 14 dias de sessões, encontra exatamente onde está o desperdício, explica em linguagem simples (sem jargão — vamos te ensinar o que são tokens), e aplica correções de um parágrafo no seu arquivo de configuração. Mesmo trabalho. Metade do custo.

**Economia média: 50%+ da sua conta de tokens.** Suporta todos os modelos LLM. Funciona com Claude Code, OpenClaw, Codex, OpenCode e 24+ ferramentas de código IA. 100% local — seus dados nunca saem da sua máquina.

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## Privacidade

**Seus dados nunca saem da sua máquina.** Sem servidor, sem API, sem telemetria. É tecnicamente impossível o autor coletar seus dados. O código é completamente open source.

## Instalação

**Ferramentas de código IA (experiência completa):** `claude install-skill https://github.com/wallmage/vibecheck`, depois `/vibecheck scan`.

**Ambientes sandbox (Cowork, etc.):** Mesmo sem escanear logs você obtém 80% do benefício — compressão do arquivo de config, regras de economia. Para o scan completo, cole um comando no seu terminal (apenas últimos 14 dias, ~20-50 MB).

## Comandos

- `/vibecheck scan` — Educação interativa + diagnóstico completo + correções
- `/vibecheck explain` — Apenas educação
- `/vibecheck compress` — Comprimir arquivo de config (25-50% menor)
- `/vibecheck monitor` — Comparação semanal + alertas

## 15 padrões de desperdício

Narração ociosa, deterioração de contexto, debugging ping-pong, saída verbosa, comandos não encadeados, exploração do codebase, edições não agrupadas, releituras de arquivo, loops sleep/poll, retries falhos, buscas de schema, cerimônia Git, e para agentes 24/7: heartbeats inativos, bloat do workspace, acúmulo de memória.

## Ferramentas suportadas

24+: Claude Code, Cursor, Codex, Windsurf, Cline, OpenClaw, CodeBuddy, TRAE, Kimi Code e mais.

Todos os LLM: Claude (Opus/Sonnet/Haiku), GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.
