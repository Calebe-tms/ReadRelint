# -*- coding: utf-8 -*-
"""
Schema Pydantic estruturado para extração isolada e dedicada do registro policial em
outro órgão (delegacia/DPPA/Polícia Civil) — campo raro e desconexo do número do próprio RELINT.
"""

from typing import Optional
from pydantic import BaseModel, Field


class RegistryExtraction(BaseModel):
    """
    Schema focado exclusivamente na extração de um eventual registro policial em outro órgão,
    mencionado no corpo narrativo do RELINT — nunca o número do próprio RELINT (cabeçalho).
    """
    registry_number: Optional[str] = Field(
        default=None,
        description=(
            "Número sequencial do registro policial em outro órgão (DP/DPPA/Polícia Civil), "
            "geralmente com até 4 dígitos. NÃO é o número do próprio RELINT (esse aparece no "
            "cabeçalho, ex: 'RELATÓRIO Nº 015/2026/ADJ-INT-CRIM', e deve ser ignorado). Só "
            "preencha se houver menção explícita tipo 'Registro na DP', 'registrado sob o "
            "número', 'registro na DPPA', 'registro na Polícia Civil'. Caso contrário, retorne null."
        )
    )
    registry_agency: Optional[str] = Field(
        default=None,
        description=(
            "Código numérico do órgão de registro (delegacia/DP), quase sempre com 6 dígitos. "
            "Só preencha se vier junto da mesma menção de 'registry_number'. Caso contrário, retorne null."
        )
    )
    registry_year: Optional[str] = Field(
        default=None,
        description=(
            "Ano do registro policial em outro órgão, sempre com 4 dígitos (ex: 2026). Só "
            "preencha se vier junto da mesma menção de 'registry_number'. Caso contrário, retorne null."
        )
    )
