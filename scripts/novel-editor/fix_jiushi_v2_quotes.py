"""Fix quote conflicts in v2 script by escaping internal ASCII double-quotes"""
with open('d:/ProgramWork/WriteBookProject/scripts/optimize_jiushi_dashes_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Strategy: For lines that are Python tuples like ("old", "new"),
# if the old or new string contains unescaped ASCII " (U+0022) inside the Python "..." delimiter,
# we need to either:
# 1. Escape them as \"
# 2. Or change the Python delimiter to '...'

# Simplest approach: Process line by line
# Find replacement tuple lines: they start with whitespace + ("
# If the string content between outer quotes contains ASCII " not preceded by \,
# change Python delimiter to single quote '...' (and escape any internal ASCII ')

import re

lines = content.split('\n')
fixed_lines = []
fixes = 0

for line in lines:
    # Check if this is a replacement tuple line
    stripped = line.strip()
    if (stripped.startswith('("') or stripped.startswith("('")) and '", "' in stripped:
        # This is a replacement tuple
        # Extract the indent
        indent = line[:len(line) - len(line.lstrip())]

        # Strategy: convert to use single quotes for Python strings
        # But we need to handle the content carefully
        # For now, just use triple-quoted strings to be safe

        # Actually simpler: just escape internal ASCII "
        # Find all " that are inside the Python strings (not at string boundaries)
        # The pattern is: ("...", "...") where the ... may contain "

        # Let's try regex to find the two strings
        m = re.match(r'(\s*)\((".*"),\s*(".*")\)\s*,?\s*$', line)
        if m:
            indent_str = m.group(1)
            old_str = m.group(2)  # includes outer quotes
            new_str = m.group(3)  # includes outer quotes

            # Check if old_str or new_str has internal ASCII "
            # Remove outer quotes
            old_inner = old_str[1:-1]
            new_inner = new_str[1:-1]

            if '"' in old_inner or '"' in new_inner:
                # Escape internal "
                old_fixed = '"' + old_inner.replace('"', '\\"') + '"'
                new_fixed = '"' + new_inner.replace('"', '\\"') + '"'
                fixed_line = f'{indent_str}({old_fixed}, {new_fixed}),'
                fixed_lines.append(fixed_line)
                fixes += 1
                continue

    fixed_lines.append(line)

with open('d:/ProgramWork/WriteBookProject/scripts/optimize_jiushi_dashes_v2.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print(f'Fixed {fixes} lines')
