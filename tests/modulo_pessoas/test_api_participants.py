"""
Testes unitários e de integração para os endpoints de Participantes e Dossiês (/api/v1/participants).
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.api.dependencies import get_person_repo
from backend.core.entities import Person
from backend.database.sqlite_person_repo import SqlitePersonRepo


def test_list_participants_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/participants")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "person_id" in first or "chave_pessoa" in first
        assert "name" in first or "nome" in first
        assert "photos" in first or "galeria_fotos" in first
        assert "linked_relints_count" in first or "quantidade_relints" in first

def test_list_participants_search_filter():
    client = TestClient(app)
    response = client.get("/api/v1/participants?search=Luana")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_list_participants_recurrent_filter():
    client = TestClient(app)
    response = client.get("/api/v1/participants?recurrent_only=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for p in data:
        cnt = p.get("linked_relints_count", p.get("quantidade_relints", 0))
        assert cnt > 1

def test_get_participant_dossier_not_found():
    client = TestClient(app)
    response = client.get("/api/v1/participants/invalido_999999")
    assert response.status_code == 404


def test_documento_sintetico_nao_vaza_como_documento_real(tmp_path: Path):
    """ADR-0101: chave_pessoa foi eliminada, documento absorveu seu papel de chave única —
    quando não há RG/CPF real, documento vira o nome em minúsculo (chave sintética). O
    endpoint não pode expor isso como se fosse um documento de verdade."""
    repo = SqlitePersonRepo(tmp_path / "test_documento_sintetico.db")
    repo.save(Person(person_id="", name="Pessoa Sem Documento", aliases=[], documents=[]))

    app.dependency_overrides[get_person_repo] = lambda: repo
    try:
        client = TestClient(app)
        response = client.get("/api/v1/participants")
        assert response.status_code == 200
        data = response.json()
        alvo = next(p for p in data if p["name"] == "Pessoa Sem Documento")
        assert alvo["document"] == ""
    finally:
        app.dependency_overrides.clear()
