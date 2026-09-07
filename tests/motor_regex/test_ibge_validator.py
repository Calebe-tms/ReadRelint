# -*- coding: utf-8 -*-
from backend.engine.extractors.deterministic.participants.ibge_validator import (
    is_valid_first_name,
    is_valid_brazilian_name,
)


def test_is_valid_first_name():
    # Prenomes brasileiros comuns devem retornar True
    assert is_valid_first_name("Carlos") is True
    assert is_valid_first_name("carlos") is True
    assert is_valid_first_name("Maria") is True
    assert is_valid_first_name("João") is True
    assert is_valid_first_name("JOAO") is True
    assert is_valid_first_name("Wellington") is True
    assert is_valid_first_name("Daiane") is True
    assert is_valid_first_name("Gabriel") is True

    # Palavras e substantivos comuns não devem ser prenomes válidos
    assert is_valid_first_name("Hospital") is False
    assert is_valid_first_name("Avenida") is False
    assert is_valid_first_name("Relatório") is False
    assert is_valid_first_name("Delegacia") is False
    assert is_valid_first_name("") is False


def test_is_valid_brazilian_name():
    # Nomes completos válidos
    assert is_valid_brazilian_name("Carlos Eduardo da Silva") is True
    assert is_valid_brazilian_name("Maria de Fátima") is True
    assert is_valid_brazilian_name("Johnny Schroeder") is True
    assert is_valid_brazilian_name("João Witor Fagundes") is True

    # Termos não humanos ou inválidos
    assert is_valid_brazilian_name("Hospital de Pronto Socorro") is False
    assert is_valid_brazilian_name("Avenida Brasil 1500") is False
    assert is_valid_brazilian_name("Carlos") is False  # Nome único sem sobrenome
    assert is_valid_brazilian_name("") is False
