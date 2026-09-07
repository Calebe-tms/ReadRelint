# ADR-0094: Extração de Especialidades Reformulada em 2 Estágios — Substitui as Rules/Entidades Monolíticas Legadas

- Status: Aceita
- Data: não registrada

## Contexto
Uma auditoria do pipeline ao vivo revelou que a extração de campos de especialidade (motivação, quantidade de droga, modelo de veículo etc.) nunca de fato funcionava na prática: o controller desktop fixava uma regra genérica, então esses campos nunca eram perguntados à LLM, e a camada de persistência gravava apenas valores default do Pydantic em vez de dado real extraído — confirmado ao vivo com um caso onde a tabela de detalhes continha exatamente os defaults do modelo, mesmo quando o próprio nome do arquivo já indicava um dado diferente.

## Decisão
Auditoria revelou que as 7 classes `Rule` especializadas (`HomicideRule`, `DrugTraffickingRule` etc.) e as entidades Pydantic estendidas nunca estavam de fato conectadas ao pipeline ao vivo, pois `desktop/controllers/main_controller.py` usa `self.active_rule = RelintRule()` fixo. Nova arquitetura em 2 estágios: Estágio 1 (Classificação 100% determinística) com `classify_bm_group()` rodando sempre, tanto no caminho IA quanto sem-IA; Estágio 2 (Extração, LLM só quando há campo livre genuíno) com o novo `SpecialtyExtractor`, onde campos binários/enum simples são resolvidos por regex e campos nuançados usam schemas Pydantic minúsculos por especialidade com guardrails de enum fechado e evidência literal. Persistência sem reviver o schema monolítico: `IncidentReport` ganha `model_config = ConfigDict(extra="allow")`. Correção pós-implementação (2026-09-03): as 7 entidades Pydantic especializadas NÃO estão superadas — continuam sendo o caminho vivo de persistência; apenas as 7 classes `Rule` são código morto.

## Consequências
Corrige um bug estrutural onde uma parte inteira da extração (dados de especialidade) simplesmente nunca funcionou, entregando agora extração real com guardrails de evidência literal. A auditoria também evita um erro de limpeza mais grave: as 7 entidades Pydantic de especialidade precisam ser preservadas (são o caminho vivo de persistência e leitura), apenas as classes `Rule` são seguras para remoção — distinção registrada explicitamente para não ser perdida em limpezas futuras.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
