# ADR-0019: Acesso Online com E2EE (Cloudflare Tunnel)

- Status: **Substituída pela [ADR-0106](./0106-acesso-da-equipe-via-vpn-em-malha-sem-expor-o-sistema.md)** (acesso passou a ser por VPN em malha, sem expor o sistema na internet — o TLS do túnel terminava na borda do provedor, o que não atende ao requisito de nenhum servidor de terceiro no caminho dos dados)
- Data: não registrada

## Contexto
Expor o dashboard fora da rede local via Cloudflare Tunnel para acesso remoto cria a necessidade de proteger dados sensíveis de RELINTs em trânsito, mesmo confiando no túnel do provedor.

## Decisão
Criptografia ponta-a-ponta (AES-256-GCM) na camada da aplicação.

## Consequências
Dados sensíveis ficam protegidos mesmo que a camada de transporte do túnel seja comprometida. Isso adiciona overhead de implementação e manutenção de criptografia própria na camada de aplicação.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
