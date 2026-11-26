"""Automato Linearmente Limitado (ALL) deterministico para a repeticao em tandem.

L_ALL = { u u : u in {A,C,G,T}^+ }   (linguagem "copia", nao livre de contexto)

ALL = (Q, Sigma, Gamma, delta, q0, <, >, qac, qrj)
  * fita: '<' + n celulas gravaveis (a propria entrada) + '>'  -> n + 2 celulas;
  * os marcadores '<' e '>' sao fixos: podem ser lidos, nunca sobrescritos,
    e o cabecote nunca os ultrapassa (verificado por construcao e em execucao);
  * movimentos: E (esquerda), D (direita), P (parado - usado so ao parar).

Algoritmo (3 fases):
  Fase 1 - acha o meio: marca, alternadamente, a base nao marcada mais a esquerda
           e a mais a direita (maiuscula -> minuscula). Se sobrar uma unica base
           sem par, o comprimento e impar e a entrada e rejeitada.
  Fase 2 - restaura a 2a metade (minuscula -> maiuscula). A fita fica u' . U,
           com a 1a copia em minusculas e a 2a em maiusculas.
  Fase 3 - compara: pega a 1a minuscula, grava '*' e "carrega" a base no estado
           (qA, qC, qG, qT); vai ate a 1a maiuscula da 2a copia; se for igual
           grava '*' e volta; se for diferente rejeita. Se so restarem '*',
           aceita.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .alfabetos import BASES, SIGMA_ALL, descrever_simbolo, verificar_alfabeto

MARCA_ESQ = "<"
MARCA_DIR = ">"
CONFERIDA = "*"
MINUSCULAS: tuple[str, ...] = tuple(b.lower() for b in BASES)
ALFABETO_FITA: tuple[str, ...] = BASES + MINUSCULAS + (CONFERIDA, MARCA_ESQ, MARCA_DIR)

ESQUERDA, DIREITA, PARADO = "E", "D", "P"
DESLOCAMENTO = {ESQUERDA: -1, DIREITA: +1, PARADO: 0}

ESTADO_INICIAL = "q0"
ESTADO_ACEITA = "qac"
ESTADO_REJEITA = "qrj"

ESTADOS: dict[str, str] = {
    "q0": "início: cabeçote sobre o marcador '<'",
    "q1": "Fase 1: procura a base não marcada mais à esquerda",
    "q2": "Fase 1: avança até o fim da região não marcada",
    "q3": "Fase 1: marca a base não marcada mais à direita",
    "q4": "Fase 1: volta até a última marca da esquerda",
    "q5": "Fase 2: meio encontrado; restaura a 2ª metade (minúscula → maiúscula)",
    "q6": "retorna ao marcador '<'",
    "q7": "Fase 3: escolhe a próxima base da 1ª cópia",
    "qA": "Fase 3: carrega 'A' até a 2ª cópia",
    "qC": "Fase 3: carrega 'C' até a 2ª cópia",
    "qG": "Fase 3: carrega 'G' até a 2ª cópia",
    "qT": "Fase 3: carrega 'T' até a 2ª cópia",
    ESTADO_ACEITA: "aceitação (parada)",
    ESTADO_REJEITA: "rejeição (parada)",
}

# Descricao de cada regra. As transicoes concretas de cada regra (so com simbolos reais de Γ,
# sem metavariaveis) sao obtidas da tabela TRANSICOES, abaixo, em REGRAS.
# Formato: (regra, estado de origem ou None, estado de destino ou None, descricao)
_DESCRICOES: list[tuple[str, str | None, str | None, str]] = [
    ("M1", None, None, "sai do marcador esquerdo"),
    ("M2", None, None, "marca o extremo esquerdo (maiúscula → minúscula)"),
    ("M3", None, None, "não há base livre: meio encontrado; restaura a 1ª célula da 2ª metade"),
    ("M4", None, None, "entrada vazia: REJEITA"),
    ("M5", None, None, "atravessa bases não marcadas"),
    ("M6", None, None, "achou a marca da direita: recua"),
    ("M7", None, None, "achou o marcador direito: recua"),
    ("M8", None, None, "marca o extremo direito (maiúscula → minúscula)"),
    ("M9", None, None, "base sem par: comprimento ímpar, REJEITA"),
    ("M10", None, None, "volta sobre bases não marcadas"),
    ("M11", None, None, "achou a última marca da esquerda"),
    ("M12", None, None, "restaura a 2ª metade (minúscula → maiúscula)"),
    ("M13", None, None, "2ª metade restaurada"),
    ("M14", None, None, "retorna à esquerda"),
    ("M15", None, None, "chegou ao marcador esquerdo"),
    ("M16", None, None, "pula bases já conferidas"),
    *(("M17", None, "q" + X, f"pega '{X.lower()}' da 1ª cópia, grava '*' e carrega {X} no estado q{X}") for X in BASES),
    ("M18", None, None, "tudo conferido: ACEITA"),
    *(("M19", "q" + X, None, f"q{X} atravessa o resto da 1ª cópia e as conferidas da 2ª") for X in BASES),
    *(("M20", "q" + X, None, f"q{X} encontra {X} na 2ª cópia: confere e volta") for X in BASES),
    *(("M21", "q" + X, None, f"q{X} encontra outra base: REJEITA") for X in BASES),
]


@dataclass(frozen=True)
class TransicaoALL:
    regra: str
    origem: str
    lido: str
    destino: str
    escrito: str
    movimento: str

    def __str__(self) -> str:
        return f"{self.regra}: δ({self.origem}, {self.lido}) = ({self.destino}, {self.escrito}, {self.movimento})"


def _gerar_transicoes() -> dict[tuple[str, str], TransicaoALL]:
    delta: dict[tuple[str, str], TransicaoALL] = {}

    def adicionar(regra: str, q: str, lido: str, p: str, escrito: str, mov: str) -> None:
        chave = (q, lido)
        if chave in delta:
            raise AssertionError(f"ALL não determinístico em {chave}")
        # Marcadores de borda sao fixos e nunca podem ser ultrapassados.
        if lido == MARCA_ESQ and (escrito != MARCA_ESQ or mov == ESQUERDA):
            raise AssertionError(f"Transição {chave} viola o marcador esquerdo")
        if lido == MARCA_DIR and (escrito != MARCA_DIR or mov == DIREITA):
            raise AssertionError(f"Transição {chave} viola o marcador direito")
        delta[chave] = TransicaoALL(regra, q, lido, p, escrito, mov)

    adicionar("M1", "q0", MARCA_ESQ, "q1", MARCA_ESQ, DIREITA)
    for X in BASES:
        x = X.lower()
        adicionar("M2", "q1", X, "q2", x, DIREITA)
        adicionar("M3", "q1", x, "q5", X, DIREITA)
        adicionar("M5", "q2", X, "q2", X, DIREITA)
        adicionar("M6", "q2", x, "q3", x, ESQUERDA)
        adicionar("M8", "q3", X, "q4", x, ESQUERDA)
        adicionar("M9", "q3", x, ESTADO_REJEITA, x, PARADO)
        adicionar("M10", "q4", X, "q4", X, ESQUERDA)
        adicionar("M11", "q4", x, "q1", x, DIREITA)
        adicionar("M12", "q5", x, "q5", X, DIREITA)
    adicionar("M4", "q1", MARCA_DIR, ESTADO_REJEITA, MARCA_DIR, PARADO)
    adicionar("M7", "q2", MARCA_DIR, "q3", MARCA_DIR, ESQUERDA)
    adicionar("M13", "q5", MARCA_DIR, "q6", MARCA_DIR, ESQUERDA)
    for s in BASES + MINUSCULAS + (CONFERIDA,):
        adicionar("M14", "q6", s, "q6", s, ESQUERDA)
    adicionar("M15", "q6", MARCA_ESQ, "q7", MARCA_ESQ, DIREITA)
    adicionar("M16", "q7", CONFERIDA, "q7", CONFERIDA, DIREITA)
    for X in BASES:
        adicionar("M17", "q7", X.lower(), "q" + X, CONFERIDA, DIREITA)
    adicionar("M18", "q7", MARCA_DIR, ESTADO_ACEITA, MARCA_DIR, PARADO)
    for X in BASES:
        q_base = "q" + X  # qA, qC, qG ou qT
        for s in MINUSCULAS + (CONFERIDA,):
            adicionar("M19", q_base, s, q_base, s, DIREITA)
        for Y in BASES:
            if Y == X:
                adicionar("M20", q_base, Y, "q6", CONFERIDA, ESQUERDA)
            else:
                adicionar("M21", q_base, Y, ESTADO_REJEITA, Y, PARADO)
    return delta


TRANSICOES: dict[tuple[str, str], TransicaoALL] = _gerar_transicoes()


def _montar_regras() -> list[dict]:
    regras = []
    for regra, origem, destino, descricao in _DESCRICOES:
        ts = [t for t in TRANSICOES.values() if t.regra == regra
              and (origem is None or t.origem == origem) and (destino is None or t.destino == destino)]
        concretas = [f"δ({t.origem}, {t.lido}) = ({t.destino}, {t.escrito}, {t.movimento})" for t in ts]
        regras.append({"id": regra, "transicoes": concretas, "delta": "; ".join(concretas), "descricao": descricao})
    assert sum(len(r["transicoes"]) for r in regras) == len(TRANSICOES)  # cada transição em exatamente uma linha
    return regras


# Regras com as transições concretas (o que aparece nas tabelas, no relatório e nos diagramas).
REGRAS: list[dict] = _montar_regras()


class LimiteDaFitaViolado(RuntimeError):
    """Nunca deve ocorrer: indica tentativa de sair da fita limitada."""


@dataclass
class PassoALL:
    passo: int
    estado: str
    cabecote: int  # 0 = '<', 1..n = celulas gravaveis, n+1 = '>'
    fita: str
    transicao: str

    def fita_com_cabecote(self) -> str:
        """Fita com a celula sob o cabecote entre colchetes, ex.: <aC[G]T>."""
        return self.fita[: self.cabecote] + "[" + self.fita[self.cabecote] + "]" + self.fita[self.cabecote + 1:]


@dataclass
class ResultadoALL:
    cadeia: str
    aceita: bool
    motivo: str
    passos: list[PassoALL] = field(default_factory=list)

    @property
    def decisao(self) -> str:
        return "ACEITA" if self.aceita else "REJEITA"

    @property
    def estado_final(self) -> str:
        return self.passos[-1].estado

    @property
    def fita_final(self) -> str:
        return self.passos[-1].fita

    @property
    def celulas(self) -> int:
        """Total de celulas da fita (n gravaveis + 2 marcadores)."""
        return len(self.passos[0].fita)


class AutomatoLinearmenteLimitado:
    """Simulador do ALL: executa as transicoes de TRANSICOES sobre a fita limitada."""

    estados = ESTADOS
    alfabeto_entrada = SIGMA_ALL
    alfabeto_fita = ALFABETO_FITA
    estado_inicial = ESTADO_INICIAL

    def __init__(self) -> None:
        self.delta = TRANSICOES

    def executar(self, cadeia: str) -> ResultadoALL:
        verificar_alfabeto(cadeia, SIGMA_ALL, "ALL")
        n = len(cadeia)
        fita = [MARCA_ESQ] + list(cadeia) + [MARCA_DIR]  # n celulas gravaveis + 2 marcadores
        cabecote = 0
        estado = ESTADO_INICIAL
        passos = [PassoALL(0, estado, cabecote, "".join(fita), "configuração inicial")]
        vistas: set[tuple[str, int, str]] = set()
        motivo = ""

        while estado not in (ESTADO_ACEITA, ESTADO_REJEITA):
            config = (estado, cabecote, "".join(fita))
            if config in vistas:  # salvaguarda teorica: nunca ocorre (ver prova de parada)
                return ResultadoALL(cadeia, False, "Laço detectado: configuração repetida.", passos)
            vistas.add(config)

            lido = fita[cabecote]
            t = self.delta.get((estado, lido))
            if t is None:
                motivo = f"Sem transição definida para ({estado}, {descrever_simbolo(lido)})."
                estado = ESTADO_REJEITA
                break
            fita[cabecote] = t.escrito
            novo = cabecote + DESLOCAMENTO[t.movimento]
            if not 0 <= novo <= n + 1:
                raise LimiteDaFitaViolado(f"Cabeçote sairia da fita em {t}")
            cabecote_anterior, cabecote = cabecote, novo
            estado = t.destino
            passos.append(PassoALL(len(passos), estado, cabecote, "".join(fita), str(t)))

            if estado == ESTADO_REJEITA:
                motivo = self._motivo_rejeicao(t, cabecote_anterior, n)

        if estado == ESTADO_ACEITA:
            u = cadeia[: n // 2]
            motivo = (f"Todas as {n} células foram conferidas ('*'): as duas metades são idênticas "
                      f"(u = {u}, |u| = {n // 2}).")
        return ResultadoALL(cadeia, estado == ESTADO_ACEITA, motivo, passos)

    @staticmethod
    def _motivo_rejeicao(t: TransicaoALL, celula: int, n: int) -> str:
        if t.regra == "M4":
            return "Entrada vazia (regra M4): a cópia u precisa ser não vazia."
        if t.regra == "M9":
            return (f"Comprimento ímpar, n = {n} (regra M9): a base da célula {celula} ficou sem par, "
                    f"logo a fita não se divide em duas metades iguais.")
        if t.regra == "M21":
            carregada = t.origem[1]
            metade = n // 2
            return (f"Cópias diferentes (regra M21): a célula {celula} (posição {celula - metade} da 2ª cópia) "
                    f"contém '{t.lido}', mas a base correspondente da 1ª cópia (célula {celula - metade}) "
                    f"é '{carregada}'.")
        return f"Rejeitada pela regra {t.regra}."


def reconhecer(cadeia: str) -> ResultadoALL:
    """Atalho: executa o ALL sobre a cadeia."""
    return AutomatoLinearmenteLimitado().executar(cadeia)
