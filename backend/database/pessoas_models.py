# -*- coding: utf-8 -*-
"""
Models SQLModel do módulo Gerenciador de Pessoas (schema ADR-0101, ORM ADR-0102).

`Pessoa` mapeia a tabela `pessoas` já existente (gerenciada por SqlitePersonRepo/SqliteRepo
via SQL puro) — este módulo só acrescenta a coluna `dados_aj` e não recria a tabela do zero
nem substitui o repositório existente do dossiê de participantes.

`documento` é a chave única (não existe mais `chave_pessoa` separada — eliminada por ser
redundante, já que guardava o mesmo RG em formato normalizado). Quando a pessoa não tem
RG/CPF real, `documento` guarda o nome em minúsculo como chave sintética (mesmo fallback que
`chave_pessoa` já fazia) — os consumidores (SqlitePersonRepo, participants.py) tratam esse
caso para não expor a chave sintética como se fosse um documento de verdade.
"""
from typing import Optional
from sqlmodel import SQLModel, Field


class Pessoa(SQLModel, table=True):
    __tablename__ = "pessoas"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    alcunha: Optional[str] = None
    documento: str = Field(unique=True)
    antecedentes: Optional[str] = None
    dados_aj: Optional[str] = None  # JSON livre, chave:valor (ver ADR-0101)


class PessoaFoto(SQLModel, table=True):
    __tablename__ = "pessoa_fotos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pessoa_id: int = Field(foreign_key="pessoas.id")
    caminho_arquivo: str
    ordem: Optional[int] = None


class Qrb(SQLModel, table=True):
    __tablename__ = "qrb"

    id: Optional[int] = Field(default=None, primary_key=True)
    chave_externa: str = Field(unique=True)
    nome_local: str
    municipio: Optional[str] = None
    endereco: Optional[str] = None
    coordenadas: Optional[str] = None
    tipo_local: Optional[str] = None
    foto: Optional[str] = None


class GrupoCriminoso(SQLModel, table=True):
    __tablename__ = "grupos_criminosos"

    id: Optional[int] = Field(default=None, primary_key=True)
    chave_externa: str = Field(unique=True)
    nome: str
    qrb_id: Optional[int] = Field(default=None, foreign_key="qrb.id")
    observacao: Optional[str] = None


class GrupoFamiliar(SQLModel, table=True):
    __tablename__ = "grupos_familiares"

    id: Optional[int] = Field(default=None, primary_key=True)
    chave_externa: str = Field(unique=True)
    nome: str
    qrb_id: Optional[int] = Field(default=None, foreign_key="qrb.id")
    observacao: Optional[str] = None


class Veiculo(SQLModel, table=True):
    __tablename__ = "veiculos"

    id: Optional[int] = Field(default=None, primary_key=True)
    placa: str = Field(unique=True)
    marca: Optional[str] = None
    cor: Optional[str] = None
    localizacao: Optional[str] = None
    proprietario: Optional[str] = None
    foto_path: Optional[str] = None
    observacao: Optional[str] = None


class PessoaGrupoCriminoso(SQLModel, table=True):
    __tablename__ = "pessoa_grupo_criminoso"

    id: Optional[int] = Field(default=None, primary_key=True)
    pessoa_id: int = Field(foreign_key="pessoas.id")
    grupo_criminoso_id: int = Field(foreign_key="grupos_criminosos.id")
    funcao: Optional[str] = None


class PessoaGrupoFamiliar(SQLModel, table=True):
    __tablename__ = "pessoa_grupo_familiar"

    id: Optional[int] = Field(default=None, primary_key=True)
    pessoa_id: int = Field(foreign_key="pessoas.id")
    grupo_familiar_id: int = Field(foreign_key="grupos_familiares.id")
    funcao: Optional[str] = None


class PessoaQrb(SQLModel, table=True):
    __tablename__ = "pessoa_qrb"

    id: Optional[int] = Field(default=None, primary_key=True)
    pessoa_id: int = Field(foreign_key="pessoas.id")
    qrb_id: int = Field(foreign_key="qrb.id")


class PessoaVeiculo(SQLModel, table=True):
    __tablename__ = "pessoa_veiculo"

    id: Optional[int] = Field(default=None, primary_key=True)
    pessoa_id: int = Field(foreign_key="pessoas.id")
    veiculo_id: int = Field(foreign_key="veiculos.id")
    data_posse: Optional[str] = None
