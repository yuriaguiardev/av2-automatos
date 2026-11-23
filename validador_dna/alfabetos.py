"""Alfabetos, complementaridade de bases e validacao de simbolos de entrada."""

from __future__ import annotations

# Bases pareadas (haste do grampo e regiao de repeticao) - maiusculas.
BASES: tuple[str, ...] = ("A", "C", "G", "T")
# Bases nao pareadas da alca do grampo - minusculas (convencao do projeto).
BASES_ALCA: tuple[str, ...] = ("a", "c", "g", "t")
# Separador entre o grampo e a regiao de repeticao.
SEPARADOR = "#"

# Alfabeto de entrada de cada modulo.
SIGMA_AP: tuple[str, ...] = BASES + BASES_ALCA + (SEPARADOR,)
SIGMA_ALL: tuple[str, ...] = BASES

# Pareamento de Watson-Crick.
COMPLEMENTO: dict[str, str] = {"A": "T", "T": "A", "C": "G", "G": "C"}


def complemento_reverso(sequencia: str) -> str:
    """Retorna o complemento reverso de uma sequencia de bases maiusculas."""
    return "".join(COMPLEMENTO[b] for b in reversed(sequencia))


def descrever_simbolo(simbolo: str) -> str:
    """Representacao legivel de um simbolo (inclui espacos e invisiveis)."""
    if simbolo == " ":
        return "' ' (espaço)"
    if not simbolo.isprintable():
        return f"{simbolo!r} (caractere invisível)"
    return f"'{simbolo}'"


class SimboloForaDoAlfabeto(ValueError):
    """Erro lancado quando a cadeia contem simbolo fora do alfabeto de entrada."""

    def __init__(self, simbolo: str, posicao: int, alfabeto: tuple[str, ...], modulo: str):
        self.simbolo = simbolo
        self.posicao = posicao
        self.alfabeto = alfabeto
        self.modulo = modulo
        lista = ", ".join(alfabeto)
        mensagem = (
            f"ERRO: o símbolo {descrever_simbolo(simbolo)} na posição {posicao} não pertence "
            f"ao alfabeto de entrada do {modulo} Σ = {{{lista}}}. "
            f"A cadeia não foi submetida ao autômato."
        )
        super().__init__(mensagem)


def verificar_alfabeto(cadeia: str, alfabeto: tuple[str, ...], modulo: str) -> None:
    """Lanca SimboloForaDoAlfabeto no primeiro simbolo invalido (posicao 1-based)."""
    permitidos = set(alfabeto)
    for posicao, simbolo in enumerate(cadeia, start=1):
        if simbolo not in permitidos:
            raise SimboloForaDoAlfabeto(simbolo, posicao, alfabeto, modulo)
