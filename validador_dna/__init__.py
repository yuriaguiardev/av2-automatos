"""Validador de construtos de DNA em duas etapas.

Etapa 1 - Automato de Pilha (AP): verifica a estrutura livre de contexto
          (grampo/hairpin: haste 5' . alca . complemento reverso da haste 5').
Etapa 2 - Automato Linearmente Limitado (ALL): verifica a dependencia
          sensivel ao contexto (repeticao em tandem: a regiao apos '#' e uu).
"""

__version__ = "1.0.0"
