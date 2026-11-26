"""Gera os diagramas de estados do AP e do ALL em SVG (docs/diagramas/).

Uso:  python scripts/gerar_diagramas.py
Os diagramas foram desenhados pela equipe a partir das tabelas de transicao;
este script apenas posiciona os estados e as setas.
"""

from __future__ import annotations

import math
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from validador_dna.automato_linear import TRANSICOES as DELTA_ALL  # noqa: E402

SAIDA = RAIZ / "docs" / "diagramas"
R = 25  # raio dos estados

COR_TRACO = "#1f2937"
COR_ROTULO = "#1e3a8a"
COR_FINAL = "#dcfce7"
COR_REJ = "#fee2e2"
COR_NO = "#ffffff"


class Diagrama:
    def __init__(self, largura: int, altura: int, titulo: str, ident: str = "d"):
        self.l, self.a = largura, altura
        self.ident = ident  # prefixo do id do marcador de seta (único por diagrama na mesma página)
        self.partes: list[str] = []
        self.pos: dict[str, tuple[float, float]] = {}
        self.titulo = titulo

    # -------------------------------------------------------------- nos
    def estado(self, nome: str, x: float, y: float, final: bool = False, inicial: bool = False,
               cor: str = COR_NO, rotulo: str | None = None) -> None:
        self.pos[nome] = (x, y)
        self.partes.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="{cor}" stroke="{COR_TRACO}" stroke-width="1.6"/>')
        if final:
            self.partes.append(f'<circle cx="{x}" cy="{y}" r="{R - 4}" fill="none" stroke="{COR_TRACO}" stroke-width="1.4"/>')
        texto = rotulo or nome
        self.partes.append(f'<text x="{x}" y="{y + 5}" text-anchor="middle" class="no">{texto}</text>')
        if inicial:
            self.partes.append(f'<line x1="{x - R - 34}" y1="{y}" x2="{x - R - 2}" y2="{y}" class="seta-{self.ident}"/>')
            self.partes.append(f'<text x="{x - R - 36}" y="{y + 20}" class="rot" text-anchor="start">início</text>')

    # ------------------------------------------------------------ arestas
    def _borda(self, x: float, y: float, alvo_x: float, alvo_y: float) -> tuple[float, float]:
        d = math.hypot(alvo_x - x, alvo_y - y) or 1
        return x + (alvo_x - x) * R / d, y + (alvo_y - y) * R / d

    def _rotulo(self, x: float, y: float, linhas: list[str], ancora: str = "middle") -> None:
        for i, linha in enumerate(linhas):
            self.partes.append(f'<text x="{x}" y="{y + i * 14}" text-anchor="{ancora}" class="rot">{escape(linha)}</text>')

    def seta(self, a: str, b: str, rotulo: list[str], curva: float = 0.0, dx: float = 0, dy: float = -8,
             ancora: str = "middle", t: float = 0.5) -> None:
        """Seta de a para b; o rotulo fica no ponto t da curva (0 = origem, 1 = destino)."""
        (x1, y1), (x2, y2) = self.pos[a], self.pos[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        d = math.hypot(x2 - x1, y2 - y1)
        nx, ny = -(y2 - y1) / d, (x2 - x1) / d  # normal
        cx, cy = mx + nx * curva, my + ny * curva
        sx, sy = self._borda(x1, y1, cx, cy)
        ex, ey = self._borda(x2, y2, cx, cy)
        self.partes.append(f'<path d="M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" class="seta-{self.ident}"/>')
        # ponto t da curva quadratica
        u = 1 - t
        px, py = u * u * sx + 2 * u * t * cx + t * t * ex, u * u * sy + 2 * u * t * cy + t * t * ey
        self._rotulo(px + dx, py + dy, rotulo, ancora)

    def laco(self, a: str, rotulo: list[str], lado: str | float = "cima") -> None:
        """Laco no estado a. lado: cima/baixo/esq/dir ou um angulo em graus (0 = direita, 90 = baixo)."""
        x, y = self.pos[a]
        ang = lado if isinstance(lado, (int, float)) else {"cima": -90, "baixo": 90, "esq": 180, "dir": 0}[lado]
        t = math.radians(ang)
        if isinstance(lado, (int, float)):
            lado = "dir" if math.cos(t) > 0.35 else ("esq" if math.cos(t) < -0.35 else ("baixo" if math.sin(t) > 0 else "cima"))
        a1, a2 = t - 0.45, t + 0.45
        sx, sy = x + R * math.cos(a1), y + R * math.sin(a1)
        ex, ey = x + R * math.cos(a2), y + R * math.sin(a2)
        k = 62
        c1x, c1y = x + k * math.cos(a1 - 0.25), y + k * math.sin(a1 - 0.25)
        c2x, c2y = x + k * math.cos(a2 + 0.25), y + k * math.sin(a2 + 0.25)
        self.partes.append(f'<path d="M{sx:.1f},{sy:.1f} C{c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {ex:.1f},{ey:.1f}" class="seta-{self.ident}"/>')
        lx, ly = x + 58 * math.cos(t), y + 58 * math.sin(t)
        if lado == "cima":
            self._rotulo(lx, ly - 6 - 14 * (len(rotulo) - 1), rotulo)
        elif lado == "baixo":
            self._rotulo(lx, ly + 14, rotulo)
        elif lado == "esq":
            self._rotulo(lx - 4, ly, rotulo, "end")
        else:
            self._rotulo(lx + 4, ly, rotulo, "start")

    def nota(self, x: float, y: float, linhas: list[str]) -> None:
        for i, linha in enumerate(linhas):
            self.partes.append(f'<text x="{x}" y="{y + i * 16}" class="nota">{escape(linha)}</text>')

    def svg(self) -> str:
        estilo = f"""
  <defs><marker id="ponta-{self.ident}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{COR_TRACO}"/></marker></defs>
  <style>
    .seta-{self.ident} {{ fill: none; stroke: {COR_TRACO}; stroke-width: 1.4; marker-end: url(#ponta-{self.ident}); }}
    .no {{ font: 600 14px 'Segoe UI', Arial, sans-serif; fill: #111827; }}
    .rot {{ font: 12px Consolas, 'Courier New', monospace; fill: {COR_ROTULO};
            paint-order: stroke; stroke: white; stroke-width: 4px; stroke-linejoin: round; }}
    .nota {{ font: 13px 'Segoe UI', Arial, sans-serif; fill: #374151; }}
    .titulo {{ font: 700 17px 'Segoe UI', Arial, sans-serif; fill: #111827; }}
  </style>"""
        corpo = "\n  ".join(self.partes)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.l} {self.a}" width="{self.l}" height="{self.a}">'
                f'{estilo}\n  <rect width="100%" height="100%" fill="white"/>\n'
                f'  <text x="20" y="28" class="titulo">{self.titulo}</text>\n  {corpo}\n</svg>\n')


def diagrama_ap() -> str:
    d = Diagrama(1150, 470, "Autômato de Pilha — estrutura do grampo (aceitação por estado final q15)", "ap")
    y1, y2 = 120, 330
    for i in range(9):
        d.estado(f"q{i}", 95 + i * 122, y1, inicial=i == 0)
    xs = {9: 1071, 10: 949, 11: 827, 12: 705, 13: 583, 14: 461, 15: 339, 16: 140}
    for i, x in xs.items():
        d.estado(f"q{i}", x, y2, final=i == 15, cor=COR_FINAL if i == 15 else COR_NO)
    d.seta("q0", "q1", ["T1", "X,Z/XZ"], dy=-22)
    for i, t in ((1, "T2"), (2, "T3"), (3, "T4")):
        d.seta(f"q{i}", f"q{i + 1}", [t, "X,Y/XY"], dy=-22)
    d.laco("q4", ["T5", "X,Y/XY"])
    for i, t in ((4, "T6"), (5, "T7"), (6, "T8")):
        d.seta(f"q{i}", f"q{i + 1}", [t, "x,Y/Y"], dy=-22)
    d.laco("q7", ["T9", "x,Y/Y"])
    d.seta("q7", "q8", ["T10", "X,X'/ε"], dy=-22)
    d.laco("q8", ["T11", "X,X'/ε"])
    d.seta("q8", "q9", ["T12", "#,Z/Z"], dx=10, dy=0, ancora="start")
    for i, t in zip(range(9, 15), ("T13", "T14", "T15", "T16", "T17", "T18")):
        d.seta(f"q{i}", f"q{i + 1}", [t, "X,Z/Z"], dy=24)
    d.seta("q15", "q16", ["T19  X,Z/Z"], curva=-30, dy=20)
    d.seta("q16", "q15", ["T20  X,Z/Z"], curva=-30, dy=-8)
    d.nota(20, 420, ["X, Y ∈ {A,C,G,T};  x ∈ {a,c,g,t};  X' = complemento de X (A↔T, C↔G).",
                     "Rótulo  a,b/γ : lê a com b no topo e troca b por γ (γ = ε desempilha). Sem transição ⇒ rejeição. Estado final: q15."])
    return d.svg()


def rotulo_all(regra: str, origem: str, destino: str, por_linha: int = 2) -> list[str]:
    """Rotulo de uma seta do ALL no formato  regra lido/escrito,mov , com as transicoes concretas
    lidas da tabela δ real. Ex.: M5 A/A,D C/C,D G/G,D T/T,D (4 transicoes, quebradas em linhas)."""
    pares = [f"{t.lido}/{t.escrito},{t.movimento}" for t in DELTA_ALL.values()
             if t.regra == regra and t.origem == origem and t.destino == destino]
    if not pares:
        raise ValueError(f"sem transições {regra} de {origem} para {destino}")
    linhas = [" ".join(pares[i:i + por_linha]) for i in range(0, len(pares), por_linha)]
    linhas[0] = f"{regra} {linhas[0]}"
    return linhas


def diagrama_all(notas: bool = True) -> str:
    """Diagrama do ALL: só estados e símbolos reais (sem X, x, s, Y genéricos nem estado qX).

    notas=False omite a legenda de rodapé (usado nos slides, que explicam a notação no texto).
    """
    d = Diagrama(1400, 950 if notas else 890, "Autômato Linearmente Limitado — repetição em tandem uu", "all")
    r = rotulo_all
    # Fase 1 (achar o meio) na linha de cima
    d.estado("q0", 70, 140, inicial=True)
    d.estado("q1", 230, 140)
    d.estado("q2", 460, 140)
    d.estado("q3", 690, 140)
    d.estado("q4", 460, 330)
    d.estado("qrj", 900, 140, cor=COR_REJ)
    # Fase 2 (restaurar) e fase 3 (comparar): um estado por base carregada
    d.estado("q5", 230, 760)
    d.estado("q6", 900, 760)
    d.estado("q7", 900, 360)
    d.estado("qac", 995, 615, final=True, cor=COR_FINAL)
    carregadores = {"A": 500, "C": 710, "G": 1090, "T": 1300}
    for b, x in carregadores.items():
        d.estado("q" + b, x, 555)

    d.seta("q0", "q1", r("M1", "q0", "q1"), dy=-10)
    d.seta("q1", "q2", r("M2", "q1", "q2", por_linha=2), dy=-24)
    d.laco("q2", r("M5", "q2", "q2"), lado="baixo")
    d.seta("q2", "q3", r("M6", "q2", "q3") + r("M7", "q2", "q3"), dy=-38)
    d.seta("q3", "q4", r("M8", "q3", "q4"), dx=12, dy=4, ancora="start")
    d.laco("q4", r("M10", "q4", "q4"), lado="baixo")
    d.seta("q4", "q1", r("M11", "q4", "q1", por_linha=2), dx=-12, dy=4, ancora="end", t=0.35)
    d.seta("q3", "qrj", r("M9", "q3", "qrj", por_linha=2) + ["(ímpar)"], dy=22)
    d.seta("q1", "qrj", [r("M4", "q1", "qrj")[0] + "  (vazia)"], curva=-115, dy=-8)
    d.seta("q1", "q5", r("M3", "q1", "q5") + ["(meio achado)"], dx=-10, dy=0, ancora="end")
    d.laco("q5", r("M12", "q5", "q5", por_linha=2), lado="esq")
    d.seta("q5", "q6", r("M13", "q5", "q6"), dy=-10)
    d.laco("q6", r("M14", "q6", "q6", por_linha=3), lado="baixo")
    d.seta("q6", "q7", r("M15", "q6", "q7"), dx=-8, dy=0, ancora="end", t=0.62)
    d.laco("q7", r("M16", "q7", "q7"), lado="cima")
    d.seta("q7", "qac", r("M18", "q7", "qac"), dx=9, dy=4, ancora="start", t=0.8)

    for b, x in carregadores.items():
        q = "q" + b
        esq = x < 900
        externo = b in "AT"
        # M17: q7 le a minuscula, grava '*' e passa a "carregar" a base no estado
        if externo:
            d.seta("q7", q, r("M17", "q7", q), dy=-8, t=0.55)
        else:
            d.seta("q7", q, r("M17", "q7", q), dx=8 if esq else -8, dy=4, ancora="start" if esq else "end", t=0.68)
        # M19: atravessa o resto da 1a copia e as celulas ja conferidas
        d.laco(q, r("M19", q, q), lado="baixo")
        # M20: achou a mesma base na 2a copia
        if externo:
            d.seta(q, "q6", r("M20", q, "q6"), dx=-6 if esq else 6, dy=18, ancora="end" if esq else "start", t=0.62)
        else:
            d.seta(q, "q6", r("M20", q, "q6"), dx=8 if esq else -8, dy=6, ancora="start" if esq else "end", t=0.5)
        # M21: achou outra base: rejeita
        d.seta(q, "qrj", r("M21", q, "qrj", por_linha=1), dx=-8 if esq else 8, dy=0,
               ancora="end" if esq else "start", t=0.5)
    if notas:
        d.nota(20, 912, ["Rótulo  lido/escrito,mov  (E = esquerda, D = direita, P = parado). Uma seta pode ter várias transições: "
                         "M2 A/a,D C/c,D G/g,D T/t,D são 4 transições de q1 para q2.",
                         "'*' = célula conferida. Fase 3: qA, qC, qG e qT guardam no estado a base lida da 1ª cópia. "
                         "Todos os símbolos dos rótulos são símbolos reais de Γ."])
        return d.svg()
    # slides: sem título nem legenda, recortando a faixa vazia do topo
    d.titulo = ""
    return d.svg().replace(f'viewBox="0 0 {d.l} {d.a}" width="{d.l}" height="{d.a}"',
                           f'viewBox="0 40 {d.l} {d.a - 40}" width="{d.l}" height="{d.a - 40}"')


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "ap.svg").write_text(diagrama_ap(), encoding="utf-8")
    (SAIDA / "all.svg").write_text(diagrama_all(), encoding="utf-8")
    print(f"Diagramas gravados em {SAIDA}")


if __name__ == "__main__":
    main()
