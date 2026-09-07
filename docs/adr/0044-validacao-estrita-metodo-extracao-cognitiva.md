# ADR-0044: Validação Estrita do Método de Extração Cognitiva (`isLlmExtraction`)

- Status: Aceita
- Data: não registrada

## Contexto
A checagem ingênua por substring `'IA'` produzia um bug de rotulagem onde relatórios extraídos por Regex (sem IA) eram exibidos como se tivessem sido extraídos por IA, já que a própria string "Sem IA" contém a substring buscada.

## Decisão
Eliminação do falso-positivo na rotulagem dos relatórios Web. A verificação anterior utilizava `.includes('IA')`, que avaliava `true` para a string "Regex (Sem IA)" por conter o substring 'IA'. Implementação da função `isLlmExtraction` verificando a presença explícita de "Ollama" ou "LLM" e descartando "Sem IA" e "Regex", além do ajuste do fallback do schema `/api/v1/relints` para "Regex (Sem IA)".

## Consequências
Corrige a rotulagem visual dos relatórios, restaurando a confiabilidade do badge de método de extração (ADR-030) que dependia dessa checagem. É uma correção de bug pontual, sem mudança de comportamento além do esperado.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
