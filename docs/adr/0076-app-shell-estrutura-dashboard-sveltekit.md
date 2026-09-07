# ADR-0076: App Shell & Estrutura do Dashboard SvelteKit

- Status: Aceita
- Data: não registrada

## Contexto
A migração para SvelteKit precisava de uma estrutura de layout mestre coerente, com navegação lateral e cabeçalho compartilhados entre rotas, além de uma rota dedicada para documentar/visualizar o design system usado na aplicação.

## Decisão
Criação do layout mestre `AppShell.svelte` com `Sidebar.svelte` retrátil (64px / 240px) e `Header.svelte` com detecção de rotas ativas. Reorganização das rotas deixando `/` para a Visão Geral de Inteligência e `/design-system` para o catálogo visual do Penpot.

## Consequências
Estabelece a espinha dorsal de navegação do novo dashboard SvelteKit, sobre a qual as demais rotas e páginas são construídas. A sidebar retrátil e a detecção de rota ativa tornam-se contrato de UI que componentes futuros precisam respeitar.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
