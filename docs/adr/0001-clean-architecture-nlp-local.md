# ADR-0001: Clean Architecture e NLP Local

- Status: Aceita
- Data: não registrada

## Contexto
O sistema processa RELINTs — documentos de inteligência policial que contêm dados pessoais sensíveis sujeitos à LGPD. Usar uma API de LLM na nuvem para extração cognitiva criaria risco de vazamento desses dados para terceiros e dependência de conectividade externa.

## Decisão
Isolamento total via Ports e Adapters. Uso exclusivo do `Ollama` rodando localmente, evitando quebras de LGPD (nenhum PDF sai da máquina).

## Consequências
Conformidade com LGPD garantida por design, sem dependência de conectividade externa ou custos de API por chamada. Como contrapartida, a qualidade de extração fica limitada à capacidade de modelos locais (menores que os de nuvem), e o sistema exige que o usuário tenha hardware capaz de rodar Ollama.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
