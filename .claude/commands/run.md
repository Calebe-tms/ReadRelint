---
description: Inicia os serviços do ReadRelint (FastAPI + SvelteKit) e abre o navegador automaticamente
---

# Workflow: Run (Iniciar FastAPI + SvelteKit)

Execute o comando abaixo para iniciar o backend e o frontend web e abrir no navegador:

```powershell
& .\.venv\Scripts\python.exe start_web.py
```

### O que o comando faz automaticamente:
1. Inicia o **Backend FastAPI** (`:8000`) em segundo plano via Uvicorn.
2. Inicia o **Frontend SvelteKit** (`:5173`) em segundo plano via Vite.
3. Aguarda os serviços responderem e abre automaticamente o navegador em `http://localhost:5173`.
