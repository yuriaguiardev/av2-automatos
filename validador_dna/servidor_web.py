"""Interface web (biblioteca padrao: http.server) para a demonstracao em sala.

Execucao:  python -m validador_dna web            (abre http://127.0.0.1:8000)
           python -m validador_dna web --porta 8080 --sem-navegador

Rotas:
  GET  /                       pagina (validador_dna/web/index.html)
  POST /api/validar            {"cadeia": "...", "modo": "completo" | "ap" | "all"}
  POST /api/derivar            {"cadeia": "..."}
  GET  /api/especificacao      GLC, AP e ALL em texto
"""

from __future__ import annotations

import json
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import formatacao as F
from .alfabetos import SimboloForaDoAlfabeto
from .automato_linear import ResultadoALL
from .automato_linear import reconhecer as rodar_all
from .automato_pilha import ResultadoAP
from .automato_pilha import reconhecer as rodar_ap
from .pipeline import validar

PAGINA = Path(__file__).with_name("web") / "index.html"
# O ALL faz O(n^2) passos; o limite evita respostas enormes no navegador.
COMPRIMENTO_MAXIMO = 300

EXEMPLOS = [
    {"cadeia": "GATCCgaaaGGATC#ATGGCAATGGCA", "rotulo": "Cenário 1 — aceito pelo AP e pelo ALL", "modo": "completo"},
    {"cadeia": "GATCCgaaaGGATG#ATGGCAATGGCA", "rotulo": "Cenário 2 — rejeitado pelo AP", "modo": "completo"},
    {"cadeia": "GATCCgaaaGGATC#ATGGCAATGGCT", "rotulo": "Cenário 3 — aceito pelo AP, rejeitado pelo ALL", "modo": "completo"},
    {"cadeia": "GATCCgaaaGGATC#ATGGCNATGGCA", "rotulo": "Extra — símbolo fora do alfabeto", "modo": "completo"},
    {"cadeia": "GGACgaaGTCC#ATGATG", "rotulo": "Menor cadeia aceita (n = 18)", "modo": "completo"},
    {"cadeia": "CAGCAGCAGCAGCAGCAG", "rotulo": "Entrada só para o ALL (CAG repetido)", "modo": "all"},
]


def _ap_json(res: ResultadoAP) -> dict:
    return {
        "cadeia": res.cadeia,
        "aceita": res.aceita,
        "decisao": res.decisao,
        "motivo": res.motivo,
        "passos": [
            {"passo": p.passo, "estado": p.estado, "posicao": p.posicao, "lida": p.lida,
             "restante": p.restante, "pilha": p.pilha, "transicao": p.transicao}
            for p in res.passos
        ],
    }


def _all_json(res: ResultadoALL) -> dict:
    return {
        "cadeia": res.cadeia,
        "aceita": res.aceita,
        "decisao": res.decisao,
        "motivo": res.motivo,
        "passos": [
            {"passo": p.passo, "estado": p.estado, "cabecote": p.cabecote, "fita": p.fita, "transicao": p.transicao}
            for p in res.passos
        ],
    }


def processar_validacao(cadeia: str, modo: str) -> dict:
    """Executa o modo pedido e devolve um dicionario serializavel em JSON."""
    cadeia = cadeia.strip()
    if not cadeia:
        return {"erro": "Digite uma cadeia."}
    if len(cadeia) > COMPRIMENTO_MAXIMO:
        return {"erro": f"A interface web aceita cadeias de até {COMPRIMENTO_MAXIMO} símbolos (recebida: {len(cadeia)})."}

    if modo == "ap":
        try:
            return {"modo": modo, "cadeia": cadeia, "ap": _ap_json(rodar_ap(cadeia))}
        except SimboloForaDoAlfabeto as e:
            return {"modo": modo, "cadeia": cadeia, "erro": str(e)}
    if modo == "all":
        try:
            return {"modo": modo, "cadeia": cadeia, "all": _all_json(rodar_all(cadeia))}
        except SimboloForaDoAlfabeto as e:
            return {"modo": modo, "cadeia": cadeia, "erro": str(e)}
    if modo != "completo":
        return {"erro": f"Modo desconhecido: {modo!r}."}

    res = validar(cadeia)
    return {
        "modo": modo,
        "cadeia": cadeia,
        "erro": res.erro,
        "decisao": res.decisao,
        "aceita": res.aceita,
        "trecho_all": res.trecho_all,
        "ap": None if res.ap is None else _ap_json(res.ap),
        "all": None if res.all is None else _all_json(res.all),
    }


def processar_derivacao(cadeia: str) -> dict:
    cadeia = cadeia.strip()
    try:
        return {"cadeia": cadeia, "texto": F.derivacao(cadeia)}
    except ValueError as e:
        return {"cadeia": cadeia, "erro": str(e)}


def especificacao() -> dict:
    return {
        "glc": F.especificacao_glc(),
        "ap": F.especificacao_ap(),
        "all": F.especificacao_all(),
        "exemplos": EXEMPLOS,
    }


class Manipulador(BaseHTTPRequestHandler):
    server_version = "ValidadorDNA/1.0"

    def log_message(self, formato: str, *args) -> None:  # silencia o log padrao
        pass

    def _responder(self, status: HTTPStatus, corpo: bytes, tipo: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, dados: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._responder(status, json.dumps(dados, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        caminho = self.path.split("?", 1)[0]
        if caminho in ("/", "/index.html"):
            self._responder(HTTPStatus.OK, PAGINA.read_bytes(), "text/html; charset=utf-8")
        elif caminho == "/api/especificacao":
            self._json(especificacao())
        else:
            self._json({"erro": "Rota não encontrada."}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            dados = json.loads(self.rfile.read(min(tamanho, 10_000)) or b"{}")
            cadeia = str(dados.get("cadeia", ""))
        except (ValueError, json.JSONDecodeError, AttributeError):
            self._json({"erro": "Requisição inválida."}, HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/validar":
            self._json(processar_validacao(cadeia, str(dados.get("modo", "completo"))))
        elif self.path == "/api/derivar":
            self._json(processar_derivacao(cadeia))
        else:
            self._json({"erro": "Rota não encontrada."}, HTTPStatus.NOT_FOUND)


def iniciar(porta: int = 8000, abrir_navegador: bool = True) -> None:
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), Manipulador)
    url = f"http://127.0.0.1:{servidor.server_port}/"
    print(f"Interface web em {url}  (Ctrl+C para encerrar)")
    if abrir_navegador:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.server_close()
