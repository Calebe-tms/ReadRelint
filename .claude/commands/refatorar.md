---
description: 
---

---
description: Workflow focado em ações práticas de refatoração, priorizando estabilidade e zero regressão.
---

# Workflow de Refatoração e Limpeza de Código

**🎯 PREMISSA MÁXIMA (Zero Regressão):** O código pode e deve ser modificado para melhorar sua estrutura, legibilidade e manutenibilidade. Porém, o **comportamento** do sistema deve continuar exatamente o mesmo. Nenhuma regra de negócio, contrato de API, payload de entrada/saída ou fluxo de usuário deve ter seu funcionamento final alterado.

## 1. Mapeamento e Rede de Segurança
- [ ] **Testes Iniciais:** Executar a suíte de testes e assegurar que estão 100% passando. Adicionar testes de regressão básicos se áreas críticas estiverem descobertas antes de tocá-las.
- [ ] **Análise Estática:** Executar linters e ferramentas de análise para identificar código inacessível (*unreachable code*), arquivos isolados e importações órfãs.

## 2. Remoção de Código Morto (Dead Code)
- [ ] Deletar arquivos, pastas e dependências obsoletas sem referências no projeto.
- [ ] Remover classes, funções, métodos, parâmetros e variáveis declarados mas sem leitura/uso.
- [ ] Eliminar todo código comentado (o histórico fica salvo no Git).
- [ ] *Check de segurança:* Verificar injeções de dependência, reflexões ou rotinas de inicialização antes de deletar arquivos.

## 3. Nomenclatura e Comentários
- [ ] **Expressividade:** Renomear variáveis, classes e funções (usando `Verbo + Substantivo` para funções) para que o nome carregue a intenção real, sem abreviações confusas.
- [ ] **Comentários:** Remover descrições óbvias de "como" o código funciona. Manter ou reescrever apenas comentários focados no "porquê" (regras de negócio peculiares, restrições técnicas ou integrações).

## 4. Estrutura Direta, Granularidade e Escopo
- [ ] **Um Arquivo, Uma Responsabilidade:** Cada arquivo deve exportar preferencialmente apenas uma função ou classe principal. Evite arquivos "utilitários" gigantes; divida-os por contexto.
- [ ] **Regra da Tela (Tamanho):** Arquivos devem ser curtos. O ideal é que o código inteiro de um arquivo caiba em uma única tela do monitor, dispensando rolagens longas, isso nao deve ser uma regra rígida e sim uma preferencia.
- [ ] **Responsabilidade Única (SRP):** Extrair métodos muito longos para funções menores e coesas.
- [ ] **Simplificação de Condicionais:** Aplicar *Early Returns* (Guard Clauses) para reduzir o aninhamento profundo de blocos `if/else`.

## 5. Validação Final (Zero Regressão)
- [ ] Manter 100% das interfaces públicas, assinaturas e contratos de payloads de entrada/saída intactos.
- [ ] Executar a suíte completa de testes automatizados para checar regressões (tudo deve continuar passando).
- [ ] Executar a verificação de tipos e o build/compilação do projeto.
- [ ] Garantir que a aplicação inicializa perfeitamente, sem erros no console ou novos *warnings*.
- [ ] criar um relatório completo de todas a melhorias que foram realizadas, com uma % de quanto do sistema foi alterado*.