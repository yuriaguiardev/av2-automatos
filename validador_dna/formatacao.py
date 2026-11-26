"""Formatacao textual de rastreamentos, especificacoes e derivacoes."""

from __future__ import annotations

from . import automato_linear as ALL
from . import automato_pilha as AP
from . import gramatica as GLC
from .alfabetos import SIGMA_ALL, SIGMA_AP


def tabela(cabecalho: list[str], linhas: list[list[str]]) -> str:
    larguras = [len(c) for c in cabecalho]
    for linha in linhas:
        for i, celula in enumerate(linha):
            larguras[i] = max(larguras[i], len(celula))

    def fmt(linha: list[str]) -> str:
        return " | ".join(c.ljust(larguras[i]) for i, c in enumerate(linha)).rstrip()

    sep = "-+-".join("-" * w for w in larguras)
    return "\n".join([fmt(cabecalho), sep] + [fmt(l) for l in linhas])


def rastro_ap(res: AP.ResultadoAP) -> str:
    linhas = []
    for p in res.passos:
        leitura = (p.lida + "|" + p.restante) if res.cadeia else "|"
        linhas.append([str(p.passo), p.estado, str(p.posicao), leitura, p.pilha, p.transicao])
    corpo = tabela(["Passo", "Estado", "Pos", "Leitura (lido|restante)", "Pilha (topo→base)", "Transição aplicada"], linhas)
    return (f"Rastreamento do AP para '{res.cadeia}' (n = {len(res.cadeia)})\n{corpo}\n"
            f"Decisão do AP: {res.decisao} — {res.motivo}")


def rastro_all(res: ALL.ResultadoALL, resumido: bool = False) -> str:
    passos = res.passos
    ocultos = 0
    if resumido:
        filtrados = [passos[0]]
        for anterior, atual in zip(passos, passos[1:]):
            if atual.estado != anterior.estado or atual.fita != anterior.fita or atual is passos[-1]:
                filtrados.append(atual)
        ocultos = len(passos) - len(filtrados)
        passos = filtrados
    linhas = [[str(p.passo), p.estado, str(p.cabecote), p.fita_com_cabecote(), p.transicao] for p in passos]
    corpo = tabela(["Passo", "Estado", "Cab", "Fita ([ ] = cabeçote)", "Transição aplicada"], linhas)
    nota = f"\n({ocultos} passos de simples deslocamento omitidos; use --completo para ver todos)" if ocultos else ""
    n = len(res.cadeia)
    return (f"Rastreamento do ALL para '{res.cadeia}' (n = {n}; fita com {n} células graváveis + 2 marcadores = {n + 2})\n"
            f"{corpo}{nota}\nTotal de passos: {len(res.passos) - 1}\n"
            f"Decisão do ALL: {res.decisao} — {res.motivo}")


def derivacao(cadeia: str) -> str:
    passos = GLC.derivacao_mais_a_esquerda(cadeia)
    linhas = []
    for i, p in enumerate(passos):
        linhas.append([str(i), "" if p.producao is None else f"{p.producao.id}: {p.producao}", p.forma])
    return f"Derivação mais à esquerda de '{cadeia}' na GLC\n" + tabela(["#", "Produção", "Forma sentencial"], linhas)


def especificacao_ap() -> str:
    partes = [
        "AUTÔMATO DE PILHA  M = (Q, Σ, Γ, δ, q0, Z, F)",
        f"Q  = {{{', '.join(AP.ESTADOS)}}}   ({len(AP.ESTADOS)} estados)",
        f"Σ  = {{{', '.join(SIGMA_AP)}}}",
        f"Γ  = {{{', '.join(AP.ALFABETO_PILHA)}}}",
        f"q0 = {AP.ESTADO_INICIAL};  Z = símbolo inicial da pilha;  F = {{{', '.join(sorted(AP.ESTADOS_FINAIS))}}}",
        "Aceitação por ESTADO FINAL, com a entrada consumida por inteiro. Determinístico, sem transições ε.",
        "",
        "Estados:",
        tabela(["Estado", "Significado"], [[q, d] for q, d in AP.ESTADOS.items()]),
        "",
        "Transições (X, Y ∈ {A,C,G,T}; x ∈ {a,c,g,t}; X' = complemento de X):",
        tabela(["Regra", "δ", "Efeito"], [[r["id"], r["delta"], r["descricao"]] for r in AP.REGRAS]),
        f"Total de transições concretas: {len(AP.TRANSICOES)}. Combinações ausentes ⇒ rejeição.",
    ]
    return "\n".join(partes)


def especificacao_all() -> str:
    partes = [
        "AUTÔMATO LINEARMENTE LIMITADO  M = (Q, Σ, Γ, δ, q0, <, >, qac, qrj)",
        f"Q  = {{{', '.join(ALL.ESTADOS)}}}   ({len(ALL.ESTADOS)} estados)",
        f"Σ  = {{{', '.join(SIGMA_ALL)}}}",
        f"Γ  = {{{', '.join(ALL.ALFABETO_FITA)}}}",
        "Fita: < w1 ... wn >  (n células graváveis + 2 marcadores fixos); cabeçote inicia sobre '<' em q0.",
        "Movimentos: E = esquerda, D = direita, P = parado (apenas ao parar).",
        "",
        "Estados:",
        tabela(["Estado", "Significado"], [[q, d] for q, d in ALL.ESTADOS.items()]),
        "",
        "Transições (todas com símbolos reais de Γ; qA, qC, qG, qT = estados que carregam a base):",
        tabela(["Regra", "δ", "Efeito"], [[r["id"] if i == 0 else "", t, r["descricao"] if i == 0 else ""]
                                          for r in ALL.REGRAS for i, t in enumerate(r["transicoes"])]),
        f"Total de transições concretas: {len(ALL.TRANSICOES)}. Combinações ausentes ⇒ rejeição.",
    ]
    return "\n".join(partes)


def especificacao_glc() -> str:
    return "\n".join([
        "GRAMÁTICA LIVRE DE CONTEXTO  G = (V, T, P, S)",
        f"V = {{{', '.join(GLC.NAO_TERMINAIS)}}}",
        f"T = {{{', '.join(GLC.TERMINAIS)}}}",
        "S = símbolo inicial",
        "P:",
        *("  " + l for l in GLC.producoes_agrupadas()),
        f"({len(GLC.PRODUCOES)} produções)",
    ])
