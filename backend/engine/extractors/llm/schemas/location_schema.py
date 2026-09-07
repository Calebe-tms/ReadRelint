# -*- coding: utf-8 -*-
"""
Schema Pydantic estruturado para extração isolada e dedicada de Localização, Endereço e Coordenadas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LocationExtraction(BaseModel):
    """
    Schema focado exclusivamente na extração da geografia da ocorrência policial.
    """
    street: Optional[str] = Field(
        default=None,
        description="Nome do logradouro onde o fato ocorreu, exatamente como aparece no texto. Se não houver logradouro identificável no documento, retorne null."
    )
    number: Optional[str] = Field(
        default=None,
        description="Número predial do imóvel ou 'S/N' (ou indicação de Km, ex: Km 47)."
    )
    neighborhood: Optional[str] = Field(
        default=None,
        description="Nome do bairro ou localidade rural (ex: Centro, São Cristóvão, Fátima, Interior)."
    )
    municipality: Optional[str] = Field(
        default=None,
        description="Nome da cidade/município da ocorrência (ex: Porto Alegre, Frederico Westphalen, Seberi, Panambi)."
    )
    coordinates: Optional[str] = Field(
        default=None,
        description="Coordenadas decimais de GPS mencionadas no texto no padrão '-29.xxxx, -51.xxxx' ou DMS."
    )
    map_url: Optional[str] = Field(
        default=None,
        description="Link ou URL explícita do Google Maps presente no documento (ex: https://maps.app.goo.gl/...)."
    )
    location_types: Optional[List[str]] = Field(
        default=None,
        description=(
            "Categorize o tipo do local do fato a partir do contexto (ex: 'Propriedade Rural', "
            "'Escolas', 'Residência', 'Via Pública', 'Estabelecimento Comercial'). Pode retornar "
            "mais de uma categoria se fizer sentido. Se não for possível categorizar com "
            "confiança, retorne null (NUNCA invente uma categoria sem base no texto)."
        )
    )
