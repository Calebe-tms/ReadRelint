# -*- coding: utf-8 -*-
"""
Testes unitários para os guardrails determinísticos do LocationExtractor:
quebra de linha no sinal de coordenadas, conversão DMS, blindagem geográfica
do RS, resolução determinística de unidade policial e guardrail de rua.
"""

from backend.engine.extractors.llm.extractors.location_extractor import (
    LocationExtractor,
    check_raw_text_geo_sources,
    dms_to_decimal,
    enforce_rs_coordinate_signs,
    extract_battalion_mentions,
    extract_municipality_from_context,
    format_google_standard_address,
    normalize_line_broken_sign,
    resolve_battalion_by_municipality,
    resolve_police_unit,
    text_contains,
    validate_municipality,
)
from backend.engine.extractors.llm.llm_processor import ILlmProcessor


class FakeProcessor(ILlmProcessor):
    """Processor falso para testar o LocationExtractor sem depender do Ollama real."""

    def __init__(self, response: dict) -> None:
        self.response = response

    def process_text(self, text, questions=None, schema_model=None, pre_extracted_entities=None) -> dict:
        return self.response


# ---------------------------------------------------------------------------
# Quebra de linha no sinal de coordenadas (bug real encontrado na auditoria)
# ---------------------------------------------------------------------------

def test_normalize_line_broken_sign_reattaches_minus_to_digit():
    broken = "nas coordenadas geográficas: -\n28.704834, -53.111531, por volta das 21h30min."
    fixed = normalize_line_broken_sign(broken)
    assert "-28.704834" in fixed
    assert "\n28" not in fixed


def test_check_raw_text_geo_sources_recovers_latitude_sign():
    text = "Interior (-\n28.715267, -53.019818), conforme relatado pela guarnição."
    has_coords, _, raw_coords, _ = check_raw_text_geo_sources(text)
    assert has_coords is True
    assert raw_coords == "-28.715267, -53.019818"


# ---------------------------------------------------------------------------
# Conversão DMS -> decimal
# ---------------------------------------------------------------------------

def test_dms_to_decimal_applies_southern_western_negative_sign():
    lat = dms_to_decimal("28", "34", "58.5", "S")
    lon = dms_to_decimal("53", "7", "10.0", "W")
    assert round(lat, 4) == -28.5829
    assert round(lon, 4) == -53.1194


def test_check_raw_text_geo_sources_converts_dms_pattern_to_decimal():
    text = "acionada nas coordenadas 28°34'58.5\"S 53°07'10.0\"W conforme registrado."
    has_coords, _, raw_coords, _ = check_raw_text_geo_sources(text)
    assert has_coords is True
    lat_str, lon_str = [p.strip() for p in raw_coords.split(",")]
    assert float(lat_str) < 0
    assert float(lon_str) < 0


# ---------------------------------------------------------------------------
# Blindagem geográfica do RS (sinal negativo obrigatório + faixa válida)
# ---------------------------------------------------------------------------

def test_enforce_rs_coordinate_signs_forces_negative_latitude():
    assert enforce_rs_coordinate_signs("28.704834, -53.111531") == "-28.704834, -53.111531"


def test_enforce_rs_coordinate_signs_forces_negative_on_both_axes():
    assert enforce_rs_coordinate_signs("28.6914035686101, 53.62326597234348") == "-28.691404, -53.623266"


def test_enforce_rs_coordinate_signs_rejects_placeholder_text():
    for placeholder in ("N/A", "Não disponível", "Sem informação", "https://maps.app.goo.gl/xyz", "Latitude, Longitude"):
        assert enforce_rs_coordinate_signs(placeholder) == ""


def test_enforce_rs_coordinate_signs_rejects_out_of_range_values():
    # Latitude fora da faixa aproximada do RS (~-27 a -34)
    assert enforce_rs_coordinate_signs("5.1234, -53.1234") == ""


def test_enforce_rs_coordinate_signs_normalizes_to_six_decimals():
    # Padrão Google Maps: sempre 6 casas decimais — completa com zero quando falta precisão...
    assert enforce_rs_coordinate_signs("-28.2612, -53.4912") == "-28.261200, -53.491200"
    # ...e trunca/arredonda quando o documento tinha mais dígitos do que o padrão.
    assert enforce_rs_coordinate_signs("-28.6914035686101, -53.62326597234348") == "-28.691404, -53.623266"


# ---------------------------------------------------------------------------
# Resolução determinística de unidade policial (tabela município -> BPM)
# ---------------------------------------------------------------------------

def test_resolve_battalion_by_municipality_known_city():
    assert resolve_battalion_by_municipality("Cruz Alta") == "16º BPM"
    assert resolve_battalion_by_municipality("Seberi") == "37º BPM"
    assert resolve_battalion_by_municipality("Santa Bárbara do Sul") == "39º BPM"


def test_resolve_battalion_by_municipality_normalizes_accents_and_case():
    assert resolve_battalion_by_municipality("sao pedro das missoes") == "39º BPM"


def test_resolve_battalion_by_municipality_unknown_city_returns_empty():
    assert resolve_battalion_by_municipality("Porto Alegre") == ""


def test_extract_battalion_mentions_deduplicates_repeated_numbers():
    text = "Uma guarnição do 16º BPM foi acionada. Reforço adicional do 16º BPM chegou em seguida."
    assert extract_battalion_mentions(text) == ["16"]


def test_extract_battalion_mentions_ignores_invalid_numbers():
    text = "Artigo 13 do código, seguido pela guarnição do 156º BPM (typo)."
    # "13" não é um BPM válido; "156" não bate no padrão de 1-2 dígitos
    assert extract_battalion_mentions(text) == []


def test_resolve_police_unit_single_literal_mention_wins_over_table():
    # Tabela diz 16º BPM para Cruz Alta, mas o texto cita explicitamente o 37º BPM (apoio mútuo)
    text = "Compareceu ao local uma guarnição do 37º BPM para apoio à ocorrência."
    assert resolve_police_unit("Cruz Alta", text) == "37º BPM"


def test_resolve_police_unit_no_mention_falls_back_to_table():
    assert resolve_police_unit("Cruz Alta", "texto sem nenhuma menção a batalhão") == "16º BPM"


def test_resolve_police_unit_ambiguous_mentions_fall_back_to_table():
    text = "O 16º BPM foi acionado, com apoio posterior do 39º BPM."
    assert resolve_police_unit("Seberi", text) == "37º BPM"


def test_resolve_police_unit_unknown_municipality_without_mention_is_blank():
    assert resolve_police_unit("Porto Alegre", "nenhuma unidade citada aqui") == ""


# ---------------------------------------------------------------------------
# Guardrail de evidência textual
# ---------------------------------------------------------------------------

def test_text_contains_is_tolerant_to_accent_and_case():
    assert text_contains("Rua General Osório", "ocorrido na rua general osorio, conforme relatado") is True


def test_text_contains_returns_false_when_absent():
    assert text_contains("Rua General Osório", "nenhuma rua foi mencionada no relatório") is False


# ---------------------------------------------------------------------------
# Integração: LocationExtractor.extract() com processor falso
# ---------------------------------------------------------------------------

def test_extract_discards_hallucinated_street_without_textual_evidence():
    text = "ASSUNTO: FURTO EM CRUZ ALTA - RS\nOcorreu um furto na cidade, sem endereço específico relatado."
    extractor = LocationExtractor(FakeProcessor({
        "street": "Rua General Osório",
        "number": "S/N",
        "neighborhood": "Centro",
        "municipality": "Cruz Alta",
        "coordinates": None,
        "map_url": None,
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert "osório" not in result["address"].lower()


def test_extract_assunto_municipality_wins_over_diverging_llm_answer():
    # Reproduz o caso real encontrado na auditoria (id 743 do banco): ASSUNTO diz uma cidade,
    # mas o corpo do texto cita outra cidade (ex: origem do veículo furtado) e a LLM confunde as duas.
    text = (
        "ASSUNTO: PRISÃO POR ROUBO DE VEÍCULO EM SANTA BÁRBARA DO SUL - RS\n"
        "Ocorreu um Roubo de Veículo no município de Panambi - RS, sendo que o automóvel foi "
        "posteriormente localizado em Santa Bárbara do Sul - RS."
    )
    extractor = LocationExtractor(FakeProcessor({
        "street": None,
        "number": None,
        "neighborhood": None,
        "municipality": "Panambi",
        "coordinates": None,
        "map_url": None,
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["municipality"].lower() == "santa bárbara do sul"
    assert result["municipality"].lower() != "panambi"


def test_format_address_discards_sem_informacao_especifica_placeholder():
    # Auditoria de 2026-09 (RELINT id 345 real): placeholder "Sem informação específica" vazava
    # pro endereço composto em vez de ser descartado como os outros placeholders já eram.
    address = format_google_standard_address(
        street="Sem informação específica", number="", neighborhood="", municipality="Cruz Alta",
    )
    assert "sem informação específica" not in address.lower()


def test_extract_discards_literal_null_string_from_llm_municipality():
    # Auditoria de 2026-09 (RELINT id 313 real): sem cidade no ASSUNTO/filename, a LLM às vezes
    # devolve a string literal "null" (não o JSON null) — não pode virar o valor do município.
    text = "ASSUNTO: RESPOSTA AO PB 7561 - QUANTITATIVO DE PISTOLAS\nRelatório administrativo sem cidade específica."
    extractor = LocationExtractor(FakeProcessor({
        "street": None, "number": None, "neighborhood": None,
        "municipality": "null", "coordinates": None, "map_url": None,
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["municipality"] != "null"
    assert result["municipality"] == ""


def test_extract_municipality_ignores_earlier_em_occurrences_in_assunto():
    # Auditoria de 2026-09 (RELINT id 631 real): assunto com mais de um "em" antes da cidade
    # ("...em face de policial militar em serviço em Panambi - RS") capturava tudo entre o
    # primeiro "em" e o único "- RS" do texto, em vez de só o nome da cidade.
    text = (
        "ASSUNTO: Prisão por lesão corporal leve em face de policial militar "
        "em serviço em Panambi - RS"
    )
    assert extract_municipality_from_context(text) == "Panambi"


def test_extract_municipality_ignores_earlier_em_occurrences_in_filename():
    filename = "RELINT 001 - Prisão em face de policial em serviço em Panambi - RS.pdf"
    assert extract_municipality_from_context("", filename=filename) == "Panambi"


def test_validate_municipality_accepts_the_41_battalion_cities():
    assert validate_municipality("Cruz Alta") == "Cruz Alta"


def test_validate_municipality_accepts_other_rs_cities_via_ibge_list():
    # Farroupilha é um município real do RS, mas fora da lista de 41 com BPM conhecido.
    assert validate_municipality("Farroupilha") == "Farroupilha"


def test_validate_municipality_rejects_non_municipality_text():
    assert validate_municipality("Face De Policial Militar Em Serviço Em Panambi") == ""
    assert validate_municipality("") == ""


def test_extract_discards_municipality_that_is_not_a_real_city():
    # Fim a fim: mesmo se o regex determinístico (ou a LLM) capturar algo que não é uma
    # cidade real, o resultado final de municipality deve vir vazio, não o texto lixo.
    text = (
        "ASSUNTO: Prisão por lesão corporal leve em face de policial militar "
        "em serviço em Cidade Que Não Existe No Rs - RS\nTexto do histórico."
    )
    extractor = LocationExtractor(FakeProcessor({
        "street": None, "number": None, "neighborhood": None,
        "municipality": None, "coordinates": None, "map_url": None,
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["municipality"] == ""


def test_extract_resolves_police_unit_deterministically_without_llm_field():
    text = "ASSUNTO: FURTO EM CRUZ ALTA - RS\nOcorrência registrada sem menção a unidade responsável."
    extractor = LocationExtractor(FakeProcessor({
        "street": None, "number": None, "neighborhood": None,
        "municipality": "Cruz Alta", "coordinates": None, "map_url": None,
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["police_unit"] == "16º BPM"


# ---------------------------------------------------------------------------
# location_types (categorização livre do tipo de local, sem enum fechado)
# ---------------------------------------------------------------------------

def test_extract_captures_location_types_list():
    text = "ASSUNTO: FURTO EM CRUZ ALTA - RS\nO fato ocorreu em uma propriedade rural isolada."
    extractor = LocationExtractor(FakeProcessor({
        "street": None, "number": None, "neighborhood": None,
        "municipality": "Cruz Alta", "coordinates": None, "map_url": None,
        "location_types": ["Propriedade Rural"],
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["location_types"] == ["Propriedade Rural"]


def test_extract_location_types_defaults_to_empty_list_when_absent():
    text = "ASSUNTO: FURTO EM CRUZ ALTA - RS\nSem detalhes adicionais do local."
    extractor = LocationExtractor(FakeProcessor({
        "street": None, "number": None, "neighborhood": None,
        "municipality": "Cruz Alta", "coordinates": None, "map_url": None,
        "location_types": None,
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["location_types"] == []


def test_extract_location_types_filters_placeholders_and_dedupes():
    text = "ASSUNTO: FURTO EM CRUZ ALTA - RS\nO fato ocorreu em uma escola municipal."
    extractor = LocationExtractor(FakeProcessor({
        "street": None, "number": None, "neighborhood": None,
        "municipality": "Cruz Alta", "coordinates": None, "map_url": None,
        "location_types": ["Escolas", "N/A", "escolas", "", "None"],
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["location_types"] == ["Escolas"]


def test_extract_location_types_caps_at_five_categories():
    text = "ASSUNTO: FURTO EM CRUZ ALTA - RS\nMúltiplas características do local."
    extractor = LocationExtractor(FakeProcessor({
        "street": None, "number": None, "neighborhood": None,
        "municipality": "Cruz Alta", "coordinates": None, "map_url": None,
        "location_types": ["A", "B", "C", "D", "E", "F", "G"],
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["location_types"] == ["A", "B", "C", "D", "E"]


def test_extract_location_types_ignores_non_list_response():
    text = "ASSUNTO: FURTO EM CRUZ ALTA - RS\nSem detalhes adicionais do local."
    extractor = LocationExtractor(FakeProcessor({
        "street": None, "number": None, "neighborhood": None,
        "municipality": "Cruz Alta", "coordinates": None, "map_url": None,
        "location_types": "Propriedade Rural",
    }))
    result = extractor.extract(text, filename="teste.pdf")
    assert result["location_types"] == []
