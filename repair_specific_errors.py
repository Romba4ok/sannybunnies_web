import re
from pathlib import Path
import py_compile

ERR_FILES = [
    'auth_service.py',
    'firebase_admin_service.py',
    'scripts/migrate_children.py',
    'routes/auth/auth.py',
    'routes/faq/faq.py',
    'routes/groups/groups.py',
    'routes/interior/interior.py',
    'routes/kindergarten/kindergarten.py',
    'routes/menu/menu.py',
    'routes/news/news.py',
    'routes/requests/requests.py',
    'routes/reviews/reviews.py',
    'routes/schedule/schedule.py',
    'routes/teachers/teachers.py',
    'routes/users/users.py',
]

ROOT = Path('.')

for rel in ERR_FILES:
    p = ROOT / rel
    if not p.exists():
        print('missing', rel)
        continue
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    new = []
    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip(' ')
        indent = len(line) - len(stripped)
        if re.match(r'(def|class)\s+\w+', stripped) and indent == 0:
            new.append(line)
            i += 1
                                    
            while i < len(lines):
                nxt = lines[i]
                nxt_stripped = nxt.lstrip(' ')
                nxt_indent = len(nxt) - len(nxt_stripped)
                if nxt.strip() == '':
                    new.append(nxt)
                    i += 1
                    continue
                if re.match(r'(def|class)\s+\w+', nxt_stripped) and nxt_indent == 0:
                    break
                if nxt_stripped.startswith('@'):
                    new.append(nxt)
                    i += 1
                    continue
                if nxt_indent == 0:
                    new.append(' ' * 4 + nxt)
                    changed = True
                else:
                    new.append(nxt)
                i += 1
            continue
        else:
            new.append(line)
            i += 1
    if changed:
        bak = p.with_name(p.name + '.bak2')
        bak.write_text(text, encoding='utf-8')
        p.write_text('\n'.join(new) + ('\n' if text.endswith('\n') else ''), encoding='utf-8')
        print('fixed', rel)
    else:
        print('no-change', rel)
    try:
        py_compile.compile(str(p), doraise=True)
        print('ok', rel)
    except py_compile.PyCompileError as e:
        print('compile-error', rel, e.msg)
