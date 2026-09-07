# ADR-0054: Tradução do Esquema do Banco de Dados SQLite e do Sistema para Português (pt-BR)

- Status: Aceita
- Data: não registrada

## Contexto
O projeto adota português do Brasil como língua de comunicação com o usuário e para o banco de dados (ver diretrizes de linguagem do projeto), mas o schema original do SQLite havia sido criado com nomes de tabela e coluna em inglês, criando uma inconsistência entre o domínio do negócio (em pt-BR) e sua persistência.

## Decisão
Decisão de migrar todas as tabelas (`relints`, `homicidio_detalhes`, `pessoas`, `relint_participantes`, `relint_imagens`) e colunas do banco relacional SQLite nativo (`data/relints.db`) para o Português (pt-BR). A infraestrutura de banco executa migração automática em `_init_db()` usando `ALTER TABLE RENAME COLUMN` para preservar dados existentes sem perdas. O arquivo de especificação `schema.dbml` foi atualizado com todas as tabelas de especialidades polimórficas (Tráfico, Roubos e Furtos) em Português. As rotas REST e modelos Pydantic utilizam aliases (`validation_alias` e `serialization_alias`) para garantir total retrocompatibilidade e comunicação limpa com o frontend SPA e com a suíte de testes unitários Pytest.

## Consequências
Alinha o banco de dados ao idioma de domínio do projeto, facilitando a leitura direta do schema por analistas brasileiros. A migração automática via `ALTER TABLE RENAME COLUMN` preserva dados existentes, mas o uso de aliases Pydantic para retrocompatibilidade adiciona uma camada extra de mapeamento entre nomes em inglês (código/API legada) e português (banco) que precisa ser mantida.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
