import pytest
from backend.engine.cleaners.text_cleaner import clean_relint_text

def test_clean_relint_text_no_cut():
    # Texto sem nenhuma palavra-chave de corte não deve ser modificado
    raw_text = "Ocorrência de roubo a pedestre no centro de Cruz Alta."
    assert clean_relint_text(raw_text) == raw_text

def test_clean_relint_text_with_distribuicao():
    # Deve cortar tudo a partir de Distribuição:
    raw_text = (
        "Ocorrência de roubo a pedestre.\n"
        "Distribuição:\n"
        "- 1º Batalhão\n"
        "- Delegacia de Polícia"
    )
    expected = "Ocorrência de roubo a pedestre."
    assert clean_relint_text(raw_text) == expected

def test_clean_relint_text_with_assinatura():
    # Deve cortar tudo a partir de Assinatura:
    raw_text = (
        "Fato ocorrido no dia 01/01.\n"
        " Assinatura:\n"
        "Cap. PM João da Silva"
    )
    expected = "Fato ocorrido no dia 01/01."
    assert clean_relint_text(raw_text) == expected

def test_clean_relint_text_case_insensitive_and_accent():
    # Deve reconhecer variações acentuadas e maiúsculas
    raw_text = (
        "Texto principal da ocorrência.\n"
        "DISTRIBUIÇÃO: Geral"
    )
    expected = "Texto principal da ocorrência."
    assert clean_relint_text(raw_text) == expected

    raw_text_accent = (
        "Texto principal da ocorrência.\n"
        "instruções: ler com atenção"
    )
    assert clean_relint_text(raw_text_accent) == expected

def test_clean_relint_text_with_disclaimer():
    raw_text = (
        "Início da ocorrência.\n"
        "DOCUMENTO PREPARATÓRIO – ACESSO RESTRITO\n"
        "Nos termos do Art. 7, § 3º da Lei nº 12.527/2011, os documentos...\n"
        "pessoas ou órgãos não autorizados.\n"
        "Meio do texto da ocorrência."
    )
    expected = "Início da ocorrência.\n\nMeio do texto da ocorrência."
    assert clean_relint_text(raw_text) == expected

def test_clean_relint_text_with_header():
    raw_text = (
        "ESTADO DO RIO GRANDE DO SUL\n"
        "SECRETARIA DA SEGURANÇA PÚBLICA\n"
        "BRIGADA MILITAR\n"
        "SISTEMA DE INTELIGÊNCIA\n"
        "Relatório de inteligência número 01."
    )
    expected = "\n\n\n\nRelatório de inteligência número 01."
    assert clean_relint_text(raw_text) == expected.strip()

def test_clean_relint_text_empty():
    assert clean_relint_text("") == ""
    assert clean_relint_text(None) == ""  # type: ignore

def test_clean_relint_text_pagination():
    # Testar se "Página 1 de 5", "Pág. 3", "Pg 10", "Page 2" e números de linha isolados são removidos
    raw_text = (
        "Página 1 de 5\n"
        "Ocorrência de teste.\n"
        "Pág. 2\n"
        "Conteúdo da segunda página.\n"
        " 12 \n"
        "Fim do documento.\n"
        "pg 3\n"
        "Page 4 of 4"
    )
    # 12 isolado, Página 1 de 5, Pág. 2, pg 3, Page 4 of 4 devem ser removidos.
    # O texto restante deve conter a essência sem esses termos.
    cleaned = clean_relint_text(raw_text)
    assert "Página 1 de 5" not in cleaned
    assert "Pág. 2" not in cleaned
    assert "pg 3" not in cleaned
    assert "Page 4 of 4" not in cleaned
    assert "12" not in cleaned.split("\n")
    assert "Ocorrência de teste." in cleaned
    assert "Conteúdo da segunda página." in cleaned
    assert "Fim do documento." in cleaned


def test_extract_date_and_time_of_fact():
    from backend.engine.cleaners.text_cleaner import extract_date_of_fact, extract_time_of_fact

    text = "Fato ocorrido no dia 15 de julho de 2026, por volta das 14h30min, no centro da cidade."
    assert extract_date_of_fact(text) == "15 de julho de 2026"
    assert extract_time_of_fact(text) == "14h30min"

    text2 = "Ocorrência registrada em 10/08/2026 às 08:15h."
    assert extract_date_of_fact(text2) == "10/08/2026"
    assert extract_time_of_fact(text2) == "08:15h"


def test_extract_map_url_and_coordinates():
    from backend.engine.cleaners.text_cleaner import extract_map_url, resolve_coordinates_and_map_info

    text = "Localização disponível em https://google.com/maps/place/-28.2612,-53.4912 no município."
    url = extract_map_url(text)
    assert "google.com/maps" in url

    text_coords = "Ocorrência no ponto -28.26123, -53.49123 na zona rural."
    found_url, coords = resolve_coordinates_and_map_info(text_coords)
    # Normalizado para 6 casas decimais (padrão Google Maps)
    assert coords == "-28.261230, -53.491230"


def test_extract_subject_fallback():
    from backend.engine.cleaners.text_cleaner import extract_subject_fallback

    text = (
        "RELATÓRIO DE INTELIGÊNCIA Nº 100\n"
        "ASSUNTO: HOMICÍDIO DOLOSO EM PANAMBI - RS\n"
        "ORIGEM: ARI"
    )
    filename = "RELINT 100 - ADJ-INT-CRIM - Homicídio Doloso em Panambi - RS.pdf"

    assert extract_subject_fallback(text, filename) == "HOMICÍDIO DOLOSO EM PANAMBI - RS"
    assert extract_subject_fallback("", filename) == "Homicídio Doloso em Panambi - RS"


def test_extract_fallback_summary():
    from backend.engine.cleaners.text_cleaner import extract_fallback_summary

    text = (
        "RELATÓRIO DE INTELIGÊNCIA Nº 459/2026\n"
        "DATA: 30/07/2026\n"
        "ASSUNTO: ROUBO A ESTABELECIMENTO COMERCIAL EM PANAMBI -RS\n"
        "ORIGEM: ARI/AJ\n"
        "DIFUSÃO: ACI\n"
        "REFERÊNCIA: XXX\n"
        "ANEXOS: XXX\n"
        "Em 30 de julho de 2026, por volta das 01h30min, quatro indivíduos armados efetuaram um roubo.\n"
        "FOTO DO ISOLAMENTO DO LOCAL\n"
        "Segundo relatos, os indivíduos invadiram a residência..."
    )

    summary = extract_fallback_summary(text, subject="ROUBO A ESTABELECIMENTO COMERCIAL")
    assert "RELATÓRIO DE INTELIGÊNCIA" not in summary
    assert "DIFUSÃO:" not in summary
    assert summary.startswith("ROUBO A ESTABELECIMENTO COMERCIAL")


def test_normalize_whitespace_and_paragraphs():
    from backend.engine.cleaners.text_cleaner import normalize_whitespace_and_paragraphs

    raw_text = (
        "como\n"
        "GILMAR\n"
        "LAURINDO\n"
        "BELLINI\n"
        "RG7036249394 - 60 anos , ATUAL PREFEITO DO MUNICÍPIO DE BOA VISTA DO\n"
        "INCRA/RS pelo Partido Democrático Brasileiro (MDB).\n\n"
        "Conforme relato da vítima LUANA, o indivíduo compareceu ao estabelecimento e,\n"
        "durante o atendimento, solicitou seu número de telefone.\n"
    )

    cleaned = normalize_whitespace_and_paragraphs(raw_text)
    assert "como GILMAR LAURINDO BELLINI RG7036249394 - 60 anos, ATUAL PREFEITO" in cleaned
    assert "estabelecimento e, durante o atendimento, solicitou" in cleaned
    assert "anos , ATUAL" not in cleaned

def test_header_anexos_blank_line_separation():
    raw_header_text = (
        "RELATÓRIO DE INTELIGÊNCIA Nº 467/ADJ-INT-CRIM – 02/08/2026\n"
        "DATA: 02/08/2026\n"
        "ASSUNTO: HOMICÍDIO DOLOSO EM PANAMBI - RS\n"
        "ORIGEM: ARI/AJ DIFUSÃO: ACI DIFUSÃO ANTERIOR: XXX REFERÊNCIA:\n"
        "ANEXOS: XXX\n"
        "No dia 02 de agosto de 2026, por volta das 22h, a guarnição foi acionada..."
    )

    cleaned = clean_relint_text(raw_header_text)
    assert "ANEXOS: XXX\n\nNo dia 02 de agosto" in cleaned

def test_clean_person_name():
    from backend.engine.cleaners.text_cleaner import clean_person_name

    assert clean_person_name("Posteriormente Identificado Como Johnny Schroeder") == "Johnny Schroeder"
    assert clean_person_name("Estavam João Witor Fagundes Garmatz") == "João Witor Fagundes Garmatz"
    assert clean_person_name("momento em que foi feito contato com Mariane") == "Mariane"
    assert clean_person_name("Vítima identificada como LUANA MARIA DE LIMA - RG: 8127846916") == "Luana Maria de Lima"

