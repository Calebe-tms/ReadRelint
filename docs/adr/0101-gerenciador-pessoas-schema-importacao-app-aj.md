# ADR-0101: Gerenciador de Pessoas — Schema de Importação do App-AJ

- Status: Aceita
- Data: 2026-09-07

## Contexto

Um novo módulo ("Gerenciador de Pessoas") vai importar dados de uma planilha externa (Google Sheets, "App-AJ") com 10 abas: `CRIMINOSOS`, `VEICULOS`, `GRUPOS CRIMINOSOS`, `QRB` (locais nomeados), `GRUPOS FAMILIARES`, `VEICULOS_POSSE`, `R_QRB`, `R_GRUPO_FAMILIAR`, `R_GRUPO_CRIMINOSO`. Os vínculos N:N (pessoa↔veículo, pessoa↔local, pessoa↔grupo) são expressos em abas de junção próprias, chaveadas por RG (documento da pessoa) + um ID hash da outra entidade — nunca dentro da própria linha da pessoa.

A tabela `pessoas` hoje em produção só tem `id`, `chave_pessoa`, `nome`, `alcunha`, `documento`, `antecedentes` — a maioria dos campos da planilha (`Situação`, `Presídio`, `Cela`, `Crimes`, `Município`, `Endereço`, `Outras Informações`, `Rede Social`, `Sinais Particulares`, `Tatuagens`, `Companheiro(a)`+RG+Rede Social, 3 fotos) não existe. O `docs/database/schema.dbml` antigo já previa um campo `dados_aj JSON` para esses dados e tabelas `grupos_criminosos`/`grupos_familiares`/`veiculos`+pivots, mas nenhuma delas chegou a ser implementada de fato — são aspiracionais.

As duas abas de vínculo pessoa↔grupo têm dados reais, mas com formatos diferentes entre si: `R_GRUPO_FAMILIAR` tem `ID`, `CRIMINOSO` [RG], `GRUPO FAMILIAR` [hash do grupo] — sem coluna de função. `R_GRUPO_CRIMINOSO` tem `ID`, `Criminoso` [RG], `Grupo Criminoso` [hash], `Função` [texto livre: "Chefe", "Motorista", "Distribuidor" etc., sem enum fechado].

## Decisão

1. **`pessoas.dados_aj` vira um campo JSON livre, chave:valor sem schema fixo** — substitui a ideia de normalizar `Situação`/`Presídio`/`Cela`/`Crimes`/`Tatuagens`/etc. em colunas individuais. Motivo do usuário: são dados que "estão há anos na planilha e quase nunca são usados" — não justificam colunas tipadas nem migração por campo novo. Editado por um endpoint de merge parcial (`PATCH .../dados-aj`) e um componente de UI dedicado (editor de pares chave/valor), permitindo ao usuário adicionar uma chave nova a qualquer momento sem alteração de schema.
2. **`pessoa_fotos` (nova, 1:N)** substitui as 3 colunas fixas `Foto`/`Foto_2`/`Foto_3` da planilha — mesmo padrão já usado por `relint_imagens`.
3. **Novas tabelas `qrb`, `grupos_criminosos`, `grupos_familiares`** ganham uma coluna `chave_externa TEXT UNIQUE` guardando o ID hash da planilha, mantendo `id INTEGER` autoincrement como chave interna — mesmo padrão que `pessoas.chave_pessoa`/`pessoas.id` já usa. Isso deixa a reimportação idempotente (mesmo ID da planilha atualiza a mesma linha) sem misturar tipos de chave estrangeira (`TEXT` vs `INTEGER`) entre tabelas do schema.
4. **Pivots (`pessoa_qrb`, `pessoa_grupo_criminoso`, `pessoa_grupo_familiar`, `pessoa_veiculo`) referenciam o `id` interno de `pessoas`**, nunca o RG bruto — a importação resolve RG → `pessoas.id` (criando a pessoa se ainda não existir) antes de gravar o vínculo. `pessoa_grupo_criminoso` e `pessoa_grupo_familiar` são padronizadas com a mesma coluna `funcao` (texto livre) — a de familiar fica `NULL` na migração inicial (a aba de origem não traz esse dado), preenchível depois via CRUD.
5. **`veiculos.proprietario` continua texto livre.** Cruzar esse texto com `pessoas` fica deliberadamente fora de escopo agora — decisão futura, não implementada nesta ADR.
6. **Colunas de auditoria da planilha (`Data de Atualização`, usuário) não são importadas** — um sistema de auditoria próprio do projeto é trabalho futuro separado.
7. Escolha de ferramenta de ORM/migração para persistir esse schema **não faz parte desta ADR** — decisão em aberto, tratada à parte.

## Correções pós-extração dos dados reais (2026-09-07)

Ao baixar as 9 abas como CSV para preservar os dados antes da perda de acesso à planilha, 2 pontos do desenho acima precisaram de ajuste:

- **`qrb`** tem duas colunas reais não previstas: `Tipo de Local` (ex: "Moradia", "Propriedade Rural ligada ao Tráfico") e `Foto`. Adicionadas como `tipo_local`/`foto`.
- **`pessoa_veiculo`**: a coluna `Posse` da aba `VEICULOS_POSSE` não é um campo descritivo de "tipo de posse" como eu tinha suposto — é o **RG da pessoa**, ou seja, a própria chave de vínculo (`ID`, `Veículo`, `Posse`=RG, `Data`). O campo `tipo_posse` foi removido do schema; `pessoa_veiculo` fica só com `pessoa_id`, `veiculo_id`, `data_posse`.

## Segunda correção: eliminação de `chave_pessoa` (2026-09-07)

O usuário notou que `pessoas.chave_pessoa` e `pessoas.documento` guardavam basicamente o mesmo RG (um limpo/só dígitos, outro com pontuação) — redundante sempre que o documento existe. Decisão: **`chave_pessoa` foi eliminada**, e `documento` passa a ser a própria chave única da tabela (`UNIQUE NOT NULL`), absorvendo o valor normalizado que `chave_pessoa` guardava. Quando não há RG/CPF real (participante extraído de RELINT sem documento identificado), `documento` recebe o nome em minúsculo como chave sintética — mesmo fallback que `chave_pessoa` já fazia.

Isso exigiu blindar os consumidores para não exporem essa chave sintética como se fosse um documento de verdade: `SqlitePersonRepo._build_person_from_row()` e os dois endpoints de `participants.py` agora comparam `documento.lower() == nome.lower()` e, se bater, tratam como "sem documento" (string vazia) em vez de devolver o nome disfarçado de RG. Testado em `tests/modulo_pessoas/test_api_participants.py::test_documento_sintetico_nao_vaza_como_documento_real`.

Nenhuma FK foi afetada — todos os pivots já referenciavam `pessoas.id` (interno), nunca `chave_pessoa`/`documento` diretamente.

**Achado à parte, não corrigido nesta mudança**: `get_participant_dossier()` (`backend/api/routers/participants.py`) não tem `return` no caminho de sucesso — bug pré-existente, não coberto por nenhum teste hoje (só o caminho 404 é testado). Sinalizado, não corrigido, por estar fora do escopo desta mudança.

## Consequências

O schema ganha 5 tabelas novas (`qrb`, `pessoa_fotos`, `pessoa_qrb` — as demais 3 pivots/entidades já existiam só no papel) e `pessoas` ganha a coluna `dados_aj`, sem colunas tipadas extras. Consultas sobre os dados esparsos (ex.: "quantos estão presos?") exigem `json_extract`/`LIKE` em vez de filtro indexado direto — aceitável dado que o próprio usuário caracterizou esses campos como baixo uso.

Ambas as tabelas de vínculo pessoa↔grupo (`R_GRUPO_CRIMINOSO` e `R_GRUPO_FAMILIAR`) têm dados reais na planilha e podem ser migradas com confiança.

---
