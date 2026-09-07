---
description: Diretrizes de Perfect Pixel e Grade Base de 4px para criação de Tokens e Componentes de UI
---

# Regra: Perfect Pixel e Grade Base de 4px (Tokens e Componentes de UI)

Esta regra é ativada estritamente durante a criação, refatoração ou sincronização de **Design Tokens** e **Componentes de UI** (Svelte e Penpot).

---

## 1. Princípio da Grade Base de 4px (4px Baseline Grid)
- **Zero Frações de Pixel**: É terminantemente proibido utilizar valores decimais ou frações de pixel (ex: `13.5px`, `0.33rem` sem conversão exata) em dimensões, espaçamentos ou alturas de linha.
- **Espaçamentos e Dimensões**: Todos os `paddings`, `margins`, `gaps`, `widths` e `heights` de componentes devem ser múltiplos inteiros de 4px (`4px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`, `40px`, `48px`, etc.).

---

## 2. Tipografia e Altura de Linha (Line-Height) Congruente
- **Line-Height Obrigatório em Múltiplo de 4px**:
  Toda definição de tipografia DEVE possuir um `line-height` fixo e exato que seja múltiplo de 4px:

| Token de Tipografia | Font Size | Line-Height (4px Grid) | Uso |
| :--- | :--- | :--- | :--- |
| **`typography.display-lg`** | `32px` | **`40px`** | Títulos principais |
| **`typography.display-md`** | `24px` | **`32px`** | Cabeçalhos de painéis e modais |
| **`typography.title-section`** | `18px` | **`24px`** | Títulos de cards e seções |
| **`typography.body-large`** | `16px` | **`24px`** | Textos longos e relatórios |
| **`typography.body-medium`** | `14px` | **`20px`** | Texto base de formulários e tabelas |
| **`typography.body-small`** | `12px` | **`16px`** | Legendas e notas de rodapé |
| **`typography.ui-button`** | `13px` | **`20px`** | Rótulos de botões |
| **`typography.ui-badge`** | `11px` | **`16px`** | Badges e chips de status |
| **`typography.code-metric`** | `13px` | **`16px`** | Identificadores e códigos técnicos |

---

## 3. Altura de Componentes e Alinhamento Vertical
- A altura final calculada de qualquer elemento interativo (`Button`, `Input`, `Badge`, `Switch`, linha de `Table`) deve fechar em múltiplos de 4px e 8px:
  - `Badge / Tag`: **`24px`** ou **`28px`**
  - `Button Sm`: **`32px`**
  - `Button Md` / `Input`: **`40px`** ou **`44px`**
  - `Button Lg`: **`48px`**
- Em alinhamentos horizontais (ex: Botão ao lado de Input ou Ícone ao lado de Badge), as alturas de linha e paddings devem coincidir matematicamente para eliminar qualquer salto de pixel.
