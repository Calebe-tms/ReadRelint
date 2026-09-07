# -*- coding: utf-8 -*-
"""
Testes unitários para o RegistryExtractor: guardrail de evidência literal, restrição ao
corpo narrativo (pós-ANEXOS) e reclassificação determinística por contagem de dígitos.
"""

from backend.engine.extractors.llm.extractors.registry_extractor import (
    RegistryExtractor,
    classify_registry_digits,
)
from backend.engine.extractors.llm.llm_processor import ILlmProcessor


class FakeProcessor(ILlmProcessor):
    """Processor falso para testar o RegistryExtractor sem depender do Ollama real."""

    def __init__(self, response: dict) -> None:
        self.response = response

    def process_text(self, text, questions=None, schema_model=None, pre_extracted_entities=None) -> dict:
        return self.response


# ---------------------------------------------------------------------------
# classify_registry_digits (função pura, reclassificação por tamanho de dígitos)
# ---------------------------------------------------------------------------

def test_classify_registry_digits_reorders_scrambled_values():
    # Exemplo real dado pelo usuário: "Registro na DP Nº 26/2026/151641" — a LLM devolveu
    # os 3 valores em posições trocadas; a reclassificação deve corrigir pelo tamanho.
    scrambled = {
        "registry_number": "2026",
        "registry_agency": "26",
        "registry_year": "151641",
    }
    result = classify_registry_digits(scrambled)
    assert result == {
        "registry_number": "26",
        "registry_agency": "151641",
        "registry_year": "2026",
    }


def test_classify_registry_digits_keeps_already_correct_values():
    correct = {
        "registry_number": "516",
        "registry_agency": "151641",
        "registry_year": "2026",
    }
    assert classify_registry_digits(correct) == correct


def test_classify_registry_digits_falls_back_when_ambiguous():
    # Nenhum valor de 6 dígitos e dois valores de 4 dígitos — não dá pra saber qual é o ano
    # e qual é o número por tamanho. Mantém a resposta original em vez de arriscar.
    ambiguous = {
        "registry_number": "1234",
        "registry_agency": "",
        "registry_year": "5678",
    }
    assert classify_registry_digits(ambiguous) == ambiguous


def test_classify_registry_digits_strips_non_digit_characters():
    with_noise = {
        "registry_number": "Nº 26",
        "registry_agency": "151641",
        "registry_year": "2026",
    }
    result = classify_registry_digits(with_noise)
    assert result == {
        "registry_number": "26",
        "registry_agency": "151641",
        "registry_year": "2026",
    }


# ---------------------------------------------------------------------------
# RegistryExtractor.extract (guardrails de evidência e restrição ao corpo)
# ---------------------------------------------------------------------------

DOCUMENT_WITH_REGISTRY = """
RELATÓRIO DE INTELIGÊNCIA Nº 015/2026/ADJ-INT-CRIM – 08/01/2026
DATA: 08/01/2026
ASSUNTO: HOMICÍDIO EM SEBERI - RS
ANEXOS: XXX

Em 08 de janeiro de 2025, um indivíduo foi vítima de latrocínio em Seberi - RS.
Registro na DP Nº 26/2026/151641 conforme boletim de ocorrência local.
"""

DOCUMENT_WITHOUT_REGISTRY = """
RELATÓRIO DE INTELIGÊNCIA Nº 009/2026/ADJ-INT-CRIM – 05/01/2026
DATA: 05/01/2026
ASSUNTO: FURTO DE VEÍCULO EM IBIRUBÁ - RS
ANEXOS: XXX

Em 05 de janeiro de 2025, um veículo foi furtado em Ibirubá - RS. Nenhuma outra
informação relevante foi apurada até o momento.
"""


def test_extract_returns_empty_when_no_mention_in_text():
    processor = FakeProcessor({"registry_number": None, "registry_agency": None, "registry_year": None})
    extractor = RegistryExtractor(processor)
    result = extractor.extract(DOCUMENT_WITHOUT_REGISTRY)
    assert result == {"registry_number": "", "registry_agency": "", "registry_year": ""}


def test_extract_captures_and_reclassifies_scrambled_registry():
    # A LLM encontrou o trio certo mas devolveu nas chaves trocadas (mesmo cenário do
    # classify_registry_digits, agora passando pelo extractor completo com guardrail de evidência).
    processor = FakeProcessor({
        "registry_number": "2026",
        "registry_agency": "26",
        "registry_year": "151641",
    })
    extractor = RegistryExtractor(processor)
    result = extractor.extract(DOCUMENT_WITH_REGISTRY)
    assert result == {
        "registry_number": "26",
        "registry_agency": "151641",
        "registry_year": "2026",
    }


def test_extract_discards_hallucinated_values_not_in_text():
    # Nenhum desses números existe no documento — deve ser descartado por completo.
    processor = FakeProcessor({
        "registry_number": "999",
        "registry_agency": "888888",
        "registry_year": "1999",
    })
    extractor = RegistryExtractor(processor)
    result = extractor.extract(DOCUMENT_WITHOUT_REGISTRY)
    assert result == {"registry_number": "", "registry_agency": "", "registry_year": ""}


def test_extract_ignores_mention_that_only_exists_in_header():
    # Simula a LLM confundindo o número do próprio RELINT (cabeçalho, "015/2026") com o
    # campo de registro — mesmo que os dígitos existam no documento, eles só aparecem no
    # cabeçalho (antes de ANEXOS), então o guardrail de corpo-apenas deve descartar.
    header_only_text = """
RELATÓRIO DE INTELIGÊNCIA Nº 015/2026/ADJ-INT-CRIM – 08/01/2026
DATA: 08/01/2026
ASSUNTO: HOMICÍDIO EM SEBERI - RS
ANEXOS: XXX

Em 08 de janeiro de 2025, um indivíduo foi vítima de latrocínio em Seberi - RS, sem
nenhuma outra informação de registro policial em outro órgão.
"""
    processor = FakeProcessor({
        "registry_number": "015",
        "registry_agency": "",
        "registry_year": "2026",
    })
    extractor = RegistryExtractor(processor)
    result = extractor.extract(header_only_text)
    assert result == {"registry_number": "", "registry_agency": "", "registry_year": ""}


def test_extract_handles_empty_text_gracefully():
    processor = FakeProcessor({"registry_number": None, "registry_agency": None, "registry_year": None})
    extractor = RegistryExtractor(processor)
    assert extractor.extract("") == {"registry_number": "", "registry_agency": "", "registry_year": ""}
    assert extractor.extract("   ") == {"registry_number": "", "registry_agency": "", "registry_year": ""}
