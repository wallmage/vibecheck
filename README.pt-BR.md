# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Cada turno da sua IA custa dinheiro.** Sonnet 4.6: $3/$15 por MTok (entrada/saída). Opus 4.6: $5/$25 — 1,67x mais caro. Um turno no meio da sessão no Sonnet custa ~$0.038. Quando a IA diz "OK, vou corrigir isso" antes de corrigir — esses $0.031 são desperdício puro. E piora: cada turno relê toda a conversa do início. Quanto mais longa a conversa, mais caro cada turno. Isso é inflação de contexto.

Ferramentas de código IA desperdiçam turnos constantemente — narrar em vez de agir, ler arquivos um por um, executar `git add` e `git commit` separadamente. vibecheck detecta 18 mecanismos em 4 níveis, corrige com regras no arquivo de config e compressão, e monitora melhorias. Reduz sua conta em 40-65% dependendo do padrão de uso. [Especificações detalhadas →](SPECSHEET.md)

Suporta Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ ferramentas. Execução local, seus dados nunca saem da sua máquina.

## Como instalar

Cole isso na sua ferramenta de código IA e pressione Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

Pronto. Sua IA faz o resto.

<details>
<summary>Ou instalação manual por linha de comando</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Depois digite `/vibecheck scan` em qualquer sessão

Atualizar: `cd ~/.claude/skills/vibecheck && git pull`
</details>

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

## 18 mecanismos

**Nível 1 (70-80%):** Narração ociosa, deterioração de contexto, debugging ping-pong
**Nível 2 (15-20%):** Saída verbosa, comandos não encadeados, exploração do codebase, edições não agrupadas
**Nível 3 (5-10%):** Releituras, loops sleep/poll, retries falhos, buscas de schema, cerimônia Git
**Nível 4 — Agentes 24/7:** Heartbeats inativos, bloat do workspace, acúmulo de memória

## Ferramentas suportadas

24+. Todos os LLM: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7 e 40+ outros.

macOS, Windows, Linux, iPad/mobile via SSH. Python 3.8+, sem dependências externas.
