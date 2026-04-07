#!/usr/bin/env python3
"""
Measure document size in words, lines, characters, and estimated tokens.

Token estimation uses the ~4 chars/token heuristic for English text,
which is accurate within ~10% for Claude/GPT tokenizers without needing
tiktoken installed.

Usage:
    python measure.py file1.txt [file2.txt ...]
    python measure.py original.txt compressed.txt  # shows comparison
"""

import sys
from pathlib import Path


def estimate_tokens(text: str) -> int:
    """Estimate token count. ~4 chars per token for English text."""
    return len(text) // 4


def measure(text: str) -> dict:
    lines = text.count('\n') + (1 if text and not text.endswith('\n') else 0)
    words = len(text.split())
    chars = len(text)
    tokens = estimate_tokens(text)
    return {'lines': lines, 'words': words, 'chars': chars, 'tokens_est': tokens}


def main():
    if len(sys.argv) < 2:
        print("Usage: measure.py file1.txt [file2.txt ...]", file=sys.stderr)
        sys.exit(1)

    files = [Path(f) for f in sys.argv[1:]]
    results = []

    for f in files:
        text = f.read_text(encoding='utf-8')
        m = measure(text)
        results.append((f.name, m))

    # Single file
    if len(results) == 1:
        name, m = results[0]
        print(f"{name}: {m['words']:,} words | {m['lines']:,} lines | {m['chars']:,} chars | ~{m['tokens_est']:,} tokens")
        return

    # Comparison mode
    print(f"{'File':<30} {'Words':>8} {'Lines':>8} {'Chars':>10} {'~Tokens':>10}")
    print('-' * 70)
    for name, m in results:
        print(f"{name:<30} {m['words']:>8,} {m['lines']:>8,} {m['chars']:>10,} {m['tokens_est']:>10,}")

    if len(results) == 2:
        before = results[0][1]
        after = results[1][1]
        word_delta = after['words'] - before['words']
        token_delta = after['tokens_est'] - before['tokens_est']
        word_pct = (word_delta / before['words'] * 100) if before['words'] else 0
        token_pct = (token_delta / before['tokens_est'] * 100) if before['tokens_est'] else 0
        print('-' * 70)
        print(f"{'Delta':<30} {word_delta:>+8,} {'':>8} {'':>10} {token_delta:>+10,}")
        print(f"{'Reduction':<30} {abs(word_pct):>7.1f}% {'':>8} {'':>10} {abs(token_pct):>9.1f}%")


if __name__ == '__main__':
    main()
