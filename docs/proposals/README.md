# Propostas Técnicas

Esta pasta guarda propostas técnicas em avaliação ou parcialmente implementadas — documentos de trabalho que descrevem um problema, suas causas-raiz e um plano de correção ou melhoria, antes de virarem decisão definitiva. Diferente das ADRs em [`../adr/`](../adr/), que são registros imutáveis de uma decisão já tomada, as propostas aqui podem ser atualizadas conforme a implementação avança (ver o campo `Status` no topo de cada uma).

Quando uma proposta é totalmente aceita e implementada, uma ADR nova é criada em `docs/adr/` documentando a decisão final, e a proposta correspondente pode ser marcada como resolvida aqui — o arquivo não é apagado, permanece como registro histórico do raciocínio que levou à decisão.

## Propostas atuais

- [`melhorias-extracao-geo.md`](./melhorias-extracao-geo.md) — Correção de inconsistências na extração de localização/unidade policial (parcialmente implementada).
- [`termometro-certeza.md`](./termometro-certeza.md) — Termômetro de certeza generalizado por campo extraído (pendente).
- [`eliminacao-pass1-legado.md`](./eliminacao-pass1-legado.md) — Eliminação do Pass 1 legado monolítico do pipeline LLM, redistribuindo campos entre determinismo e passes dedicados (pendente).
