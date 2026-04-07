# Model Pricing Registry

This repo hardcodes the model pricing chart as of `2026-04-08`.

What is in scope:
- frontier coding and agent models we expect to see in Claude Code, Codex, Cursor, Copilot, Windsurf, OpenClaw, TRAE, Qoder, Buddy, and Antigravity logs
- token pricing
- cache read / cache write behavior where the provider publishes it
- provider tool-fee metadata when the provider documents direct web-search or execution charges
- service-tier and batch/priority notes where they materially change effective agent cost

What is intentionally normalized:
- all prices are stored in `USD per 1M tokens`
- `Qwen` source prices are published in `CNY`, then converted with `USD_CNY_RATE_2026_04_08 = 6.88258`
- `MiniMax` source prices are also normalized from `CNY`

Main source set used for the April 8, 2026 chart:
- OpenRouter programming rankings for current model selection
- OpenAI API pricing
- Anthropic pricing
- Google Gemini API pricing
- Alibaba Cloud / Qwen pricing docs
- MiniMax pricing docs
- Z.AI / BigModel pricing docs
- Moonshot / Kimi platform pricing
- DeepSeek API pricing

Important assumptions:
- `Gemini 3.0 Pro` is currently normalized to `gemini-3.1-pro-preview` in the matcher. That is a compatibility alias, not a claim that Google published separate standalone price tables for both names on April 8, 2026.
- `Gemini 3.0 Flash` and `Gemini 3.1 Flash` are normalized to `gemini-3-flash-preview` for the same reason.
- `gpt-5.1` is kept as a compatibility alias and currently priced like `gpt-5`.
- `o3-mini` is kept as a compatibility alias and currently priced like `o4-mini`.
- `deepseek-v3` is normalized to the current `deepseek-v3.2` rate card unless a log explicitly identifies another rate table.
- Tool-fee metadata is stored for education/reporting now; not every provider surcharge is necessarily added into per-session totals yet because many logs do not expose the billable tool-call counts directly.
- Anthropic cache writes default to the `5 minute` write price in totals because logs usually do not reveal the chosen cache TTL. The `1 hour` write price is stored as metadata too.
- Qwen totals currently default to the `implicit cache hit` rate when logs only show cached tokens. The lower `explicit cache` hit rate is stored separately because most current logs do not expose that distinction.
- Gemini totals use the standard explicit-cache price when logs expose cached-token counts, but the registry also stores notes that Google implicit caching is opportunistic and not guaranteed.

Model families currently built into the registry:
- Anthropic: `claude-opus-4.6`, `claude-sonnet-4.6`, `claude-haiku-3.5`
- OpenAI: `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-5.2`, `gpt-5.1`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-pro`, `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `o1`, `o3`, `o3-mini`, `o4-mini`
- Google: `gemini-3.1-pro-preview`, `gemini-3.1-flash-lite-preview`, `gemini-3-flash-preview`, `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`
- Qwen: `qwen3.6-plus`, `qwen3-coder-plus`, `qwen3-coder-flash`
- MiniMax: `minimax-m2.7`, `minimax-m2.7-highspeed`, `minimax-m2.5`, `minimax-m2.5-highspeed`
- Z.AI: `glm-5`, `glm-5-turbo`, `glm-5v-turbo`, `glm-4.7`, `glm-4.6`, `glm-4.5-air`
- Moonshot: `kimi-k2.5`, `kimi-k2`, `kimi-k2-thinking`
- DeepSeek: `deepseek-v3.2`, `deepseek-v3`, `deepseek-r1`

Tiered pricing currently modeled:
- Claude Sonnet 4.6
- Claude Opus 4.6
- Gemini 3.1 Pro Preview
- Gemini 2.5 Pro
- Qwen 3.6 Plus
- Qwen 3 Coder Plus
- Qwen 3 Coder Flash

Provider-specific mechanics currently encoded:
- Anthropic: `cache_write_price_5m`, `cache_write_price_1h`, batch pricing, US-hosted price multipliers where documented
- OpenAI: cached-prefix pricing, batch pricing, and the special case that `gpt-5-pro` currently has no listed cached-input discount
- Google: service-tier metadata for standard/batch/flex/priority, explicit cache storage rent, and notes about opportunistic implicit caching
- Qwen: separate implicit vs explicit cache-hit prices
- MiniMax: normalized CNY source pricing plus explicit cache read/write prices

Implementation files:
- pricing registry: `/Users/wallny/Developer/vibecheck/scripts/model_pricing.py`
- shared Claude analyzer: `/Users/wallny/Developer/vibecheck/scripts/analyze_claude_sessions.py`
- lesson/report builder: `/Users/wallny/Developer/vibecheck/scripts/explain.py`
