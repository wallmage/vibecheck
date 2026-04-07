#!/usr/bin/env python3
"""Generate interactive cost education data from real session analysis.
Output: JSON lesson plan with real numbers from user's sessions."""
import json, sys, os, locale, subprocess
from collections import defaultdict
from model_pricing import PROVIDER_TOOL_PRICING, get_pricing, get_pricing_metadata

# Subscription tiers and their actual API spending power
SUBSCRIPTION_TIERS = {
    'claude': {
        'free':  {'monthly': 0,   'api_equiv': 5,    'note': 'Very limited, ~$5 API value'},
        'pro':   {'monthly': 20,  'api_equiv': 200,  'note': '~10x value, heavy users hit limits'},
        '5x':    {'monthly': 100, 'api_equiv': 1000, 'note': '~10x value'},
        '20x':   {'monthly': 200, 'api_equiv': 4000, 'note': '~20x value, power users'},
    },
    'openai': {
        'free':  {'monthly': 0,   'api_equiv': 3,    'note': 'Very limited'},
        'plus':  {'monthly': 20,  'api_equiv': 100,  'note': '~5x value'},
        'pro':   {'monthly': 200, 'api_equiv': 3000, 'note': '~15x value'},
    },
}

def detect_system_language():
    """Detect system language for default output."""
    # Try locale
    try:
        loc = locale.getlocale()[0]
        lang = loc or ''
    except Exception:
        lang = ''

    # Try macOS defaults
    if not lang or lang.startswith('en'):
        try:
            result = subprocess.run(['defaults', 'read', '-g', 'AppleLanguages'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                out = result.stdout.lower()
                for code, name in [('zh', 'chinese'), ('ja', 'japanese'), ('ko', 'korean'),
                                   ('es', 'spanish'), ('fr', 'french'), ('de', 'german'),
                                   ('pt', 'portuguese'), ('ru', 'russian'), ('ar', 'arabic'),
                                   ('hi', 'hindi'), ('it', 'italian')]:
                    if code in out or name in out:
                        return code
        except Exception:
            pass

    # Try Windows
    if not lang:
        try:
            result = subprocess.run(['powershell', '-c', '(Get-Culture).Name'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lang = result.stdout.strip()
        except Exception:
            pass

    if lang:
        code = lang[:2].lower()
        return 'en' if code == 'c' else code
    return 'en'

def find_most_expensive_day(sessions):
    """Find the single most expensive day with breakdown."""
    by_date = defaultdict(list)
    for s in sessions:
        by_date[s.get('date', 'unknown')].append(s)

    if not by_date:
        return None

    worst_date = max(by_date, key=lambda d: sum(s['total_cost'] for s in by_date[d]))
    day_sessions = by_date[worst_date]
    total = sum(s['total_cost'] for s in day_sessions)
    turns = sum(s['total_turns'] for s in day_sessions)
    cache_read = sum(s.get('total_cache_read', 0) for s in day_sessions)
    cache_create = sum(s.get('total_cache_create', 0) for s in day_sessions)
    output_tokens = sum(s.get('total_output_tokens', 0) for s in day_sessions)
    waste = sum(sum(w['cost'] for w in s['waste'].values()) for s in day_sessions)

    # Estimate cost breakdown by token type
    model = day_sessions[0].get('model', 'sonnet')
    p = get_pricing(model, total_input_tokens=cache_read + cache_create)

    cr_cost = cache_read * p.get('cache_read_price', p['input'] * p['cache_read_mult']) / 1_000_000
    cc_cost = cache_create * p.get('cache_write_price', p['input'] * p['cache_create_mult']) / 1_000_000
    out_cost = output_tokens * p['output'] / 1_000_000
    inp_cost = total - cr_cost - cc_cost - out_cost  # remainder = fresh input

    return {
        'date': worst_date,
        'sessions': len(day_sessions),
        'total_cost': round(total, 2),
        'total_turns': turns,
        'model': model,
        'cost_breakdown': {
            'cache_read': {'tokens': cache_read, 'cost': round(cr_cost, 2), 'pct': round(cr_cost/total*100, 1) if total > 0 else 0},
            'cache_create': {'tokens': cache_create, 'cost': round(cc_cost, 2), 'pct': round(cc_cost/total*100, 1) if total > 0 else 0},
            'output': {'tokens': output_tokens, 'cost': round(out_cost, 2), 'pct': round(out_cost/total*100, 1) if total > 0 else 0},
            'fresh_input': {'cost': round(max(0, inp_cost), 2), 'pct': round(max(0, inp_cost)/total*100, 1) if total > 0 else 0},
        },
        'waste_cost': round(waste, 2),
        'waste_pct': round(waste / total * 100, 1) if total > 0 else 0,
    }

def top_waste_items(sessions):
    """Get top 3 waste categories by cost."""
    waste_totals = defaultdict(float)
    for s in sessions:
        for key, w in s['waste'].items():
            waste_totals[key] += w['cost']
    sorted_waste = sorted(waste_totals.items(), key=lambda x: -x[1])
    return sorted_waste[:3]

def build_lesson_plan(data):
    """Build structured lesson data from analysis."""
    sessions = data.get('sessions', [])
    summary = data.get('summary', {})

    if not sessions:
        return {'error': 'No sessions to analyze'}

    language = detect_system_language()
    worst_day = find_most_expensive_day(sessions)
    top3_waste = top_waste_items(sessions)
    analysis_confidence = data.get('analysis_confidence', {
        'label': 'estimated',
        'score': 0.5,
        'reason': 'This analyzer did not report a confidence level, so treat totals as estimate-weighted.',
    })

    # Detect primary model family
    model_mix = data.get('model_mix', {})
    primary_model = list(model_mix.keys())[0] if model_mix else 'sonnet'

    # Determine provider
    pricing = get_pricing(primary_model)
    provider = pricing.get('provider', 'unknown')
    pricing_metadata = data.get('pricing_metadata', get_pricing_metadata(primary_model))

    # Calculate daily/monthly rates
    n_days = 14
    daily_cost = summary['total_cost'] / n_days
    monthly_cost = daily_cost * 30
    daily_sessions = summary['sessions'] / n_days

    # Provider-specific cache explanation
    cache_explanations = {
        'anthropic': {
            'mechanism': 'Prompt Caching with cache_read (0.1x input) and cache_create (1.25x input)',
            'key_insight': 'Cache reads are cheap (10% of input price) but happen EVERY turn. Cache creates cost 25% MORE than fresh input — first time content enters context is expensive.',
            'analogy': 'Like a copy shop: first copy costs extra (cache_create), but re-prints are 90% off (cache_read). Problem: you re-print the WHOLE book every turn.',
        },
        'openai': {
            'mechanism': 'Prompt Caching with 50% discount on repeated prefixes',
            'key_insight': 'GPT caches repeated prompt prefixes at 50% off. No creation surcharge. Simpler than Claude pricing but still adds up with long conversations.',
            'analogy': 'Like a subscription discount: repeat customers get 50% off. But you still pay for the full conversation every turn.',
        },
        'openai_gpt5': {
            'mechanism': 'Prompt Caching with deeply discounted cached input on repeated prefixes',
            'key_insight': 'GPT-5 family models discount cached input heavily, so re-reading repeated prefixes is cheaper than fresh input. But long sessions still get expensive because the model keeps processing a large prompt over and over.',
            'analogy': 'Like a copy shop that gives a steep discount on reprints, but you still pay every time you reprint the whole binder.',
        },
        'google': {
            'mechanism': 'Context Caching with 25% cache read cost + per-hour storage fee',
            'key_insight': 'Gemini charges 25% of input price for cached reads, plus a small hourly fee to keep the cache alive. Good for long-running sessions.',
            'analogy': 'Like a storage locker: cheap to access (25% off), but you pay rent by the hour to keep it.',
        },
        'qwen': {
            'mechanism': 'Implicit and explicit context caching with billed cache hits and writes',
            'key_insight': 'Qwen cache hits are discounted, but not free. Repeated long prompts still cost real money, and explicit-vs-implicit cache mode is not always visible in current logs.',
            'analogy': 'Like a warehouse with discounted reorders: repeats are cheaper, but every pallet you pull still has a price tag.',
        },
        'minimax': {
            'mechanism': 'Prompt caching with distinct read and write prices',
            'key_insight': 'MiniMax publishes separate cache read and cache write rates, so the first time a long prompt is stored can cost more than later hits.',
            'analogy': 'Like paying to archive a box once, then paying a smaller fee each time you retrieve it.',
        },
        'z_ai': {
            'mechanism': 'Context caching plus optional paid web search tools',
            'key_insight': 'GLM models can keep repeated context cheaper than fresh input, but search-driven agent runs can add direct tool fees on top of token charges.',
            'analogy': 'Like a consultant who discounts repeat briefings but still bills separately when they have to do outside research.',
        },
        'moonshot': {
            'mechanism': 'Cached prompt hits plus optional per-call web search charges',
            'key_insight': 'Kimi cache hits are cheaper than fresh input, but search-heavy runs can add both search fees and extra grounded tokens.',
            'analogy': 'Like a researcher who gives you a repeat-client discount, but still charges each time they run out to the library.',
        },
        'deepseek': {
            'mechanism': 'Cache read at 10-14% of input price, no creation surcharge',
            'key_insight': 'DeepSeek has the cheapest per-token rates AND cheap cache reads. But the same "re-read everything every turn" problem applies.',
            'analogy': 'Cheapest copy shop in town. But if you copy a 500-page book 60 times, even cheap copies add up.',
        },
    }

    # Universal top 10 waste descriptions for lessons (plain language)
    waste_descriptions = {
        'idle_narration': {
            'name': 'Idle narration',
            'plain': 'AI says "Now I\'ll edit the file..." then edits the file in the NEXT turn. The "now I\'ll" turn did nothing useful but re-read your entire conversation.',
            'analogy': 'Like a mechanic who narrates "now I\'ll open the hood" before opening the hood. You\'re paying for the narration.',
        },
        'context_rot': {
            'name': 'Context rot (long sessions)',
            'plain': 'Your conversation grows with every turn. Turn 50 re-reads everything from turns 1-49 — all the old code, old errors, old file contents. Late turns cost 3-5x what early turns cost.',
            'analogy': 'Like a meeting where everyone re-reads all previous meeting notes before speaking. The longer the meeting, the more re-reading.',
        },
        'pingpong_debugging': {
            'name': 'Fix-break-fix loops',
            'plain': 'AI edits code, it breaks, AI edits again, breaks differently, tries again... each cycle carries the FULL conversation history. 5 cycles can burn more than the entire rest of the session.',
            'analogy': 'Like a plumber who fixes one leak, creates another, fixes that one, creates another — charging for a full house inspection each time.',
        },
        'verbose_output': {
            'name': 'Verbose output flooding',
            'plain': 'A build command dumps 500 lines of output. That output stays in context forever — re-read on EVERY future turn. One verbose command can cost more than 10 edits.',
            'analogy': 'Like printing a 500-page report and carrying it in your backpack for the rest of the day.',
        },
        'codebase_wandering': {
            'name': 'Codebase wandering',
            'plain': 'AI doesn\'t know where things are, so it reads file after file, searches, reads more... 8 read turns before making one edit. A project map in your instructions would eliminate this.',
            'analogy': 'Like a new employee opening every drawer in the office looking for a stapler instead of asking where it is.',
        },
        'chainable_bash': {
            'name': 'Unchained commands',
            'plain': 'AI runs `git status`, waits for the response (re-reads everything), then runs `git diff` (re-reads everything again). Could have done both in one turn with `git status && git diff`.',
            'analogy': 'Like making two separate trips to the store when you could carry both bags at once.',
        },
        'unbatched_edits': {
            'name': 'Unbatched edits',
            'plain': 'AI edits File A in one turn, File B in the next, File C in the next. Each turn = full context re-read. All 3 edits could have happened in ONE turn.',
            'analogy': 'Like a tailor who makes one stitch, puts down the needle, picks it up, makes another stitch...',
        },
        'duplicate_reads': {
            'name': 'File re-reads',
            'plain': 'AI reads the same file twice in one session. After the first read, the content is already in the conversation — reading it again is pure waste.',
            'analogy': 'Like re-reading a page in a book you just read 5 minutes ago.',
        },
        'sleep_poll_loops': {
            'name': 'Sleep/poll loops',
            'plain': 'AI runs `sleep 5`, checks if a process finished, sleeps again, checks again. Each check re-reads the entire conversation.',
            'analogy': 'Like checking your oven every 30 seconds — each check costs you a walk to the kitchen.',
        },
        'failed_tools': {
            'name': 'Failed tool retries',
            'plain': 'AI tries a command that fails, then retries — the failed attempt and error message stay in context forever, adding cost to every future turn.',
            'analogy': 'Like a wrong turn on a road trip — you don\'t just lose the detour time, you carry the memory of it for the rest of the trip.',
        },
        'toolsearch': {
            'name': 'Schema lookups',
            'plain': 'AI looks up how to use a tool it already knows before using it. Like checking the instruction manual for your microwave every time you heat something up.',
            'analogy': 'Like re-reading the manual for your car before every drive.',
        },
        'git_ceremony': {
            'name': 'Git ceremony',
            'plain': 'AI runs git status, waits, then git diff, waits, then git log — three separate messages for something that takes one.',
            'analogy': 'Like asking three different people for directions to the same place instead of asking once.',
        },
        # Always-on agent patterns (OpenClaw, etc.)
        'heartbeat_idle': {
            'name': 'Idle heartbeats (always-on agents)',
            'plain': 'Your agent wakes up every few minutes to check for new tasks. If there\'s nothing to do, it still pays for a full "wake up" — re-reading its entire memory, personality, and rules. An agent checking every 5 minutes with nothing to do can cost $50/month just in wake-up fees.',
            'analogy': 'Like an employee who drives to the office every 5 minutes to check if there\'s mail, even at 3am.',
        },
        'workspace_bloat': {
            'name': 'Bloated personality files (always-on agents)',
            'plain': 'Every time the agent wakes up, it re-reads ALL its personality files (SOUL.md, AGENTS.md, rules). If these files are large and verbose, that\'s thousands of words re-read on every single wake-up. Over a day, that adds up fast.',
            'analogy': 'Like an employee who re-reads their entire 20-page job description before answering each email.',
        },
        'memory_accumulation': {
            'name': 'Memory buildup (always-on agents)',
            'plain': 'The agent\'s conversation history grows forever without cleanup. After 100+ messages, every new message costs a fortune because the AI re-reads ALL previous messages. Session pruning or compacting is essential.',
            'analogy': 'Like a filing cabinet that never gets cleaned out — eventually you can\'t find anything and it takes forever to search through.',
        },
    }

    if primary_model.startswith('gpt-5'):
        cache_explanation = cache_explanations['openai_gpt5']
    else:
        cache_explanation = cache_explanations.get(provider, cache_explanations['anthropic'])

    return {
        'language': language,
        'provider': provider,
        'primary_model': primary_model,
        'analysis_confidence': analysis_confidence,
        'pricing_registry': pricing_metadata,
        'pricing': {
            'input_per_mtok': pricing['input'],
            'output_per_mtok': pricing['output'],
            'cache_read_mult': pricing['cache_read_mult'],
            'cache_create_mult': pricing['cache_create_mult'],
        },
        'subscription_tiers': SUBSCRIPTION_TIERS.get('claude' if provider == 'anthropic' else provider, {}),
        'usage_summary': {
            'total_sessions': summary['sessions'],
            'total_cost': summary['total_cost'],
            'avg_cost_per_session': summary['avg_cost_per_session'],
            'avg_turns_per_session': summary['avg_turns_per_session'],
            'daily_cost': round(daily_cost, 2),
            'monthly_projected': round(monthly_cost, 0),
            'daily_sessions': round(daily_sessions, 1),
        },
        'worst_day': worst_day,
        'top3_waste': [{'pattern': k, 'cost': round(v, 2)} for k, v in top3_waste],
        'waste_summary': {
            'total_waste': summary['total_waste'],
            'waste_pct': summary['waste_percentage'],
            'per_session': summary['waste_per_session'],
        },
        'model_mix': model_mix,
        'cache_explanation': cache_explanation,
        'tool_pricing': PROVIDER_TOOL_PRICING.get(provider, {}),
        'waste_descriptions': waste_descriptions,
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: explain.py <analysis.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    lesson = build_lesson_plan(data)
    print(json.dumps(lesson, indent=2))

if __name__ == "__main__":
    main()
