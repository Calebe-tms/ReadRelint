# ADR-0003: Migração de TinyDB para SQLite (Persistência Principal)

- Status: Aceita
- Data: não registrada

## Contexto
TinyDB, por ser um banco de documentos baseado em arquivo JSON, não lida bem com acessos concorrentes (monitoramento de pasta escrevendo enquanto a Web lê) nem oferece queries relacionais eficientes para montar dossiês cruzando RELINTs e pessoas.

## Decisão
Uso de `SQLite` nativo em modo WAL (Write-Ahead Logging) em `data/relints.db`. Motivo: Resiliência contra concorrência e tabelas estruturadas que permitem queries velozes para dossiês.

## Consequências
Ganho de resiliência sob concorrência e de performance em consultas estruturadas. Em troca, o projeto passa a carregar a complexidade de um schema relacional formal e de migrações de banco, algo que o TinyDB dispensava.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
