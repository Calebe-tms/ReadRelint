# -*- coding: utf-8 -*-
"""
Testes unitários para validação dos prompts modulares, sanitizador de síntese e gerador Google Maps.
"""

from backend.engine.extractors.llm.prompts import build_extraction_prompt
from backend.engine.extractors.llm.validators.llm_response_validator import (
    sanitize_summary,
    format_address_and_maps,
    validate_and_normalize_llm_response
)


def test_build_extraction_prompt_contains_all_rules():
    prompt = build_extraction_prompt(
        text="Texto de teste da ocorrencia policial",
        schema_str='{"title": "IncidentReport"}',
        rule_system_prompt="Regra específica de homicídio"
    )

    assert "DIRETRIZES DA SÍNTESE FACTUAL" in prompt
    assert "DIRETRIZES DE ENDEREÇO E LOCALIZAÇÃO" in prompt
    assert "NÃO inclua o endereço, rua, número ou bairro no texto da síntese" in prompt
    assert "Regra específica de homicídio" in prompt
    assert "Texto de teste da ocorrencia policial" in prompt


def test_sanitize_summary_removes_police_preambles():
    raw_summary = "Chegando ao local, a guarnição constatou que a vítima foi atingida por disparos de arma de fogo e socorrida ao hospital."
    clean = sanitize_summary(raw_summary)
    
    assert not clean.startswith("Chegando ao local")
    assert clean.startswith("A vítima foi atingida por disparos")


def test_format_address_and_maps_standard_format():
    data = {
        "street": "Rua Marechal Deodoro",
        "number": "540",
        "municipality": "Passo Fundo",
        "coordinates": "-28.2612, -52.4083"
    }
    
    address, map_url, coords = format_address_and_maps(data)
    
    assert address == "Rua Marechal Deodoro, nº 540 - Passo Fundo"
    assert coords == "-28.2612, -52.4083"
    assert map_url == "https://www.google.com/maps?q=-28.2612,-52.4083"


def test_format_address_and_maps_without_coords():
    data = {
        "street": "Avenida Brasil",
        "number": "S/N",
        "municipality": "Canoas"
    }
    
    address, map_url, coords = format_address_and_maps(data)
    
    assert address == "Avenida Brasil, S/N - Canoas"
    assert "google.com/maps/search" in map_url
    assert "Avenida+Brasil" in map_url


def test_validate_and_normalize_llm_response_complete():
    raw_response = {
        "summary": "conforme boletim de ocorrência, autor armado efetuou roubo ao estabelecimento comercial e fugiu a pé.",
        "street": "Rua Sete de Setembro",
        "number": "100",
        "municipality": "Porto Alegre",
        "coordinates": "-30.0346, -51.2177"
    }

    result = validate_and_normalize_llm_response(raw_response)

    assert result["summary"].startswith("Autor armado efetuou roubo")
    assert result["address"] == "Rua Sete de Setembro, nº 100 - Porto Alegre"
    assert result["coordinates"] == "-30.0346, -51.2177"
    assert result["map_url"] == "https://www.google.com/maps?q=-30.0346,-51.2177"
