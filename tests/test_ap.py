"""Testes do modulo 1: Automato de Pilha (estrutura do grampo)."""

import pytest
from conftest import carregar

from validador_dna.alfabetos import SIGMA_AP, SimboloForaDoAlfabeto
from validador_dna.automato_pilha import ESTADOS, FUNDO, TRANSICOES, AutomatoPilha, reconhecer

CASOS = carregar("casos_ap.json")


@pytest.mark.parametrize("caso", CASOS, ids=[c["id"] for c in CASOS])
def test_decisao_do_ap(caso):
    res = reconhecer(caso["entrada"])
    assert res.decisao == caso["esperado"], f"{caso['id']}: {caso['regra']} | motivo: {res.motivo}"


def test_requisitos_dos_casos():
    aceitas = [c for c in CASOS if c["esperado"] == "ACEITA"]
    rejeitadas = [c for c in CASOS if c["esperado"] == "REJEITA"]
    assert len(aceitas) >= 8 and len(rejeitadas) >= 8
    entradas = [c["entrada"] for c in CASOS]
    assert len(entradas) == len(set(entradas)), "cadeias devem ser distintas"
    assert all(set(e) <= set(SIGMA_AP) for e in entradas), "todas formadas com o alfabeto do módulo"
    assert any("Caso-limite" in c["regra"] for c in CASOS)
    # todas as cadeias aceitas tem pelo menos 18 simbolos (o minimo da linguagem e 18)
    assert min(len(c["entrada"]) for c in aceitas) == 18


def test_pelo_menos_oito_estados_e_determinismo():
    assert len(ESTADOS) >= 8
    # chaves unicas => no maximo uma transicao por (estado, simbolo, topo); nao ha transicoes-epsilon
    assert all(simbolo != "" for (_q, simbolo, _z) in TRANSICOES)


def test_rastreamento_contem_estado_posicao_e_pilha():
    res = reconhecer("GGACgaaGTCC#ATGATG")
    inicial = res.passos[0]
    assert (inicial.estado, inicial.posicao, inicial.pilha) == ("q0", 1, FUNDO)
    # cada passo consome exatamente um simbolo
    assert [p.posicao for p in res.passos] == list(range(1, 20))
    # apos a haste 5' (4 bases) a pilha guarda w invertida sobre Z
    assert res.passos[4].pilha == "CAGGZ"
    # ao ler '#', a pilha voltou a conter apenas Z
    assert res.passos[12].pilha == FUNDO and res.passos[12].estado == "q9"
    assert res.estado_final == "q15" and res.pilha_final == FUNDO


def test_entrada_deve_ser_consumida_por_inteiro():
    # a cadeia passa por q15 (estado final) no meio, mas so aceita se terminar la
    res = reconhecer("GGACgaaGTCC#ATGATGA")
    assert any(p.estado == "q15" for p in res.passos) and not res.aceita


@pytest.mark.parametrize("entrada,simbolo,posicao", [
    ("GGACgaaGUCC#ATGATG", "U", 9),
    ("GGACgaaGTCC#ATGNTG", "N", 16),
    ("GGACgaaGTCC #ATGATG", " ", 12),
])
def test_simbolo_fora_do_alfabeto(entrada, simbolo, posicao):
    with pytest.raises(SimboloForaDoAlfabeto) as erro:
        AutomatoPilha().executar(entrada)
    assert erro.value.simbolo == simbolo and erro.value.posicao == posicao
    assert "não pertence ao alfabeto de entrada" in str(erro.value)
