# -*- coding: utf-8 -*-
"""
Extrator especializado de Participantes via LLM (Pass dedicado do Pipeline Multi-Pass).

Substitui o `participants` do antigo Pass 1 legado (ver docs/proposals/eliminacao-pass1-legado.md,
último campo pendente). Divide o trabalho por tipo de confiança: a LLM só resolve o que exige
julgamento narrativo genuíno (quem é a pessoa, qual o papel, antecedentes); vulgo e documento são
resolvidos deterministicamente por proximidade textual ao nome já extraído, reaproveitando as
mesmas funções maduras do motor determinístico (`role_detector.py`) — são utilitários puros e
sem estado, não um mecanismo de fallback entre motores (ADR-0085/ADR-0099 continuam respeitadas:
nenhum resultado de um motor substitui silenciosamente o do outro).
"""

import logging
from typing import Any, Dict, List

from backend.engine.extractors.deterministic.participants.negative_filters import is_blacklisted_name
from backend.engine.extractors.deterministic.participants.role_detector import (
    extract_document_near_name,
    extract_nickname,
)
from backend.engine.extractors.llm.extractors.location_extractor import text_contains
from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.engine.extractors.llm.prompts.participants_prompt import PARTICIPANTS_INSTRUCTIONS
from backend.engine.extractors.llm.schemas.participants_schema import ParticipantsExtraction

logger = logging.getLogger(__name__)


class LlmParticipantsExtractor:
    """
    Extrator cognitivo dedicado à lista de participantes (vítimas, testemunhas, autores/suspeitos).
    """

    def __init__(self, processor: ILlmProcessor) -> None:
        self.processor = processor

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Executa o pass focado exclusivamente em participantes.
        Retorna uma lista de dicionários com 'name', 'nickname', 'document',
        'participation_type' e 'background'.
        """
        if not text or not text.strip():
            return []

        try:
            logger.info("Executando Pass de Participantes via LLM...")
            raw_response = self.processor.process_text(
                text=text,
                questions={"system_prompt": PARTICIPANTS_INSTRUCTIONS},
                schema_model=ParticipantsExtraction
            )
        except Exception as err:
            logger.error(f"Erro na execução do LlmParticipantsExtractor: {err}. Mantendo vazio.")
            return []

        if not isinstance(raw_response, dict):
            return []

        raw_entries = raw_response.get("participants")
        if not isinstance(raw_entries, list):
            return []

        resolved: List[Dict[str, Any]] = []
        for entry in raw_entries:
            if not isinstance(entry, dict):
                continue

            name = str(entry.get("name") or "").strip()
            if not name:
                continue

            # Guardrail de evidência literal: um nome que a LLM alucinou nunca sobrevive.
            if not text_contains(name, text):
                logger.warning(f"Descartando participante sem evidência literal no texto ('{name}').")
                continue

            # Guardrail anti-PM/instituição/objeto: reaproveita a blacklist já madura do
            # motor determinístico, garantindo que nenhum policial entre no dossiê mesmo
            # que a LLM tenha ignorado a instrução do prompt.
            if is_blacklisted_name(name):
                logger.warning(f"Descartando participante bloqueado pela blacklist ('{name}').")
                continue

            participation_type = str(entry.get("participation_type") or "").strip() or "Autor/Suspeito"
            background = str(entry.get("background") or "").strip()

            resolved.append({
                "name": name,
                "nickname": extract_nickname(text, name),
                "document": extract_document_near_name(text, name),
                "participation_type": participation_type,
                "background": background,
            })

        return resolved
