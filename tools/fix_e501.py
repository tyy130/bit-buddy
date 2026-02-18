#!/usr/bin/env python3
"""
Auto-fix common flake8 E501 errors by adding line breaks
This handles cases Black doesn't catch (long strings, comments, etc.)
"""

import re
from pathlib import Path


def fix_long_strings(filepath: Path):
    """Fix long string literals by breaking them up"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    for line in lines:
        if len(line.rstrip()) <= 79:
            new_lines.append(line)
            continue

        # Check for long f-strings or regular strings
        # Pattern: long string in function call
        if re.search(r'["\'].*["\']', line) and len(line.rstrip()) > 79:
            # Try to break at a reasonable point
            indent = len(line) - len(line.lstrip())
            indent_str = " " * indent

            # Check if it's an f-string
            if 'f"' in line or "f'" in line:
                # Try to split f-string
                match = re.search(r'(.*?f["\'])(.+)(["\'].*)', line)
                if match and len(match.group(2)) > 40:
                    # Split into multiple parts
                    prefix = match.group(1)
                    content = match.group(2)
                    suffix = match.group(3)

                    # Find a good break point (space, comma, etc.)
                    mid = len(content) // 2
                    break_point = content.rfind(" ", 0, mid + 20)
                    if break_point < 0:
                        break_point = content.find(" ", mid)

                    if break_point > 0:
                        part1 = content[:break_point]
                        part2 = content[break_point + 1 :]

                        new_lines.append(
                            f"{indent_str}(\n"
                            f'{indent_str}    {prefix}{part1}"\n'
                            f'{indent_str}    f"{part2}{suffix}\n'
                            f"{indent_str})\n"
                        )
                        modified = True
                        continue

        # If no special handling, keep original
        new_lines.append(line)

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    return False


def main():
    """Fix E501 errors in all Python files"""
    files = [
        "buddy_gui.py",
        "installer.py",
        "debug_tools.py",
        "deploy.py",
        "enhanced_buddy.py",
        "mesh_network.py",
        "setup.py",
        "test_runner.py",
    ]

    print("🔧 Auto-fixing E501 errors...")
    fixed = 0

    for filename in files:
        filepath = Path(filename)
        if not filepath.exists():
            continue

        if fix_long_strings(filepath):
            print(f"  ✓ Fixed {filename}")
            fixed += 1
        else:
            print(f"  - {filename} (no changes)")

    print(f"\n✅ Modified {fixed} files")
    print("\n💡 Run 'black --line-length 79 .' to format")
    print("   Then 'flake8 --select=E501' to verify")


if __name__ == "__main__":
    main()
