# ADR-0002: Interface Híbrida

- Status: Aceita
- Data: não registrada

## Contexto
O sistema precisa, ao mesmo tempo, monitorar pastas do sistema operacional local (algo que uma aplicação puramente web não acessa diretamente) e oferecer um dashboard rico de leitura e cruzamento de dados. Nenhuma das duas frentes sozinha atende às duas necessidades.

## Decisão
FastAPI + SPA Web para leitura e cruzamento (Dashboard) e CustomTkinter para monitoramento de pastas OS-level (Desktop).

## Consequências
Cada camada usa a tecnologia mais adequada ao seu propósito, mas o projeto passa a manter dois stacks de UI em paralelo (desktop e web), aumentando a superfície de manutenção e exigindo sincronização de estado entre eles.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
