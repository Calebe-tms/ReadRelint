# Modelo de Dados (SQLite)

O ReadRelint persiste seus dados em um único banco SQLite (`data/relints.db`), operando em modo **WAL** (Write-Ahead Logging) para suportar leitura/escrita concorrente sem travamentos. O schema é inteiramente em português do Brasil (nomes de tabelas e colunas), seguindo a regra de idioma híbrido do projeto. O desenho completo em formato DBML está em [`schema.dbml`](./schema.dbml).

## `relints` — Entidade Base

Tabela central do sistema: cada linha corresponde a exatamente um documento RELINT processado (**Single Source of Truth** — um PDF = um registro). Contém os campos genéricos de qualquer RELINT, independente da especialidade/tipo de crime:

- Identificação do documento: `arquivo_origem`, `numero_registro`, `orgao_registro`, `ano_registro`.
- Conteúdo interpretado: `assunto`, `fato_principal`, `data_fato`, `hora_fato`, `resumo`, `conteudo` (texto literal extraído do PDF).
- Classificação: `grupo_bm` (categoria de crime, ex.: Homicídio, Prisão por Tráfico, Roubo de Veículo) e `tipo_relint` (ex.: Ocorrência, Disk Denúncia, Resposta a PB).
- Geolocalização: `municipio`, `bairro`, `endereco`, `unidade_policial` (batalhão da Brigada Militar responsável), `coordenadas`, `url_mapa`.
- Rastreabilidade e curadoria: `metodo_extracao` (`"Ollama (IA)"` ou `"Regex (Sem IA)"`, default `'Ollama (IA)'`) e `editado_usuario` (flag booleana — quando `1`, o registro foi editado manualmente por um curador humano e passa a ser imune a sobrescritas automáticas em reprocessamentos).

## Tabelas de Especialidade Polimórficas

Cada uma dessas tabelas guarda os campos adicionais específicos de um tipo de crime, em relação **1:1** com `relints` — a chave primária de cada tabela de detalhe É a própria `relint_id` (chave estrangeira para `relints.id`). Um RELINT só possui uma linha em, no máximo, uma dessas tabelas, conforme seu `grupo_bm`:

| Tabela | Campos específicos |
|---|---|
| `homicidio_detalhes` | `tipo_fato` (Tentado/Consumado), `motivacao` (ex.: Feminicídio, Tráfico, Desavença, Latrocínio) |
| `prisao_trafico_detalhes` | `quantidade_drogas`, `tipo_drogas` |
| `roubo_estabelecimento_detalhes` | `tipo_estabelecimento`, `tipo_local`, `vitimas_lesionadas`, `vitima_refem` |
| `roubo_residencia_detalhes` | `tipo_local`, `vitimas_lesionadas`, `vitima_refem` |
| `roubo_veiculo_detalhes` | `modelo_veiculo`, `placa`, `recuperado`, `local_recuperacao` |
| `roubo_pedestre_detalhes` | `vitimas_lesionadas`, `arma_utilizada`, `objeto_roubado` |
| `furto_veiculo_detalhes` | `modelo_veiculo`, `placa`, `recuperado`, `local_recuperacao` |

Esse desenho preserva um esquema relacional limpo (colunas tipadas por especialidade, em vez de um JSON genérico) enquanto mantém a tabela `relints` enxuta e comum a todos os documentos.

## `pessoas` — Cadastro Unificado de Indivíduos

Tabela de domínio independente de pessoas, compartilhada entre todos os RELINTs em que um mesmo indivíduo aparece (permitindo dossiês e cruzamento de vínculos), e também pelo módulo Gerenciador de Pessoas (importação App-AJ). Campos: `nome`, `alcunha`, `documento`, `antecedentes`.

`documento` é a **chave única** da tabela (`UNIQUE NOT NULL`) — não existe mais uma `chave_pessoa` separada (eliminada por ser redundante, ver [ADR-0101](../adr/0101-gerenciador-pessoas-schema-importacao-app-aj.md)). Quando a pessoa não tem RG/CPF real (ex.: participante extraído de um RELINT sem documento identificado), `documento` guarda o nome em minúsculo como chave sintética. Os consumidores (`SqlitePersonRepo`, endpoints de `participants.py`) tratam esse caso explicitamente para não exibir a chave sintética como se fosse um documento de verdade.

O campo `dados_aj` (`JSON` livre, chave:valor sem schema fixo) guarda dados esparsos que só existem para alguns indivíduos, oriundos do App-AJ — ex.: situação prisional, presídio, cela, crimes, companheiro(a), tatuagens, redes sociais. Usar JSON aqui em vez de novas colunas evita que o schema relacional cresça com campos majoritariamente vazios, e permite ao usuário adicionar uma chave nova a qualquer momento (formulário de pares chave/valor) sem migração de banco.

## `pessoa_fotos` — Galeria de Fotos de Pessoas

Relação **1:N** com `pessoas` (`pessoa_id`, `caminho_arquivo`, `ordem`) — substitui a ideia de colunas fixas `foto`/`foto_2`/`foto_3`, mesmo padrão já usado por `relint_imagens`.

## `relint_participantes` — Junção RELINT ↔ Pessoa

Tabela de junção N:N entre `relints` e `pessoas`, com atributos próprios da participação: `tipo_participacao` (classificação tripla oficial — `Vítima`, `Testemunha` ou `Autor/Suspeito`) e `caminho_foto` (foto específica daquele indivíduo naquele RELINT, quando vinculada manualmente pela curadoria).

## `relint_imagens` — Anexos e Fotos

Guarda todas as imagens recortadas de um PDF (`caminho_arquivo`, `legenda`), relacionadas 1:N com `relints`. Diferente de `relint_participantes.caminho_foto` (foto vinculada a uma pessoa específica), esta tabela é a galeria geral de anexos do documento.

## Entidades de Inteligência Compartilhada — Módulo Gerenciador de Pessoas (App-AJ)

Conjunto de tabelas importadas da planilha externa "App-AJ" ([ADR-0101](../adr/0101-gerenciador-pessoas-schema-importacao-app-aj.md)), que estende o modelo de inteligência para além dos RELINTs individuais, permitindo cruzar pessoas com grupos, veículos e locais nomeados. Gerenciadas via SQLModel + Alembic ([ADR-0102](../adr/0102-sqlmodel-alembic-modulo-gerenciador-pessoas.md)), diferente do restante do schema (SQL puro):

- `qrb`: locais nomeados (`chave_externa`, `nome_local`, `municipio`, `endereco`, `coordenadas`, `tipo_local`, `foto`).
- `grupos_criminosos`: facções/grupos criminosos (`chave_externa`, `nome`, `qrb_id` [FK opcional pra `qrb`], `observacao`).
- `grupos_familiares`: núcleos familiares de interesse (`chave_externa`, `nome`, `qrb_id`, `observacao`).
- `veiculos`: veículos de interesse (`placa` única, `marca`, `cor`, `localizacao`, `proprietario` [texto livre — cruzamento com `pessoas` fica para decisão futura], `foto_path`, `observacao`).

`chave_externa` guarda o ID hash da planilha de origem, mantendo `id` interno autoincrement como chave real do banco — reimportação idempotente sem misturar tipos de FK.

E as tabelas pivot N:N que ligam pessoas a essas entidades (todas referenciam o `id` interno de `pessoas`, nunca `documento` diretamente):

- `pessoa_qrb` (`pessoa_id`, `qrb_id`).
- `pessoa_grupo_criminoso` (`pessoa_id`, `grupo_criminoso_id`, `funcao` — texto livre, ex. "Chefe"/"Distribuidor").
- `pessoa_grupo_familiar` (`pessoa_id`, `grupo_familiar_id`, `funcao` — padronizada com a tabela irmã, mas a planilha de origem não traz esse dado; fica `NULL`).
- `pessoa_veiculo` (`pessoa_id`, `veiculo_id`, `data_posse` — sem campo de "tipo de posse": a coluna `Posse` da planilha de origem é o RG da pessoa, não uma descrição).

## Referências

- Desenho completo em DBML: [`schema.dbml`](./schema.dbml)
- Repositórios de acesso a dados: `backend/database/sqlite_repo.py` (RELINTs, SQL puro) e `backend/database/sqlite_person_repo.py` (dossiê de pessoas, SQL puro) — motor de RELINT.
- `backend/database/pessoas_models.py` / `pessoas_repo.py` (SQLModel) — módulo Gerenciador de Pessoas, migrações em `alembic/versions/`.
