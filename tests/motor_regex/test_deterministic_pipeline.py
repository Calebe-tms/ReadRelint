# -*- coding: utf-8 -*-
from backend.engine.extractors.deterministic.pipeline import DeterministicPipeline


def test_deterministic_pipeline_full_execution():
    pipeline = DeterministicPipeline()
    sample_text = """
    SECRETARIA DA SEGURANÇA PÚBLICA
    BRIGADA MILITAR - 16º BPM
    RELATÓRIO DE INTELIGÊNCIA

    ASSUNTO: HOMICÍDIO CONSUMADO EM CRUZ ALTA

    HISTÓRICO:
    No dia 15/08/2026, às 22h30min, na Rua General Osório, 120, Bairro Centro, Cruz Alta - RS,
    a vítima JOÃO BATISTA DE SOUZA, RG: 8172635491, foi encontrada caída com ferimentos por disparos.
    O suspeito MARCOS VINICIUS COSTA (vulgo "Alemão") foi visto fugindo do local.

    COORDENADAS: -28.6385, -53.6063
    """

    result = pipeline.extract(sample_text, filename="RELINT_01_HOMICIDIO.pdf")

    assert result.success is True
    assert result.extraction_method == "Regex (Sem IA)"
    assert "HOMICÍDIO" in result.data["subject"].upper()
    assert result.data["bm_group"] == "Homicídio"

    # Participantes extraídos
    participants = result.data.get("participants", [])
    names = [p["name"].upper() for p in participants]
    assert any("JOÃO BATISTA" in n for n in names)
    assert any("MARCOS VINICIUS" in n for n in names)


def test_deterministic_pipeline_empty_text():
    pipeline = DeterministicPipeline()
    result = pipeline.extract("", filename="teste.pdf")
    assert result.success is False
    assert len(result.alerts) > 0
    assert any(a.stage == "input_validation" for a in result.alerts)
