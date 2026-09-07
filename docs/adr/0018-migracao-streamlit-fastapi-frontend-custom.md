# ADR-0018: Migração de Streamlit para FastAPI + Frontend Custom

- Status: Aceita
- Data: não registrada

## Contexto
O Streamlit, apesar de rápido para prototipar, impõe limitações de customização de layout, performance de recarregamento e controle fino sobre o comportamento da interface — restrições que passaram a pesar à medida que o dashboard ganhou complexidade.

## Decisão
Decisão de substituir o Streamlit por uma arquitetura **FastAPI (backend API REST)** + **Frontend HTML/CSS/JS puro**.

## Consequências
Ganho de liberdade total sobre UI/UX e de uma API REST reutilizável por outros clientes (como o app desktop). O custo é a necessidade de construir manualmente componentes de interface que o Streamlit oferecia prontos.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
