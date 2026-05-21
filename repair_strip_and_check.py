import tokenize
import io
from pathlib import Path
import py_compile

ROOT = Path('.').resolve()
EXCLUDE = {'__pycache__', '.git', 'venv', 'env', 'node_modules'}

files = list(ROOT.rglob('*.py'))
processed = 0
errors = []

for p in files:
    if any(part in EXCLUDE for part in p.parts):
        continue
    # skip this script
    if p.name in ('repair_strip_and_check.py', 'repair_indent_test.py'):
        continue
    try:
        text = p.read_text(encoding='utf-8')
    except Exception as e:
        errors.append((str(p), f'read error: {e}'))
        continue
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
        filtered = [t for t in tokens if t.type != tokenize.COMMENT]
        new = tokenize.untokenize(filtered)
    except Exception as e:
        errors.append((str(p), f'tokenize error: {e}'))
        continue
    if new != text:
        try:
            bak = p.with_name(p.name + '.bak')
            bak.write_text(text, encoding='utf-8')
            p.write_text(new, encoding='utf-8')
            processed += 1
        except Exception as e:
            errors.append((str(p), f'write error: {e}'))
            continue
    # compile check
    try:
        py_compile.compile(str(p), doraise=True)
    except py_compile.PyCompileError as e:
        errors.append((str(p), f'compile error: {e.msg}'))

print(f'Files scanned: {len(files)}, processed: {processed}, errors: {len(errors)}')
for f, m in errors:
    print(f'ERROR: {f} -> {m}')
