import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
DADOS = RAIZ / "dados"


def carregar(nome: str) -> list[dict]:
    with open(DADOS / nome, encoding="utf-8") as f:
        return json.load(f)
