# ADR-0039: Execução Direta por Script `.py` em Batch Script (`Iniciar-Painel.bat`)

- Status: Aceita
- Data: não registrada

## Contexto
Usuários finais iniciam o app via um atalho `.bat` que chama `pythonw.exe`; esse executável sem console tem comportamento diferente do `python.exe` normal quanto à resolução do `sys.path` ao usar o modo de módulo (`-m`), causando falha silenciosa (sem mensagem de erro visível) na inicialização.

## Decisão
Substituição do modo `-m` (module mode) pela execução explícita do arquivo `src\presentation\desktop\desktop_app.py`. Motivo: O `pythonw.exe` (sem console no Windows) não adicionava automaticamente o diretório raiz ao `sys.path` no modo `-m`, causando `ModuleNotFoundError: No module named 'src'` e falha silenciosa de inicialização.

## Consequências
Resolve a falha silenciosa de inicialização para usuários finais no Windows, tornando o atalho `.bat` confiável. É uma correção pontual de ambiente de execução, sem impacto na lógica de negócio.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
