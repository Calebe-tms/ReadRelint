---
description: Workflow para espelhar e gerar no Penpot 100% dos componentes do sistema, garantindo paridade total entre o código Svelte 5 e a prancheta Design System Library Components, com amarração estrita aos Core Tokens.
---

# Workflow de Geração e Espelhamento no Penpot (`/export-to-penpot`)

Este workflow é responsável por ler os componentes e tokens da aplicação web (`frontend/src/themes/dark-theme/style.css` e `frontend/src/lib/components/ui/`) e recriar/atualizar de forma idêntica a prancheta **`Design System Library Components`** no Penpot, transformando cada elemento em Componente Oficial da Biblioteca vinculado exclusivamente a **Design Tokens do conjunto `Core Tokens`**.

---

## 🚫 Regra Estrita Antitoxidade de Ativos (Anti-Assets Rule)

> [!CAUTION]
> **NUNCA crie cores ou tipografias na aba de Ativos (`localLib.colors` ou `localLib.typographies`).**
> - O Penpot separa **Ativos (Assets)** de **Design Tokens**.
> - O Design System do ReadRelint opera **100% via Design Tokens** (`Core Tokens`).
> - O script de exportação DEVE conter limpeza preventiva de `localLib.colors` e `localLib.typographies` para garantir que a aba de ativos permaneça com contagem zero.
> - Toda e qualquer estilização visual em shapes DEVE ser vinculada via `shape.applyToken(token, ["fill" | "strokeColor" | "borderRadius..." | "typography"])`.

---

## Etapas do Workflow

### 1. Leitura dos Componentes e Tokens no Código
O agente analisa:
- O arquivo de tokens oficial: `frontend/src/themes/dark-theme/style.css`;
- Todos os componentes Svelte 5 em `frontend/src/lib/components/ui/`:
  - `Button.svelte`
  - `Badge.svelte`
  - `Card.svelte`
  - `StatCard.svelte`
  - `Input.svelte`
  - `Switch.svelte`
  - `Table.svelte`
  - `Alert.svelte`
  - `Modal.svelte`
  - `Tabs.svelte`
- A rota viva `frontend/src/routes/design-system/+page.svelte`.

### 2. Higienização e Preparação no Penpot
O agente executa o script via MCP (`execute_code`) executando:
1. Limpeza preventiva de ativos soltos: `localLib.colors.forEach(c => c.remove())` e `localLib.typographies.forEach(t => t.remove())`;
2. Localização e validação do conjunto único oficial de tokens: `Core Tokens`;
3. Remoção e recriação limpa da prancheta `Design System Library Components`.

### 3. Construção das Seções na Prancheta Oficial
A prancheta deve conter com alinhamentos perfeitos na grade de 4px:
1. **Cartões de Métrica (`StatCard`)**: Fundo `colors.background.surface-card`, borda `colors.border.subtle`, valor 32px display em `colors.amber.primary`, chip percentual e descrição.
2. **Botões (`Button`)**: Variantes `Primary`, `Glow`, `Secondary`, `Outline`, `Ghost`, `Danger`, `Disabled` com raio `radius.sm` (8px) e escala de tamanhos (32px, 40px, 48px).
3. **Badges / Tags (`Badge`)**: Variantes `Amber`, `Success`, `Warning`, `Error`, `Info`, `Neutral` com raio `radius.xs` (4px), dot indicador e tamanhos (20px, 24px).
4. **Navegação & Formulários (`Tabs`, `Input`, `Switch`)**:
   - Card com inputs (`Default`, `Focus` com halo âmbar, `Error` com borda vermelha) e switches estilo Apple;
   - Card translúcido com barra de abas segmentadas e indicador ativo âmbar.
5. **Tabela de Dados (`Table`)**: Grade com cabeçalho `colors.background.secondary`, linhas zebradas, códigos em `JetBrains Mono` e botões de ação.
6. **Alertas e Notificações (`Alert`)**: Variantes `Info`, `Success`, `Warning`, `Error` com borda contínua fina de 1px e fundos translúcidos semânticos.

### 4. Registro Oficial como Library Components e Vínculo de Tokens
- Cada elemento gerado é registrado na biblioteca de componentes do Penpot via `localLib.createComponent()`.
- Todas as propriedades visuais (preenchimentos, bordas, raios e tipografia) são amarradas diretamente aos tokens do conjunto **`Core Tokens`** através de `shape.applyToken()`.

### 5. Validação com `svelte-check`
- Executar `npm run check` para garantir 0 erros e 0 avisos.
- Confirmar que a visualização web em `http://localhost:5173/design-system` e o canvas do Penpot possuem paridade visual 1:1.
