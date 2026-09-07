# Referência da API REST/WebSocket

Todos os endpoints REST são montados com o prefixo `/api/v1`. O servidor FastAPI (`backend/api/app.py`) também serve o frontend SvelteKit compilado (`/`, `/design-system`, `/ds`) e o diretório de mídia (`/media/...`, imagens extraídas dos PDFs).

Endpoint de sistema:
- `GET /api/v1/health` — health-check simples do servidor, retorna `{status, service, version}`.

---

## Router: RELINTs (`backend/api/routers/relints.py`, prefixo `/relints`)

### `GET /api/v1/relints/stats`
Retorna as estatísticas consolidadas do dashboard (KPI Cards) via `repo.get_dashboard_metrics()`, executando agregação SQL em tempo constante (< 5ms).

### `GET /api/v1/relints`
Lista todos os RELINTs, com suporte a busca textual e filtros. Parâmetros de query:
- `search` (opcional): busca textual em assunto, resumo, conteúdo, município e dados de participantes.
- `bm_group` (opcional): filtra por grupo BM (comparação case-insensitive; `"todos"` desativa o filtro).
- `relint_type` (opcional): filtra por tipo de RELINT.
- `municipality` (opcional): filtro por correspondência parcial de município.
- `limit` (opcional): número máximo de registros retornados.
- `offset` (padrão `0`): deslocamento para paginação.

Retorna uma lista de `RelintSummaryResponse` (resumo por registro: id, arquivo de origem, assunto, data/hora do fato, grupo BM, tipo, município, bairro, unidade policial, resumo, método de extração, lista resumida de participantes, contagem de participantes e imagens, flag `user_edited`).

### `GET /api/v1/relints/{report_id}`
Retorna o detalhe completo de um único RELINT (`RelintDetailResponse`), incluindo endereço estruturado e informações de mapa resolvidas em tempo real (`extract_structured_address`, `resolve_report_map_info`), lista completa de imagens normalizadas para URLs `/media/...`, lista completa de participantes, e o bloco de detalhes de especialidade correspondente ao tipo do relatório (`homicide_details`, `drug_trafficking_details`, `establishment_robbery_details`, `residence_robbery_details`, `vehicle_robbery_details`, `pedestrian_robbery_details` ou `vehicle_theft_details` — escolhido via `isinstance()` sobre a entidade polimórfica carregada do banco). Retorna 404 se o RELINT não existir.

### `PUT /api/v1/relints/{report_id}`
Atualiza um RELINT existente e seus detalhes de especialidade. Recebe um `RelintUpdateRequest` (todos os campos opcionais — só os enviados são atualizados). Sempre define `user_edited = true` no registro salvo, imunizando-o contra sobrescritas automáticas em reprocessamentos futuros. Reconstrói a entidade polimórfica correta (`HomicideReport`, `DrugTraffickingReport` etc.) com base no `bm_group` atual ou nos blocos de detalhe enviados no payload, e também permite substituir a lista completa de `participants`. Ao salvar com sucesso, dispara um evento WebSocket `relint_updated` via o `broadcaster` (ver router de Eventos). Retorna o detalhe atualizado (mesmo formato do `GET /{report_id}`).

### Rotas de conveniência para Participantes (montadas neste router)
Para garantir que `/api/v1/participants` também funcione a partir do router de RELINTs, os handlers abaixo delegam diretamente para o router de Participantes:
- `GET /api/v1/relints/participants` — lista de participantes (mesmo contrato de `GET /api/v1/participants`).
- `GET /api/v1/relints/participants/{person_id}` — dossiê de um participante (mesmo contrato de `GET /api/v1/participants/{person_id}`).

---

## Router: Participantes (`backend/api/routers/participants.py`, prefixo `/participants`)

### `GET /api/v1/participants`
Lista consolidada de todos os participantes (pessoas), cada um com contagem de RELINTs vinculados, foto principal e galeria de fotos. Parâmetros de query:
- `search` (opcional): busca por nome, alcunha ou RG/CPF (normalizado, ignorando pontuação).
- `recurrent_only` (padrão `false`): filtra apenas reincidentes (vinculados a mais de 1 RELINT).

Retorna uma lista de `PersonDossierDTO`, ordenada por quantidade de RELINTs vinculados (decrescente). O DTO expõe tanto campos em inglês (`name`, `nickname`, `document`, `background`, `photo_path`, `photos`, `linked_relints_count`, `linked_relints`) quanto aliases computados em português (`nome`, `alcunha`, `documento`, `antecedentes`, `caminho_foto`, `galeria_fotos`, `quantidade_relints`) para compatibilidade com o frontend.

### `GET /api/v1/participants/{person_id}`
Retorna o dossiê detalhado de um único participante (mesmo formato de `PersonDossierDTO`), incluindo a lista completa de RELINTs vinculados com o papel desempenhado em cada um. Busca por `documento` (chave única de `pessoas` desde a eliminação de `chave_pessoa`, ver ADR-0101) ou `id`. Retorna 404 se não encontrado.

### `PUT /api/v1/participants/{person_id}`
Atualiza os dados de identificação e antecedentes de uma pessoa (`name`, `nickname`, `document`, `background` — todos opcionais, só os enviados são alterados). Retorna o dossiê atualizado.

---

## Router: Monitoramento (`backend/api/routers/monitoring.py`, prefixo `/monitoring`)

Expõe o motor de monitoramento de pastas e o estado do Ollama para a interface Web (réplica do painel Desktop).

### `GET /api/v1/monitoring/status`
Retorna o status completo do monitoramento: caminho monitorado, se está ativo, se o modo IA está ligado, arquivo em leitura, contadores de arquivos totais/pulados/processados/descobertos, status de saúde do Ollama (cache TTL de 5s, com bypass quando há processamento IA ativo), contagens agregadas de relatórios (total/IA/regex) e os logs recentes.

### `POST /api/v1/monitoring/browse`
Abre a janela nativa do Windows (`tkinter.filedialog.askdirectory`) no servidor local para o usuário selecionar uma pasta. Ao selecionar, já define o caminho de monitoramento e retorna a contagem de arquivos.

### `POST /api/v1/monitoring/path`
Define o diretório de monitoramento diretamente por caminho de texto (corpo `{"path": "..."}"`), validando que o diretório existe. Retorna 400 se vazio, 404 se não existir.

### `POST /api/v1/monitoring/start`
Inicia (ou retoma) o monitoramento contínuo da pasta selecionada. Retorna 400 se nenhuma pasta foi definida ainda.

### `POST /api/v1/monitoring/stop`
Pausa o monitoramento contínuo.

### `POST /api/v1/monitoring/reset`
Executa reset completo: banco relacional, tabela de pessoas, mídias, e dispara re-leitura de tudo.

### `POST /api/v1/monitoring/reprocess-file`
Remove o registro de um arquivo PDF específico (corpo `{"filename": "..."}"`) e dispara sua re-leitura imediata. Retorna 400 se o nome do arquivo não for informado.

### `POST /api/v1/monitoring/toggle-llm`
Alterna o modo de processamento entre IA (Ollama) e Regex (corpo `{"use_llm": true|false}"`), executando teste de saúde em tempo real.

### `GET /api/v1/monitoring/events` (Server-Sent Events)
Stream SSE (`text/event-stream`) que emite, a cada 1.5s, um snapshot do status de monitoramento (mesmos campos de `GET /status`, sem as contagens agregadas de relatórios). Usado para atualização em tempo real do painel de monitoramento na Web. Observação: este é um canal SSE específico do monitoramento; a reatividade geral do dashboard (novo RELINT criado/atualizado) migrou para WebSocket (ver router de Eventos, ADR-087).

---

## Router: Eventos / WebSocket (`backend/api/routers/events.py`, prefixo `/events`)

### `WS /api/v1/events` (WebSocket bidirecional)
Endpoint WebSocket principal de notificações em tempo real do dashboard. Ao conectar, o servidor:
1. Aceita a conexão e a registra no `EventBroadcaster` (`broadcaster`, singleton do módulo).
2. Envia uma mensagem inicial `{"event": "connected", "data": {"status": "online"}}`.
3. Mantém a conexão viva, recebendo mensagens de texto do cliente (hoje apenas logadas — não há roteamento de comandos do frontend para o backend implementado ainda).

O `EventBroadcaster.broadcast(event_type, data)` é chamado por outras partes do backend (ex.: `PUT /api/v1/relints/{id}` dispara `relint_updated`) para empurrar eventos `{"event": ..., "data": ...}` a todos os clientes WebSocket conectados, de forma thread-safe (usa `asyncio.run_coroutine_threadsafe` quando chamado fora do event loop principal).

### `GET /api/v1/events/test_emit`
Endpoint de depuração: dispara manualmente um evento `relint_created` de teste para todos os listeners conectados.

### `GET /api/v1/events/debug`
Endpoint de depuração: retorna o id do broadcaster, quantidade de listeners conectados e se o event loop está ativo.

---

## Referências

- Entidades e schemas Pydantic de resposta: `backend/api/schemas/relints.py`
- Injeção de dependências (repositórios, controller): `backend/api/dependencies.py`
- Modelo de dados subjacente: [`../database/schema.md`](../database/schema.md)
