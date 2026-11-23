# Resultados dos testes

Gerado por `python scripts/gerar_resultados_testes.py`. **53/53 casos com decisão obtida igual à esperada.**

## Módulo 1 — Autômato de Pilha

| ID | Entrada | n | Esperado | Obtido | Regra verificada | Justificativa do autômato |
|---|---|---|---|---|---|---|
| AP-A01 | `GGACgaaGTCC#ATGATG` | 18 | ACEITA | ACEITA | Caso-limite: menor cadeia aceita (\|w\|=4, alça=3, região=6; 18 símbolos) | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A02 | `GATCCgaaaGGATC#ATGGCAATGGCA` | 27 | ACEITA | ACEITA | Hastes complementares (5 pares), alça 4, região par 12 | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A03 | `CAGTGttcgCACTG#AAGCTTAAGCTT` | 27 | ACEITA | ACEITA | Hastes complementares (5 pares), alça 4, região par 12 | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A04 | `TTGCAGCcttgGCTGCAA#CCGGAACCGGAA` | 31 | ACEITA | ACEITA | Haste longa (7 pares): pilha com 7 bases antes de desempilhar | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A05 | `ACGTACGTaaaACGTACGT#TATATA` | 26 | ACEITA | ACEITA | Haste autocomplementar (palíndromo biológico) e região par 6; o AP não confere cópia | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A06 | `GCGCtttGCGC#GATTACAGATTACA` | 26 | ACEITA | ACEITA | Haste mínima (4 pares) e região par 14 | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A07 | `AATTCCGGgacCCGGAATT#TGCATGCA` | 28 | ACEITA | ACEITA | Haste de 8 pares e região par 8 | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A08 | `CCCCaaaaGGGG#ATGATGATGATG` | 25 | ACEITA | ACEITA | Haste homopolimérica C/G e região par 12 | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A09 | `TGACctgGTCA#ACGTTGACGTTG` | 24 | ACEITA | ACEITA | Haste mínima e região par 12 | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-A10 | `GGACgaaGTCC#ATGATGAT` | 20 | ACEITA | ACEITA | Região par 8 que não é cópia: o AP aceita (regra de cópia é do ALL) | Entrada consumida por completo no estado final q15: hastes complementares de mesmo tamanho, alça ≥ 3 e região de repetição de comprimento par ≥ 6. |
| AP-R01 | `GGACgaaGTCA#ATGATG` | 18 | REJEITA | REJEITA | Pareamento: 4ª base da haste 3' ('A') não é complementar ao topo 'G' | Sem transição: Pareamento inválido: a base 'A' na posição 11 não é complementar ao topo da pilha 'G' (esperado 'C'). |
| AP-R02 | `GGACTgaaAGTC#ATGATG` | 19 | REJEITA | REJEITA | Haste 3' mais curta: '#' lido com base ainda na pilha | Sem transição: Haste 3' mais curta que a haste 5': separador '#' na posição 13 lido com 1 base(s) ainda na pilha (topo 'G'). |
| AP-R03 | `GGACgaaGTCCA#ATGATG` | 19 | REJEITA | REJEITA | Haste 3' mais longa: base lida com apenas Z na pilha | Sem transição: Haste 3' mais longa que a haste 5': a base 'A' na posição 12 encontrou apenas Z no topo da pilha (nenhuma base para parear). |
| AP-R04 | `GGCgaaaGCC#ATGATGAT` | 19 | REJEITA | REJEITA | Haste 5' com só 3 bases (mínimo 4) | Sem transição: Haste 5' incompleta: após 3 base(s) foi lido 'g' na posição 4; a haste 5' exige ao menos 4 bases maiúsculas antes da alça. |
| AP-R05 | `GGACgaGTCC#ATGATGAT` | 19 | REJEITA | REJEITA | Alça com só 2 bases (mínimo 3) | Sem transição: Alça curta: após 2 base(s) não pareada(s) foi lido 'G' na posição 7; a alça exige ao menos 3 bases minúsculas. |
| AP-R06 | `GGACGTCC#ATGATGATGA` | 19 | REJEITA | REJEITA | Sem alça: '#' lido ainda na haste 5' | Sem transição: Separador '#' na posição 9 lido ainda na haste 5': falta a alça (≥ 3 bases minúsculas) e a haste 3'. |
| AP-R07 | `GGACgaaGTCC#ATGATGA` | 19 | REJEITA | REJEITA | Região de repetição com comprimento ímpar (7) | Região de repetição com comprimento ímpar (7): o AP exige comprimento par ≥ 6. |
| AP-R08 | `GGACTgaaaAGTCC#ATGA` | 19 | REJEITA | REJEITA | Região de repetição com menos de 6 bases (4) | Região de repetição com 4 base(s): o mínimo é 6. |
| AP-R09 | `GGACTTCAgaaaTGAAGTCC` | 20 | REJEITA | REJEITA | Sem separador '#' nem região de repetição | Entrada terminou após o grampo: falta o separador '#' e a região de repetição. |
| AP-R10 | `GGACgaaGTCC#ATG#ATGAT` | 21 | REJEITA | REJEITA | Separador '#' repetido | Sem transição: Separador '#' na posição 16 repetido: só pode haver um '#'. |
| AP-R11 | `GGACgaaGTCC#ATGatgATG` | 21 | REJEITA | REJEITA | Minúscula na região de repetição | Sem transição: Base minúscula 'a' na posição 16 na região de repetição: após '#' só são admitidas bases maiúsculas. |
| AP-R12 | `gaaGGACGTCC#ATGATGAT` | 20 | REJEITA | REJEITA | Cadeia começa pela alça (haste 5' vazia) | Sem transição: Haste 5' incompleta: após 0 base(s) foi lido 'g' na posição 1; a haste 5' exige ao menos 4 bases maiúsculas antes da alça. |
| AP-R13 | ε (vazia) | 0 | REJEITA | REJEITA | Caso-limite: entrada vazia | Entrada vazia: o construto exige grampo, '#' e região de repetição. |
| AP-R14 | `GGACgaaGTCC#ATGAT` | 17 | REJEITA | REJEITA | Caso-limite: 17 símbolos, um a menos que o mínimo (região com 5 bases) | Região de repetição com 5 base(s): o mínimo é 6. |

## Módulo 2 — Autômato Linearmente Limitado

| ID | Entrada | n | Esperado | Obtido | Regra verificada | Justificativa do autômato |
|---|---|---|---|---|---|---|
| ALL-A01 | `ATGGCATTGATGGCATTG` | 18 | ACEITA | ACEITA | Cópia exata, \|u\| = 9 (18 símbolos) | Todas as 18 células foram conferidas ('*'): as duas metades são idênticas (u = ATGGCATTG, \|u\| = 9). |
| ALL-A02 | `GATTACAGATAGATTACAGATA` | 22 | ACEITA | ACEITA | Cópia exata, \|u\| = 11 | Todas as 22 células foram conferidas ('*'): as duas metades são idênticas (u = GATTACAGATA, \|u\| = 11). |
| ALL-A03 | `ACGTACGTACACGTACGTAC` | 20 | ACEITA | ACEITA | Cópia exata, \|u\| = 10 | Todas as 20 células foram conferidas ('*'): as duas metades são idênticas (u = ACGTACGTAC, \|u\| = 10). |
| ALL-A04 | `TTTTTTTTTTTTTTTTTT` | 18 | ACEITA | ACEITA | Cópia exata homopolimérica, \|u\| = 9 | Todas as 18 células foram conferidas ('*'): as duas metades são idênticas (u = TTTTTTTTT, \|u\| = 9). |
| ALL-A05 | `CAGCAGCAGCAGCAGCAG` | 18 | ACEITA | ACEITA | Repetição CAG (u = CAGCAGCAG), \|u\| = 9 | Todas as 18 células foram conferidas ('*'): as duas metades são idênticas (u = CAGCAGCAG, \|u\| = 9). |
| ALL-A06 | `AAGCTTGGCCAAGCTTGGCC` | 20 | ACEITA | ACEITA | Cópia exata, \|u\| = 10 | Todas as 20 células foram conferidas ('*'): as duas metades são idênticas (u = AAGCTTGGCC, \|u\| = 10). |
| ALL-A07 | `TGCATGCATGTGCATGCATG` | 20 | ACEITA | ACEITA | Cópia exata, \|u\| = 10 | Todas as 20 células foram conferidas ('*'): as duas metades são idênticas (u = TGCATGCATG, \|u\| = 10). |
| ALL-A08 | `GGATCCGAATTCGGATCCGAATTC` | 24 | ACEITA | ACEITA | Cópia exata (sítios BamHI+EcoRI), \|u\| = 12 | Todas as 24 células foram conferidas ('*'): as duas metades são idênticas (u = GGATCCGAATTC, \|u\| = 12). |
| ALL-A09 | `ACACACACACACACACACAC` | 20 | ACEITA | ACEITA | Cópia exata, \|u\| = 10 | Todas as 20 células foram conferidas ('*'): as duas metades são idênticas (u = ACACACACAC, \|u\| = 10). |
| ALL-A10 | `AA` | 2 | ACEITA | ACEITA | Caso-limite: menor cadeia aceita (\|u\| = 1) | Todas as 2 células foram conferidas ('*'): as duas metades são idênticas (u = A, \|u\| = 1). |
| ALL-R01 | `ATGGCATTGATGGCATTC` | 18 | REJEITA | REJEITA | Última base da 2ª cópia difere | Cópias diferentes (regra M21): a célula 18 (posição 9 da 2ª cópia) contém 'C', mas a base correspondente da 1ª cópia (célula 9) é 'G'. |
| ALL-R02 | `ATGGCATTGATGGCATTGA` | 19 | REJEITA | REJEITA | Comprimento ímpar (19) | Comprimento ímpar, n = 19 (regra M9): a base da célula 10 ficou sem par, logo a fita não se divide em duas metades iguais. |
| ALL-R03 | `CAGCAGCAGCAGCAGCAA` | 18 | REJEITA | REJEITA | Última base difere (CAG…CAA) | Cópias diferentes (regra M21): a célula 18 (posição 9 da 2ª cópia) contém 'A', mas a base correspondente da 1ª cópia (célula 9) é 'G'. |
| ALL-R04 | `GATTACAGATACATTACAGATA` | 22 | REJEITA | REJEITA | 1ª base da 2ª cópia difere | Cópias diferentes (regra M21): a célula 12 (posição 1 da 2ª cópia) contém 'C', mas a base correspondente da 1ª cópia (célula 1) é 'G'. |
| ALL-R05 | `TTTTTTTTTATTTTTTTT` | 18 | REJEITA | REJEITA | 1ª base da 2ª cópia difere (A no lugar de T) | Cópias diferentes (regra M21): a célula 10 (posição 1 da 2ª cópia) contém 'A', mas a base correspondente da 1ª cópia (célula 1) é 'T'. |
| ALL-R06 | `AAAAAAAAACCCCCCCCC` | 18 | REJEITA | REJEITA | Mesma quantidade nas metades, mas conteúdos diferentes (A^9 C^9) | Cópias diferentes (regra M21): a célula 10 (posição 1 da 2ª cópia) contém 'C', mas a base correspondente da 1ª cópia (célula 1) é 'A'. |
| ALL-R07 | `ACGTACGTACCATGCATGCA` | 20 | REJEITA | REJEITA | Segunda metade é o reverso (u u^R): aceitável por pilha, não é cópia | Cópias diferentes (regra M21): a célula 11 (posição 1 da 2ª cópia) contém 'C', mas a base correspondente da 1ª cópia (célula 1) é 'A'. |
| ALL-R08 | `GGATCCGAATTCGAATTCGGATCC` | 24 | REJEITA | REJEITA | Blocos trocados de ordem | Cópias diferentes (regra M21): a célula 14 (posição 2 da 2ª cópia) contém 'A', mas a base correspondente da 1ª cópia (célula 2) é 'G'. |
| ALL-R09 | `ACGTTGCAACGTTGCAAC` | 18 | REJEITA | REJEITA | Comprimento par (18) mas deslocada: u ≠ v | Cópias diferentes (regra M21): a célula 10 (posição 1 da 2ª cópia) contém 'C', mas a base correspondente da 1ª cópia (célula 1) é 'A'. |
| ALL-R10 | ε (vazia) | 0 | REJEITA | REJEITA | Caso-limite: entrada vazia | Entrada vazia (regra M4): a cópia u precisa ser não vazia. |
| ALL-R11 | `A` | 1 | REJEITA | REJEITA | Caso-limite: um único símbolo (ímpar) | Comprimento ímpar, n = 1 (regra M9): a base da célula 1 ficou sem par, logo a fita não se divide em duas metades iguais. |
| ALL-R12 | `AC` | 2 | REJEITA | REJEITA | Caso-limite: comprimento mínimo par com metades diferentes | Cópias diferentes (regra M21): a célula 2 (posição 1 da 2ª cópia) contém 'C', mas a base correspondente da 1ª cópia (célula 1) é 'A'. |

## Fluxo completo (integração AP → ALL)

| ID | Entrada | n | AP esperado/obtido | ALL esperado/obtido | Final esperado | Final obtido | Regra verificada |
|---|---|---|---|---|---|---|---|
| INT-1 | `GATCCgaaaGGATC#ATGGCAATGGCA` | 27 | ACEITA / ACEITA | ACEITA / ACEITA | ACEITA | ACEITA | Aceita pelos dois módulos: grampo válido e região = uu |
| INT-2 | `GATCCgaaaGGATG#ATGGCAATGGCA` | 27 | REJEITA / REJEITA | NÃO EXECUTA / NÃO EXECUTA | REJEITA (AP) | REJEITA (AP) | Rejeitada pelo AP: 'G' na haste 3' não pareia com o topo 'G' |
| INT-3 | `GATCCgaaaGGATC#ATGGCAATGGCT` | 27 | ACEITA / ACEITA | REJEITA / REJEITA | REJEITA (ALL) | REJEITA (ALL) | Aceita pelo AP e rejeitada pelo ALL: última base da 2ª cópia difere |

## Símbolos fora do alfabeto de entrada

| ID | Módulo | Entrada | Esperado | Obtido | Mensagem exibida |
|---|---|---|---|---|---|
| ERR-1 | validar | `GATCCgaaaGGATC#ATGGCNATGGCA` | ERRO | ERRO | ERRO: o símbolo 'N' na posição 21 não pertence ao alfabeto de entrada do validador (AP) Σ = {A, C, G, T, a, c, g, t, #}. A cadeia não foi submetida ao autômato. |
| ERR-2 | ap | `GGACgaaGUCC#ATGATG` | ERRO | ERRO | ERRO: o símbolo 'U' na posição 9 não pertence ao alfabeto de entrada do AP Σ = {A, C, G, T, a, c, g, t, #}. A cadeia não foi submetida ao autômato. |
| ERR-3 | all | `CAGCAGCAGcagCAGCAG` | ERRO | ERRO | ERRO: o símbolo 'c' na posição 10 não pertence ao alfabeto de entrada do ALL Σ = {A, C, G, T}. A cadeia não foi submetida ao autômato. |
| ERR-4 | validar | `GGACgaaGTCC #ATGATG` | ERRO | ERRO | ERRO: o símbolo ' ' (espaço) na posição 12 não pertence ao alfabeto de entrada do validador (AP) Σ = {A, C, G, T, a, c, g, t, #}. A cadeia não foi submetida ao autômato. |
