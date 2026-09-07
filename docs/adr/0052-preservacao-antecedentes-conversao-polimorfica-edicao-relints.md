# ADR-0052: Preservação de Antecedentes e Conversão Polimórfica na Edição de RELINTs (`PUT /api/v1/relints/{id}`)

- Status: Aceita
- Data: não registrada

## Contexto
Um formulário de edição que reenvia o payload completo do participante corre o risco de sobrescrever com valores vazios campos que não foram tocados pelo usuário (como foto ou antecedentes já vinculados), além de a edição poder mudar a classificação de um RELINT para uma especialidade polimórfica (ADR-022) que exige tabela própria.

## Decisão
Ao editar um RELINT via API/Web, o sistema cruza os participantes enviados com os existentes para preservar `photo_path` e `background` caso não sejam editados explicitamente. Além disso, se o `bm_group` for alterado para "Homicídio", a entidade é convertida dinamicamente para `HomicideReport` para garantir que a tabela `homicide_details` seja atualizada e mantida em sincronia.

## Consequências
Evita perda acidental de dados de participantes durante edições parciais e mantém a consistência entre a especialidade classificada e a tabela de detalhes correspondente. Aumenta a complexidade do endpoint de PUT, que agora precisa cruzar estado existente com o payload recebido e decidir sobre conversão polimórfica em tempo de execução.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
