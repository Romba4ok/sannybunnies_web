import pathlib, py_compile
root = pathlib.Path('.')
for path in root.rglob('*.py'):
    if any(part in path.parts for part in ('__pycache__', '.venv', 'venv', '.git')):
        continue
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as e:
        print(path, repr(str(e)))
