"""Reset the local SQLite demo database and regenerate realistic NEXORA data."""
from pathlib import Path
import subprocess, sys

root = Path(__file__).resolve().parent
for name in ('nexora.db', 'nexora.db-shm', 'nexora.db-wal'):
    p = root / name
    if p.exists(): p.unlink()
subprocess.run([sys.executable, '-m', 'app.seed'], cwd=root, check=True)
print('NEXORA demo database reset complete.')
