# Proposta: Módulo Gerenciador de Pessoas (Importação App-AJ + Participantes no Motor LLM)

> Status: **Passos 1 e 2 implementados e executados.** Schema desenhado em [ADR-0101](../adr/0101-gerenciador-pessoas-schema-importacao-app-aj.md), ORM/migração decidido em [ADR-0102](../adr/0102-sqlmodel-alembic-modulo-gerenciador-pessoas.md) (SQLModel + Alembic, só para este módulo — o motor de RELINT não muda). Passos 3 e 4 registrados como próximos passos confirmados (2026-09-07), ainda sem desenho/implementação.

---

## Ordem de dependência

```
1. Estrutura de Pessoas (schema + repos)  ✅ feito
        │
        ├──> 2. Migração dos dados da planilha  ✅ feito
        │
        ├──> 3. Extração de Pessoas no motor LLM do RELINT  — próximo passo
        │
        └──> 4. Dashboard de Gerenciamento de Pessoas (dash + CRUD)  — próximo passo
```

---

## 1. Estrutura de Pessoas — ✅ feito (2026-09-07)

- [x] Models SQLModel em [`backend/database/pessoas_models.py`](../../backend/database/pessoas_models.py): `Pessoa` (mapeia a tabela `pessoas` já existente, com `dados_aj` JSON adicionada), `PessoaFoto`, `Qrb`, `GrupoCriminoso`, `GrupoFamiliar`, `Veiculo`, `PessoaGrupoCriminoso`, `PessoaGrupoFamiliar`, `PessoaQrb`, `PessoaVeiculo`.
- [x] Alembic inicializado na raiz do projeto (`alembic.ini`, `alembic/env.py` — `target_metadata` só com as tabelas deste módulo, o motor de RELINT fica de fora do autogenerate).
- [x] Migration `alembic/versions/7c8217112386_gerenciador_pessoas_schema_inicial.py`: cria as 7 tabelas novas + `ALTER`-equivalente em `pessoas` (via `CREATE TABLE` novo, já que o banco tinha sido apagado — ver decisão abaixo).
- [x] Sessão/engine em [`backend/database/pessoas_repo.py`](../../backend/database/pessoas_repo.py) — sem interface `IPersoasRepo` dedicada ainda (endpoints REST/CRUD ficam para quando o dashboard do módulo for implementado).
- [ ] Endpoints REST de CRUD e o form de `dados_aj` no frontend — **não implementados nesta etapa**, escopo era só schema + dados.

**Decisão sobre o banco**: como o banco (`data/relints.db`) era só de teste e já tinha sido reescrito várias vezes, o usuário optou por apagá-lo e recriar do zero, em vez de fazer um `ALTER TABLE` incremental sobre uma `pessoas` com dados reais. `SqliteRepo`/`SqlitePersonRepo` continuam intocados — eles recriam o lado RELINT normalmente ao instanciar (`_init_db()`), e o Alembic cuida só das tabelas novas + `dados_aj`. Testado: os dois lados coexistem sem conflito no mesmo arquivo (`tests/modulo_pessoas/test_migration_schema.py::test_alembic_upgrade_coexiste_com_bootstrap_legado_do_motor_relint`).

**Como recriar o banco do zero** (documentado por causa do requisito de "recriar caso corrompa/apague"):
```bash
rm data/relints.db data/relints.db-wal data/relints.db-shm   # se existirem
alembic upgrade head                                          # cria o lado Pessoas
python -c "from backend.database.sqlite_repo import SqliteRepo; from pathlib import Path; SqliteRepo(Path('data/relints.db'))"  # cria o lado RELINT
```
(iniciar a aplicação normalmente também recria o lado RELINT — o passo acima só evita precisar subir o app inteiro.)

## 2. Migração dos dados da planilha — ✅ feito (2026-09-07)

Confirmado com o usuário: migração **única** (planilha deixa de ser fonte da verdade). Como o acesso à planilha ia se perder em breve, as 9 abas foram baixadas como CSV (`gviz/tq?tqx=out:csv&sheet=NOME`, acessível sem login por ser "somente ver") para `data/app_aj_import/*.csv` — **pasta coberta pelo `.gitignore` (`data/`), nunca vai pro git**, já que contém dados sensíveis de inteligência policial (nomes, RG, endereços).

Script de importação: [`scripts/import_app_aj_data.py`](../../scripts/import_app_aj_data.py) — lê os CSVs, resolve RG → `pessoas.id`, popula `dados_aj` (JSON livre com as colunas esparsas), `pessoa_fotos`, e todos os pivots. Roda uma vez só (aborta se já houver pessoas no banco). Executado com sucesso:

| Tabela | Linhas importadas |
|---|---|
| `pessoas` | 1693 (1 RG duplicado na planilha, ignorado na 2ª ocorrência) |
| `pessoa_fotos` | 1901 |
| `qrb` | 87 |
| `grupos_criminosos` | 42 |
| `grupos_familiares` | 16 |
| `veiculos` | 14 |
| `pessoa_qrb` | 2 |
| `pessoa_grupo_criminoso` | 366 |
| `pessoa_grupo_familiar` | 58 |
| `pessoa_veiculo` | 2 |

Nenhum RG referenciado nos pivots ficou órfão (0 pessoas-stub criadas) — os dados da planilha eram consistentes entre abas.

**2 correções de schema feitas com dados reais** (ver ADR-0101, seção "Correções pós-extração"): `qrb` ganhou `tipo_local`/`foto` (existiam na planilha, não previstos antes); `pessoa_veiculo` perdeu o campo `tipo_posse` (a coluna `Posse` da planilha é o RG da pessoa, não uma descrição).

**Fotos**: só as de pessoas (`Foto`/`Foto_2`/`Foto_3`, prefixo `Dados Criminosos_Images/`) foram reescritas para `pessoas_Images/` (caminho confirmado com o usuário). **Item em aberto**: fotos de veículos (`VEICULOS_Images/`, `placas_Images/`) e de QRB (`QRB_Images/`) foram importadas com o caminho original da planilha, sem reescrita — nenhum caminho novo foi definido pra elas ainda.

## 3. Configurar extração de Pessoas do RELINT — próximo passo

Item pendente desde a remoção do Pass 1 legado (ver [`eliminacao-pass1-legado.md`](./eliminacao-pass1-legado.md), seção `participants`) — registrado agora como próximo passo confirmado (2026-09-07). Agora que a estrutura de Pessoas existe, a extração pode resolver/persistir a pessoa identificada no texto (buscar por documento/nome em `pessoas`, criar se não existir, vincular ao RELINT). Desenho próprio (quantos passes, onde entra no `LlmPipeline`, como decide criar vs. reaproveitar uma pessoa já cadastrada) fica para quando chegarmos nele — não antecipado aqui.

## 4. Criar dashboard de Gerenciamento de Pessoas (dash + CRUD) — próximo passo

Registrado agora como próximo passo confirmado (2026-09-07): interface no SvelteKit para o usuário gerenciar `pessoas`/`grupos_criminosos`/`grupos_familiares`/`veiculos`/`qrb` diretamente — visualizar, criar, editar e apagar registros (o motivo original de adotar SQLModel, ver ADR-0102). Cobre o item que já estava em aberto desde o passo 1 ("Endpoints REST de CRUD e o form de `dados_aj`"):
- Endpoints REST (`/api/v1/pessoas`, `/api/v1/grupos-criminosos`, `/api/v1/grupos-familiares`, `/api/v1/veiculos`, `/api/v1/qrb`), incluindo `PATCH .../dados-aj` para o merge parcial do JSON livre.
- Componentes Svelte dedicados (`$lib/components/`, conforme regra de modularização do projeto), incluindo o editor de pares chave/valor de `dados_aj`.
- Desenho de telas (lista, detalhe/dossiê, formulário de edição) fica para quando chegarmos nele.

---

## Perguntas respondidas (2026-09-07)

- [x] Migração da planilha é **única** — dados congelados no momento da migração, sem importador recorrente.
- [x] Caminho novo da pasta de fotos de pessoas: `D:\www\ReadRelint\data\pessoas_Images`.
- [x] `R_GRUPO_CRIMINOSO` e `R_GRUPO_FAMILIAR` **têm dados reais as duas** — ambos os pivots migrados com dados reais. Formatos diferentes entre si: `R_GRUPO_CRIMINOSO` tem uma 4ª coluna `Função` (texto livre) que `R_GRUPO_FAMILIAR` não tem — padronizada no schema como `funcao` em ambas, `NULL` para familiar.
- [x] ORM: `sqlmodel` + `alembic`, só para este módulo — motor de RELINT sem mudança (ver ADR-0102).
- [x] Banco de teste apagado e recriado do zero via Alembic + bootstrap do motor de RELINT.

## Itens em aberto (não bloqueiam o que já foi feito)

- [ ] Caminho de destino para fotos de veículos e QRB (só pessoas foi definido).
- [ ] Passo 3 — Configurar extração de Pessoas do RELINT (ver seção acima).
- [ ] Passo 4 — Dashboard de Gerenciamento de Pessoas, dash + CRUD (ver seção acima).
- [ ] **Achado, não corrigido, com ADR própria** ([ADR-0103](../adr/0103-correcao-pendente-return-ausente-dossie-participante.md)): `get_participant_dossier()` (`backend/api/routers/participants.py`) não tem `return` no caminho de sucesso — bug pré-existente à esta sessão, sem cobertura de teste (só o caminho 404 é testado hoje).

## Correção adicional: eliminação de `chave_pessoa` (2026-09-07)

`pessoas.chave_pessoa` foi removida — redundante com `documento` (guardavam o mesmo RG, um limpo e outro com pontuação). `documento` agora é a chave única da tabela; sem RG/CPF real, recebe o nome em minúsculo como chave sintética (mesmo fallback que `chave_pessoa` já fazia). Consumidores (`SqlitePersonRepo`, `participants.py`) foram blindados para não exporem essa chave sintética como se fosse documento real. Banco recriado do zero e dados reimportados com o schema corrigido (mesmas contagens da tabela acima). Detalhes em [ADR-0101](../adr/0101-gerenciador-pessoas-schema-importacao-app-aj.md#segunda-correção-eliminação-de-chave_pessoa-2026-09-07).
