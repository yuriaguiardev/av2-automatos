"""Gera os diagramas de estados do AP e do ALL em SVG (docs/diagramas/).

Uso:  python scripts/gerar_diagramas.py
Os diagramas foram desenhados pela equipe a partir das tabelas de transicao;
este script apenas posiciona os estados e as setas.
"""

from __future__ import annotations

import math
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "docs" / "diagramas"
R = 25  # raio dos estados

COR_TRACO = "#1f2937"
COR_ROTULO = "#1e3a8a"
COR_FINAL = "#dcfce7"
COR_REJ = "#fee2e2"
COR_NO = "#ffffff"


class Diagrama:
    def __init__(self, largura: int, altura: int, titulo: str):
        self.l, self.a = largura, altura
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
            self.partes.append(f'<line x1="{x - R - 34}" y1="{y}" x2="{x - R - 2}" y2="{y}" class="seta"/>')
            self.partes.append(f'<text x="{x - R - 36}" y="{y + 20}" class="rot" text-anchor="start">início</text>')

    # ------------------------------------------------------------ arestas
    def _borda(self, x: float, y: float, alvo_x: float, alvo_y: float) -> tuple[float, float]:
        d = math.hypot(alvo_x - x, alvo_y - y) or 1
        return x + (alvo_x - x) * R / d, y + (alvo_y - y) * R / d

    def _rotulo(self, x: float, y: float, linhas: list[str], ancora: str = "middle") -> None:
        for i, linha in enumerate(linhas):
            self.partes.append(f'<text x="{x}" y="{y + i * 14}" text-anchor="{ancora}" class="rot">{escape(linha)}</text>')

    def seta(self, a: str, b: str, rotulo: list[str], curva: float = 0.0, dx: float = 0, dy: float = -8,
             ancora: str = "middle") -> None:
        (x1, y1), (x2, y2) = self.pos[a], self.pos[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        d = math.hypot(x2 - x1, y2 - y1)
        nx, ny = -(y2 - y1) / d, (x2 - x1) / d  # normal
        cx, cy = mx + nx * curva, my + ny * curva
        sx, sy = self._borda(x1, y1, cx, cy)
        ex, ey = self._borda(x2, y2, cx, cy)
        self.partes.append(f'<path d="M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" class="seta"/>')
        # ponto medio da curva quadratica
        px, py = 0.25 * sx + 0.5 * cx + 0.25 * ex, 0.25 * sy + 0.5 * cy + 0.25 * ey
        self._rotulo(px + dx, py + dy, rotulo, ancora)

    def laco(self, a: str, rotulo: list[str], lado: str = "cima") -> None:
        x, y = self.pos[a]
        ang = {"cima": -90, "baixo": 90, "esq": 180, "dir": 0}[lado]
        t = math.radians(ang)
        a1, a2 = t - 0.45, t + 0.45
        sx, sy = x + R * math.cos(a1), y + R * math.sin(a1)
        ex, ey = x + R * math.cos(a2), y + R * math.sin(a2)
        k = 62
        c1x, c1y = x + k * math.cos(a1 - 0.25), y + k * math.sin(a1 - 0.25)
        c2x, c2y = x + k * math.cos(a2 + 0.25), y + k * math.sin(a2 + 0.25)
        self.partes.append(f'<path d="M{sx:.1f},{sy:.1f} C{c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {ex:.1f},{ey:.1f}" class="seta"/>')
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
  <defs><marker id="ponta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{COR_TRACO}"/></marker></defs>
  <style>
    .seta {{ fill: none; stroke: {COR_TRACO}; stroke-width: 1.4; marker-end: url(#ponta); }}
    .no {{ font: 600 14px 'Segoe UI', Arial, sans-serif; fill: #111827; }}
    .rot {{ font: 12px Consolas, 'Courier New', monospace; fill: {COR_ROTULO}; }}
    .nota {{ font: 13px 'Segoe UI', Arial, sans-serif; fill: #374151; }}
    .titulo {{ font: 700 17px 'Segoe UI', Arial, sans-serif; fill: #111827; }}
  </style>"""
        corpo = "\n  ".join(self.partes)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.l} {self.a}" width="{self.l}" height="{self.a}">'
                f'{estilo}\n  <rect width="100%" height="100%" fill="white"/>\n'
                f'  <text x="20" y="28" class="titulo">{self.titulo}</text>\n  {corpo}\n</svg>\n')


def diagrama_ap() -> str:
    d = Diagrama(1150, 470, "Autômato de Pilha — estrutura do grampo (aceitação por estado final q15)")
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


def diagrama_all() -> str:
    d = Diagrama(1000, 800, "Autômato Linearmente Limitado — repetição em tandem uu")
    d.estado("q0", 80, 130, inicial=True)
    d.estado("q1", 240, 130)
    d.estado("q2", 450, 130)
    d.estado("q3", 660, 130)
    d.estado("q4", 450, 290)
    d.estado("qrj", 900, 130, cor=COR_REJ)
    d.estado("q5", 240, 450)
    d.estado("q6", 560, 450)
    d.estado("q7", 560, 640)
    d.estado("qac", 300, 640, final=True, cor=COR_FINAL)
    d.estado("qX", 860, 640, rotulo="qX")

    d.seta("q0", "q1", ["M1 </<,D"], dy=-10)
    d.seta("q1", "q2", ["M2 X/x,D"], dy=-10)
    d.laco("q2", ["M5 X/X,D"], lado="baixo")
    d.seta("q2", "q3", ["M6 x/x,E", "M7 >/>,E"], dy=-24)
    d.seta("q3", "q4", ["M8 X/x,E"], dx=12, dy=4, ancora="start")
    d.laco("q4", ["M10 X/X,E"], lado="baixo")
    d.seta("q4", "q1", ["M11 x/x,D"], dx=-12, dy=4, ancora="end")
    d.seta("q3", "qrj", ["M9 x/x,P", "(ímpar)"], dy=20)
    d.seta("q1", "qrj", ["M4 >/>,P  (vazia)"], curva=-95, dy=-8)
    d.seta("q1", "q5", ["M3 x/X,D", "(meio achado)"], dx=-10, dy=0, ancora="end")
    d.laco("q5", ["M12 x/X,D"], lado="baixo")
    d.seta("q5", "q6", ["M13 >/>,E"], dy=-10)
    d.laco("q6", ["M14 s/s,E", "s∈{X,x,*}"], lado="dir")
    d.seta("q6", "q7", ["M15 </<,D"], dx=-10, dy=0, ancora="end")
    d.laco("q7", ["M16 */*,D"], lado="baixo")
    d.seta("q7", "qac", ["M18 >/>,P"], dy=-10)
    d.seta("q7", "qX", ["M17 x/*,D"], dy=-10, curva=0)
    d.laco("qX", ["M19 s/s,D", "s∈{x,*}"], lado="baixo")
    d.seta("qX", "q6", ["M20 X/*,E"], dx=14, dy=0, ancora="start")
    d.seta("qX", "qrj", ["M21 Y/Y,P", "(Y≠X)"], dx=10, dy=0, ancora="start")
    d.nota(20, 765, ["qX representa os 4 estados qA, qC, qG, qT (a base X lida da 1ª cópia fica \"guardada\" no estado).",
                     "X, Y ∈ {A,C,G,T}; x = minúscula de X; '*' = célula conferida.  Rótulo  lido/escrito,mov  (E, D, P). Sem transição ⇒ rejeição."])
    return d.svg()


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "ap.svg").write_text(diagrama_ap(), encoding="utf-8")
    (SAIDA / "all.svg").write_text(diagrama_all(), encoding="utf-8")
    print(f"Diagramas gravados em {SAIDA}")


if __name__ == "__main__":
    main()
