# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Cada turno que da tu IA cuesta dinero.** Sonnet 4.6: $3/$15 por millón de tokens (entrada/salida). Opus 4.6: $5/$25 — 1.67x más caro. Esto es lo que significa en la práctica:

- Tu IA dice "Claro, lo arreglo" antes de arreglarlo. Ese turno de narración: **$0.031 desperdiciado.** Cinco por sesión: **$0.165 perdidos.**
- Tu conversación llega a 40 turnos en vez de dividirse en 20. Coste extra de releer todo ese historial: **$0.67 desperdiciado.**
- `git add`, luego `git commit`, luego `git push` — tres turnos en lugar de un comando encadenado: **$0.098 desperdiciado.**

Estos son 3 de los 15 patrones de desperdicio que detecta vibecheck. Cada uno explicado a continuación con importes en dólares, qué falla y cómo lo corregimos.

Funciona con Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. Más de 24 herramientas de programación. Se ejecuta localmente — tus datos permanecen en tu máquina.

## Cómo instalar

Pega esto en tu herramienta de programación con IA y pulsa Intro:

> Help me install this skill: https://github.com/wallmage/vibecheck

Eso es todo. Tu IA hace el resto.

<details>
<summary>O instala manualmente desde la línea de comandos</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Luego escribe `/vibecheck scan` en cualquier sesión.

Para actualizar: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### ¿Qué es una skill?

Una tarjeta de receta para tu IA. No modifica nada ni instala nada. Es solo un archivo de texto que dice "así se detecta el desperdicio y se corrige." Bórrala cuando quieras.

### Herramientas de programación vs. herramientas de chat

**Herramientas de programación** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, etc.) se ejecutan en tu máquina — vibecheck detecta automáticamente tu herramienta y analiza los registros de tu sesión.

**Herramientas de chat** (Cowork, basadas en navegador) se ejecutan en un sandbox. vibecheck igualmente optimiza tu archivo de instrucciones (donde está la mayor parte del beneficio), o puedes pegar un comando de terminal para copiar 14 días de registros y hacer un análisis completo.

### Permisos

vibecheck lee y edita tu archivo de instrucciones (CLAUDE.md, .cursorrules, etc.). Pregunta antes de cada cambio.

## Privacidad

Tus datos no salen de tu máquina. Sin servidor, sin API, sin telemetría. Código abierto.

## Comandos

- `/vibecheck scan` — te enseña qué son los tokens, analiza tus sesiones y aplica correcciones
- `/vibecheck explain` — solo la lección, sin cambios
- `/vibecheck compress` — reduce tu archivo de instrucciones un 25-50%
- `/vibecheck monitor` — comparación semanal, detecta regresiones

## Antes / Después

```
                          ANTES          AHORA          CAMBIO
Turnos medios/sesión      36.8           25.9           -10.9
Ventana de context media  128.4K         89.9K          -30%
Turnos con desperdicio    36.7%          8.1%           -28.6%

Coste medio/sesión        $2.62          $1.35          -$1.27
Gasto mensual             $224           $115           -$109
```

---

## Cómo los turnos cuestan dinero

En cada turno, tu IA relee toda la conversación — el system prompt, el archivo de instrucciones, todos los mensajes anteriores y toda la salida de herramientas — y luego genera una respuesta.

**Coste por turno = tokens de entrada x tarifa de entrada + tokens de salida x tarifa de salida**

Los primeros turnos son baratos (context pequeño). Los turnos tardíos son caros (todo lo anterior se relee). Por eso el desperdicio se acumula — un turno malgastado encarece todos los turnos futuros, porque el contenido desperdiciado permanece en el context.

El prompt caching reduce el coste de entrada 10x para contenido ya visto. La mayoría de las herramientas lo usan automáticamente.

**Usuarios con suscripción:** No ves directamente los precios de la API, pero el desperdicio agota tu cuota de mensajes más rápido. Claude Pro ($20/mes) equivale a ~$200 en valor de API. Max ($200/mes) equivale a ~$4,000.

<details>
<summary><strong>Investigación: Cuánto vale realmente tu suscripción en tokens</strong></summary>

### Cómo lo medí

Tengo el plan Claude 20x Max de $200/mes y constantemente agotaba mi cuota. Así que me pregunté: ¿cuánto uso de API compra realmente cada tier?

Cambié a facturación por API y rastreé el gasto real en dólares en más de 100 puntos de datos — cada actividad seguida de una actualización de consumo. Suficiente para calcular la relación lineal entre precio de suscripción y valor en tokens.

### Los multiplicadores

| Plan | Precio | Valor API | Multiplicador | Ventana 5h | Total semanal |
|---|---|---|---|---|---|
| Claude Pro | $20/mes | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mes | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mes | ~$4,000 | 20x | $133.33 | $933.31 |

Solo el tier 20x Max ofrece un aumento real de multiplicador (20x vs. 10x en los tiers inferiores).

### Uso real en horas

- **$20 Claude Pro** — trabajo serio (desarrollo, investigación, redacción) dura menos de 1 hora antes de que tu cuota de 5h se agote. Total semanal menor a 7 horas. Demasiado limitado para cualquier profesional.
- **$100 5x Max** — puedes trabajar unas 4 horas antes de alcanzar la ventana de 5h. 30-35 horas/semana en total. Aceptable para uso regular.
- **$200 20x Max** — para quienes trabajan 80-100+ horas/semana, frecuentemente con múltiples sesiones en paralelo.

### Por qué Claude prohibió el uso de suscripciones por terceros

Estos multiplicadores lo explican. A 10-20x del valor nominal, cada dólar de suscripción compra mucho más cómputo que los precios de API. Herramientas de terceros consumiendo cuotas de suscripción a tasas equivalentes de API hacían el modelo económico insostenible.

### La alternativa Codex

Aún no he medido completamente el valor en dólares de Codex, pero en el tier de $20, Codex Plus entrega aproximadamente **3x el uso real** de Claude Pro.

Por qué: las conversaciones de ChatGPT (incluso con el modelo o4 de pensamiento extendido) no cuentan contra tu cuota de Codex. Obtienes el producto de chat completo gratis además del uso de código. Entonces $20 Codex ≈ $60 Claude en uso real.

**Si no planeas comprar al menos el tier de Claude de $100, compra $20 Codex Plus.** Obtienes investigación profunda gratis, chat con pensamiento extendido gratis, y 3x más uso de código que Claude Pro.

</details>

### Escenario de referencia

Todos los importes en dólares que aparecen a continuación usan esta línea base (Sonnet 4.6):

| Parámetro | Valor |
|---|---|
| Duración de sesión | 25 turnos |
| Context inicial | 5,000 tokens |
| Crecimiento por turno | ~3,000 tokens |
| Tasa de cache hit | 90% |
| Coste de turno en mitad de sesión | $0.038 |
| Total de sesión eficiente | $0.96 |

Para Opus 4.6, multiplica todos los costes por 1.67x.

---

## Los 15 patrones de desperdicio

### Nivel 1 — Los 3 grandes (60-70% del desperdicio)

#### 1. Narración ociosa

**Qué es.** La IA dice "Claro, lo arreglo" o "Déjame leer el archivo primero" — y luego hace el trabajo real en el siguiente turno. El turno de narración no hizo nada: ninguna llamada a herramienta, nada de código, ninguna lectura de archivo.

**El desperdicio.** Cada turno de narración cuesta **$0.031** (relectura del context + ~500 tokens de texto de estado). La mayoría de las sesiones tienen 5 de estos: **$0.165/sesión desperdiciados** — el 17% de tu factura sin producir nada. Con 10 sesiones/día: **$1.65/día ($50/mes)** solo en narración.

**La corrección.** vibecheck añade: *"Ningún turno sin llamada a herramienta. Nada de narración. Piensa y actúa en el mismo turno."* Elimina la narración por completo. **Ahorra $0.15-0.18/sesión.**

#### 2. Podredumbre de context

**Qué es.** Las conversaciones largas se vuelven progresivamente más caras. El turno 50 relee los 49 anteriores. El coste total de la sesión crece cuadráticamente con la longitud.

**El desperdicio.** Una sesión de 40 turnos: **$1.89.** Dos sesiones de 20 turnos (mismo trabajo): **$1.22.** La diferencia — **$0.67** — no compra nada. A 100 turnos: una sesión cuesta **$5.62** frente a cuatro sesiones de 25 turnos a **$3.84.** Son **$1.78 desperdiciados** por no dividir la sesión.

**La corrección.** Enseña: *"Usa /clear o /compact entre tareas no relacionadas. Empieza conversaciones nuevas."* **Ahorra $0.30-0.70/sesión para usuarios con hábito de sesiones largas.**

#### 3. Depuración de ping-pong

**Qué es.** Arregla, rompe, reintenta, rompe de nuevo. Cada intento fallido añade salida de error al context (~4K tokens por ciclo), que se relee en cada turno futuro.

**El desperdicio.** Tres ciclos fallidos: 6 turnos extra ($0.252) + 12K tokens de errores muertos ($0.036 de impuesto por context). **Total: ~$0.29 por episodio.** Ocurre en ~1/3 de las sesiones. **Ponderado: ~$0.10/sesión.**

**La corrección.** Añade: *"Tras 2 intentos fallidos en el mismo archivo: para, relee el error completo, piensa, aplica una corrección concreta."* **Ahorra ~$0.20 por episodio.**

### Nivel 2 — Densidad de turnos (15-20% del desperdicio)

#### 4. Salida de herramientas verbosa

**Qué es.** El comando de compilación o test vuelca 500 líneas (~5K tokens) en la conversación. Esos tokens se releen en cada turno futuro.

**El desperdicio.** 5K tokens x 12 turnos restantes x $0.30/1M = **$0.018/instancia** de impuesto por context. Ocurre 2-3 veces/sesión. Sin caching: **$0.180/instancia** — 10x peor. **Total: $0.04-0.05/sesión.**

**La corrección.** Añade: *"Redirige la salida de compilación/test a /tmp/, usa flags --quiet, máximo tail -50."* **Ahorra $0.03-0.05/sesión.**

#### 5. Comandos no encadenados

**Qué es.** `npm install` en un turno, `npm run build` en el siguiente. Dos relecturas del context cuando `&&` los encadena en uno.

**El desperdicio.** Cada separación: **$0.023.** Las sesiones típicas tienen 3-4 separaciones. **Total: $0.07-0.09/sesión.**

**La corrección.** Añade: *"Encadena comandos con `&&` cuando sea seguro."* **Ahorra $0.06-0.08/sesión.**

#### 6. Vagabundeo por el código

**Qué es.** La IA abre archivo tras archivo — README, package.json, configs — antes de hacer ningún trabajo. Cinco o más lecturas consecutivas antes de la primera edición.

**El desperdicio.** Cinco lecturas innecesarias: $0.190 en turnos + $0.027 de impuesto por context = **$0.217/episodio.** Ocurre en ~25% de las sesiones. **Ponderado: ~$0.054/sesión.**

**La corrección.** Fomenta la búsqueda dirigida (grep/glob primero), agrupando múltiples lecturas por turno. **Ahorra ~$0.15 por episodio.**

#### 7. Ediciones no agrupadas

**Qué es.** Editar el archivo A, luego el B, luego el C — tres turnos cuando un turno con ediciones en paralelo sería suficiente.

**El desperdicio.** 2 turnos extra x $0.038 = **$0.076/instancia.** Ocurre en ~60% de las sesiones. **Ponderado: ~$0.046/sesión.**

**La corrección.** Añade: *"Agrupa llamadas a herramientas independientes (múltiples lecturas/ediciones por turno)."* **Ahorra ~$0.04/sesión.**

### Nivel 3 — La cola (5-10% del desperdicio)

#### 8. Relecturas de archivos

**Qué es.** El mismo archivo se lee dos veces en una sesión. El contenido ya está en el context tras la primera lectura.

**El desperdicio.** 1 turno desperdiciado + contenido duplicado = **$0.043/relectura.** 1-2 por sesión. **Ponderado: ~$0.039/sesión.**

**La corrección.** Añade: *"El contenido está en el context tras la primera lectura. Relee solo si el archivo ha cambiado."* **Ahorra ~$0.03/sesión.**

#### 9. Bucles de espera y sondeo

**Qué es.** `sleep 5 && check_status`, repetido 3-5 veces. Cada sondeo relee el context completo.

**El desperdicio.** 4 sondeos x $0.038 = **$0.152/episodio.** Ocurre en ~20% de las sesiones. **Ponderado: ~$0.030/sesión.**

**La corrección.** Añade: *"Usa flags --wait o run_in_background."* **Ahorra ~$0.12/episodio.**

#### 10. Reintentos fallidos

**Qué es.** Un comando falla, la IA ejecuta exactamente el mismo comando de nuevo. La salida de error ahora está en el context dos veces.

**El desperdicio.** **$0.042/reintento.** Ocurre en ~30% de las sesiones. **Ponderado: ~$0.013/sesión.**

**La corrección.** La misma regla que para el ping-pong: *"Para, relee el error, piensa, aplica una corrección concreta."*

#### 11. Búsquedas de esquema

**Qué es.** La IA consulta sus propias definiciones de herramientas — información que ya tiene. Añade más de 2K tokens al context.

**El desperdicio.** **$0.052/búsqueda.** Ocurre en ~40% de las sesiones. **Ponderado: ~$0.021/sesión.**

**La corrección.** "Ningún turno sin llamada a herramienta" desalienta los turnos de descubrimiento. **Ahorra ~$0.02/sesión.**

#### 12. Ceremonia de git

**Qué es.** `git add` → `git status` → `git commit` → `git push`, cuatro turnos. `git add -A && git commit -m "msg" && git push` es uno solo.

**El desperdicio.** 3 turnos extra + salida de git = **$0.098/instancia.** Ocurre en ~70% de las sesiones. **Ponderado: ~$0.069/sesión.**

**La corrección.** Añade: *"Encadena comandos de git con `&&`."* **Ahorra ~$0.06/sesión.**

### Nivel 4 — Agentes siempre activos (OpenClaw, etc.)

Modelo de coste diferente: coste por activación x activaciones por día.

#### 13. Latidos ociosos

**Qué es.** El agente se activa cada 5 minutos, relee el espacio de trabajo completo y no encuentra nada. 288 activaciones/día, ~97% en reposo.

**El desperdicio.** 280 activaciones ociosas/día x $0.04 = **$11.20/día ($336/mes)** sin hacer nada.

**La corrección.** *"Intervalo mínimo de 30 minutos. Omitir si no hay disparadores."* Reduce a ~48 activaciones/día. **Ahorra $8-10/día ($240-300/mes).**

#### 14. Inflación de archivos del espacio de trabajo

**Qué es.** 35K tokens de archivos de personalidad (SOUL.md, AGENTS.md) releídos en cada activación. La IA solo necesita las reglas de comportamiento — los tutoriales y el material de guía son para humanos.

**El desperdicio.** **$5.76/día ($173/mes)** solo leyendo archivos de configuración.

**La corrección.** Comprime los archivos del espacio de trabajo: de 35K a 12-15K tokens. **Ahorra $3-4/día ($90-120/mes).**

#### 15. Acumulación de memoria

**Qué es.** El historial de sesión crece sin podarse. Más de 100 entradas releídas en cada activación.

**El desperdicio.** **$3.17/día ($95/mes)** leyendo memoria obsoleta.

**La corrección.** *"Archivar tras 50 turnos, resumir, empezar de nuevo."* **Ahorra $2-3/día ($60-90/mes).**

---

## Además: Herramientas de optimización

### Compresión del archivo de instrucciones

Tu archivo de instrucciones se lee en cada turno — un impuesto fijo que pagas independientemente de la tarea. vibecheck incluye un compresor sin pérdidas de 4 pasadas (23 técnicas) que reduce el tamaño del archivo un 25-50%:

- **Pasada 1 (Mecánica):** Elimina markdown, convierte tablas, fusiona viñetas. ~10-15%.
- **Pasada 2 (Conservación de hechos):** Deduplica hechos, comprime ejemplos de código. ~15-25%.
- **Pasada 3 (Alta fidelidad):** Elimina tutoriales y texto de guía que los humanos necesitan pero la IA no. ~10-15%.
- **Pasada 4 (Telegrama):** Reescritura completa en taquigrafía para archivos solo de IA. ~15-25% (solo con permiso).

Un archivo de 10K tokens comprimido a 6K ahorra $0.057/sesión. Con 10 sesiones/día: **$0.57/día ($17/mes).**

### Supresión de salida

Los tokens de salida cuestan 5x los de entrada ($15 vs $3/MTok en Sonnet). Que la IA muestre bloques de código y diffs completos que no pediste desperdicia **~$0.047/sesión.** vibecheck añade: *"Sin código ni diffs a menos que se pidan."*

### Monitoreo de costes

`/vibecheck monitor` hace una instantánea de tu perfil de sesión y la compara con la línea base en ejecuciones posteriores. Detecta regresiones antes de que cuesten dinero.

---

## Resumen de ahorros

### Herramientas interactivas (Sonnet 4.6)

| # | Patrón | Desperdicio medio/sesión | Ahorro medio |
|---|---|---|---|
| 1 | Narración ociosa | $0.165 | $0.155 |
| 2 | Podredumbre de context | $0.150 | $0.120 |
| 3 | Depuración ping-pong | $0.097 | $0.067 |
| 4 | Salida verbosa | $0.045 | $0.035 |
| 5 | Comandos no encadenados | $0.080 | $0.065 |
| 6 | Vagabundeo por el código | $0.054 | $0.040 |
| 7 | Ediciones no agrupadas | $0.046 | $0.038 |
| 8 | Relecturas de archivos | $0.039 | $0.030 |
| 9 | Bucles de espera/sondeo | $0.030 | $0.025 |
| 10 | Reintentos fallidos | $0.013 | $0.010 |
| 11 | Búsquedas de esquema | $0.021 | $0.018 |
| 12 | Ceremonia de git | $0.069 | $0.058 |
| + | Compresión | $0.057 | $0.057 |
| + | Supresión de salida | $0.047 | $0.038 |
| | **Total** | **$0.913** | **$0.756** |

**Sesión típica con desperdicio: $1.87. Tras vibecheck: $1.11. Ahorro: 41%.**

- **Poco desperdicio** (sesiones cortas, pocos patrones): 25-35%
- **Desperdicio moderado** (usuario promedio): 40-50%
- **Mucho desperdicio** (sesiones largas, múltiples patrones): 50-65%

### Agentes siempre activos

| # | Patrón | Desperdicio diario | Ahorro diario |
|---|---|---|---|
| 13 | Latidos ociosos | $11.20 | $9.70 |
| 14 | Inflación del espacio de trabajo | $5.76 | $3.76 |
| 15 | Acumulación de memoria | $3.17 | $2.37 |
| | **Total** | **$20.13/día** | **$15.83/día** |

**Ahorro mensual para agentes siempre activos: ~$475.**

---

## Herramientas compatibles

Más de 24 herramientas.

- **Análisis completo de sesión:** Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- **Detección + optimización de instrucciones:** Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

Todos los LLMs: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, y más de 40 adicionales.

macOS, Windows, Linux, iPad vía SSH. Python 3.8+, sin dependencias.

<details>
<summary>Metodología</summary>

Todas las estimaciones de coste usan el escenario de referencia anterior. Supuestos clave:

- **90% de tasa de cache hit** — típico en sesiones de programación rápida. Las sesiones más lentas tendrán costes más altos.
- **25 turnos productivos/sesión** — las sesiones con desperdicio añaden 8-12 turnos extra por narración, reintentos y comandos no encadenados.
- **3,000 tokens/turno de crecimiento** — las sesiones verbosas pueden llegar a 4,000-5,000.
- **Tarifa efectiva de entrada: $0.57/1M** — combinación del 90% con cache ($0.30) + 10% sin cache ($3.00).
- **Tarifa de impuesto por context: $0.30/1M** — tarifa de entrada con cache para adiciones permanentes al context.

Las estimaciones son conservadoras. Los ahorros reales pueden superar las proyecciones para usuarios con sesiones largas, archivos de instrucciones grandes o depuración intensa.
</details>
