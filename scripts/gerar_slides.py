"""Gera os slides da apresentacao (docs/slides/slides.html e slides.pdf, 16:9).

Uso:  python scripts/gerar_slides.py
Para ver um unico slide no navegador: slides.html?s=5
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

from gerar_diagramas import diagrama_all, diagrama_ap  # noqa: E402
from gerar_relatorio import figura_dependencias, html_para_pdf  # noqa: E402
from gerar_resultados_testes import executar_todos  # noqa: E402

from validador_dna import automato_linear as ALL  # noqa: E402
from validador_dna import automato_pilha as AP  # noqa: E402
from validador_dna import gramatica as GLC  # noqa: E402
from validador_dna.pipeline import validar  # noqa: E402

e = html.escape
SAIDA = RAIZ / "docs" / "slides"
INT1, INT2, INT3 = "GATCCgaaaGGATC#ATGGCAATGGCA", "GATCCgaaaGGATG#ATGGCAATGGCA", "GATCCgaaaGGATC#ATGGCAATGGCT"

CSS = """
@page { size: 1280px 720px; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #e5e7eb; }
body { font-family: 'Segoe UI', Calibri, Arial, sans-serif; color: #0f172a; }
.slide { width: 1280px; height: 720px; position: relative; overflow: hidden; background: #ffffff;
         padding: 56px 72px 48px; page-break-after: always; break-after: page; margin: 0 auto; }
.slide.escuro { background: #0b2545; color: #f8fafc; }
h1 { font-size: 40px; margin: 0 0 22px; font-weight: 700; color: #0b2545; letter-spacing: -0.3px; }
.escuro h1 { color: #ffffff; }
h2 { font-size: 22px; margin: 0 0 10px; color: #0e7c7b; }
p, li { font-size: 19px; line-height: 1.45; }
ul { margin: 6px 0; padding-left: 24px; } li { margin: 4px 0; }
code, .mono { font-family: Consolas, 'Courier New', monospace; }
code { background: #eef2f7; padding: 1px 5px; border-radius: 4px; font-size: 0.92em; }
.escuro code { background: #183a63; color: #e2e8f0; }
.quem { position: absolute; right: 72px; bottom: 20px; font-size: 13px; color: #64748b; }
.num { position: absolute; left: 72px; bottom: 20px; font-size: 13px; color: #94a3b8; }
.escuro .quem, .escuro .num { color: #9fb3c8; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 36px; }
.cols.c64 { grid-template-columns: 1.5fr 1fr; } .cols.c46 { grid-template-columns: 1fr 1.5fr; }
.card { background: #f1f5f9; border-radius: 14px; padding: 18px 22px; }
.card.teal { background: #e6f6f5; } .card.rosa { background: #fdecec; } .card.verde { background: #e9f7ee; }
.escuro .card { background: #12355f; }
.def { font-size: 20px; background: #e6f6f5; border-radius: 12px; padding: 14px 18px; margin: 8px 0 14px; }
pre { font-family: Consolas, monospace; font-size: 16px; line-height: 1.35; margin: 0; white-space: pre; }
table { border-collapse: collapse; width: 100%; }
th { background: #0b2545; color: #fff; text-align: left; font-weight: 600; }
th, td { padding: 4px 8px; font-size: 14.5px; }
td { border-bottom: 1px solid #e2e8f0; }
table.mono td { font-family: Consolas, monospace; font-size: 14px; }
.fig svg { width: 100%; height: auto; }
.grande { font-size: 60px; font-weight: 800; color: #0e7c7b; line-height: 1; }
.lbl { font-size: 15px; color: #475569; margin-top: 6px; }
.ok { color: #15803d; font-weight: 700; } .nok { color: #b91c1c; font-weight: 700; }
.chip { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 15px; font-weight: 700; }
.chip.ok { background: #dcfce7; } .chip.nok { background: #fee2e2; } .chip.cinza { background: #e2e8f0; color: #334155; }
.fluxo { display: flex; align-items: center; gap: 14px; margin: 14px 0 26px; }
.caixa { border-radius: 14px; padding: 14px 16px; text-align: center; font-size: 17px; font-weight: 600; background: #f1f5f9; min-width: 150px; }
.caixa small { display: block; font-weight: 400; font-size: 14px; color: #475569; margin-top: 4px; }
.caixa.ap { background: #dbeafe; } .caixa.all { background: #fde68a; } .caixa.fim { background: #dcfce7; }
.seta { font-size: 30px; color: #64748b; }
.fita { display: flex; gap: 4px; margin: 6px 0; }
.fita span { width: 34px; height: 38px; display: flex; align-items: center; justify-content: center; border: 1.5px solid #334155;
             border-radius: 6px; font-family: Consolas, monospace; font-size: 19px; background: #fff; }
.fita span.m { background: #dbeafe; } .fita span.l { background: #fef3c7; } .fita span.x { background: #dcfce7; }
.fita span.h { outline: 3px solid #dc2626; outline-offset: 1px; }
.base { display: inline-block; width: 30px; text-align: center; font-family: Consolas, monospace; font-size: 22px; font-weight: 700; }
"""

JS = """
<script>
const s = new URLSearchParams(location.search).get('s');
if (s) document.querySelectorAll('.slide').forEach((el, i) => { if (i + 1 != s) el.style.display = 'none'; });
</script>"""


def fita(conteudo: str, cab: int | None = None) -> str:
    cel = []
    for i, c in enumerate(conteudo):
        cls = "m" if c in "<>" else ("x" if c == "*" else ("l" if c.islower() else ""))
        if i == cab:
            cls += " h"
        cel.append(f'<span class="{cls}">{e(c)}</span>')
    return '<div class="fita">' + "".join(cel) + "</div>"


def quadros_fita() -> str:
    """Configuracoes reais do ALL para ATGATG, escolhidas por evento."""
    passos = ALL.reconhecer("ATGATG").passos
    eventos = [(0, "início")]
    def primeiro(regra: str, k: int = 1) -> int:
        idx = [i for i, p in enumerate(passos) if p.transicao.startswith(regra + ":")]
        return idx[k - 1]
    eventos += [(primeiro("M8"), "M8: pontas marcadas"), (primeiro("M3"), "M3: meio achado"),
                (primeiro("M13"), "M13: 2ª metade restaurada"),
                (primeiro("M17"), f"M17: lê a, carrega A em {passos[primeiro('M17')].estado}"),
                (primeiro("M20"), "M20: qA achou A, 1º par conferido"),
                (len(passos) - 1, "M18: aceita")]
    linhas = []
    for i, rotulo in eventos:
        p = passos[i]
        linhas.append(f'<div style="display:flex;align-items:center;gap:12px">{fita(p.fita, p.cabecote)}'
                      f'<span style="font-size:14px;color:#475569">passo {p.passo} · {p.estado} · {e(rotulo)}</span></div>')
    return "".join(linhas) + (f'<p style="font-size:16px;margin-top:8px"><span class="chip ok">ACEITA</span> '
                              f'em {len(passos) - 1} passos</p>')


def montar() -> str:
    slides: list[tuple[str, str, str]] = []  # (classe, conteudo, quem)

    def add(conteudo: str, quem: str = "", classe: str = "") -> None:
        slides.append((classe, conteudo, quem))

    grupos = executar_todos()
    total = sum(len(v) for v in grupos.values())
    ok = sum(l["ok"] for v in grupos.values() for l in v)

    # 1 - capa
    add("""
<div style="position:absolute;left:72px;top:150px;right:72px">
  <div style="font-size:20px;color:#7dd3c8;font-weight:600">Linguagens Formais e Autômatos · Trabalho prático</div>
  <div style="font-size:54px;font-weight:800;line-height:1.12;margin:18px 0 22px">Validador de construtos<br>de DNA sintético</div>
  <div style="font-size:24px;color:#cbd5e1">Grampo verificado por <b style="color:#fff">Autômato de Pilha</b> ·
  repetição em tandem verificada por <b style="color:#fff">Autômato Linearmente Limitado</b></div>
  <div style="margin-top:48px;font-size:21px">João Rath &nbsp;·&nbsp; Pedro Paulo &nbsp;·&nbsp; Yuri Aguiar</div>
</div>
<div style="position:absolute;right:72px;top:70px;font-family:Consolas,monospace;font-size:26px;color:#7dd3c8;text-align:right;line-height:1.5">
GATCC<span style="color:#fbbf24">gaaa</span>GGATC<br><span style="color:#94a3b8">#</span>ATGGCA·ATGGCA</div>
""", "Yuri", "escuro")

    # 2 - problema
    add(f"""
<h1>O problema: validar um construto antes da síntese</h1>
<div class="cols">
 <div class="card teal">
  <h2>1. Grampo (hairpin)</h2>
  <pre style="font-size:21px">       alça
 5' G A T C C  g
    | | | | |    a
 3' C T A G G  a
               a</pre>
  <p style="font-size:17px;margin-top:10px">A haste 3' é o <b>complemento reverso</b> da haste 5' (A↔T, C↔G): a 1ª base pareia com a última.
  Haste ≥ 4 pares · alça ≥ 3 bases (em <b>minúsculas</b>).</p>
 </div>
 <div class="card" style="background:#fef9e7">
  <h2>2. Repetição em tandem (após #)</h2>
  <p style="font-size:26px;font-family:Consolas,monospace;margin:22px 0"><span style="background:#fde68a;padding:2px 4px">ATGGCA</span><span style="background:#bfdbfe;padding:2px 4px">ATGGCA</span></p>
  <p style="font-size:17px">A região deve ser <b>uu</b>: duas cópias idênticas e consecutivas (ex.: repetições <code>CAG</code>).
  Unidade ≥ 3 bases, então a região tem comprimento par ≥ 6.</p>
 </div>
</div>
<p style="margin-top:22px">Menor construto válido: <code>GGACgaaGTCC#ATGATG</code>, com <b>18 símbolos</b>.
Base do domínio: Searls (1992), <i>The Linguistics of DNA</i>.</p>
""", "Yuri")

    # 3 - arquitetura
    add(f"""
<h1>Arquitetura: duas etapas, dois níveis de Chomsky</h1>
<div class="fluxo">
 <div class="caixa">Entrada<small>Σ = {{A,C,G,T,a,c,g,t,#}}</small></div><div class="seta">→</div>
 <div class="caixa">Alfabeto<small>símbolo inválido ⇒ ERRO</small></div><div class="seta">→</div>
 <div class="caixa ap">AP<small>estrutura livre de contexto</small></div><div class="seta">→</div>
 <div class="caixa all">ALL<small>recebe só o trecho após #</small></div><div class="seta">→</div>
 <div class="caixa fim">Decisão</div>
</div>
<table>
<tr><th>Cenário</th><th>Entrada</th><th>AP</th><th>ALL</th></tr>
<tr><td>1</td><td class="mono"><code>{INT1}</code></td><td><span class="chip ok">aceita</span></td><td><span class="chip ok">aceita</span></td></tr>
<tr><td>2</td><td class="mono"><code>{INT2}</code></td><td><span class="chip nok">rejeita</span></td><td><span class="chip cinza">não executa</span></td></tr>
<tr><td>3</td><td class="mono"><code>{INT3}</code></td><td><span class="chip ok">aceita</span></td><td><span class="chip nok">rejeita</span></td></tr>
</table>
<p style="margin-top:20px"><b>Divisão de trabalho:</b> o AP verifica tudo o que é livre de contexto (hastes, alça, um único #, região par ≥ 6).
O ALL verifica só o que a pilha não consegue: <b>a 1ª metade é igual à 2ª</b>.</p>
""", "Yuri")

    # 4 - L1 e GLC
    prod = "\n".join(GLC.producoes_agrupadas())
    add(f"""
<h1>L₁ e a gramática livre de contexto</h1>
<div class="def">L₁ = {{ w · x · cr(w) # y &nbsp;|&nbsp; w ∈ {{A,C,G,T}}<sup>k</sup>, k ≥ 4; &nbsp;x ∈ {{a,c,g,t}}<sup>m</sup>, m ≥ 3; &nbsp;y ∈ {{A,C,G,T}}<sup>2j</sup>, j ≥ 3 }}
<br><span style="font-size:16px;color:#475569">cr(w) = complemento reverso de w</span></div>
<div class="cols c64">
 <div><p style="margin:0 0 6px"><b>G = (V, T, P, S)</b>, V = {{S,H,I,J,K,L,N,R,B}}, T = Σ, {len(GLC.PRODUCOES)} produções:</p>
 <pre style="font-size:15.5px;background:#f8fafc;padding:12px;border-radius:10px">{e(prod)}</pre></div>
 <div class="card"><h2>Como ler</h2><ul style="font-size:17px">
  <li><code>H → X H X'</code> põe uma base e o seu complemento em <b>pontas opostas</b>: aninhamento</li>
  <li>H → I → J → K forçam <b>≥ 4 pares</b></li>
  <li>L → NL | NNN: alça ≥ 3</li>
  <li>R → BBR | B⁶: região par ≥ 6</li></ul></div>
</div>
""", "Pedro")

    # 5 - derivacao
    der = GLC.derivacao_mais_a_esquerda("GGACgaaGTCC#ATGATG")
    linhas = [f"<tr><td>{i}</td><td>{'' if p.producao is None else e(str(p.producao))}</td><td><code>{e(p.forma)}</code></td></tr>"
              for i, p in enumerate(der)]
    meio = 9
    add(f"""
<h1>Derivação mais à esquerda de <code style="font-size:34px">GGACgaaGTCC#ATGATG</code></h1>
<div class="cols">
 <table class="mono"><tr><th>#</th><th>Produção</th><th>Forma sentencial</th></tr>{''.join(linhas[:meio + 1])}</table>
 <div><table class="mono"><tr><th>#</th><th>Produção</th><th>Forma sentencial</th></tr>{''.join(linhas[meio + 1:])}</table>
 <div class="card teal" style="margin-top:18px"><p style="font-size:17px;margin:0">Pares gerados de fora para dentro:
 G…C, G…C, A…T, C…G. A haste 3' (GTCC) sai automaticamente como o complemento reverso de GGAC.</p></div></div>
</div>
""", "Pedro")

    # 6 - AP diagrama
    add(f"""
<h1>Autômato de Pilha M = (Q, Σ, Γ, δ, q0, Z, F)</h1>
<div class="fig" style="margin-top:-6px">{diagrama_ap()}</div>
<div class="cols" style="gap:24px;margin-top:2px">
 <p style="font-size:17px;margin:0"><b>17 estados</b> · Γ = {{Z, A, C, G, T}} · início (q0, entrada, Z) · <b>aceitação por estado final</b> F = {{q15}},
 com a entrada consumida por inteiro.</p>
 <p style="font-size:17px;margin:0"><b>Determinístico, sem ε</b>: a minúscula marca o fim da haste 5', então não é preciso adivinhar o meio.
 20 regras esquemáticas geram {len(AP.TRANSICOES)} transições concretas.</p>
</div>
""", "Pedro")

    # 7 - como a pilha decide
    add(f"""
<h1>Como a pilha decide</h1>
<div class="cols c46">
 <div class="card">
  <h2>As 4 fases do AP</h2>
  <ul style="font-size:17.5px">
  <li><b>q0→q4</b> (T1–T5): <b>empilha</b> a haste 5'</li>
  <li><b>q5→q7</b> (T6–T9): lê a alça, pilha intacta</li>
  <li><b>q8</b> (T10–T11): <b>desempilha</b> se a base lida for o complemento do topo</li>
  <li><b>T12</b>: lê <code>#</code> só com Z no topo</li>
  <li><b>q9→q16</b> (T13–T20): conta a região; para em q15 se for par ≥ 6</li></ul>
  <p style="font-size:16px;color:#475569">Sem transição ⇒ rejeita na hora.</p>
 </div>
 <div>
  <table class="mono"><tr><th>Passo</th><th>Estado</th><th>Lido | restante</th><th>Pilha</th></tr>
  <tr><td>0</td><td>q0</td><td>|GGACgaaGTCC#…</td><td>Z</td></tr>
  <tr><td>4</td><td>q4</td><td>GGAC|gaaGTCC#…</td><td>CAGGZ</td></tr>
  <tr><td>7</td><td>q7</td><td>…gaa|GTCC#…</td><td>CAGGZ</td></tr>
  <tr><td>8</td><td>q8</td><td>…G|TCC#…</td><td>AGGZ</td></tr>
  <tr><td>11</td><td>q8</td><td>…GTCC|#ATGATG</td><td>Z</td></tr>
  <tr><td>12</td><td>q9</td><td>…#|ATGATG</td><td>Z</td></tr>
  <tr><td>18</td><td><b>q15</b></td><td>…ATGATG|</td><td>Z</td></tr></table>
  <p style="font-size:17px">A última base empilhada (C) é a primeira a ser casada (G): <b>LIFO = aninhamento</b>.</p>
 </div>
</div>
""", "Pedro")

    # 8 - GLC <-> AP e nao regular
    add("""
<h1>Por que L(AP) = L(G) e por que L₁ não é regular</h1>
<div class="cols">
 <div class="card teal"><h2>GLC ↔ AP</h2><ul style="font-size:17px">
 <li>Cada <code>X·H·X'</code> da gramática corresponde a <b>empilhar X</b> e, depois, <b>desempilhar ao ler X'</b></li>
 <li>Invariante em q8: lido z = cr(w''), pilha = w'ᴿZ, com w = w'w''</li>
 <li>T12 só com Z ⇒ hastes de mesmo tamanho e complementares</li>
 <li>Níveis H/I/J/K ↔ q1–q4; L ↔ q5–q7; R ↔ q9–q16</li>
 <li>Testado: 4000 cadeias com a mesma decisão no AP e na definição</li></ul></div>
 <div class="card"><h2>Não regular (bombeamento)</h2>
 <p style="font-size:17px">s = A<sup>p</sup> aaa T<sup>p</sup> #AAAAAA ∈ L₁. Com |xy| ≤ p, temos y = A<sup>i</sup>.</p>
 <p style="font-size:17px">xy²z = A<sup>p+i</sup> aaa T<sup>p</sup> #AAAAAA ∉ L₁, pois a haste 3' fica curta.</p>
 <p style="font-size:17px">Um AFD precisaria lembrar uma haste de tamanho <b>ilimitado</b>. A pilha dá essa memória.</p></div>
</div>
""", "Pedro")

    # 9 - dependencia sensivel ao contexto
    add(f"""
<h1>A dependência que a pilha não consegue verificar</h1>
<div class="fig" style="max-width:1000px;margin:0 auto 10px">{figura_dependencias()}</div>
<div class="cols">
 <div class="card rosa"><h2>L₂ = {{ uu | u ∈ {{A,C,G,T}}⁺ }} não é LLC</h2>
 <p style="font-size:16.5px">L₂ ∩ A⁺C⁺A⁺C⁺ = AⁱCʲAⁱCʲ. Pelo bombeamento para LLC, a janela vxy (≤ p) toca só 2 blocos <b>vizinhos</b>,
 e bombear desequilibra o bloco correspondente. Como LLC é fechada sob ∩ regular, L₂ não pode ser LLC.</p></div>
 <div class="card verde"><h2>L₂ é sensível ao contexto</h2>
 <p style="font-size:16.5px">Construímos um ALL que a decide. Teorema de <b>Kuroda (1964)</b>: ALL ⇔ LSC.
 A pilha é LIFO e a cópia pede ordem FIFO: <b>u₁ com u₁, u₂ com u₂…</b></p></div>
</div>
""", "João")

    # 10 - ALL diagrama
    add(f"""
<h1 style="margin-bottom:10px">Autômato Linearmente Limitado</h1>
<div style="display:grid;grid-template-columns:1fr 205px;gap:16px;align-items:start">
 <div class="fig">{diagrama_all(notas=False)}</div>
 <div style="font-size:14.5px;line-height:1.4">
  <p style="font-size:14.5px;margin:0 0 6px"><b>M = (Q, Σ, Γ, δ, q0, &lt;, &gt;, qac, qrj)</b></p>
  <ul style="padding-left:16px;margin:0">
   <li style="font-size:14.5px"><b>14 estados</b>: q0–q7, qA, qC, qG, qT, qac, qrj</li>
   <li style="font-size:14.5px">Σ = {{A,C,G,T}}; Γ = Σ ∪ {{a,c,g,t,*,&lt;,&gt;}}</li>
   <li style="font-size:14.5px">Início: q0 sobre <code>&lt;</code></li>
   <li style="font-size:14.5px">δ(q, lido) = (p, escrito, E/D/P)</li>
   <li style="font-size:14.5px">Aceita em <b>qac</b>; rejeita em <b>qrj</b> ou sem transição</li>
   <li style="font-size:14.5px">Determinístico: {len(ALL.TRANSICOES)} transições</li>
  </ul>
  <div class="card teal" style="padding:10px 12px;margin-top:10px">
   <p style="font-size:14px;margin:0"><b>Fase 3: um estado por base.</b> q7 lê <code>a</code> ⇒ <b>qA</b>. Em qA, achar <code>A</code> confere (M20);
   achar C, G ou T rejeita (M21).</p></div>
 </div>
</div>
""", "João")

    # 11 - algoritmo 3 fases
    add(f"""
<h1>O algoritmo em 3 fases, na própria fita</h1>
<div class="cols" style="grid-template-columns:0.9fr 1.1fr;gap:28px">
 <div style="font-size:17px">
  <p><b style="color:#0e7c7b">Fase 1: achar o meio</b> (q1–q4). Marca as pontas alternadamente, de maiúscula para minúscula (A→a, C→c, G→g, T→t). Se sobrar uma base sem par, o comprimento é ímpar e a cadeia é rejeitada (M9).</p>
  <p><b style="color:#0e7c7b">Fase 2: restaurar</b> (q5). A 2ª metade volta a maiúsculas.</p>
  <p><b style="color:#0e7c7b">Fase 3: comparar</b> (q6, q7, qA, qC, qG, qT). q7 troca a 1ª minúscula por <code>*</code> e vai para o estado da base lida
  (<code>a</code> ⇒ qA, <code>t</code> ⇒ qT…). Esse estado anda até a 1ª maiúscula: a mesma base vira <code>*</code> (M20), outra rejeita (M21). Só <code>*</code> ⇒ aceita.</p>
 </div>
 <div>
  <p style="margin:0;font-size:15px;color:#475569">Entrada <code>ATGATG</code> (n = 6, fita com 8 células)</p>
  {quadros_fita()}
 </div>
</div>
""", "João")

    # 12 - fita limitada e parada
    add(f"""
<h1>Fita limitada e garantia de parada</h1>
<div class="cols">
 <div class="card"><h2>n células + 2 marcadores fixos</h2>
  {fita("<GATGAT>", None)}
  <ul style="font-size:16.5px">
   <li>Quem lê <code>&lt;</code> regrava <code>&lt;</code> e só vai para D. Quem lê <code>&gt;</code> regrava <code>&gt;</code> e só vai para E</li>
   <li>Cabeçote sempre em [0, n+1], verificado na tabela e em todo passo dos testes</li>
   <li>Memória = reescrita das células (x, *) + estados qA, qC, qG, qT</li></ul></div>
 <div class="card teal"><h2>Por que sempre termina</h2>
  <ul style="font-size:16.5px">
   <li><b>AP:</b> sem ε, cada passo consome 1 símbolo ⇒ ≤ n passos</li>
   <li><b>ALL:</b> cada ciclo marca 2 células (fase 1) ou confere 2 (fase 3) ⇒ ≤ n/2 ciclos de O(n)</li>
   <li>Total O(n²). Aceitas: exatamente <b>(5n² + 18n + 16)/4</b> passos</li>
   <li>Salvaguarda: configurações finitas, |Q|·(n+2)·|Γ|ⁿ</li></ul></div>
</div>
""", "João")

    # 13 - rastreamentos
    r2 = validar(INT2).ap
    linhas_ap = "".join(f"<tr><td>{p.passo}</td><td>{p.estado}</td><td>{p.posicao}</td><td>{e(p.pilha)}</td><td>{e(p.transicao.split(':')[0])}</td></tr>"
                        for p in r2.passos[9:])
    r3 = validar(INT3).all
    sel = [b for a, b in zip(r3.passos, r3.passos[1:]) if a.estado != b.estado or a.fita != b.fita][-6:]
    linhas_all = "".join(f"<tr><td>{p.passo}</td><td>{p.estado}</td><td>{p.cabecote}</td><td>{e(p.fita_com_cabecote())}</td></tr>" for p in sel)
    add(f"""
<h1>Rastreamentos: como as operações levam à decisão</h1>
<div class="cols">
 <div><h2>AP, cenário 2: <span class="nok">rejeita</span></h2>
  <table class="mono"><tr><th>Passo</th><th>Estado</th><th>Pos</th><th>Pilha</th><th>Regra</th></tr>{linhas_ap}</table>
  <p style="font-size:16px">Na posição 14 é lido <b>G</b> com <b>G</b> no topo. Esperava-se C, e não há transição: <b>rejeita</b>. O ALL nem executa.</p></div>
 <div><h2>ALL, cenário 3: <span class="nok">rejeita</span></h2>
  <table class="mono"><tr><th>Passo</th><th>Estado</th><th>Cab</th><th>Fita</th></tr>{linhas_all}</table>
  <p style="font-size:16px">qA carrega a 6ª base da 1ª cópia (A) e encontra <b>T</b> na célula 12: regra M21, <b>rejeita</b>
  após {len(r3.passos) - 1} passos.</p></div>
</div>
""", "Pedro (AP) e João (ALL)")

    # 14 - demo
    add(f"""
<h1>Demonstração ao vivo</h1>
<div class="cols c64">
 <div>
  <pre style="font-size:17px;background:#0b2545;color:#e2e8f0;padding:18px;border-radius:12px">python -m validador_dna demo --resumido
python -m validador_dna gui

python -m validador_dna validar "{INT1}" --rastro
python -m validador_dna validar "{INT2}" --rastro
python -m validador_dna validar "{INT3}" --rastro
python -m validador_dna derivar "GGACgaaGTCC#ATGATG"</pre>
 </div>
 <div class="card" style="font-size:17px">
  <p><span class="chip ok">1</span> AP e ALL aceitam</p>
  <p><span class="chip nok">2</span> AP rejeita: G × topo G</p>
  <p><span class="chip nok">3</span> AP aceita, ALL rejeita: T ≠ A</p>
  <p><span class="chip cinza">+</span> <code>…ATGGCNATGGCA</code> ⇒ <b>ERRO</b>: “o símbolo 'N' na posição 21 não pertence ao alfabeto de entrada…”</p>
 </div>
</div>
""", "Yuri (executa); Pedro e João comentam")

    # 15 - testes
    n_ap = len(grupos["ap"]); n_all = len(grupos["all"])
    add(f"""
<h1>Testes: {ok}/{total} decisões conferem</h1>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin:10px 0 26px">
 <div class="card"><div class="grande">{n_ap}</div><div class="lbl">casos do AP: {sum(l['esperado']=='ACEITA' for l in grupos['ap'])} aceitas, {sum(l['esperado']=='REJEITA' for l in grupos['ap'])} rejeitadas</div></div>
 <div class="card"><div class="grande">{n_all}</div><div class="lbl">casos do ALL: {sum(l['esperado']=='ACEITA' for l in grupos['all'])} aceitas, {sum(l['esperado']=='REJEITA' for l in grupos['all'])} rejeitadas</div></div>
 <div class="card"><div class="grande">3 + 4</div><div class="lbl">cenários de integração + entradas fora do alfabeto</div></div>
 <div class="card"><div class="grande">120</div><div class="lbl">testes pytest passando</div></div>
</div>
<div class="cols">
 <ul style="font-size:17px">
  <li>Casos-limite: menor aceita (18 símbolos), vazia, 17 símbolos, <code>AA</code>, <code>A</code></li>
  <li>Cada registro tem entrada, esperado, obtido e regra verificada (<code>docs/resultados_testes.md</code>)</li></ul>
 <ul style="font-size:17px">
  <li>ALL exaustivo: todas as <b>5461</b> cadeias com até 6 símbolos</li>
  <li>GLC → AP: 1000 cadeias geradas; AP × definição: 3000 mutadas</li></ul>
</div>
""", "Yuri")

    # 16 - limitacoes
    add("""
<h1>O que os testes mostraram e as limitações</h1>
<div class="cols">
 <div class="card teal"><h2>Observações</h2><ul style="font-size:17px">
  <li><code>…#ATGATGAT</code> passa no AP (par ≥ 6) mas não é cópia: só o ALL pega</li>
  <li><code>ACGTACGTAC·CATGCATGCA</code> (uuᴿ) seria aceito por uma pilha; o ALL rejeita</li>
  <li>Cenários 2 e 3 diferem do 1 em um único símbolo, e cada erro é pego pelo módulo certo</li></ul></div>
 <div class="card rosa"><h2>Limitações</h2><ul style="font-size:17px">
  <li><b>Custo quadrático do ALL</b>: 238 passos (n = 12), 832 (n = 24), daí o modo <code>--resumido</code></li>
  <li>Determinismo depende da alça em minúsculas</li>
  <li>Só pares perfeitos A–T/C–G; cópia exata e só 2 cópias</li>
  <li>Estados de contagem (mínimos) alongam o AP</li></ul></div>
</div>
""", "Yuri")

    # 17 - equipe e IA
    add("""
<h1>Equipe, contribuições e uso de IA</h1>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:22px">
 <div class="card"><h2>Yuri Aguiar</h2><p style="font-size:16.5px">Problema, arquitetura e integração AP → ALL, validação do alfabeto, interfaces CLI/GUI, testes e documentação</p></div>
 <div class="card"><h2>Pedro Paulo</h2><p style="font-size:16.5px">L₁, GLC, derivação, AP, relação GLC ↔ AP e prova de não regularidade</p></div>
 <div class="card"><h2>João Rath</h2><p style="font-size:16.5px">L₂, prova não-LLC, ALL em 3 fases, parada e limite da fita, diagramas</p></div>
</div>
<div class="card" style="margin-top:24px;font-size:16.5px">
<p style="margin:0 0 6px"><b>Uso de IA:</b> Claude (Anthropic), via Claude Code, como apoio na sugestão do domínio e no rascunho de código, testes, relatório e slides.</p>
<p style="margin:0"><b>A equipe verificou:</b> simulação à mão dos 3 cenários, tabelas × diagramas, provas × referências, execução de toda a suíte de testes.</p></div>
<p style="font-size:16px;color:#475569;margin-top:18px">Referências: Hopcroft, Motwani e Ullman (2006); Sipser (2007); Menezes (2011); Kuroda (1964); Searls (1992; 2002); Aho et al. (2008).</p>
""", "Yuri")

    partes = []
    for i, (classe, conteudo, quem) in enumerate(slides, start=1):
        rodape = f'<div class="num">{i}/{len(slides)}</div>' + (f'<div class="quem">Apresenta: {e(quem)}</div>' if quem else "")
        partes.append(f'<section class="slide {classe}">{conteudo}{rodape}</section>')
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Slides — Validador de construtos de DNA</title>'
            f'<style>{CSS}</style></head><body>{"".join(partes)}{JS}</body></html>')


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    caminho = SAIDA / "slides.html"
    caminho.write_text(montar(), encoding="utf-8")
    pdf = SAIDA / "slides.pdf"
    if pdf.exists():
        pdf.unlink()
    ok = html_para_pdf(caminho, pdf)
    print(f"HTML: {caminho}" + (f"\nPDF:  {pdf}" if ok else ""))


if __name__ == "__main__":
    main()
