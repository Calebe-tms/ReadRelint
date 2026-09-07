# ADR-0017: Remoção da Tabela de Municípios (Cálculo On-The-Fly)

- Status: Aceita
- Data: não registrada

## Contexto
Manter uma tabela separada de municípios exigia mantê-la sincronizada com os dados já presentes em `relints`, criando redundância e risco de dessincronização entre as duas fontes.

## Decisão
Eliminação da tabela `municipalities`. Os índices de criminalidade são agrupados dinamicamente diretamente a partir da tabela principal `relints`.

## Consequências
Simplifica o schema e elimina uma fonte potencial de inconsistência. Em compensação, os agregados por município passam a depender de cálculo em tempo de consulta (SQL de agrupamento) em vez de leitura direta de uma tabela pré-computada.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
