"""Testes do modulo 2: Automato Linearmente Limitado (repeticao em tandem uu)."""

import itertools
import random

import pytest
from conftest import carregar

from validador_dna.alfabetos import BASES, SIGMA_ALL, SimboloForaDoAlfabeto
from validador_dna.automato_linear import (
    ESTADOS,
    MARCA_DIR,
    MARCA_ESQ,
    TRANSICOES,
    AutomatoLinearmenteLimitado,
    reconhecer,
)

CASOS = carregar("casos_all.json")


def oraculo(s: str) -> bool:
    """Definicao direta de L_ALL = { uu : u nao vazia }."""
    h = len(s) // 2
    return len(s) > 0 and len(s) % 2 == 0 and s[:h] == s[h:]


@pytest.mark.parametrize("caso", CASOS, ids=[c["id"] for c in CASOS])
def test_decisao_do_all(caso):
    res = reconhecer(caso["entrada"])
    assert res.decisao == caso["esperado"], f"{caso['id']}: {caso['regra']} | motivo: {res.motivo}"


def test_requisitos_dos_casos():
    aceitas = [c for c in CASOS if c["esperado"] == "ACEITA"]
    rejeitadas = [c for c in CASOS if c["esperado"] == "REJEITA"]
    assert len(aceitas) >= 8 and len(rejeitadas) >= 8
    entradas = [c["entrada"] for c in CASOS]
    assert len(entradas) == len(set(entradas))
    assert all(set(e) <= set(SIGMA_ALL) for e in entradas)
    assert any("Caso-limite" in c["regra"] for c in CASOS)
    principais = [c for c in CASOS if "Caso-limite" not in c["regra"]]
    assert sum(len(c["entrada"]) >= 18 for c in principais) >= 16


def test_pelo_menos_oito_estados():
    assert len(ESTADOS) >= 8


@pytest.mark.parametrize("caso", CASOS, ids=[c["id"] for c in CASOS])
def test_fita_limitada_e_marcadores_fixos(caso):
    """n celulas gravaveis + 2 marcadores; cabecote sempre dentro de [0, n+1]."""
    res = reconhecer(caso["entrada"])
    n = len(caso["entrada"])
    for p in res.passos:
        assert len(p.fita) == n + 2
        assert p.fita[0] == MARCA_ESQ and p.fita[-1] == MARCA_DIR
        assert MARCA_ESQ not in p.fita[1:-1] and MARCA_DIR not in p.fita[1:-1]
        assert 0 <= p.cabecote <= n + 1


def test_transicoes_respeitam_os_marcadores():
    for (q, lido), t in TRANSICOES.items():
        if lido == MARCA_ESQ:
            assert t.escrito == MARCA_ESQ and t.movimento != "E"
        if lido == MARCA_DIR:
            assert t.escrito == MARCA_DIR and t.movimento != "D"


def test_numero_de_passos_quadratico_nas_aceitas():
    """Prova de parada empirica: aceitacao em exatamente (5n^2 + 18n + 16)/4 passos."""
    for k in range(1, 13):
        s = ("ACGT" * 4)[:k] * 2
        n = len(s)
        res = reconhecer(s)
        assert res.aceita
        assert len(res.passos) - 1 == (5 * n * n + 18 * n + 16) // 4


def test_exaustivo_ate_comprimento_6():
    """Todas as 5461 cadeias sobre {A,C,G,T} com |s| <= 6 concordam com a definicao."""
    alla = AutomatoLinearmenteLimitado()
    for n in range(0, 7):
        for t in itertools.product(BASES, repeat=n):
            s = "".join(t)
            assert alla.executar(s).aceita == oraculo(s), s


def test_aleatorio_cadeias_longas():
    rng = random.Random(2026)
    alla = AutomatoLinearmenteLimitado()
    for _ in range(300):
        u = "".join(rng.choice(BASES) for _ in range(rng.randint(1, 15)))
        s = u + u
        if rng.random() < 0.5:  # mutacao em uma posicao ou em comprimento
            i = rng.randrange(len(s))
            s = s[:i] + rng.choice(BASES) + s[i + rng.choice((0, 1)):]
        assert alla.executar(s).aceita == oraculo(s), s


@pytest.mark.parametrize("entrada", ["CAGCAGCAGcagCAGCAG", "ATG#ATG", "ATGXATGX"])
def test_simbolo_fora_do_alfabeto(entrada):
    with pytest.raises(SimboloForaDoAlfabeto) as erro:
        reconhecer(entrada)
    assert "ALL" in str(erro.value)
