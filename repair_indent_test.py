from pathlib import Path
import re

path = Path('routes/faq/faq.py')
lines = path.read_text(encoding='utf-8').splitlines()
new = []
in_func = False
expected = 0
for line in lines:
    stripped = line.lstrip(' ')
    indent = len(line) - len(stripped)
    if re.match(r'(def|class)\s+\w+', stripped) and indent == 0:
        in_func = True
        expected = 4
        new.append(line)
        continue
    if in_func and stripped and not stripped.startswith('@') and not (
        re.match(r'(def|class)\s+\w+', stripped) and indent == 0
    ):
        if indent < expected:
            line = ' ' * (expected - indent) + line
    if stripped == '' and in_func:
        new.append(line)
        continue
    new.append(line)
print('\n'.join(new))
