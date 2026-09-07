import pytest
from pathlib import Path
from backend.core.entities import IncidentReport, Person
from backend.database.sqlite_repo import SqliteRepo
from backend.database.sqlite_person_repo import SqlitePersonRepo


def test_sqlite_repo_crud(tmp_path: Path):
    db_file = tmp_path / "test_relints.db"
    repo = SqliteRepo(db_file)

    report = IncidentReport(
        source_file="relint_test_01.pdf",
        subject="PRISÃO POR ROUBO",
        summary="Ocorrência de roubo em Panambi",
        content="Conteúdo completo do histórico."
    )

    # 1. Save
    doc_id = repo.save(report)
    assert doc_id != ""

    # 2. Exists & Get
    assert repo.exists_by_source_file("relint_test_01.pdf") is True
    assert repo.exists_by_source_file("inexistente.pdf") is False

    fetched = repo.get_by_id(doc_id)
    assert fetched is not None
    assert fetched.subject == "PRISÃO POR ROUBO"
    assert fetched.source_file == "relint_test_01.pdf"

    by_file = repo.get_by_source_file("relint_test_01.pdf")
    assert by_file is not None
    assert by_file.summary == "Ocorrência de roubo em Panambi"

    # 3. Get All
    all_reports = repo.get_all()
    assert len(all_reports) == 1

    # 4. Upsert (Save same source_file with updated content)
    report_updated = IncidentReport(
        source_file="relint_test_01.pdf",
        subject="PRISÃO POR ROUBO ATUALIZADO",
        summary="Resumo atualizado",
        content="Novo conteúdo."
    )
    repo.save(report_updated)
    all_reports_after = repo.get_all()
    assert len(all_reports_after) == 1
    assert all_reports_after[0].subject == "PRISÃO POR ROUBO ATUALIZADO"

    # 5. Delete
    deleted = repo.delete_by_source_file("relint_test_01.pdf")
    assert deleted is True
    assert repo.exists_by_source_file("relint_test_01.pdf") is False
    assert len(repo.get_all()) == 0


def test_get_all_survives_homicide_report_without_registry_number(tmp_path: Path):
    """
    Regressão: `_build_report_from_row` tinha um fallback (linhas 555-558) que chamava
    `hom_row.get(...)` em um `sqlite3.Row` — que não tem método `.get()` — sempre que um
    RELINT classificado como Homicídio (linha em `homicidio_detalhes`) tivesse
    `numero_registro` vazio na tabela principal `relints`. Esse fallback ficou dormente
    enquanto o Pass 1 legado preenchia `registry_number`; depois da remoção do Pass 1
    (ADR-0096), o campo passou a vir sempre vazio, tornando o bug sempre acionado e
    derrubando silenciosamente todo RELINT de Homicídio de `get_all()` (o `except Exception:
    pass` ali engolia o AttributeError sem log nenhum).
    """
    db_file = tmp_path / "test_relints_homicide.db"
    repo = SqliteRepo(db_file)

    report = IncidentReport(
        source_file="relint_homicidio.pdf",
        subject="Homicídio em Seberi - RS",
        summary="Resumo do homicídio.",
        content="Conteúdo completo.",
        bm_group="Homicídio",
        registry_number=""
    )
    doc_id = repo.save(report)
    assert doc_id != ""

    # Antes do fix, esta chamada lançava AttributeError dentro de _build_report_from_row
    fetched = repo.get_by_id(doc_id)
    assert fetched is not None
    assert fetched.subject == "Homicídio em Seberi - RS"

    all_reports = repo.get_all()
    assert len(all_reports) == 1
    assert all_reports[0].subject == "Homicídio em Seberi - RS"


def test_sqlite_person_repo_crud(tmp_path: Path):
    db_file = tmp_path / "test_persons.db"
    person_repo = SqlitePersonRepo(db_file)

    # person_id vazio: o repositório deriva a chave a partir do documento (mesmo padrão
    # usado de verdade em EtlService.process_file(): person_id = p_doc if p_doc else p_name.lower()).
    # Desde a eliminação de chave_pessoa (ADR-0101), documento é a própria chave única —
    # não faz mais sentido um person_id explícito divergir do documento.
    person = Person(
        person_id="",
        name="Carlos da Silva",
        aliases=["Carlinhos"],
        documents=["123.456.789-00"],
        linked_relints=["relint_01.pdf"]
    )

    # Save
    pid = person_repo.save(person)
    assert pid == "12345678900"

    # Get by ID
    fetched = person_repo.get_by_id("12345678900")
    assert fetched is not None
    assert fetched.name == "Carlos da Silva"
    assert "Carlinhos" in fetched.aliases

    # Get by Document
    by_doc = person_repo.get_by_document("12345678900")
    assert by_doc is not None
    assert by_doc.person_id == "12345678900"

    # Update
    person.person_id = "12345678900"
    person.aliases.append("Novo Apelido")
    person_repo.update(person)
    updated = person_repo.get_by_id("12345678900")
    assert updated is not None
    assert "Novo Apelido" in updated.aliases

    # Get All
    assert len(person_repo.get_all()) == 1



