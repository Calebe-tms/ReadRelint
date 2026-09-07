# ADR-0055: Centralização dos Campos de Registro Policial na Tabela Principal (`relints`)

- Status: Aceita
- Data: não registrada

## Contexto
Os campos de registro policial (número, órgão e ano) inicialmente só existiam na tabela de detalhes de homicídio, mas na prática qualquer tipo de ocorrência pode ter um registro policial formal associado, tornando esses campos genéricos e não exclusivos de uma especialidade.

## Decisão
Mover os campos `numero_registro`, `orgao_registro` e `ano_registro` das tabelas de especialidades para a tabela base principal `relints` (e entidade de domínio `IncidentReport`). Isso elimina redundância no esquema relacional e permite que qualquer ocorrência (independente da especialidade) possua um registro policial associado. O adapter `SqliteRepo` executa migração automática dos valores pré-existentes de `homicidio_detalhes` para `relints`.

## Consequências
Elimina redundância de schema e disponibiliza o registro policial para todas as especialidades de forma uniforme. Exige uma migração de dados cuidadosa para não perder os valores já gravados na tabela de detalhes de homicídio.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
