# ADR-0035: Proteção contra Desconexões Falso-Positivas de IA

- Status: Aceita
- Data: não registrada

## Contexto
Durante uma inferência pesada do Ollama, a checagem de heartbeat (ADR-031) podia interpretar a lentidão momentânea como queda de serviço, desligando a IA por engano e interrompendo a fila de processamento sem necessidade real.

## Decisão
Otimização da verificação de conexão com Ollama durante a inferência pesada para impedir desativação automática da chave de IA e pausas involuntárias na fila de monitoramento.

## Consequências
Reduz falsos positivos de desconexão, mantendo o pipeline de IA ativo durante picos de carga legítimos de inferência. Exige calibrar com cuidado os limites de tempo entre lentidão aceitável e queda real de serviço.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
