# ADR-0107: Avatares na Aba Participantes via Galeria do Gerenciador de Pessoas

- Status: Aceita
- Data: 2026-09-10

## Contexto

A aba `/participantes` (ADR-0084) já tinha o template pronto para exibir `person.photo_path` como avatar circular (`ParticipantListPane.svelte`, `ParticipantDetailPane.svelte`), mas o campo vinha sempre vazio: a única fonte consultada pela API era `relint_participantes.caminho_foto`, que por desenho (ADR-0020) nunca é preenchida automaticamente — fotos extraídas de um RELINT vão para a galeria geral do boletim, exigindo vinculação manual que nunca foi feita na prática.

Paralelamente, o módulo Gerenciador de Pessoas (ADR-0101/0102) já importou 1901 fotos reais para a tabela `pessoa_fotos` (`pessoa_id`, `caminho_arquivo`, `ordem`), com os arquivos físicos em `data/pessoas_Images/`, mas nenhum endpoint expunha essa galeria.

Durante a implementação, verificado que `pessoa_fotos.caminho_arquivo` guarda dois prefixos de pasta incompatíveis entre si (`pessoas_Images/`, herdado da importação atual, e `CRIMINOSOS_Images/`, herdado do nome original da planilha) — só a pasta `pessoas_Images` existe de fato em disco. Das 1901 linhas, 850 (~45%) referenciam `CRIMINOSOS_Images/...` e o arquivo correspondente **não existe em `pessoas_Images` sob nenhum nome** — são fotos genuinamente ausentes, não um problema de normalização de caminho.

Também foi corrigida nesta mudança a ADR-0103 (bug pré-existente, já registrado como pendente): `get_participant_dossier()` não tinha `return` no caminho de sucesso.

## Decisão

1. **Nova pasta estática `/pessoas_images`** montada em `backend/api/app.py` (`data/pessoas_Images`), com proxy correspondente em `frontend/vite.config.js` para o dev server.
2. **`participants.py` passa a consultar `pessoa_fotos`** (`_fetch_pessoa_photos()`) para montar `photo_path`/`photos` do `PersonDossierDTO`, em `list_participants()` e `get_participant_dossier()`. A consulta resolve pelo **nome do arquivo** (não pelo prefixo de pasta gravado) e só inclui a foto se o arquivo existir de fato em `data/pessoas_Images/` — descarta silenciosamente as ~850 referências a `CRIMINOSOS_Images/` sem arquivo real, evitando ícones de imagem quebrada na UI.
3. `relint_participantes.caminho_foto` continua sendo mesclado como fonte adicional (mantendo compatibilidade com o fluxo da ADR-0061, caso um dia passe a ser preenchido), mas na prática hoje está sempre vazio.
4. `_fetch_pessoa_photos()` verifica a existência da tabela `pessoa_fotos` antes de consultar (`sqlite_master`) — ela é criada pela migração Alembic do módulo Gerenciador de Pessoas (ADR-0102), não pelo schema base de `SqlitePersonRepo`, e pode não existir em bancos novos/de teste.
5. Nenhuma mudança no frontend: os templates já consumiam `photo_path` corretamente.

## Consequências

Fotos reais aparecem na aba Participantes sem nenhuma mudança de UI. Em contrapartida, ~45% das fotos catalogadas em `pessoa_fotos` continuam invisíveis por serem dados de origem realmente ausentes (arquivos nunca entregues/copiados na importação do App-AJ) — corrigir isso exige localizar ou reimportar os arquivos de `CRIMINOSOS_Images/`, fora do escopo desta mudança. A checagem de existência em disco a cada requisição tem custo desprezível no volume atual (~1900 linhas), mas deve ser revisitada se a tabela crescer muito.
