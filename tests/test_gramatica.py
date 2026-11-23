"""Testes que relacionam a GLC ao AP: L(G) = L(AP) (evidencia empirica da prova)."""

import random

import pytest
from conftest import carregar

from validador_dna import gramatica as G
from validador_dna.alfabetos import SIGMA_AP
from validador_dna.automato_pilha import reconhecer

CASOS = carregar("casos_ap.json")


def test_estrutura_da_gramatica():
    assert set(G.NAO_TERMINAIS).isdisjoint(G.TERMINAIS)
    assert G.SIMBOLO_INICIAL in G.NAO_TERMINAIS
    assert len(G.PRODUCOES) == 33
    for p in G.PRODUCOES:
        assert p.esquerda in G.NAO_TERMINAIS
        assert all(s in G.NAO_TERMINAIS or s in G.TERMINAIS for s in p.direita)


@pytest.mark.parametrize("caso", [c for c in CASOS if c["esperado"] == "ACEITA"], ids=lambda c: c["id"])
def test_derivacao_das_cadeias_aceitas(caso):
    passos = G.derivacao_mais_a_esquerda(caso["entrada"])
    assert passos[0].forma == "S" and passos[-1].forma == caso["entrada"]
    # cada passo aplica uma producao de P ao nao terminal mais a esquerda
    for anterior, atual in zip(passos, passos[1:]):
        i = next(k for k, s in enumerate(anterior.forma) if s in G.NAO_TERMINAIS)
        assert anterior.forma[i] == atual.producao.esquerda
        assert atual.forma == anterior.forma[:i] + atual.producao.direita + anterior.forma[i + 1:]


@pytest.mark.parametrize("caso", [c for c in CASOS if c["esperado"] == "REJEITA"], ids=lambda c: c["id"])
def test_rejeitadas_nao_tem_derivacao(caso):
    with pytest.raises(ValueError):
        G.derivacao_mais_a_esquerda(caso["entrada"])


def test_toda_cadeia_gerada_pela_glc_e_aceita_pelo_ap():
    rng = random.Random(7)
    for _ in range(1000):
        s = G.gerar(rng)
        assert G.pertence(s)
        assert reconhecer(s).aceita, s


def _mutar(s: str, rng: random.Random) -> str:
    i = rng.randrange(len(s) + 1)
    op = rng.choice(("troca", "insere", "remove"))
    c = rng.choice(SIGMA_AP)
    if op == "troca" and i < len(s):
        return s[:i] + c + s[i + 1:]
    if op == "insere":
        return s[:i] + c + s[i:]
    return s[:i] + s[i + 1:]


def test_ap_concorda_com_a_definicao_em_cadeias_aleatorias():
    rng = random.Random(42)
    aceitas = rejeitadas = 0
    for _ in range(3000):
        s = G.gerar(rng)
        for _ in range(rng.randint(0, 2)):
            s = _mutar(s, rng)
        res = reconhecer(s)
        assert res.aceita == G.pertence(s), s
        aceitas += res.aceita
        rejeitadas += not res.aceita
    assert aceitas > 300 and rejeitadas > 300
