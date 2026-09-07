# ADR-0095: `active_rule` Fixo em `RelintRule()` é Decisão Deliberada, Não Débito Pendente

- Status: Aceita
- Data: não registrada

## Contexto
A nova arquitetura de extração de especialidade em 2 estágios (ADR-094) deixou intacto, deliberadamente, o código que fixa `active_rule` em uma regra genérica — um estado que, visto isoladamente e sem o contexto da ADR-094, parece um bug ou débito técnico esquecido, criando risco real de ser "corrigido" por engano no futuro.

## Decisão
Review pós-implementação da ADR-094 identificou risco de um mantenedor futuro "consertar" `desktop/controllers/main_controller.py:55` (hoje fixo em `RelintRule()`) achando que destravaria as 7 Rules especializadas — reativando acidentalmente o schema monolítico legado em paralelo ao `SpecialtyExtractor`, produzindo extração de especialidade duplicada/conflitante. Documentado explicitamente que a extração de especialidade não depende mais de `rule`/`active_rule`/`get_schema_model()`. Comentário de aviso adicionado diretamente na linha do `main_controller.py`. Adicionalmente, o Pass 1 legado teve os campos já superados (`bm_group`/`address`/`municipality`/`neighborhood`/`police_unit`/`coordinates`/`map_url`) removidos do JSON Schema enviado à LLM (`_strip_superseded_fields` em `ollama_client.py`), reduzindo custo de inferência sem uso algum.

## Consequências
Previne uma regressão específica e já identificada como risco (reativação acidental do schema legado duplicando extração). O comentário de aviso inline e esta ADR funcionam como documentação de intenção arquitetural que precisa sobreviver à rotatividade de mantenedores do projeto; a limpeza do JSON Schema enviado à LLM também reduz custo de inferência ao parar de pedir campos que sempre são descartados.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
