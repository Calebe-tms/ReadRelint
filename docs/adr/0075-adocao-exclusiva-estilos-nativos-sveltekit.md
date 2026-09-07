# ADR-0075: Adoção Exclusiva de Estilos Nativos no SvelteKit (Limpeza de Temas Customizados Legados)

- Status: Aceita
- Data: não registrada

## Contexto
Mesmo após o encapsulamento das pastas de tema (ADR-074), o projeto ainda mantinha uma camada de temas customizados paralela ao sistema de estilização nativo do SvelteKit (CSS escopado por componente), gerando duas formas concorrentes de estilizar a aplicação.

## Decisão
Remoção completa das pastas de temas customizadas não-nativas (`src/lib/themes/` e `src/css/themes/`). O sistema de estilização passa a ser 100% nativo do SvelteKit utilizando tokens globais em `app.css` / `variables.css` e CSS escopado de componentes Svelte, garantindo performance e manutenção simples sem dependências de arquivos externos.

## Consequências
Simplifica definitivamente a arquitetura de estilos, eliminando uma fonte de duplicidade e dependência externa. Exige que toda customização visual futura seja feita via tokens globais e CSS escopado por componente, sem reintroduzir arquivos de tema paralelos.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
