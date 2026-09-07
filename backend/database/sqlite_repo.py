import sqlite3
from pathlib import Path
from typing import List, Optional, Any
from backend.core.entities import IncidentReport, HomicideReport, Participant
from backend.database.database_repo import IDatabaseRepo


class SqliteRepo(IDatabaseRepo):
    """
    Implementação concreta (Adapter) para o repositório de relatórios de incidentes (RELINTs)
    utilizando banco de dados relacional SQLite 100% em Português.
    """

    def __init__(self, db_path: Path):
        """
        Inicializa o repositório SQLite garantindo a criação/migração automática das tabelas.

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

            # 1. Tabela Principal de Ocorrências / RELINTs em Português
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arquivo_origem TEXT UNIQUE NOT NULL,
                    numero_registro TEXT,
                    orgao_registro TEXT,
                    ano_registro TEXT,
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

            # Migração automática para tabelas relints pré-existentes
            cursor.execute("PRAGMA table_info(relints);")
            cols = [row["name"] for row in cursor.fetchall()]
            if "source_file" in cols and "arquivo_origem" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN source_file TO arquivo_origem;")
            if "subject" in cols and "assunto" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN subject TO assunto;")
            if "main_fact" in cols and "fato_principal" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN main_fact TO fato_principal;")
            if "date_of_fact" in cols and "data_fato" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN date_of_fact TO data_fato;")
            if "time_of_fact" in cols and "hora_fato" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN time_of_fact TO hora_fato;")
            if "bm_group" in cols and "grupo_bm" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN bm_group TO grupo_bm;")
            if "relint_type" in cols and "tipo_relint" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN relint_type TO tipo_relint;")
            if "municipality" in cols and "municipio" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN municipality TO municipio;")
            if "neighborhood" in cols and "bairro" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN neighborhood TO bairro;")
            if "address" in cols and "endereco" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN address TO endereco;")
            if "police_unit" in cols and "unidade_policial" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN police_unit TO unidade_policial;")
            if "coordinates" in cols and "coordenadas" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN coordinates TO coordenadas;")
            if "map_url" in cols and "url_mapa" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN map_url TO url_mapa;")
            if "summary" in cols and "resumo" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN summary TO resumo;")
            if "content" in cols and "conteudo" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN content TO conteudo;")
            if "extraction_method" in cols and "metodo_extracao" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN extraction_method TO metodo_extracao;")
            if "user_edited" in cols and "editado_usuario" not in cols:
                cursor.execute("ALTER TABLE relints RENAME COLUMN user_edited TO editado_usuario;")
            if "numero_registro" not in cols:
                cursor.execute("ALTER TABLE relints ADD COLUMN numero_registro TEXT;")
            if "orgao_registro" not in cols:
                cursor.execute("ALTER TABLE relints ADD COLUMN orgao_registro TEXT;")
            if "ano_registro" not in cols:
                cursor.execute("ALTER TABLE relints ADD COLUMN ano_registro TEXT;")

            # 2. Especialização de Homicídios (1 para 1 com relints)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='homicide_details';")
            if cursor.fetchone():
                cursor.execute("ALTER TABLE homicide_details RENAME TO homicidio_detalhes;")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS homicidio_detalhes (
                    relint_id INTEGER PRIMARY KEY,
                    tipo_fato TEXT,
                    motivacao TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            cursor.execute("PRAGMA table_info(homicidio_detalhes);")
            h_cols = [row["name"] for row in cursor.fetchall()]
            if "fact_type" in h_cols and "tipo_fato" not in h_cols:
                cursor.execute("ALTER TABLE homicidio_detalhes RENAME COLUMN fact_type TO tipo_fato;")
            if "motivation" in h_cols and "motivacao" not in h_cols:
                cursor.execute("ALTER TABLE homicidio_detalhes RENAME COLUMN motivation TO motivacao;")

            # Migração de registros policiais de homicidio_detalhes para relints caso existam em bancos legados
            if "numero_registro" in h_cols or "registry_number" in h_cols:
                col_num = "numero_registro" if "numero_registro" in h_cols else "registry_number"
                col_agency = "orgao_registro" if "orgao_registro" in h_cols else "registry_agency"
                col_year = "ano_registro" if "ano_registro" in h_cols else "registry_year"
                cursor.execute(f"""
                    UPDATE relints
                    SET 
                        numero_registro = (SELECT h.{col_num} FROM homicidio_detalhes h WHERE h.relint_id = relints.id),
                        orgao_registro = (SELECT h.{col_agency} FROM homicidio_detalhes h WHERE h.relint_id = relints.id),
                        ano_registro = (SELECT h.{col_year} FROM homicidio_detalhes h WHERE h.relint_id = relints.id)
                    WHERE EXISTS (SELECT 1 FROM homicidio_detalhes h WHERE h.relint_id = relints.id);
                """)

            # Novas Tabelas de Especialidades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prisao_trafico_detalhes (
                    relint_id INTEGER PRIMARY KEY,
                    quantidade_drogas TEXT,
                    tipo_drogas TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roubo_estabelecimento_detalhes (
                    relint_id INTEGER PRIMARY KEY,
                    tipo_estabelecimento TEXT,
                    tipo_local TEXT,
                    vitimas_lesionadas INTEGER,
                    vitima_refem INTEGER,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roubo_residencia_detalhes (
                    relint_id INTEGER PRIMARY KEY,
                    tipo_local TEXT,
                    vitimas_lesionadas INTEGER,
                    vitima_refem INTEGER,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roubo_veiculo_detalhes (
                    relint_id INTEGER PRIMARY KEY,
                    modelo_veiculo TEXT,
                    placa TEXT,
                    recuperado INTEGER,
                    local_recuperacao TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roubo_pedestre_detalhes (
                    relint_id INTEGER PRIMARY KEY,
                    vitimas_lesionadas INTEGER,
                    arma_utilizada TEXT,
                    objeto_roubado TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS furto_veiculo_detalhes (
                    relint_id INTEGER PRIMARY KEY,
                    modelo_veiculo TEXT,
                    placa TEXT,
                    recuperado INTEGER,
                    local_recuperacao TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            # 3. Cadastro Central de Pessoas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persons';")
            if cursor.fetchone():
                cursor.execute("ALTER TABLE persons RENAME TO pessoas;")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    alcunha TEXT,
                    documento TEXT UNIQUE NOT NULL,
                    antecedentes TEXT
                );
            """)

            cursor.execute("PRAGMA table_info(pessoas);")
            p_cols = [row["name"] for row in cursor.fetchall()]
            if "name" in p_cols and "nome" not in p_cols:
                cursor.execute("ALTER TABLE pessoas RENAME COLUMN name TO nome;")
            if "nickname" in p_cols and "alcunha" not in p_cols:
                cursor.execute("ALTER TABLE pessoas RENAME COLUMN nickname TO alcunha;")
            if "document" in p_cols and "documento" not in p_cols:
                cursor.execute("ALTER TABLE pessoas RENAME COLUMN document TO documento;")
            if "background" in p_cols and "antecedentes" not in p_cols:
                cursor.execute("ALTER TABLE pessoas RENAME COLUMN background TO antecedentes;")

            # 4. Tabela de Junção de Participantes (N para N)
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

            cursor.execute("PRAGMA table_info(relint_participantes);")
            part_cols = [row["name"] for row in cursor.fetchall()]
            if "person_id" in part_cols and "pessoa_id" not in part_cols:
                cursor.execute("ALTER TABLE relint_participantes RENAME COLUMN person_id TO pessoa_id;")
            if "participation_type" in part_cols and "tipo_participacao" not in part_cols:
                cursor.execute("ALTER TABLE relint_participantes RENAME COLUMN participation_type TO tipo_participacao;")
            if "photo_path" in part_cols and "caminho_foto" not in part_cols:
                cursor.execute("ALTER TABLE relint_participantes RENAME COLUMN photo_path TO caminho_foto;")

            # 5. Imagens e Mídias Anexas (1 para N)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relint_imagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    relint_id INTEGER NOT NULL,
                    caminho_arquivo TEXT NOT NULL,
                    legenda TEXT,
                    FOREIGN KEY (relint_id) REFERENCES relints(id) ON DELETE CASCADE
                );
            """)

            cursor.execute("PRAGMA table_info(relint_imagens);")
            img_cols = [row["name"] for row in cursor.fetchall()]
            if "file_path" in img_cols and "caminho_arquivo" not in img_cols:
                cursor.execute("ALTER TABLE relint_imagens RENAME COLUMN file_path TO caminho_arquivo;")
            if "caption" in img_cols and "legenda" not in img_cols:
                cursor.execute("ALTER TABLE relint_imagens RENAME COLUMN caption TO legenda;")

            # Visão retrocompatível 'reports'
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS reports AS SELECT id AS doc_id, * FROM relints;
            """)

            conn.commit()

    def _enum_to_str(self, val: Any) -> str:
        if not val:
            return ""
        if hasattr(val, "value"):
            return str(val.value)
        return str(val)

    def save(self, report: IncidentReport) -> str:
        """
        Salva ou atualiza um relatório de incidente no SQLite.

        :param report: Entidade IncidentReport ou HomicideReport a ser persistida.
        :return: ID único atribuído ao relatório persistido.
        """
        source_file = report.source_file or ""
        reg_num = getattr(report, "registry_number", None) or ""
        reg_agency = getattr(report, "registry_agency", None) or ""
        reg_year = getattr(report, "registry_year", None) or ""
        subject = report.subject or ""
        main_fact = getattr(report, "main_fact", "") or ""
        date_of_fact = report.date_of_fact or ""
        time_of_fact = report.time_of_fact or ""
        bm_group = self._enum_to_str(report.bm_group) or "Outros"
        relint_type = self._enum_to_str(report.relint_type) or "Outros"
        municipality = report.municipality or ""
        neighborhood = getattr(report, "neighborhood", "") or ""
        address = getattr(report, "address", "") or ""
        police_unit = getattr(report, "police_unit", "") or ""
        coordinates = getattr(report, "coordinates", "") or ""
        map_url = getattr(report, "map_url", "") or ""
        summary = report.summary or ""
        content = report.content or ""
        extraction_method = getattr(report, "extraction_method", None) or "Regex (Sem IA)"
        user_edited = 1 if getattr(report, "user_edited", False) else 0

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Salva na tabela principal 'relints'
            cursor.execute("""
                INSERT INTO relints (
                    arquivo_origem, numero_registro, orgao_registro, ano_registro,
                    assunto, fato_principal, data_fato, hora_fato,
                    grupo_bm, tipo_relint, municipio, bairro, endereco,
                    unidade_policial, coordenadas, url_mapa, resumo, conteudo, metodo_extracao, editado_usuario
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(arquivo_origem) DO UPDATE SET
                    numero_registro=excluded.numero_registro,
                    orgao_registro=excluded.orgao_registro,
                    ano_registro=excluded.ano_registro,
                    assunto=excluded.assunto,
                    fato_principal=excluded.fato_principal,
                    data_fato=excluded.data_fato,
                    hora_fato=excluded.hora_fato,
                    grupo_bm=excluded.grupo_bm,
                    tipo_relint=excluded.tipo_relint,
                    municipio=excluded.municipio,
                    bairro=excluded.bairro,
                    endereco=excluded.endereco,
                    unidade_policial=excluded.unidade_policial,
                    coordenadas=excluded.coordenadas,
                    url_mapa=excluded.url_mapa,
                    resumo=excluded.resumo,
                    conteudo=excluded.conteudo,
                    metodo_extracao=excluded.metodo_extracao,
                    editado_usuario=excluded.editado_usuario;
            """, (
                source_file, reg_num, reg_agency, reg_year,
                subject, main_fact, date_of_fact, time_of_fact,
                bm_group, relint_type, municipality, neighborhood, address,
                police_unit, coordinates, map_url, summary, content, extraction_method, user_edited
            ))

            cursor.execute("SELECT id FROM relints WHERE arquivo_origem = ?;", (source_file,))
            row = cursor.fetchone()
            if not row:
                conn.commit()
                return ""
            relint_id = row["id"]

            # 2. Atualiza detalhes específicos da especialidade
            # 2.1 Homicídio
            from backend.core.entities import HomicideReport, DrugTraffickingReport, EstablishmentRobberyReport, ResidenceRobberyReport, VehicleRobberyReport, PedestrianRobberyReport, VehicleTheftReport

            is_homicide = (bm_group == "Homicídio" or isinstance(report, HomicideReport))
            if is_homicide:
                fact_type = getattr(report, "fact_type", None) or ""
                motivation = self._enum_to_str(getattr(report, "motivation", "Desconhecido")) or "Desconhecido"
                cursor.execute("""
                    INSERT INTO homicidio_detalhes (relint_id, tipo_fato, motivacao)
                    VALUES (?, ?, ?)
                    ON CONFLICT(relint_id) DO UPDATE SET tipo_fato=excluded.tipo_fato, motivacao=excluded.motivacao;
                """, (relint_id, fact_type, motivation))
            else:
                cursor.execute("DELETE FROM homicidio_detalhes WHERE relint_id = ?;", (relint_id,))

            # 2.2 Tráfico de Drogas
            if bm_group == "Prisão por Tráfico" or isinstance(report, DrugTraffickingReport):
                cursor.execute("""
                    INSERT INTO prisao_trafico_detalhes (relint_id, quantidade_drogas, tipo_drogas)
                    VALUES (?, ?, ?)
                    ON CONFLICT(relint_id) DO UPDATE SET quantidade_drogas=excluded.quantidade_drogas, tipo_drogas=excluded.tipo_drogas;
                """, (relint_id, getattr(report, "drug_quantity", "") or "", getattr(report, "drug_types", "") or ""))
            else:
                cursor.execute("DELETE FROM prisao_trafico_detalhes WHERE relint_id = ?;", (relint_id,))

            # 2.3 Roubo a Estabelecimento
            if bm_group == "Roubo a Estabelecimento" or isinstance(report, EstablishmentRobberyReport):
                cursor.execute("""
                    INSERT INTO roubo_estabelecimento_detalhes (relint_id, tipo_estabelecimento, tipo_local, vitimas_lesionadas, vitima_refem)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(relint_id) DO UPDATE SET tipo_estabelecimento=excluded.tipo_estabelecimento, tipo_local=excluded.tipo_local, vitimas_lesionadas=excluded.vitimas_lesionadas, vitima_refem=excluded.vitima_refem;
                """, (relint_id, getattr(report, "establishment_type", "") or "", getattr(report, "location_type", "Urbano") or "Urbano", getattr(report, "injured_victims", 0) or 0, getattr(report, "hostage_victim", 0) or 0))
            else:
                cursor.execute("DELETE FROM roubo_estabelecimento_detalhes WHERE relint_id = ?;", (relint_id,))

            # 2.4 Roubo a Residência
            if bm_group == "Roubo a Residência" or isinstance(report, ResidenceRobberyReport):
                cursor.execute("""
                    INSERT INTO roubo_residencia_detalhes (relint_id, tipo_local, vitimas_lesionadas, vitima_refem)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(relint_id) DO UPDATE SET tipo_local=excluded.tipo_local, vitimas_lesionadas=excluded.vitimas_lesionadas, vitima_refem=excluded.vitima_refem;
                """, (relint_id, getattr(report, "location_type", "Urbano") or "Urbano", getattr(report, "injured_victims", 0) or 0, getattr(report, "hostage_victim", 0) or 0))
            else:
                cursor.execute("DELETE FROM roubo_residencia_detalhes WHERE relint_id = ?;", (relint_id,))

            # 2.5 Roubo de Veículo
            if bm_group == "Roubo de Veículo" or isinstance(report, VehicleRobberyReport):
                cursor.execute("""
                    INSERT INTO roubo_veiculo_detalhes (relint_id, modelo_veiculo, placa, recuperado, local_recuperacao)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(relint_id) DO UPDATE SET modelo_veiculo=excluded.modelo_veiculo, placa=excluded.placa, recuperado=excluded.recuperado, local_recuperacao=excluded.local_recuperacao;
                """, (relint_id, getattr(report, "vehicle_model", "") or "", getattr(report, "license_plate", "") or "", getattr(report, "recovered", 0) or 0, getattr(report, "recovery_location", "") or ""))
            else:
                cursor.execute("DELETE FROM roubo_veiculo_detalhes WHERE relint_id = ?;", (relint_id,))

            # 2.6 Roubo a Pedestre
            if bm_group == "Roubo a Pedestre" or isinstance(report, PedestrianRobberyReport):
                cursor.execute("""
                    INSERT INTO roubo_pedestre_detalhes (relint_id, vitimas_lesionadas, arma_utilizada, objeto_roubado)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(relint_id) DO UPDATE SET vitimas_lesionadas=excluded.vitimas_lesionadas, arma_utilizada=excluded.arma_utilizada, objeto_roubado=excluded.objeto_roubado;
                """, (relint_id, getattr(report, "injured_victims", 0) or 0, getattr(report, "weapon_used", "") or "", getattr(report, "stolen_object", "") or ""))
            else:
                cursor.execute("DELETE FROM roubo_pedestre_detalhes WHERE relint_id = ?;", (relint_id,))

            # 2.7 Furto de Veículo
            if bm_group == "Furto de Veículo" or isinstance(report, VehicleTheftReport):
                cursor.execute("""
                    INSERT INTO furto_veiculo_detalhes (relint_id, modelo_veiculo, placa, recuperado, local_recuperacao)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(relint_id) DO UPDATE SET modelo_veiculo=excluded.modelo_veiculo, placa=excluded.placa, recuperado=excluded.recuperado, local_recuperacao=excluded.local_recuperacao;
                """, (relint_id, getattr(report, "vehicle_model", "") or "", getattr(report, "license_plate", "") or "", getattr(report, "recovered", 0) or 0, getattr(report, "recovery_location", "") or ""))
            else:
                cursor.execute("DELETE FROM furto_veiculo_detalhes WHERE relint_id = ?;", (relint_id,))

            # 3. Atualiza Imagens anexas
            cursor.execute("DELETE FROM relint_imagens WHERE relint_id = ?;", (relint_id,))
            for img in (report.images or []):
                file_path = ""
                caption = ""
                if isinstance(img, dict):
                    file_path = img.get("file_path") or img.get("caminho_arquivo") or img.get("path") or ""
                    caption = img.get("caption") or img.get("legenda") or ""
                elif isinstance(img, str):
                    file_path = img
                if file_path:
                    cursor.execute("""
                        INSERT INTO relint_imagens (relint_id, caminho_arquivo, legenda)
                        VALUES (?, ?, ?);
                    """, (relint_id, file_path, caption))

            # 4. Atualiza Pessoas e Participantes
            cursor.execute("DELETE FROM relint_participantes WHERE relint_id = ?;", (relint_id,))
            for part in (report.participants or []):
                if isinstance(part, dict):
                    raw_name = part.get("name") or part.get("nome")
                    p_name = str(raw_name).strip() if (raw_name and not isinstance(raw_name, bool)) else ""
                    
                    raw_doc = part.get("document") or part.get("documento")
                    p_doc = str(raw_doc).strip() if (raw_doc and not isinstance(raw_doc, bool)) else ""
                    
                    raw_nick = part.get("nickname") or part.get("alcunha")
                    p_nick = str(raw_nick).strip() if (raw_nick and not isinstance(raw_nick, bool)) else ""
                    
                    raw_back = part.get("background") or part.get("antecedentes")
                    p_back = str(raw_back).strip() if (raw_back and not isinstance(raw_back, bool)) else ""
                    
                    raw_type = part.get("participation_type") or part.get("tipo_participacao") or "Acusado"
                    photo_path = part.get("photo_path") or part.get("caminho_foto") or ""
                else:
                    raw_name = getattr(part, "name", "")
                    p_name = str(raw_name).strip() if (raw_name and not isinstance(raw_name, bool)) else ""
                    
                    raw_doc = getattr(part, "document", "")
                    p_doc = str(raw_doc).strip() if (raw_doc and not isinstance(raw_doc, bool)) else ""
                    
                    raw_nick = getattr(part, "nickname", "")
                    p_nick = str(raw_nick).strip() if (raw_nick and not isinstance(raw_nick, bool)) else ""
                    
                    raw_back = getattr(part, "background", "")
                    p_back = str(raw_back).strip() if (raw_back and not isinstance(raw_back, bool)) else ""
                    
                    raw_type = getattr(part, "participation_type", "Acusado")
                    photo_path = getattr(part, "photo_path", "") or ""

                if not p_name:
                    continue

                clean_doc = p_doc.replace(".", "").replace("-", "") if p_doc else ""
                p_key = clean_doc if clean_doc else p_name.lower()

                cursor.execute("""
                    INSERT INTO pessoas (documento, nome, alcunha, antecedentes)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(documento) DO UPDATE SET
                        nome=excluded.nome,
                        alcunha=CASE WHEN excluded.alcunha != '' THEN excluded.alcunha ELSE pessoas.alcunha END,
                        antecedentes=CASE WHEN excluded.antecedentes != '' THEN excluded.antecedentes ELSE pessoas.antecedentes END;
                """, (p_key, p_name, p_nick, p_back))

                cursor.execute("SELECT id FROM pessoas WHERE documento = ?;", (p_key,))
                p_row = cursor.fetchone()
                if p_row:
                    person_id = p_row["id"]
                    part_type = self._enum_to_str(raw_type) or "Acusado"
                    cursor.execute("""
                        INSERT INTO relint_participantes (relint_id, pessoa_id, tipo_participacao, caminho_foto)
                        VALUES (?, ?, ?, ?);
                    """, (relint_id, person_id, part_type, photo_path))

            conn.commit()
            return str(relint_id)

    def _build_report_from_row(self, conn: sqlite3.Connection, relint_row: sqlite3.Row) -> IncidentReport:
        relint_id = relint_row["id"]
        cursor = conn.cursor()

        # 1. Carrega Imagens
        cursor.execute("SELECT caminho_arquivo, legenda FROM relint_imagens WHERE relint_id = ? ORDER BY id ASC;", (relint_id,))
        img_rows = cursor.fetchall()
        images = [{"file_path": r["caminho_arquivo"], "caminho_arquivo": r["caminho_arquivo"], "caption": r["legenda"], "legenda": r["legenda"]} for r in img_rows]

        # 2. Carrega Participantes
        cursor.execute("""
            SELECT p.nome, p.alcunha, p.documento, p.antecedentes, rp.tipo_participacao, rp.caminho_foto
            FROM relint_participantes rp
            JOIN pessoas p ON rp.pessoa_id = p.id
            WHERE rp.relint_id = ?
            ORDER BY rp.id ASC;
        """, (relint_id,))
        part_rows = cursor.fetchall()
        participants = []
        for pr in part_rows:
            participants.append(Participant(
                name=pr["nome"],
                nickname=pr["alcunha"] or "",
                document=pr["documento"] or "",
                background=pr["antecedentes"] or "",
                participation_type=pr["tipo_participacao"] or "Acusado",
                photo_path=pr["caminho_foto"] or ""
            ))

        # 3. Verifica se possui detalhes de Homicídio
        cursor.execute("SELECT * FROM homicidio_detalhes WHERE relint_id = ?;", (relint_id,))
        hom_row = cursor.fetchone()

        source_file = relint_row["arquivo_origem"] if "arquivo_origem" in relint_row.keys() else relint_row["source_file"]
        reg_num = relint_row["numero_registro"] if "numero_registro" in relint_row.keys() else getattr(relint_row, "registry_number", "")
        reg_agency = relint_row["orgao_registro"] if "orgao_registro" in relint_row.keys() else getattr(relint_row, "registry_agency", "")
        reg_year = relint_row["ano_registro"] if "ano_registro" in relint_row.keys() else getattr(relint_row, "registry_year", "")
        
        # Fallback de bancos antigos onde o registro ficava em homicidio_detalhes
        if hom_row and not reg_num:
            reg_num = hom_row["numero_registro"] if "numero_registro" in hom_row.keys() else (hom_row["registry_number"] if "registry_number" in hom_row.keys() else "")
            reg_agency = hom_row["orgao_registro"] if "orgao_registro" in hom_row.keys() else (hom_row["registry_agency"] if "registry_agency" in hom_row.keys() else "")
            reg_year = hom_row["ano_registro"] if "ano_registro" in hom_row.keys() else (hom_row["registry_year"] if "registry_year" in hom_row.keys() else "")

        subject = relint_row["assunto"] if "assunto" in relint_row.keys() else relint_row["subject"]
        main_fact = relint_row["fato_principal"] if "fato_principal" in relint_row.keys() else relint_row["main_fact"]
        date_of_fact = relint_row["data_fato"] if "data_fato" in relint_row.keys() else relint_row["date_of_fact"]
        time_of_fact = relint_row["hora_fato"] if "hora_fato" in relint_row.keys() else relint_row["time_of_fact"]
        bm_group = relint_row["grupo_bm"] if "grupo_bm" in relint_row.keys() else relint_row["bm_group"]
        relint_type = relint_row["tipo_relint"] if "tipo_relint" in relint_row.keys() else relint_row["relint_type"]
        municipality = relint_row["municipio"] if "municipio" in relint_row.keys() else relint_row["municipality"]
        neighborhood = relint_row["bairro"] if "bairro" in relint_row.keys() else relint_row["neighborhood"]
        address = relint_row["endereco"] if "endereco" in relint_row.keys() else relint_row["address"]
        police_unit = relint_row["unidade_policial"] if "unidade_policial" in relint_row.keys() else relint_row["police_unit"]
        coordinates = relint_row["coordenadas"] if "coordenadas" in relint_row.keys() else relint_row["coordinates"]
        map_url = relint_row["url_mapa"] if "url_mapa" in relint_row.keys() else relint_row["map_url"]
        summary = relint_row["resumo"] if "resumo" in relint_row.keys() else relint_row["summary"]
        content = relint_row["conteudo"] if "conteudo" in relint_row.keys() else relint_row["content"]
        ext_method = relint_row["metodo_extracao"] if ("metodo_extracao" in relint_row.keys() and relint_row["metodo_extracao"]) else "Regex (Sem IA)"
        user_edited = bool(relint_row["editado_usuario"]) if "editado_usuario" in relint_row.keys() else bool(relint_row["user_edited"])

        report_data = {
            "id": str(relint_id),
            "source_file": source_file,
            "registry_number": reg_num or "",
            "registry_agency": reg_agency or "",
            "registry_year": reg_year or "",
            "subject": subject or "",
            "main_fact": main_fact or "",
            "date_of_fact": date_of_fact or "",
            "time_of_fact": time_of_fact or "",
            "bm_group": bm_group or "Outros",
            "relint_type": relint_type or "Outros",
            "municipality": municipality or "",
            "neighborhood": neighborhood or "",
            "address": address or "",
            "police_unit": police_unit or "",
            "coordinates": coordinates or "",
            "map_url": map_url or "",
            "summary": summary or "",
            "content": content or "",
            "extraction_method": ext_method,
            "user_edited": user_edited,
            "images": images,
            "participants": participants
        }

        if hom_row or bm_group == "Homicídio":
            fact_type = ""
            motivation = "Desconhecido"
            if hom_row:
                fact_type = (hom_row["tipo_fato"] if "tipo_fato" in hom_row.keys() else (hom_row["fact_type"] if "fact_type" in hom_row.keys() else "")) or ""
                motivation = (hom_row["motivacao"] if "motivacao" in hom_row.keys() else (hom_row["motivation"] if "motivation" in hom_row.keys() else "")) or "Desconhecido"

            report_data.update({
                "fact_type": fact_type,
                "motivation": motivation,
            })
            from backend.core.entities import HomicideReport
            return HomicideReport.model_validate(report_data)

        if bm_group == "Prisão por Tráfico":
            cursor.execute("SELECT * FROM prisao_trafico_detalhes WHERE relint_id = ?;", (relint_id,))
            dt_row = cursor.fetchone()
            if dt_row:
                report_data.update({
                    "drug_quantity": dt_row["quantidade_drogas"] or "",
                    "drug_types": dt_row["tipo_drogas"] or ""
                })
            from backend.core.entities import DrugTraffickingReport
            return DrugTraffickingReport.model_validate(report_data)

        if bm_group == "Roubo a Estabelecimento":
            cursor.execute("SELECT * FROM roubo_estabelecimento_detalhes WHERE relint_id = ?;", (relint_id,))
            er_row = cursor.fetchone()
            if er_row:
                report_data.update({
                    "establishment_type": er_row["tipo_estabelecimento"] or "",
                    "location_type": er_row["tipo_local"] or "Urbano",
                    "injured_victims": er_row["vitimas_lesionadas"] or 0,
                    "hostage_victim": er_row["vitima_refem"] or 0
                })
            from backend.core.entities import EstablishmentRobberyReport
            return EstablishmentRobberyReport.model_validate(report_data)

        if bm_group == "Roubo a Residência":
            cursor.execute("SELECT * FROM roubo_residencia_detalhes WHERE relint_id = ?;", (relint_id,))
            rr_row = cursor.fetchone()
            if rr_row:
                report_data.update({
                    "location_type": rr_row["tipo_local"] or "Urbano",
                    "injured_victims": rr_row["vitimas_lesionadas"] or 0,
                    "hostage_victim": rr_row["vitima_refem"] or 0
                })
            from backend.core.entities import ResidenceRobberyReport
            return ResidenceRobberyReport.model_validate(report_data)

        if bm_group == "Roubo de Veículo":
            cursor.execute("SELECT * FROM roubo_veiculo_detalhes WHERE relint_id = ?;", (relint_id,))
            vr_row = cursor.fetchone()
            if vr_row:
                report_data.update({
                    "vehicle_model": vr_row["modelo_veiculo"] or "",
                    "license_plate": vr_row["placa"] or "",
                    "recovered": vr_row["recuperado"] or 0,
                    "recovery_location": vr_row["local_recuperacao"] or ""
                })
            from backend.core.entities import VehicleRobberyReport
            return VehicleRobberyReport.model_validate(report_data)

        if bm_group == "Roubo a Pedestre":
            cursor.execute("SELECT * FROM roubo_pedestre_detalhes WHERE relint_id = ?;", (relint_id,))
            pr_row = cursor.fetchone()
            if pr_row:
                report_data.update({
                    "injured_victims": pr_row["vitimas_lesionadas"] or 0,
                    "weapon_used": pr_row["arma_utilizada"] or "",
                    "stolen_object": pr_row["objeto_roubado"] or ""
                })
            from backend.core.entities import PedestrianRobberyReport
            return PedestrianRobberyReport.model_validate(report_data)

        if bm_group == "Furto de Veículo":
            cursor.execute("SELECT * FROM furto_veiculo_detalhes WHERE relint_id = ?;", (relint_id,))
            vt_row = cursor.fetchone()
            if vt_row:
                report_data.update({
                    "vehicle_model": vt_row["modelo_veiculo"] or "",
                    "license_plate": vt_row["placa"] or "",
                    "recovered": vt_row["recuperado"] or 0,
                    "recovery_location": vt_row["local_recuperacao"] or ""
                })
            from backend.core.entities import VehicleTheftReport
            return VehicleTheftReport.model_validate(report_data)

        return IncidentReport.model_validate(report_data)

    def get_by_id(self, report_id: str) -> Optional[IncidentReport]:
        """
        Busca um relatório no SQLite pelo seu ID único.
        """
        try:
            relint_id = int(report_id)
        except ValueError:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM relints WHERE id = ?;", (relint_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_report_from_row(conn, row)

    def get_all(self) -> List[IncidentReport]:
        """
        Retorna todos os relatórios cadastrados no SQLite ordenados do mais recente para o mais antigo.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM relints ORDER BY id DESC;")
            rows = cursor.fetchall()
            reports = []
            for row in rows:
                try:
                    reports.append(self._build_report_from_row(conn, row))
                except Exception:
                    pass
            return reports

    def exists_by_source_file(self, filename: str) -> bool:
        """
        Verifica se um relatório originado do arquivo fornecido já existe.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM relints WHERE arquivo_origem = ? LIMIT 1;", (filename,))
            return cursor.fetchone() is not None

    def delete_by_source_file(self, filename: str) -> bool:
        """
        Remove um relatório do SQLite com base no nome do arquivo original.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relints WHERE arquivo_origem = ?;", (filename,))
            conn.commit()
            return cursor.rowcount > 0

    def get_by_source_file(self, filename: str) -> Optional[IncidentReport]:
        """
        Busca um relatório pelo nome do arquivo original.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM relints WHERE arquivo_origem = ? LIMIT 1;", (filename,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._build_report_from_row(conn, row)

    def clear_all(self) -> None:
        """
        Remove todos os registros das tabelas de relatórios.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relints;")
            cursor.execute("DELETE FROM pessoas;")
            conn.commit()

    def get_all_source_filenames(self) -> set:
        """
        Retorna um conjunto em memória contendo os nomes de todos os arquivos já cadastrados (busca O(1)).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT arquivo_origem FROM relints WHERE arquivo_origem IS NOT NULL AND arquivo_origem != '';")
            rows = cursor.fetchall()
            return {row["arquivo_origem"] for row in rows}

    def get_report_counts(self) -> dict:
        """
        Retorna a contagem estatística agregada em 1 única query SQL ultrarrápida (0.1ms).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM relints;")
            total_row = cursor.fetchone()
            total = total_row["total"] if total_row else 0

            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN metodo_extracao LIKE '%Ollama%' OR metodo_extracao LIKE '%LLM%' THEN 1 ELSE 0 END) AS llm_count,
                    SUM(CASE WHEN (metodo_extracao LIKE '%Regex%' OR metodo_extracao LIKE '%Sem IA%') AND metodo_extracao NOT LIKE '%Ollama%' THEN 1 ELSE 0 END) AS regex_count
                FROM relints;
            """)
            row = cursor.fetchone()
            llm_cnt = row["llm_count"] if (row and row["llm_count"]) else 0
            regex_cnt = row["regex_count"] if (row and row["regex_count"]) else 0

            return {
                "total": total,
                "llm": llm_cnt,
                "regex": regex_cnt
            }

    def get_dashboard_metrics(self) -> dict:
        """
        Retorna todas as métricas essenciais do dashboard em uma única transação SQL ultrarrápida.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de relints, contagem de homicídios e métodos
            cursor.execute("""
                SELECT 
                    COUNT(*) AS total_relints,
                    SUM(CASE WHEN grupo_bm = 'Homicídio' THEN 1 ELSE 0 END) AS homicide_count,
                    SUM(CASE WHEN metodo_extracao LIKE '%Ollama%' OR metodo_extracao LIKE '%LLM%' OR (metodo_extracao LIKE '%IA%' AND metodo_extracao NOT LIKE '%Sem IA%') THEN 1 ELSE 0 END) AS llm_count
                FROM relints;
            """)
            rel_row = cursor.fetchone()
            total_relints = rel_row["total_relints"] if (rel_row and rel_row["total_relints"]) else 0
            homicide_count = rel_row["homicide_count"] if (rel_row and rel_row["homicide_count"]) else 0
            llm_count = rel_row["llm_count"] if (rel_row and rel_row["llm_count"]) else 0

            # Total de pessoas cadastradas / participantes
            cursor.execute("SELECT COUNT(*) AS total_persons FROM pessoas;")
            p_row = cursor.fetchone()
            total_persons = p_row["total_persons"] if (p_row and p_row["total_persons"]) else 0

            llm_rate = round((llm_count / total_relints) * 100, 1) if total_relints > 0 else 100.0

            return {
                "total_relints": total_relints,
                "total_persons": total_persons,
                "homicide_count": homicide_count,
                "llm_rate": llm_rate
            }

