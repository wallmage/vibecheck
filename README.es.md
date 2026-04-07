# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Tu herramienta de código IA está quemando dinero que no ves.**

Cada mensaje que envías, tu IA relee *toda* la conversación desde cero. El mensaje #50 cuesta 50x lo que costó el mensaje #1. Esa narración "OK, ahora voy a arreglar eso"? Te costó dinero y no hizo nada. Esas 500 líneas de logs de build? Se releen en cada. futuro. mensaje.

La mayoría de los vibe coders desperdician **más del 50%** de su presupuesto de tokens IA sin saberlo.

vibecheck lo arregla. Escanea tus últimos 14 días de sesiones, encuentra exactamente dónde está el desperdicio, lo explica en lenguaje claro (sin jerga — te enseñamos qué son los tokens), y aplica correcciones de un párrafo a tu archivo de configuración. Mismo trabajo. Mitad de costo.

**Ahorro promedio: 50%+ de tu factura de tokens.** Soporta todos los modelos LLM. Funciona con Claude Code, OpenClaw, Codex, OpenCode y 24+ herramientas de código IA. 100% local — tus datos nunca salen de tu máquina.

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## Privacidad

**Tus datos nunca salen de tu máquina.** Sin servidor, sin API, sin telemetría. Es técnicamente imposible que el autor recopile tus datos. El código es completamente open source.

## Instalación

**Herramientas de código IA (experiencia completa):** `claude install-skill https://github.com/wallmage/vibecheck`, luego `/vibecheck scan`.

**Entornos sandbox (Cowork, etc.):** Incluso sin escanear logs obtienes el 80% del beneficio — compresión del archivo de config, reglas de ahorro. Para el escaneo completo, pega un comando en tu terminal (solo últimos 14 días, ~20-50 MB).

## Comandos

- `/vibecheck scan` — Educación interactiva + diagnóstico completo + correcciones
- `/vibecheck explain` — Solo educación
- `/vibecheck compress` — Comprimir archivo de config (25-50% más pequeño)
- `/vibecheck monitor` — Comparación semanal + alertas

## 15 patrones de desperdicio

Narración inactiva, degradación de contexto, debugging ping-pong, salida verbosa, comandos sin encadenar, exploración del codebase, ediciones sin agrupar, relecturas de archivos, bucles sleep/poll, reintentos fallidos, búsquedas de schema, ceremonia Git, y para agentes 24/7: heartbeats inactivos, bloat del workspace, acumulación de memoria.

## Herramientas soportadas

24+: Claude Code, Cursor, Codex, Windsurf, Cline, OpenClaw, CodeBuddy, TRAE, Kimi Code y más.

Todos los LLM: Claude (Opus/Sonnet/Haiku), GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.
