# ADR-0106: Acesso da Equipe via VPN em Malha, sem Expor o Sistema na Internet

- Status: Aceita
- Data: 2026-09-08
- Substitui a [ADR-0019](./0019-acesso-online-e2ee-cloudflare-tunnel.md) (Cloudflare Tunnel + E2EE na camada de aplicação)

## Contexto

O sistema precisa ficar acessível para a equipe, mas com duas restrições absolutas do usuário: **a hospedagem tem que ser a máquina local dele** e **os dados não podem trafegar por servidor de terceiro** — são dados de inteligência policial (nomes, RG, endereços, antecedentes, vínculos criminais).

A decisão anterior ([ADR-0019](./0019-acesso-online-e2ee-cloudflare-tunnel.md)) previa expor o FastAPI local via **Cloudflare Tunnel**, compensando o risco com criptografia ponta-a-ponta (AES-256-GCM) na camada de aplicação. Dois problemas com esse caminho:

1. **O TLS do Cloudflare Tunnel termina na borda do provedor** — a Cloudflare tecnicamente consegue ver o tráfego em texto claro. Isso não fecha com o requisito literal de "nenhum servidor de terceiro".
2. A mitigação prevista (E2EE na camada de aplicação) nunca foi implementada e é um trabalho grande e delicado: exigiria a chave viver só no cliente, com o backend operando sobre dados cifrados — perdendo busca, filtro e agregação no servidor.

## Decisão

**Acesso por VPN em malha baseada em WireGuard, em vez de publicar o sistema na internet.** A equipe entra numa rede privada com a máquina do usuário e acessa o dashboard como se estivesse na mesma rede local. O sistema **nunca fica exposto à internet pública** — não há porta HTTP/HTTPS aberta para o mundo, e a superfície de ataque cai para "dispositivos explicitamente autorizados na malha".

Isso resolve o requisito de privacidade pela topologia, não por criptografia de aplicação: o tráfego é cifrado ponta a ponta entre o dispositivo do membro da equipe e a máquina local (WireGuard), e o banco continua exclusivamente em disco local.

**Escolha da ferramenta concreta fica pendente**, entre duas opções levantadas (ambas open source, ambas WireGuard por baixo):
- **Tailscale** — clientes open source (BSD); o plano de controle é SaaS, mas só troca chaves públicas e resolve NAT, nunca vê o payload. Dispensa abrir porta no roteador e funciona atrás de CGNAT. Caminho de migração futura para **Headscale** (reimplementação open source do coordenador, self-hosted) sem trocar os clientes.
- **WireGuard puro** — zero dependência externa desde o início, mas exige abrir porta UDP no roteador, DDNS se o IP for dinâmico, e gestão manual de chaves.

## Consequências

O requisito de confidencialidade passa a ser atendido pela topologia de rede, sem precisar implementar (nem manter) criptografia própria na camada de aplicação — a ADR-0019 fica superada por inteiro, incluindo o item de E2EE. Em troca, o acesso deixa de ser "abrir uma URL no navegador" e passa a exigir um cliente VPN instalado e autorizado em cada dispositivo da equipe.

**Riscos aceitos conscientemente nesta etapa** (decisões do usuário, cada uma a ser tratada em trabalho posterior):

- **Sem autenticação na API.** Hoje não existe nenhuma checagem de identidade em `backend/api/app.py` nem nos routers — qualquer dispositivo que alcance a porta lê, edita e apaga tudo. Dentro da VPN isso significa que "estar na malha" é a única credencial. Sistema multiusuário (login/perfis) fica para depois, junto com **log de auditoria**.
- **Sem backup.** A máquina local hospedando é ponto único de falha e o arquivo `.db` não tem rotina de cópia. Fica para depois.
- **O sistema roda hoje como aplicação de desktop** (painel PyQt6 / `start_web.py`), não como serviço do Windows — logout, suspensão ou reinício derrubam o acesso da equipe. Precisa ser resolvido para o acesso ser estável de fato, mas não é objeto desta ADR.
