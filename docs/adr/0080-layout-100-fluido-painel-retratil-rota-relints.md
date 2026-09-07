# ADR-0080: Layout 100% Fluido e Painel Retrátil na Rota `/relints`

- Status: Aceita
- Data: não registrada

## Contexto
Em monitores de alta resolução, o limite fixo de largura da AppShell deixava grandes áreas de tela ociosas, e a listagem lateral de RELINTs (master pane) ocupava espaço permanente mesmo quando o analista queria se concentrar apenas na leitura do dossiê selecionado.

## Decisão
Remoção do limite estático `max-width: 1440px` no `AppShell.svelte` para preenchimento de telas de alta resolução. Introdução de botão retrátil com transição animada no grid master-detail (`30% / 70%` vs `0px / 100%`) permitindo leitura integral sem ruídos visuais.

## Consequências
Aproveita melhor telas grandes e dá ao usuário controle para maximizar a área de leitura do dossiê quando necessário. A remoção do max-width exige atenção à legibilidade em telas ultra-largas, e o painel retrátil adiciona mais um estado de UI (aberto/fechado) a persistir ou gerenciar.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
