"""Interface grafica (Tkinter, biblioteca padrao) para a demonstracao em sala.

Execucao:  python -m validador_dna gui
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import formatacao as F
from .alfabetos import SimboloForaDoAlfabeto
from .automato_linear import ResultadoALL
from .automato_linear import reconhecer as rodar_all
from .automato_pilha import ResultadoAP
from .automato_pilha import reconhecer as rodar_ap
from .pipeline import validar

EXEMPLOS = [
    "GATCCgaaaGGATC#ATGGCAATGGCA",  # aceita AP e ALL
    "GATCCgaaaGGATG#ATGGCAATGGCA",  # rejeita AP
    "GATCCgaaaGGATC#ATGGCAATGGCT",  # aceita AP, rejeita ALL
    "GATCCgaaaGGATC#ATGGCNATGGCA",  # simbolo fora do alfabeto
    "GGACgaaGTCC#ATGATG",           # menor cadeia aceita (18)
    "CAGCAGCAGCAGCAGCAG",           # entrada para o modulo ALL
]

COR_OK = "#1b7f3b"
COR_ERRO = "#b3261e"
COR_NEUTRA = "#444444"
FONTE_MONO = ("Consolas", 11)


class Aplicacao(ttk.Frame):
    def __init__(self, raiz: tk.Tk) -> None:
        super().__init__(raiz, padding=10)
        self.raiz = raiz
        raiz.title("Validador de construtos de DNA — AP + ALL")
        raiz.geometry("1250x780")
        self.pack(fill="both", expand=True)
        self.res_ap: ResultadoAP | None = None
        self.res_all: ResultadoALL | None = None
        self._animando = False
        self._montar()

    # ------------------------------------------------------------------ layout
    def _montar(self) -> None:
        topo = ttk.Frame(self)
        topo.pack(fill="x")
        ttk.Label(topo, text="Cadeia:").pack(side="left")
        self.entrada = ttk.Combobox(topo, values=EXEMPLOS, font=FONTE_MONO, width=48)
        self.entrada.set(EXEMPLOS[0])
        self.entrada.pack(side="left", padx=6)
        self.entrada.bind("<Return>", lambda _e: self.validar())
        ttk.Button(topo, text="Validar (AP → ALL)", command=self.validar).pack(side="left", padx=3)
        ttk.Button(topo, text="Só AP", command=self.so_ap).pack(side="left", padx=3)
        ttk.Button(topo, text="Só ALL", command=self.so_all).pack(side="left", padx=3)
        ttk.Button(topo, text="Derivação", command=self.derivar).pack(side="left", padx=3)

        resultado = ttk.Frame(self, padding=(0, 8))
        resultado.pack(fill="x")
        self.lbl_ap = tk.Label(resultado, anchor="w", justify="left", font=("Segoe UI", 10), wraplength=1200)
        self.lbl_all = tk.Label(resultado, anchor="w", justify="left", font=("Segoe UI", 10), wraplength=1200)
        self.lbl_final = tk.Label(resultado, anchor="w", font=("Segoe UI", 13, "bold"))
        for w in (self.lbl_ap, self.lbl_all, self.lbl_final):
            w.pack(fill="x")

        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True)
        self._aba_ap()
        self._aba_all()
        self.txt_der = self._aba_texto("Derivação (GLC)")
        txt_esp = self._aba_texto("Especificação formal")
        txt_esp.insert("1.0", "\n\n".join([F.especificacao_glc(), F.especificacao_ap(), F.especificacao_all()]))
        txt_esp.configure(state="disabled")

    def _tabela(self, pai: ttk.Frame, colunas: list[tuple[str, int]]) -> ttk.Treeview:
        quadro = ttk.Frame(pai)
        quadro.pack(fill="both", expand=True)
        arvore = ttk.Treeview(quadro, columns=[c for c, _ in colunas], show="headings", height=14)
        for nome, largura in colunas:
            arvore.heading(nome, text=nome)
            arvore.column(nome, width=largura, anchor="w", stretch=nome == colunas[-1][0])
        barra = ttk.Scrollbar(quadro, orient="vertical", command=arvore.yview)
        arvore.configure(yscrollcommand=barra.set)
        arvore.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        arvore.tag_configure("mono", font=FONTE_MONO)
        return arvore

    def _aba_ap(self) -> None:
        aba = ttk.Frame(self.abas, padding=6)
        self.abas.add(aba, text="AP — pilha")
        self.tab_ap = self._tabela(aba, [("Passo", 55), ("Estado", 65), ("Pos", 45),
                                         ("Leitura (lido|restante)", 300), ("Pilha (topo→base)", 170),
                                         ("Transição", 300)])
        self.tab_ap.bind("<<TreeviewSelect>>", lambda _e: self._desenhar_ap())
        self.canvas_ap = tk.Canvas(aba, height=200, background="white")
        self.canvas_ap.pack(fill="x", pady=(6, 0))

    def _aba_all(self) -> None:
        aba = ttk.Frame(self.abas, padding=6)
        self.abas.add(aba, text="ALL — fita limitada")
        self.tab_all = self._tabela(aba, [("Passo", 55), ("Estado", 65), ("Cab", 45),
                                          ("Fita ([ ] = cabeçote)", 330), ("Transição", 300)])
        self.tab_all.bind("<<TreeviewSelect>>", lambda _e: self._desenhar_all())
        controles = ttk.Frame(aba)
        controles.pack(fill="x", pady=4)
        ttk.Button(controles, text="◀ passo", command=lambda: self._mover(-1)).pack(side="left")
        ttk.Button(controles, text="passo ▶", command=lambda: self._mover(+1)).pack(side="left", padx=4)
        ttk.Button(controles, text="▶ reproduzir / ■ parar", command=self._alternar_animacao).pack(side="left")
        self.canvas_all = tk.Canvas(aba, height=150, background="white")
        self.canvas_all.pack(fill="x")

    def _aba_texto(self, titulo: str) -> tk.Text:
        aba = ttk.Frame(self.abas, padding=6)
        self.abas.add(aba, text=titulo)
        txt = tk.Text(aba, font=FONTE_MONO, wrap="none")
        barra = ttk.Scrollbar(aba, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=barra.set)
        txt.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return txt

    # ----------------------------------------------------------------- acoes
    def _cadeia(self) -> str:
        return self.entrada.get().strip()

    def _rotulo(self, rotulo: tk.Label, texto: str, ok: bool | None) -> None:
        cor = COR_NEUTRA if ok is None else (COR_OK if ok else COR_ERRO)
        rotulo.configure(text=texto, foreground=cor)

    def _limpar(self) -> None:
        self._animando = False
        for t in (self.tab_ap, self.tab_all):
            t.delete(*t.get_children())
        self.canvas_ap.delete("all")
        self.canvas_all.delete("all")
        self.res_ap = self.res_all = None
        for r in (self.lbl_ap, self.lbl_all, self.lbl_final):
            r.configure(text="")

    def validar(self) -> None:
        self._limpar()
        res = validar(self._cadeia())
        if res.erro:
            self._rotulo(self.lbl_final, res.erro, False)
            return
        self._preencher_ap(res.ap)  # type: ignore[arg-type]
        if res.all is None:
            self._rotulo(self.lbl_all, "ALL: sem execução (cadeia rejeitada pelo AP).", None)
        else:
            self._preencher_all(res.all)
        self._rotulo(self.lbl_final, f"Decisão final: {res.decisao}", res.aceita)
        self.abas.select(0 if res.all is None else 1)

    def so_ap(self) -> None:
        self._limpar()
        try:
            res = rodar_ap(self._cadeia())
        except SimboloForaDoAlfabeto as e:
            self._rotulo(self.lbl_final, str(e), False)
            return
        self._preencher_ap(res)
        self._rotulo(self.lbl_final, f"Decisão do AP: {res.decisao}", res.aceita)
        self.abas.select(0)

    def so_all(self) -> None:
        self._limpar()
        try:
            res = rodar_all(self._cadeia())
        except SimboloForaDoAlfabeto as e:
            self._rotulo(self.lbl_final, str(e), False)
            return
        self._preencher_all(res)
        self._rotulo(self.lbl_final, f"Decisão do ALL: {res.decisao}", res.aceita)
        self.abas.select(1)

    def derivar(self) -> None:
        self.txt_der.delete("1.0", "end")
        try:
            self.txt_der.insert("1.0", F.derivacao(self._cadeia()))
        except ValueError as e:
            self.txt_der.insert("1.0", f"ERRO: {e}")
        self.abas.select(2)

    def _preencher_ap(self, res: ResultadoAP) -> None:
        self.res_ap = res
        for p in res.passos:
            self.tab_ap.insert("", "end", values=(p.passo, p.estado, p.posicao, f"{p.lida}|{p.restante}",
                                                  p.pilha, p.transicao), tags=("mono",))
        self._rotulo(self.lbl_ap, f"AP: {res.decisao} — {res.motivo}", res.aceita)
        ultimo = self.tab_ap.get_children()[-1]
        self.tab_ap.selection_set(ultimo)
        self.tab_ap.see(ultimo)

    def _preencher_all(self, res: ResultadoALL) -> None:
        self.res_all = res
        for p in res.passos:
            self.tab_all.insert("", "end", values=(p.passo, p.estado, p.cabecote, p.fita_com_cabecote(),
                                                   p.transicao), tags=("mono",))
        self._rotulo(self.lbl_all, f"ALL: {res.decisao} — {res.motivo}", res.aceita)
        primeiro = self.tab_all.get_children()[0]
        self.tab_all.selection_set(primeiro)

    # -------------------------------------------------------------- desenhos
    @staticmethod
    def _indice(tabela: ttk.Treeview) -> int | None:
        sel = tabela.selection()
        return None if not sel else tabela.index(sel[0])

    def _desenhar_ap(self) -> None:
        c = self.canvas_ap
        c.delete("all")
        i = self._indice(self.tab_ap)
        if self.res_ap is None or i is None:
            return
        p = self.res_ap.passos[i]
        cadeia = self.res_ap.cadeia
        c.create_text(10, 12, anchor="w", text=f"Estado {p.estado}  —  posição de leitura {p.posicao}",
                      font=("Segoe UI", 10, "bold"))
        lado = 26
        for j, s in enumerate(cadeia):
            x = 10 + j * lado
            lido = j < len(p.lida)
            c.create_rectangle(x, 30, x + lado, 30 + lado, fill="#e8e8e8" if lido else "white")
            c.create_text(x + lado / 2, 30 + lado / 2, text=s, font=FONTE_MONO)
        xcab = 10 + len(p.lida) * lado
        c.create_polygon(xcab + lado / 2 - 6, 70, xcab + lado / 2 + 6, 70, xcab + lado / 2, 60, fill=COR_ERRO)
        # pilha desenhada na horizontal: topo a esquerda
        c.create_text(10, 100, anchor="w", text="Pilha (topo → base):", font=("Segoe UI", 10))
        for j, s in enumerate(p.pilha):
            x = 150 + j * lado
            c.create_rectangle(x, 88, x + lado, 88 + lado, fill="#fff4cc" if j == 0 else "white")
            c.create_text(x + lado / 2, 88 + lado / 2, text=s, font=FONTE_MONO)
        c.create_text(10, 140, anchor="w", text=p.transicao, font=FONTE_MONO)

    def _desenhar_all(self) -> None:
        c = self.canvas_all
        c.delete("all")
        i = self._indice(self.tab_all)
        if self.res_all is None or i is None:
            return
        p = self.res_all.passos[i]
        c.create_text(10, 12, anchor="w",
                      text=f"Passo {p.passo}  —  estado {p.estado}  —  cabeçote na célula {p.cabecote}",
                      font=("Segoe UI", 10, "bold"))
        lado = 30
        for j, s in enumerate(p.fita):
            x = 10 + j * lado
            borda = j in (0, len(p.fita) - 1)
            cor = "#d0d7ff" if borda else ("#e3f5e1" if s == "*" else ("#fff4cc" if s.islower() else "white"))
            c.create_rectangle(x, 32, x + lado, 32 + lado, fill=cor, width=3 if j == p.cabecote else 1,
                               outline=COR_ERRO if j == p.cabecote else "black")
            c.create_text(x + lado / 2, 32 + lado / 2, text=s, font=FONTE_MONO)
            c.create_text(x + lado / 2, 32 + lado + 10, text=str(j), font=("Segoe UI", 7))
        xc = 10 + p.cabecote * lado + lado / 2
        c.create_polygon(xc - 7, 92, xc + 7, 92, xc, 80, fill=COR_ERRO)
        c.create_text(10, 115, anchor="w", text=p.transicao, font=FONTE_MONO)

    def _mover(self, delta: int) -> bool:
        filhos = self.tab_all.get_children()
        if not filhos:
            return False
        i = self._indice(self.tab_all) or 0
        novo = max(0, min(len(filhos) - 1, i + delta))
        self.tab_all.selection_set(filhos[novo])
        self.tab_all.see(filhos[novo])
        return novo != i

    def _alternar_animacao(self) -> None:
        self._animando = not self._animando
        if self._animando:
            self._animar()

    def _animar(self) -> None:
        if self._animando and self._mover(+1):
            self.after(120, self._animar)
        else:
            self._animando = False


def iniciar() -> None:
    raiz = tk.Tk()
    Aplicacao(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    iniciar()
