# handoff

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | Español | [Italiano](README.it.md) | [Português](README.pt-BR.md)

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

**Tus conversaciones se degradan. Esta herramienta mantiene viva la senal.**

Cada chat de IA tiene una vida media. Cuanto mas largo es el hilo, mas contexto obsoleto relee el modelo, menos precisa es su salida y mas tokens desperdicias en ruido. Ya conoces la solucion: iniciar una sesion nueva. Pero entonces pierdes todas las decisiones tomadas, los bugs que ya rastreaste, la arquitectura que definiste. Asi que sigues en el hilo viejo y la calidad sigue cayendo.

`handoff` rompe ese ciclo. Di `handoff` en cualquier sesion y genera un bloque de transferencia unico -- compresion sin perdida, 2-4K tokens -- que captura todo lo importante: decisiones, descubrimientos, fallos, estado actual, problemas abiertos y proximos pasos. Pegalo en un chat nuevo y vuelves a velocidad maxima sin redescubrir nada.

Sin archivos. Sin plugins. Sin bases de datos. Solo copiar y pegar.

## Como funciona

**Modo generacion** -- en la sesion anterior, di `handoff`. El skill comprime toda la conversacion en un bloque de transferencia estructurado usando compresion sin perdida. No es un resumen superficial. Preserva resultados concretos -- que se decidio, que fallo, que esta a medias, que viene despues -- eliminando saludos, charla lateral, explicaciones repetidas y transcripciones sin procesar.

**Modo reanudacion** -- pega el bloque en una sesion nueva. El skill lo analiza, te da un resumen compacto del estado actual y espera tu siguiente instruccion.

El bloque de transferencia apunta a **2-4K tokens**. Lo suficientemente pequeno para usarlo con frecuencia. Lo suficientemente denso para no perder nada importante.

## Disparadores naturales

No necesitas recordar un comando especial. Cualquiera de estos funciona:

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## Que se preserva

- Decisiones y sus razones
- Descubrimientos tecnicos y mecanismos
- Experimentos fallidos y por que fallaron
- Numeros importantes, limites, versiones, tiempos, costos
- Branch / commit / estado dirty actual
- Trabajo no commiteado o parcialmente completado
- Problemas abiertos y bloqueadores
- La mejor siguiente accion

Que se descarta: saludos, palabras de aliento, intercambios repetitivos, volcados de codigo sin procesar, discusiones laterales que no cambiaron nada, narracion sobre lo que el asistente iba a hacer. La senal se queda. El ruido desaparece.

## Funciona en todas partes

`handoff` funciona con texto plano. Es compatible con:

- Herramientas de codigo (Claude Code, Cursor, Copilot, Windsurf)
- Herramientas CLI (asistentes de IA en terminal)
- Herramientas de chat GUI (ChatGPT, Claude chat, Gemini)
- Cualquier producto donde puedas pegar texto en una conversacion nueva

No requiere integracion especial.

## Cuando usarlo

- El chat actual se alarga y el modelo se vuelve lento
- Terminaste una parte del trabajo y quieres una sesion limpia
- Estas cerca del limite de contexto
- Quieres preservar decisiones sin mantener vivo todo el hilo anterior
- Estas cambiando de maquina o herramienta

## Instalacion

Copia esto en tu herramienta de IA:

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## Uso

En el chat anterior:

```text
handoff
```

Copia el bloque generado. Abre una sesion nueva. Pega.

Eso es todo.

---

Autor: [Wallny](https://github.com/wallmage)
