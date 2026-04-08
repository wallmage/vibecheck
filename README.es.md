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

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | Español | [Italiano](README.it.md) | [Português](README.pt-BR.md)

Cada tarde se me agotaba la cuota de Claude y no entendía por qué. Resultó que el 70% de mis sesiones de coding con IA eran desperdicio — la IA narrando lo que iba a hacer, comandos divididos en tres turnos cuando uno bastaba, contexto obsoleto acumulándose y releyéndose en cada turno.

vibecheck encuentra ese desperdicio. Lee los logs reales de tus sesiones en más de 24 herramientas de coding, pone cifras en dólares a 15 patrones específicos y los corrige. Todo se ejecuta localmente. Sin subidas, sin telemetría, sin servidores.

En mi caso: el gasto mensual pasó de $2,816 a $422. **85% de reducción.**

## Cómo instalar

Pega esto en tu herramienta de coding con IA y pulsa Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

Eso es todo. Tu IA carga el skill y estás listo para escanear.

<details>
<summary>O instala manualmente por línea de comandos</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Luego escribe `/vibecheck scan` en cualquier sesión.

Para actualizar: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### ¿Qué es exactamente un "skill"?

Un archivo de texto plano que enseña a tu IA algo nuevo. Sin binarios, sin procesos en segundo plano, sin modificaciones del sistema. El archivo skill de vibecheck dice "así se encuentra el desperdicio y se corrige". Borra la carpeta y desaparece.

### Herramientas de coding vs. herramientas de chat

**Las herramientas de coding** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, etc.) se ejecutan en tu máquina y dejan logs de sesión. vibecheck detecta automáticamente cuáles tienes y escanea esos logs directamente.

**Las herramientas de chat** (Cowork, Claude en navegador) se ejecutan en un sandbox sin logs locales. vibecheck aún optimiza tus archivos de instrucciones — de hecho, la mayor parte del ahorro viene de ahí. También puedes pegar un comando de terminal para exportar 14 días de logs y hacer un escaneo completo.

### Permisos

vibecheck lee tus logs de sesión locales e inspecciona archivos de instrucciones (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) y configuraciones globales de herramientas. Si tu herramienta tiene una configuración global — un archivo que cubre todos los proyectos — el optimizador va ahí primero, porque una corrección te ahorra dinero en todas partes. Pregunta antes de cambiar cualquier cosa.

## Privacidad

Todo se queda en tu máquina. El análisis es un conjunto de scripts Python que parsean tus logs de sesión locales. Sin servidor, sin llamadas API, sin analytics. Código abierto — lee cada línea si quieres.

## Comandos

| Comando | Qué hace |
|---|---|
| `/vibecheck scan` | Escanea todas las herramientas detectadas en tu máquina. Un informe unificado con indicadores de salud, estadísticas clasificadas, principales patrones de desperdicio y hoja de ruta de optimización |
| `/vibecheck explain` | Te enseña los patrones de desperdicio sin cambiar nada. Pura educación |
| `/vibecheck compress` | Reduce tus archivos de instrucciones un 25-50% con un compresor sin pérdida de 4 pasadas |
| `/vibecheck monitor` | Comparación semanal con tu línea base. Detecta regresiones de coste antes de que se acumulen |

El escaneo es discreto: un indicador de progreso compacto, luego un resumen limpio. `Good` significa desperdicio medido bajo 10%, `Waste` significa por encima. Los logs crudos y la salida de herramientas se quedan entre bastidores a menos que algo falle.

### Mantener las sesiones frescas

Las conversaciones largas cuestan más que las cortas — cada nuevo turno relee todos los anteriores, y el contexto sobrecargado hace que la IA sea menos precisa, lo que genera más ida y vuelta.

Regla general: 5-10 minutos activos por sesión, 30-40 turnos antes de que el impuesto de contexto empiece a pesar. Al iniciar una sesión nueva, mantén tus reglas permanentes en archivos de instrucciones (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) y el contexto del proyecto en documentos locales pequeños. Nueva sesión no significa arranque en frío — solo un contexto limpio con todo tu conocimiento intacto.

---

## Antes / Después

Medido en sesiones reales:

```
                          BEFORE         NOW            CHANGE
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## Cómo los turnos de IA cuestan dinero

Introducción rápida para quien nunca haya pensado en la economía de tokens. No se necesitan conocimientos previos sobre precios de IA.

### Qué ocurre en cada turno

Cada vez que tu IA responde, relee toda la conversación desde el principio. System prompt, archivo de instrucciones, cada mensaje que enviaste, cada respuesta que dio, toda la salida de herramientas — contenidos de archivos, resultados de terminal, logs de error — todo. Luego genera una nueva respuesta.

**Coste del turno = tokens leídos x precio de entrada + tokens generados x precio de salida**

Los primeros turnos son baratos. El turno 1 puede leer 5,000 tokens. En el turno 40, relee más de 40,000 tokens de conversación acumulada — cada mensaje anterior, cada snippet de código, cada traza de error. Ese turno tardío cuesta 8 veces más que el primero.

La clave: el desperdicio se **compone**. Un turno desperdiciado no solo cuesta sus propios tokens. Se queda en el contexto el resto de la sesión, releyéndose en cada turno futuro. Un mensaje de narración innecesario en el turno 10 se relee 30 veces más antes de terminar.

### El caché de prompt ayuda, pero no resuelve el problema

La mayoría de proveedores ahora cachean contenido ya visto y cobran 10 veces menos. El coste efectivo de entrada baja de $3.00/millón de tokens a $0.30/millón.

Ayuda. Pero el contenido nuevo — salida fresca de herramientas, nuevos mensajes de error, cada nueva respuesta de IA — siempre entra a precio completo antes de ser cacheado. Y el desperdicio se compone incluso a la tarifa cacheada.

### Las suscripciones sienten el mismo dolor

Si tienes suscripción, quizá pienses que los precios API no te afectan. Sí te afectan — solo los sientes de otra forma. Las suscripciones compran un pool fijo de cómputo, y el desperdicio consume ese pool más rápido. Cuando llegas a tu cuota y te limitan a las 3 de la tarde, no es porque hayas trabajado demasiado — es porque gran parte de ese trabajo fue desperdicio.

Claude Pro ($20/mes) cubre aproximadamente $200 en valor API equivalente. Claude 20x Max ($200/mes) cubre aproximadamente $4,000. Más desperdicio = muro más rápido.

<details>
<summary><strong>Análisis detallado: cuánto vale realmente tu suscripción en tokens</strong></summary>

### Cómo lo medí

Tenía el plan Claude 20x Max de $200/mes y me quedaba constantemente sin cuota. Lo suficientemente curioso como para cambiar a facturación API y rastrear el gasto real en más de 100 puntos de datos — registrando cada actividad de coding, verificando el consumo justo después. Eso me permitió calcular la relación entre el precio de suscripción y el valor real en tokens.

### Los multiplicadores

| Plan | Precio | Valor API | Multiplicador | Ventana 5h | Total semanal |
|---|---|---|---|---|---|
| Claude Pro | $20/mes | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mes | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mes | ~$4,000 | 20x | $133.33 | $933.31 |

El tier 20x Max es el único con un salto real de multiplicador — 20x el valor nominal frente a 10x en los tiers inferiores.

### En la práctica

- **$20 Claude Pro** — trabajo de desarrollo serio (implementar features, investigación, documentación) consume tu cuota de 5 horas en menos de una hora. Capacidad semanal bajo 7 horas. Justo para cualquier uso profesional.
- **$100 5x Max** — unas 4 horas antes de llegar a la ventana de 5 horas. 30-35 horas/semana en total. Viable para uso regular.
- **$200 20x Max** — diseñado para quienes trabajan 80-100+ horas/semana, a menudo ejecutando múltiples sesiones en paralelo.

### Por qué Anthropic restringió el uso de suscripciones por terceros

A 10-20x el valor nominal, cada dólar de suscripción compra mucho más cómputo que la tarifa API. Herramientas de terceros consumiéndolo a velocidad equivalente API hacían las cuentas insostenibles.

### La alternativa Codex

En el tier de $20, Codex Plus ofrece aproximadamente **3 veces el uso de coding** de Claude Pro. Las conversaciones de ChatGPT — incluso GPT-5.4 Extended Thinking e investigación profunda — no cuentan contra la cuota de coding de Codex. Obtienes 3x la capacidad de coding más GPT-5.4 gratis.

**Si tu presupuesto es $20/mes, Codex Plus te da más tiempo de coding que Claude Pro.** Si puedes gastar más, los tiers Claude 5x y 20x ofrecen una propuesta de valor diferente.

</details>

### Escenario de referencia

Todas las cifras en este documento usan esta línea base (precios de Sonnet 4.6):

| Parámetro | Valor |
|---|---|
| Duración de sesión | 25 turnos |
| Contexto inicial | 21,000 tokens |
| Crecimiento por turno | ~600 tokens |
| Tasa de acierto de caché | 95% |
| Coste por turno (mitad de sesión) | $0.017 |
| Total sesión eficiente | $0.41 |

Para Opus 4.6, multiplica todos los costes por 1.67x.

---

## Los 15 patrones de desperdicio

Organizados por cuánto dinero queman. Los tres primeros solos representan el 60-70% de todo el desperdicio.

### Tier 1 — Los tres grandes (60-70% del desperdicio)

#### 1. Narración ociosa

Tu IA dice "OK, voy a corregir eso" o "Déjame leer el archivo primero" — y luego hace el trabajo en el siguiente turno. Ese turno de narración no hizo nada. Sin llamada a herramienta, sin código, sin lectura de archivo. Solo un anuncio.

Cada uno cuesta alrededor de **$0.017** — y peor, esos 300-500 tokens de texto de estado se quedan en el contexto, releyéndose en cada turno futuro. En 428 sesiones medidas: **$1.03/sesión desperdiciados**, 30% de todo el desperdicio. A 10 sesiones/día: **$309/mes solo en narración.**

Regla vibecheck: *"Ningún turno sin llamada a herramienta. Piensa y actúa en el mismo turno."* **Ahorra ~$0.88/sesión.**

#### 2. Deterioro del contexto

El coste de sesión crece cuadráticamente, no linealmente. El turno 50 relee los 49 turnos anteriores.

Comparación concreta: una sesión de 40 turnos cuesta **$0.70**. El mismo trabajo dividido en dos sesiones de 20 turnos: **$0.60**. Esos $0.10 de diferencia son puro desperdicio por mantener una conversación inflada. Las sesiones reales promedian 74 turnos — **$0.46/sesión desperdiciados**, 13% de todo el desperdicio.

vibecheck enseña: *"Los trabajos no relacionados van en sesiones separadas. En hilos largos, mantente compacto."* **Ahorra ~$0.37/sesión.**

#### 3. Depuración ping-pong

Corregir, romper, reintentar, romper otra vez. Cada intento fallido inyecta ~4,000 tokens de error en el contexto, y ese texto muerto se relee en cada turno posterior. Tres ciclos: 6 turnos extra ($0.102) + 12K tokens de errores obsoletos ($0.036) = **~$0.14 por episodio**. Ocurre en ~10% de las sesiones. **Ponderado: $0.015/sesión.**

Interruptor vibecheck: *"Después de 2 correcciones fallidas en el mismo archivo — para, relee el error completo, piensa, una corrección precisa."* **Ahorra ~$0.01/sesión.**

### Tier 2 — Densidad de turnos (15-20% del desperdicio)

Hacer en tres turnos lo que debería tomar uno.

#### 4. Salida de herramienta verbosa

Un comando de build o test vuelca 500 líneas (~5,000 tokens) en la conversación. Esos tokens se releen en cada turno restante. 5K tokens x 12 turnos restantes a tarifa cacheada = **$0.018/instancia**. Sin caché: **$0.180** — 10x peor.

Es el patrón más costoso individualmente. Logs de build, salida de npm, dumps de tests — inundan casi todas las sesiones. **$1.05/sesión**, 31% de todo el desperdicio.

Corrección: *"Redirigir salida a /tmp/. Usar flags --quiet. tail -50 máximo."* **Ahorra ~$0.89/sesión.**

#### 5. Comandos sin encadenar

`npm install` en un turno. `npm run build` en el siguiente. Dos relecturas de contexto para lo que `npm install && npm run build` hace en uno. Cada división: **$0.010**. Suma **$0.14/sesión** en sesiones intensivas en comandos.

Corrección: *"Encadenar comandos con `&&` cuando sea seguro."* **Ahorra ~$0.11/sesión.**

#### 6. Exploración del codebase

La IA abre README, package.json, tres configs y dos módulos no relacionados antes de escribir una sola línea de código. Cinco lecturas consecutivas, sin ediciones, sin decisiones. $0.085 en turnos desperdiciados + $0.027 impuesto de contexto = **$0.112/episodio.** Promedio: **$0.09/sesión.**

Corrección: grep o glob primero, leer solo lo relevante, agrupar múltiples lecturas por turno. **Ahorra ~$0.07/sesión.**

#### 7. Ediciones sin agrupar

Editar archivo A, luego B, luego C — tres turnos. Un turno con ediciones paralelas hace lo mismo. Dos turnos extra a $0.017 = **$0.034/instancia.** Promedio: **$0.058/sesión.**

Corrección: *"Agrupar llamadas de herramientas independientes."* **Ahorra ~$0.05/sesión.**

### Tier 3 — La cola (5-10% del desperdicio)

Pequeños individualmente. Se acumulan.

#### 8. Relecturas de archivos

El mismo archivo leído dos veces en una sesión — el contenido ya está en contexto, pero la IA lo vuelve a obtener. **$0.019/relectura**, los archivos se releen 3-4 veces en promedio. **$0.066/sesión.** Corrección: *"Ya está en contexto. Releer solo si el archivo cambió."* **Ahorra ~$0.05/sesión.**

#### 9. Bucles sleep/poll

`sleep 5 && check_status`, repetido 3-5 veces. Cada poll = relectura completa del contexto para ver si un proceso en segundo plano terminó. 4 polls x $0.017 = **$0.068/episodio**, **$0.043/sesión.** Corrección: *"Usar --wait o run_in_background."* **Ahorra ~$0.034/sesión.**

#### 10. Reintentos fallidos

Comando falla, la IA ejecuta el mismo comando sin cambios. La salida de error ahora está duplicada en el contexto. **$0.019/reintento**, **$0.080/sesión.** Corrección: igual que el ping-pong — *"Para, lee el error, intenta algo diferente."*

#### 11. Consultas de esquema

La IA consulta sus propias definiciones de herramientas — información que ya tiene. Añade 2K+ tokens innecesariamente. **$0.023/sesión.** La regla "ningún turno sin llamada a herramienta" resuelve esto. **Ahorra ~$0.02/sesión.**

#### 12. Ceremonia Git

`git add` → `git status` → `git commit` → `git push`. Cuatro turnos. `git add -A && git commit -m "msg" && git push` es uno. **$0.044/instancia** pero menos frecuente de lo esperado — **$0.003/sesión.** Corrección: encadenar con `&&`.

### Tier 4 — Agentes siempre activos

Modelo de coste diferente. Agentes como OpenClaw despiertan periódicamente, y el desperdicio se mide por día, no por sesión.

#### 13. Heartbeats ociosos

El agente despierta cada 5 minutos, relee todo el workspace, no encuentra nada, vuelve a dormir. 288 despertares/día, ~97% ociosos. Son 280 despertares ociosos a $0.04 cada uno = **$11.20/día ($336/mes)** sin hacer nada.

Corrección: *"Heartbeat mínimo de 30 minutos. Saltar si no hay triggers pendientes."* Reduce a ~48 despertares/día. **Ahorra $8-10/día ($240-300/mes).**

#### 14. Inflación del workspace

35,000 tokens de archivos de personalidad (SOUL.md, AGENTS.md, etc.) releídos en cada despertar. Tutoriales, coaching, filosofía — escritos para humanos, no para una IA ejecutando tareas. **$5.76/día ($173/mes)** solo en archivos de configuración.

vibecheck los comprime: 35K → 12-15K tokens. Mismas reglas de comportamiento, sin relleno para humanos. **Ahorra $3-4/día ($90-120/mes).**

#### 15. Acumulación de memoria

El historial de sesiones crece sin límite. Más de 100 entradas de memoria releídas en cada despertar, incluyendo cosas de hace semanas que ya no importan. **$3.17/día ($95/mes)** en memorias obsoletas.

Corrección: *"Archivar después de 50 entradas, resumir, empezar de nuevo."* **Ahorra $2-3/día ($60-90/mes).**

---

## El kit de optimización

vibecheck no solo señala problemas — los corrige.

### Compresión de archivos de instrucciones

Tu archivo de instrucciones (`CLAUDE.md`, `AGENTS.md`, `Memory.md`, como lo llame tu herramienta) se lee en cada turno. Es un impuesto fijo sobre todo lo que haces. Un archivo de instrucciones inflado es un peaje en cada carretera de la ciudad.

vibecheck tiene un compresor sin pérdida de 4 pasadas — 23 técnicas, y "sin pérdida" significa literalmente que no se elimina ningún dato. Misma información, menos tokens.

| Pasada | Qué hace | Cuánto ahorra |
|---|---|---|
| **Pasada 1 — Mecánica** | Elimina formato markdown, convierte tablas a forma compacta, fusiona viñetas | 10-15% |
| **Pasada 2 — Preservación de datos** | Deduplica datos repetidos, comprime ejemplos de código, colapsa descripciones verbosas | 15-25% |
| **Pasada 3 — Alta fidelidad** | Elimina tutoriales y texto de coaching que los humanos necesitan pero la IA no | 10-15% |
| **Pasada 4 — Telegrama** | Reescritura completa en taquigrafía para archivos solo-IA. Denso, comprimido — solo con tu permiso explícito | 15-25% |

Un archivo de instrucciones de 10,000 tokens comprimido a 6,000 ahorra $0.044 por sesión. A 10 sesiones por día: **$0.44/día ($13/mes)** solo de compresión.

### Supresión de salida

Los tokens de salida cuestan 5x más que los de entrada ($15 vs. $3/millón en Sonnet 4.6). ¿La IA imprimiendo bloques de código o diffs que no pediste? Caro. vibecheck añade: *"Sin código ni diffs a menos que se pidan."* **Ahorra ~$0.047/sesión.**

### Monitoreo de costes

`/vibecheck monitor` toma una instantánea de tu perfil de sesión y la compara con la línea base en ejecuciones futuras. ¿Un nuevo archivo de instrucciones introdujo verbosidad? ¿Proyecto diferente, hábitos diferentes? El monitor detecta regresiones antes de que se acumulen.

---

## Resumen de ahorros

### Herramientas interactivas (precios Sonnet 4.6)

| # | Patrón | Desperdicio medio/sesión | Ahorro medio |
|---|---|---|---|
| 1 | Narración ociosa | $1.03 | $0.88 |
| 2 | Deterioro del contexto | $0.46 | $0.37 |
| 3 | Depuración ping-pong | $0.015 | $0.01 |
| 4 | Salida verbosa | $1.05 | $0.89 |
| 5 | Comandos sin encadenar | $0.14 | $0.11 |
| 6 | Exploración del codebase | $0.09 | $0.07 |
| 7 | Ediciones sin agrupar | $0.058 | $0.05 |
| 8 | Relecturas de archivos | $0.066 | $0.05 |
| 9 | Bucles sleep/poll | $0.043 | $0.034 |
| 10 | Reintentos fallidos | $0.08 | $0.06 |
| 11 | Consultas de esquema | $0.023 | $0.02 |
| 12 | Ceremonia Git | $0.003 | $0.003 |
| + | Compresión | $0.044 | $0.044 |
| + | Supresión de salida | $0.047 | $0.038 |
| | **Total** | **$3.15*** | **$2.61** |

*Los patrones individuales pueden coexistir en el mismo turno — los totales reflejan mediciones por patrón. Agregado real: $3.07 a $0.46 (ver Antes / Después).

**Sesión típica con desperdicio: $3.07. Después de vibecheck: $0.46. Ahorro: 85%.**

- **Desperdicio leve** (sesiones cortas, pocos patrones): reducción del 40-55%
- **Desperdicio moderado** (usuario promedio): reducción del 55-70%
- **Desperdicio alto** (sesiones largas, múltiples patrones): reducción del 70-85%

### Agentes siempre activos

| # | Patrón | Desperdicio diario | Ahorro diario |
|---|---|---|---|
| 13 | Heartbeats ociosos | $11.20 | $9.70 |
| 14 | Inflación del workspace | $5.76 | $3.76 |
| 15 | Acumulación de memoria | $3.17 | $2.37 |
| | **Total** | **$20.13/día** | **$15.83/día** |

**Ahorro mensual para agentes siempre activos: ~$475.**

---

## Herramientas soportadas

Más de 24 herramientas. Sin lock-in — vibecheck es un archivo de texto, cualquier IA que lea instrucciones puede usarlo. Los scripts de escaneo son Python puro, sin dependencias.

**Escaneo completo de sesión** (lee tus logs, pone cifras al desperdicio):
Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity

**Detección + optimización de instrucciones** (sin parseo completo de logs aún, pero detecta la herramienta y optimiza tus archivos de configuración):
Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

**LLMs con datos de precios:** Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, más 40+.

**Plataformas:** macOS, Windows, Linux, iPad via SSH. Python 3.8+.

---

<details>
<summary><strong>Metodología</strong></summary>

Todas las estimaciones de coste usan el escenario de referencia anterior. Supuestos clave:

- **95% de tasa de acierto de caché de prompt** — típico para sesiones de coding rápidas. Sesiones más lentas con pausas más largas entre turnos tendrán tasas de caché más bajas y costes más altos.
- **25 turnos productivos/sesión** — las sesiones con desperdicio añaden 8-12 turnos extra por narración, reintentos y comandos sin encadenar.
- **600 tokens/turno de crecimiento** — sesiones verbosas pueden alcanzar 1,000-2,000 tokens por turno.
- **Tarifa de entrada efectiva: $0.435/1M** — tarifa ponderada de 95% cacheado ($0.30/1M) + 5% no cacheado ($3.00/1M).
- **Tasa de impuesto de contexto: $0.30/1M** — tarifa de entrada cacheada para adiciones permanentes al contexto.

Estimaciones conservadoras. Los ahorros reales suelen superar estas cifras, especialmente con sesiones largas, archivos de instrucciones grandes o depuración intensiva.
</details>

## Autor

[Wallny](https://github.com/wallmage)
