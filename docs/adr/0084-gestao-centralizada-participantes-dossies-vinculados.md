# ADR-0084: Gestão Centralizada de Participantes e Dossiês Vinculados

- Status: Aceita
- Data: não registrada

## Contexto
Com a migração do dashboard para SvelteKit, a experiência de gestão de participantes construída anteriormente na SPA legada (ADR-061/ADR-063) precisava ser reconstruída na nova stack, mantendo o padrão master-detail já validado e acrescentando edição direta dos dados cadastrais.

## Decisão
Implementação da rota `/participantes` com layout Master-Detail (30% lista com filtros de reincidência / 70% dossiê completo, galeria de fotos e histórico de ocorrências) e integração de modal de dossiê interativo dentro dos boletins RELINT (`TabParticipants.svelte`), permitindo edição direta de dados cadastrais e antecedentes persistidos no SQLite via `PUT /api/v1/participants/{person_id}`.

## Consequências
Consolida no SvelteKit a mesma qualidade de gestão investigativa de participantes já alcançada na SPA anterior, agora com edição de dados cadastrais integrada diretamente ao dossiê. Cria um novo endpoint de escrita (`PUT /api/v1/participants/{person_id}`) que precisa ser mantido em conjunto com as regras de preservação de dados já existentes para edição de RELINTs (ADR-052).

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
