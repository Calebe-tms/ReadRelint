# Estado do Projeto e Backlog

Este documento documenta o que já foi construído, o que está sendo finalizado no momento e o backlog de tarefas futuras do **ReadRelint**.

## 1. O que já foi implementado (Checklist Final)
- [x] **Estrutura de Pastas Simplificada:** Organização limpa na raiz do projeto: `backend/` (contendo api, core, database, engine, task_manager e desktop controllers), `frontend/` (SvelteKit SPA integrado com CSS nativo no `app.css` / `variables.css`), `tests/` e `data/`.
- [x] **Banco de Dados Relacional SQLite (WAL):** SQLite nativo (`relints.db`) com tabelas em Português (`relints`, `pessoas`, `relint_participantes`, `homicidio_detalhes`, `relint_imagens`) e auto-migração de schema.
- [x] **Processamento Híbrido (Ollama Local / Pipeline Determinístico):** Suporte a modo com IA e 100% sem IA via chave/switch no app Desktop e na Web, com monitor de saúde do Ollama em tempo real (heartbeat) e fallback gracioso.
- [x] **Rastreabilidade de Método de Leitura (`extraction_method`):** Gravação explícita de `"Ollama (IA)"` vs `"Regex (Sem IA)"` no banco relacional e exibição de badges coloridos na interface.
- [x] **Aba Web de Monitoramento & IA (`monitoring_view.js`):**
  - Réplica completa do motor de monitoramento do Tkinter na Web em tema **Resend Dark System**.
  - **Layout Split View:** Painel de controle responsivo com terminal de logs em tempo real (SSE Streaming) na coluna da direita.
  - **Medidores Circulares SVG (Apple Watch Style):** Cards individuais com medidores em anel, porcentagem centralizada e animações em tempo real de `stroke-dashoffset`.
  - **Seletor Nativo do Windows (`📁 Procurar Pasta no PC`):** Aciona a janela `filedialog.askdirectory()` do Windows via API local (`POST /api/v1/monitoring/browse`).
  - **Pausa Imediata de Leitura:** Limpeza instantânea da fila de processamento (`processing_queue.queue.clear()`).
  - **Relatório em 2 Colunas:** Gauges SVG verticais na coluna esquerda e lista de RELINTs com scroll adaptativo na coluna direita.
- [x] **Painel de Controle Desktop Nativo em PyQt6 (`painel.py` / `desktop/ui/pyqt_app.py`):** Painel desktop construído em **PyQt6 (Qt6 nativo)** com tema escuro moderno (QSS), alta estabilidade e layout otimizado em **2 Abas Estratégicas**:
  - **Redimensionamento Livre da Janela + Coluna Esquerda com Largura Fixa (`410px`):** O usuário pode redimensionar a janela principal livremente sem que os controles e barras sofram deformações.
  - **Aba 1 (Operação & Leitura em Split View):** Coluna esquerda fixa com seletor nativo de pastas (`QFileDialog`), botão principal de monitoramento, **Barras Lineares Tradicionais de Progresso** (Total da Pasta e Sessão Atual com porcentagens e contadores), **Caixa de Status Estática com Extração Inteligente do Número/Código do RELINT (`RELINT Nº ...` + Tooltip com nome completo)**, **Indicador de Leitura Ativa Estilo Web** (animação contínua a 60 FPS com spinner e marquee animado com `RetainSizeWhenHidden` contra pulos de layout) e card de Ações Rápidas com alternador do Modo IA, botão do Dashboard Web e botão **`⛔ Encerrar Todos os Serviços & Sair`** posicionado estrategicamente abaixo do Dashboard. Coluna direita com **Console de logs com Efeito Typewriter Inteligente (Auto-Speed)**, **destaque de mensagens de erro em vermelho vívido (`#ef4444`)** e auto-scroll thread-safe.
  - **Aba 2 (Serviços & Relatórios):** Card de diagnóstico dos serviços com **ServiceWatcher assíncrono em background** (zero bloqueios de rede/subprocessos na UI thread) e **histórico limpo de RELINTs processados** (fonte compacta de 11px em até 2 linhas com `setWordWrap`, badge de método `IA`/`Regex`, badge de status `🟢 Lido com Sucesso`, **badge/card em vermelho `#451a1a` para falhas de leitura (`🔴 Falha na Leitura`)** e **botão largo de reprocessamento `🔄 Re-processar`**).
  - **Performance & Zero Latência:** Fila de logs em lote com Typewriter a 60 FPS acelerado ao fim da leitura eliminando engasgos de renderização do `QTextEdit`, proteção seletiva de botões de disco durante leitura e atualização ultrarrápida de progresso (< 0.1ms).
  - **Minimização na Bandeja do Sistema (`System Tray`):** Fechar a janela minimiza o app diretamente para o System Tray com menu de contexto (`Abrir Painel`, `Abrir Dashboard Web`, `Encerrar Todos os Serviços`). `setQuitOnLastWindowClosed(False)` garante permanência em background sem fechar o processo.
  - **Botão de Encerramento Total (`⛔ Encerrar Todos os Serviços & Sair`):** Finaliza com segurança todos os processos (Watchdog, FastAPI, Vite/Node na porta 5173), fecha o tray icon e encerra o app completamente.
- [x] **Limpeza de Arquivos Legados do Flet:** Expurgo total de arquivos e referências legadas do Flet (`flet_app.py`), concentrando a stack desktop exclusivamente no PyQt6 e o frontend no SvelteKit.
- [x] **Arquitetura de Especialidades Polimórficas:** Modelo `HomicideReport` estendendo `IncidentReport` com extração especializada (motivação, registro policial, unidade BPM) persistida no SQLite.
- [x] **Classificador Determinístico (`bm_classifier.py`):** Classificação regex por especificidade pós-LLM e fallback para processamento sem IA.
- [x] **Dashboard Web Completo (Resend Design System):**
  - Tema escuro puro (`#000000`), hairlines translúcidas, componentes modulares em `variables.css`.
  - Visualizador de dossiês por especialidade (`homicides_view.js`).
  - Dashboard de Crimes & Analytics com gráficos offline **ApexCharts** (`crimes_view.js`).
  - Galeria de imagens geral com visualizador Lightbox com zoom.
- [x] **Suíte de Testes Automatizados:** 110 testes unitários e de integração de API com `pytest` cobrindo 100% da aplicação.
- [x] **Unificação de Ações e Minimalismo no Header Web:** Remoção do botão `Abrir Dashboard` e Badge de Status do topo, centralizando ações de UX na interface principal e limpando componentes obsoletos. O botão de recolher a Sidebar foi convertido em um botão circular flutuante elegante.
- [x] **Botões e Navegação Enxutos:** Remoção do box-border redundante nos botões de abas da visualização de Monitoramento. Troca do Checkbox estático do motor IA por um Botão de Status Interativo e Inteligente (Verde Esmeralda p/ ativo, Amarelo de Alerta p/ Modo Regex).
- [x] **Melhoria Gráfica Circular Avançada:** Engrossamento dos SVGs da aba de Monitoramento para o formato Anel Premium (tipo Apple Watch), com ajuste dinâmico do `overflow: visible` para eliminação do corte na caixa da animação incandescente e aumento da pulsação e velocidade das barras luminosas.
- [x] **Indicador Animado de Carregamento:** O painel de leitura agora conta com um Spinner animado inline (`<svg class="spin-fast">`) elegante em vez de texto seco durante a leitura do conteúdo do relatório.
- [x] **Estabilidade e Loading Otimista da IA:** Adição de feedback visual instantâneo (spinner "Testando IA..." ou "Desativando...") ao alternar o modo de processamento de Inteligência Artificial. Implementação de proteção de concorrência (flag `_isTogglingLLM`) para impedir que o polling assíncrono de gráficos sobreponha o estado do botão durante a latência de rede/Ollama, e correção do bug que travava cliques subsequentes.
- [x] **Migração de Esquema do Banco de Dados e Sistema para Português (pt-BR):**
  - Tradução de todas as tabelas (`relints`, `homicidio_detalhes`, `pessoas`, `relint_participantes`, `relint_imagens`) e colunas no SQLite nativo e adapters (`SqliteRepo`, `SqlitePersonRepo`).
  - Auto-migração transparente de bancos legados executada em `_init_db()` via `ALTER TABLE RENAME COLUMN`.
  - Atualização do arquivo de especificação do banco `schema.dbml` com todas as colunas e tabelas de especialidade polimórficas (Tráfico, Roubos e Furtos) em Português.
  - Suporte completo a aliases Pydantic e fallbacks retrocompatíveis na API REST e na interface Web SPA (`relints_view.js`, `homicides_view.js`).
- [x] **Unificação Global e Modularização de Abas (DRY Architecture):**
  - **Componente Único de Participantes (`ParticipantsTabComponent`):** Layout Master-Detail (40% Lista / 60% Dossiê) com busca em tempo real por nome/vulgo, badges de função e suporte a galeria de imagens vinculadas.
  - **Biblioteca Central de Abas (`RelintTabsComponents`):** Renderização padronizada de `Síntese` (caixa compacta invertida + resumo), `Especialidades` (atributos estruturados), `Fotos` (galeria com lightbox), `Localização` (dashboard geográfico com OSM iframe e badges de precisão) e `Transcrição` (leitor literal).
  - Eliminação de duplicação de código entre os painéis `relints_view.js` e `homicides_view.js`.
- [x] **Migração para SvelteKit & Sistema de Design Tokens do Penpot:**
  - Construção da biblioteca oficial de 10 componentes de UI em Svelte 5 (`Button`, `Badge`, `Card`, `StatCard`, `Input`, `Switch`, `Alert`, `Table`, `Modal`, `Tabs`) consumindo estritamente variáveis de tokens (`style.css`) e respeitando a grade base de 4px e interações táteis do Apple Design.
  - Ajustado o alinhamento vertical *Pixel-Perfect* de ícones e tipografia em todos os componentes (`Button`, `Badge`, `Input`, `Tabs`, `Alert`), isolando os nós SVG em `inline-flex` e fixando a linha base ótica com `line-height: 1`.
  - Implementado o **App Shell do Dashboard** modular em `src/lib/components/layout/` contendo `Sidebar.svelte` (retrátil com ícones Phosphor), `Header.svelte` (fixo) e `AppShell.svelte`.
  - Otimizada a inicialização e estabilidade do aplicativo desktop (`painel.py` / `desktop/ui/pyqt_app.py`):
    - Varredura de arquivos e inspeção de pasta tornadas **100% assíncronas** (`inspect_folder(async_exec=True)`), reduzindo o tempo de abertura do painel para **menos de 0.3 segundos**.
    - Botões de serviços desacoplados: Botão Unificado na Aba 1 (`🌐 Iniciar & Abrir Dashboard Completo`) e botões individuais dedicados na Aba 2 (`🚀 Iniciar API` e `🚀 Iniciar Svelte`).
    - **Proteção contra concorrência e transições de estado:** Implementação de flags de transição (`_is_transitioning_backend`, `_is_transitioning_frontend`, `_is_transitioning_dashboard`) para garantir que o monitor de background (`ServiceWatcher`) não sobrescreva o estado transitório dos botões enquanto os serviços estão inicializando ou parando.
    - **Monitoramento 100% Silencioso via Sockets Nativos:** Substituição de comandos `subprocess` (`netstat`) por verificações TCP nativas com `socket.connect_ex`, eliminando piscadas de terminal no Windows.
    - **Indicadores de Carregamento Ativo no Console:** Badge dinâmico no cabeçalho com spinner animado (`⠋ ⠙ ⠹...`) e barra de progresso indeterminada de 3px indicando atividades em segundo plano (verificação de IA, inicialização de serviços, reindexação e reprocessamento).
    - **Reprocessamento individual assíncrono na Aba de Relatórios:** Botão `🔄 Re-processar` em cada card de RELINT executa em background com feedback visual imediato no console e auto-atualização do histórico.
  - Reorganizada a estrutura de rotas: `/` tornou-se a "Visão Geral" do Dashboard (Estatísticas e KPIs) usando o novo App Shell, enquanto a biblioteca visual foi preservada na rota exclusiva `/design-system`.
- [x] **Pipeline Cognitivo Multi-Pass (Etapas 1 e 2 Concluídas):**
  - Transição da extração monolítica da LLM para uma arquitetura em 5 leituras especializadas.
  - **Etapa 1 (Síntese & Assunto):** Implementação do schema isolado `SummaryExtraction`, do extrator especializado `SummaryExtractor` (`backend/engine/extractors/llm/extractors/summary_extractor.py`) e integração ao `LlmPipeline`.
  - **Etapa 2 (Localização & Georreferenciamento):** Implementação do schema isolado `LocationExtraction`, do extrator `LocationExtractor` (`backend/engine/extractors/llm/extractors/location_extractor.py`) com normalização no padrão Google Maps, herança determinística obrigatória de município, sanitização estrita de ruídos (links, verbos policiais, coordenadas no meio do texto), tratamento de zonas rurais como `Interior`, blindagem anti-alucinação de GPS (zero fake GPS), enquadramento de município sem balão no mapa e classificação estrita em 3 níveis de precisão (Alta/Verde, Média/Azul, Baixa/Âmbar).
  - **Interface SvelteKit (`TabLocation.svelte`):** Renderização de badge dinâmico de precisão de 3 cores, box de mapa escuro interativo com suporte a enquadramento de cidade inteira sem balão e botão de abertura direta no Google Maps com ícones Phosphor.
- [x] **Preservados todos os documentos de contexto e workflows na pasta `.agents/` e `.ai_context/`:**
  - `.ai_context/05_design_system_penpot_guide.md` (Guia de Design System e sincronização com Penpot);
    - `.agents/workflows/sync-penpot.md` (`/sync-penpot`: Workflow de auditoria 1:1 e sincronização Penpot -> Código);
    - `.agents/workflows/export-to-penpot.md` (`/export-to-penpot`: Workflow de geração de componentes Código -> Penpot).
- [x] **Maximização e Otimização da Área de Leitura & Dossiê:**
  - **Layout 100% Fluido no AppShell:** Remoção do limite artificial `max-width: 1440px`, permitindo que o Dashboard ocupe 100% da resolução em monitores Full HD, Quad HD e UltraWide.
  - **Painel Master-Detail Proporcional 30% / 70% e Retrátil na rota `/relints`:** Coluna lateral balanceada com botão flutuante de recolhimento instantâneo para 100% no Dossiê.
  - **Otimização de Inicialização & Novo Workflow `/run`:** Script autônomo e leve `start_web.py` para subir diretamente o **FastAPI** (`:8000`) e o **SvelteKit** (`:5173`) abrindo no navegador.
  - **Performance Extrema do Dashboard (Backend & Frontend):** Método `get_dashboard_metrics()` no `SqliteRepo` executando agregação SQL em tempo constante (< 5ms) e endpoint `GET /api/v1/relints/stats`.
  - **Transições Fluidas de Página & Dossiê (Apple WWDC Fluid Motion):** Animação `.page-enter-animation` em `+layout.svelte` e `.relint-enter-animation` em `relints/+page.svelte`.
  - **Módulo Completo de Participantes & Dossiês (`/participantes` e `TabParticipants.svelte`):** Página inteira Master-Detail e modal de visualização e edição direta com persistência SQLite.
- [x] **Desacoplamento e Isolamento Físico dos Motores LLM e Regex:**
  - Criação do pipeline especialista `LlmPipeline` em `backend/engine/extractors/llm/` com execução 100% orientada a IA sem fallbacks silenciosos.
  - Centralização do motor determinístico em `DeterministicPipeline` e realocação de listas negras (`negative_filters.py`) e base IBGE (`ibge_names.json`) para a pasta `deterministic/`.
  - Expurgo da pasta compartilhada `common/`.
- [x] **Reatividade em Tempo Real via SSE (Server-Sent Events) no SvelteKit:**
  - Criação do serviço singleton [eventsService.js](file:///d:/www/ReadRelint/frontend/src/lib/services/eventsService.js) com auto-reconexão inteligente.
  - Atualização instantânea sem refresh dos contadores, KPIs e lista de relatórios recentes na rota `/` ([+page.svelte](file:///d:/www/ReadRelint/frontend/src/routes/+page.svelte)).
  - Correção de bloqueio silencioso CORS do navegador usando URL relativas no Svelte para bypass do FastAPI no WebView nativo do Windows.
- [x] **Migração da Reatividade para WebSockets (Bidirecional):**
  - Substituição planejada do fluxo unidirecional SSE (`EventSource`) por WebSockets nativos (`ws://`) no Svelte 5 e FastAPI.
  - O objetivo é pavimentar o caminho para a funcionalidade de edição reversa de relatórios pela UI web em tempo real.
- [x] **Configuração de Ambiente IDE (.vscode):**


  - Adicionada regra `files.exclude` no `.vscode/settings.json` para ocultar automaticamente pastas `__pycache__`, `.pytest_cache` e arquivos `.pyc`/`.pyo`.
- [x] **Correção de Inconsistências na Extração de Localização/Unidade (Auditoria + Guardrails Determinísticos):**
  - Auditoria completa nos 562 RELINTs comparando `endereco`/`municipio`/`unidade_policial`/`coordenadas` contra a Transcrição Literal — detalhamento completo em [`melhorias-extracao-geo.md`](./proposals/melhorias-extracao-geo.md) e [`termometro-certeza.md`](./proposals/termometro-certeza.md).
  - **`police_unit` sai do prompt da LLM e vira 100% determinístico**: tabela fixa de 41 municípios → 16º/37º/39º BPM, com regra de mão dupla (menção literal única no texto vence; ambíguo/ausente cai para a tabela; fora da tabela e sem menção fica vazio). Eliminava o viés de âncora no exemplo do prompt (56% dos registros vinham "39º BPM", 70% deles sem nenhuma sustentação no texto).
  - **Guardrail de evidência textual para `street`**: descarta a rua devolvida pela LLM se ela não existir literalmente no texto (mesmo viés de âncora identificado em "Rua General Osório").
  - **Prioridade determinística de `municipality`**: o município do cabeçalho `ASSUNTO` agora sempre prevalece sobre a resposta da LLM (antes só prevalecia quando o valor da LLM não aparecia em nenhum lugar do texto, o que falhava quando o documento citava a cidade errada em outro contexto).
  - **Correção da perda do sinal "-" nas coordenadas**: normalização do artefato de quebra de linha do PyMuPDF (`-\n<dígitos>`), conversão real de DMS para decimal, e blindagem geográfica que força sinal negativo em lat/long e valida a faixa aproximada do RS (descarta também placeholders textuais como "N/A"/"Sem informação").
  - **Correção crítica no `LlmPipeline`**: o Pass 2 (`LocationExtractor`, com todos os guardrails acima) só sobrescrevia o resultado do pass legado (schema `IncidentReport`, sem guardrails) quando retornava valor não-vazio — deixando vazar placeholders/alucinações do pass antigo sempre que o Pass 2 corretamente abstraía. Agora o Pass 2 é sempre autoritativo para os campos geográficos.
  - Suíte de testes dedicada em `tests/test_location_extractor.py` (23 testes, incluindo reprodução dos casos reais encontrados na auditoria).
- [x] **Extração de Especialidades em 2 Estágios (Substitui as Rules/Entidades Legadas Desconectadas):**
  - Detalhamento completo nos [ADR-0091](./adr/0091-unidade-policial-deterministica-tabela-municipio-bpm.md) a [ADR-0094](./adr/0094-extracao-especialidades-2-estagios-substitui-rules-legadas.md).
  - Descoberto que as 7 classes `Rule` especializadas e as entidades polimórficas (`HomicideReport` etc.) nunca estavam conectadas ao pipeline ao vivo (`main_controller.py` usa `RelintRule()` fixo) — os campos de especialidade nunca eram perguntados à LLM e as tabelas de detalhe (`homicidio_detalhes` etc.) só recebiam valores default do Pydantic, nunca dado real.
  - **Estágio 1 (Classificação):** `classify_bm_group()` (`bm_classifier.py`) passa a rodar sempre (antes só no modo sem-IA), priorizando filename+assunto sobre o conteúdo — 100% determinístico, sem LLM.
  - **Estágio 2 (Extração):** Novo `SpecialtyExtractor` (`backend/engine/extractors/llm/extractors/specialty_extractor.py`), Passo 3 do pipeline multi-pass. Campos binários (`injured_victims`, `hostage_victim`, `recovered`, `location_type`) resolvidos por regex, sem LLM. Campos livres (`motivation`, `drug_quantity`, `vehicle_model` etc.) usam schemas Pydantic minúsculos por especialidade (`specialty_schemas.py`) com guardrails de enum fechado e evidência literal no texto. Especialidades sem campo livre (`Roubo a Residência`, `Furto Qualificado`, `Outros`) nunca chamam a LLM.
  - `IncidentReport` ganha `model_config = ConfigDict(extra="allow")` para os campos de especialidade sobreviverem sem reviver os schemas monolíticos por subclasse.
  - Suíte de testes dedicada em `tests/test_specialty_extractor.py` (20 testes).
- [x] **Transcrição Literal com Realce de Entidades & Formulários de Especialidade (7 Tipos):** Detalhamento completo no [ADR-0097](./adr/0097-transcricao-literal-realce-inline-entidades-formularios-config-driven.md).
  - `TabTranscription.svelte`: fonte trocada pra `body-large` (16px/24px) do design system, mais confortável pra leitura longa. Realce inline de coordenadas, endereço, município e link do mapa (verde translúcido, só aparece quando o dado bate literalmente no texto — link sintetizado de busca nunca realça) e de participantes por papel (Autor/Suspeito vermelho, Vítima âmbar, Testemunha azul), com badges de legenda condicionais no topo.
  - `TabSpecialty.svelte`: reescrito de formulário fixo só-Homicídio (com 2 campos fantasmas que nunca existiram no backend) pra renderizador config-driven cobrindo as 7 especialidades.
- [x] **Code Review Pós-Implementação (10 achados corrigidos):** Detalhamento completo no [ADR-0095](./adr/0095-active-rule-fixo-relintrule-decisao-deliberada.md). Destaques: correção do `$derived.by` no `TabSpecialty.svelte` que mutava o prop `relint` (Svelte 5 `state_unsafe_mutation`); Passo 3 agora sobrescreve incondicionalmente `result.data` (mesmo padrão do Passo 2), impedindo que resposta crua do Pass 1 legado vaze quando o guardrail do Passo 3 descarta um campo; regex de realce de participantes no `TabTranscription.svelte` corrigido para nomes acentuados (`José`, `André`); `geo_precision` recalculado após `enforce_rs_coordinate_signs` (evita badge "alta" com coordenada vazia); janela de negação em `specialty_extractor.py` agora respeita fronteira de oração; correção da ADR-094 (as 7 entidades especializadas NÃO estão superadas, só as 7 classes `Rule`); comentário de aviso em `main_controller.py:55` contra reativação acidental; campos supérfluos removidos do schema do Pass 1 legado; funções de coordenada movidas para `text_cleaner.py` (reuso entre motor LLM e motor determinístico, fechando a lacuna do caminho sem-IA); `classify_bm_group` deixa de rodar em duplicidade no caminho Ollama.
- [x] **Coordenadas Normalizadas em 6 Casas Decimais (Padrão Google Maps):** Detalhamento no ADR-098. `enforce_rs_coordinate_signs()` (`text_cleaner.py`) agora sempre formata a saída com `.6f` — completa com zero quando o documento tinha menos precisão, arredonda quando tinha mais. Antes a precisão salva variava por documento (3 a 14+ dígitos).

## 2. Próximas Etapas (Prioridade e Roteiro de Tasks)

### 🧠 FASE 1: EXTRAÇÃO COGNITIVA (100% LLM)
- [x] **Task 1.1 — Engenharia de Prompt e Estruturação da Síntese:**
  - Modularização em `backend/engine/extractors/llm/prompts/summary_prompt.py`.
  - Método das 5 Perguntas Policiais (*O quê, Quem, Onde/Quando, Como, Desfecho*).
  - Regra explícita anti-redundância: zero repetição de endereços ou dados burocráticos de pessoas na síntese.
- [x] **Task 1.2 — Engenharia de Prompt e Decomposição de Endereço / Localização:**
  - Criação de `backend/engine/extractors/llm/prompts/address_prompt.py`.
  - Padrão de saída simplificado: `Rua/Av, nº - Município`.
  - Extração de coordenadas decimais Google Maps (`-29.xxxx, -51.xxxx`) e link `map_url`.
- [x] **Task 1.3 — Schemas Pydantic & Validador de Saída JSON:**
  - Criação de `backend/engine/extractors/llm/schemas/address_schema.py`.
  - Validador e normalizador `backend/engine/extractors/llm/validators/llm_response_validator.py` com geração de links Google Maps.
- [x] **Task 1.4 — Calibração e Validação de Testes Unitários:**
  - Suíte completa em `tests/test_llm_prompts.py` (14 testes passando).
- [ ] **Task 1.5 — Eliminação Total do Pass 1 Legado, Quebrado em Passes Dedicados (PRÓXIMA ETAPA):**
  - Plano completo em [`eliminacao-pass1-legado.md`](./proposals/eliminacao-pass1-legado.md) e [ADR-0096](./adr/0096-eliminacao-total-pass1-legado-passes-dedicados-proposta.md).
  - Objetivo confirmado: **não é reduzir** chamadas à LLM, é quebrar em passes mais especializados pra aumentar qualidade — determinismo onde o campo for formulaico, LLM só onde há julgamento genuíno.
  - `date_of_fact`/`time_of_fact` → 100% determinístico. `relint_type` → novo classificador determinístico. `registry_number`/`registry_agency`/`registry_year` → novo pass LLM dedicado. `location_types` → novo pass LLM dedicado. `main_fact` → derivado sem chamada nova. `participants` → removido do Pass 1 legado agora, passes novos a desenhar em etapa futura separada.

### ⚡ FASE 2: EXTRAÇÃO DETERMINÍSTICA (100% REGEX & HEURÍSTICAS)
- [ ] **Task 2.1 — Modularização dos Extratores Regex por Domínio:**

  - Criação de classes dedicadas em `backend/engine/extractors/deterministic/extractors/` (`date_time_extractor.py`, `metadata_extractor.py`, `classifier_extractor.py`).
- [ ] **Task 2.2 — Extrator Especialista de Endereço Regex & Coordenadas:**
  - Criação de `address_extractor.py` e `coordinates_extractor.py` (vias, números e conversão de GPS/UTM).
- [ ] **Task 2.3 — Extrator Heurístico de Síntese Regex:**
  - Criação de `summary_extractor.py` para seleção do parágrafo mais representativo em modo sem IA.
- [ ] **Task 2.4 — Suíte de Testes Automatizados:**
  - Criação de testes unitários isolados para cada sub-extrator determinístico.

### 🌐 FASE 3: Acesso Online Seguro & Infraestrutura
- [ ] Configurar **Cloudflare Tunnel** para expor o FastAPI local via domínio fixo com HTTPS.
- [ ] Implementar **Criptografia Ponta-a-Ponta (E2EE)** na camada da aplicação.

## 3. Backlog Futuro (Planejado / Aguardando Ordem de Execução)
- [ ] **Dashboard Público Anonimizado (Hostinger):**
  - Gerenciador de layouts e páginas de dashboards no app local (ReadRelint).
  - Botão de publicação inicial com geração de payload 100% anonimizado (apenas totais/KPIs numéricos, 0% PII ou textos de RELINTs).
  - Sincronização automática em tempo real: após publicado, novos PDFs lidos localmente disparam PUSH dos deltas estatísticos para a Hostinger.
  - Hospedagem pública Hostinger com autenticação por senha e logs de visualização no futuro.
- [ ] **Exportação de Relatórios Estruturados:** Botões para exportar Dossiê e Casos para Excel, CSV ou PDF.
- [ ] **Grafos de Vínculos (Visualização Gráfica):** Plot interativo mostrando conexões em rede entre Pessoas e Relatórios.
- [ ] **Check de Hashes (SHA-256):** Hashing dos PDFs para re-processamento automático ao detectar modificações no arquivo.
