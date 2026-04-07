#!/usr/bin/env python3
"""
Pass 1: Mechanical Markdown stripping.

Removes formatting tokens (headers, bold, italic, bullets, code fences, etc.)
while preserving section numbers, blank lines, and semantic content.

Usage:
    python strip_markdown.py input.txt output.txt
    python strip_markdown.py input.txt  # prints to stdout
"""

import re
import sys
from pathlib import Path


def catalog_section_numbers(text: str) -> set[str]:
    """Extract all section/subsection numbers for post-verification."""
    # Match patterns like "1.", "8.7.3", "§16.1", "Appendix A"
    numbers = set()
    for line in text.splitlines():
        stripped = line.lstrip("#").strip()
        # Section number at start of line: "8.7.3 Title" or "§8.7.3 Title"
        m = re.match(r'^(§?\d+(?:\.\d+)*\.?)\s', stripped)
        if m:
            numbers.add(m.group(1).rstrip('.'))
        # Appendix references
        m = re.match(r'^(Appendix\s+[A-Z])\b', stripped, re.IGNORECASE)
        if m:
            numbers.add(m.group(1))
    return numbers


def is_section_header(line: str) -> bool:
    """Detect if a numbered line is a section header vs a list item."""
    stripped = line.lstrip()
    # Lines starting with §
    if stripped.startswith('§'):
        return True
    # Lines with Markdown heading markers followed by number
    if re.match(r'^#{1,6}\s+\d', stripped):
        return True
    # Standalone numbered title (number + capitalized words, not part of a sequence)
    if re.match(r'^\d+(?:\.\d+)*\.?\s+[A-Z]', stripped):
        # Heuristic: if it's short-ish and title-cased, likely a header
        words = stripped.split()
        if len(words) <= 12:
            return True
    return False


def strip_markdown(text: str) -> str:
    """Apply Pass 1 mechanical transformations."""
    lines = text.splitlines()
    result = []
    in_code_block = False
    in_table = False
    table_rows = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Handle code fences
        if re.match(r'^```', line.strip()):
            if in_code_block:
                in_code_block = False
                i += 1
                continue
            else:
                in_code_block = True
                i += 1
                continue

        if in_code_block:
            # Keep code content, strip the fence markers only
            result.append(line)
            i += 1
            continue

        # Handle tables - collect rows and convert
        if '|' in line and re.match(r'^\s*\|', line.strip()):
            # Skip separator rows
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
                i += 1
                continue
            # Extract cell contents
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if cells:
                table_rows.append(cells)
            i += 1
            # Check if next line continues table
            if i < len(lines) and '|' in lines[i] and re.match(r'^\s*\|', lines[i].strip()):
                continue
            # Flush table
            for row in table_rows:
                result.append('; '.join(row))
            table_rows = []
            continue

        # Strip heading markers but preserve section numbers
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            content = heading_match.group(2).strip()
            result.append(content)
            i += 1
            continue

        # Strip blockquote markers
        if line.lstrip().startswith('> '):
            line = re.sub(r'^(\s*)>\s?', r'\1', line)

        # Strip horizontal rules
        if re.match(r'^\s*[-*_]{3,}\s*$', line):
            result.append('')
            i += 1
            continue

        # Strip bold/italic markers
        line = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', line)
        line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
        line = re.sub(r'\*(.*?)\*', r'\1', line)
        line = re.sub(r'_(.*?)_', r'\1', line)

        # Strip inline code backticks (but keep content)
        line = re.sub(r'`([^`]+)`', r'\1', line)

        # Convert link syntax: [text](url) -> text (url) or just text
        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', line)

        # Handle bullet lists - convert to semicolon-separated
        bullet_match = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if bullet_match:
            indent = bullet_match.group(1)
            content = bullet_match.group(2)
            # Look ahead for consecutive bullets at same indent
            items = [content]
            while i + 1 < len(lines):
                next_match = re.match(r'^' + re.escape(indent) + r'[-*+]\s+(.*)', lines[i + 1])
                if next_match:
                    items.append(next_match.group(1))
                    i += 1
                else:
                    break
            if len(items) > 1:
                # Join short items with semicolons, keep long ones as separate lines
                if all(len(item) < 80 for item in items):
                    result.append('; '.join(items))
                else:
                    for item in items:
                        result.append(item)
            else:
                result.append(content)
            i += 1
            continue

        # Handle numbered lists (but NOT section headers)
        num_match = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if num_match and not is_section_header(line):
            indent = num_match.group(1)
            content = num_match.group(2)
            items = [content]
            while i + 1 < len(lines):
                next_match = re.match(r'^' + re.escape(indent) + r'\d+\.\s+(.*)', lines[i + 1])
                if next_match and not is_section_header(lines[i + 1]):
                    items.append(next_match.group(1))
                    i += 1
                else:
                    break
            if len(items) > 1 and all(len(item) < 80 for item in items):
                result.append('; '.join(items))
            else:
                for item in items:
                    result.append(item)
            i += 1
            continue

        result.append(line)
        i += 1

    return '\n'.join(result)


def verify_sections(original: str, compressed: str) -> list[str]:
    """Check that all section numbers survived compression."""
    orig_nums = catalog_section_numbers(original)
    comp_nums = catalog_section_numbers(compressed)
    missing = orig_nums - comp_nums
    return sorted(missing)


def count_stats(text: str) -> dict:
    """Count lines, words, and characters."""
    lines = text.count('\n') + (1 if text and not text.endswith('\n') else 0)
    words = len(text.split())
    chars = len(text)
    return {'lines': lines, 'words': words, 'chars': chars}


def main():
    if len(sys.argv) < 2:
        print("Usage: strip_markdown.py input.txt [output.txt]", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    original = input_path.read_text(encoding='utf-8')

    before = count_stats(original)
    compressed = strip_markdown(original)
    after = count_stats(compressed)

    # Verify section numbers
    missing = verify_sections(original, compressed)
    if missing:
        print(f"WARNING: Missing section numbers: {', '.join(missing)}", file=sys.stderr)

    # Report
    word_reduction = (1 - after['words'] / before['words']) * 100 if before['words'] else 0
    print(f"Pass 1: {before['words']} → {after['words']} words ({word_reduction:.1f}% reduction)", file=sys.stderr)
    if missing:
        print(f"  ⚠ {len(missing)} section number(s) may need manual check", file=sys.stderr)
    else:
        print(f"  ✓ All section numbers preserved", file=sys.stderr)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
        output_path.write_text(compressed, encoding='utf-8')
        print(f"  Written to {output_path}", file=sys.stderr)
    else:
        print(compressed)


if __name__ == '__main__':
    main()
