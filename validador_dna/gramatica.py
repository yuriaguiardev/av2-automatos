"""Gramatica Livre de Contexto (GLC) da linguagem do AP e derivacao mais a esquerda.

G = (V, T, P, S)
  V = {S, H, I, J, K, L, N, R, B}            (nao terminais)
  T = {A, C, G, T, a, c, g, t, #}            (terminais)
  S = simbolo inicial

  S -> H # R
  H -> A H T | C H G | G H C | T H A          (pares extras da haste, >= 0 vezes)
     | A I T | C I G | G I C | T I A          (faltam 3 pares)
  I -> A J T | C J G | G J C | T J A          (faltam 2 pares)
  J -> A K T | C K G | G K C | T K A          (falta 1 par)
  K -> A L T | C L G | G L C | T L A          (par mais interno, encosta na alca)
  L -> N L | N N N                            (alca com >= 3 bases)
  N -> a | c | g | t
  R -> B B R | B B B B B B                    (regiao de repeticao: par, >= 6)
  B -> A | C | G | T
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

from .alfabetos import BASES, BASES_ALCA, COMPLEMENTO, SEPARADOR, complemento_reverso

NAO_TERMINAIS: tuple[str, ...] = ("S", "H", "I", "J", "K", "L", "N", "R", "B")
TERMINAIS: tuple[str, ...] = BASES + BASES_ALCA + (SEPARADOR,)
SIMBOLO_INICIAL = "S"

PARES: tuple[tuple[str, str], ...] = tuple((X, COMPLEMENTO[X]) for X in BASES)


@dataclass(frozen=True)
class Producao:
    id: str
    esquerda: str
    direita: str  # cada caractere e um simbolo (todos os simbolos tem 1 caractere)

    def __str__(self) -> str:
        return f"{self.esquerda} → {' '.join(self.direita)}"


def _montar_producoes() -> list[Producao]:
    regras: list[tuple[str, str]] = [("S", "H#R")]
    for X, Xc in PARES:
        regras.append(("H", X + "H" + Xc))
    for X, Xc in PARES:
        regras.append(("H", X + "I" + Xc))
    for esq, interno in (("I", "J"), ("J", "K"), ("K", "L")):
        for X, Xc in PARES:
            regras.append((esq, X + interno + Xc))
    regras += [("L", "NL"), ("L", "NNN")]
    regras += [("N", x) for x in BASES_ALCA]
    regras += [("R", "BBR"), ("R", "BBBBBB")]
    regras += [("B", X) for X in BASES]
    return [Producao(f"P{i}", e, d) for i, (e, d) in enumerate(regras, start=1)]


PRODUCOES: list[Producao] = _montar_producoes()
_POR_REGRA = {(p.esquerda, p.direita): p for p in PRODUCOES}


def producoes_agrupadas() -> list[str]:
    """Producoes no formato compacto 'A -> x | y | ...'."""
    linhas = []
    for nt in NAO_TERMINAIS:
        alternativas = [" ".join(p.direita) for p in PRODUCOES if p.esquerda == nt]
        linhas.append(f"{nt} → " + " | ".join(alternativas))
    return linhas


# ---------------------------------------------------------------------------
# Oraculo independente (usado so nos testes para conferir AP e GLC)
# ---------------------------------------------------------------------------
_PADRAO = re.compile(r"([ACGT]+)([acgt]+)([ACGT]+)#([ACGT]*)")


def decompor(cadeia: str) -> tuple[str, str, str, str] | None:
    """Separa a cadeia em (haste 5', alca, haste 3', regiao) ou None."""
    m = _PADRAO.fullmatch(cadeia)
    return None if m is None else (m.group(1), m.group(2), m.group(3), m.group(4))


def pertence(cadeia: str) -> bool:
    """Definicao direta de L(G), escrita sem pilha (oraculo de teste)."""
    partes = decompor(cadeia)
    if partes is None:
        return False
    w, x, w3, y = partes
    return len(w) >= 4 and w3 == complemento_reverso(w) and len(x) >= 3 and len(y) >= 6 and len(y) % 2 == 0


# ---------------------------------------------------------------------------
# Arvore de derivacao e derivacao mais a esquerda
# ---------------------------------------------------------------------------
@dataclass
class No:
    simbolo: str
    filhos: list["No"]


def _folha(s: str) -> No:
    return No(s, [])


def _arvore_haste(w: str, alca: str, nivel: str) -> No:
    X, Xc = w[0], COMPLEMENTO[w[0]]
    if nivel == "K":
        interno = _arvore_alca(alca)
    else:
        proximo = {"H": "H" if len(w) > 4 else "I", "I": "J", "J": "K"}[nivel]
        interno = _arvore_haste(w[1:], alca, proximo)
    return No(nivel, [_folha(X), interno, _folha(Xc)])


def _arvore_alca(x: str) -> No:
    if len(x) > 3:
        return No("L", [No("N", [_folha(x[0])]), _arvore_alca(x[1:])])
    return No("L", [No("N", [_folha(c)]) for c in x])


def _arvore_regiao(y: str) -> No:
    if len(y) > 6:
        return No("R", [No("B", [_folha(y[0])]), No("B", [_folha(y[1])]), _arvore_regiao(y[2:])])
    return No("R", [No("B", [_folha(c)]) for c in y])


def arvore_derivacao(cadeia: str) -> No:
    """Constroi a arvore de derivacao de G para uma cadeia de L(G)."""
    if not pertence(cadeia):
        raise ValueError(f"A cadeia {cadeia!r} não pertence a L(G); não há derivação.")
    w, x, _w3, y = decompor(cadeia)  # type: ignore[misc]
    return No("S", [_arvore_haste(w, x, "H"), _folha(SEPARADOR), _arvore_regiao(y)])


@dataclass
class PassoDerivacao:
    producao: Producao | None
    forma: str  # forma sentencial


def derivacao_mais_a_esquerda(cadeia: str) -> list[PassoDerivacao]:
    """Lista de formas sentenciais S =>* cadeia, expandindo sempre o NT mais a esquerda."""
    raiz = arvore_derivacao(cadeia)
    forma: list[No] = [raiz]
    passos = [PassoDerivacao(None, "S")]
    while True:
        indice = next((i for i, n in enumerate(forma) if n.filhos), None)
        if indice is None:
            break
        no = forma[indice]
        direita = "".join(f.simbolo for f in no.filhos)
        producao = _POR_REGRA[(no.simbolo, direita)]
        forma = forma[:indice] + no.filhos + forma[indice + 1:]
        passos.append(PassoDerivacao(producao, "".join(n.simbolo for n in forma)))
    assert passos[-1].forma == cadeia
    return passos


# ---------------------------------------------------------------------------
# Gerador aleatorio de cadeias de L(G) (aplicando producoes ao acaso)
# ---------------------------------------------------------------------------
def gerar(rng: random.Random, max_extras: int = 6) -> str:
    """Deriva uma cadeia aleatoria aplicando as producoes de G."""
    def expandir(simbolo: str) -> str:
        if simbolo in TERMINAIS:
            return simbolo
        opcoes = [p for p in PRODUCOES if p.esquerda == simbolo]
        if simbolo in ("H", "L", "R"):
            recursiva, base = [p for p in opcoes if simbolo in p.direita], [p for p in opcoes if simbolo not in p.direita]
            opcoes = recursiva if rng.random() < 1 - 1 / (max_extras / 2 + 1) else base
        p = rng.choice(opcoes)
        return "".join(expandir(s) for s in p.direita)

    return expandir(SIMBOLO_INICIAL)
