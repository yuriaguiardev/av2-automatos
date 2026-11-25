"""Interface de linha de comando.

Exemplos:
  python -m validador_dna validar "GATCCgaaaGGATC#ATGGCAATGGCA" --rastro
  python -m validador_dna ap "GGACgaaGTCC#ATGATG"
  python -m validador_dna all "CAGCAGCAGCAGCAGCAG" --resumido
  python -m validador_dna derivar "GGACgaaGTCC#ATGATG"
  python -m validador_dna demo
  python -m validador_dna especificacao
  python -m validador_dna interativo
  python -m validador_dna gui
  python -m validador_dna web
"""

from __future__ import annotations

import argparse
import os
import sys

from . import formatacao as F
from .alfabetos import SimboloForaDoAlfabeto
from .automato_linear import reconhecer as rodar_all
from .automato_pilha import reconhecer as rodar_ap
from .pipeline import validar

CENARIOS_DEMO = [
    ("Cenário 1 — aceito pelo AP e pelo ALL", "GATCCgaaaGGATC#ATGGCAATGGCA"),
    ("Cenário 2 — rejeitado pelo AP (ALL não executa)", "GATCCgaaaGGATG#ATGGCAATGGCA"),
    ("Cenário 3 — aceito pelo AP, rejeitado pelo ALL", "GATCCgaaaGGATC#ATGGCAATGGCT"),
    ("Cenário extra — símbolo fora do alfabeto", "GATCCgaaaGGATC#ATGGCNATGGCA"),
]


def _configurar_console() -> None:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    if os.name == "nt":
        os.system("")  # habilita sequencias ANSI no console do Windows


def _cor(texto: str) -> str:
    if not sys.stdout.isatty():
        return texto
    if texto.startswith("ACEITA"):
        return f"\033[1;32m{texto}\033[0m"
    if texto.startswith(("REJEITA", "ERRO")):
        return f"\033[1;31m{texto}\033[0m"
    return texto


def _limpar(cadeia: str) -> str:
    # Aspas e espacos externos sao tratados como formatacao da linha de comando.
    return cadeia.strip()


def cmd_validar(cadeia: str, rastro: bool, resumido: bool) -> int:
    res = validar(cadeia)
    print(f"Entrada: '{cadeia}' (n = {len(cadeia)})")
    if res.erro:
        print(_cor(res.erro))
        return 2
    if rastro:
        print()
        print(F.rastro_ap(res.ap))  # type: ignore[arg-type]
        if res.all is not None:
            print()
            print(F.rastro_all(res.all, resumido=resumido))
        print()
    print(res.resumo())
    print("Decisão:", _cor(res.decisao))
    return 0 if res.aceita else 1


def cmd_ap(cadeia: str) -> int:
    try:
        res = rodar_ap(cadeia)
    except SimboloForaDoAlfabeto as e:
        print(_cor(str(e)))
        return 2
    print(F.rastro_ap(res))
    print("Decisão:", _cor(res.decisao))
    return 0 if res.aceita else 1


def cmd_all(cadeia: str, resumido: bool) -> int:
    try:
        res = rodar_all(cadeia)
    except SimboloForaDoAlfabeto as e:
        print(_cor(str(e)))
        return 2
    print(F.rastro_all(res, resumido=resumido))
    print("Decisão:", _cor(res.decisao))
    return 0 if res.aceita else 1


def cmd_derivar(cadeia: str) -> int:
    try:
        print(F.derivacao(cadeia))
    except ValueError as e:
        print(_cor(f"ERRO: {e}"))
        return 1
    return 0


def cmd_demo(resumido: bool) -> int:
    for titulo, cadeia in CENARIOS_DEMO:
        print("=" * 100)
        print(titulo)
        print("=" * 100)
        cmd_validar(cadeia, rastro=True, resumido=resumido)
        print()
    return 0


def cmd_interativo() -> int:
    print("Validador de construtos de DNA (AP + ALL). Digite uma cadeia ou um comando:")
    print("  :ap <cadeia>   :all <cadeia>   :der <cadeia>   :resumido   :sair")
    resumido = True
    while True:
        try:
            linha = input("\ncadeia> ")
        except EOFError:
            return 0
        linha = linha.strip()
        if linha in (":sair", ":q"):
            return 0
        if linha == ":resumido":
            resumido = not resumido
            print(f"Rastreamento do ALL resumido: {resumido}")
        elif linha.startswith(":ap "):
            cmd_ap(_limpar(linha[4:]))
        elif linha.startswith(":all "):
            cmd_all(_limpar(linha[5:]), resumido)
        elif linha.startswith(":der "):
            cmd_derivar(_limpar(linha[5:]))
        else:
            cmd_validar(linha, rastro=True, resumido=resumido)


def main(argv: list[str] | None = None) -> int:
    _configurar_console()
    parser = argparse.ArgumentParser(
        prog="python -m validador_dna",
        description="Validador de construtos de DNA: AP (grampo) seguido de ALL (repetição em tandem).",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("validar", help="fluxo completo AP -> ALL")
    p.add_argument("cadeia")
    p.add_argument("--rastro", action="store_true", help="mostra os rastreamentos dos dois autômatos")
    p.add_argument("--resumido", action="store_true", help="omite passos do ALL que só deslocam o cabeçote")

    p = sub.add_parser("ap", help="executa somente o autômato de pilha")
    p.add_argument("cadeia")

    p = sub.add_parser("all", help="executa somente o autômato linearmente limitado")
    p.add_argument("cadeia")
    p.add_argument("--resumido", action="store_true")

    p = sub.add_parser("derivar", help="derivação mais à esquerda na GLC")
    p.add_argument("cadeia")

    p = sub.add_parser("demo", help="executa os três cenários de integração e o teste de erro")
    p.add_argument("--resumido", action="store_true")

    sub.add_parser("especificacao", help="imprime GLC, AP e ALL formalmente")
    sub.add_parser("interativo", help="modo interativo no terminal")
    sub.add_parser("gui", help="interface gráfica (Tkinter)")
    p = sub.add_parser("web", help="interface web no navegador (http://127.0.0.1:8000)")
    p.add_argument("--porta", type=int, default=8000)
    p.add_argument("--sem-navegador", action="store_true", help="não abre o navegador automaticamente")

    args = parser.parse_args(argv)
    if args.comando == "validar":
        return cmd_validar(_limpar(args.cadeia), args.rastro, args.resumido)
    if args.comando == "ap":
        return cmd_ap(_limpar(args.cadeia))
    if args.comando == "all":
        return cmd_all(_limpar(args.cadeia), args.resumido)
    if args.comando == "derivar":
        return cmd_derivar(_limpar(args.cadeia))
    if args.comando == "demo":
        return cmd_demo(args.resumido)
    if args.comando == "especificacao":
        print(F.especificacao_glc(), F.especificacao_ap(), F.especificacao_all(), sep="\n\n")
        return 0
    if args.comando == "interativo":
        return cmd_interativo()
    if args.comando == "gui":
        from .gui import iniciar
        iniciar()
        return 0
    if args.comando == "web":
        from .servidor_web import iniciar as iniciar_web
        iniciar_web(args.porta, abrir_navegador=not args.sem_navegador)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
