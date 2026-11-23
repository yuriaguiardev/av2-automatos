"""Automato de Pilha (AP) deterministico que reconhece a linguagem do grampo.

L_AP = { w . x . cr(w) # y  :  w in {A,C,G,T}^k, k >= 4,
                               x in {a,c,g,t}^m, m >= 3,
                               y in {A,C,G,T}^(2j), j >= 3 }

em que cr(w) e o complemento reverso de w (A<->T, C<->G, lido de tras para frente).

AP = (Q, Sigma, Gamma, delta, q0, Z, F)
  * aceitacao por ESTADO FINAL (F = {q15}) com a entrada consumida por inteiro;
  * deterministico e sem transicoes-epsilon: cada passo consome exatamente
    um simbolo da entrada, logo a execucao termina em no maximo n passos.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .alfabetos import (
    BASES,
    BASES_ALCA,
    COMPLEMENTO,
    SEPARADOR,
    SIGMA_AP,
    descrever_simbolo,
    verificar_alfabeto,
)

FUNDO = "Z"  # simbolo inicial da pilha (Z0)
EPSILON = "ε"

ESTADOS: dict[str, str] = {
    "q0": "início: aguardando a 1ª base da haste 5'",
    "q1": "haste 5' com 1 base empilhada",
    "q2": "haste 5' com 2 bases empilhadas",
    "q3": "haste 5' com 3 bases empilhadas",
    "q4": "haste 5' com ≥ 4 bases (continua empilhando)",
    "q5": "alça com 1 base não pareada",
    "q6": "alça com 2 bases não pareadas",
    "q7": "alça com ≥ 3 bases (pode iniciar a haste 3')",
    "q8": "haste 3': desempilha conferindo a complementaridade",
    "q9": "após '#': região de repetição com 0 bases",
    "q10": "região de repetição com 1 base",
    "q11": "região de repetição com 2 bases",
    "q12": "região de repetição com 3 bases",
    "q13": "região de repetição com 4 bases",
    "q14": "região de repetição com 5 bases",
    "q15": "região de repetição com comprimento par ≥ 6 (FINAL)",
    "q16": "região de repetição com comprimento ímpar ≥ 7",
}
ESTADO_INICIAL = "q0"
ESTADOS_FINAIS = frozenset({"q15"})
ALFABETO_PILHA: tuple[str, ...] = (FUNDO,) + BASES

# Regras esquematicas (X, Y em {A,C,G,T};  x em {a,c,g,t};  X' = complemento de X).
# Cada regra gera varias transicoes concretas em _gerar_transicoes().
REGRAS: list[dict[str, str]] = [
    {"id": "T1", "delta": "δ(q0, X, Z) = (q1, XZ)", "descricao": "empilha a 1ª base da haste 5'"},
    {"id": "T2", "delta": "δ(q1, X, Y) = (q2, XY)", "descricao": "empilha a 2ª base da haste 5'"},
    {"id": "T3", "delta": "δ(q2, X, Y) = (q3, XY)", "descricao": "empilha a 3ª base da haste 5'"},
    {"id": "T4", "delta": "δ(q3, X, Y) = (q4, XY)", "descricao": "empilha a 4ª base da haste 5'"},
    {"id": "T5", "delta": "δ(q4, X, Y) = (q4, XY)", "descricao": "empilha bases adicionais da haste 5'"},
    {"id": "T6", "delta": "δ(q4, x, Y) = (q5, Y)", "descricao": "1ª base da alça (pilha inalterada)"},
    {"id": "T7", "delta": "δ(q5, x, Y) = (q6, Y)", "descricao": "2ª base da alça"},
    {"id": "T8", "delta": "δ(q6, x, Y) = (q7, Y)", "descricao": "3ª base da alça"},
    {"id": "T9", "delta": "δ(q7, x, Y) = (q7, Y)", "descricao": "bases adicionais da alça"},
    {"id": "T10", "delta": "δ(q7, X, X') = (q8, ε)", "descricao": "1ª base da haste 3' pareia com o topo e desempilha"},
    {"id": "T11", "delta": "δ(q8, X, X') = (q8, ε)", "descricao": "demais bases da haste 3' pareiam e desempilham"},
    {"id": "T12", "delta": "δ(q8, #, Z) = (q9, Z)", "descricao": "pilha só com Z: hastes do mesmo tamanho; lê '#'"},
    {"id": "T13", "delta": "δ(q9, X, Z) = (q10, Z)", "descricao": "1ª base da região de repetição"},
    {"id": "T14", "delta": "δ(q10, X, Z) = (q11, Z)", "descricao": "2ª base da região de repetição"},
    {"id": "T15", "delta": "δ(q11, X, Z) = (q12, Z)", "descricao": "3ª base da região de repetição"},
    {"id": "T16", "delta": "δ(q12, X, Z) = (q13, Z)", "descricao": "4ª base da região de repetição"},
    {"id": "T17", "delta": "δ(q13, X, Z) = (q14, Z)", "descricao": "5ª base da região de repetição"},
    {"id": "T18", "delta": "δ(q14, X, Z) = (q15, Z)", "descricao": "6ª base: comprimento par ≥ 6"},
    {"id": "T19", "delta": "δ(q15, X, Z) = (q16, Z)", "descricao": "comprimento passa a ser ímpar"},
    {"id": "T20", "delta": "δ(q16, X, Z) = (q15, Z)", "descricao": "comprimento volta a ser par"},
]


@dataclass(frozen=True)
class TransicaoAP:
    """Transicao concreta delta(origem, simbolo, topo) = (destino, empilha).

    `empilha` e a cadeia que substitui o topo; o 1º caractere vira o novo topo.
    Cadeia vazia significa desempilhar (epsilon).
    """

    regra: str
    origem: str
    simbolo: str
    topo: str
    destino: str
    empilha: str

    def __str__(self) -> str:
        return (
            f"{self.regra}: δ({self.origem}, {self.simbolo}, {self.topo}) = "
            f"({self.destino}, {self.empilha or EPSILON})"
        )


def _gerar_transicoes() -> dict[tuple[str, str, str], TransicaoAP]:
    delta: dict[tuple[str, str, str], TransicaoAP] = {}

    def adicionar(regra: str, q: str, a: str, z: str, p: str, gama: str) -> None:
        chave = (q, a, z)
        if chave in delta:  # garante o determinismo por construcao
            raise AssertionError(f"AP não determinístico em {chave}")
        delta[chave] = TransicaoAP(regra, q, a, z, p, gama)

    for X in BASES:
        adicionar("T1", "q0", X, FUNDO, "q1", X + FUNDO)
    for regra, q, p in (("T2", "q1", "q2"), ("T3", "q2", "q3"), ("T4", "q3", "q4"), ("T5", "q4", "q4")):
        for X in BASES:
            for Y in BASES:
                adicionar(regra, q, X, Y, p, X + Y)
    for regra, q, p in (("T6", "q4", "q5"), ("T7", "q5", "q6"), ("T8", "q6", "q7"), ("T9", "q7", "q7")):
        for x in BASES_ALCA:
            for Y in BASES:
                adicionar(regra, q, x, Y, p, Y)
    for X in BASES:
        adicionar("T10", "q7", X, COMPLEMENTO[X], "q8", "")
        adicionar("T11", "q8", X, COMPLEMENTO[X], "q8", "")
    adicionar("T12", "q8", SEPARADOR, FUNDO, "q9", FUNDO)
    cadeia_contagem = [
        ("T13", "q9", "q10"), ("T14", "q10", "q11"), ("T15", "q11", "q12"),
        ("T16", "q12", "q13"), ("T17", "q13", "q14"), ("T18", "q14", "q15"),
        ("T19", "q15", "q16"), ("T20", "q16", "q15"),
    ]
    for regra, q, p in cadeia_contagem:
        for X in BASES:
            adicionar(regra, q, X, FUNDO, p, FUNDO)
    return delta


TRANSICOES: dict[tuple[str, str, str], TransicaoAP] = _gerar_transicoes()


@dataclass
class PassoAP:
    """Configuracao instantanea registrada no rastreamento."""

    passo: int
    estado: str
    posicao: int  # indice (1-based) do proximo simbolo a ser lido; n+1 = entrada consumida
    lida: str
    restante: str
    pilha: str  # topo a esquerda
    transicao: str


@dataclass
class ResultadoAP:
    cadeia: str
    aceita: bool
    motivo: str
    passos: list[PassoAP] = field(default_factory=list)

    @property
    def estado_final(self) -> str:
        return self.passos[-1].estado

    @property
    def pilha_final(self) -> str:
        return self.passos[-1].pilha

    @property
    def decisao(self) -> str:
        return "ACEITA" if self.aceita else "REJEITA"


def _motivo_bloqueio(q: str, a: str, topo: str, posicao: int, pilha: list[str]) -> str:
    """Explica por que nao existe transicao para (q, a, topo)."""
    simb = f"{descrever_simbolo(a)} na posição {posicao}"
    indice = int(q[1:])
    if indice <= 3:
        return (f"Haste 5' incompleta: após {indice} base(s) foi lido {simb}; "
                f"a haste 5' exige ao menos 4 bases maiúsculas antes da alça.")
    if q == "q4":
        return (f"Separador {simb} lido ainda na haste 5': falta a alça "
                f"(≥ 3 bases minúsculas) e a haste 3'.")
    if q in ("q5", "q6"):
        return (f"Alça curta: após {indice - 4} base(s) não pareada(s) foi lido {simb}; "
                f"a alça exige ao menos 3 bases minúsculas.")
    if q in ("q7", "q8"):
        if a in BASES:
            if topo == FUNDO:
                return (f"Haste 3' mais longa que a haste 5': a base {simb} encontrou "
                        f"apenas Z no topo da pilha (nenhuma base para parear).")
            return (f"Pareamento inválido: a base {simb} não é complementar ao topo da pilha "
                    f"'{topo}' (esperado '{COMPLEMENTO[topo]}').")
        if a == SEPARADOR:
            if q == "q7":
                return f"Haste 3' ausente: separador {simb} lido logo após a alça."
            sem_par = len(pilha) - 1
            return (f"Haste 3' mais curta que a haste 5': separador {simb} lido com "
                    f"{sem_par} base(s) ainda na pilha (topo '{topo}').")
        return f"Base minúscula {simb} dentro da haste 3' (a alça já havia terminado)."
    # q9..q16: regiao de repeticao
    if a == SEPARADOR:
        return f"Separador {simb} repetido: só pode haver um '#'."
    return (f"Base minúscula {simb} na região de repetição: "
            f"após '#' só são admitidas bases maiúsculas.")


def _motivo_fim(q: str, pilha: list[str], comprimento_regiao: int, vazia: bool) -> str:
    """Explica a decisao quando a entrada foi consumida por inteiro."""
    if q in ESTADOS_FINAIS:
        return ("Entrada consumida por completo no estado final q15: hastes complementares "
                "de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6.")
    if vazia:
        return "Entrada vazia: o construto exige grampo, '#' e região de repetição."
    indice = int(q[1:])
    if indice <= 4:
        return "Entrada terminou na haste 5' (faltam alça, haste 3', '#' e região de repetição)."
    if indice <= 7:
        return "Entrada terminou na alça (faltam haste 3', '#' e região de repetição)."
    if q == "q8":
        if pilha[-1] != FUNDO:
            return (f"Entrada terminou na haste 3' com {len(pilha) - 1} base(s) sem par na pilha "
                    f"(falta também '#' e a região de repetição).")
        return "Entrada terminou após o grampo: falta o separador '#' e a região de repetição."
    if q == "q16":
        return (f"Região de repetição com comprimento ímpar ({comprimento_regiao}): "
                f"o AP exige comprimento par ≥ 6.")
    return f"Região de repetição com {comprimento_regiao} base(s): o mínimo é 6."


class AutomatoPilha:
    """Simulador do AP: executa as transicoes de TRANSICOES sobre a pilha."""

    estados = ESTADOS
    alfabeto_entrada = SIGMA_AP
    alfabeto_pilha = ALFABETO_PILHA
    estado_inicial = ESTADO_INICIAL
    simbolo_inicial_pilha = FUNDO
    estados_finais = ESTADOS_FINAIS

    def __init__(self) -> None:
        self.delta = TRANSICOES

    def executar(self, cadeia: str) -> ResultadoAP:
        verificar_alfabeto(cadeia, SIGMA_AP, "AP")
        estado = ESTADO_INICIAL
        pilha: list[str] = [FUNDO]  # topo no fim da lista
        passos = [PassoAP(0, estado, 1, "", cadeia, FUNDO, "configuração inicial")]
        pos_separador = None

        for i, simbolo in enumerate(cadeia):
            topo = pilha[-1]
            t = self.delta.get((estado, simbolo, topo))
            if t is None:
                motivo = "Sem transição: " + _motivo_bloqueio(estado, simbolo, topo, i + 1, pilha)
                return ResultadoAP(cadeia, False, motivo, passos)
            pilha.pop()
            pilha.extend(reversed(t.empilha))
            estado = t.destino
            if simbolo == SEPARADOR:
                pos_separador = i
            passos.append(PassoAP(
                passo=i + 1,
                estado=estado,
                posicao=i + 2,
                lida=cadeia[: i + 1],
                restante=cadeia[i + 1:],
                pilha="".join(reversed(pilha)),
                transicao=str(t),
            ))

        regiao = 0 if pos_separador is None else len(cadeia) - pos_separador - 1
        aceita = estado in ESTADOS_FINAIS
        return ResultadoAP(cadeia, aceita, _motivo_fim(estado, pilha, regiao, cadeia == ""), passos)


def reconhecer(cadeia: str) -> ResultadoAP:
    """Atalho: executa o AP sobre a cadeia."""
    return AutomatoPilha().executar(cadeia)
