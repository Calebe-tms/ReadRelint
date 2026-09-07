# ADR-0077: Transições Suaves Aceleradas por Hardware (Apple WWDC Fluid Motion)

- Status: Aceita
- Data: não registrada

## Contexto
A troca de páginas e de dossiês no novo dashboard SvelteKit podia ocorrer de forma abrupta, sem transição visual, o que contrasta com o padrão de fluidez perseguido para a experiência do usuário em outras partes do sistema.

## Decisão
Implementação de animações CSS nativas (`.page-enter-animation` e `.relint-enter-animation`) utilizando curvas cúbicas de alta precisão (`cubic-bezier(0.16, 1, 0.3, 1)`) e diretiva `will-change: opacity, transform`, garantindo transições de páginas e troca de dossiês a 60/120 FPS sem travamentos ou layout shift.

## Consequências
Dá à navegação uma sensação fluida e polida, aproveitando aceleração por hardware (`will-change`) para manter alta taxa de quadros. Exige atenção ao uso de `will-change` para não consumir memória de GPU desnecessariamente em elementos que não estão de fato animando.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
