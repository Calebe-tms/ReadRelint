# -*- coding: utf-8 -*-
from backend.engine.extractors.deterministic.participants.role_detector import (
    detect_participation_role,
    extract_nickname,
    extract_document_near_name,
)


def test_detect_participation_role():
    # Contexto de Vítima
    text_victim = "No local do fato, a vítima Carlos Alberto da Silva foi alvejada por disparos e socorrida ao HPS."
    assert detect_participation_role(text_victim, "Carlos Alberto da Silva") == "Vítima"

    # Contexto de Acusado / Preso / Autor
    text_accused = "Durante diligências, o autor dos disparos Marcos Vinicius Pereira foi preso em flagrante com a arma."
    assert detect_participation_role(text_accused, "Marcos Vinicius Pereira") == "Autor/Suspeito"

    # Contexto de Testemunha
    text_witness = "A testemunha Maria Aparecida relatou que ouviu cerca de 5 estampidos na esquina."
    assert detect_participation_role(text_witness, "Maria Aparecida") == "Testemunha"

    # Contexto genérico / Suspeito
    text_generic = "Indivíduo João da Silva foi abordado transitando na via pública."
    assert detect_participation_role(text_generic, "João da Silva") == "Autor/Suspeito"


def test_extract_nickname():
    text1 = "O indivíduo Paulo Roberto (vulgo Caveirinha) tentou fugir pelos fundos."
    assert extract_nickname(text1, "Paulo Roberto") == "Caveirinha"

    text2 = "Contato com Lucas Oliveira \"Gordo\" no interior da residência."
    assert extract_nickname(text2, "Lucas Oliveira") == "Gordo"

    text3 = "Nome: Gabriel Souza sem alcunha informada."
    assert extract_nickname(text3, "Gabriel Souza") == ""


def test_extract_document_near_name():
    text = "Participante: Rodrigo Mendes, RG: 8127394812, filho de Maria Mendes."
    assert extract_document_near_name(text, "Rodrigo Mendes") == "8127394812"

    text_cpf = "Indivíduo Lucas Silva CPF 123.456.789-00 abordado."
    assert "123.456.789-00" in extract_document_near_name(text_cpf, "Lucas Silva")
