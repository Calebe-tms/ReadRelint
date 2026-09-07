# -*- coding: utf-8 -*-
"""
Testes dos models SQLModel do Gerenciador de Pessoas (ADR-0101/ADR-0102).
Cada teste usa um banco SQLite em arquivo temporário com o schema criado via
SQLModel.metadata.create_all() — não depende do arquivo real nem do Alembic.
"""
import json

import pytest
from sqlmodel import SQLModel, Session, create_engine, select

from backend.database.pessoas_models import (
    Pessoa, PessoaFoto, Qrb, GrupoCriminoso, GrupoFamiliar, Veiculo,
    PessoaGrupoCriminoso, PessoaGrupoFamiliar, PessoaQrb, PessoaVeiculo,
)


@pytest.fixture
def session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test_pessoas.db'}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_pessoa_com_dados_aj_livre(session):
    pessoa = Pessoa(
        nome="Fulano de Tal",
        documento="12345678900",
        dados_aj=json.dumps({"Situação": "Preso", "Presidio": "Complexo Central"}, ensure_ascii=False),
    )
    session.add(pessoa)
    session.commit()

    lida = session.exec(select(Pessoa).where(Pessoa.documento == "12345678900")).one()
    assert lida.nome == "Fulano de Tal"
    dados = json.loads(lida.dados_aj)
    assert dados["Situação"] == "Preso"
    assert dados["Presidio"] == "Complexo Central"


def test_pessoa_sem_chave_pessoa_separada(session):
    """ADR-0101: chave_pessoa foi eliminada — documento absorve o papel de chave única
    (valor real de RG/CPF, ou nome em minúsculo como fallback quando não há documento)."""
    assert not hasattr(Pessoa, "chave_pessoa")

    pessoa = Pessoa(nome="Fulano Sem Documento", documento="fulano sem documento")
    session.add(pessoa)
    session.commit()

    lida = session.exec(select(Pessoa).where(Pessoa.documento == "fulano sem documento")).one()
    assert lida.nome == "Fulano Sem Documento"


def test_pessoa_dados_aj_aceita_chave_arbitraria(session):
    """Formulário livre: o usuário pode gravar qualquer chave nova em dados_aj sem migração."""
    pessoa = Pessoa(documento="1", nome="Fulano", dados_aj=json.dumps({"Chave Inventada Pelo Usuário": "valor"}))
    session.add(pessoa)
    session.commit()

    lida = session.exec(select(Pessoa)).one()
    assert json.loads(lida.dados_aj) == {"Chave Inventada Pelo Usuário": "valor"}


def test_pessoa_fotos_1_para_n(session):
    pessoa = Pessoa(documento="1", nome="Fulano")
    session.add(pessoa)
    session.commit()
    session.refresh(pessoa)

    session.add(PessoaFoto(pessoa_id=pessoa.id, caminho_arquivo="pessoas_Images/a.jpg", ordem=1))
    session.add(PessoaFoto(pessoa_id=pessoa.id, caminho_arquivo="pessoas_Images/b.jpg", ordem=2))
    session.commit()

    fotos = session.exec(select(PessoaFoto).where(PessoaFoto.pessoa_id == pessoa.id)).all()
    assert len(fotos) == 2
    assert {f.caminho_arquivo for f in fotos} == {"pessoas_Images/a.jpg", "pessoas_Images/b.jpg"}


def test_qrb_com_tipo_local_e_foto(session):
    qrb = Qrb(chave_externa="hash1", nome_local="Casa X", tipo_local="Moradia", foto="QRB_Images/x.png")
    session.add(qrb)
    session.commit()

    lido = session.exec(select(Qrb).where(Qrb.chave_externa == "hash1")).one()
    assert lido.tipo_local == "Moradia"
    assert lido.foto == "QRB_Images/x.png"


def test_grupo_criminoso_referencia_qrb(session):
    qrb = Qrb(chave_externa="hash-qrb", nome_local="Boca")
    session.add(qrb)
    session.commit()
    session.refresh(qrb)

    grupo = GrupoCriminoso(chave_externa="hash-grupo", nome="Grupo X", qrb_id=qrb.id)
    session.add(grupo)
    session.commit()

    lido = session.exec(select(GrupoCriminoso).where(GrupoCriminoso.chave_externa == "hash-grupo")).one()
    assert lido.qrb_id == qrb.id


def test_pessoa_grupo_criminoso_tem_funcao_livre(session):
    pessoa = Pessoa(documento="1", nome="Fulano")
    grupo = GrupoCriminoso(chave_externa="g1", nome="Grupo X")
    session.add(pessoa)
    session.add(grupo)
    session.commit()
    session.refresh(pessoa)
    session.refresh(grupo)

    vinculo = PessoaGrupoCriminoso(pessoa_id=pessoa.id, grupo_criminoso_id=grupo.id, funcao="Chefe")
    session.add(vinculo)
    session.commit()

    lido = session.exec(select(PessoaGrupoCriminoso)).one()
    assert lido.funcao == "Chefe"


def test_pessoa_grupo_familiar_padronizada_com_funcao_mas_pode_ser_nula(session):
    """ADR-0101: funcao padronizada nas duas tabelas de vínculo, mas a familiar não tem
    esse dado na planilha de origem — fica NULL."""
    pessoa = Pessoa(documento="1", nome="Fulano")
    grupo = GrupoFamiliar(chave_externa="gf1", nome="Familia X")
    session.add(pessoa)
    session.add(grupo)
    session.commit()
    session.refresh(pessoa)
    session.refresh(grupo)

    vinculo = PessoaGrupoFamiliar(pessoa_id=pessoa.id, grupo_familiar_id=grupo.id)
    session.add(vinculo)
    session.commit()

    lido = session.exec(select(PessoaGrupoFamiliar)).one()
    assert lido.funcao is None


def test_pessoa_veiculo_sem_campo_tipo_posse(session):
    """ADR-0101: pessoa_veiculo não tem 'tipo_posse' — a planilha só tem pessoa+veiculo+data."""
    assert not hasattr(PessoaVeiculo, "tipo_posse")

    pessoa = Pessoa(documento="1", nome="Fulano")
    veiculo = Veiculo(placa="ABC1234")
    session.add(pessoa)
    session.add(veiculo)
    session.commit()
    session.refresh(pessoa)
    session.refresh(veiculo)

    vinculo = PessoaVeiculo(pessoa_id=pessoa.id, veiculo_id=veiculo.id, data_posse="19/09/2023")
    session.add(vinculo)
    session.commit()

    lido = session.exec(select(PessoaVeiculo)).one()
    assert lido.data_posse == "19/09/2023"


def test_pessoa_qrb_vinculo_simples(session):
    pessoa = Pessoa(documento="1", nome="Fulano")
    qrb = Qrb(chave_externa="q1", nome_local="Local X")
    session.add(pessoa)
    session.add(qrb)
    session.commit()
    session.refresh(pessoa)
    session.refresh(qrb)

    session.add(PessoaQrb(pessoa_id=pessoa.id, qrb_id=qrb.id))
    session.commit()

    lido = session.exec(select(PessoaQrb)).one()
    assert lido.pessoa_id == pessoa.id
    assert lido.qrb_id == qrb.id
