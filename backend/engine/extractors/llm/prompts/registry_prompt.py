# -*- coding: utf-8 -*-
"""
Diretrizes especializadas para extração do registro policial em outro órgão (Pass dedicado).
"""

REGISTRY_INSTRUCTIONS = """
DIRETRIZES DE REGISTRO POLICIAL EM OUTRO ÓRGÃO (registry_number, registry_agency, registry_year):
1. Este campo é RARO — a maioria dos RELINTs não menciona nenhum registro em outro órgão.
   Quando não houver menção explícita, retorne null nos 3 campos. NUNCA invente ou adivinhe.
2. Procure ESTRITAMENTE no corpo narrativo do texto (não no cabeçalho) por frases-gatilho como:
   'Registro na DP', 'registrado sob o número', 'registro na DPPA', 'registro na Polícia Civil',
   ou variações semânticas equivalentes.
3. NUNCA confunda com o número do próprio RELATÓRIO DE INTELIGÊNCIA (ex: 'Nº 015/2026/ADJ-INT-CRIM'
   no cabeçalho do documento) — isso é um número diferente, de outro documento/órgão.
4. Os 3 números costumam aparecer juntos, separados por barra, mas em ORDEM VARIÁVEL. Use estas
   pistas de tamanho para não confundir a ordem:
   - Código do órgão (registry_agency): quase sempre 6 dígitos.
   - Ano (registry_year): sempre 4 dígitos.
   - Número do registro (registry_number): o mais curto dos três, raramente passa de 4 dígitos.
   Exemplo: em 'Registro na DP Nº 26/2026/151641', o correto é registry_number='26',
   registry_year='2026', registry_agency='151641' — mesmo a ordem no texto sendo diferente.
"""
