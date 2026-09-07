# -*- coding: utf-8 -*-
"""
Extrator especializado de Registro Policial em Outro Órgão via LLM (Pass dedicado do Pipeline Multi-Pass).
"""

import logging
import re
from typing import Dict

from backend.engine.cleaners.text_cleaner import extract_history_from_annex
from backend.engine.extractors.llm.extractors.location_extractor import text_contains
from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.engine.extractors.llm.prompts.registry_prompt import REGISTRY_INSTRUCTIONS
from backend.engine.extractors.llm.schemas.registry_schema import RegistryExtraction

logger = logging.getLogger(__name__)


def classify_registry_digits(raw_values: Dict[str, str]) -> Dict[str, str]:
    """
    Reclassifica número/órgão/ano por contagem de dígitos — heurística confirmada pelo usuário:
    o código do órgão quase sempre tem 6 dígitos, o ano sempre tem 4, e o número do registro
    raramente passa de 4. A ORDEM em que os 3 números aparecem no texto não é confiável; o
    tamanho é. Roda por cima da classificação que a LLM já tentou, corrigindo trocas de posição.
    """
    digits_only = {k: re.sub(r'\D', '', v or '') for k, v in raw_values.items()}
    pool = [v for v in digits_only.values() if v]
    if not pool:
        return raw_values

    six_digit = [v for v in pool if len(v) == 6]
    four_digit = [v for v in pool if len(v) == 4]

    # Ambíguo se mais de um valor disputar a mesma categoria por tamanho (ex: dois valores de
    # 4 dígitos) — nesse caso o tamanho sozinho não decide qual é o ano, mantém a resposta original.
    if len(six_digit) > 1 or len(four_digit) > 1:
        return raw_values

    agency = six_digit[0] if six_digit else ""
    year = four_digit[0] if four_digit else ""
    remaining = [v for v in pool if v != agency and v != year]
    number = remaining[0] if remaining else ""

    resolved = sum(1 for v in (agency, year, number) if v)
    if resolved < min(2, len(pool)):
        # Não deu pra classificar com confiança pelo tamanho — mantém a resposta original da LLM
        # em vez de arriscar uma reclassificação pior que o palpite original.
        return raw_values

    return {"registry_number": number, "registry_agency": agency, "registry_year": year}


class RegistryExtractor:
    """
    Extrator cognitivo dedicado ao registro policial em outro órgão (DP/DPPA/Polícia Civil) —
    campo raro, desconexo do número do próprio RELINT, e com ordem de dígitos inconsistente no texto.
    """

    def __init__(self, processor: ILlmProcessor) -> None:
        self.processor = processor

    def extract(self, text: str) -> Dict[str, str]:
        """
        Executa o pass focado exclusivamente no registro policial em outro órgão.
        Retorna um dicionário com 'registry_number', 'registry_agency' e 'registry_year'.
        """
        empty = {"registry_number": "", "registry_agency": "", "registry_year": ""}

        # Restringe a busca ao corpo narrativo (pós-ANEXOS), nunca ao cabeçalho — é lá que
        # vive o número do próprio RELINT, que nunca deve ser confundido com este campo.
        body_text = extract_history_from_annex(text) or text
        if not body_text or not body_text.strip():
            return empty

        try:
            logger.info("Executando Pass de Registro Policial via LLM...")
            raw_response = self.processor.process_text(
                text=body_text,
                questions={"system_prompt": REGISTRY_INSTRUCTIONS},
                schema_model=RegistryExtraction
            )
        except Exception as err:
            logger.error(f"Erro na execução do RegistryExtractor: {err}. Mantendo vazio.")
            return empty

        if not isinstance(raw_response, dict):
            return empty

        raw_values = {
            "registry_number": str(raw_response.get("registry_number") or "").strip(),
            "registry_agency": str(raw_response.get("registry_agency") or "").strip(),
            "registry_year": str(raw_response.get("registry_year") or "").strip(),
        }

        if not any(raw_values.values()):
            return empty

        # Guardrail de evidência literal: cada valor retornado precisa existir no corpo do texto.
        for key, value in list(raw_values.items()):
            digits = re.sub(r'\D', '', value)
            if not digits or not text_contains(digits, body_text):
                logger.warning(f"Descartando '{key}' sem evidência literal no corpo do texto ('{value}').")
                raw_values[key] = ""

        if not any(raw_values.values()):
            return empty

        return classify_registry_digits(raw_values)
