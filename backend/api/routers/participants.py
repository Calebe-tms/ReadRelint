"""
FastAPI Router para Gerenciamento de Participantes e Dossiês Consolidados de Envolvidos.
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, computed_field

from backend.api.dependencies import get_person_repo
from backend.database.person_repo import IPersonRepo

router = APIRouter(prefix="/participants", tags=["participants"])

# pessoa_fotos.caminho_arquivo guarda caminhos com prefixos de pasta legados e
# inconsistentes entre si (ex: "pessoas_Images/", "CRIMINOSOS_Images/") — só a pasta
# "pessoas_Images" existe de fato em disco. Resolvemos pelo nome do arquivo e conferimos
# a existência real para não devolver URLs de fotos que nunca foram importadas.
PESSOAS_IMAGES_DIR = Path(__file__).resolve().parents[3] / "data" / "pessoas_Images"


def _fetch_pessoa_photos(cursor, pessoa_id: int) -> List[str]:
    """Busca a galeria de fotos de uma pessoa (módulo Gerenciador de Pessoas) que existem em disco, em ordem.

    A tabela `pessoa_fotos` é criada pela migração Alembic do módulo Gerenciador de Pessoas
    (ADR-0102), não pelo schema base de `SqlitePersonRepo` — pode não existir ainda em bancos
    novos/de teste que não passaram por essa migração.
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'pessoa_fotos';")
    if not cursor.fetchone():
        return []

    cursor.execute("""
        SELECT caminho_arquivo
        FROM pessoa_fotos
        WHERE pessoa_id = ?
        ORDER BY ordem, id;
    """, (pessoa_id,))
    photos = []
    for row in cursor.fetchall():
        raw = row["caminho_arquivo"]
        if not raw:
            continue
        filename = str(raw).replace("\\", "/").rsplit("/", 1)[-1]
        if (PESSOAS_IMAGES_DIR / filename).is_file():
            photos.append(f"/pessoas_images/{filename}")
    return photos


class LinkedRelintSummary(BaseModel):
    relint_id: int
    source_file: str
    subject: str
    date_of_fact: str
    participation_type: str
    municipality: str


class PersonDossierDTO(BaseModel):
    person_id: str
    name: str
    nickname: str
    document: str
    background: str
    photo_path: str
    photos: List[str]
    linked_relints_count: int
    linked_relints: List[LinkedRelintSummary]

    @computed_field
    @property
    def nome(self) -> str:
        return self.name

    @computed_field
    @property
    def alcunha(self) -> str:
        return self.nickname

    @computed_field
    @property
    def documento(self) -> str:
        return self.document

    @computed_field
    @property
    def antecedentes(self) -> str:
        return self.background

    @computed_field
    @property
    def caminho_foto(self) -> str:
        return self.photo_path

    @computed_field
    @property
    def galeria_fotos(self) -> List[str]:
        return self.photos

    @computed_field
    @property
    def quantidade_relints(self) -> int:
        return self.linked_relints_count


@router.get("", response_model=List[PersonDossierDTO])
def list_participants(
    search: Optional[str] = Query(None, description="Busca por nome, alcunha ou RG/CPF"),
    recurrent_only: bool = Query(False, description="Filtrar apenas reincidentes (> 1 RELINT)"),
    person_repo: IPersonRepo = Depends(get_person_repo)
) -> List[PersonDossierDTO]:
    """
    Retorna a lista consolidada de todos os participantes com contagem de ocorrências,
    foto principal e galeria de fotos vinculadas.
    """
    with person_repo._get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT
                p.id,
                p.nome,
                p.alcunha,
                p.documento,
                p.antecedentes,
                COUNT(DISTINCT rp.relint_id) AS relint_count
            FROM pessoas p
            LEFT JOIN relint_participantes rp ON p.id = rp.pessoa_id
            GROUP BY p.id
        """
        cursor.execute(query)
        p_rows = cursor.fetchall()

        results = []
        search_lower = search.lower().strip() if search else ""

        for p in p_rows:
            p_id = p["id"]
            p_key = p["documento"]
            name = p["nome"] or ""
            nick = p["alcunha"] or ""
            # documento pode guardar a chave sintética (nome em minúsculo) quando não há RG/CPF
            # real (ADR-0101) — nesse caso não deve aparecer como documento pro usuário.
            doc = p["documento"] or ""
            if doc and doc.lower() == name.strip().lower():
                doc = ""
            bg = p["antecedentes"] or ""
            relint_cnt = p["relint_count"] or 0

            if recurrent_only and relint_cnt <= 1:
                continue

            if search_lower:
                match_name = search_lower in name.lower()
                match_nick = search_lower in nick.lower()
                clean_doc = doc.lower().replace(".", "").replace("-", "")
                clean_search = search_lower.replace(".", "").replace("-", "")
                match_doc = clean_search in clean_doc if clean_doc else False
                if not (match_name or match_nick or match_doc):
                    continue

            cursor.execute("""
                SELECT 
                    r.id AS relint_id,
                    r.arquivo_origem,
                    r.assunto,
                    r.data_fato,
                    r.municipio,
                    rp.tipo_participacao,
                    rp.caminho_foto
                FROM relint_participantes rp
                JOIN relints r ON rp.relint_id = r.id
                WHERE rp.pessoa_id = ?
                ORDER BY r.id DESC;
            """, (p_id,))
            rel_rows = cursor.fetchall()

            linked_relints = []
            photos = _fetch_pessoa_photos(cursor, p_id)

            for r in rel_rows:
                f_path = r["caminho_foto"] or ""
                if f_path and f_path not in photos:
                    photos.append(f_path)

                linked_relints.append(LinkedRelintSummary(
                    relint_id=r["relint_id"],
                    source_file=r["arquivo_origem"] or "",
                    subject=r["assunto"] or "Sem assunto",
                    date_of_fact=r["data_fato"] or "",
                    participation_type=r["tipo_participacao"] or "Acusado",
                    municipality=r["municipio"] or ""
                ))

            results.append(PersonDossierDTO(
                person_id=p_key,
                name=name,
                nickname=nick,
                document=doc,
                background=bg,
                photo_path=photos[0] if photos else "",
                photos=photos,
                linked_relints_count=len(linked_relints),
                linked_relints=linked_relints
            ))

        results.sort(key=lambda x: x.linked_relints_count, reverse=True)
        return results


@router.get("/{person_id}", response_model=PersonDossierDTO)
def get_participant_dossier(
    person_id: str,
    person_repo: IPersonRepo = Depends(get_person_repo)
) -> PersonDossierDTO:
    """
    Retorna o dossiê detalhado de um participante específico.
    """
    with person_repo._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pessoas WHERE documento = ? OR id = ? LIMIT 1;", (person_id, person_id))
        p = cursor.fetchone()
        if not p:
            raise HTTPException(status_code=404, detail="Participante não encontrado.")

        p_id = p["id"]
        p_key = p["documento"]
        name = p["nome"] or ""
        nick = p["alcunha"] or ""
        # documento pode guardar a chave sintética (nome em minúsculo) quando não há RG/CPF
        # real (ADR-0101) — nesse caso não deve aparecer como documento pro usuário.
        doc = p["documento"] or ""
        if doc and doc.lower() == name.strip().lower():
            doc = ""
        bg = p["antecedentes"] or ""

        cursor.execute("""
            SELECT
                r.id AS relint_id,
                r.arquivo_origem,
                r.assunto,
                r.data_fato,
                r.municipio,
                rp.tipo_participacao,
                rp.caminho_foto
            FROM relint_participantes rp
            JOIN relints r ON rp.relint_id = r.id
            WHERE rp.pessoa_id = ?
            ORDER BY r.id DESC;
        """, (p_id,))
        rel_rows = cursor.fetchall()

        linked_relints = []
        photos = _fetch_pessoa_photos(cursor, p_id)

        for r in rel_rows:
            f_path = r["caminho_foto"] or ""
            if f_path and f_path not in photos:
                photos.append(f_path)

            linked_relints.append(LinkedRelintSummary(
                relint_id=r["relint_id"],
                source_file=r["arquivo_origem"] or "",
                subject=r["assunto"] or "Sem assunto",
                date_of_fact=r["data_fato"] or "",
                participation_type=r["tipo_participacao"] or "Acusado",
                municipality=r["municipio"] or ""
            ))

        return PersonDossierDTO(
            person_id=p_key,
            name=name,
            nickname=nick,
            document=doc,
            background=bg,
            photo_path=photos[0] if photos else "",
            photos=photos,
            linked_relints_count=len(linked_relints),
            linked_relints=linked_relints
        )


class PersonUpdateRequest(BaseModel):
    name: Optional[str] = None
    nickname: Optional[str] = None
    document: Optional[str] = None
    background: Optional[str] = None


@router.put("/{person_id}", response_model=PersonDossierDTO)
def update_participant(
    person_id: str,
    payload: PersonUpdateRequest,
    person_repo: IPersonRepo = Depends(get_person_repo)
) -> PersonDossierDTO:
    """
    Atualiza os dados de identificação e antecedentes de uma pessoa no SQLite.
    """
    with person_repo._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pessoas WHERE documento = ? OR id = ? LIMIT 1;", (person_id, person_id))
        p = cursor.fetchone()
        if not p:
            raise HTTPException(status_code=404, detail="Participante não encontrado.")

        db_id = p["id"]
        new_name = payload.name if payload.name is not None else p["nome"]
        new_nick = payload.nickname if payload.nickname is not None else p["alcunha"]
        new_doc = payload.document if payload.document is not None else p["documento"]
        new_bg = payload.background if payload.background is not None else p["antecedentes"]

        cursor.execute("""
            UPDATE pessoas
            SET nome = ?, alcunha = ?, documento = ?, antecedentes = ?
            WHERE id = ?;
        """, (new_name, new_nick, new_doc, new_bg, db_id))
        conn.commit()

    return get_participant_dossier(person_id=person_id, person_repo=person_repo)

