# handoff

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | Português

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

**Suas conversas se degradam. Esta ferramenta mantém o sinal vivo.**

Todo chat de IA tem uma meia-vida. Quanto mais longa a thread, mais contexto obsoleto o modelo relê, menos precisa fica a saída e mais tokens você desperdiça com ruído. Você já sabe a solução: iniciar uma sessão nova. Mas aí você perde todas as decisões tomadas, os bugs já rastreados, a arquitetura definida. Então você continua na thread antiga e a qualidade segue caindo.

`handoff` quebra esse ciclo. Diga `handoff` em qualquer sessão e ele gera um bloco de transferência único -- compressão sem perda, 2-4K tokens -- que captura tudo que importa: decisões, descobertas, falhas, estado atual, problemas em aberto e próximos passos. Cole em um chat novo e você volta à velocidade máxima sem precisar redescobrir nada.

Sem arquivos. Sem plugins. Sem bancos de dados. Só copiar e colar.

## Como funciona

**Modo geração** -- na sessão antiga, diga `handoff`. A skill comprime toda a conversa em um bloco de transferência estruturado usando compressão sem perda. Não é um resumo superficial. Preserva resultados concretos -- o que foi decidido, o que falhou, o que está pela metade, o que vem a seguir -- eliminando saudações, conversa paralela, explicações repetidas e transcrições brutas.

**Modo retomada** -- cole o bloco em uma sessão nova. A skill analisa o conteúdo, apresenta um resumo compacto do estado atual e aguarda sua próxima instrução.

O bloco de transferência tem como alvo **2-4K tokens**. Pequeno o suficiente para usar com frequência. Denso o suficiente para não perder nada importante.

## Gatilhos naturais

Não precisa lembrar de nenhum comando especial. Qualquer um destes funciona:

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## O que é preservado

- Decisões e suas justificativas
- Descobertas técnicas e mecanismos
- Experimentos que falharam e por quê
- Números importantes, limites, versões, tempos, custos
- Branch / commit / estado dirty atual
- Trabalho não commitado ou parcialmente concluído
- Problemas em aberto e bloqueadores
- A melhor próxima ação

O que é descartado: saudações, palavras de incentivo, trocas repetitivas, dumps de código bruto, discussões laterais que não mudaram nada, narração sobre o que o assistente ia fazer. O sinal fica. O ruído desaparece.

## Funciona em qualquer lugar

`handoff` funciona com texto puro. É compatível com:

- Ferramentas de código (Claude Code, Cursor, Copilot, Windsurf)
- Ferramentas CLI (assistentes de IA no terminal)
- Ferramentas de chat GUI (ChatGPT, Claude chat, Gemini)
- Qualquer produto onde você possa colar texto em uma conversa nova

Nenhuma integração especial necessária.

## Quando usar

- O chat atual está ficando longo e o modelo está ficando lento
- Você terminou uma parte do trabalho e quer uma sessão limpa
- Está chegando perto do limite de contexto
- Quer preservar decisões sem manter toda a thread antiga viva
- Está trocando de máquina ou ferramenta

## Instalação

Copie isto na sua ferramenta de IA:

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## Uso

No chat antigo:

```text
handoff
```

Copie o bloco gerado. Abra uma sessão nova. Cole.

É isso.

---

Autor: [Wallny](https://github.com/wallmage)
