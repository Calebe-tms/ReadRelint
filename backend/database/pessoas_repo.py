# -*- coding: utf-8 -*-
"""
Repositório SQLModel do módulo Gerenciador de Pessoas — engine/sessão compartilhada
pelos endpoints de CRUD (ADR-0102). O motor de RELINT (SqliteRepo/SqlitePersonRepo)
não usa nada deste arquivo.
"""
from pathlib import Path
from sqlmodel import create_engine, Session


def get_pessoas_engine(db_path: Path):
    return create_engine(f"sqlite:///{db_path}")


def get_pessoas_session(db_path: Path) -> Session:
    return Session(get_pessoas_engine(db_path))
