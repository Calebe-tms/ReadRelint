# ADR-0067: Desacoplamento da Checagem de Rede da LLM da UI Main Thread

- Status: Aceita
- Data: não registrada

## Contexto
Após a migração para PyQt6 (ADR-066), um timer periódico fazia requisições HTTP síncronas para checar o status do Ollama diretamente na main thread da UI, bloqueando a interface por até 3 segundos a cada verificação quando o serviço estava lento ou indisponível.

## Decisão
Remoção da requisição síncrona HTTP `requests.get` do timer contínuo de 2 segundos do PyQt. A verificação do status do Ollama foi convertida para ação sob demanda (botão "Testar Conexão" e alternância de switch), zerando completamente os travamentos de 3s e mantendo a interface desktop a 60 FPS fluidos.

## Consequências
Elimina completamente os travamentos periódicos da interface desktop, mantendo-a fluida a 60 FPS. A checagem deixa de ser automática e contínua, passando a depender de ação explícita do usuário para verificar a conexão com a IA.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
