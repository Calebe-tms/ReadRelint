# ADR-0050: Refinamento Avançado da UX Web (Zero Redundâncias)

- Status: Aceita
- Data: não registrada

## Contexto
A interface web acumulou, ao longo de iterações anteriores, controles duplicados e pouco intuitivos (múltiplos botões para a mesma ação, um checkbox genérico para uma ação com estado visual rico), o que aumentava a carga cognitiva do usuário.

## Decisão
Limpeza do Header de componentes redundantes, centralização da alternância do menu lateral em um único botão sobre a linha divisória (`right: -12px`), uso de botão de Status Interativo ao invés de Checkbox para a alternância do Ollama, e melhoria na visibilidade e espessura das animações SVG (remoção do clipping com `overflow: visible` e substituição de textos por spinner de carregamento dinâmico).

## Consequências
Resulta em uma interface mais enxuta e coerente, com um único controle claro por ação. São ajustes cumulativos de polimento que, isoladamente, são pequenos, mas exigem atenção contínua para não reintroduzir redundância.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
