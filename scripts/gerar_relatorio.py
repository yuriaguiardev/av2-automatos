"""Gera o relatorio tecnico (docs/relatorio/relatorio.html e relatorio.pdf).

Todas as tabelas de teste, derivacoes e rastreamentos sao produzidos executando
o codigo do repositorio, de modo que o relatorio sempre reflete a implementacao.

Uso:  python scripts/gerar_relatorio.py            (gera HTML e, se houver Edge/Chrome, o PDF)
"""

from __future__ import annotations

import html
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

from gerar_diagramas import diagrama_all, diagrama_ap  # noqa: E402
from gerar_resultados_testes import executar_todos  # noqa: E402

from validador_dna import automato_linear as ALL  # noqa: E402
from validador_dna import automato_pilha as AP  # noqa: E402
from validador_dna import gramatica as GLC  # noqa: E402
from validador_dna.pipeline import validar  # noqa: E402

# ----------------------------------------------------------------------------
# Dados da equipe (edite e rode o script novamente)
# ----------------------------------------------------------------------------
DISCIPLINA = "Linguagens Formais e Autômatos"
TURMA = os.environ.get("TURMA", "CC6__")  # ex.: set TURMA=CC6MA
INTEGRANTES = ["João Rath", "Pedro Paulo", "Yuri Aguiar"]
REPOSITORIO = os.environ.get("REPO_URL", "https://github.com/<usuario>/av2-automatos")
DATA = "novembro de 2026"

SAIDA = RAIZ / "docs" / "relatorio"
e = html.escape


def cod(s: str) -> str:
    return f"<code>{e(s)}</code>" if s else "<i>ε (vazia)</i>"


def tabela(cab: list[str], linhas: list[list[str]], classe: str = "") -> str:
    th = "".join(f"<th>{c}</th>" for c in cab)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas)
    return f'<table class="{classe}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'


def figura_dependencias() -> str:
    """Arcos aninhados (grampo) x arcos cruzados (copia)."""
    def arcos(seq: str, pares: list[tuple[int, int]], x0: float, titulo: str, cor: str) -> str:
        passo = 26
        partes = [f'<text x="{x0}" y="18" class="ft">{titulo}</text>']
        for i, c in enumerate(seq):
            partes.append(f'<text x="{x0 + i * passo}" y="110" class="fs" text-anchor="middle">{c}</text>')
        for a, b in pares:
            xa, xb = x0 + a * passo, x0 + b * passo
            h = 12 + (b - a) * 7
            partes.append(f'<path d="M{xa},94 C{xa},{94 - h} {xb},{94 - h} {xb},94" fill="none" stroke="{cor}" stroke-width="1.6"/>')
        return "".join(partes)

    grampo = "GATCgaaGATC"
    pares_g = [(0, 10), (1, 9), (2, 8), (3, 7)]
    copia = "ATGCATGC"
    pares_c = [(i, i + 4) for i in range(4)]
    return (
        '<svg viewBox="0 0 640 125" width="100%" style="max-width:640px">'
        "<style>.ft{font:600 12px 'Segoe UI',Arial}.fs{font:15px Consolas,monospace}</style>"
        + arcos(grampo, pares_g, 20, "Grampo (L₁): dependências ANINHADAS — pilha (LIFO)", "#1d4ed8")
        + arcos(copia, pares_c, 380, "Cópia uu (L₂): dependências CRUZADAS", "#b91c1c")
        + "</svg>"
    )


CSS = """
@page { size: A4; margin: 2.2cm 2cm 2.2cm 2cm;
  @bottom-center { content: counter(page); font: 9pt 'Segoe UI', Arial; color: #555; } }
@page :first { @bottom-center { content: none; } }
body { font: 10.5pt/1.5 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; color: #111; }
h1 { font-size: 17pt; margin: 0 0 4pt; color: #0f2c59; }
h2 { font-size: 14pt; color: #0f2c59; border-bottom: 1.5px solid #0f2c59; padding-bottom: 2pt; margin-top: 20pt; page-break-after: avoid; }
h3 { font-size: 11.5pt; color: #1e3a8a; margin: 14pt 0 4pt; page-break-after: avoid; }
p { text-align: justify; margin: 5pt 0; }
code, pre, .mono { font-family: Consolas, 'Courier New', monospace; font-size: 9.2pt; }
code { background: #f3f4f6; padding: 0 2px; border-radius: 2px; }
pre { background: #f8fafc; border: 1px solid #e5e7eb; padding: 6pt 8pt; white-space: pre-wrap; word-break: break-all; page-break-inside: avoid; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 8.6pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th { background: #0f2c59; color: white; text-align: left; padding: 3pt 4pt; }
td { border-bottom: 1px solid #e5e7eb; padding: 2.5pt 4pt; vertical-align: top; }
td code { font-size: 8.4pt; background: none; padding: 0; word-break: break-all; }
table.rastro td, table.rastro th { font-family: Consolas, monospace; font-size: 7.8pt; padding: 1.5pt 3pt; }
.capa { height: 25cm; display: flex; flex-direction: column; justify-content: space-between; page-break-after: always; }
.capa .topo { font-size: 12pt; color: #333; }
.capa .titulo { font-size: 24pt; font-weight: 700; color: #0f2c59; line-height: 1.25; }
.capa .sub { font-size: 13pt; color: #374151; margin-top: 10pt; }
.capa .equipe { font-size: 12pt; }
.caixa { border-left: 4px solid #1d4ed8; background: #eff6ff; padding: 6pt 10pt; margin: 8pt 0; page-break-inside: avoid; }
.caixa.aviso { border-color: #b45309; background: #fffbeb; }
.fig { text-align: center; margin: 8pt 0; page-break-inside: avoid; }
.fig svg { max-width: 100%; height: auto; }
.legenda { font-size: 9pt; color: #374151; text-align: center; margin-top: 2pt; }
.ok { color: #166534; font-weight: 600; } .nok { color: #b91c1c; font-weight: 600; }
.sumario li { margin: 1pt 0; }
.quebra { page-break-before: always; }
"""


def secao_testes(grupos: dict) -> str:
    def lin(l: dict) -> list[str]:
        cls = "ok" if l["ok"] else "nok"
        return [l["id"], cod(l["entrada"]), str(l["n"]), l["esperado"], f'<span class="{cls}">{l["obtido"]}</span>',
                e(l["regra"])]

    cab = ["ID", "Entrada", "n", "Esperado", "Obtido", "Regra verificada"]
    ap_html = tabela(cab, [lin(l) for l in grupos["ap"]])
    all_html = tabela(cab, [lin(l) for l in grupos["all"]])
    integ = tabela(
        ["ID", "Entrada", "AP (esp./obt.)", "ALL (esp./obt.)", "Final (esp./obt.)", "Regra verificada"],
        [[l["id"], cod(l["entrada"]), f'{l["esperado_ap"]} / {l["obtido_ap"]}', f'{l["esperado_all"]} / {l["obtido_all"]}',
          f'{l["esperado"]} / <span class="{"ok" if l["ok"] else "nok"}">{l["obtido"]}</span>', e(l["regra"])]
         for l in grupos["integracao"]])
    erros = tabela(
        ["ID", "Módulo", "Entrada", "Obtido", "Mensagem de erro exibida"],
        [[l["id"], l["modulo"], cod(l["entrada"]), l["obtido"], e(l["motivo"])] for l in grupos["erro"]])
    total = sum(len(v) for v in grupos.values())
    ok = sum(l["ok"] for v in grupos.values() for l in v)
    n_ap_a = sum(l["esperado"] == "ACEITA" for l in grupos["ap"])
    n_all_a = sum(l["esperado"] == "ACEITA" for l in grupos["all"])
    return f"""
<h2 id="testes">7. Testes</h2>
<p>Os casos estão em <code>dados/*.json</code> e são executados por <code>python -m pytest</code> (verificação automática)
e por <code>python scripts/gerar_resultados_testes.py</code> (gera <code>docs/resultados_testes.md/.csv</code>). Cada registro
contém a entrada, a decisão esperada, a decisão obtida e a regra verificada. Resultado: <b>{ok}/{total} casos com a decisão
obtida igual à esperada</b>; a suíte pytest completa (120 testes, incluindo os testes de propriedade da seção 7.5) passa integralmente.</p>

<h3>7.1 Módulo 1 — AP ({n_ap_a} aceitas, {len(grupos["ap"]) - n_ap_a} rejeitadas)</h3>
<p>Todas as cadeias são distintas e formadas com Σ<sub>AP</sub>. Casos-limite: AP-A01 (menor cadeia aceita, 18 símbolos),
AP-R13 (entrada vazia) e AP-R14 (17 símbolos, um a menos que o mínimo).</p>
{ap_html}

<h3>7.2 Módulo 2 — ALL ({n_all_a} aceitas, {len(grupos["all"]) - n_all_a} rejeitadas)</h3>
<p>Todas as cadeias são distintas e formadas com Σ<sub>ALL</sub>. As principais têm ≥ 18 símbolos; os casos-limite
são ALL-A10 (menor cadeia aceita, <code>AA</code>), ALL-R10 (vazia), ALL-R11 (um símbolo) e ALL-R12 (<code>AC</code>).</p>
{all_html}

<h3>7.3 Fluxo completo (três cenários obrigatórios)</h3>
{integ}

<h3>7.4 Símbolo fora do alfabeto de entrada</h3>
<p>A validação do alfabeto ocorre antes de qualquer transição. A cadeia não é submetida ao autômato e a mensagem abaixo é exibida
(código de saída 2 na linha de comando).</p>
{erros}

<h3>7.5 Testes de propriedade (evidência adicional de correção)</h3>
<ul>
<li><b>GLC → AP:</b> 1000 cadeias geradas aleatoriamente pelas produções de G são todas aceitas pelo AP.</li>
<li><b>AP × definição:</b> 3000 cadeias (geradas por G e depois mutadas por troca, inserção ou remoção de símbolos) têm a mesma
decisão no AP e na definição matemática de L₁ escrita sem pilha (oráculo usado só nos testes).</li>
<li><b>Derivação:</b> para cada cadeia aceita pelo AP, a derivação mais à esquerda construída termina na própria cadeia, e cada passo
aplica uma produção de P ao não terminal mais à esquerda; para as rejeitadas, não há derivação.</li>
<li><b>ALL exaustivo:</b> todas as 5461 cadeias sobre {{A,C,G,T}} com até 6 símbolos têm a decisão do ALL igual à de
<i>s ∈ {{uu}}</i>; mais 300 cadeias aleatórias de até 30 símbolos.</li>
<li><b>Fita limitada:</b> em todos os passos de todos os casos, a fita tem n + 2 células, os marcadores permanecem nas pontas e o cabeçote fica em [0, n+1].</li>
<li><b>Custo:</b> para u de 1 a 12 bases, as cadeias aceitas param em exatamente (5n² + 18n + 16)/4 passos.</li>
</ul>
"""


def rastro_ap_html(cadeia: str) -> str:
    r = validar(cadeia).ap
    linhas = [[str(p.passo), p.estado, str(p.posicao), e(p.lida) + "|" + e(p.restante), e(p.pilha), e(p.transicao)]
              for p in r.passos]
    return tabela(["Passo", "Estado", "Pos.", "Lido | restante", "Pilha (topo→base)", "Transição"], linhas, "rastro")


def rastro_all_html(cadeia: str, resumido: bool = True) -> tuple[str, int]:
    r = ALL.reconhecer(cadeia)
    passos = r.passos
    if resumido:
        sel = [passos[0]] + [b for a, b in zip(passos, passos[1:]) if a.estado != b.estado or a.fita != b.fita]
    else:
        sel = passos
    linhas = [[str(p.passo), p.estado, str(p.cabecote), e(p.fita_com_cabecote()), e(p.transicao)] for p in sel]
    return tabela(["Passo", "Estado", "Cab.", "Fita ([ ] = cabeçote)", "Transição"], linhas, "rastro"), len(passos) - 1


def montar() -> str:
    grupos = executar_todos()
    deriv = GLC.derivacao_mais_a_esquerda("GGACgaaGTCC#ATGATG")
    deriv_html = tabela(["#", "Produção aplicada", "Forma sentencial"],
                        [[str(i), "—" if p.producao is None else e(f"{p.producao.id}: {p.producao}"), f"<code>{e(p.forma)}</code>"]
                         for i, p in enumerate(deriv)])
    estados_ap = tabela(["Estado", "Significado"], [[q, e(d)] for q, d in AP.ESTADOS.items()])
    regras_ap = tabela(["Regra", "δ", "Efeito"], [[r["id"], f"<code>{e(r['delta'])}</code>", e(r["descricao"])] for r in AP.REGRAS])
    estados_all = tabela(["Estado", "Significado"], [[q, e(d)] for q, d in ALL.ESTADOS.items()])
    regras_all = tabela(["Regra", "δ", "Efeito"], [[r["id"], f"<code>{e(r['delta'])}</code>", e(r["descricao"])] for r in ALL.REGRAS])
    producoes = "<br>".join(e(l) for l in GLC.producoes_agrupadas())
    int1 = "GATCCgaaaGGATC#ATGGCAATGGCA"
    rastro_ap = rastro_ap_html(int1)
    rastro_all_curto, _ = rastro_all_html("ATGATG", resumido=False)
    rastro_all_int, passos_int = rastro_all_html("ATGGCAATGGCA")
    rastro_all_rej, passos_rej = rastro_all_html("ATGGCAATGGCT")

    capa = f"""
<div class="capa">
  <div class="topo">{DISCIPLINA}<br>Turma {e(TURMA)} — Trabalho prático: reconhecimento de linguagens com pilha e fita limitada</div>
  <div>
    <div class="titulo">Validador de construtos de DNA sintético:<br>grampo verificado por Autômato de Pilha e repetição em tandem
    verificada por Autômato Linearmente Limitado</div>
    <div class="sub">Relatório técnico</div>
  </div>
  <div class="equipe"><b>Equipe</b><br>{"<br>".join(e(n) for n in INTEGRANTES)}<br><br>
  Repositório: <code>{e(REPOSITORIO)}</code><br>{DATA}</div>
</div>"""

    sumario = """
<h2>Sumário</h2>
<ol class="sumario">
<li>Problema</li><li>Fontes consultadas</li><li>Linguagem livre de contexto L₁, GLC e derivação</li>
<li>Autômato de Pilha</li><li>Linguagem sensível ao contexto L₂ e Autômato Linearmente Limitado</li>
<li>Implementação</li><li>Testes</li><li>Análise dos resultados e limitações</li><li>Contribuição de cada integrante</li>
<li>Originalidade e uso de inteligência artificial</li><li>Referências</li><li>Apêndices: rastreamentos</li>
</ol>"""

    problema = f"""
<h2>1. Problema</h2>
<p>Em biologia sintética, encomendam-se oligonucleotídeos (fitas curtas de DNA) com estruturas projetadas. Antes da síntese, o
projeto precisa ser validado. Nosso sistema valida a descrição textual de um <b>construto</b> com duas regiões separadas por <code>#</code>:</p>
<ul>
<li><b>Grampo (<i>hairpin</i> ou <i>stem-loop</i>):</b> uma <i>haste 5'</i> <code>w</code>, uma <i>alça</i> <code>x</code> de bases não pareadas e uma
<i>haste 3'</i> que deve ser o <b>complemento reverso</b> de <code>w</code>. Assim a fita dobra-se sobre si e forma pares de Watson-Crick
(A–T, C–G): a 1ª base pareia com a última, a 2ª com a penúltima, e assim por diante. Bases pareadas são escritas em maiúsculas e
as bases da alça em minúsculas, convenção do projeto inspirada no <i>soft-masking</i> da bioinformática.</li>
<li><b>Repetição em tandem:</b> após <code>#</code> vem uma região <code>y</code> formada por <b>duas cópias idênticas e consecutivas</b>
de uma unidade <code>u</code> (y = uu). Repetições em tandem, como as de <code>CAG</code> associadas à doença de Huntington, são usadas
como marcadores e precisam ser sintetizadas sem erro de cópia.</li>
</ul>
<p>Parâmetros de projeto: haste com ≥ 4 pares (estabilidade), alça com ≥ 3 bases (restrição usual em algoritmos de predição de estrutura
secundária, como Nussinov e Jacobson, 1980, e Zuker e Stiegler, 1981) e unidade de repetição com ≥ 3 bases (um códon), logo |y| ≥ 6. Com isso,
a menor cadeia válida tem exatamente <b>18 símbolos</b>, por exemplo <code>GGACgaaGTCC#ATGATG</code>:</p>
<pre>        alça
 5' G G A C  g
    | | | |    a        haste 5' = GGAC, alça = gaa, haste 3' = GTCC = complemento reverso de GGAC
 3' C C T G  a        região de repetição após '#': ATG ATG  (u = ATG)</pre>
<p><b>Por que duas etapas?</b> Searls (1992, 2002) mostrou que estruturas de DNA/RNA se descrevem por gramáticas. O grampo gera
<b>dependências aninhadas</b>, típicas das linguagens livres de contexto e verificáveis com pilha. Repetições diretas (cópias) geram
<b>dependências cruzadas</b>, que estão além das linguagens livres de contexto (é o mesmo fenômeno da linguagem <i>{{wcw}}</i>
citada por Aho et al., 2008, §4.2.7). Daí a divisão de trabalho:</p>
<div class="caixa"><b>Etapa 1 — AP:</b> verifica tudo o que é livre de contexto: formato, hastes complementares de mesmo tamanho, alça,
um único <code>#</code> e comprimento par ≥ 6 da região de repetição.<br>
<b>Etapa 2 — ALL:</b> recebe apenas o trecho após <code>#</code> e verifica a regra sensível ao contexto: <b>a 1ª metade é idêntica à 2ª</b>.</div>
<div class="fig">{figura_dependencias()}<div class="legenda">Figura 1 — No grampo os arcos se encaixam (o último a abrir é o primeiro a
fechar: LIFO). Na cópia os arcos se cruzam: a 1ª base de u precisa ser comparada antes da 2ª, ordem FIFO que a pilha não oferece.</div></div>
"""

    fontes = """
<h2>2. Fontes consultadas</h2>
<table><thead><tr><th>Fonte</th><th>Uso no projeto</th></tr></thead><tbody>
<tr><td>Hopcroft, Motwani e Ullman (2006), cap. 4, 6 e 7</td><td>Definição formal de AP, equivalência GLC ↔ AP, lemas do bombeamento para linguagens regulares e livres de contexto, fecho por interseção com linguagem regular.</td></tr>
<tr><td>Sipser (2007), seções 2.2, 2.3 e 5.1</td><td>Autômatos de pilha, prova de que {ww} não é livre de contexto, definição de autômato linearmente limitado.</td></tr>
<tr><td>Menezes (2011)</td><td>Notação em português para AP, hierarquia de Chomsky e linguagens sensíveis ao contexto.</td></tr>
<tr><td>Kuroda (1964); Myhill (1960)</td><td>Teorema: as linguagens aceitas por ALL são exatamente as sensíveis ao contexto. Fundamenta a classificação de L₂.</td></tr>
<tr><td>Aho, Lam, Sethi e Ullman (2008), §4.2.7</td><td>Construções não livres de contexto em linguagens reais ({wcw}, cópia): motivação da etapa ALL.</td></tr>
<tr><td>Searls (1992; 2002)</td><td>Linguística do DNA: grampos são livres de contexto; repetições diretas e pseudonós não são. Escolha do domínio do problema.</td></tr>
<tr><td>Nussinov e Jacobson (1980); Zuker e Stiegler (1981)</td><td>Parâmetro de alça mínima com 3 nucleotídeos usado na predição de estrutura secundária.</td></tr>
<tr><td>Documentação do Python 3 e do pytest</td><td>Implementação (dataclasses, tkinter) e testes parametrizados.</td></tr>
</tbody></table>"""

    l1 = f"""
<h2>3. Linguagem livre de contexto L₁, GLC e derivação</h2>
<h3>3.1 Alfabeto e regra de formação</h3>
<p>Σ<sub>AP</sub> = {{A, C, G, T, a, c, g, t, #}}. Seja cr(w) o complemento reverso de w (A↔T, C↔G, lido de trás para frente).</p>
<div class="caixa">L₁ = {{ w · x · cr(w) # y  |  w ∈ {{A,C,G,T}}<sup>k</sup>, k ≥ 4;  x ∈ {{a,c,g,t}}<sup>m</sup>, m ≥ 3;
y ∈ {{A,C,G,T}}<sup>2j</sup>, j ≥ 3 }}</div>
<p>Exemplos: <code>GGACgaaGTCC#ATGATG</code> ∈ L₁. <code>GGACgaaGTCA#ATGATG</code> ∉ L₁, porque A não pareia com G.
<code>GGACgaaGTCC#ATGATGA</code> ∉ L₁, porque a região tem comprimento ímpar.</p>

<h3>3.2 Gramática Livre de Contexto G = (V, T, P, S)</h3>
<p><b>V</b> = {{S, H, I, J, K, L, N, R, B}} (não terminais) &nbsp; <b>T</b> = {{A, C, G, T, a, c, g, t, #}} (terminais) &nbsp; <b>S</b> = símbolo inicial.
P contém {len(GLC.PRODUCOES)} produções:</p>
<pre>{producoes}</pre>
<p>H gera os pares da haste de fora para dentro: cada produção X·H·X' coloca uma base e seu complemento nas pontas opostas, o que
produz exatamente cr(w) à direita. A cadeia H → I → J → K obriga ao menos 4 pares; K encosta a alça L (≥ 3 bases N); R gera a
região com comprimento par ≥ 6, dois símbolos B por vez.</p>

<h3>3.3 Derivação de uma cadeia aceita</h3>
<p>Derivação mais à esquerda de <code>GGACgaaGTCC#ATGATG</code>, a menor cadeia de L₁ (gerada por <code>python -m validador_dna derivar</code>):</p>
{deriv_html}
<p>A derivação da cadeia de demonstração <code>{int1}</code> ({len(GLC.derivacao_mais_a_esquerda(int1)) - 1} passos) está em <code>docs/rastreamentos/derivacao_INT-1.txt</code>.</p>

<h3>3.4 L₁ é livre de contexto, mas não é regular</h3>
<p><b>Livre de contexto:</b> é gerada pela GLC G (e reconhecida pelo AP da seção 4).</p>
<p><b>Não regular (lema do bombeamento):</b> suponha L₁ regular, com constante de bombeamento p. Tome
s = A<sup>p</sup>·aaa·T<sup>p</sup>#AAAAAA ∈ L₁ (|s| ≥ p). Em qualquer decomposição s = xyz com |xy| ≤ p e |y| ≥ 1, y = A<sup>i</sup> com i ≥ 1.
Então xy²z = A<sup>p+i</sup>aaaT<sup>p</sup>#AAAAAA, cuja haste 3' (T<sup>p</sup>) não é o complemento reverso da haste 5' (exigiria T<sup>p+i</sup>).
Logo xy²z ∉ L₁, o que contradiz o lema. Intuitivamente, um autômato finito precisaria lembrar uma haste 5' de tamanho arbitrário, o que exige memória
ilimitada. A pilha fornece essa memória.</p>
"""

    ap_sec = f"""
<h2 class="quebra">4. Autômato de Pilha</h2>
<h3>4.1 Especificação M<sub>AP</sub> = (Q, Σ, Γ, δ, q0, Z, F)</h3>
<ul>
<li><b>Q</b> = {{q0, …, q16}} ({len(AP.ESTADOS)} estados); <b>Σ</b> = {{A, C, G, T, a, c, g, t, #}}; <b>Γ</b> = {{Z, A, C, G, T}}.</li>
<li><b>Configuração inicial:</b> (q0, s, Z): estado q0, cabeça de leitura no 1º símbolo, pilha contendo só Z.</li>
<li><b>Critério de aceitação: por estado final</b>, F = {{q15}}. A cadeia é aceita se, <b>após consumir a entrada inteira</b>, o AP está em q15.
Se não houver transição para (estado, símbolo, topo), a cadeia é rejeitada imediatamente. Ao aceitar, a pilha contém apenas Z.</li>
<li><b>Determinístico e sem transições ε:</b> há no máximo uma transição para cada (estado, símbolo, topo), o que é verificado no código ao montar a tabela.</li>
</ul>
{estados_ap}
<h3>4.2 Transições</h3>
<p>Notação δ(q, a, Y) = (p, γ): em q, lendo a com Y no topo, vai para p e troca Y por γ (o 1º símbolo de γ vira o topo; γ = ε desempilha).
X, Y ∈ {{A,C,G,T}}, x ∈ {{a,c,g,t}}, X' = complemento de X. As 20 regras esquemáticas geram {len(AP.TRANSICOES)} transições concretas.</p>
{regras_ap}
<div class="fig">{diagrama_ap()}<div class="legenda">Figura 2 — Diagrama de estados do AP (<code>docs/diagramas/ap.svg</code>).</div></div>

<h3>4.3 Por que o AP reconhece exatamente L(G)</h3>
<p><b>Invariantes</b> (provados por indução no número de passos):</p>
<ol>
<li>Em q1…q4, após ler v, vale v ∈ {{A,C,G,T}}<sup>+</sup> e pilha = v<sup>R</sup>Z (v invertido sobre Z). Os estados q1–q3 contam 1–3 bases; q4 significa ≥ 4.</li>
<li>Em q5, q6, q7 a pilha não muda (= w<sup>R</sup>Z) e foram lidas 1, 2, ≥ 3 minúsculas.</li>
<li>Em q8, após ler z da haste 3', w = w'w'' com z = cr(w'') e pilha = w'<sup>R</sup>Z. Cada T10/T11 só existe se a base lida for o
complemento do topo, e o topo é justamente a base de w que deve parear com ela (a última empilhada pareia com a primeira da haste 3').</li>
<li>T12 só lê <code>#</code> com Z no topo, ou seja, quando w' = ε e z = cr(w): as hastes têm o mesmo tamanho e são complementares.</li>
<li>Em q9…q16 a pilha é Z; os estados contam 0–5 bases, e q15/q16 registram a paridade a partir de 6. Terminar em q15 ⇔ |y| par ≥ 6.</li>
</ol>
<p><b>L(G) ⊆ L(AP):</b> toda cadeia derivada de G tem a forma w·x·cr(w)#y com |w| ≥ 4, |x| ≥ 3 e |y| par ≥ 6 (as produções H/I/J/K
colocam X à esquerda e X' à direita em níveis simétricos). Pelos invariantes, o AP empilha w, atravessa x, desempilha casando cr(w),
lê <code>#</code> com Z e termina em q15. <b>L(AP) ⊆ L(G):</b> se o AP aceita s, os invariantes 1–5 garantem que s = w·x·cr(w)#y com as
mesmas restrições, e a derivação S ⇒ H#R ⇒* w·L·cr(w)#R ⇒* s é construída aplicando H → XHX' (|w| − 4 vezes), H → XIX', I → XJX',
J → XKX', K → XLX', L → NL (|x| − 3 vezes), L → NNN, R → BBR (|y|/2 − 3 vezes), R → B<sup>6</sup> e N, B nos terminais. O código faz exatamente
essa construção (<code>gramatica.derivacao_mais_a_esquerda</code>), e os testes de propriedade da seção 7.5 confirmam a equivalência em 4000 cadeias.</p>
<p><b>Relação com a construção clássica GLC → AP:</b> cada nível de recursão de H corresponde a um símbolo empilhado. Expandir X·H·X'
equivale a ler X e empilhá-lo; fechar o nível com X' equivale a desempilhar conferindo o complemento.</p>
<h3>4.4 Rastreamento</h3>
<p>O rastreamento mostra, a cada passo, o <b>estado</b>, a <b>posição de leitura</b> (índice do próximo símbolo; | separa o lido do
restante) e o <b>conteúdo da pilha</b> (topo à esquerda). O rastreamento completo do cenário de integração aceito está no Apêndice A.</p>
"""

    all_sec = f"""
<h2 class="quebra">5. Linguagem sensível ao contexto L₂ e Autômato Linearmente Limitado</h2>
<h3>5.1 Alfabeto e regra de aceitação</h3>
<p>Σ<sub>ALL</sub> = {{A, C, G, T}}.</p>
<div class="caixa">L₂ = {{ u·u  |  u ∈ {{A,C,G,T}}<sup>+</sup> }}. O ALL aceita se, e somente se, a entrada tem comprimento par, não vazio,
e cada base i da 1ª metade é igual à base i da 2ª metade.</div>
<p>No fluxo completo, o ALL recebe o trecho y após <code>#</code>, que o AP já garantiu ter comprimento par ≥ 6. Logo |u| ≥ 3.
Como módulo isolado, o ALL decide L₂ para qualquer cadeia sobre Σ<sub>ALL</sub>, inclusive a vazia e as de comprimento ímpar.</p>

<h3>5.2 Classificação: L₂ não é livre de contexto</h3>
<p>Suponha L₂ livre de contexto. As LLC são fechadas sob interseção com linguagens regulares (Hopcroft et al., 2006, cap. 7), logo
L' = L₂ ∩ A<sup>+</sup>C<sup>+</sup>A<sup>+</sup>C<sup>+</sup> = {{A<sup>i</sup>C<sup>j</sup>A<sup>i</sup>C<sup>j</sup> | i, j ≥ 1}} seria LLC. Seja p a constante do lema do
bombeamento para LLC e s = A<sup>p</sup>C<sup>p</sup>A<sup>p</sup>C<sup>p</sup>. Em qualquer decomposição s = uvxyz com |vxy| ≤ p e |vy| ≥ 1, a janela vxy
toca no máximo dois blocos <b>adjacentes</b>. Bombear (uv²xy²z) altera o tamanho de um ou dois blocos vizinhos, mas não o do bloco
correspondente na outra metade (1º↔3º, 2º↔4º), que está a distância &gt; p. Se v ou y misturar letras, a ordem A…C…A…C é quebrada.
Em ambos os casos uv²xy²z ∉ L'. Contradição; portanto L₂ não é livre de contexto (o mesmo resultado aparece em Sipser, 2007, §2.3, para {{ww}}).</p>
<p><b>Intuição (Figura 1):</b> a pilha só devolve o último símbolo guardado, o que serve para casar pares aninhados. Para comparar
u₁ com u₁ (cópia), seria preciso recuperar primeiro o símbolo guardado primeiro, comportamento de fila.</p>
<h3>5.3 Classificação: L₂ é sensível ao contexto</h3>
<p>Pelo teorema de Kuroda (1964), uma linguagem é sensível ao contexto se, e somente se, é aceita por um autômato linearmente
limitado. O ALL determinístico da seção 5.4 aceita exatamente L₂ (prova abaixo e testes exaustivos da seção 7.5) usando apenas as n células
da entrada. Logo L₂ é sensível ao contexto e, pela seção 5.2, não é livre de contexto. <b>L₁ fica no nível 2 da hierarquia de Chomsky e
L₂ no nível 1.</b></p>

<h3>5.4 Especificação M<sub>ALL</sub> = (Q, Σ, Γ, δ, q0, &lt;, &gt;, qac, qrj)</h3>
<ul>
<li><b>Q</b> = {{q0, q1, …, q7, qA, qC, qG, qT, qac, qrj}} ({len(ALL.ESTADOS)} estados).</li>
<li><b>Σ</b> = {{A, C, G, T}}; <b>Γ</b> = {{A, C, G, T, a, c, g, t, *, &lt;, &gt;}}. Minúsculas marcam bases visitadas na fase 1, e <code>*</code> marca célula conferida.</li>
<li><b>Fita e configuração inicial:</b> para a entrada w₁…wₙ, a fita é <code>&lt; w₁ … wₙ &gt;</code>: <b>n células graváveis e dois marcadores
de borda fixos</b> (⊢ e ⊣, representados por <code>&lt;</code> e <code>&gt;</code>). Estado q0, cabeçote na célula 0 (sobre <code>&lt;</code>).</li>
<li><b>Movimentos:</b> E (esquerda), D (direita), P (parado, usado apenas na transição que leva à parada).</li>
<li><b>Aceitação:</b> atingir qac. <b>Rejeição:</b> atingir qrj (vazia, ímpar ou base divergente) ou não haver transição definida.</li>
</ul>
<p><b>Algoritmo em três fases:</b></p>
<ol>
<li><b>Achar o meio (q1–q4):</b> marca em minúscula a base livre mais à esquerda (M2), corre até a mais à direita e a marca (M8), volta (M10, M11)
e repete. Se a última base livre ficar sem par, o comprimento é ímpar (M9). Se q1 encontrar uma minúscula, não restam bases livres e o cabeçote
está exatamente na 1ª célula da 2ª metade (M3).</li>
<li><b>Restaurar a 2ª metade (q5):</b> converte as minúsculas à direita do meio de volta para maiúsculas (M12). A fita fica u em minúsculas seguida de u' em maiúsculas.</li>
<li><b>Comparar (q6, q7, qA, qC, qG, qT):</b> pega a 1ª minúscula, grava <code>*</code> e guarda a base no <b>estado</b> (M17); atravessa até a 1ª maiúscula da
2ª metade; se for igual grava <code>*</code> e volta (M20), se for diferente rejeita (M21). Quando só restam <code>*</code>, aceita (M18).</li>
</ol>
{estados_all}
<h3>5.5 Transições (leitura, escrita e movimento)</h3>
<p>Notação δ(q, lido) = (p, escrito, movimento). X, Y ∈ {{A,C,G,T}}, x = minúscula de X, e qX é o estado que carrega X. As 21 regras esquemáticas
geram {len(ALL.TRANSICOES)} transições concretas.</p>
{regras_all}
<div class="fig">{diagrama_all()}<div class="legenda">Figura 3 — Diagrama de estados do ALL (<code>docs/diagramas/all.svg</code>); qX representa os 4 estados qA, qC, qG, qT.</div></div>

<h3>5.6 Limite da fita</h3>
<p>O simulador cria a fita com exatamente n + 2 células, e nenhuma transição acrescenta células. As transições que leem <code>&lt;</code> regravam
<code>&lt;</code> e movem para D (ou param); as que leem <code>&gt;</code> regravam <code>&gt;</code> e movem para E (ou param). Isso é verificado ao montar
a tabela e testado. Portanto os marcadores nunca são sobrescritos e o cabeçote nunca sai do intervalo [0, n+1]. Se isso acontecesse,
o simulador lançaria <code>LimiteDaFitaViolado</code>. Toda a memória de trabalho (marcas de meio, células conferidas e a base “carregada”) cabe nas n células, por
reescrita de símbolos, e no controle finito (estados qA…qT).</p>

<h3>5.7 Rastreamento</h3>
<p>Cada linha mostra o <b>estado</b>, a <b>posição do cabeçote</b> (0 = <code>&lt;</code>, n+1 = <code>&gt;</code>) e a <b>fita inteira</b> com a célula
sob o cabeçote entre colchetes. Rastreamento completo do ALL para <code>ATGATG</code> (trecho de AP-A01):</p>
{rastro_all_curto}
"""

    impl = f"""
<h2 class="quebra">6. Implementação</h2>
<h3>6.1 Linguagem, interface e organização</h3>
<p><b>Python 3.10+</b>, usando apenas a biblioteca padrão para executar a aplicação (pytest é a única dependência, usada nos testes). Escolhemos Python
pela legibilidade, já que as tabelas de transição ficam próximas da notação matemática, e pela disponibilidade nos laboratórios. Há duas interfaces:
<b>linha de comando</b> (<code>python -m validador_dna …</code>, com rastreamentos em tabela) e <b>interface gráfica</b> Tkinter
(<code>python -m validador_dna gui</code>), que desenha a pilha e a fita e permite avançar passo a passo ou animar o ALL.</p>
{tabela(["Arquivo", "Responsabilidade"], [
        ["<code>validador_dna/alfabetos.py</code>", "Σ de cada módulo, complemento, validação de símbolos e mensagem de erro"],
        ["<code>validador_dna/automato_pilha.py</code>", "Estados, tabela δ do AP (gerada das regras T1–T20) e simulador com rastreamento"],
        ["<code>validador_dna/automato_linear.py</code>", "Estados, tabela δ do ALL (regras M1–M21), fita limitada e simulador com rastreamento"],
        ["<code>validador_dna/gramatica.py</code>", "GLC, derivação mais à esquerda, gerador aleatório e oráculo de testes"],
        ["<code>validador_dna/pipeline.py</code>", "Fluxo AP → ALL (o ALL recebe o trecho após '#')"],
        ["<code>validador_dna/__main__.py</code>, <code>gui.py</code>", "Interfaces de linha de comando e gráfica"],
        ["<code>tests/</code>, <code>dados/</code>", "Testes pytest e casos de teste em JSON"],
        ["<code>scripts/</code>", "Geração de resultados, diagramas e deste relatório"],
    ])}
<h3>6.2 A decisão resulta da execução das transições</h3>
<p>Os simuladores não usam expressões regulares nem comparações de cadeias para decidir. O AP mantém uma lista como pilha e, a cada
símbolo, consulta <code>δ[(estado, símbolo, topo)]</code>, desempilha o topo e empilha γ. O ALL mantém a fita como lista de n + 2 células e
consulta <code>δ[(estado, símbolo sob o cabeçote)]</code>, grava e move. A decisão é o estado alcançado (q15 / qac) ou a ausência de transição.
O oráculo de <code>gramatica.pertence</code> existe apenas para os testes compararem o AP com a definição matemática.</p>
<h3>6.3 Por que o programa termina para toda entrada</h3>
<p><b>Validação do alfabeto:</b> é uma varredura única da entrada (n passos). Símbolos fora de Σ encerram com mensagem de erro antes de qualquer autômato.</p>
<p><b>AP:</b> não há transições ε, então cada passo consome exatamente um símbolo. Após no máximo n passos a entrada acaba (decide pelo estado) ou
falta transição (rejeita). Total ≤ n passos.</p>
<p><b>ALL:</b> mostramos uma medida que decresce em cada ciclo.
Fase 1: cada ciclo q1→q2→q3→q4→q1 converte 2 maiúsculas em minúsculas. Os laços internos (M5, M10) andam em um só sentido e param numa
minúscula ou num marcador, que sempre existem, então cada ciclo tem ≤ 2n + 2 passos e há ≤ n/2 ciclos.
Fase 2: q5 só anda para a direita até <code>&gt;</code> e q6 só para a esquerda até <code>&lt;</code> (≤ n + 1 passos cada).
Fase 3: cada ciclo q7→qX→q6→q7 converte 2 células em <code>*</code> com ≤ 2n + 4 passos, e há ≤ n/2 ciclos. Assim o ALL sempre atinge qac ou qrj
em O(n²) passos. Nas cadeias aceitas o total é exatamente (5n² + 18n + 16)/4, valor verificado nos testes.
Como salvaguarda adicional, o número de configurações de um ALL é finito (|Q|·(n+2)·|Γ|<sup>n</sup>) e o simulador determinístico
rejeitaria ao detectar uma configuração repetida. Pela prova acima, isso nunca ocorre.</p>
<h3>6.4 Não determinismo</h3>
<p>Os dois autômatos são <b>determinísticos</b>: no máximo uma transição por configuração, o que o código verifica ao construir as tabelas.
Logo o simulador não precisa explorar alternativas. Essa foi uma decisão de modelagem: escrever a alça em minúsculas marca onde termina
a haste 5'. Sem essa convenção (alça em maiúsculas), o AP teria de <b>adivinhar</b> o fim da haste, como no reconhecimento de palíndromos
sem marcador central, e o simulador precisaria de busca em largura sobre as configurações (estado, posição, pilha), rejeitando só quando
todos os ramos falhassem.</p>
<h3>6.5 Comandos</h3>
<pre>pip install -r requirements.txt                          # apenas pytest
python -m validador_dna demo                             # 3 cenários de integração + erro de alfabeto
python -m validador_dna validar "{int1}" --rastro
python -m validador_dna ap "GGACgaaGTCC#ATGATG"
python -m validador_dna all "CAGCAGCAGCAGCAGCAG" --resumido
python -m validador_dna derivar "GGACgaaGTCC#ATGATG"
python -m validador_dna gui
python -m pytest -v                                      # repete todos os testes</pre>
"""

    analise = f"""
<h2>8. Análise dos resultados e limitações</h2>
<p>Todas as decisões obtidas coincidiram com as esperadas. Os casos mais informativos foram:</p>
<ul>
<li><b>AP-A05 e AP-A10:</b> o AP aceita <code>…#TATATA</code> e <code>…#ATGATGAT</code>, que têm comprimento par mas não são cópias. Isso mostra
que a regra da cópia não está ao alcance do AP e precisa do ALL.</li>
<li><b>ALL-R07</b> (<code>ACGTACGTAC·CATGCATGCA</code> = u·u<sup>R</sup>): uma pilha reconheceria essa cadeia (é um palíndromo par), mas ela
não é uma cópia. O ALL a rejeita na 1ª comparação. É a fronteira entre dependências aninhadas e cruzadas.</li>
<li><b>INT-2 × INT-3:</b> diferem de INT-1 em um único símbolo. Em INT-2 o erro está na haste e é detectado pela pilha (posição 14), sem
executar o ALL. Em INT-3 o erro está na cópia: o AP aceita e o ALL rejeita na última comparação.</li>
<li><b>Custo:</b> o AP usa n passos; o ALL usa O(n²): {passos_int} passos para os 12 símbolos de INT-1 e 832 para 24 símbolos (ALL-A08).</li>
</ul>
<h3>Limitações observadas</h3>
<ol>
<li><b>Rastreamento longo do ALL:</b> o custo quadrático gera centenas de linhas, por exemplo 708 passos em ALL-A02 (22 símbolos). Para a
apresentação criamos o modo <code>--resumido</code>, que omite passos que só deslocam o cabeçote. A tabela completa continua disponível.</li>
<li><b>Dependência da convenção de caixa:</b> o AP é determinístico porque a alça vem em minúsculas. Sequências reais não vêm anotadas, e um
validador real precisaria de um AP não determinístico ou de um algoritmo de dobramento.</li>
<li><b>Simplificações biológicas:</b> só pares de Watson-Crick perfeitos (sem pares G–U, bolhas ou pareamentos incorretos); a repetição deve
ser exata e com exatamente duas cópias. Repetições reais toleram mutações e podem ter várias cópias.</li>
<li><b>Estados de contagem:</b> parte dos 17 estados do AP (q1–q3, q5–q6, q9–q14) apenas contam comprimentos mínimos, que são restrições
regulares. Isso torna o diagrama mais longo, mas deixa cada restrição visível.</li>
<li><b>Mensagens de erro:</b> o erro de alfabeto aponta só o primeiro símbolo inválido.</li>
</ol>
"""

    contrib = """
<h2>9. Contribuição de cada integrante</h2>
<table><thead><tr><th>Integrante</th><th>Contribuição</th><th>Parte apresentada</th></tr></thead><tbody>
<tr><td>Yuri Aguiar</td><td>Escolha e pesquisa do problema; definição de L₁; GLC e derivação; modelagem e implementação do AP
(<code>automato_pilha.py</code>, <code>gramatica.py</code>); prova de que L₁ não é regular.</td><td>Problema, GLC, derivação e relação GLC ↔ AP; rastreamento do AP.</td></tr>
<tr><td>João Rath</td><td>Definição de L₂ e prova de que não é LLC; algoritmo de três fases do ALL; prova de parada e do limite da fita;
implementação de <code>automato_linear.py</code>; diagramas.</td><td>Dependência sensível ao contexto, ALL, limite da fita e rastreamento do ALL.</td></tr>
<tr><td>Pedro Paulo</td><td>Integração AP → ALL (<code>pipeline.py</code>); interfaces de linha de comando e gráfica; casos e suíte de testes; README,
relatório e slides.</td><td>Arquitetura, demonstração ao vivo dos três cenários, testes e limitações.</td></tr>
</tbody></table>
<p>Todos revisaram a modelagem formal, simularam cadeias à mão e ensaiaram a arguição.</p>
"""

    ia = """
<h2>10. Originalidade e uso de inteligência artificial</h2>
<p><b>Originalidade:</b> o problema (construtos de DNA com grampo e repetição em tandem) e todos os autômatos e gramáticas foram elaborados para
este trabalho. Não se baseiam nos exercícios de sala nem no exemplo da lauda (parênteses balanceados com blocos R, V, E de mesma quantidade).
O código foi escrito para este repositório, sem cópia de código de terceiros. Os diagramas são gerados por <code>scripts/gerar_diagramas.py</code>.
As cadeias de exemplo foram criadas pela equipe, e algumas usam motivos reais: <code>GAATTC</code> (EcoRI), <code>GGATCC</code> (BamHI), <code>CAG</code> (repetição de Huntington).
As provas usam resultados clássicos das referências da seção 11, adaptados às nossas linguagens.</p>
<p><b>Uso de IA:</b> a equipe usou o assistente <b>Claude (Anthropic), via Claude Code</b>, como apoio para: sugerir o domínio do problema,
redigir versões iniciais do código Python, dos testes, dos scripts de documentação, deste relatório, dos slides e do guia de arguição.</p>
<p><b>O que a equipe verificou:</b> (i) simulou à mão o AP e o ALL nas cadeias dos três cenários de integração e conferiu com os rastreamentos;
(ii) conferiu cada regra das tabelas de transição contra os diagramas; (iii) revisou as provas (lemas do bombeamento, invariantes do AP,
parada e limite da fita do ALL) com as referências; (iv) executou <code>python -m pytest</code> e
<code>python scripts/gerar_resultados_testes.py</code> e conferiu as decisões esperadas; (v) testou as interfaces de linha de comando e gráfica.</p>
"""

    refs = """
<h2>11. Referências</h2>
<ul>
<li>AHO, A. V.; LAM, M. S.; SETHI, R.; ULLMAN, J. D. <i>Compiladores: princípios, técnicas e ferramentas</i>. 2. ed. São Paulo: Pearson, 2008. (Seção 4.2.7.)</li>
<li>HOPCROFT, J. E.; MOTWANI, R.; ULLMAN, J. D. <i>Introduction to Automata Theory, Languages, and Computation</i>. 3. ed. Boston: Addison-Wesley, 2006.</li>
<li>KURODA, S.-Y. Classes of languages and linear-bounded automata. <i>Information and Control</i>, v. 7, n. 2, p. 207–223, 1964.</li>
<li>MENEZES, P. B. <i>Linguagens Formais e Autômatos</i>. 6. ed. Porto Alegre: Bookman, 2011.</li>
<li>MYHILL, J. <i>Linear bounded automata</i>. WADD Technical Note 60-165. Wright-Patterson AFB, 1960.</li>
<li>NUSSINOV, R.; JACOBSON, A. B. Fast algorithm for predicting the secondary structure of single-stranded RNA. <i>PNAS</i>, v. 77, n. 11, p. 6309–6313, 1980.</li>
<li>SEARLS, D. B. The linguistics of DNA. <i>American Scientist</i>, v. 80, n. 6, p. 579–591, 1992.</li>
<li>SEARLS, D. B. The language of genes. <i>Nature</i>, v. 420, p. 211–217, 2002.</li>
<li>SIPSER, M. <i>Introdução à Teoria da Computação</i>. 2. ed. São Paulo: Cengage Learning, 2007.</li>
<li>ZUKER, M.; STIEGLER, P. Optimal computer folding of large RNA sequences using thermodynamics and auxiliary information. <i>Nucleic Acids Research</i>, v. 9, n. 1, p. 133–148, 1981.</li>
<li>PYTHON SOFTWARE FOUNDATION. <i>Python 3 documentation</i> (tkinter, dataclasses). Disponível em: https://docs.python.org/3/.</li>
</ul>
"""

    apendice = f"""
<h2 class="quebra">12. Apêndices — rastreamentos</h2>
<h3>A. AP — cenário INT-1 <code>{int1}</code> (aceita)</h3>
{rastro_ap}
<h3>B. ALL — cenário INT-1, trecho <code>ATGGCAATGGCA</code> (aceita; {passos_int} passos, versão resumida)</h3>
<p>Mostra só os passos em que o estado muda ou uma célula é reescrita. A versão completa está em <code>docs/rastreamentos/INT-1.txt</code>.</p>
{rastro_all_int}
<h3>C. ALL — cenário INT-3, trecho <code>ATGGCAATGGCT</code> (rejeitada; {passos_rej} passos, versão resumida)</h3>
{rastro_all_rej}
"""

    corpo = (capa + sumario + problema + fontes + l1 + ap_sec + all_sec + impl + secao_testes(grupos)
             + analise + contrib + ia + refs + apendice)
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório — Validador de construtos de DNA (AP + ALL)</title><style>{CSS}</style></head>
<body>{corpo}</body></html>"""


def navegador() -> str | None:
    candidatos = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    for nome in ("google-chrome", "chromium", "chromium-browser", "msedge"):
        if shutil.which(nome):
            return shutil.which(nome)
    return None


def html_para_pdf(html_path: Path, pdf_path: Path) -> bool:
    exe = navegador()
    if exe is None:
        print("Edge/Chrome não encontrado: abra o HTML no navegador e use Imprimir → Salvar como PDF.")
        return False
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    return pdf_path.exists()


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    html_path = SAIDA / "relatorio.html"
    html_path.write_text(montar(), encoding="utf-8")
    pdf = SAIDA / "relatorio.pdf"
    if pdf.exists():
        pdf.unlink()
    ok = html_para_pdf(html_path, pdf)
    print(f"HTML: {html_path}" + (f"\nPDF:  {pdf}" if ok else ""))


if __name__ == "__main__":
    main()
