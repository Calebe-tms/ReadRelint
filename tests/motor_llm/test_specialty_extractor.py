# -*- coding: utf-8 -*-
"""
Testes unitários para o Passo 3 do Pipeline Multi-Pass: extração de campos de
especialidade (SpecialtyExtractor). Cobre os detectores determinísticos (sem LLM)
e os guardrails de enum/evidência textual aplicados à resposta da LLM.
"""

from backend.engine.extractors.llm.extractors.specialty_extractor import (
    SPECIALTY_SCHEMAS,
    SpecialtyExtractor,
    detect_hostage_victim,
    detect_injured_victims,
    detect_location_type,
    detect_recovered,
)
from backend.engine.extractors.llm.llm_processor import ILlmProcessor


class FakeProcessor(ILlmProcessor):
    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls = 0

    def process_text(self, text, questions=None, schema_model=None, pre_extracted_entities=None) -> dict:
        self.calls += 1
        return self.response


# ---------------------------------------------------------------------------
# Detectores determinísticos
# ---------------------------------------------------------------------------

def test_detect_injured_victims_true_for_lesao_singular():
    assert detect_injured_victims("A vítima sofreu lesão corporal leve no braço.") == 1


def test_detect_injured_victims_true_for_lesoes_plural():
    assert detect_injured_victims("A vítima sofreu lesões corporais leves.") == 1


def test_detect_injured_victims_false_when_negated():
    assert detect_injured_victims("A vítima não sofreu lesões corporais.") == 0


def test_detect_injured_victims_false_when_absent():
    assert detect_injured_victims("Ocorrência registrada sem intercorrências.") == 0


def test_detect_hostage_victim_true_for_refem_singular():
    assert detect_hostage_victim("A vítima foi mantida como refém por 10 minutos.") == 1


def test_detect_hostage_victim_true_for_refens_plural():
    assert detect_hostage_victim("Duas vítimas foram feitas reféns durante o roubo.") == 1


def test_detect_hostage_victim_false_when_negated():
    assert detect_hostage_victim("Não houve reféns durante a ocorrência.") == 0


def test_detect_recovered_true():
    assert detect_recovered("O veículo foi recuperado horas depois pela guarnição.") == 1


def test_detect_recovered_false_when_negated():
    assert detect_recovered("O veículo não foi recuperado até o momento.") == 0


def test_detect_location_type_rural_when_interior():
    assert detect_location_type("Interior") == "Rural"


def test_detect_location_type_urban_otherwise():
    assert detect_location_type("Centro") == "Urbano"
    assert detect_location_type("") == "Urbano"


# ---------------------------------------------------------------------------
# Especialidades sem campo livre nunca chamam a LLM
# ---------------------------------------------------------------------------

def test_specialty_without_free_fields_never_calls_llm():
    for bm_group in ("Roubo a Residência", "Furto Qualificado", "Outros"):
        assert bm_group not in SPECIALTY_SCHEMAS
        processor = FakeProcessor({})
        extractor = SpecialtyExtractor(processor)
        extractor.extract("qualquer texto", bm_group=bm_group)
        assert processor.calls == 0


def test_residencia_resolves_deterministic_fields_without_llm():
    processor = FakeProcessor({})
    extractor = SpecialtyExtractor(processor)
    result = extractor.extract(
        "A vítima sofreu lesões corporais leves. Interior.",
        bm_group="Roubo a Residência",
        neighborhood="Interior",
    )
    assert processor.calls == 0
    assert result["injured_victims"] == 1
    assert result["location_type"] == "Rural"
    assert result["hostage_victim"] == 0


# ---------------------------------------------------------------------------
# Guardrails de enum fechado
# ---------------------------------------------------------------------------

def test_homicide_invalid_fact_type_is_discarded():
    processor = FakeProcessor({"fact_type": "Provável", "motivation": "Feminicídio"})
    extractor = SpecialtyExtractor(processor)
    text = "Feminicídio ocorrido na residência da vítima."
    result = extractor.extract(text, bm_group="Homicídio")
    assert "fact_type" not in result
    assert result["motivation"] == "Feminicídio"


def test_homicide_motivation_outside_enum_is_discarded():
    processor = FakeProcessor({"motivation": "Motivo desconhecido qualquer"})
    extractor = SpecialtyExtractor(processor)
    result = extractor.extract("texto qualquer", bm_group="Homicídio")
    assert "motivation" not in result


def test_pedestrian_weapon_outside_enum_is_discarded():
    processor = FakeProcessor({"weapon_used": "Faca improvisada estranha", "stolen_object": "celular"})
    extractor = SpecialtyExtractor(processor)
    text = "Roubo a pedestre com subtração de celular."
    result = extractor.extract(text, bm_group="Roubo a Pedestre")
    assert "weapon_used" not in result
    assert result["stolen_object"] == "celular"


def test_pedestrian_weapon_within_enum_is_kept():
    processor = FakeProcessor({"weapon_used": "arma de fogo"})
    extractor = SpecialtyExtractor(processor)
    result = extractor.extract("Roubo mediante emprego de arma de fogo.", bm_group="Roubo a Pedestre")
    assert result["weapon_used"] == "Arma de fogo"


# ---------------------------------------------------------------------------
# Guardrail de evidência textual (campos livres)
# ---------------------------------------------------------------------------

def test_drug_trafficking_discards_quantity_without_textual_evidence():
    processor = FakeProcessor({"drug_quantity": "500g", "drug_types": "Cocaína"})
    extractor = SpecialtyExtractor(processor)
    text = "Prisão por tráfico com apreensão de porções de Cocaína."
    result = extractor.extract(text, bm_group="Prisão por Tráfico")
    assert "drug_quantity" not in result
    assert result["drug_types"] == "Cocaína"


def test_vehicle_specialty_keeps_model_with_evidence_and_recovered_flag():
    processor = FakeProcessor({"vehicle_model": "Fiat Uno", "license_plate": "ABC1234"})
    extractor = SpecialtyExtractor(processor)
    text = "O veículo Fiat Uno, placa ABC1234, foi recuperado na sequência."
    result = extractor.extract(text, bm_group="Roubo de Veículo")
    assert result["vehicle_model"] == "Fiat Uno"
    assert result["license_plate"] == "ABC1234"
    assert result["recovered"] == 1


def test_specialty_extractor_survives_llm_exception():
    class ExplodingProcessor(ILlmProcessor):
        def process_text(self, *args, **kwargs):
            raise RuntimeError("Ollama indisponível")

    extractor = SpecialtyExtractor(ExplodingProcessor())
    result = extractor.extract("texto qualquer", bm_group="Homicídio")
    assert result == {}
