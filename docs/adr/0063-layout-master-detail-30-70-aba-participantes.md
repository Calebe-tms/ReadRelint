# ADR-0063: Layout Master-Detail (30% / 70%) para a Aba Participantes

- Status: Aceita
- Data: não registrada

## Contexto
A visualização inicial de participantes (ADR-061) exibia os dossiês individuais separadamente da lista, exigindo navegação extra; um padrão master-detail sincronizado permite explorar vários indivíduos rapidamente sem perder o contexto da lista.

## Decisão
Reformulação completa da interface SPA `participants_view.js` (`participants_view.js`) e inclusão das regras `.participants-layout` em `main.css` (`main.css`). O layout passou a ser dividido em duas colunas sincronizadas (Master Pane de 30% com busca em tempo real, filtro de reincidentes e cartões compactos; Detail Pane de 70% exibindo o dossiê individual do participante selecionado com sub-abas de Linha do Tempo de RELINTs, Galeria Cruzada com Lightbox e Ficha Civil).

## Consequências
Agiliza a navegação investigativa entre múltiplos participantes, mantendo lista e detalhe sempre visíveis lado a lado. Aumenta a complexidade de estado da SPA, que precisa manter sincronizados seleção na lista e conteúdo do painel de detalhe.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
