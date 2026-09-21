import os
from pathlib import Path


def load_dotenv() -> None:
    path = Path(__file__).resolve().parents[2] / '.env'
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        os.environ.setdefault(key.strip(), value.strip())
