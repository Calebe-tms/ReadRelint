import pytest
from backend.engine.cleaners.name_parser import BrazilianNameParser
from backend.engine.cleaners.text_cleaner import clean_person_name


def test_standard_brazilian_names():
    """Testa a limpeza de nomes civis comuns em pt-BR com conectivos."""
    assert BrazilianNameParser.clean_name("ELEMAR SOARES DA SILVA") == "Elemar Soares da Silva"
    assert BrazilianNameParser.clean_name("joão pedro dos santos e silva") == "João Pedro dos Santos e Silva"
    assert BrazilianNameParser.clean_name("MARIANE DE SOUZA") == "Mariane de Souza"


def test_prefix_removal():
    """Testa a remoção de prefixos policiais e narrativos comuns."""
    raw_1 = "vítima identificada como MARCOS ANTONIO DA SILVA"
    assert BrazilianNameParser.clean_name(raw_1) == "Marcos Antonio da Silva"

    raw_2 = "Posteriormente identificado como Johnny Schroeder"
    assert BrazilianNameParser.clean_name(raw_2) == "Johnny Schroeder"

    raw_3 = "uma agressão sofrida por ELEMAR SOARES DA SILVA no local"
    assert BrazilianNameParser.clean_name(raw_3) == "Elemar Soares da Silva"

    raw_4 = "momento em que foi feito contato com Mariane"
    assert BrazilianNameParser.clean_name(raw_4) == "Mariane"

    raw_5 = "trata-se de CARLOS EDUARDO"
    assert BrazilianNameParser.clean_name(raw_5) == "Carlos Eduardo"


def test_suffix_and_details_removal():
    """Testa o corte de sufixos de endereço, idade e documentos."""
    raw_1 = "GUSTAVO SCHMIDT, residente no bairro Centro"
    assert BrazilianNameParser.clean_name(raw_1) == "Gustavo Schmidt"

    raw_2 = "ROBERTO SILVA, RG 12.345.678"
    assert BrazilianNameParser.clean_name(raw_2) == "Roberto Silva"

    raw_3 = "LUCAS FERREIRA com idade de 25 anos"
    assert BrazilianNameParser.clean_name(raw_3) == "Lucas Ferreira"


def test_nickname_extraction():
    """Testa a extração e separação de alcunhas/vulgos."""
    res_1 = BrazilianNameParser.parse_person("JOÃO DOS SANTOS, vulgo 'Alemão'")
    assert res_1["name"] == "João dos Santos"
    assert res_1["nickname"] == "Alemão"

    res_2 = BrazilianNameParser.parse_person('GUSTAVO SCHMIDT "Guto"')
    assert res_2["name"] == "Gustavo Schmidt"
    assert res_2["nickname"] == "Guto"

    res_3 = BrazilianNameParser.parse_person("MARCOS DA SILVA, alcunha Marquinhos, residente no Centro")
    assert res_3["name"] == "Marcos da Silva"
    assert res_3["nickname"] == "Marquinhos"


def test_invalid_noise_strings():
    """Testa strings institucionais que não devem gerar nomes de pessoas."""
    assert BrazilianNameParser.clean_name("DOCUMENTO PREPARATÓRIO ACESSO RESTRITO") == ""
    assert BrazilianNameParser.clean_name("16º BATALHÃO DE POLÍCIA MILITAR") == ""
    assert BrazilianNameParser.clean_name("VEÍCULO APREENDIDO NO LOCAL") == ""


def test_clean_person_name_helper_integration():
    """Testa a integração da função utilitária clean_person_name."""
    assert clean_person_name("vítima identificada como MARCOS ANTONIO DA SILVA") == "Marcos Antonio da Silva"
