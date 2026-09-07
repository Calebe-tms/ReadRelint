# Índice de ADRs (Architecture Decision Records)

Este diretório contém o registro de decisões arquiteturais do ReadRelint no formato [MADR](https://adr.github.io/madr/) (Markdown Architectural Decision Records). Cada ADR é um arquivo próprio e **imutável**: uma vez aceita, uma decisão não é editada retroativamente — uma mudança de rumo gera uma **nova** ADR que referencia e supera a anterior (status "Substituída pela ADR-NNNN"), preservando o histórico de raciocínio do projeto.

Os números **ADR-010 a ADR-016 não existem** neste índice de propósito: são lacunas reais deixadas por decisões antigas que foram removidas do histórico do projeto (revertidas antes da consolidação deste registro), não uma falha de numeração. Números repetidos que existiam no registro compactado original (`.ai_context/03_decisions_and_workflow.md`) — segundas ocorrências de ADR-053, ADR-054 e ADR-055 com conteúdo diferente das primeiras — foram renumeradas para ADR-041, ADR-071 e ADR-077 respectivamente, preenchendo lacunas que também existiam nessa sequência original.

| Nº | Título | Status | Arquivo |
|---|---|---|---|
| 0001 | Clean Architecture e NLP Local | Aceita | [0001-clean-architecture-nlp-local.md](./0001-clean-architecture-nlp-local.md) |
| 0002 | Interface Híbrida | Aceita | [0002-interface-hibrida-web-desktop.md](./0002-interface-hibrida-web-desktop.md) |
| 0003 | Migração de TinyDB para SQLite (Persistência Principal) | Aceita | [0003-migracao-tinydb-sqlite.md](./0003-migracao-tinydb-sqlite.md) |
| 0004 | Separação de Dados de Pessoas | Aceita | [0004-separacao-dados-pessoas.md](./0004-separacao-dados-pessoas.md) |
| 0005 | Exclusão de Guarnições PM e Transcrição Segura | Aceita | [0005-exclusao-guarnicoes-pm-transcricao-segura.md](./0005-exclusao-guarnicoes-pm-transcricao-segura.md) |
| 0006 | Prioridade da Curadoria Humana | Aceita | [0006-prioridade-curadoria-humana.md](./0006-prioridade-curadoria-humana.md) |
| 0007 | Geolocalização Visual por 3 Níveis | Aceita | [0007-geolocalizacao-visual-3-niveis.md](./0007-geolocalizacao-visual-3-niveis.md) |
| 0008 | Repositório Universal (Sem Descartes) | Aceita | [0008-repositorio-universal-sem-descartes.md](./0008-repositorio-universal-sem-descartes.md) |
| 0009 | Suíte de Testes 100% Mockada | Aceita | [0009-suite-testes-100-mockada.md](./0009-suite-testes-100-mockada.md) |
| 0017 | Remoção da Tabela de Municípios (Cálculo On-The-Fly) | Aceita | [0017-remocao-tabela-municipios.md](./0017-remocao-tabela-municipios.md) |
| 0018 | Migração de Streamlit para FastAPI + Frontend Custom | Aceita | [0018-migracao-streamlit-fastapi-frontend-custom.md](./0018-migracao-streamlit-fastapi-frontend-custom.md) |
| 0019 | Acesso Online com E2EE (Cloudflare Tunnel) | Aceita | [0019-acesso-online-e2ee-cloudflare-tunnel.md](./0019-acesso-online-e2ee-cloudflare-tunnel.md) |
| 0020 | Descarte da Associação Automática de Fotos a Participantes | Aceita | [0020-descarte-associacao-automatica-fotos-participantes.md](./0020-descarte-associacao-automatica-fotos-participantes.md) |
| 0021 | Remoção Completa do Streamlit | Aceita | [0021-remocao-completa-streamlit.md](./0021-remocao-completa-streamlit.md) |
| 0022 | Especialidades Polimórficas (Homicídios) | Aceita | [0022-especialidades-polimorficas-homicidios.md](./0022-especialidades-polimorficas-homicidios.md) |
| 0023 | Schemas Dinâmicos na Camada Cognitiva (LLM) | Aceita | [0023-schemas-dinamicos-camada-cognitiva-llm.md](./0023-schemas-dinamicos-camada-cognitiva-llm.md) |
| 0024 | Classificação Determinística por Regex (`bm_classifier.py`) | Aceita | [0024-classificacao-deterministica-regex-bm-classifier.md](./0024-classificacao-deterministica-regex-bm-classifier.md) |
| 0025 | Adoção do Resend Design System (`Design.md`) | Aceita | [0025-adocao-resend-design-system.md](./0025-adocao-resend-design-system.md) |
| 0026 | Dashboard Analytics com ApexCharts Offline | Aceita | [0026-dashboard-analytics-apexcharts-offline.md](./0026-dashboard-analytics-apexcharts-offline.md) |
| 0027 | Foco na Experiência Desktop Nativa (Tkinter / CustomTkinter) | Aceita | [0027-foco-experiencia-desktop-nativa-tkinter.md](./0027-foco-experiencia-desktop-nativa-tkinter.md) |
| 0028 | Tema Dark Slate Neutro para UI Desktop | Aceita | [0028-tema-dark-slate-neutro-ui-desktop.md](./0028-tema-dark-slate-neutro-ui-desktop.md) |
| 0029 | Duas Barras de Progresso e Inspecção Instantânea de Diretório | Aceita | [0029-duas-barras-progresso-inspecao-instantanea-diretorio.md](./0029-duas-barras-progresso-inspecao-instantanea-diretorio.md) |
| 0030 | Rastreabilidade de Método de Extração (`Ollama (IA)` vs `Regex (Sem IA)`) | Aceita | [0030-rastreabilidade-metodo-extracao.md](./0030-rastreabilidade-metodo-extracao.md) |
| 0031 | Monitoramento de Conexão da LLM em Tempo Real (Heartbeat) | Aceita | [0031-monitoramento-conexao-llm-tempo-real-heartbeat.md](./0031-monitoramento-conexao-llm-tempo-real-heartbeat.md) |
| 0032 | Layout Split View 60/40 com Coluna Retrátil na Web | Aceita | [0032-layout-split-view-60-40-coluna-retratil-web.md](./0032-layout-split-view-60-40-coluna-retratil-web.md) |
| 0033 | Medidores Circulares de Progresso SVG em Cards Individuais | Aceita | [0033-medidores-circulares-progresso-svg-cards.md](./0033-medidores-circulares-progresso-svg-cards.md) |
| 0034 | Transmissão SSE de Logs do Terminal para a Web | Aceita | [0034-transmissao-sse-logs-terminal-web.md](./0034-transmissao-sse-logs-terminal-web.md) |
| 0035 | Proteção contra Desconexões Falso-Positivas de IA | Aceita | [0035-protecao-desconexoes-falso-positivas-ia.md](./0035-protecao-desconexoes-falso-positivas-ia.md) |
| 0036 | Redesign Compacto Vertical e Aba STATUS em 1º Lugar (Desktop UI) | Aceita | [0036-redesign-compacto-vertical-aba-status-desktop.md](./0036-redesign-compacto-vertical-aba-status-desktop.md) |
| 0037 | Minimizado para a Bandeja do Sistema (System Tray) via `pystray` | Aceita | [0037-minimizado-bandeja-sistema-system-tray-pystray.md](./0037-minimizado-bandeja-sistema-system-tray-pystray.md) |
| 0038 | Servidor Web In-Process via Thread Daemon (Sincronização Perfeita Tkinter & Web) | Aceita | [0038-servidor-web-in-process-thread-daemon.md](./0038-servidor-web-in-process-thread-daemon.md) |
| 0039 | Execução Direta por Script `.py` em Batch Script (`Iniciar-Painel.bat`) | Aceita | [0039-execucao-direta-script-py-batch-script.md](./0039-execucao-direta-script-py-batch-script.md) |
| 0040 | Botão Dinâmico de Servidor Web e Centralização das Ações Globais na Aba Status | Aceita | [0040-botao-dinamico-servidor-web-centralizacao-acoes-status.md](./0040-botao-dinamico-servidor-web-centralizacao-acoes-status.md) |
| 0041 | Inicialização Autônoma Web-Only (`start_web.py` e Workflow `/run`) | Aceita | [0041-inicializacao-autonoma-web-only.md](./0041-inicializacao-autonoma-web-only.md) |
| 0042 | Reorganização do Monitoramento Web em Sub-Abas com Terminal de Logs na Coluna Direita | Aceita | [0042-reorganizacao-monitoramento-web-sub-abas-terminal-logs.md](./0042-reorganizacao-monitoramento-web-sub-abas-terminal-logs.md) |
| 0043 | Layout Dividido do Relatório Web (20% Gauges Circulares SVG / 80% Lista com Scroll Adaptativo) | Aceita | [0043-layout-dividido-relatorio-web-gauges-svg-lista.md](./0043-layout-dividido-relatorio-web-gauges-svg-lista.md) |
| 0044 | Validação Estrita do Método de Extração Cognitiva (`isLlmExtraction`) | Aceita | [0044-validacao-estrita-metodo-extracao-cognitiva.md](./0044-validacao-estrita-metodo-extracao-cognitiva.md) |
| 0045 | Otimização de Performance e Baixa Latência no Fluxo de Monitoramento | Aceita | [0045-otimizacao-performance-baixa-latencia-monitoramento.md](./0045-otimizacao-performance-baixa-latencia-monitoramento.md) |
| 0046 | Otimização de E/S em Disco no Início do Monitoramento (`remove_records_bulk`) | Aceita | [0046-otimizacao-es-disco-inicio-monitoramento.md](./0046-otimizacao-es-disco-inicio-monitoramento.md) |
| 0047 | Inicialização Assíncrona Não-Bloqueante & Loading Explicativo de Varredura | Aceita | [0047-inicializacao-assincrona-nao-bloqueante-loading.md](./0047-inicializacao-assincrona-nao-bloqueante-loading.md) |
| 0048 | Eliminação da Oscilação (Flicker/Bounce) do Estado de Monitoramento no Frontend | Aceita | [0048-eliminacao-oscilacao-flicker-bounce-monitoramento.md](./0048-eliminacao-oscilacao-flicker-bounce-monitoramento.md) |
| 0049 | Transformação do App Desktop em Service Launcher & Hub (Zero Overhead) | Aceita | [0049-transformacao-app-desktop-service-launcher-hub.md](./0049-transformacao-app-desktop-service-launcher-hub.md) |
| 0050 | Refinamento Avançado da UX Web (Zero Redundâncias) | Aceita | [0050-refinamento-avancado-ux-web-zero-redundancias.md](./0050-refinamento-avancado-ux-web-zero-redundancias.md) |
| 0051 | Proteção de Estado Visual com Flag Atômica (`_isTogglingLLM`) | Aceita | [0051-protecao-estado-visual-flag-atomica-toggling-llm.md](./0051-protecao-estado-visual-flag-atomica-toggling-llm.md) |
| 0052 | Preservação de Antecedentes e Conversão Polimórfica na Edição de RELINTs (`PUT /api/v1/relints/{id}`) | Aceita | [0052-preservacao-antecedentes-conversao-polimorfica-edicao-relints.md](./0052-preservacao-antecedentes-conversao-polimorfica-edicao-relints.md) |
| 0053 | Modal de Edição em Sub-Abas & Extensibilidade de Especialidades (`#edit-relint-modal`) | Aceita | [0053-modal-edicao-sub-abas-extensibilidade-especialidades.md](./0053-modal-edicao-sub-abas-extensibilidade-especialidades.md) |
| 0054 | Tradução do Esquema do Banco de Dados SQLite e do Sistema para Português (pt-BR) | Aceita | [0054-traducao-esquema-banco-dados-sqlite-sistema-pt-br.md](./0054-traducao-esquema-banco-dados-sqlite-sistema-pt-br.md) |
| 0055 | Centralização dos Campos de Registro Policial na Tabela Principal (`relints`) | Aceita | [0055-centralizacao-campos-registro-policial-tabela-principal.md](./0055-centralizacao-campos-registro-policial-tabela-principal.md) |
| 0056 | Normalização Bilíngue (pt-BR / en) da Extração Cognitiva via LLM (`EtlService`) | Aceita | [0056-normalizacao-bilingue-extracao-cognitiva-llm.md](./0056-normalizacao-bilingue-extracao-cognitiva-llm.md) |
| 0057 | Compatibilidade Dupla (Dual Computed Fields) nos Schemas REST & Views JS | Aceita | [0057-compatibilidade-dupla-dual-computed-fields.md](./0057-compatibilidade-dupla-dual-computed-fields.md) |
| 0058 | Separação por Linha em Branco (`\n\n`) após o Cabeçalho de ANEXOS no Texto Integral | Aceita | [0058-separacao-linha-branco-cabecalho-anexos-texto-integral.md](./0058-separacao-linha-branco-cabecalho-anexos-texto-integral.md) |
| 0059 | Arquitetura Reativa em Tempo Real via Server-Sent Events (SSE) e Listener EventSource | Aceita | [0059-arquitetura-reativa-tempo-real-sse-eventsource.md](./0059-arquitetura-reativa-tempo-real-sse-eventsource.md) |
| 0060 | Design Responsivo e Adaptável (Mobile, Tablet e Desktop) | Aceita | [0060-design-responsivo-adaptavel-mobile-tablet-desktop.md](./0060-design-responsivo-adaptavel-mobile-tablet-desktop.md) |
| 0061 | Dossiê de Participantes & Vinculação de Foto Principal e Galeria | Aceita | [0061-dossie-participantes-vinculacao-foto-principal-galeria.md](./0061-dossie-participantes-vinculacao-foto-principal-galeria.md) |
| 0062 | Higienização de Nomes de Participantes (LLM & Regex Rules) | Aceita | [0062-higienizacao-nomes-participantes-llm-regex-rules.md](./0062-higienizacao-nomes-participantes-llm-regex-rules.md) |
| 0063 | Layout Master-Detail (30% / 70%) para a Aba Participantes | Aceita | [0063-layout-master-detail-30-70-aba-participantes.md](./0063-layout-master-detail-30-70-aba-participantes.md) |
| 0064 | Reversão do Docling e Manutenção do PyMuPDF | Aceita | [0064-reversao-docling-manutencao-pymupdf.md](./0064-reversao-docling-manutencao-pymupdf.md) |
| 0065 | Migração do Painel Desktop para Flet (Flutter) e Isolamento na Raiz (/desktop) | Aceita | [0065-migracao-painel-desktop-flet.md](./0065-migracao-painel-desktop-flet.md) |
| 0066 | Migração Definitiva do Painel Desktop para PyQt6 (Qt6 Nativo) | Aceita | [0066-migracao-definitiva-painel-desktop-pyqt6.md](./0066-migracao-definitiva-painel-desktop-pyqt6.md) |
| 0067 | Desacoplamento da Checagem de Rede da LLM da UI Main Thread | Aceita | [0067-desacoplamento-checagem-rede-llm-ui-main-thread.md](./0067-desacoplamento-checagem-rede-llm-ui-main-thread.md) |
| 0068 | Thread-Safety de Atualizações de Progresso do ETL via `pyqtSignal` (`StatsEmitter`) | Aceita | [0068-thread-safety-atualizacoes-progresso-etl-pyqtsignal.md](./0068-thread-safety-atualizacoes-progresso-etl-pyqtsignal.md) |
| 0069 | Redesign da UI Desktop em 2 Abas Estratégicas (Split View & Gauges Circulares Vetoriais) | Aceita | [0069-redesign-ui-desktop-2-abas-split-view-gauges.md](./0069-redesign-ui-desktop-2-abas-split-view-gauges.md) |
| 0070 | Desacoplamento Total de UI a 60 FPS com ServiceWatcher e Fila de Logs Typewriter | Aceita | [0070-desacoplamento-total-ui-60fps-servicewatcher-typewriter.md](./0070-desacoplamento-total-ui-60fps-servicewatcher-typewriter.md) |
| 0071 | Métricas de Dashboard em Tempo Constante O(1) via SQL e Paginação Leve | Aceita | [0071-metricas-dashboard-tempo-constante-sql-paginacao.md](./0071-metricas-dashboard-tempo-constante-sql-paginacao.md) |
| 0072 | Unificação do Ciclo de Vida do Servidor Web (FastAPI + SvelteKit) | Aceita | [0072-unificacao-ciclo-vida-servidor-web-fastapi-sveltekit.md](./0072-unificacao-ciclo-vida-servidor-web-fastapi-sveltekit.md) |
| 0073 | Otimização de Encerramento Assíncrono de Serviços (Zero Lag UI) | Aceita | [0073-otimizacao-encerramento-assincrono-servicos.md](./0073-otimizacao-encerramento-assincrono-servicos.md) |
| 0074 | Encapsulamento dos Temas no Frontend SvelteKit (`frontend/src/lib/themes`) | Aceita | [0074-encapsulamento-temas-frontend-sveltekit.md](./0074-encapsulamento-temas-frontend-sveltekit.md) |
| 0075 | Adoção Exclusiva de Estilos Nativos no SvelteKit (Limpeza de Temas Customizados Legados) | Aceita | [0075-adocao-exclusiva-estilos-nativos-sveltekit.md](./0075-adocao-exclusiva-estilos-nativos-sveltekit.md) |
| 0076 | App Shell & Estrutura do Dashboard SvelteKit | Aceita | [0076-app-shell-estrutura-dashboard-sveltekit.md](./0076-app-shell-estrutura-dashboard-sveltekit.md) |
| 0077 | Transições Suaves Aceleradas por Hardware (Apple WWDC Fluid Motion) | Aceita | [0077-transicoes-suaves-aceleradas-hardware-fluid-motion.md](./0077-transicoes-suaves-aceleradas-hardware-fluid-motion.md) |
| 0078 | Monitoramento Silencioso de Portas via Sockets TCP e Travas de Transição no PyQt6 | Aceita | [0078-monitoramento-silencioso-portas-sockets-tcp.md](./0078-monitoramento-silencioso-portas-sockets-tcp.md) |
| 0079 | Indicadores Reativos de Carregamento e Diagnóstico no Console de Logs | Aceita | [0079-indicadores-reativos-carregamento-diagnostico-console.md](./0079-indicadores-reativos-carregamento-diagnostico-console.md) |
| 0080 | Layout 100% Fluido e Painel Retrátil na Rota `/relints` | Aceita | [0080-layout-100-fluido-painel-retratil-rota-relints.md](./0080-layout-100-fluido-painel-retratil-rota-relints.md) |
| 0081 | Refinamento Visual de Cards e Metadados Minimalistas | Aceita | [0081-refinamento-visual-cards-metadados-minimalistas.md](./0081-refinamento-visual-cards-metadados-minimalistas.md) |
| 0082 | Aba Síntese em Destaque e Campos de Metadados em Modo Leitura Pura | Aceita | [0082-aba-sintese-destaque-metadados-modo-leitura-pura.md](./0082-aba-sintese-destaque-metadados-modo-leitura-pura.md) |
| 0083 | Workflow `/run` e Inicialização Automática em Primeiro Plano (`--autostart`) | Aceita | [0083-workflow-run-inicializacao-automatica-autostart.md](./0083-workflow-run-inicializacao-automatica-autostart.md) |
| 0084 | Gestão Centralizada de Participantes e Dossiês Vinculados | Aceita | [0084-gestao-centralizada-participantes-dossies-vinculados.md](./0084-gestao-centralizada-participantes-dossies-vinculados.md) |
| 0085 | Desacoplamento Arquitetural Estrito dos Motores LLM e Regex | Aceita | [0085-desacoplamento-arquitetural-motores-llm-regex.md](./0085-desacoplamento-arquitetural-motores-llm-regex.md) |
| 0086 | Bypass de CORS em Transmissão SSE no SvelteKit | Aceita | [0086-bypass-cors-transmissao-sse-sveltekit.md](./0086-bypass-cors-transmissao-sse-sveltekit.md) |
| 0087 | Migração de SSE para WebSockets Bidirecionais (Concluída) | Aceita | [0087-migracao-sse-websockets-bidirecionais.md](./0087-migracao-sse-websockets-bidirecionais.md) |
| 0088 | Arquitetura Cognitiva Multi-Pass em 5 Leituras Especializadas (Multi-Step Extraction) | Aceita | [0088-arquitetura-cognitiva-multi-pass-5-leituras.md](./0088-arquitetura-cognitiva-multi-pass-5-leituras.md) |
| 0089 | Blindagem de Georreferenciamento, Anti-Alucinação de GPS e Sanitização de Endereços | Aceita | [0089-blindagem-georreferenciamento-anti-alucinacao-gps.md](./0089-blindagem-georreferenciamento-anti-alucinacao-gps.md) |
| 0090 | Especificação Completa dos Filtros e Camadas de Sanitização na Extração de Endereços por LLM | Aceita | [0090-especificacao-completa-filtros-sanitizacao-enderecos-llm.md](./0090-especificacao-completa-filtros-sanitizacao-enderecos-llm.md) |
| 0091 | Unidade Policial 100% Determinística via Tabela Município → BPM (Substitui Extração por LLM) | Aceita | [0091-unidade-policial-deterministica-tabela-municipio-bpm.md](./0091-unidade-policial-deterministica-tabela-municipio-bpm.md) |
| 0092 | Correção do Sinal de Coordenadas Perdido em Quebra de Linha do PDF e Blindagem Geográfica do RS | Aceita | [0092-correcao-sinal-coordenadas-quebra-linha-pdf-blindagem-rs.md](./0092-correcao-sinal-coordenadas-quebra-linha-pdf-blindagem-rs.md) |
| 0093 | Pass 2 (Localização) Torna-se Sempre Autoritativo sobre o Pass Legado | Aceita | [0093-pass2-localizacao-sempre-autoritativo-pass-legado.md](./0093-pass2-localizacao-sempre-autoritativo-pass-legado.md) |
| 0094 | Extração de Especialidades Reformulada em 2 Estágios — Substitui as Rules/Entidades Monolíticas Legadas | Aceita | [0094-extracao-especialidades-2-estagios-substitui-rules-legadas.md](./0094-extracao-especialidades-2-estagios-substitui-rules-legadas.md) |
| 0095 | `active_rule` Fixo em `RelintRule()` é Decisão Deliberada, Não Débito Pendente | Aceita | [0095-active-rule-fixo-relintrule-decisao-deliberada.md](./0095-active-rule-fixo-relintrule-decisao-deliberada.md) |
| 0096 | Próxima Etapa — Eliminação Total do Pass 1 Legado, Quebrado em Passes Dedicados (Proposta, Não Implementada) | Aceita | [0096-eliminacao-total-pass1-legado-passes-dedicados-proposta.md](./0096-eliminacao-total-pass1-legado-passes-dedicados-proposta.md) |
| 0097 | Transcrição Literal com Realce Inline de Entidades & Formulários de Especialidade Config-Driven | Aceita | [0097-transcricao-literal-realce-inline-entidades-formularios-config-driven.md](./0097-transcricao-literal-realce-inline-entidades-formularios-config-driven.md) |
| 0098 | Coordenadas Sempre Normalizadas em 6 Casas Decimais (Padrão Google Maps) | Aceita | [0098-coordenadas-normalizadas-6-casas-decimais-google-maps.md](./0098-coordenadas-normalizadas-6-casas-decimais-google-maps.md) |
| 0099 | Isolamento Estrito entre os Motores LLM e Determinístico — Sem Fallback Cruzado (por Enquanto) | Aceita | [0099-isolamento-estrito-motores-sem-fallback-cruzado.md](./0099-isolamento-estrito-motores-sem-fallback-cruzado.md) |
| 0100 | `RegistryExtractor` — Pass Dedicado para Registro Policial em Outro Órgão | Aceita | [0100-registry-extractor-registro-policial-outro-orgao.md](./0100-registry-extractor-registro-policial-outro-orgao.md) |
