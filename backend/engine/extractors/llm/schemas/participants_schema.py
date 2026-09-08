# -*- coding: utf-8 -*-
"""
Schema Pydantic estruturado para extração isolada e dedicada de participantes via LLM.
Pede à LLM só o que exige julgamento narrativo genuíno (nome, papel, antecedentes) — vulgo e
documento são resolvidos deterministicamente por proximidade textual ao nome já extraído.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ParticipantEntry(BaseModel):
    """Uma pessoa de interesse citada no fato (vítima, testemunha ou autor/suspeito)."""
    name: Optional[str] = Field(
        default=None,
        description="Nome completo da pessoa, exatamente como aparece no texto. Nunca abrevie nem corrija grafia."
    )
    participation_type: Optional[str] = Field(
        default=None,
        description="Escolha ESTRITAMENTE uma: 'Vítima', 'Testemunha' ou 'Autor/Suspeito'."
    )
    background: Optional[str] = Field(
        default=None,
        description="Antecedentes explicitamente mencionados sobre a pessoa. Se não houver menção clara, retorne null."
    )


class ParticipantsExtraction(BaseModel):
    """Schema focado exclusivamente na lista de participantes do fato."""
    participants: List[ParticipantEntry] = Field(
        default_factory=list,
        description="Lista de pessoas de interesse citadas no fato. NUNCA inclua policiais da guarnição, delegados ou peritos."
    )
