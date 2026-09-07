# ADR-0098: Coordenadas Sempre Normalizadas em 6 Casas Decimais (Padrão Google Maps)

- Status: Aceita
- Data: não registrada

## Contexto
Como cada boletim de origem citava coordenadas com uma precisão diferente (de poucos dígitos a mais de uma dezena), o banco acumulava coordenadas com formatação inconsistente entre registros, o que não afetava a exatidão mas dificultava comparação e padronização dos dados salvos.

## Decisão
`enforce_rs_coordinate_signs()` (`backend/engine/cleaners/text_cleaner.py`, usada tanto pelo motor LLM quanto pelo determinístico) agora formata toda coordenada final com `f"{lat:.6f}, {lon:.6f}"` em vez de preservar a string de dígitos original do documento. Antes, a precisão salva variava com o que o documento continha (de 3 a 14+ dígitos, ex: `-28.6914035686101, -53.62326597234348`), inconsistente entre registros. Agora: precisão excedente é arredondada, precisão insuficiente é completada com zero — sempre 6 dígitos, o mesmo padrão usado pelo Google Maps. Validação de faixa geográfica do RS e rejeição de placeholders continuam intactas, só a formatação final da saída mudou.

## Consequências
Padroniza a apresentação de todas as coordenadas no mesmo formato usado pelo Google Maps, tornando os dados mais consistentes para exibição e comparação. É uma mudança puramente de formatação de saída — as validações de faixa geográfica e rejeição de placeholders (ADR-092) continuam funcionando como antes.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
