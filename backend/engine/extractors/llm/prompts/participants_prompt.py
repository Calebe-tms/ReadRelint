# -*- coding: utf-8 -*-
"""
Diretrizes especializadas para extração de participantes (Pass dedicado).
"""

PARTICIPANTS_INSTRUCTIONS = """
DIRETRIZES DE PARTICIPANTES (participants: lista de {name, participation_type, background}):
1. Liste APENAS pessoas de interesse citadas nominalmente no fato: vítimas, testemunhas e
   autores/suspeitos. NUNCA inclua policiais da guarnição, delegados, peritos, bombeiros ou
   qualquer agente público que apenas atendeu a ocorrência — mesmo que seus nomes apareçam
   no texto.
2. 'participation_type': escolha ESTRITAMENTE uma das 3 opções: 'Vítima', 'Testemunha' ou
   'Autor/Suspeito'. Se não houver como determinar o papel com segurança, prefira omitir a
   pessoa da lista a adivinhar.
3. 'background': só preencha se o texto mencionar antecedentes explícitos da pessoa (ex:
   "já possui antecedentes por furto", "é usuário de entorpecentes conhecido das forças
   policiais"). Se não houver menção explícita, retorne null — NUNCA invente antecedentes.
4. 'name': copie o nome exatamente como aparece no texto, sem abreviar nem corrigir grafia.
5. Se o texto não citar nenhuma pessoa de interesse além da guarnição, retorne uma lista vazia.
""".strip()
