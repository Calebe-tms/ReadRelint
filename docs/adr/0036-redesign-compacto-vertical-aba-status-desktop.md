# ADR-0036: Redesign Compacto Vertical e Aba STATUS em 1º Lugar (Desktop UI)

- Status: Aceita
- Data: não registrada

## Contexto
O usuário abre o app desktop primariamente para checar se os serviços (monitoramento, Web, IA) estão saudáveis; deixar essa informação atrás de outras abas obrigava um clique extra sempre que o app era aberto.

## Decisão
Redefinição das dimensões da janela desktop (`520x700`) com alinhamento vertical dos botões de ação e introdução do componente `StatusTab` como primeira aba padrão para visualização imediata da saúde dos serviços ao iniciar o sistema.

## Consequências
O usuário vê imediatamente o status dos serviços ao abrir o app, reduzindo fricção operacional. A janela mais compacta e vertical limita o espaço disponível para conteúdo mais denso em outras abas.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
