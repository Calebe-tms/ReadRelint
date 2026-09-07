# -*- coding: utf-8 -*-
from backend.engine.extractors.deterministic.rules.homicide_rule import HomicideDeterministicRule
from backend.engine.extractors.deterministic.rules.drug_trafficking_rule import DrugTraffickingDeterministicRule


def test_homicide_deterministic_rule_extraction():
    rule = HomicideDeterministicRule()
    assert rule.name == "Homicídios (Determinístico)"

    # Caso 1: Homicídio consumado ligado a tráfico
    sample_text_1 = """
    No local foi constatado o óbito da vítima atingida por disparos.
    Informações dão conta de que o crime ocorreu em disputa de território do tráfico de drogas da facção local.
    """
    data_1, alerts_1 = rule.extract_specialty_data(sample_text_1)
    assert data_1["fact_type"] == "Consumado"
    assert data_1["motivation"] == "Tráfico de Drogas"

    # Caso 2: Tentativa de feminicídio
    sample_text_2 = """
    Ocorrência de tentativa de homicídio contra a mulher pelo ex-marido (caso de feminicídio).
    A vítima foi socorrida ao hospital com vida.
    """
    data_2, alerts_2 = rule.extract_specialty_data(sample_text_2)
    assert data_2["fact_type"] == "Tentado"
    assert data_2["motivation"] == "Feminicídio"


def test_drug_trafficking_deterministic_rule_extraction():
    rule = DrugTraffickingDeterministicRule()
    assert rule.name == "Tráfico de Drogas (Determinístico)"

    sample_text = """
    Durante abordagem ao suspeito, foram localizados 500g de cocaína, 32 pedras de crack e 15 buchas de maconha.
    """
    data, alerts = rule.extract_specialty_data(sample_text)
    assert "Cocaína" in data["drug_types"]
    assert "Crack" in data["drug_types"]
    assert "Maconha" in data["drug_types"]
    assert "500g" in data["drug_quantities"]
    assert "32 pedras" in data["drug_quantities"]
