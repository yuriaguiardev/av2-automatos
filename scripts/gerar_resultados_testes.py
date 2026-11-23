"""Executa todos os casos de dados/*.json e registra entrada, decisao esperada,
decisao obtida e regra verificada em docs/resultados_testes.md e .csv.
Tambem salva rastreamentos completos em docs/rastreamentos/.

Uso:  python scripts/gerar_resultados_testes.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from validador_dna import formatacao as F  # noqa: E402
from validador_dna.alfabetos import SimboloForaDoAlfabeto  # noqa: E402
from validador_dna.automato_linear import reconhecer as rodar_all  # noqa: E402
from validador_dna.automato_pilha import reconhecer as rodar_ap  # noqa: E402
from validador_dna.pipeline import validar  # noqa: E402

DOCS = RAIZ / "docs"


def carregar(nome: str) -> list[dict]:
    return json.loads((RAIZ / "dados" / nome).read_text(encoding="utf-8"))


def executar_todos() -> dict[str, list[dict]]:
    """Retorna as linhas de resultado de cada grupo de testes."""
    grupos: dict[str, list[dict]] = {"ap": [], "all": [], "integracao": [], "erro": []}
    for c in carregar("casos_ap.json"):
        r = rodar_ap(c["entrada"])
        grupos["ap"].append({**c, "n": len(c["entrada"]), "obtido": r.decisao, "motivo": r.motivo})
    for c in carregar("casos_all.json"):
        r = rodar_all(c["entrada"])
        grupos["all"].append({**c, "n": len(c["entrada"]), "obtido": r.decisao, "motivo": r.motivo,
                              "passos": len(r.passos) - 1})
    for c in carregar("casos_integracao.json"):
        r = validar(c["entrada"])
        grupos["integracao"].append({
            **c, "n": len(c["entrada"]), "obtido": r.decisao,
            "obtido_ap": r.ap.decisao, "obtido_all": "NÃO EXECUTA" if r.all is None else r.all.decisao,
            "motivo": r.ap.motivo if r.all is None else r.all.motivo,
        })
    for c in carregar("casos_erro.json"):
        if c["modulo"] == "validar":
            res = validar(c["entrada"])
            msg, obtido = (res.erro, "ERRO") if res.erro else ("(sem erro)", res.decisao)
        else:
            try:
                (rodar_ap if c["modulo"] == "ap" else rodar_all)(c["entrada"])
                msg, obtido = "(sem erro)", "SEM ERRO"
            except SimboloForaDoAlfabeto as e:
                msg, obtido = str(e), "ERRO"
        grupos["erro"].append({**c, "n": len(c["entrada"]), "obtido": obtido, "motivo": msg})
    for linhas in grupos.values():
        for l in linhas:
            l["ok"] = l["obtido"] == l["esperado"]
    return grupos


def _md(texto: str) -> str:
    return texto.replace("|", "\\|")


def _entrada_md(e: str) -> str:
    return f"`{e}`" if e else "ε (vazia)"


def gerar() -> dict[str, list[dict]]:
    grupos = executar_todos()
    DOCS.mkdir(exist_ok=True)

    with open(DOCS / "resultados_testes.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["grupo", "id", "entrada", "n", "esperado", "obtido", "ok", "regra verificada", "motivo/mensagem"])
        for g, linhas in grupos.items():
            for l in linhas:
                w.writerow([g, l["id"], l["entrada"], l["n"], l["esperado"], l["obtido"],
                            "sim" if l["ok"] else "NÃO", l["regra"], l["motivo"]])

    total = sum(len(v) for v in grupos.values())
    ok = sum(l["ok"] for v in grupos.values() for l in v)
    md = [f"# Resultados dos testes\n", f"Gerado por `python scripts/gerar_resultados_testes.py`. "
          f"**{ok}/{total} casos com decisão obtida igual à esperada.**\n"]
    titulos = {
        "ap": "## Módulo 1 — Autômato de Pilha",
        "all": "## Módulo 2 — Autômato Linearmente Limitado",
        "integracao": "## Fluxo completo (integração AP → ALL)",
        "erro": "## Símbolos fora do alfabeto de entrada",
    }
    for g, linhas in grupos.items():
        md.append(titulos[g] + "\n")
        if g == "integracao":
            md.append("| ID | Entrada | n | AP esperado/obtido | ALL esperado/obtido | Final esperado | Final obtido | Regra verificada |")
            md.append("|---|---|---|---|---|---|---|---|")
            for l in linhas:
                md.append(f"| {l['id']} | {_entrada_md(l['entrada'])} | {l['n']} | {l['esperado_ap']} / {l['obtido_ap']} | "
                          f"{l['esperado_all']} / {l['obtido_all']} | {l['esperado']} | {l['obtido']} | {_md(l['regra'])} |")
        elif g == "erro":
            md.append("| ID | Módulo | Entrada | Esperado | Obtido | Mensagem exibida |")
            md.append("|---|---|---|---|---|---|")
            for l in linhas:
                md.append(f"| {l['id']} | {l['modulo']} | {_entrada_md(l['entrada'])} | {l['esperado']} | {l['obtido']} | {_md(l['motivo'])} |")
        else:
            md.append("| ID | Entrada | n | Esperado | Obtido | Regra verificada | Justificativa do autômato |")
            md.append("|---|---|---|---|---|---|---|")
            for l in linhas:
                md.append(f"| {l['id']} | {_entrada_md(l['entrada'])} | {l['n']} | {l['esperado']} | {l['obtido']} | "
                          f"{_md(l['regra'])} | {_md(l['motivo'])} |")
        md.append("")
    (DOCS / "resultados_testes.md").write_text("\n".join(md), encoding="utf-8")

    rastros = DOCS / "rastreamentos"
    rastros.mkdir(exist_ok=True)
    for c in carregar("casos_integracao.json"):
        r = validar(c["entrada"])
        partes = [f"{c['id']} — {c['regra']}", "", F.rastro_ap(r.ap)]
        if r.all is not None:
            partes += ["", F.rastro_all(r.all)]
        partes += ["", r.resumo()]
        (rastros / f"{c['id']}.txt").write_text("\n".join(partes) + "\n", encoding="utf-8")
    (rastros / "derivacao_AP-A01.txt").write_text(F.derivacao("GGACgaaGTCC#ATGATG") + "\n", encoding="utf-8")
    (rastros / "derivacao_INT-1.txt").write_text(F.derivacao(carregar("casos_integracao.json")[0]["entrada"]) + "\n",
                                                 encoding="utf-8")
    print(f"{ok}/{total} casos conferem. Arquivos em {DOCS}")
    return grupos


if __name__ == "__main__":
    grupos = gerar()
    sys.exit(0 if all(l["ok"] for v in grupos.values() for l in v) else 1)
