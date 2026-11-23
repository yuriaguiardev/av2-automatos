"""Testes do fluxo completo AP -> ALL e das mensagens de erro de alfabeto."""

import pytest
from conftest import carregar

from validador_dna.__main__ import main
from validador_dna.alfabetos import SimboloForaDoAlfabeto
from validador_dna.automato_linear import reconhecer as rodar_all
from validador_dna.automato_pilha import reconhecer as rodar_ap
from validador_dna.pipeline import validar

INTEGRACAO = carregar("casos_integracao.json")
ERROS = carregar("casos_erro.json")


@pytest.mark.parametrize("caso", INTEGRACAO, ids=[c["id"] for c in INTEGRACAO])
def test_fluxo_completo(caso):
    res = validar(caso["entrada"])
    assert len(caso["entrada"]) >= 18
    assert res.decisao == caso["esperado"]
    assert res.ap.decisao == caso["esperado_ap"]
    if caso["esperado_all"] == "NÃO EXECUTA":
        assert res.all is None
    else:
        assert res.all.decisao == caso["esperado_all"]
        assert res.trecho_all == caso["entrada"].split("#")[1]


def test_tres_cenarios_obrigatorios():
    finais = {c["esperado"] for c in INTEGRACAO}
    assert finais == {"ACEITA", "REJEITA (AP)", "REJEITA (ALL)"}


@pytest.mark.parametrize("caso", ERROS, ids=[c["id"] for c in ERROS])
def test_mensagem_de_erro(caso):
    if caso["modulo"] == "validar":
        res = validar(caso["entrada"])
        assert res.decisao == "ERRO" and res.ap is None and res.all is None
        mensagem = res.erro
    else:
        executar = rodar_ap if caso["modulo"] == "ap" else rodar_all
        with pytest.raises(SimboloForaDoAlfabeto) as erro:
            executar(caso["entrada"])
        mensagem = str(erro.value)
    assert mensagem.startswith("ERRO: o símbolo") and "não pertence ao alfabeto de entrada" in mensagem


def test_cli_codigos_de_saida(capsys):
    assert main(["validar", INTEGRACAO[0]["entrada"]]) == 0
    assert main(["validar", INTEGRACAO[1]["entrada"]]) == 1
    assert main(["validar", ERROS[0]["entrada"]]) == 2
    saida = capsys.readouterr().out
    assert "ERRO: o símbolo 'N'" in saida
