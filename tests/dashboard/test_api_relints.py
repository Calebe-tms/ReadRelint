"""
Unit tests for RELINTs FastAPI endpoints using TestClient with Portuguese schemas.
"""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.core.entities import IncidentReport, Participant, BmGroup, RelintType
from backend.database.sqlite_repo import SqliteRepo
from backend.api.app import app
from backend.api.dependencies import get_db_repo

@pytest.fixture
def mock_db_repo(tmp_path: Path):
    db_file = tmp_path / "test_api_relints.db"
    repo = SqliteRepo(db_file)
    
    # Insert sample test report
    report = IncidentReport(
        source_file="RELINT_001_TEST.pdf",
        subject="Homicídio qualificado em via pública",
        main_fact="Indivíduo alvejado por disparos de arma de fogo",
        date_of_fact="2026-08-10",
        time_of_fact="22:30",
        bm_group=BmGroup.OUTROS,
        relint_type=RelintType.OCORRENCIA,
        municipality="Porto Alegre",
        summary="Ataque a tiros resultante em um óbito.",
        content="CONTEÚDO INTEGRAL DO RELINT TESTE 001",
        participants=[
            Participant(name="João da Silva", nickname="Gordo", document="1234567890")
        ]
    )
    repo.save(report)
    return repo

@pytest.fixture
def client(mock_db_repo):
    # Override FastAPI dependency to use temporary test SQLite DB
    app.dependency_overrides[get_db_repo] = lambda: mock_db_repo
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_list_relints(client):
    response = client.get("/api/v1/relints")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["arquivo_origem"] == "RELINT_001_TEST.pdf"
    assert data[0]["assunto"] == "Homicídio qualificado em via pública"
    assert data[0]["total_participantes"] == 1

def test_get_relint_by_id(client):
    # First get the list to grab ID
    list_res = client.get("/api/v1/relints")
    relint_id = list_res.json()[0]["id"]

    detail_res = client.get(f"/api/v1/relints/{relint_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["arquivo_origem"] == "RELINT_001_TEST.pdf"
    assert detail["conteudo"] == "CONTEÚDO INTEGRAL DO RELINT TESTE 001"
    assert len(detail["participantes"]) == 1
    assert detail["participantes"][0]["nome"] == "João da Silva"


def test_update_relint_general_fields(client):
    list_res = client.get("/api/v1/relints")
    relint_id = list_res.json()[0]["id"]

    update_payload = {
        "assunto": "Assunto Editado Manualmente",
        "resumo": "Síntese atualizada pelo usuário",
        "municipio": "Novo Hamburgo",
        "editado_usuario": True,
        "participantes": [
            {
                "nome": "João da Silva",
                "alcunha": "Gordinho",
                "documento": "1234567890",
                "tipo_participacao": "Acusado"
            },
            {
                "nome": "Maria de Oliveira",
                "alcunha": "Mariazinha",
                "documento": "0987654321",
                "tipo_participacao": "Vítima"
            }
        ]
    }

    put_res = client.put(f"/api/v1/relints/{relint_id}", json=update_payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()
    assert updated_data["assunto"] == "Assunto Editado Manualmente"
    assert updated_data["resumo"] == "Síntese atualizada pelo usuário"
    assert updated_data["municipio"] == "Novo Hamburgo"
    assert updated_data["editado_usuario"] is True
    assert len(updated_data["participantes"]) == 2


def test_update_relint_homicide_fields(client):
    list_res = client.get("/api/v1/relints")
    relint_id = list_res.json()[0]["id"]

    update_payload = {
        "grupo_bm": "Homicídio",
        "homicidio_detalhes": {
            "numero_registro": "516/151641/2026",
            "orgao_registro": "1ª DP",
            "ano_registro": "2026",
            "tipo_fato": "Consumado",
            "motivacao": "Envolvimento com o Tráfico"
        }
    }

    put_res = client.put(f"/api/v1/relints/{relint_id}", json=update_payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()
    assert updated_data["grupo_bm"] == "Homicídio"
    assert updated_data["editado_usuario"] is True


def test_update_relint_not_found(client):
    put_res = client.put("/api/v1/relints/999999", json={"assunto": "Inexistente"})
    assert put_res.status_code == 404


def test_all_processed_relints_appear_in_dashboard_listing(tmp_path: Path):
    """
    Regressão ampla: simula uma pasta com um RELINT de cada especialidade (BmGroup) já
    processado e garante que TODOS aparecem na listagem do dashboard, tanto na camada de
    repositório (SqliteRepo.get_all()) quanto na camada de API (GET /api/v1/relints).

    Motivação: um RELINT já lido/salvo com sucesso pode ainda assim sumir do dashboard se
    algo na leitura de volta (_build_report_from_row) lançar exceção que get_all() engole
    silenciosamente (`except Exception: pass`) — foi exatamente assim que os RELINTs de
    Homicídio desapareceram (AttributeError de `hom_row.get()` em um sqlite3.Row, corrigido
    em backend/database/sqlite_repo.py). Este teste itera por todas as especialidades para
    detectar qualquer regressão equivalente em qualquer uma delas, não só em Homicídio.
    """
    db_file = tmp_path / "test_all_specialties_listing.db"
    repo = SqliteRepo(db_file)

    expected_source_files = []
    for bm_group in BmGroup:
        source_file = f"RELINT_{bm_group.name}.pdf"
        expected_source_files.append(source_file)
        report = IncidentReport(
            source_file=source_file,
            subject=f"Ocorrência de teste - {bm_group.value}",
            summary=f"Resumo de teste para {bm_group.value}.",
            content="Conteúdo integral de teste.",
            bm_group=bm_group.value,
        )
        repo.save(report)

    # 1. Camada de repositório: nenhum RELINT processado pode sumir de get_all()
    all_reports = repo.get_all()
    assert len(all_reports) == len(expected_source_files)
    assert {r.source_file for r in all_reports} == set(expected_source_files)

    # 2. Camada de API: o dashboard consome este endpoint, não o repositório diretamente
    app.dependency_overrides[get_db_repo] = lambda: repo
    try:
        api_client = TestClient(app)
        response = api_client.get("/api/v1/relints")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(expected_source_files)
        assert {r["arquivo_origem"] for r in data} == set(expected_source_files)
    finally:
        app.dependency_overrides.clear()
