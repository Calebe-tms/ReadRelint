# ADR-0009: Suíte de Testes 100% Mockada

- Status: Aceita
- Data: não registrada

## Contexto
Depender do Ollama real ou de arquivos PDF físicos nos testes tornaria a suíte lenta, frágil a variações do modelo de IA e dependente de infraestrutura local, inviabilizando execução rápida em CI.

## Decisão
O `pytest` usa fixtures de memória (`tmp_path`) e mocks simulando Ollama e PyMuPDF para executar CI instantâneo.

## Consequências
A suíte roda de forma rápida e determinística, sem depender de um serviço Ollama disponível ou de PDFs reais. A contrapartida é que os mocks podem divergir do comportamento real do Ollama/PyMuPDF ao longo do tempo, exigindo atenção para não mascarar regressões de integração.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
