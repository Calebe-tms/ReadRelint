# -*- coding: utf-8 -*-
"""
Cliente Ollama para processamento cognitivo local via LLM.
"""

import json
import logging
import requests
from typing import Any, Dict, Optional, Tuple
from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.core.entities import IncidentReport

logger = logging.getLogger(__name__)


class OllamaClient(ILlmProcessor):
    """
    Implementação concreta para processamento de linguagem natural usando
    o Ollama rodando localmente.
    """

    def __init__(self, model_name: str = "llama3.1:latest", base_url: str = "http://localhost:11434") -> None:
        self.model_name = model_name
        self.base_url = base_url

    def check_connection(self) -> Tuple[bool, str]:
        """
        Testa se o serviço Ollama está rodando localmente na URL base.
        Retorna uma tupla (sucesso: bool, mensagem: str).
        """
        try:
            url = f"{self.base_url}/api/tags"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                models = res.json().get("models", [])
                if models:
                    model_names = ", ".join(m.get("name", "") for m in models[:3])
                    return True, f"Ollama online! Modelo(s) encontrado(s): {model_names}"
                return True, "Ollama online! Nenhum modelo instalado no momento."
            return False, f"Ollama respondeu com código de erro {res.status_code}."
        except Exception:
            return False, f"Serviço Ollama indisponível ou desativado em {self.base_url}"

    def process_text(self, text: str, questions: Optional[Dict[str, str]] = None, schema_model: type = None, pre_extracted_entities: list = None) -> dict:
        """
        Envia o texto limpo ao Ollama solicitando a estruturação em formato JSON
        baseado no JSON Schema do modelo IncidentReport (ou do schema_model se fornecido).
        """
        system_prompt = ""
        if questions and "system_prompt" in questions:
            system_prompt = questions["system_prompt"]
        
        # Gera o JSON Schema do modelo Pydantic para orientar a extração
        model_to_use = schema_model if schema_model else IncidentReport
        schema = model_to_use.model_json_schema()
        # Remove campos mantidos pelo sistema Python para não poluir nem confundir o Ollama
        if "properties" in schema:
            schema["properties"].pop("source_file", None)
            schema["properties"].pop("content", None)
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False)

        from backend.engine.extractors.llm.prompts import build_extraction_prompt

        prompt = build_extraction_prompt(
            text=text,
            schema_str=schema_str,
            rule_system_prompt=system_prompt,
            pre_extracted_entities=pre_extracted_entities
        )



        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0
            }
        }

        try:
            logger.info(f"Enviando texto do RELINT para processamento local via Ollama ({self.model_name})...")
            response = requests.post(url, json=payload, timeout=25)
            
            # Recuperação Automática: Se der 404 (model not found), tenta buscar modelos ativos no Ollama
            if response.status_code == 404:
                logger.warning(f"Modelo '{self.model_name}' não encontrado no Ollama. Buscando modelos alternativos...")
                tags_response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if tags_response.status_code == 200:
                    models = tags_response.json().get("models", [])
                    if models:
                        alternative_model = models[0]["name"]
                        logger.info(f"Alternando automaticamente para o modelo disponível: '{alternative_model}'")
                        self.model_name = alternative_model
                        payload["model"] = alternative_model
                        
                        # Segunda tentativa
                        response = requests.post(url, json=payload, timeout=25)
            
            response.raise_for_status()
            
            response_json = response.json()
            response_text = response_json.get("response", "{}")
            
            extracted_data = json.loads(response_text)
            return extracted_data
            
        except Exception as e:
            logger.error(f"Erro ao processar texto com Ollama: {e}")
            raise e
