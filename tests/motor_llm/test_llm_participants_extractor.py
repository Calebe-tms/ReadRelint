# -*- coding: utf-8 -*-
"""
Testes unitários para o LlmParticipantsExtractor: guardrail de evidência literal, blacklist
anti-PM/instituição, e enriquecimento determinístico de vulgo/documento por proximidade ao nome.
"""

from backend.engine.extractors.llm.extractors.llm_participants_extractor import LlmParticipantsExtractor
from backend.engine.extractors.llm.llm_processor import ILlmProcessor


class FakeProcessor(ILlmProcessor):
    """Processor falso para testar o LlmParticipantsExtractor sem depender do Ollama real."""

    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls = 0

    def process_text(self, text, questions=None, schema_model=None, pre_extracted_entities=None) -> dict:
        self.calls += 1
        return self.response


def test_extract_returns_empty_for_blank_text():
    extractor = LlmParticipantsExtractor(FakeProcessor({"participants": []}))
    assert extractor.extract("") == []
    assert extractor.extract("   ") == []


def test_extract_survives_llm_exception():
    class ExplodingProcessor(ILlmProcessor):
        def process_text(self, *args, **kwargs):
            raise RuntimeError("Ollama indisponível")

    extractor = LlmParticipantsExtractor(ExplodingProcessor())
    assert extractor.extract("texto qualquer") == []


def test_extract_discards_participant_without_name():
    processor = FakeProcessor({"participants": [{"participation_type": "Vítima"}]})
    extractor = LlmParticipantsExtractor(processor)
    assert extractor.extract("texto qualquer") == []


def test_extract_discards_hallucinated_name_without_textual_evidence():
    processor = FakeProcessor({"participants": [{"name": "Fulano Inventado", "participation_type": "Vítima"}]})
    extractor = LlmParticipantsExtractor(processor)
    text = "A vítima Maria da Silva foi socorrida ao hospital."
    assert extractor.extract(text) == []


def test_extract_discards_blacklisted_pm_name():
    processor = FakeProcessor({"participants": [{"name": "SD PM Carlos Alberto", "participation_type": "Autor/Suspeito"}]})
    extractor = LlmParticipantsExtractor(processor)
    text = "Compareceu ao local o SD PM Carlos Alberto para atendimento da ocorrência."
    assert extractor.extract(text) == []


def test_extract_keeps_valid_victim_with_evidence():
    processor = FakeProcessor({"participants": [{"name": "Maria da Silva", "participation_type": "Vítima", "background": None}]})
    extractor = LlmParticipantsExtractor(processor)
    text = "A vítima Maria da Silva foi socorrida ao hospital municipal."
    result = extractor.extract(text)
    assert len(result) == 1
    assert result[0]["name"] == "Maria da Silva"
    assert result[0]["participation_type"] == "Vítima"
    assert result[0]["background"] == ""


def test_extract_enriches_nickname_and_document_deterministically():
    processor = FakeProcessor({"participants": [{"name": "Carlos Souza", "participation_type": "Autor/Suspeito"}]})
    extractor = LlmParticipantsExtractor(processor)
    text = (
        "O autor Carlos Souza, vulgo Carlão, RG: 1234567, foi preso em flagrante "
        "pela guarnição durante patrulhamento na região central."
    )
    result = extractor.extract(text)
    assert len(result) == 1
    assert result[0]["nickname"] == "Carlão"
    assert "1234567" in result[0]["document"]


def test_extract_defaults_missing_participation_type_to_autor_suspeito():
    processor = FakeProcessor({"participants": [{"name": "João Pereira"}]})
    extractor = LlmParticipantsExtractor(processor)
    text = "Foi identificado como autor do fato João Pereira, que fugiu do local."
    result = extractor.extract(text)
    assert len(result) == 1
    assert result[0]["participation_type"] == "Autor/Suspeito"


def test_extract_handles_multiple_participants_and_malformed_entries():
    processor = FakeProcessor({
        "participants": [
            {"name": "Ana Ferreira", "participation_type": "Testemunha"},
            "entrada malformada, nao deveria quebrar",
            {"name": "", "participation_type": "Vítima"},
            {"name": "Pedro Lima", "participation_type": "Autor/Suspeito"},
        ]
    })
    extractor = LlmParticipantsExtractor(processor)
    text = "A testemunha Ana Ferreira relatou ter visto Pedro Lima fugir do local do crime."
    result = extractor.extract(text)
    names = {p["name"] for p in result}
    assert names == {"Ana Ferreira", "Pedro Lima"}


def test_extract_returns_empty_when_response_not_dict():
    processor = FakeProcessor(["nao", "eh", "um", "dict"])
    extractor = LlmParticipantsExtractor(processor)
    assert extractor.extract("texto qualquer") == []


def test_extract_returns_empty_when_participants_key_not_a_list():
    processor = FakeProcessor({"participants": "nao eh uma lista"})
    extractor = LlmParticipantsExtractor(processor)
    assert extractor.extract("texto qualquer") == []
