# ADR-0041: Inicialização Autônoma Web-Only (`start_web.py` e Workflow `/run`)

- Status: Aceita
- Data: não registrada

## Contexto
Para desenvolvimento e para usuários que só precisam do dashboard web, subir toda a aplicação desktop (PyQt6) apenas para iniciar os servidores era um overhead desnecessário de tempo de boot e de recursos.

## Decisão
Criação de script Python autônomo e de alta velocidade para inicializar apenas o servidor Uvicorn (FastAPI :8000) e o Vite Dev Server (SvelteKit :5173) em segundo plano, abrindo o navegador padrão diretamente na interface web sem a necessidade de subir o loop de eventos desktop do PyQt6.

## Consequências
Reduz drasticamente o tempo de inicialização para o fluxo web-only, sem depender do loop de eventos do PyQt6. Cria, porém, um segundo caminho de inicialização do sistema que precisa ser mantido em paralelo ao fluxo desktop completo.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
