# Especificação: Gerenciador de RELINTs (Master-Detail 30/70)

> ⚠️ **SUPERADO** — Este documento descreve a interface HTML/JS vanilla anterior à migração para SvelteKit (ver ADR-076, "App Shell & Estrutura do Dashboard SvelteKit"). Mantido apenas como registro histórico de design; não reflete a UI atual do sistema.

Este documento descreve a especificação técnica e comportamental da página de **Gerenciamento Geral dos RELINTs** na rota `/relints`, adotando o padrão **Master-Detail (30% / 70%)** alinhado ao nosso Design System em Svelte 5.

---

## 1. Arquitetura de Layout: Master-Detail (30% / 70%)

A interface elimina modais centrais para garantir navegação contínua e sem interrupções:

### ⬅️ Coluna Esquerda: Lista Master Compacta (30% da largura)
- **Barra de Controle Superior**:
  - Campo de busca em tempo real (por assunto, código ou participante).
  - Filtros rápidos por Especialidade (Homicídio, Tráfico de Drogas, Roubos e Furtos, Geral).
- **Lista de Cards Ultracompactos**:
  - Exibe o código do RELINT (ex: `RELINT-2026-001`), o assunto resumido e a data do fato.
  - **Sinalização Visual por Mini-Ícones (Pixel-Perfect)**:
    - **Especialidade**: `<Crosshair color="red" />` (Homicídio), `<Pill color="orange" />` (Tráfico), `<ShieldWarning color="blue" />` (Roubos/Furtos) ou `<FileText color="gray" />` (Geral).
    - **Situação de Revisão**: `<CheckCircle color="green" />` para **Revisado por Humano** (`user_edited = true`) e `<Clock color="gray" />` para **Pendente Revisão**.
  - **Navegação Contínua**: Seleção via clique ou teclas de atalho (setas ↑ e ↓), atualizando instantaneamente o painel de detalhes à direita.

### ➡️ Coluna Direita: Workspace de Detalhes (70% da largura)
Exibe o relatório completo selecionado, com fluxo de **Somente Leitura por Padrão** e alternância de edição:

- **Modo de Exibição / Somente Leitura**:
  - Por padrão, os campos permanecem desabilitados para leitura confortável e sem edições acidentais.
  - O botão de ação no topo exibe **`EDITAR DADOS`** com o ícone `PencilSimple`.
- **Modo de Edição**:
  - Ao clicar em `EDITAR DADOS`, o formulário libera os campos e o botão altera para **`SALVAR E MARCAR REVISADO`** (`FloppyDisk`).
  - Ao salvar, a flag `user_edited = true` é atribuída, ativando o badge de curadoria e retornando a interface ao modo somente leitura.

- **Navegação em 5 Sub-Abas com Ícones (`Tabs.svelte`)**:
  1. **Aba 1: Geral (`<Info />`)**: Resumo, Assunto, Data do Fato, Número de Registro Policial (`numero_registro`), Órgão e Ano.
  2. **Aba 2: Localização (`<MapPin />`)**: Endereço estruturado, Bairro, Município e nível de precisão geográfica.
  3. **Aba 3: Especialidade (`<Shield />`)**: Formulário polimórfico adaptativo (exibe campos de Homicídios como motivação, delegacia e meio empregado quando a especialidade for *Homicídio*).
  4. **Aba 4: Participantes (`<UserList />`)**: Cards Policiais de Indivíduos (Avatar/Foto, Nome, Alcunha, Função: *Autor/Vítima/Testemunha*) + Modal/Ações de edição quando em modo ativo.
  5. **Aba 5: Transcrição Bruta (`<Article />`)**: Texto integral do boletim com realce visual (*highlight*) de entidades e botão de "Copiar Texto".

---

## 2. Indicadores e Estilização no Design System

- **Badge de Status "Revisado" (Header do Workspace)**:
  - Ícone: `CheckCircle` (Phosphor Icons em formato `fill`).
  - Texto: **Revisado**.
  - Variante: `success` (verde escuro com brilho sutil).
- **Indicadores da Lista Lateral**:
  - Uso de mini-ícones de 14px com suporte a `title` (tooltip nativo ao passar o mouse).
- **Responsividade**: Em telas menores (mobile/tablet < 992px), a lista master recolhe em um painel responsivo com suporte a toque.

---

## 3. Integração com a API REST (FastAPI)
- `GET /api/v1/relints`: Carregamento e atualização da lista master e detalhes.
- `PUT /api/v1/relints/{id}`: Envio das alterações editadas no workspace (atualiza `user_edited = true` e grava o badge "Revisado").
