import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from backend.core.entities import Person
from backend.database.person_repo import IPersonRepo


class SqlitePersonRepo(IPersonRepo):
    """
    Implementação concreta (Adapter) para o repositório de Pessoas (Dossiê consolidado)
    utilizando a tabela relacional normalizada 'pessoas' e junções com 'relint_participantes' em Português.
    """

    def __init__(self, db_path: Path):
        """
        Inicializa o repositório de pessoas apontando para o arquivo de banco SQLite fornecido.

        :param db_path: Caminho completo para o arquivo .db do SQLite.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persons';")
            if cursor.fetchone():
                cursor.execute("ALTER TABLE persons RENAME TO pessoas;")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arquivo_origem TEXT UNIQUE NOT NULL,
                    assunto TEXT,
                    fato_principal TEXT,
                    data_fato TEXT,
                    hora_fato TEXT,
                    grupo_bm TEXT,
                    tipo_relint TEXT,
                    municipio TEXT,
                    bairro TEXT,
                    endereco TEXT,
                    unidade_policial TEXT,
                    coordenadas TEXT,
                    url_mapa TEXT,
                    resumo TEXT,
                    conteudo TEXT,
                    metodo_extracao TEXT DEFAULT 'Ollama (IA)',
                    editado_usuario INTEGER DEFAULT 0
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    alcunha TEXT,
                    documento TEXT UNIQUE NOT NULL,
                    antecedentes TEXT
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relint_participantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    relint_id INTEGER NOT NULL,
                    pessoa_id INTEGER NOT NULL,
                    tipo_participacao TEXT,
                    caminho_foto TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE,
                    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id) ON DELETE CASCADE
                );
            """)
            conn.commit()

    def save(self, person: Person) -> str:
        """
        Salva ou atualiza uma pessoa no SQLite.
        """
        p_name = person.name.strip()
        p_doc = (person.documents[0] if person.documents else "") or ""
        clean_doc = p_doc.replace(".", "").replace("-", "") if p_doc else ""
        p_key = person.person_id or (clean_doc if clean_doc else p_name.lower())
        p_nick = ", ".join(set(person.aliases)) if person.aliases else ""

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pessoas (documento, nome, alcunha)
                VALUES (?, ?, ?)
                ON CONFLICT(documento) DO UPDATE SET
                    nome=excluded.nome,
                    alcunha=CASE WHEN excluded.alcunha != '' THEN excluded.alcunha ELSE pessoas.alcunha END;
            """, (p_key, p_name, p_nick))
            conn.commit()
            return p_key

    def update(self, person: Person) -> None:
        """
        Atualiza uma pessoa existente no SQLite.
        """
        self.save(person)

    def _build_person_from_row(self, conn: sqlite3.Connection, row: sqlite3.Row) -> Person:
        person_db_id = row["id"]
        person_key = row["documento"] if "documento" in row.keys() else row["document"]
        name = row["nome"] if "nome" in row.keys() else row["name"]
        nickname = (row["alcunha"] if "alcunha" in row.keys() else row["nickname"]) or ""
        document = person_key or ""
        # documento agora também guarda a chave sintética (nome em minúsculo) quando a pessoa
        # não tem RG/CPF real (ADR-0101 — chave_pessoa foi eliminada, valor absorvido aqui) —
        # nesse caso não é um documento de verdade, não deve aparecer como tal.
        if document and document.lower() == name.strip().lower():
            document = ""

        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.arquivo_origem, rp.caminho_foto
            FROM relint_participantes rp
            JOIN relints r ON rp.relint_id = r.id
            WHERE rp.pessoa_id = ?;
        """, (person_db_id,))
        p_rows = cursor.fetchall()

        linked_relints = list(set(r["arquivo_origem"] for r in p_rows if r["arquivo_origem"]))
        photos = list(set(r["caminho_foto"] for r in p_rows if r["caminho_foto"]))
        aliases = [a.strip() for a in nickname.split(",") if a.strip()]
        documents = [document] if document else []

        return Person(
            person_id=person_key,
            name=name,
            aliases=aliases,
            documents=documents,
            photos=photos,
            linked_relints=linked_relints,
            last_updated=datetime.now().isoformat()
        )

    def get_by_id(self, person_id: str) -> Optional[Person]:
        """
        Busca uma pessoa no SQLite pelo seu documento (chave única).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pessoas WHERE documento = ? LIMIT 1;", (person_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_person_from_row(conn, row)

    def get_by_document(self, document: str) -> Optional[Person]:
        """
        Busca uma pessoa pelo número de documento (RG/CPF). `documento` pode estar salvo com
        ou sem pontuação (depende de como a pessoa foi originalmente inserida — ver save()),
        então a comparação limpa pontuação dos dois lados antes de comparar.
        """
        if not document:
            return None
        clean_doc = document.strip().replace(".", "").replace("-", "")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pessoas WHERE REPLACE(REPLACE(documento, '.', ''), '-', '') = ? LIMIT 1;", (clean_doc,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_person_from_row(conn, row)

    def get_all(self) -> List[Person]:
        """
        Retorna todas as pessoas cadastradas no banco SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pessoas ORDER BY nome ASC;")
            rows = cursor.fetchall()
            persons = []
            for row in rows:
                try:
                    persons.append(self._build_person_from_row(conn, row))
                except Exception:
                    pass
            return persons

    def clear_all(self) -> None:
        """
        Remove todas as pessoas cadastradas no banco SQLite.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pessoas;")
            conn.commit()
