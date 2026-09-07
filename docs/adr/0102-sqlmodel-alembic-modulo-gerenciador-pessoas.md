# ADR-0102: SQLModel + Alembic para o Módulo Gerenciador de Pessoas

- Status: Aceita
- Data: 2026-09-07

## Contexto

O módulo Gerenciador de Pessoas ([ADR-0101](./0101-gerenciador-pessoas-schema-importacao-app-aj.md)) vai expor CRUD livre pelo dashboard (usuário cria/edita/apaga pessoas, grupos, veículos, QRB diretamente pela UI) — cenário onde SQL manual escrito à mão em cada handler é risco real de erro/inconsistência. Separadamente, o sistema precisa poder **recriar o schema do banco** caso o arquivo seja corrompido ou apagado — isso exige um histórico de migração versionado, independente de qual (ou nenhum) ORM seja usado.

O motor de leitura de RELINTs (`SqliteRepo`, `SqlitePersonRepo`) usa `sqlite3` puro, é read-heavy, já tem otimizações de performance documentadas (ADR-0071) e não tem CRUD livre de usuário — não há motivo para reescrevê-lo. A fronteira de Ports & Adapters já existente (`IDatabaseRepo`, `IPersonRepo` como interfaces separadas dos adapters concretos) permite que cada módulo escolha sua própria tecnologia de persistência sem vazar a decisão para o domínio.

Opções de ORM avaliadas: SQLAlchemy 2.0 (ORM clássico), SQLModel, Peewee, Tortoise ORM, Prisma (client Python), Django ORM standalone.

## Decisão

Adotar **SQLModel** para os models/tabelas do módulo Gerenciador de Pessoas (`pessoas` ampliada, `pessoa_fotos`, `qrb`, `grupos_criminosos`, `grupos_familiares`, `veiculos`, e os 4 pivots N:N) e **Alembic** para o histórico de migração versionado dessas tabelas.

Motivos:
- SQLModel é construído sobre SQLAlchemy + Pydantic — uma única classe serve como schema de validação da API (FastAPI) e como tabela do banco, evitando duplicar `PessoaORM`/`Pessoa` como duas classes que precisariam ser mantidas em sincronia manualmente.
- Alembic funciona igualmente bem com metadata do SQLModel (mesmo mecanismo por baixo ser SQLAlchemy) — dá o histórico de migração necessário para recriar o schema do zero a qualquer momento.
- O motor de RELINT (`SqliteRepo`/`SqlitePersonRepo`, `sqlite3` puro) **não é alterado** por esta decisão — permanece como está, atrás da mesma interface.

Descartadas:
- **SQLAlchemy 2.0 clássico**: mais maduro e com suporte "oficial" mais direto ao Alembic, mas exige 2 classes por entidade (modelo ORM + schema Pydantic) e uma função de conversão manual entre elas — mais boilerplate sem ganho que justifique, dado o tamanho do módulo.
- **Peewee**: sem integração com FastAPI/Pydantic (conversão 100% manual), ferramenta de migração (`peewee-migrate`) menos madura que Alembic.
- **Tortoise ORM**: async-first; a stack de banco do projeto é síncrona hoje, adotá-lo exigiria reescrever as rotas de Pessoas para `async`/`await` sem necessidade real de I/O concorrente num SQLite local.
- **Prisma (client Python)**: schema definido em DSL própria (`.prisma`), depende de um binário/gerador Node por trás — foge do "tudo Python" do backend.
- **Django ORM standalone**: maduro, mas trazer o Django inteiro só pelo ORM é peso desproporcional.

Risco aceito conscientemente: SQLModel é mantido essencialmente por uma pessoa (autor do FastAPI, que divide atenção entre vários projetos) — ritmo de correção de bugs e paridade com features novas do SQLAlchemy 2.0 é mais lento que o SQLAlchemy puro. Aceito em troca de menos duplicação de classes.

## Consequências

CRUD do módulo Gerenciador de Pessoas passa a usar queries parametrizadas e validadas automaticamente via SQLModel, e o schema dessas tabelas passa a ter histórico de migração real (Alembic), permitindo recriação completa em caso de corrupção/exclusão do arquivo `.db`. Consultas muito complexas (joins elaborados entre as entidades novas) podem exigir cair para a sintaxe "crua" do SQLAlchemy dentro do mesmo arquivo — aceitável dado que o módulo é majoritariamente CRUD simples, não leitura analítica pesada como o motor de RELINT.

**Recriar o schema (via Alembic) não substitui backup de dados** — uma rotina de backup/restore do arquivo `.db` (ex: `sqlite3 .backup` periódico) continua como item em aberto, não coberto por esta ADR.

---
