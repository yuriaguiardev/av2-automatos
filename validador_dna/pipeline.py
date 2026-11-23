"""Fluxo completo de validacao em duas etapas: AP (estrutura) -> ALL (copia)."""

from __future__ import annotations

from dataclasses import dataclass

from .alfabetos import SEPARADOR, SIGMA_AP, SimboloForaDoAlfabeto, verificar_alfabeto
from .automato_linear import AutomatoLinearmenteLimitado, ResultadoALL
from .automato_pilha import AutomatoPilha, ResultadoAP


@dataclass
class ResultadoValidacao:
    cadeia: str
    erro: str | None = None
    ap: ResultadoAP | None = None
    trecho_all: str | None = None
    all: ResultadoALL | None = None

    @property
    def aceita(self) -> bool:
        return self.erro is None and self.ap is not None and self.ap.aceita and self.all is not None and self.all.aceita

    @property
    def decisao(self) -> str:
        if self.erro is not None:
            return "ERRO"
        if not self.ap.aceita:  # type: ignore[union-attr]
            return "REJEITA (AP)"
        if not self.all.aceita:  # type: ignore[union-attr]
            return "REJEITA (ALL)"
        return "ACEITA"

    def resumo(self) -> str:
        if self.erro is not None:
            return self.erro
        linhas = [f"Etapa 1 - AP : {self.ap.decisao}  -> {self.ap.motivo}"]  # type: ignore[union-attr]
        if self.all is None:
            linhas.append("Etapa 2 - ALL: sem execução (a cadeia foi rejeitada pelo AP).")
        else:
            linhas.append(f"Etapa 2 - ALL: {self.all.decisao}  (trecho após '#': {self.trecho_all}) -> {self.all.motivo}")
        linhas.append(f"Decisão final: {self.decisao}")
        return "\n".join(linhas)


def validar(cadeia: str) -> ResultadoValidacao:
    """Executa o AP; se aceitar, entrega ao ALL o trecho apos '#'."""
    try:
        verificar_alfabeto(cadeia, SIGMA_AP, "validador (AP)")
    except SimboloForaDoAlfabeto as e:
        return ResultadoValidacao(cadeia, erro=str(e))

    resultado = ResultadoValidacao(cadeia, ap=AutomatoPilha().executar(cadeia))
    if resultado.ap.aceita:  # type: ignore[union-attr]
        resultado.trecho_all = cadeia.split(SEPARADOR, 1)[1]
        resultado.all = AutomatoLinearmenteLimitado().executar(resultado.trecho_all)
    return resultado
