"""Testes da camada JSON usada pela interface web (sem abrir servidor)."""

from validador_dna.servidor_web import processar_derivacao, processar_validacao


def test_fluxo_completo_aceita():
    d = processar_validacao("GATCCgaaaGGATC#ATGGCAATGGCA", "completo")
    assert d["decisao"] == "ACEITA" and d["aceita"]
    assert d["trecho_all"] == "ATGGCAATGGCA"
    assert d["ap"]["passos"][0]["estado"] == "q0"
    assert d["all"]["passos"][-1]["estado"] == "qac"


def test_rejeicoes_e_erro():
    assert processar_validacao("GATCCgaaaGGATG#ATGGCAATGGCA", "completo")["decisao"] == "REJEITA (AP)"
    d = processar_validacao("GATCCgaaaGGATC#ATGGCAATGGCT", "completo")
    assert d["decisao"] == "REJEITA (ALL)" and d["all"] is not None
    d = processar_validacao("GATCCgaaaGGATC#ATGGCNATGGCA", "completo")
    assert d["decisao"] == "ERRO" and "'N'" in d["erro"]


def test_modos_isolados():
    assert processar_validacao("GGACgaaGTCC#ATGATG", "ap")["ap"]["aceita"]
    assert processar_validacao("CAGCAGCAGCAGCAGCAG", "all")["all"]["aceita"]
    assert "erro" in processar_validacao("GGACgaaGTCC#ATGATG", "all")


def test_entradas_invalidas():
    assert "erro" in processar_validacao("   ", "completo")
    assert "erro" in processar_validacao("A" * 301, "completo")
    assert "erro" in processar_validacao("GGACgaaGTCC#ATGATG", "xyz")


def test_derivacao():
    assert "P1: S → H # R" in processar_derivacao("GGACgaaGTCC#ATGATG")["texto"]
    assert "erro" in processar_derivacao("XYZ")
