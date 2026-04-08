#!/usr/bin/env python3
"""Shared model pricing registry for April 8, 2026.

All prices are normalized to USD per 1M tokens unless noted.
"""

PRICING_REGISTRY_VERSION = "2026-04-08"
PRICING_REGISTRY_LABEL = "April 8, 2026 frontier pricing"
USD_CNY_RATE_2026_04_08 = 6.88258

FULL_BILLING_MODELS = {
    'claude-opus-4.6',
    'claude-sonnet-4.6',
    'gpt-5.4',
    'gemini-3.1-pro-preview',
    'gemini-3-flash-preview',
    'glm-5',
    'minimax-m2.7',
    'kimi-k2.5',
    'deepseek-v3.2',
    'qwen3.6-plus',
}


def cny_to_usd(amount_cny):
    return round(amount_cny / USD_CNY_RATE_2026_04_08, 6)


def pricing(input_price, output_price, cache_read_price=None, cache_write_price=None, **extra):
    cache_read_price = input_price if cache_read_price is None else cache_read_price
    cache_write_price = input_price if cache_write_price is None else cache_write_price
    return {
        'input': input_price,
        'output': output_price,
        'cache_read_mult': round(cache_read_price / input_price, 6) if input_price else 0,
        'cache_create_mult': round(cache_write_price / input_price, 6) if input_price else 0,
        'cache_read_price': cache_read_price,
        'cache_write_price': cache_write_price,
        **extra,
    }


PROVIDER_TOOL_PRICING = {
    'anthropic': {
        'web_search_per_1k': 10.0,
        'code_execution_per_hour': 0.05,
        'batch_discount_pct': 50,
        'notes': 'Prompt caching has distinct 5m and 1h write prices. Web search is billed per search plus normal tokens. Code execution is billed per session-hour. Tool definitions also add input tokens.',
    },
    'openai': {
        'web_search_per_1k': 10.0,
        'web_search_preview_reasoning_per_1k': 10.0,
        'web_search_preview_non_reasoning_per_1k': 25.0,
        'file_search_storage_per_gb_day': 0.10,
        'file_search_tool_call_per_1k': 2.50,
        'containers_1gb_per_20m': 0.03,
        'containers_4gb_per_20m': 0.12,
        'containers_16gb_per_20m': 0.48,
        'containers_64gb_per_20m': 1.92,
        'batch_discount_pct': 50,
        'notes': 'Cached input is provider-managed repeated-prefix pricing, not an explicit cache-create bill. Search content tokens are free on the current pricing page for built-in web search.',
    },
    'google': {
        'google_search_per_1k': 35.0,
        'gemini_3_search_per_1k': 14.0,
        'google_maps_per_1k': 14.0,
        'code_execution': 0.0,
        'file_search_embeddings_per_1m': 0.15,
        'batch_discount_pct': 50,
        'notes': 'Gemini has implicit caching with no guaranteed savings and explicit caching with guaranteed pricing plus storage rent. Search/query grounding is billed per search query.',
    },
    'moonshot': {
        'web_search_per_call': 0.005,
        'notes': 'When $web_search fires, Moonshot also bills the search-result tokens that are fed back into the next completion.',
    },
    'z_ai': {
        'web_search_per_call': 0.01,
        'notes': 'Z.AI publishes a direct per-use charge for Web Search in addition to token costs.',
    },
    'qwen': {
        'notes': 'Function/tool descriptions count toward input tokens. Implicit context-cache hits are billed at 20% of input price; explicit cache can be as low as 10%, but that distinction is not inferable from current logs.',
    },
    'minimax': {
        'notes': 'Prompt caching has explicit read/write prices on PAYG plans. No separate public tool-call surcharge was found in current text-model pricing docs.',
    },
    'deepseek': {
        'notes': 'Official pricing currently exposes cache-hit vs cache-miss token rates for DeepSeek-V3.2.',
    },
}


TIERED_PRICING = {
    'claude-sonnet-4.6': [
        {'max_input_tokens': 200_000, **pricing(3.0, 15.0, 0.30, 3.75), 'cache_write_price_5m': 3.75, 'cache_write_price_1h': 6.0},
        {'max_input_tokens': None, **pricing(6.0, 22.5, 0.60, 7.50), 'cache_write_price_5m': 7.50, 'cache_write_price_1h': 12.0, 'long_context': True},
    ],
    'claude-opus-4.6': [
        {'max_input_tokens': 200_000, **pricing(5.0, 25.0, 0.50, 6.25), 'cache_write_price_5m': 6.25, 'cache_write_price_1h': 10.0},
        {'max_input_tokens': None, **pricing(10.0, 37.5, 1.00, 12.50), 'cache_write_price_5m': 12.50, 'cache_write_price_1h': 20.0, 'long_context': True},
    ],
    'gemini-3.1-pro-preview': [
        {'max_input_tokens': 200_000, **pricing(2.0, 12.0, 0.20, 2.0), 'cache_storage_per_mtok_hour': 4.50},
        {'max_input_tokens': None, **pricing(4.0, 18.0, 0.40, 4.0), 'cache_storage_per_mtok_hour': 4.50, 'long_context': True},
    ],
    'gemini-2.5-pro': [
        {'max_input_tokens': 200_000, **pricing(1.25, 10.0, 0.125, 1.25), 'cache_storage_per_mtok_hour': 4.50},
        {'max_input_tokens': None, **pricing(2.50, 15.0, 0.25, 2.50), 'cache_storage_per_mtok_hour': 4.50, 'long_context': True},
    ],
    'qwen3.6-plus': [
        {'max_input_tokens': 256_000, **pricing(cny_to_usd(2.0), cny_to_usd(12.0), cny_to_usd(0.4), cny_to_usd(2.0)), 'cache_read_price_implicit': cny_to_usd(0.4), 'cache_read_price_explicit': cny_to_usd(0.2), 'source_currency': 'CNY'},
        {'max_input_tokens': None, **pricing(cny_to_usd(8.0), cny_to_usd(48.0), cny_to_usd(1.6), cny_to_usd(8.0)), 'cache_read_price_implicit': cny_to_usd(1.6), 'cache_read_price_explicit': cny_to_usd(0.8), 'source_currency': 'CNY', 'long_context': True},
    ],
    'qwen3-coder-plus': [
        {'max_input_tokens': 32_000, **pricing(cny_to_usd(7.339), cny_to_usd(36.696), cny_to_usd(1.4678), cny_to_usd(7.339)), 'cache_read_price_implicit': cny_to_usd(1.4678), 'cache_read_price_explicit': cny_to_usd(0.7339), 'source_currency': 'CNY'},
        {'max_input_tokens': 128_000, **pricing(cny_to_usd(13.211), cny_to_usd(66.053), cny_to_usd(2.6422), cny_to_usd(13.211)), 'cache_read_price_implicit': cny_to_usd(2.6422), 'cache_read_price_explicit': cny_to_usd(1.3211), 'source_currency': 'CNY'},
        {'max_input_tokens': 256_000, **pricing(cny_to_usd(22.018), cny_to_usd(110.089), cny_to_usd(4.4036), cny_to_usd(22.018)), 'cache_read_price_implicit': cny_to_usd(4.4036), 'cache_read_price_explicit': cny_to_usd(2.2018), 'source_currency': 'CNY'},
        {'max_input_tokens': None, **pricing(cny_to_usd(44.035), cny_to_usd(440.354), cny_to_usd(8.807), cny_to_usd(44.035)), 'cache_read_price_implicit': cny_to_usd(8.807), 'cache_read_price_explicit': cny_to_usd(4.4035), 'source_currency': 'CNY', 'long_context': True},
    ],
    'qwen3-coder-flash': [
        {'max_input_tokens': 32_000, **pricing(cny_to_usd(2.752), cny_to_usd(11.009), cny_to_usd(0.5504), cny_to_usd(2.752)), 'cache_read_price_implicit': cny_to_usd(0.5504), 'cache_read_price_explicit': cny_to_usd(0.2752), 'source_currency': 'CNY'},
        {'max_input_tokens': 128_000, **pricing(cny_to_usd(4.954), cny_to_usd(19.816), cny_to_usd(0.9908), cny_to_usd(4.954)), 'cache_read_price_implicit': cny_to_usd(0.9908), 'cache_read_price_explicit': cny_to_usd(0.4954), 'source_currency': 'CNY'},
        {'max_input_tokens': 256_000, **pricing(cny_to_usd(8.257), cny_to_usd(33.027), cny_to_usd(1.6514), cny_to_usd(8.257)), 'cache_read_price_implicit': cny_to_usd(1.6514), 'cache_read_price_explicit': cny_to_usd(0.8257), 'source_currency': 'CNY'},
        {'max_input_tokens': None, **pricing(cny_to_usd(16.514), cny_to_usd(82.568), cny_to_usd(3.3028), cny_to_usd(16.514)), 'cache_read_price_implicit': cny_to_usd(3.3028), 'cache_read_price_explicit': cny_to_usd(1.6514), 'source_currency': 'CNY', 'long_context': True},
    ],
}


PRICING = {
    'claude-opus-4.6': pricing(5.0, 25.0, 0.50, 6.25, provider='anthropic', cache_write_price_5m=6.25, cache_write_price_1h=10.0, batch_input=2.5, batch_output=12.5, us_only_input_multiplier=1.1, us_only_output_multiplier=1.1),
    'claude-sonnet-4.6': pricing(3.0, 15.0, 0.30, 3.75, provider='anthropic', cache_write_price_5m=3.75, cache_write_price_1h=6.0, batch_input=1.5, batch_output=7.5, us_only_input_multiplier=1.1, us_only_output_multiplier=1.1),
    'claude-haiku-3.5': pricing(0.80, 4.0, 0.08, 1.0, provider='anthropic', cache_write_price_5m=1.0, cache_write_price_1h=1.6, batch_input=0.4, batch_output=2.0),
    'opus': pricing(5.0, 25.0, 0.50, 6.25, provider='anthropic', alias_of='claude-opus-4.6', cache_write_price_5m=6.25, cache_write_price_1h=10.0),
    'sonnet': pricing(3.0, 15.0, 0.30, 3.75, provider='anthropic', alias_of='claude-sonnet-4.6', cache_write_price_5m=3.75, cache_write_price_1h=6.0),
    'haiku': pricing(0.80, 4.0, 0.08, 1.0, provider='anthropic', alias_of='claude-haiku-3.5', cache_write_price_5m=1.0, cache_write_price_1h=1.6),

    'gpt-5.4': pricing(2.50, 15.0, 0.25, 2.50, provider='openai', cache_behavior='cached_prefix', batch_input=1.25, batch_output=7.5, context_length_note='Pricing above reflects standard processing rates for context lengths under 270K.'),
    'gpt-5.4-mini': pricing(0.75, 4.50, 0.075, 0.75, provider='openai', cache_behavior='cached_prefix', batch_input=0.375, batch_output=2.25, context_length_note='Pricing above reflects standard processing rates for context lengths under 270K.'),
    'gpt-5.4-nano': pricing(0.20, 1.25, 0.02, 0.20, provider='openai', cache_behavior='cached_prefix', batch_input=0.10, batch_output=0.625, context_length_note='Pricing above reflects standard processing rates for context lengths under 270K.'),
    'gpt-5.2': pricing(1.75, 14.0, 0.175, 1.75, provider='openai', cache_behavior='cached_prefix', batch_input=0.875, batch_output=7.0),
    'gpt-5.1': pricing(1.25, 10.0, 0.125, 1.25, provider='openai', alias_of='gpt-5', cache_behavior='cached_prefix', batch_input=0.625, batch_output=5.0),
    'gpt-5': pricing(1.25, 10.0, 0.125, 1.25, provider='openai', cache_behavior='cached_prefix', batch_input=0.625, batch_output=5.0),
    'gpt-5-mini': pricing(0.25, 2.0, 0.025, 0.25, provider='openai', cache_behavior='cached_prefix', batch_input=0.125, batch_output=1.0),
    'gpt-5-nano': pricing(0.05, 0.40, 0.005, 0.05, provider='openai', cache_behavior='cached_prefix', batch_input=0.025, batch_output=0.20),
    'gpt-5-pro': pricing(15.0, 120.0, 15.0, 15.0, provider='openai', cache_behavior='no_cached_input_discount', notes='No cached-input discount is listed on the current OpenAI pricing page.', batch_input=7.5, batch_output=60.0),
    'gpt-4o': pricing(2.50, 10.0, 1.25, 2.50, provider='openai'),
    'gpt-4o-mini': pricing(0.15, 0.60, 0.075, 0.15, provider='openai'),
    'gpt-4.1': pricing(2.0, 8.0, 0.50, 2.0, provider='openai'),
    'gpt-4.1-mini': pricing(0.40, 1.60, 0.10, 0.40, provider='openai'),
    'gpt-4.1-nano': pricing(0.10, 0.40, 0.025, 0.10, provider='openai'),
    'o1': pricing(15.0, 60.0, 7.50, 15.0, provider='openai'),
    'o3': pricing(1.0, 4.0, 0.25, 1.0, provider='openai'),
    'o3-mini': pricing(1.10, 4.40, 0.275, 1.10, provider='openai', alias_of='o4-mini'),
    'o4-mini': pricing(1.10, 4.40, 0.275, 1.10, provider='openai'),

    'gemini-3.1-pro-preview': pricing(2.0, 12.0, 0.20, 2.0, provider='google', cache_storage_per_mtok_hour=4.50, default_service_tier='standard', implicit_cache_discount_not_guaranteed=True, service_tiers={'standard': {'input': 2.0, 'output': 12.0, 'cache_read_price': 0.20, 'cache_storage_per_mtok_hour': 4.50}, 'batch': {'input': 1.0, 'output': 6.0, 'cache_read_price': 0.20, 'cache_storage_per_mtok_hour': 4.50}, 'flex': {'input': 1.0, 'output': 6.0, 'cache_read_price': 0.20, 'cache_storage_per_mtok_hour': 4.50}, 'priority': {'input': 3.6, 'output': 21.6, 'cache_read_price': 0.36, 'cache_storage_per_mtok_hour': 8.10}}),
    'gemini-3-pro-preview': pricing(2.0, 12.0, 0.20, 2.0, provider='google', alias_of='gemini-3.1-pro-preview', cache_storage_per_mtok_hour=4.50, default_service_tier='standard', implicit_cache_discount_not_guaranteed=True),
    'gemini-3.1-flash-lite-preview': pricing(0.25, 1.50, 0.025, 0.25, provider='google', cache_storage_per_mtok_hour=1.00, default_service_tier='standard', implicit_cache_discount_not_guaranteed=True, service_tiers={'standard': {'input': 0.25, 'output': 1.50, 'cache_read_price': 0.025, 'cache_storage_per_mtok_hour': 1.00}, 'batch': {'input': 0.125, 'output': 0.75, 'cache_read_price': 0.0125, 'cache_storage_per_mtok_hour': 0.50}, 'flex': {'input': 0.125, 'output': 0.75, 'cache_read_price': 0.0125, 'cache_storage_per_mtok_hour': 0.50}, 'priority': {'input': 0.45, 'output': 2.70, 'cache_read_price': 0.045, 'cache_storage_per_mtok_hour': 1.80}}),
    'gemini-3-flash-preview': pricing(0.50, 3.0, 0.05, 0.50, provider='google', cache_storage_per_mtok_hour=1.00, default_service_tier='standard', implicit_cache_discount_not_guaranteed=True, service_tiers={'standard': {'input': 0.50, 'output': 3.0, 'cache_read_price': 0.05, 'cache_storage_per_mtok_hour': 1.00}, 'batch': {'input': 0.25, 'output': 1.50, 'cache_read_price': 0.05, 'cache_storage_per_mtok_hour': 1.00}, 'flex': {'input': 0.25, 'output': 1.50, 'cache_read_price': 0.05, 'cache_storage_per_mtok_hour': 1.00}, 'priority': {'input': 0.90, 'output': 5.40, 'cache_read_price': 0.09, 'cache_storage_per_mtok_hour': 1.80}}),
    'gemini-2.5-pro': pricing(1.25, 10.0, 0.125, 1.25, provider='google', cache_storage_per_mtok_hour=4.50, implicit_cache_discount_not_guaranteed=True),
    'gemini-2.5-flash': pricing(0.30, 2.50, 0.03, 0.30, provider='google', cache_storage_per_mtok_hour=1.00, implicit_cache_discount_not_guaranteed=True),
    'gemini-2.0-flash': pricing(0.10, 0.40, 0.025, 0.10, provider='google', cache_storage_per_mtok_hour=1.00),

    'qwen3.6-plus': pricing(cny_to_usd(2.0), cny_to_usd(12.0), cny_to_usd(0.4), cny_to_usd(2.0), provider='qwen', source_currency='CNY', source_exchange_rate='USD_CNY_RATE_2026_04_08', cache_read_price_implicit=cny_to_usd(0.4), cache_read_price_explicit=cny_to_usd(0.2)),
    'qwen3-coder-plus': pricing(cny_to_usd(7.339), cny_to_usd(36.696), cny_to_usd(1.4678), cny_to_usd(7.339), provider='qwen', source_currency='CNY', source_exchange_rate='USD_CNY_RATE_2026_04_08', cache_read_price_implicit=cny_to_usd(1.4678), cache_read_price_explicit=cny_to_usd(0.7339)),
    'qwen3-coder-flash': pricing(cny_to_usd(2.752), cny_to_usd(11.009), cny_to_usd(0.5504), cny_to_usd(2.752), provider='qwen', source_currency='CNY', source_exchange_rate='USD_CNY_RATE_2026_04_08', cache_read_price_implicit=cny_to_usd(0.5504), cache_read_price_explicit=cny_to_usd(0.2752)),

    'minimax-m2.7': pricing(cny_to_usd(2.1), cny_to_usd(8.4), cny_to_usd(0.42), cny_to_usd(2.625), provider='minimax', source_currency='CNY', source_exchange_rate='USD_CNY_RATE_2026_04_08'),
    'minimax-m2.7-highspeed': pricing(cny_to_usd(4.2), cny_to_usd(16.8), cny_to_usd(0.42), cny_to_usd(2.625), provider='minimax', source_currency='CNY', source_exchange_rate='USD_CNY_RATE_2026_04_08'),
    'minimax-m2.5': pricing(cny_to_usd(2.1), cny_to_usd(8.4), cny_to_usd(0.21), cny_to_usd(2.625), provider='minimax', source_currency='CNY', source_exchange_rate='USD_CNY_RATE_2026_04_08'),
    'minimax-m2.5-highspeed': pricing(cny_to_usd(4.2), cny_to_usd(16.8), cny_to_usd(0.21), cny_to_usd(2.625), provider='minimax', source_currency='CNY', source_exchange_rate='USD_CNY_RATE_2026_04_08'),

    'glm-5': pricing(1.0, 3.2, 0.20, 1.0, provider='z_ai'),
    'glm-5-turbo': pricing(1.2, 4.0, 0.24, 1.2, provider='z_ai'),
    'glm-5v-turbo': pricing(1.2, 4.0, 0.24, 1.2, provider='z_ai'),
    'glm-4.7': pricing(0.60, 2.20, 0.11, 0.60, provider='z_ai'),
    'glm-4.6': pricing(0.60, 2.20, 0.11, 0.60, provider='z_ai'),
    'glm-4.5-air': pricing(0.20, 1.10, 0.03, 0.20, provider='z_ai'),

    'kimi-k2.5': pricing(0.60, 3.0, 0.10, 0.60, provider='moonshot'),
    'kimi-k2': pricing(0.60, 2.50, 0.15, 0.60, provider='moonshot'),
    'kimi-k2-thinking': pricing(0.60, 2.50, 0.15, 0.60, provider='moonshot'),

    'deepseek-v3': pricing(0.28, 0.42, 0.028, 0.28, provider='deepseek', alias_of='deepseek-v3.2'),
    'deepseek-v3.2': pricing(0.28, 0.42, 0.028, 0.28, provider='deepseek'),
    'deepseek-r1': pricing(0.55, 2.19, 0.077, 0.55, provider='deepseek'),
}


MODEL_PATTERNS = [
    ('claude-opus-4.6', 'claude-opus-4.6'),
    ('opus 4.6', 'claude-opus-4.6'),
    ('claude opus 4.6', 'claude-opus-4.6'),
    ('claude-sonnet-4.6', 'claude-sonnet-4.6'),
    ('sonnet 4.6', 'claude-sonnet-4.6'),
    ('claude sonnet 4.6', 'claude-sonnet-4.6'),
    ('claude-haiku-3.5', 'claude-haiku-3.5'),
    ('haiku 3.5', 'claude-haiku-3.5'),
    ('gpt-5.4-mini', 'gpt-5.4-mini'),
    ('gpt-5.4-nano', 'gpt-5.4-nano'),
    ('gpt-5.4', 'gpt-5.4'),
    ('gpt-5-pro', 'gpt-5-pro'),
    ('gpt-5 mini', 'gpt-5-mini'),
    ('gpt-5-mini', 'gpt-5-mini'),
    ('gpt-5 nano', 'gpt-5-nano'),
    ('gpt-5-nano', 'gpt-5-nano'),
    ('gpt-5.2', 'gpt-5.2'),
    ('gpt-5', 'gpt-5'),
    ('gpt-4.1-mini', 'gpt-4.1-mini'),
    ('gpt-4.1-nano', 'gpt-4.1-nano'),
    ('gpt-4.1', 'gpt-4.1'),
    ('o4-mini', 'o4-mini'),
    ('o3', 'o3'),
    ('gemini-3.1-pro-preview-customtools', 'gemini-3.1-pro-preview'),
    ('gemini-3.1-pro-preview', 'gemini-3.1-pro-preview'),
    ('gemini-3-pro-preview', 'gemini-3.1-pro-preview'),
    ('gemini-3.1-pro', 'gemini-3.1-pro-preview'),
    ('gemini 3.1 pro', 'gemini-3.1-pro-preview'),
    ('gemini-3.0-pro', 'gemini-3.1-pro-preview'),
    ('gemini 3.0 pro', 'gemini-3.1-pro-preview'),
    ('gemini 3 pro', 'gemini-3.1-pro-preview'),
    ('gemini-3.1-flash-lite-preview', 'gemini-3.1-flash-lite-preview'),
    ('gemini 3.1 flash lite', 'gemini-3.1-flash-lite-preview'),
    ('gemini-3-flash-preview', 'gemini-3-flash-preview'),
    ('gemini-3.0-flash', 'gemini-3-flash-preview'),
    ('gemini 3.0 flash', 'gemini-3-flash-preview'),
    ('gemini-3.1-flash', 'gemini-3-flash-preview'),
    ('gemini 3.1 flash', 'gemini-3-flash-preview'),
    ('gemini 3 flash', 'gemini-3-flash-preview'),
    ('gemini-2.5-pro', 'gemini-2.5-pro'),
    ('gemini-2.5-flash', 'gemini-2.5-flash'),
    ('gemini-2.0-flash', 'gemini-2.0-flash'),
    ('qwen3.6 plus', 'qwen3.6-plus'),
    ('qwen3.6-plus', 'qwen3.6-plus'),
    ('qwen3-coder-plus', 'qwen3-coder-plus'),
    ('qwen3 coder plus', 'qwen3-coder-plus'),
    ('qwen3-coder-flash', 'qwen3-coder-flash'),
    ('qwen3 coder flash', 'qwen3-coder-flash'),
    ('minimax-m2.7-highspeed', 'minimax-m2.7-highspeed'),
    ('minimax m2.7 highspeed', 'minimax-m2.7-highspeed'),
    ('minimax-m2.7', 'minimax-m2.7'),
    ('minimax m2.7', 'minimax-m2.7'),
    ('minimax-m2.5-highspeed', 'minimax-m2.5-highspeed'),
    ('minimax-m2.5', 'minimax-m2.5'),
    ('glm-5v-turbo', 'glm-5v-turbo'),
    ('glm-5-turbo', 'glm-5-turbo'),
    ('glm 5 turbo', 'glm-5-turbo'),
    ('glm-5.1', 'glm-5'),
    ('glm-5', 'glm-5'),
    ('glm 5', 'glm-5'),
    ('glm-4.7', 'glm-4.7'),
    ('glm-4.6', 'glm-4.6'),
    ('glm-4.5-air', 'glm-4.5-air'),
    ('kimi-k2.5', 'kimi-k2.5'),
    ('kimi k2.5', 'kimi-k2.5'),
    ('kimi-k2-thinking', 'kimi-k2-thinking'),
    ('kimi-k2', 'kimi-k2'),
    ('moonshot-v1', 'kimi-k2'),
    ('deepseek-v3.2', 'deepseek-v3.2'),
    ('deepseek-v3', 'deepseek-v3'),
    ('deepseek-chat', 'deepseek-v3.2'),
    ('deepseek-r1', 'deepseek-r1'),
    ('deepseek v3.2', 'deepseek-v3.2'),
    ('claude-opus', 'opus'),
    ('claude-sonnet', 'sonnet'),
    ('opus', 'opus'),
    ('sonnet', 'sonnet'),
    ('haiku', 'haiku'),
]


MODEL_ALIASES = {alias.strip().lower(): canonical for alias, canonical in MODEL_PATTERNS}


def resolve_model_name(model):
    if not isinstance(model, str) or not model.strip():
        return 'sonnet'

    current = MODEL_ALIASES.get(model.strip().lower(), model.strip())
    seen = set()
    while current not in seen:
        seen.add(current)
        alias_of = PRICING.get(current, {}).get('alias_of')
        if not alias_of:
            break
        current = alias_of
    return current


def get_pricing(model, total_input_tokens=0):
    resolved = resolve_model_name(model)
    if resolved in TIERED_PRICING:
        base = PRICING.get(resolved, {})
        for tier in TIERED_PRICING[resolved]:
            if tier['max_input_tokens'] is None or total_input_tokens <= tier['max_input_tokens']:
                return {**base, **tier}
    return PRICING.get(resolved, PRICING['sonnet'])


def canonical_model(model):
    return resolve_model_name(model)


def get_billing_mode(model):
    canonical = canonical_model(model)
    if canonical in FULL_BILLING_MODELS:
        return 'full_billing'
    return 'token_only_estimate'


def get_pricing_metadata(model):
    pricing_info = get_pricing(model)
    canonical = canonical_model(model)
    return {
        'registry_version': PRICING_REGISTRY_VERSION,
        'registry_label': PRICING_REGISTRY_LABEL,
        'billing_mode': get_billing_mode(model),
        'canonical_model': canonical,
        'provider': pricing_info.get('provider', 'unknown'),
    }
