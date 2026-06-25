# Helper script to write merged chapters
import os

base_dir = r'd:\ProgramWork\WriteBooksProject\docs\2026-06-25\小说\满身遗憾的人\合并章节'

# Read a chapter file
def read_chapter(num):
    path = rf'd:\ProgramWork\WriteBooksProject\docs\2026-06-25\小说\满身遗憾的人\章节\chapter-{num:03d}.md'
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# Test
for n in [65, 66, 67]:
    c = read_chapter(n)
    print(f"Chapter {n}: {len(c)} chars")

print("Test OK")
