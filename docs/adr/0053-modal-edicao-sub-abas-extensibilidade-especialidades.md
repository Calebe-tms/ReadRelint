# ADR-0053: Modal de Edição em Sub-Abas & Extensibilidade de Especialidades (`#edit-relint-modal`)

- Status: Aceita
- Data: não registrada

## Contexto
Um único formulário plano para editar todos os campos de um RELINT (gerais, geográficos, de especialidade, participantes e transcrição) ficaria sobrecarregado visualmente, especialmente considerando que campos de especialidade variam conforme o `bm_group` do boletim.

## Decisão
Implementação de modal interativo em 5 sub-abas no frontend SPA Web (Geral, Localização, Especialidade, Participantes e Transcrição) integrado à rota REST `PUT /api/v1/relints/{id}`. O modal oferece formulário dinâmico que alterna campos por especialidade (Homicídios: registro, DP, ano, tipo de fato, motivação) e estrutura extensível para futuras especialidades, além de permitir gerenciar participantes (adicionar/remover/editar). Todas as edições humanas registram automaticamente `user_edited = True`, imunizando os registros contra sobrescritas em re-processamentos automáticos.

## Consequências
Organiza a edição de forma modular e escalável para novas especialidades futuras, além de integrar a marcação `user_edited` (reforçando a curadoria humana da ADR-006) diretamente no fluxo de edição. Aumenta a complexidade do frontend, que precisa manter estado sincronizado entre 5 sub-abas de um mesmo formulário.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
