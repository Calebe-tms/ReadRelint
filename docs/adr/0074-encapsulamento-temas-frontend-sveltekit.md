# ADR-0074: Encapsulamento dos Temas no Frontend SvelteKit (`frontend/src/lib/themes`)

- Status: Aceita
- Data: não registrada

## Contexto
Manter os arquivos de tema CSS na raiz do repositório, fora da estrutura do projeto SvelteKit, misturava ativos de frontend com arquivos de infraestrutura geral do repositório, dificultando a organização do fluxo de build do SvelteKit.

## Decisão
Realocação da pasta de temas `themes/` da raiz do repositório para `frontend/src/lib/themes/`. Os temas CSS (`resend-dark`, `resend-light`) passam a ser importados via `@import` no `variables.css` dentro do fluxo do SvelteKit ($lib), isolando os ativos visuais no escopo da aplicação frontend.

## Consequências
Organiza os ativos visuais dentro do escopo correto da aplicação frontend, seguindo as convenções do SvelteKit ($lib). É uma reorganização estrutural sem impacto visual, preparando terreno para a limpeza mais ampla de temas legados na ADR seguinte.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
