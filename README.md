# Validador de construtos de DNA: Autômato de Pilha + Autômato Linearmente Limitado

Trabalho prático de **Linguagens Formais e Autômatos**: reconhecimento de linguagens com pilha e fita limitada.

**Equipe:** João Rath · Pedro Paulo · Yuri Aguiar

O programa valida, em duas etapas, a descrição de um construto de DNA sintético no formato
`haste5' · alça · haste3' # região-de-repetição`:

| Etapa | Modelo | O que verifica | Classe da linguagem |
|---|---|---|---|
| 1 | **Autômato de Pilha** (17 estados, determinístico, aceitação por estado final) | *Grampo*: a haste 3' é o **complemento reverso** da haste 5' (A↔T, C↔G), com haste ≥ 4, alça ≥ 3 (em minúsculas), um único `#` e região de comprimento par ≥ 6 | Livre de contexto, não regular |
| 2 | **Autômato Linearmente Limitado** (14 estados, determinístico) | *Repetição em tandem*: o trecho após `#` é **uu**, duas cópias idênticas | Sensível ao contexto, não livre de contexto |

```
GATCCgaaaGGATC#ATGGCAATGGCA   → AP aceita, ALL aceita      (aceita)
GATCCgaaaGGATG#ATGGCAATGGCA   → AP rejeita (G não pareia com G); ALL não executa
GATCCgaaaGGATC#ATGGCAATGGCT   → AP aceita, ALL rejeita (última base da 2ª cópia difere)
```

O grampo cria **dependências aninhadas** (a 1ª base pareia com a última), que uma pilha resolve. A cópia cria
**dependências cruzadas** (a 1ª base de u é comparada com a 1ª base da 2ª cópia), que exigem a fita.

## Requisitos e instalação

- Python **3.10 ou superior**. A aplicação usa só a biblioteca padrão; a interface gráfica usa `tkinter`, que já vem no Python do Windows e do macOS.
  No Linux, instale o pacote `python3-tk` se necessário.
- `pytest` para os testes.

```bash
git clone <url-do-repositorio>
cd av2-automatos
python -m venv .venv            # opcional
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Executar

```bash
# três cenários de integração + teste com símbolo fora do alfabeto (com rastreamentos)
python -m validador_dna demo
python -m validador_dna demo --resumido          # rastreamento do ALL sem os passos de simples deslocamento

# fluxo completo AP -> ALL
python -m validador_dna validar "GATCCgaaaGGATC#ATGGCAATGGCA" --rastro

# cada módulo separadamente (sempre mostra o rastreamento)
python -m validador_dna ap  "GGACgaaGTCC#ATGATG"
python -m validador_dna all "CAGCAGCAGCAGCAGCAG" --resumido

# derivação mais à esquerda na GLC
python -m validador_dna derivar "GGACgaaGTCC#ATGATG"

# especificação formal (GLC, AP e ALL: estados, alfabetos, transições)
python -m validador_dna especificacao

# modo interativo no terminal e interface gráfica
python -m validador_dna interativo
python -m validador_dna gui
```

No PowerShell, use aspas em volta da cadeia por causa do `#`.
Códigos de saída: `0` = aceita, `1` = rejeitada, `2` = símbolo fora do alfabeto.

### Rastreamentos
- **AP:** passo, estado, posição de leitura (`lido|restante`), conteúdo da pilha (topo à esquerda) e transição aplicada.
- **ALL:** passo, estado, posição do cabeçote e fita inteira `< … >` com a célula sob o cabeçote entre `[ ]`. A fita tem exatamente
  n células graváveis + 2 marcadores fixos.

## Repetir os testes

```bash
python -m pytest -v                          # 120 testes: módulos, integração, erros, propriedades
python scripts/gerar_resultados_testes.py    # tabela entrada/esperado/obtido/regra → docs/resultados_testes.md e .csv
```

Os casos ficam em [`dados/`](dados/):

| Arquivo | Conteúdo |
|---|---|
| `casos_ap.json` | 10 aceitas + 14 rejeitadas pelo AP (inclui casos-limite: menor cadeia aceita com 18 símbolos, vazia, 17 símbolos) |
| `casos_all.json` | 10 aceitas + 12 rejeitadas pelo ALL (inclui `AA`, vazia, `A`, `AC`) |
| `casos_integracao.json` | os 3 cenários obrigatórios do fluxo completo |
| `casos_erro.json` | símbolos fora do alfabeto (`N`, `U`, minúsculas no ALL, espaço) e a mensagem esperada |

Os testes de propriedade comparam o AP com a definição matemática de L₁ em 4000 cadeias. Comparam também o ALL com `s == uu` em todas as
5461 cadeias de até 6 símbolos e verificam em todos os passos que o cabeçote não sai da fita.

## Gerar a documentação

```bash
python scripts/gerar_diagramas.py      # docs/diagramas/ap.svg e all.svg
python scripts/gerar_relatorio.py      # docs/relatorio/relatorio.html e relatorio.pdf (usa Edge/Chrome em modo headless)
python scripts/gerar_slides.py         # docs/slides/slides.html e slides.pdf
```

No Windows, para pôr a turma na capa do relatório: `set TURMA=CC6MA` (cmd) ou `$env:TURMA="CC6MA"` (PowerShell), e rode o script de novo.
O endereço do repositório vai na variável `REPO_URL`.

## Estrutura

```
validador_dna/
  alfabetos.py        Σ dos módulos, complemento de bases, erro de símbolo fora do alfabeto
  automato_pilha.py   AP: estados, regras T1–T20, tabela δ e simulador com rastreamento
  automato_linear.py  ALL: estados, regras M1–M21, fita limitada e simulador com rastreamento
  gramatica.py        GLC, derivação mais à esquerda, gerador aleatório, oráculo de testes
  pipeline.py         fluxo AP → ALL
  formatacao.py       tabelas de rastreamento e especificações
  __main__.py         linha de comando
  gui.py              interface gráfica (Tkinter)
dados/                casos de teste (JSON)
tests/                testes pytest
scripts/              geração de resultados, diagramas e relatório
docs/
  relatorio/          relatório técnico (HTML + PDF)
  slides/             slides da apresentação (HTML + PDF, 16:9)
  diagramas/          diagramas de estados (SVG)
  rastreamentos/      rastreamentos completos dos cenários de integração e derivações
  resultados_testes.* tabela de resultados dos testes
```

## Modelos (resumo)

**GLC** `G = (V, T, P, S)`, com V = {S,H,I,J,K,L,N,R,B} e T = {A,C,G,T,a,c,g,t,#}:

```
S → H # R
H → A H T | C H G | G H C | T H A | A I T | C I G | G I C | T I A
I → A J T | C J G | G J C | T J A
J → A K T | C K G | G K C | T K A
K → A L T | C L G | G L C | T L A
L → N L | N N N
N → a | c | g | t
R → B B R | B B B B B B
B → A | C | G | T
```

A especificação completa (estados, transições, provas de classificação, justificativa GLC ↔ AP, parada e limite da fita) está no
[relatório](docs/relatorio/relatorio.pdf) e em `python -m validador_dna especificacao`.

## Originalidade e uso de inteligência artificial

O problema, as gramáticas e os autômatos foram elaborados para este trabalho. Não se baseiam em exercícios de sala nem no exemplo da lauda.
O código foi escrito para este repositório, sem código de terceiros. Os diagramas são gerados por `scripts/gerar_diagramas.py`.
Algumas cadeias usam motivos biológicos reais: `GAATTC` (EcoRI), `GGATCC` (BamHI), repetição `CAG`.

**Uso de IA:** a equipe usou o assistente **Claude (Anthropic), via Claude Code**, como apoio para sugerir o domínio do problema e redigir
versões iniciais do código, dos testes, dos scripts, do relatório, dos slides e do guia de arguição.
**A equipe verificou:** simulações à mão do AP e do ALL nos cenários de integração, conferidas com os rastreamentos; as tabelas de transição
contra os diagramas; as provas (bombeamento, invariantes, parada, limite da fita) contra as referências; a execução de `python -m pytest` e
das interfaces.

## Referências principais

- Hopcroft, Motwani, Ullman. *Introduction to Automata Theory, Languages, and Computation*, 3ª ed., 2006.
- Sipser. *Introdução à Teoria da Computação*, 2ª ed., Cengage, 2007.
- Menezes. *Linguagens Formais e Autômatos*, 6ª ed., Bookman, 2011.
- Kuroda (1964). Classes of languages and linear-bounded automata. *Information and Control* 7(2).
- Searls (1992). The linguistics of DNA. *American Scientist* 80(6).
- Aho, Lam, Sethi, Ullman. *Compiladores*, 2ª ed., 2008, §4.2.7.
