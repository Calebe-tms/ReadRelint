# -*- coding: utf-8 -*-
"""
Extrator especializado de campos de especialidade (Passo 3 do Pipeline Multi-Pass).

Estratégia em 2 estágios, substituindo as antigas Rules/entidades monolíticas por especialidade:
1. Campos binários/enum simples (injured_victims, hostage_victim, recovered, location_type)
   são resolvidos 100% por regex determinístico, sem LLM.
2. Campos livres/nuançados (motivation, drug_quantity, vehicle_model etc.) usam um schema Pydantic
   minúsculo (só os campos daquela especialidade) + guardrail de evidência literal no texto.
Especialidades sem nenhum campo de especialidade real (Roubo a Residência, Furto Qualificado,
Outros) nunca chamam a LLM.
"""

import logging
import re
from typing import Any, Dict, Optional, Tuple, Type

from pydantic import BaseModel

from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.engine.extractors.llm.extractors.location_extractor import normalize_for_match, text_contains
from backend.engine.extractors.llm.prompts.specialty_prompts import SPECIALTY_INSTRUCTIONS
from backend.engine.extractors.llm.schemas.specialty_schemas import (
    DrugTraffickingSpecialtyExtraction,
    EstablishmentRobberySpecialtyExtraction,
    HomicideSpecialtyExtraction,
    PedestrianRobberySpecialtyExtraction,
    VehicleSpecialtyExtraction,
)
from backend.core.entities import HomicideMotivation

logger = logging.getLogger(__name__)


SPECIALTY_SCHEMAS: Dict[str, Type[BaseModel]] = {
    "Homicídio": HomicideSpecialtyExtraction,
    "Prisão por Tráfico": DrugTraffickingSpecialtyExtraction,
    "Roubo a Estabelecimento": EstablishmentRobberySpecialtyExtraction,
    "Roubo de Veículo": VehicleSpecialtyExtraction,
    "Furto de Veículo": VehicleSpecialtyExtraction,
    "Roubo a Pedestre": PedestrianRobberySpecialtyExtraction,
    # "Roubo a Residência", "Furto Qualificado" e "Outros" não têm campos livres:
    # ficam de fora deste registro e nunca chamam a LLM.
}

# União de TODOS os campos que este extrator pode produzir (determinísticos + os de cada
# schema de especialidade). O chamador (LlmPipeline) usa esta lista para sobrescrever
# incondicionalmente 'result.data', garantindo que nenhum valor sem guardrail (ex: 'motivation'
# fora do enum) sobreviva quando o Passo 3 descarta seu campo.
ALL_SPECIALTY_FIELDS: Tuple[str, ...] = tuple(sorted({
    "location_type", "hostage_victim", "injured_victims", "recovered",
    *(field_name for schema in {
        HomicideSpecialtyExtraction, DrugTraffickingSpecialtyExtraction,
        EstablishmentRobberySpecialtyExtraction, VehicleSpecialtyExtraction,
        PedestrianRobberySpecialtyExtraction,
    } for field_name in schema.model_fields)
}))

# Campos livres validados por evidência literal no texto (descarta alucinação sem sustentação)
FREE_TEXT_FIELDS = (
    "drug_quantity", "drug_types", "establishment_type",
    "vehicle_model", "license_plate", "recovery_location", "stolen_object",
)

VALID_WEAPONS: Tuple[str, ...] = ("Arma de fogo", "Arma branca", "Agressão física")
VALID_FACT_TYPES: Tuple[str, ...] = ("Tentado", "Consumado")
VALID_MOTIVATIONS: Tuple[str, ...] = tuple(m.value for m in HomicideMotivation if m != HomicideMotivation.DESCONHECIDO)


def _match_enum(value: str, valid_options: Tuple[str, ...]) -> str:
    """Aceita o valor só se bater (tolerante a acento/caixa) com uma opção válida; senão descarta."""
    normalized_value = normalize_for_match(value)
    for option in valid_options:
        if normalize_for_match(option) == normalized_value:
            return option
    return ""


def _has_negation_nearby(text: str, keyword_match: "re.Match", window: int = 40) -> bool:
    """
    Verifica se há uma negação (não/sem) na MESMA oração do termo encontrado, para evitar
    falso positivo de uma negação em oração anterior (ex: "O suspeito não foi localizado,
    mas a vítima sofreu lesões" não deve negar "lesões").
    """
    start = max(0, keyword_match.start() - window)
    prefix = text[start:keyword_match.start()]

    # Restringe a busca à oração atual: pula tudo até a última quebra de oração
    # (pontuação ou conjunção adversativa) dentro da janela.
    clause_end = 0
    for boundary in re.finditer(r'[.,;]|\bmas\b|\bpor[ée]m\b', prefix, re.IGNORECASE):
        clause_end = boundary.end()
    prefix = prefix[clause_end:]

    return bool(re.search(r'\b(?:sem|n[ãa]o)\b', prefix.lower()))


def detect_injured_victims(text: str) -> int:
    """Regra determinística: 1 se houver menção a lesão/ferimento sem negação próxima, senão 0."""
    if not text:
        return 0
    for match in re.finditer(r'les(?:[aã]o|[oõ]es|ionad[oa]s?)\b', text, re.IGNORECASE):
        if not _has_negation_nearby(text, match):
            return 1
    return 0


def detect_hostage_victim(text: str) -> int:
    """Regra determinística: 1 se houver menção a refém/reféns sem negação próxima, senão 0."""
    if not text:
        return 0
    for match in re.finditer(r'ref[eé][nm]s?\b', text, re.IGNORECASE):
        if not _has_negation_nearby(text, match):
            return 1
    return 0


def detect_recovered(text: str) -> int:
    """Regra determinística: 1 se o texto confirmar recuperação do veículo sem negação próxima."""
    if not text:
        return 0
    for match in re.finditer(r'recuperad[oa]s?\b', text, re.IGNORECASE):
        if not _has_negation_nearby(text, match):
            return 1
    return 0


def detect_location_type(neighborhood: str) -> str:
    """Deriva Urbano/Rural a partir do bairro já resolvido deterministicamente no Passo 2 (Localização)."""
    return "Rural" if normalize_for_match(neighborhood) == "interior" else "Urbano"


class SpecialtyExtractor:
    """
    Extrator cognitivo dedicado para os campos de especialidade de cada bm_group.
    A classificação do bm_group em si é responsabilidade do chamador (classify_bm_group,
    100% determinístico) — este extrator só resolve os campos adicionais daquela especialidade.
    """

    def __init__(self, processor: ILlmProcessor) -> None:
        self.processor = processor

    def extract(self, text: str, bm_group: str, neighborhood: str = "") -> Dict[str, Any]:
        data: Dict[str, Any] = {}

        # 1. Campos 100% determinísticos (sem LLM), por especialidade
        if bm_group in ("Roubo a Estabelecimento", "Roubo a Residência"):
            data["location_type"] = detect_location_type(neighborhood)
            data["hostage_victim"] = detect_hostage_victim(text)
        if bm_group in ("Roubo a Estabelecimento", "Roubo a Residência", "Roubo a Pedestre"):
            data["injured_victims"] = detect_injured_victims(text)
        if bm_group in ("Roubo de Veículo", "Furto de Veículo"):
            data["recovered"] = detect_recovered(text)

        # 2. Campo livre/nuançado via LLM (só quando a especialidade tem algum)
        schema_model = SPECIALTY_SCHEMAS.get(bm_group)
        if not schema_model or not text or not text.strip():
            return data

        try:
            logger.info(f"Executando Passo 3 (Especialidade: {bm_group}) via LLM...")
            raw_response = self.processor.process_text(
                text=text,
                questions={"system_prompt": SPECIALTY_INSTRUCTIONS.get(bm_group, "")},
                schema_model=schema_model
            )
        except Exception as err:
            logger.error(f"Erro na execução do SpecialtyExtractor ({bm_group}): {err}. Mantendo apenas dados determinísticos.")
            return data

        if not isinstance(raw_response, dict):
            return data

        for field_name in schema_model.model_fields:
            value = str(raw_response.get(field_name) or "").strip()
            if not value or value.lower() in ("none", "null"):
                continue
            data[field_name] = value

        # 3. Guardrails de enum fechado: fora da lista válida -> descarta (nunca força um valor)
        if "fact_type" in data:
            data["fact_type"] = _match_enum(data["fact_type"], VALID_FACT_TYPES) or None
            if data["fact_type"] is None:
                data.pop("fact_type")
        if "motivation" in data:
            matched = _match_enum(data["motivation"], VALID_MOTIVATIONS)
            if matched:
                data["motivation"] = matched
            else:
                data.pop("motivation")
        if "weapon_used" in data:
            matched = _match_enum(data["weapon_used"], VALID_WEAPONS)
            if matched:
                data["weapon_used"] = matched
            else:
                data.pop("weapon_used")

        # 4. Guardrail de evidência literal: campos livres sem sustentação no texto são descartados
        for field_name in FREE_TEXT_FIELDS:
            if field_name in data and not text_contains(data[field_name], text):
                logger.warning(f"Descartando '{field_name}' sem evidência no texto ('{data[field_name]}').")
                data.pop(field_name)

        return data
