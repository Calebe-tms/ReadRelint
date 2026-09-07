# -*- coding: utf-8 -*-
"""
Testa a migration real do Alembic (não só os models SQLModel) — roda `alembic upgrade head`
contra um arquivo SQLite temporário e confere que o schema resultante bate com o esperado.
Cobre o cenário real do projeto: banco apagado -> alembic upgrade head -> estrutura completa
do módulo Gerenciador de Pessoas (ver docs/proposals/gerenciador-pessoas-app-aj.md).
"""
import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

TABELAS_ESPERADAS = {
    "pessoas", "pessoa_fotos", "qrb", "grupos_criminosos", "grupos_familiares",
    "veiculos", "pessoa_qrb", "pessoa_veiculo", "pessoa_grupo_criminoso", "pessoa_grupo_familiar",
}


def _alembic_upgrade_head(db_path: Path) -> None:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "head")


def test_alembic_upgrade_head_cria_todas_as_tabelas_do_modulo(tmp_path):
    db_path = tmp_path / "schema_test.db"

    _alembic_upgrade_head(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = {row[0] for row in cursor.fetchall()}
    finally:
        conn.close()

    faltando = TABELAS_ESPERADAS - tabelas
    assert not faltando, f"Tabelas não criadas pela migration: {faltando}"


def test_pessoas_tem_coluna_dados_aj(tmp_path):
    db_path = tmp_path / "schema_test.db"
    _alembic_upgrade_head(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(pessoas);")
        colunas = {row[1] for row in cursor.fetchall()}
    finally:
        conn.close()

    assert "dados_aj" in colunas


def test_pessoas_sem_chave_pessoa_documento_e_unico(tmp_path):
    """ADR-0101: chave_pessoa eliminada — documento absorve o papel de chave única."""
    db_path = tmp_path / "schema_test.db"
    _alembic_upgrade_head(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(pessoas);")
        info = {row[1]: row for row in cursor.fetchall()}
    finally:
        conn.close()

    assert "chave_pessoa" not in info
    documento_col = info["documento"]
    notnull = documento_col[3]
    assert notnull == 1

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("INSERT INTO pessoas (nome, documento) VALUES ('A', 'RG1');")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO pessoas (nome, documento) VALUES ('B', 'RG1');")
    finally:
        conn.close()


def test_qrb_tem_tipo_local_e_foto(tmp_path):
    db_path = tmp_path / "schema_test.db"
    _alembic_upgrade_head(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(qrb);")
        colunas = {row[1] for row in cursor.fetchall()}
    finally:
        conn.close()

    assert {"tipo_local", "foto"} <= colunas


def test_pessoa_veiculo_nao_tem_tipo_posse(tmp_path):
    """ADR-0101: coluna 'Posse' na planilha é o RG (chave de vínculo), não um campo descritivo."""
    db_path = tmp_path / "schema_test.db"
    _alembic_upgrade_head(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(pessoa_veiculo);")
        colunas = {row[1] for row in cursor.fetchall()}
    finally:
        conn.close()

    assert "tipo_posse" not in colunas
    assert {"pessoa_id", "veiculo_id", "data_posse"} <= colunas


def test_pessoa_grupo_criminoso_e_familiar_padronizadas_com_funcao(tmp_path):
    db_path = tmp_path / "schema_test.db"
    _alembic_upgrade_head(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(pessoa_grupo_criminoso);")
        colunas_crim = {row[1] for row in cursor.fetchall()}
        cursor.execute("PRAGMA table_info(pessoa_grupo_familiar);")
        colunas_fam = {row[1] for row in cursor.fetchall()}
    finally:
        conn.close()

    assert "funcao" in colunas_crim
    assert "funcao" in colunas_fam


def test_alembic_upgrade_coexiste_com_bootstrap_legado_do_motor_relint(tmp_path):
    """O motor de RELINT (SqliteRepo/SqlitePersonRepo) continua criando seu próprio schema
    via SQL puro (ADR-0102) — rodar os dois lados no mesmo arquivo não pode conflitar."""
    from backend.database.sqlite_repo import SqliteRepo
    from backend.database.sqlite_person_repo import SqlitePersonRepo

    db_path = tmp_path / "schema_test.db"
    _alembic_upgrade_head(db_path)

    # Não deve lançar exceção mesmo com 'pessoas'/'relints' já parcialmente geridos pelo Alembic.
    SqliteRepo(db_path)
    SqlitePersonRepo(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = {row[0] for row in cursor.fetchall()}
    finally:
        conn.close()

    assert "relints" in tabelas
    assert "relint_participantes" in tabelas
    assert TABELAS_ESPERADAS <= tabelas
