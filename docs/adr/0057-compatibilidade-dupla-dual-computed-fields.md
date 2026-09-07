# ADR-0057: Compatibilidade Dupla (Dual Computed Fields) nos Schemas REST & Views JS

- Status: Aceita
- Data: não registrada

## Contexto
Após a tradução do schema do banco para pt-BR (ADR-054), partes do frontend SPA já escritas esperando nomes em inglês e a suíte de testes existente ficaram em risco de quebrar caso a API expusesse apenas os novos nomes em português.

## Decisão
Adição de propriedades computadas (`@computed_field`) nos schemas REST `RelintSummaryResponse`, `RelintDetailResponse` e `ParticipantDTO`. O JSON serializado passa a conter simultaneamente as propriedades em Inglês (`source_file`, `subject`, `date_of_fact`, `bm_group`, `summary`, `participants`, etc.) e em Português (`arquivo_origem`, `assunto`, `data_fato`, `grupo_bm`, `resumo`, `participantes`, etc.). Isso solucionou a divergência de exibição no Dashboard SPA mantendo 100% de compatibilidade com a suíte de testes unitários.

## Consequências
Garante compatibilidade retroativa total com código frontend e testes existentes, evitando uma migração disruptiva de uma vez só. O payload JSON fica duplicado (mesmo dado sob duas chaves), aumentando o tamanho da resposta e exigindo decidir, no futuro, quando descontinuar um dos dois conjuntos de nomes.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
