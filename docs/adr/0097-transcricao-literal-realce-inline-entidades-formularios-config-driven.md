# ADR-0097: Transcrição Literal com Realce Inline de Entidades & Formulários de Especialidade Config-Driven

- Status: Aceita
- Data: não registrada

## Contexto
A aba de transcrição exibia o texto bruto do boletim sem nenhuma ligação visual com os dados já extraídos e validados pelo pipeline, obrigando o analista a comparar mentalmente o texto corrido com os campos estruturados; já a aba de especialidade era um formulário fixo desenhado só para Homicídio, incluindo campos que nunca existiram de fato no backend, e portanto inútil para as outras 6 especialidades.

## Decisão
`TabTranscription.svelte`: fonte trocada de monoespaçada compacta para `--font-family-main` no tamanho `body-large` do design system (16px/24px), corrigindo também uma variável CSS inexistente (`--line-height-160`) que estava quebrada. Realce inline (`<mark>`) de tudo que o pipeline já resolveu deterministicamente e que aparece literalmente no texto bruto (coordenadas, endereço, município e link do mapa em verde translúcido) e participantes realçados por papel (Autor/Suspeito vermelho, Vítima âmbar, Testemunha azul), com fronteira de palavra Unicode-aware para nomes acentuados. Badges de legenda só aparecem quando o tipo correspondente realmente tem ocorrência no texto. `TabSpecialty.svelte`: reescrito de um formulário fixo só-Homicídio (com 2 campos fantasmas que nunca existiram no backend) para um renderizador config-driven (`SPECIALTY_CONFIG`) cobrindo as 7 especialidades, usando exatamente os campos que a API já expõe. Mutação do objeto de detalhes movida de dentro do `$derived` para um `$effect` (Svelte 5 proíbe mutar `$state` dentro de `$derived`).

## Consequências
A transcrição passa a funcionar como uma camada de verificação visual, permitindo ao analista confirmar rapidamente que um dado extraído realmente aparece no texto original. O formulário de especialidade config-driven elimina os campos fantasmas e passa a escalar automaticamente para as 7 especialidades sem duplicar código de formulário por tipo.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
