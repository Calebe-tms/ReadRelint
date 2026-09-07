# ADR-0021: Remoção Completa do Streamlit

- Status: Aceita
- Data: não registrada

## Contexto
Após a migração para FastAPI + frontend custom (ADR-018), o código e as dependências do Streamlit tornaram-se código morto no repositório.

## Decisão
Limpeza de dependências e código do Streamlit.

## Consequências
Reduz a superfície de dependências e o tamanho do projeto, eliminando confusão sobre qual stack de UI está realmente em uso. Não há efeito funcional, apenas limpeza técnica.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
