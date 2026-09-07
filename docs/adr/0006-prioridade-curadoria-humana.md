# ADR-0006: Prioridade da Curadoria Humana

- Status: Aceita
- Data: não registrada

## Contexto
Como o sistema reprocessa PDFs (por exemplo após ajustes no pipeline de extração), existe o risco de que uma correção manual feita por um analista seja perdida se o mesmo arquivo for lido novamente pela IA.

## Decisão
Uso do `processed_registry.json` para gravar edições efetuadas pelo usuário humano e forçar que a IA nunca sobrescreva alterações humanas caso o PDF seja reprocessado.

## Consequências
Correções humanas tornam-se permanentes e confiáveis, incentivando a curadoria manual. Por outro lado, o sistema precisa manter e consultar esse registro de edições a cada reprocessamento, adicionando uma camada extra de estado a sincronizar.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
