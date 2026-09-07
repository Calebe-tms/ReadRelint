# ADR-0049: Transformação do App Desktop em Service Launcher & Hub (Zero Overhead)

- Status: Aceita
- Data: não registrada

## Contexto
A interface desktop (Tkinter) vinha acumulando responsabilidades de renderização pesada (listas longas, gráficos) que competiam por recursos com a main thread do Python, causando travamentos, enquanto o Dashboard Web já cumpria esse papel de forma mais adequada.

## Decisão
O aplicativo Tynker (Tkinter) foi limpo de todas as abas pesadas de relatórios e painéis complexos. Ele agora atua exclusivamente como um Hub minimalista (480x580) de status para ligar/desligar serviços (Monitor de Pasta, Servidor Web e IA). Isso delegou todo o trabalho pesado de renderização de listas infinitas, gráficos e logs (SSE) puramente para o Dashboard Web, zerando travamentos na Main Thread do Python.

## Consequências
Elimina travamentos na interface desktop ao remover renderização pesada de sua main thread, tornando-a um launcher leve e estável. Centraliza toda a experiência analítica no Dashboard Web, reforçando a divisão de papéis entre os dois frontends.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
