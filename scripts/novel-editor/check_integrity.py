import re, os
OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_PATH = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('ch149 body expansion', '重新谈判距离'),
    ('ch91 sensory expansion', '火舌舔着锅底'),
    ('ch152 bridge paragraph', '瓜叶大得像一把一把的蒲扇'),
    ('ch152 blessing line', '找到属于你自己的'),
    ('ch76 reunion detail', '穿着一件洗旧了的灰布衫'),
]
for label, keyword in checks:
    found = keyword in html
    print(f'{label}: {"OK" if found else "MISSING"}')

cnt = html.count('在朝堂上站久了')
print(f'ch49 court reflection: count={cnt} (expect 1)')

# Artifacts
print(f'Empty inner-mono: {len(re.findall(r"<div class=\"inner-monologue\">\s*<p>\s*</p>\s*</div>", html))}')
print(f'Double inner-mono: {len(re.findall(r"<div class=\"inner-monologue\">.*?<div class=\"inner-monologue\">", html, re.DOTALL))}')
print(f'Double wan: {len(re.findall(r"（完）\s*（完）", html))}')

# Check for broken edits
print(f'ch76 original text still present: {"沈秋白真的回来了。" in html and "穿着一件洗旧了的灰布衫" in html}')
