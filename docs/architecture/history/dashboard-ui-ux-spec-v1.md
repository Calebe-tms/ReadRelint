# Especificação de Design, UI e UX do Dashboard ReadRelint
**Documento de Referência para Migração e Re-criação em Svelte 5**

> ⚠️ **SUPERADO** — Este documento descreve a interface HTML/JS vanilla anterior à migração para SvelteKit (ver ADR-076, "App Shell & Estrutura do Dashboard SvelteKit"). Mantido apenas como registro histórico de design; não reflete a UI atual do sistema.

---

## 1. Visão Geral e Filosofia Visual
- **Design System:** Baseado no **Resend Design System** (Dark Mode Minimalista & Clean Light Mode).
- **Diretrizes Estéticas:** Superfícies profundas (`#000000` / `#0a0a0c`), hairlines translúcidas (`rgba(255,255,255,0.06)` a `0.14`), tipografia moderna (Google Fonts *Inter* para UI e *Fira Code / Courier New* para identificadores, RGs e logs), micro-animações a 60 FPS e ausência de elementos visuais poluídos.
- **Responsividade:** Layout adaptativo fluido para telas Desktop widescreen, monitores Full HD, Tablets e modo gaveta (*drawer overlay*) em dispositivos móveis (< 992px).

---

## 2. Estrutura Estrutural do App Shell (`index.html`)

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│  SIDEBAR RETRÁTIL (Collapsed / Expanded)     │  TOPBAR HEADER (Fixo no Topo)   │
│  - Logo & Brand "ReadRelint"                 │  - Botão Hambúrguer Mobile      │
│  - Botão Flutuante Chevron (Borda Direita)   │  - Título Dinâmico da Aba Ativa │
│  - Lista de 8 Abas de Navegação (Ícone+Texto)│  - Seletor Global de Temas      │
│  - Footer: Dot de Status + Versão (v2.0.0)   ├─────────────────────────────────┤
│                                              │  WORKSPACE PRINCIPAL (.content) │
│                                              │  - Sub-Aba Ativa (.tab-content) │
│                                              │  - Master-Detail / Split Views  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1. Top Header (`.top-header`)
- **Posição:** Fixado no topo da área de conteúdo.
- **Lado Esquerdo:** 
  - Botão Hambúrguer Mobile (`#mobile-menu-btn` com ícone `menu`, visível apenas em telas menores).
  - Título da Página (`#page-title` em `font-size: 20px; font-weight: 700; color: var(--ink)`), atualizado dinamicamente ao trocar de aba.
- **Lado Direito:** 
  - Seletor de Temas (`#theme-selector` com `ThemeManager.setTheme`) estilizado com `var(--surface-card)`, borda `var(--hairline-strong)` e opções: *Resend Dark*, *Resend Light*, *Emerald Dark*, *Nord Slate*.

### 2.2. Sidebar Lateral Expansível (`.sidebar`)
- **Estado Padrão:** Recolhida (`.sidebar.collapsed`, largura: `64px`), exibindo apenas ícones centralizados com *tooltips*.
- **Estado Expandido:** Aberta (`.sidebar`, largura: `240px`), exibindo ícone + título textual da aba.
- **Botão de Alternância Flutuante (`.sidebar-toggle-btn`):**
  - Posicionado sobre a borda divisória direita (`right: -12px; top: 18px; z-index: 100`).
  - Formato circular com ícone SVG Chevron que rotaciona `180deg` na expansão/retração.
- **Itens de Menu (8 Abas):**
  1. `relints`: **RELINTs** (Ícone: `file-text`)
  2. `homicides`: **Especialidades** (Ícone: `crosshair`)
  3. `participants`: **Participantes** (Ícone: `users`)
  4. `municipalities`: **Municípios** (Ícone: `map-pin`)
  5. `crimes`: **Estatísticas** (Ícone: `bar-chart-3`)
  6. `gallery`: **Anexos & Fotos** (Ícone: `image`)
  7. `monitoring`: **Monitoramento & IA** (Ícone: `cpu`)
  8. `about`: **Sobre** (Ícone: `info`)
- **Footer da Sidebar (`.sidebar-footer`):**
  - Dot indicador de status do Motor Local (`.status-indicator .dot`: verde quando online, cinza quando offline).
  - Texto de versão `v2.0.0 (FastAPI + Web)`.

---

## 3. Mapeamento Detalhado das Telas / Abas

### 3.1. Aba 1: RELINTs (`#tab-relints`) — Layout Master-Detail
- **Coluna da Esquerda (Master Pane - 35% a 400px):**
  - **Barra de Filtros:** Input de busca em tempo real com ícone de lupa + Select de Grupos BM (Homicídio, Tráfico, Roubos, Furtos) + Select de Tipos de Relatório (Ocorrência, Disk Denúncia, Resposta a PB).
  - **Lista de Cards de RELINTs:** Scroll infinito/adaptativo contendo:
    - Linha superior: Assunto do fato em destaque + Data/Hora do fato.
    - Linha intermediária: Badge do Método (`"Ollama (IA)"` em verde ou `"Regex (Sem IA)"` em âmbar) + Grupo BM.
    - Linha inferior: Município/Bairro + Contagem de participantes qualificados.
- **Coluna da Direita (Detail Pane - 65%):**
  - **Header do Dossiê:** Assunto completo, número de registro policial, unidade BPM e botão de ação `✏️ Editar RELINT`.
  - **Navegação em 5 Sub-Abas do Dossiê:**
    1. *Ficha Geral:* Resumo executivo, fato principal, geolocalização e histórico de modificações.
    2. *Participantes:* Cards dos envolvidos com papéis (*Vítima*, *Testemunha*, *Autor/Suspeito*), fotos de perfil vinculadas e antecedentes.
    3. *Localização:* Endereço estruturado, coordenadas GPS e link/mapa Leaflet.
    4. *Galeria de Imagens:* Grid com todas as fotos extraídas do documento PDF.
    5. *Transcrição Integral:* Histórico literal narrado no boletim, separado por parágrafos e preservando quebras de linha após o cabeçalho de anexos.

---

### 3.2. Aba 2: Especialidades Criminais (`#tab-homicides`)
- **Estrutura:** Layout Master-Detail especializado em crimes de alta prioridade (Homicídios consumados/tentados).
- **Filtros Especiais:** Motivação do crime (Feminicídio, Tráfico, Desavença, Latrocínio), Tipo do Fato (Consumado vs Tentado) e Unidade BPM responsável.
- **Cards de Dossiê:** Exibição dedicada de qualificadores penais e cruzamento direto com os suspeitos e armas apreendidas.

---

### 3.3. Aba 3: Participantes & Vínculos (`#tab-participants`) — Layout 40% / 60%
- **Coluna da Esquerda (Master Pane - 40%):**
  - Input de busca rápida por Nome, Vulgo, RG ou CPF.
  - Switch interativo: `🔴 Apenas Reincidentes (>1 RELINT)` com badge contador.
  - Lista de Indivíduos: Avatar/Foto de rosto, Nome em caixa alta, Vulgo entre aspas, RG/CPF e badge vermelho indicando a quantidade de ocorrências vinculadas.
- **Coluna da Direita (Detail Pane - 60%):**
  - **Perfil do Indivíduo:** Foto ampliada, Nome civil completo, Vulgo, Documentos oficiais e lista de antecedentes criminais.
  - **Histórico de RELINTs Vinculados:** Linha do tempo vertical interativa com todos os boletins em que a pessoa foi citada e qual papel desempenhou em cada um (*Vítima*, *Testemunha*, *Autor/Suspeito*).
  - **Galeria Cruzada:** Todas as fotografias extraídas dos relatórios em que o indivíduo aparece.

---

### 3.4. Aba 4: Estatísticas & Analytics (`#tab-crimes`)
- **Linha Superior (4 KPI Cards):**
  1. *Total de RELINTs Processados* (com indicador percentual).
  2. *Total de Indivíduos Qualificados*.
  3. *Taxa de Leitura Cognitiva por IA (Ollama)*.
  4. *Crimes do Mês / Reincidência Criminal*.
- **Área de Gráficos (ApexCharts Dark):**
  - Gráfico de Rosca/Donut: Distribuição percentual por Grupo BM (Homicídio, Tráfico, Roubo, etc.).
  - Gráfico de Barras/Linha Temporal: Evolução de ocorrências por mês/semana.
  - Ranking de Bairros/Municípios com maior incidência.

---

### 3.5. Aba 5: Galeria Geral de Anexos & Fotos (`#tab-gallery`)
- **Filtro Superior:** Busca por nome do arquivo ou legenda da imagem.
- **Grid Responsivo:** Cards com efeito de zoom no hover, thumbnail recortada em alta definição e legenda descritiva.
- **Visualizador Lightbox Modal (`#lightbox-modal`):**
  - Fundo translúcido com *backdrop-filter blur(8px)*.
  - Exibição em tela cheia com navegação anterior/próxima e legenda detalhada.

---

### 3.6. Aba 6: Monitoramento de Pastas & IA (`#tab-monitoring`)
- **Header:** Título + Seletor de Sub-Abas com botões Resend:
  - Sub-Aba 1: `🖥️ Painel & Console Logs`
  - Sub-Aba 2: `📄 Relatório de Leitura` (com badge numérico dinâmico de relatórios lidos).
- **Sub-Aba 1 (Split View 60% / 40%):**
  - *Lado Esquerdo (Controles):*
    - Seletor de pasta no PC com botão nativo `📁 Procurar Pasta no PC` (`POST /api/v1/monitoring/browse`).
    - Botão principal: Alterna entre `▶ Iniciar Leitura da Pasta` (Verde) e `⏸ Pausar Leitura` (Vermelho).
    - Switch/Botão de Status da IA (Ollama Heartbeat ativo/inativo).
    - 2 Cards com Medidores de Progresso (Barra 1: Arquivos no Disco; Barra 2: Fila Ativa da Sessão).
  - *Lado Direito (Terminal de Logs SSE):*
    - Console estilo terminal escuro com rolagem automática, cores por severidade (INFO em azul/verde, WARN em amarelo, ERROR em vermelho) e botão de limpar console.
- **Sub-Aba 2 (Layout Dividido 20% Gauges / 80% Lista):**
  - *Coluna Esquerda (20%):* 3 Medidores Circulares SVG verticais estilo Apple Watch (`Total na Pasta`, `🟢 Lidos com IA`, `⚡ Lidos com Regex`) com preenchimento animado `stroke-dashoffset`.
  - *Coluna Direita (80%):* Barra de busca + Filtros de extração + Lista de RELINTs com altura contida (`calc(100vh - 200px)`) e scroll customizado.

---

## 4. Modais e Componentes Especiais

### 4.1. Modal de Edição de RELINTs (`#edit-relint-modal`)
- **Abertura:** Acionado pelo botão `✏️ Editar RELINT` no cabeçalho do dossiê.
- **Comportamento:** Grava `user_edited = True` no SQLite ao salvar, imunizando o registro contra sobrescritas automáticas.
- **Navegação em 5 Sub-Abas:**
  1. *Geral:* Assunto, Fato Principal, Data/Hora, Grupo BM, Tipo de Relatório e Unidade Policial.
  2. *Localização:* Município, Bairro, Endereço, Coordenadas GPS e URL de Mapa.
  3. *Especialidade (Polimórfico):* Campos condicionais (se Homicídio: registro policial, delegacia, ano, tipo do fato e motivação).
  4. *Participantes:* Adicionar/remover envolvidos, editar Nome/Vulgo/Documento/Papel e **vincular foto específica da galeria**.
  5. *Transcrição:* Editor de texto da narrativa literal do boletim.

---

## 5. Design Tokens e Sistema de Temas (Dark & Light)

### 5.1. Variáveis Globais CSS ([`variables.css`](file:///e:/www/ReadRelint/src/dashboard/frontend/css/variables.css))
```css
/* Superfícies */
--canvas:           #000000;          /* Light: #fbfbfd */
--surface-card:     #0a0a0c;          /* Light: #ffffff */
--surface-elevated: #101012;          /* Light: #f4f4f6 */
--surface-deep:     #06060a;          /* Light: #eaebee */

/* Hairlines */
--hairline:         rgba(255,255,255,0.06); /* Light: rgba(0,0,0,0.08) */
--hairline-strong:  rgba(255,255,255,0.14); /* Light: rgba(0,0,0,0.16) */

/* Tipografia */
--ink:              #fcfdff;          /* Light: #09090b */
--body:             rgba(252,253,255,0.86); /* Light: rgba(9,9,11,0.88) */
--mute:             #a1a4a5;          /* Light: #71717a */

/* Acentos */
--accent-orange:    #ff801f;          /* Light: #ea580c */
--accent-green:     #11ff99;          /* Light: #16a34a */
--accent-blue:      #3b9eff;          /* Light: #2563eb */
--accent-red:       #ff2047;          /* Light: #dc2626 */
--accent-yellow:    #ffc53d;          /* Light: #d97706 */
```

### 5.2. Classificação Oficial Tripla de Participantes
- **`Vítima`**: Badge azul/ciano com ícone `shield` (`rgba(59,158,255,0.15)` / `#3b9eff`).
- **`Testemunha`**: Badge neutro com ícone `eye` (`rgba(255,255,255,0.08)` / `#e4e4e7`).
- **`Autor/Suspeito`**: Badge vermelho com ícone `user-x` (`rgba(255,32,71,0.15)` / `#ff3b5c`).

---

## 6. Arquitetura de Componentes Recomendada para Svelte 5

Ao migrar para o Svelte 5 com Runes, a árvore de componentes recomendada é:

```text
src/dashboard/frontend_svelte/src/
├── App.svelte                      # Shell principal + roteador de abas + SSE listener
├── lib/
│   ├── stores/
│   │   ├── theme.svelte.js         # Estado reativo de temas (Dark / Light)
│   │   ├── monitoring.svelte.js    # Estado reativo do monitor de pastas e logs SSE
│   │   └── relints.svelte.js       # Cache e seleção ativa de RELINTs
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.svelte      # Menu expansível com botão flutuante e tooltips
│   │   │   └── TopHeader.svelte    # Título, seletor de tema e menu mobile
│   │   │
│   │   ├── ui/
│   │   │   ├── AppleGauge.svelte   # Medidor circular SVG reativo com interpolação
│   │   │   ├── BadgeRole.svelte    # Badge para Vítima / Testemunha / Autor
│   │   │   ├── BadgeMethod.svelte  # Badge Ollama IA / Regex Sem IA
│   │   │   ├── Toast.svelte        # Notificações flutuantes com transition:fade
│   │   │   └── Lightbox.svelte     # Visualizador de imagens com zoom
│   │   │
│   │   └── modals/
│   │       └── EditRelintModal.svelte # Modal em 5 abas com bind bidirecional
│   │
│   └── views/
│       ├── RelintsView.svelte      # Master-Detail de ocorrências
│       ├── HomicidesView.svelte    # Especialidades criminais
│       ├── ParticipantsView.svelte # Dossiê de envolvidos (40/60)
│       ├── CrimesView.svelte       # KPIs + ApexCharts
│       ├── GalleryView.svelte      # Grid de fotos
│       └── MonitoringView.svelte   # Split-view de controles + Terminal de logs
```

---

## 7. Diretrizes de Preservação para a Re-criação
1. **Posicionamento Idêntico:** A Sidebar permanece à esquerda com o botão flutuante exatamente no mesmo local (`right: -12px; top: 18px`).
2. **Layouts de Colunas:** 
   - Participantes preserva a divisão **40% Master / 60% Detail**.
   - Monitoramento Sub-Aba 1 preserva a divisão **60% Controles / 40% Terminal**.
   - Monitoramento Sub-Aba 2 preserva a divisão **20% Gauges Circulares / 80% Lista**.
3. **Consistência de Rotas REST:** Nenhuma alteração nos endpoints existentes do FastAPI (`/api/v1/relints`, `/participants`, `/monitoring/*`, `/events`).
