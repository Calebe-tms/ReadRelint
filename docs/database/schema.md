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

Tabela de domínio independente de pessoas, compartilhada entre todos os RELINTs em que um mesmo indivíduo aparece (permitindo dossiês e cruzamento de vínculos). Campos: `chave_pessoa` (identificador único de deduplicação), `nome`, `alcunha`, `documento`, `foto_path`, `antecedentes`.

O campo `dados_aj` (`JSON`) guarda dados esparsos que só existem para alguns indivíduos, oriundos do App-AJ ou de RELINTs mais complexos — ex.: situação prisional, presídio, cela, crimes, companheiro(a), tatuagens, redes sociais. Usar JSON aqui em vez de novas colunas evita que o schema relacional cresça com campos majoritariamente vazios.

## `relint_participantes` — Junção RELINT ↔ Pessoa

Tabela de junção N:N entre `relints` e `pessoas`, com atributos próprios da participação: `tipo_participacao` (classificação tripla oficial — `Vítima`, `Testemunha` ou `Autor/Suspeito`) e `caminho_foto` (foto específica daquele indivíduo naquele RELINT, quando vinculada manualmente pela curadoria).

## `relint_imagens` — Anexos e Fotos

Guarda todas as imagens recortadas de um PDF (`caminho_arquivo`, `legenda`), relacionadas 1:N com `relints`. Diferente de `relint_participantes.caminho_foto` (foto vinculada a uma pessoa específica), esta tabela é a galeria geral de anexos do documento.

## Entidades de Inteligência Compartilhada (App-AJ)

Conjunto de tabelas que estende o modelo de inteligência para além dos RELINTs individuais, permitindo cruzar pessoas com grupos e veículos:

- `grupos_criminosos`: facções/grupos criminosos (`nome`, `qrb`, `observacao`).
- `grupos_familiares`: núcleos familiares de interesse (`nome`, `qrb`, `observacao`).
- `veiculos`: veículos de interesse (`placa` única, `marca`, `cor`, `localizacao`, `proprietario`, `foto_path`, `observacao`).

E as tabelas pivot N:N que ligam pessoas a essas entidades:

- `pessoa_grupo_criminoso` (`pessoa_id`, `grupo_criminoso_id`, `funcao`).
- `pessoa_grupo_familiar` (`pessoa_id`, `grupo_familiar_id`).
- `pessoa_veiculo` (`pessoa_id`, `veiculo_id`, `tipo_posse`).

## Referências

- Desenho completo em DBML: [`schema.dbml`](./schema.dbml)
- Repositórios de acesso a dados: `backend/database/sqlite_repo.py` (RELINTs) e `backend/database/sqlite_person_repo.py` (pessoas)
