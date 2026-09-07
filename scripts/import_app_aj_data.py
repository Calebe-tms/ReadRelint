# -*- coding: utf-8 -*-
"""
Migração de dados ÚNICA: importa o conteúdo da planilha App-AJ (exportado como CSV em
data/app_aj_import/, ver ADR-0101) para o schema do módulo Gerenciador de Pessoas.

Roda uma vez só, contra um banco já com o schema aplicado (alembic upgrade head).
Não é um importador recorrente — a planilha deixa de ser a fonte da verdade depois disto
(confirmado com o usuário).
"""
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select
from backend.database.pessoas_models import (
    Pessoa, PessoaFoto, Qrb, GrupoCriminoso, GrupoFamiliar, Veiculo,
    PessoaGrupoCriminoso, PessoaGrupoFamiliar, PessoaQrb, PessoaVeiculo,
)
from backend.database.pessoas_repo import get_pessoas_engine

IMPORT_DIR = Path(__file__).resolve().parent.parent / "data" / "app_aj_import"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "relints.db"

# Prefixo de pasta de fotos de pessoas na planilha -> pasta real confirmada pelo usuário
FOTO_PESSOA_PREFIXO_ANTIGO = "Dados Criminosos_Images/"
FOTO_PESSOA_PREFIXO_NOVO = "pessoas_Images/"

DADOS_AJ_CAMPOS = [
    "Situação", "Presidio", "Crimes", "Cela", "Município", "Endereço",
    "Outras Informações", "Link (facebook ou instagram)",
    "Companheiro(a)", "RG Companheiro(a)", "Rede Social Companheiro(a)",
    "Sinais particulares", "Tatuagens",
]


def _clean_doc(raw: str) -> str:
    return re.sub(r"[.\-\s]", "", raw or "")


def _ler_csv(nome: str):
    path = IMPORT_DIR / f"{nome}.csv"
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _rewrite_foto_pessoa(caminho: str) -> str:
    if caminho.startswith(FOTO_PESSOA_PREFIXO_ANTIGO):
        return FOTO_PESSOA_PREFIXO_NOVO + caminho[len(FOTO_PESSOA_PREFIXO_ANTIGO):]
    return caminho


def importar_criminosos(session: Session) -> Dict[str, int]:
    """Retorna mapa RG (limpo) -> pessoas.id, para os passos seguintes resolverem vínculos."""
    rg_para_pessoa_id: Dict[str, int] = {}
    chaves_vistas = set()
    duplicadas = 0
    for row in _ler_csv("criminosos"):
        nome = (row.get("Nome Completo") or "").strip()
        rg_raw = (row.get("RG") or "").strip()
        if not nome and not rg_raw:
            continue
        rg = _clean_doc(rg_raw)
        chave = rg if rg else nome.lower()

        if chave in chaves_vistas:
            # RG duplicado na planilha (mesma pessoa cadastrada 2x) — mantém a 1a ocorrência,
            # não descarta o vínculo (o RG já mapeia pra pessoa.id certo pros passos seguintes).
            duplicadas += 1
            continue
        chaves_vistas.add(chave)

        dados_aj = {k: (row.get(k) or "").strip() for k in DADOS_AJ_CAMPOS if (row.get(k) or "").strip()}

        pessoa = Pessoa(
            nome=nome,
            alcunha=(row.get("Alcunha") or "").strip() or None,
            documento=chave,
            dados_aj=json.dumps(dados_aj, ensure_ascii=False) if dados_aj else None,
        )
        session.add(pessoa)
        session.flush()  # garante pessoa.id sem fechar a transação

        for campo, ordem in (("Foto", 1), ("Foto_2", 2), ("Foto_3", 3)):
            caminho = (row.get(campo) or "").strip()
            if caminho:
                session.add(PessoaFoto(
                    pessoa_id=pessoa.id,
                    caminho_arquivo=_rewrite_foto_pessoa(caminho),
                    ordem=ordem,
                ))

        if rg:
            rg_para_pessoa_id[rg] = pessoa.id
    session.commit()
    if duplicadas:
        print(f"Aviso: {duplicadas} linha(s) de CRIMINOSOS com RG/nome duplicado, ignoradas.")
    return rg_para_pessoa_id


def _resolver_ou_criar_pessoa(session: Session, rg_para_pessoa_id: Dict[str, int], rg_raw: str) -> Optional[int]:
    rg = _clean_doc(rg_raw)
    if not rg:
        return None
    if rg in rg_para_pessoa_id:
        return rg_para_pessoa_id[rg]
    # RG citado num vínculo mas sem linha própria em CRIMINOSOS — cria stub em vez de descartar
    # o vínculo (ADR-0008: repositório universal, sem descartes).
    pessoa = Pessoa(nome=f"(RG {rg_raw} — sem cadastro em CRIMINOSOS)", documento=rg)
    session.add(pessoa)
    session.flush()
    rg_para_pessoa_id[rg] = pessoa.id
    return pessoa.id


def importar_qrb(session: Session) -> Dict[str, int]:
    externa_para_id: Dict[str, int] = {}
    for row in _ler_csv("qrb"):
        chave_externa = (row.get("ID") or "").strip()
        nome_local = (row.get("Nome do Local") or "").strip()
        if not chave_externa or not nome_local or chave_externa in externa_para_id:
            continue
        qrb = Qrb(
            chave_externa=chave_externa,
            nome_local=nome_local,
            municipio=(row.get("Município") or "").strip() or None,
            endereco=(row.get("Endereço") or "").strip() or None,
            coordenadas=(row.get("Coordenadas") or "").strip() or None,
            tipo_local=(row.get("Tipo de Local") or "").strip() or None,
            foto=(row.get("Foto") or "").strip() or None,
        )
        session.add(qrb)
        session.flush()
        externa_para_id[chave_externa] = qrb.id
    session.commit()
    return externa_para_id


def importar_grupos_criminosos(session: Session, qrb_externa_para_id: Dict[str, int]) -> Dict[str, int]:
    externa_para_id: Dict[str, int] = {}
    for row in _ler_csv("grupos_criminosos"):
        chave_externa = (row.get("ID") or "").strip()
        nome = (row.get("Nome") or "").strip()
        if not chave_externa or not nome or chave_externa in externa_para_id:
            continue
        qrb_ref = (row.get("QRB") or "").strip()
        grupo = GrupoCriminoso(
            chave_externa=chave_externa,
            nome=nome,
            qrb_id=qrb_externa_para_id.get(qrb_ref),
            observacao=(row.get("Observação") or "").strip() or None,
        )
        session.add(grupo)
        session.flush()
        externa_para_id[chave_externa] = grupo.id
    session.commit()
    return externa_para_id


def importar_grupos_familiares(session: Session, qrb_externa_para_id: Dict[str, int]) -> Dict[str, int]:
    externa_para_id: Dict[str, int] = {}
    for row in _ler_csv("grupos_familiares"):
        chave_externa = (row.get("ID") or "").strip()
        nome = (row.get("Nome") or "").strip()
        if not chave_externa or not nome or chave_externa in externa_para_id:
            continue
        qrb_ref = (row.get("QRB") or "").strip()
        grupo = GrupoFamiliar(
            chave_externa=chave_externa,
            nome=nome,
            qrb_id=qrb_externa_para_id.get(qrb_ref),
            observacao=(row.get("Obs") or "").strip() or None,
        )
        session.add(grupo)
        session.flush()
        externa_para_id[chave_externa] = grupo.id
    session.commit()
    return externa_para_id


def importar_veiculos(session: Session) -> Dict[str, int]:
    placa_para_id: Dict[str, int] = {}
    for row in _ler_csv("veiculos"):
        placa = (row.get("Placa") or "").strip()
        if not placa or placa in placa_para_id:
            continue  # placas duplicadas na planilha são ignoradas na 2a ocorrência
        veiculo = Veiculo(
            placa=placa,
            marca=(row.get("Veiculo Marca") or "").strip() or None,
            cor=(row.get("Cor") or "").strip() or None,
            localizacao=(row.get("Localização") or "").strip() or None,
            proprietario=(row.get("Proprietário") or "").strip() or None,
            foto_path=(row.get("Foto") or "").strip() or None,
            observacao=(row.get("Obs") or "").strip() or None,
        )
        session.add(veiculo)
        session.flush()
        placa_para_id[placa] = veiculo.id
    session.commit()
    return placa_para_id


def importar_pivots(session: Session, rg_para_pessoa_id, qrb_externa_para_id, grupo_crim_para_id, grupo_fam_para_id, placa_para_id):
    for row in _ler_csv("r_qrb"):
        pessoa_id = _resolver_ou_criar_pessoa(session, rg_para_pessoa_id, (row.get("Criminoso") or "").strip())
        qrb_id = qrb_externa_para_id.get((row.get("QRB") or "").strip())
        if pessoa_id and qrb_id:
            session.add(PessoaQrb(pessoa_id=pessoa_id, qrb_id=qrb_id))

    for row in _ler_csv("r_grupo_familiar"):
        pessoa_id = _resolver_ou_criar_pessoa(session, rg_para_pessoa_id, (row.get("CRIMINOSO") or "").strip())
        grupo_id = grupo_fam_para_id.get((row.get("GRUPO FAMILIAR") or "").strip())
        if pessoa_id and grupo_id:
            session.add(PessoaGrupoFamiliar(pessoa_id=pessoa_id, grupo_familiar_id=grupo_id))

    for row in _ler_csv("r_grupo_criminoso"):
        pessoa_id = _resolver_ou_criar_pessoa(session, rg_para_pessoa_id, (row.get("Criminoso") or "").strip())
        grupo_id = grupo_crim_para_id.get((row.get("Grupo Criminoso") or "").strip())
        if pessoa_id and grupo_id:
            session.add(PessoaGrupoCriminoso(
                pessoa_id=pessoa_id,
                grupo_criminoso_id=grupo_id,
                funcao=(row.get("Função") or "").strip() or None,
            ))

    for row in _ler_csv("veiculos_posse"):
        pessoa_id = _resolver_ou_criar_pessoa(session, rg_para_pessoa_id, (row.get("Posse") or "").strip())
        veiculo_id = placa_para_id.get((row.get("Veículo") or "").strip())
        if pessoa_id and veiculo_id:
            session.add(PessoaVeiculo(
                pessoa_id=pessoa_id,
                veiculo_id=veiculo_id,
                data_posse=(row.get("Data") or "").strip() or None,
            ))

    session.commit()


def main():
    engine = get_pessoas_engine(DB_PATH)
    with Session(engine) as session:
        ja_importado = session.exec(select(Pessoa)).first()
        if ja_importado:
            print("Já existem pessoas no banco — importação já rodou antes, abortando (migração é única).")
            return

        rg_para_pessoa_id = importar_criminosos(session)
        print(f"Pessoas importadas: {len(rg_para_pessoa_id)}")

        qrb_externa_para_id = importar_qrb(session)
        print(f"QRBs importados: {len(qrb_externa_para_id)}")

        grupo_crim_para_id = importar_grupos_criminosos(session, qrb_externa_para_id)
        print(f"Grupos criminosos importados: {len(grupo_crim_para_id)}")

        grupo_fam_para_id = importar_grupos_familiares(session, qrb_externa_para_id)
        print(f"Grupos familiares importados: {len(grupo_fam_para_id)}")

        placa_para_id = importar_veiculos(session)
        print(f"Veículos importados: {len(placa_para_id)}")

        importar_pivots(session, rg_para_pessoa_id, qrb_externa_para_id, grupo_crim_para_id, grupo_fam_para_id, placa_para_id)
        print("Vínculos (pessoa_qrb, pessoa_grupo_familiar, pessoa_grupo_criminoso, pessoa_veiculo) importados.")


if __name__ == "__main__":
    main()
