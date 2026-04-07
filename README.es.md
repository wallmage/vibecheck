# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Tu herramienta de código IA está quemando dinero que no ves.**

Cada mensaje que envías, tu IA relee *toda* la conversación desde cero. El mensaje #50 cuesta 50x lo que costó el #1. Esa narración "OK, ahora voy a arreglar eso"? Te costó dinero y no hizo nada. Esas 500 líneas de logs? Se releen en cada futuro mensaje.

La mayoría de los vibe coders desperdician **más del 50%** de su presupuesto de tokens sin saberlo.

vibecheck lo arregla. Escanea tus últimos 14 días, encuentra el desperdicio, lo explica en lenguaje claro, y aplica correcciones de un párrafo. Mismo trabajo. Mitad de costo.

**Ahorro promedio: 50%+ de tu factura de tokens.** Soporta todos los modelos LLM (Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax). Funciona con Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf y 24+ herramientas. 100% local — tus datos nunca salen de tu máquina.

## Empieza ya — nada que descargar

vibecheck es un **skill** — un conjunto de instrucciones que tu herramienta de código IA aprende. No descargas ni instalas ningún software. Dale un enlace a tu IA y aprende sola a optimizar tus costos. Un mensaje y listo.

**Copia esto en tu herramienta de código IA** (Claude Code, Cursor, Codex, Windsurf, Cline):

> Instala el skill vibecheck desde https://github.com/wallmage/vibecheck y ejecuta /vibecheck scan

Eso es todo. Tu IA lee el skill, escanea 14 días y te explica todo.

**O por CLI:**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

**Herramientas sandbox (Cowork, etc.):**
> Clona https://github.com/wallmage/vibecheck en /tmp/vibecheck, lee SKILL.md, y ejecuta /vibecheck scan

### ¿Qué es un "skill"?

Un skill es como una receta para tu IA. No modifica tu IA ni instala nada. Solo le da instrucciones — "cómo encontrar patrones de desperdicio, explicarlos y corregirlos." Se puede eliminar en cualquier momento.

### Herramientas de código vs herramientas de chat

**Herramientas de código** (Claude Code CLI, Cursor, Codex etc.): acceso directo a logs. Escaneo completo personalizado.

**Herramientas chat/sandbox** (Cowork etc.): ven archivos del proyecto pero no el historial de chat.

1. **Sin escaneo (80% del beneficio):** Optimiza el archivo de config. Sin necesidad de logs.
2. **Con escaneo (100%):** Un comando en tu terminal — solo los últimos 14 días (~20-50 MB).

### Permisos

Necesita acceso a tu **carpeta de proyecto** para leer/editar el archivo de configuración. Pide permiso antes de cada cambio.

## Privacidad

**Tus datos nunca salen de tu máquina.** Sin servidor, sin API, sin telemetría. Código completamente open source.

## Comandos

- `/vibecheck scan` — Educación interactiva + diagnóstico + correcciones
- `/vibecheck explain` — Solo educación
- `/vibecheck compress` — Comprimir archivo de config (25-50%)
- `/vibecheck monitor` — Comparación semanal + alertas

## 15 patrones de desperdicio

**Nivel 1 (70-80%):** Narración inactiva, degradación de contexto, debugging ping-pong
**Nivel 2 (15-20%):** Salida verbosa, comandos sin encadenar, exploración del codebase, ediciones sin agrupar
**Nivel 3 (5-10%):** Relecturas, bucles sleep/poll, reintentos fallidos, búsquedas de schema, ceremonia Git
**Nivel 4 — Agentes 24/7:** Heartbeats inactivos, bloat del workspace, acumulación de memoria

## Herramientas soportadas

24+. Todos los LLM: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7 y 40+ más.

macOS, Windows, Linux, iPad/móvil via SSH. Python 3.8+, sin dependencias externas.
