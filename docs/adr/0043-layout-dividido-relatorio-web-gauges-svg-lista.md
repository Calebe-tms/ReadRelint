# ADR-0043: Layout Dividido do Relatório Web (20% Gauges Circulares SVG / 80% Lista com Scroll Adaptativo)

- Status: Aceita
- Data: não registrada

## Contexto
A sub-aba de relatório de leitura (criada na ADR-042) precisava equilibrar indicadores agregados de progresso com a lista detalhada de RELINTs sem forçar o usuário a rolar excessivamente para encontrar um ou outro.

## Decisão
Reestruturação da Sub-Aba 2 em 2 colunas. A coluna esquerda (20%) hospeda 3 medidores circulares SVG verticais (`Total na Pasta`, `Lidos com IA`, `Lidos com Regex`) com preenchimento animado (`stroke-dashoffset`) e porcentagem relativa. A coluna direita (80%) hospeda a lista dos RELINTs com campo de busca/filtros no topo e área de cards contida pela altura da tela (`height: calc(100vh - 200px)`) com barra de rolagem customizada.

## Consequências
Dá visibilidade simultânea e permanente aos indicadores agregados enquanto o usuário navega pela lista detalhada, com scroll contido dentro da área de cards. Fixa uma proporção de layout (20/80) que precisa ser revisitada caso novos indicadores sejam adicionados.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
