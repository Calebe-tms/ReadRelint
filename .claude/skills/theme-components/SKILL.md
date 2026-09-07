---
name: svelte-dashboard-architect
description: Força o agente a usar variáveis CSS, slots e animações nativas no Svelte.
version: 1.0.0
---

**Goal:**
Construir componentes de UI para Svelte com separação estrita de temas, alta reutilização (Headless) e animações padronizadas.

**Requirements:**
1. Conhecimento e acesso prévio ao `themes.css` do projeto.
2. Uso exclusivo dos recursos de `svelte/transition`.

**Steps:**
1. Temas: É estritamente proibido inserir cores em Hex/RGB ou pixels fixos no bloco `<style>`. O agente deve consumir apenas `var(--token)`.
2. Isolamento (Headless): Construa a casca do layout, mas delegue o conteúdo via `<slot>`. Comunique-se via `createEventDispatcher`.
3. Animações: Aplique wrappers de transição encapsulados em vez de poluir os componentes de negócio.

**Verification:**
1. O componente busca dados ativamente? Falhe a validação e refatore para receber dados apenas via propriedades.
2. Existe algum `#hex` fixo no estilo gerado? Falhe e exija a substituição pela variável correspondente do tema.

