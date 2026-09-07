# ADR-0064: Reversão do Docling e Manutenção do PyMuPDF

- Status: Aceita
- Data: não registrada

## Contexto
Buscando melhorar a estruturação do texto extraído de PDFs, o time avaliou o Docling como alternativa ao PyMuPDF, mas na prática o texto convertido para Markdown introduziu artefatos de formatação que confundiam o LLM em vez de ajudá-lo.

## Decisão
Tentativa de integração com a biblioteca `Docling` para extração estruturada de PDFs (convertendo para Markdown) foi revertida. O uso do Docling inseriu ruídos indesejados no texto bruto, tags de estruturação desnecessárias e prejudicou a qualidade da leitura do modelo LLM. Decisão de manter e priorizar exclusivamente o `PyMuPDF` (fitz) que oferece extração de texto muito mais veloz, crua e previsível para o nosso caso de uso.

## Consequências
Mantém a extração de texto rápida, crua e previsível, sobre a qual todo o pipeline de limpeza e prompts já havia sido calibrado. Registra formalmente que essa alternativa foi avaliada e descartada, evitando que seja retentada sem justificativa nova no futuro.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
