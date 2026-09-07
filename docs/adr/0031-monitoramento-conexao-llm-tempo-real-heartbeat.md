# ADR-0031: Monitoramento de Conexão da LLM em Tempo Real (Heartbeat)

- Status: Aceita
- Data: não registrada

## Contexto
Como o Ollama roda como serviço local separado, ele pode ser fechado ou travar a qualquer momento sem aviso, e o sistema precisa detectar isso rapidamente para não tentar extrair dados via IA indisponível e travar o pipeline.

## Decisão
Execução de polling assíncrono leve a cada 4 segundos (`check_llm_heartbeat`). Em caso de interrupção ou fechamento do serviço Ollama, o sistema desativa o switch visual da IA, notifica no console de log e faz fallback instantâneo sem perda de dados para o pipeline Regex.

## Consequências
Garante continuidade do processamento (fallback automático para Regex) mesmo quando a IA cai, sem intervenção manual. O polling constante, porém, adiciona uma pequena carga contínua de checagem em segundo plano.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
