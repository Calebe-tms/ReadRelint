# ADR-0072: Unificação do Ciclo de Vida do Servidor Web (FastAPI + SvelteKit)

- Status: Aceita
- Data: não registrada

## Contexto
Com a adoção do SvelteKit como novo frontend, o sistema passou a depender de dois servidores distintos (backend FastAPI e dev server SvelteKit); gerenciar cada um separadamente na interface desktop duplicaria controles e aumentaria o risco de um subir sem o outro.

## Decisão
Controle conjunto do FastAPI (:8000) e SvelteKit (:5173) acionado sob demanda no botão da Aba 1 ("Iniciar & Abrir Dashboard" / "Parar Dashboard Web").

## Consequências
Simplifica a experiência do usuário para um único botão que garante os dois serviços sobem e descem juntos de forma coerente. Acopla o ciclo de vida dos dois processos, exigindo tratamento cuidadoso de erro caso um deles falhe ao iniciar enquanto o outro sobe normalmente.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
