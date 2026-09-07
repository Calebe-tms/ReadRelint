# -*- coding: utf-8 -*-
from backend.engine.extractors.deterministic.participants.participant_extractor import ParticipantExtractor


def test_participant_extractor_structured_block():
    extractor = ParticipantExtractor()
    sample_text = """
    RELATÓRIO DE INTELIGÊNCIA - BM
    NOME: JOÃO DA SILVA
    RG: 9182736451
    ALCUNHA: GORDO

    NOME: SD PM MARCELO SANTOS
    RG: 1111111111
    """
    participants, alerts = extractor.extract_participants(sample_text)

    # SD PM Marcelo Santos deve ser excluído pelo filtro anti-PM
    names = [p["name"].upper() for p in participants]
    assert "JOÃO DA SILVA" in names
    assert not any("MARCELO SANTOS" in n for n in names)

    joao = next(p for p in participants if p["name"].upper() == "JOÃO DA SILVA")
    assert joao["document"] == "9182736451"
    assert joao["nickname"] == "Gordo"


def test_participant_extractor_inline_and_exclusion():
    extractor = ParticipantExtractor()
    sample_text = """
    No local, a guarnição da Brigada Militar composta pelo 2° SGT PM Rodrigo e SD PM Lima fez contato com a vítima
    MARIA DE FATIMA SOUZA, RG 8271635412, a qual relatou que o acusado CARLOS EDUARDO PEREIRA (vulgo "Seco")
    adentrou sua residência. Posteriormente, foi encaminhada ao Hospital de Pronto Socorro.
    """
    participants, alerts = extractor.extract_participants(sample_text)

    names = [p["name"].upper() for p in participants]
    # Nomes reais devem ser capturados
    assert any("MARIA DE FATIMA" in n for n in names)
    assert any("CARLOS EDUARDO" in n for n in names)

    # Termos institucionais e militares não devem entrar
    assert not any("HOSPITAL" in n for n in names)
    assert not any("BRIGADA" in n for n in names)
    assert not any("RODRIGO" in n and "SGT" in n for n in names)


def test_participant_extractor_empty():
    extractor = ParticipantExtractor()
    participants, alerts = extractor.extract_participants("")
    assert participants == []
    assert alerts == []
