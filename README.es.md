# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Cada turno de tu IA cuesta dinero.** Sonnet: ~$0.03/turno. Opus: ~$0.15/turno. Cuando la IA dice "OK, voy a arreglar eso" antes de arreglar — ese turno es desperdicio puro. Y empeora: cada turno relee toda la conversación desde el inicio. Cuanto más larga la conversación, más caro cada turno. Esto es inflación de contexto.

Las herramientas de código IA desperdician turnos constantemente — narrar en vez de actuar, leer 3 archivos uno por uno en vez de todos juntos, ejecutar `git add` y `git commit` por separado. vibecheck elimina el desperdicio de dos formas: menos turnos (agrupar, paralelizar, eliminar narración) + contexto más pequeño por turno (comprimir archivo de config, limpiar conversaciones largas). Estos son solo 2 de 15 mecanismos. Juntos reducen tu factura 50%+.

Soporta Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ herramientas. Ejecución local, tus datos nunca salen de tu máquina.

## Cómo instalar

Pega esto en tu herramienta de código IA y presiona Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

Listo. Tu IA hace el resto.

<details>
<summary>O instalación manual por línea de comandos</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Luego escribe `/vibecheck scan` en cualquier sesión

Actualizar: `cd ~/.claude/skills/vibecheck && git pull`
</details>

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
