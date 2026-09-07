# -*- coding: utf-8 -*-
"""
Pipeline orquestrador de extração 100% Cognitivo via LLM (Ollama).
Processa o documento exclusivamente com Inteligência Artificial, sem interferência
ou fallbacks determinísticos/regex.
"""

from typing import Any, Dict, Optional
from backend.engine.cleaners.text_cleaner import clean_relint_text
from backend.engine.extractors.base import ExtractionAlert, ExtractionResult, IExtractor
from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.engine.extractors.llm.ollama_client import OllamaClient


from backend.engine.cleaners.bm_classifier import classify_bm_group
from backend.engine.extractors.llm.extractors.summary_extractor import SummaryExtractor
from backend.engine.extractors.llm.extractors.location_extractor import LocationExtractor
from backend.engine.extractors.llm.extractors.specialty_extractor import ALL_SPECIALTY_FIELDS, SpecialtyExtractor
from backend.engine.extractors.llm.extractors.registry_extractor import RegistryExtractor


class LlmPipeline(IExtractor):
    """
    Pipeline especialista de extração puramente cognitiva via LLM.
    """

    def __init__(self, processor: Optional[ILlmProcessor] = None) -> None:
        self.processor = processor or OllamaClient()
        self.summary_extractor = SummaryExtractor(self.processor)
        self.location_extractor = LocationExtractor(self.processor)
        self.specialty_extractor = SpecialtyExtractor(self.processor)
        self.registry_extractor = RegistryExtractor(self.processor)

    def extract(
        self,
        text: str,
        filename: str = "",
        rule: Any = None,
        pre_extracted_entities: list = None,
        **kwargs: Any
    ) -> ExtractionResult:
        """
        Executa a extração 100% orientada por LLM com JSON Schema estruturado.
        """
        result = ExtractionResult(
            data={},
            extraction_method="Ollama (IA)",
            alerts=[],
            success=True
        )

        if not text or not text.strip():
            result.add_alert(
                level="error",
                stage="llm_input_validation",
                message="Texto do documento está vazio ou inválido para envio à LLM."
            )
            result.success = False
            return result

        cleaned_text = clean_relint_text(text)

        try:
            result.data = {}

            # Pass 1: Extração Dedicada de Síntese e Assunto (Alta Fidelidade)
            summary_data = self.summary_extractor.extract(cleaned_text, filename=filename)
            if summary_data.get("summary"):
                result.data["summary"] = summary_data["summary"]
            if summary_data.get("subject") and (not result.data.get("subject") or len(str(result.data.get("subject"))) < 5):
                result.data["subject"] = summary_data["subject"]

            # Pass 2: Extração Dedicada de Localização e Georreferenciamento.
            # Sobrescreve incondicionalmente: o Pass 2 tem guardrails determinísticos que o
            # schema genérico do primeiro pass não tem, então mesmo um resultado vazio aqui
            # (ex: campo sem evidência suficiente) deve prevalecer sobre o valor sem validação.
            location_data = self.location_extractor.extract(cleaned_text, filename=filename)
            for loc_key in ["address", "municipality", "neighborhood", "police_unit", "coordinates", "map_url", "geo_precision"]:
                result.data[loc_key] = location_data.get(loc_key, "")
            result.data["location_types"] = location_data.get("location_types", [])

            # Classificação determinística de bm_group (filename+assunto primeiro, conteúdo como fallback)
            # ANTES do Passo 3, para que o schema de especialidade correto seja escolhido.
            bm_group = classify_bm_group(
                filename=filename,
                subject=result.data.get("subject", ""),
                content=cleaned_text
            )
            result.data["bm_group"] = bm_group

            # Passo 3: Extração Dedicada de Campos de Especialidade (só quando o bm_group tem algum).
            # Sempre grava o resultado do Passo 3 (mesmo vazio): se o campo foi descartado por
            # falta de evidência/enum inválido, isso é a resposta correta, não deve ser sobrescrito
            # por nenhum valor sem guardrail.
            specialty_data = self.specialty_extractor.extract(
                cleaned_text, bm_group=bm_group, neighborhood=result.data.get("neighborhood", "")
            )
            for field_name in ALL_SPECIALTY_FIELDS:
                result.data[field_name] = specialty_data.get(field_name, "")

            # Pass dedicado: Registro Policial em Outro Órgão (campo raro, buscado só no corpo
            # narrativo — nunca no cabeçalho, onde vive o número do próprio RELINT).
            registry_data = self.registry_extractor.extract(cleaned_text)
            result.data["registry_number"] = registry_data.get("registry_number", "")
            result.data["registry_agency"] = registry_data.get("registry_agency", "")
            result.data["registry_year"] = registry_data.get("registry_year", "")

        except Exception as err:
            result.success = False
            result.add_alert(
                level="error",
                stage="llm_execution",
                message=f"Falha na execução do modelo Ollama: {err}"
            )

        return result
