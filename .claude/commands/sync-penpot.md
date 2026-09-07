---
description: Workflow obrigatório para inspeção e sincronização 1:1 do Penpot com os componentes do sistema
---

# Workflow de Sincronização e Auditoria do Penpot (`/sync-penpot`)

Este workflow define as etapas obrigatórias que o agente deve executar sempre que o desenvolvedor solicitar a sincronização de componentes e tokens do Penpot para o código Svelte.

---

## 🚫 Regra de Ouro: Design Tokens Nativos (`Core Tokens`)
- A inspeção DEVE extrair as propriedades vinculadas a tokens do conjunto **`Core Tokens`**.
- Cores soltas na aba de ativos são consideradas anomalias e devem ser convertidas em tokens de `Core Tokens`.
- Todo estilo gerado em Svelte deve consumir estritamente variáveis CSS (`var(--token)`) mapeadas em `frontend/src/themes/dark-theme/style.css`.

---

## Etapas do Workflow

### 1. Extração Profunda via MCP (`execute_code`)
O agente DEVE rodar um script no Penpot para capturar o JSON de propriedades reais de **todos** os componentes (`Design System Library Components` e tokens da biblioteca `Core Tokens`):
- Preenchimento exato (`fills`: token name, cor hex e opacidade);
- Borda exata (`strokes`: token name, cor hex, espessura, alinhamento);
- Cantos arredondados (`borderRadius`: tokens `radius.xs`, `radius.sm`, `radius.md`, `radius.lg`, `radius.full`);
- Tipografia de cada texto (`typography` token, `fontFamily`, `fontSize`, `fontWeight`, `textTransform`);
- Dimensões e espaçamentos múltiplos de 4px (`width`, `height`, `padding`).

### 2. Matriz de Auditoria e Mapeamento 1:1
O agente deve cruzar o JSON extraído com os arquivos do SvelteKit sem assumir NENHUM estilo padrão:

| Componente | Propriedades Críticas a Auditar no Penpot | Arquivo Alvo |
| :--- | :--- | :--- |
| **`Card`** | Fundo exato (`--color-bg-surface-card`), cor e espessura da borda, raio | `src/lib/components/ui/Card.svelte` |
| **`Alert`** | Borda contínua de 1px, raio de 8px, fundo translúcido semântico | `src/lib/components/ui/Alert.svelte` |
| **`Badge`** | Opacidade do fundo (14%), borda (1px), fonte (*Elms Sans*), caixa alta, dot | `src/lib/components/ui/Badge.svelte` |
| **`StatCard`** | Fundo escuro, valor 32px display em Âmbar (`--color-amber-primary`), chip percentual | `src/lib/components/ui/StatCard.svelte` |
| **`Button`** | Preenchimentos das variantes (`Primary`, `Glow`, `Secondary`, `Outline`, `Ghost`, `Danger`), caixa alta, raio 8px | `src/lib/components/ui/Button.svelte` |
| **`Table`** | Fundo do cabeçalho (`--color-bg-secondary`), linhas zebradas com hover, códigos em *JetBrains Mono* | `src/lib/components/ui/Table.svelte` |
| **`Input`** | Fundo escuro, borda padrão e borda de foco com halo âmbar | `src/lib/components/ui/Input.svelte` |
| **`Switch`** | Trilha de 24px com botão de 20px, cores ativo/inativo estilo Apple | `src/lib/components/ui/Switch.svelte` |
| **`Modal`** | Backdrop translúcido com blur 16px, container com raio de 16px | `src/lib/components/ui/Modal.svelte` |
| **`Tabs`** | Controle segmentado com abas ativas em âmbar e badges numéricos | `src/lib/components/ui/Tabs.svelte` |

### 3. Verificação de Tokens Faltantes
- Se qualquer componente usar uma cor, raio ou tipografia que não exista em `src/themes/dark-theme/style.css`, adicionar ao `Core Tokens` e ao CSS oficial.

### 4. Aplicação Atômica das Mudanças
- Atualizar os arquivos Svelte e CSS correspondentes.

### 5. Validação Técnica
- Executar `npm run check` (`svelte-check`) garantindo 0 erros e 0 avisos.
- Atualizar os arquivos de contexto (`docs/project-state.md`).
