import time
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
from backend.engine.parsers.file_parser import IFileParser
from backend.engine.extractors.llm.llm_processor import ILlmProcessor
from backend.database.database_repo import IDatabaseRepo
from backend.database.person_repo import IPersonRepo
from backend.core.entities import IncidentReport, Participant
from backend.engine.cleaners.text_cleaner import (
    clean_relint_text,
    extract_history_from_annex,
    extract_date_of_fact,
    extract_time_of_fact,
    extract_map_url,
    resolve_coordinates_and_map_info,
    extract_subject_fallback,
    extract_fallback_summary
)
from backend.engine.extractors.llm.rules.base_rule import IncidentRule
from backend.task_manager.registry.processed_registry import IProcessedRegistry
from backend.engine.cleaners.bm_classifier import classify_bm_group, classify_relint_type

class EtlService:
    """
    Serviço de aplicação responsável pela orquestração do pipeline completo de ETL.
    """

    def __init__(
        self,
        file_parser: IFileParser,
        llm_processor: ILlmProcessor,
        database_repo: IDatabaseRepo,
        processed_registry: IProcessedRegistry,
        person_repo: IPersonRepo,
        use_llm: bool = True
    ):
        self.file_parser = file_parser
        self.llm_processor = llm_processor
        self.database_repo = database_repo
        self.processed_registry = processed_registry
        self.person_repo = person_repo
        self.use_llm = use_llm

    def _normalize_response_dict(self, response_dict: dict) -> dict:
        """Normaliza chaves em Português/Inglês retornadas pela LLM para o padrão da entidade de domínio."""
        if not isinstance(response_dict, dict):
            return {}

        key_map = {
            "assunto": "subject",
            "fato_principal": "main_fact",
            "data_fato": "date_of_fact",
            "hora_fato": "time_of_fact",
            "grupo_bm": "bm_group",
            "tipo_relint": "relint_type",
            "municipio": "municipality",
            "bairro": "neighborhood",
            "endereco": "address",
            "unidade_policial": "police_unit",
            "coordenadas": "coordinates",
            "url_mapa": "map_url",
            "resumo": "summary",
            "participantes": "participants",
            "numero_registro": "registry_number",
            "orgao_registro": "registry_agency",
            "ano_registro": "registry_year",
            "tipo_fato": "fact_type",
            "motivacao": "motivation"
        }

        normalized = {}
        for k, v in response_dict.items():
            std_key = key_map.get(str(k).lower(), k)
            normalized[std_key] = v

        raw_parts = normalized.get("participants", [])
        if isinstance(raw_parts, list):
            from backend.engine.cleaners.text_cleaner import clean_person_name
            norm_parts = []
            p_key_map = {
                "nome": "name",
                "alcunha": "nickname",
                "vulgo": "nickname",
                "documento": "document",
                "cpf": "document",
                "rg": "document",
                "antecedentes": "background",
                "tipo_participacao": "participation_type"
            }
            for p in raw_parts:
                if isinstance(p, dict):
                    norm_p = {}
                    for pk, pv in p.items():
                        norm_p[p_key_map.get(str(pk).lower(), pk)] = pv
                    if "name" in norm_p and norm_p["name"]:
                        norm_p["name"] = clean_person_name(str(norm_p["name"]))
                    norm_parts.append(norm_p)
                else:
                    norm_parts.append(p)
            normalized["participants"] = norm_parts

        return normalized

    def process_file(
        self,
        file_path: Path,
        rule: Optional[IncidentRule] = None,
        on_progress: Optional[Callable[[str], None]] = None,
        on_success: Optional[Callable[[IncidentReport], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_filtered: Optional[Callable[[str], None]] = None,
        on_sent_to_llm: Optional[Callable[[str], None]] = None,
        on_llm_disconnected: Optional[Callable[[str], None]] = None
    ) -> Optional[IncidentReport]:
        """
        Executa o pipeline de processamento de um único arquivo PDF.
        """
        filename = file_path.name
        start_time = time.time()
        
        try:
            if self.database_repo.exists_by_source_file(filename) is True:
                if on_progress: on_progress(f"[{filename}] Já cadastrado no banco. Pulando.")
                if rule: self.processed_registry.register_processed(filename, rule.name, "confirmed")
                return None

            if rule and self.processed_registry.is_processed(filename, rule.name) is True:
                if on_progress: on_progress(f"[{filename}] Já processado. Pulando.")
                return None

            if on_progress: on_progress(f"[{filename}] -> Extraindo texto do PDF...")
            raw_text = self.file_parser.extract_text(file_path)
            
            from backend.engine.cleaners.hybrid_cleaner import HybridCleaner
            if on_progress: on_progress(f"[{filename}] -> Limpeza Híbrida (ML + NER)...")
            try:
                cleaned_text, pre_extracted_entities = HybridCleaner.process_hybrid(file_path)
            except Exception:
                cleaned_text = ""
                pre_extracted_entities = []

            if not cleaned_text or not cleaned_text.strip():
                cleaned_text = clean_relint_text(raw_text)

            # Fallback seguro: se a limpeza removeu tudo mas o PDF tinha texto original, usa o texto bruto normalizado
            if not cleaned_text.strip() and raw_text and raw_text.strip():
                cleaned_text = raw_text.strip()

            if not cleaned_text.strip():
                raise ValueError("O arquivo PDF está vazio após a limpeza.")


            # Extração segura do histórico usando regra 11 (pós ANEXOS)
            history_from_annex = extract_history_from_annex(raw_text)
            
            questions = rule.questions if rule and rule.questions is not None else {}
            schema_model = None
            if rule and hasattr(rule, 'get_schema_model'):
                schema_model = rule.get_schema_model()
            else:
                schema_model = IncidentReport

            # Execução 100% ISOLADA de acordo com o motor selecionado
            if self.use_llm and self.llm_processor:
                if on_progress: on_progress(f"[{filename}] -> Processando exclusivamente com IA local (Ollama)...")
                if on_sent_to_llm: on_sent_to_llm(filename)
                try:
                    from backend.engine.extractors.llm.pipeline import LlmPipeline
                    llm_pipeline = LlmPipeline(processor=self.llm_processor)
                    ext_result = llm_pipeline.extract(
                        text=cleaned_text,
                        filename=filename,
                        rule=rule,
                        pre_extracted_entities=pre_extracted_entities
                    )
                    if ext_result.success and ext_result.data:
                        response_dict = ext_result.data
                        extraction_method = "Ollama (IA)"
                    else:
                        msg_fallback = f"⚠️ Falha na extração LLM ({ext_result.alerts}). Alternando para Regex (Sem IA) neste arquivo..."
                        if on_progress: on_progress(f"[{filename}] {msg_fallback}")
                        from backend.engine.extractors.deterministic.pipeline import DeterministicPipeline
                        det_pipeline = DeterministicPipeline()
                        ext_result = det_pipeline.extract(text=cleaned_text, filename=filename)
                        response_dict = ext_result.data
                        extraction_method = "Regex (Sem IA)"
                except Exception as llm_err:
                    msg_fallback = f"⚠️ Erro inesperado no pipeline LLM ({llm_err}). Alternando para Regex (Sem IA) neste arquivo..."
                    if on_progress: on_progress(f"[{filename}] {msg_fallback}")
                    from backend.engine.extractors.deterministic.pipeline import DeterministicPipeline
                    det_pipeline = DeterministicPipeline()
                    ext_result = det_pipeline.extract(text=cleaned_text, filename=filename)
                    response_dict = ext_result.data
                    extraction_method = "Regex (Sem IA)"
            else:
                if on_progress: on_progress(f"[{filename}] ⚡ Processamento Ultra-Rápido 100% Regex (Sem IA)...")
                from backend.engine.extractors.deterministic.pipeline import DeterministicPipeline
                det_pipeline = DeterministicPipeline()
                ext_result = det_pipeline.extract(text=cleaned_text, filename=filename)
                response_dict = ext_result.data
                extraction_method = "Regex (Sem IA)"

            response_dict = self._normalize_response_dict(response_dict)
            response_dict["extraction_method"] = extraction_method

            # Conteúdo integral do histórico (armazenamento puro do texto limpo)
            final_content = clean_relint_text(cleaned_text)
            if "content" in response_dict:
                del response_dict["content"]

            # Motor 100% determinístico: garante que a síntese nunca fique vazia. Não se aplica
            # ao modo Ollama (IA) — lá, o próprio SummaryExtractor já é responsável por seu
            # guardrail interno; se mesmo assim vier vazio, fica em branco (ver ADR-0099).
            if extraction_method == "Regex (Sem IA)":
                if not response_dict.get("summary") or not str(response_dict.get("summary")).strip():
                    response_dict["summary"] = extract_fallback_summary(final_content, subject=response_dict.get("subject", ""))

            # date_of_fact/time_of_fact são sempre 100% determinísticos, independente do motor:
            # o cabeçalho do RELINT é formulaico o bastante para não precisar (nem se beneficiar)
            # de uma chamada à LLM (ver docs/proposals/eliminacao-pass1-legado.md).
            if not response_dict.get("date_of_fact"):
                response_dict["date_of_fact"] = extract_date_of_fact(final_content)
            if not response_dict.get("time_of_fact"):
                response_dict["time_of_fact"] = extract_time_of_fact(final_content)

            # SE MODO REGEX: Garante preenchimento de campos determinísticos adicionais
            if extraction_method == "Regex (Sem IA)":
                if not response_dict.get("subject"):
                    response_dict["subject"] = extract_subject_fallback(final_content, filename)

                if not response_dict.get("map_url") or not response_dict.get("coordinates"):
                    r_map, r_coords = resolve_coordinates_and_map_info(final_content)
                    response_dict["map_url"] = r_map
                    response_dict["coordinates"] = r_coords

                # Reclassifica com o 'subject' já preenchido pelo fallback acima: tanto o
                # LlmPipeline (Pass 3) quanto o DeterministicPipeline já chamam classify_bm_group
                # internamente, mas o DeterministicPipeline pode ter classificado com 'subject'
                # ainda vazio antes do fallback de 2 linhas acima ser aplicado — reclassificar
                # aqui pega esse ganho sem duplicar a chamada no caminho Ollama (IA), onde o
                # Pass 1 (SummaryExtractor) já resolve o subject antes do Passo 3 classificar.
                response_dict["bm_group"] = classify_bm_group(
                    filename=filename,
                    subject=response_dict.get("subject", ""),
                    content=final_content
                )

            # relint_type e main_fact são sempre 100% determinísticos/derivados, independente
            # do motor: classify_relint_type() segue o mesmo padrão de 2 camadas de
            # classify_bm_group(), e main_fact é o próprio resumo (mesma derivação que o
            # DeterministicPipeline já usa) — nenhum dos dois precisa de julgamento da LLM.
            # Guard "só preenche se vazio" em todos os 4 campos desta fase (aqui e nas duas
            # linhas de date_of_fact/time_of_fact acima): nenhum pass, LLM ou determinístico,
            # define esses 4 campos hoje — mas o guard garante que, se algum dia um deles
            # passar a resolvê-los, esta fase nunca sobrescreve nem perde tempo recalculando.
            if not response_dict.get("relint_type"):
                response_dict["relint_type"] = classify_relint_type(
                    filename=filename,
                    subject=response_dict.get("subject", ""),
                    content=final_content
                )
            if not response_dict.get("main_fact"):
                response_dict["main_fact"] = response_dict.get("summary", "")

            # 5. Filtragem e Enriquecimento Híbrido de Participantes (Sanitização + Anti-PM + Enriquecimento)
            from backend.engine.cleaners.text_cleaner import clean_person_name
            from backend.engine.extractors.deterministic.participants.negative_filters import is_blacklisted_name
            from backend.engine.extractors.deterministic.participants.role_detector import (

                detect_participation_role,
                extract_document_near_name
            )

            raw_participants = response_dict.get("participants", [])
            if not raw_participants and extraction_method == "Regex (Sem IA)":
                # Motor 100% determinístico: extração de participantes via regex.
                # Não se aplica ao modo Ollama (IA) — esse caminho fica sem extração de
                # participantes até um pass LLM dedicado ser construído (ver
                # docs/proposals/eliminacao-pass1-legado.md), sem cair de volta pro regex.
                from backend.engine.cleaners.text_cleaner import extract_fallback_participants
                raw_participants = extract_fallback_participants(final_content)
            from backend.engine.cleaners.name_parser import BrazilianNameParser

            filtered_participants = []
            seen_participant_names = set()
            pm_keywords = ["PM", "POLICIAL", "POLICIA", "TENENTE", "CAPITAO", "MAJOR", "CORONEL", "SUBTENENTE"]
            
            for p in raw_participants:
                p_dict = p if isinstance(p, dict) else (p.model_dump() if hasattr(p, "model_dump") else {})
                raw_p_name = p_dict.get("name", "")
                if isinstance(raw_p_name, bool) or not raw_p_name:
                    continue
                p_type = p_dict.get("participation_type", "") or ""
                
                # Executa o parser sintático nativo no nome do participante
                parsed = BrazilianNameParser.parse_person(str(raw_p_name))
                clean_p_name = parsed["name"]
                extracted_nick = parsed["nickname"]
                
                if extracted_nick and not p_dict.get("nickname"):
                    p_dict["nickname"] = extracted_nick
                    
                p_dict["name"] = clean_p_name
                
                is_pm = False
                if str(p_type) in ["Parte da Guarnição", "GUARNICAO", "Parte da Guarnicao"]:
                    is_pm = True
                
                upper_name = clean_p_name.upper()
                if any(kw in upper_name for kw in pm_keywords) or upper_name.startswith("SD ") or upper_name.startswith("SGT ") or upper_name.startswith("CB "):
                    is_pm = True
                    
                if not is_pm and clean_p_name and str(clean_p_name).strip():
                    filtered_participants.append(p_dict)
            # 6. Extração de Imagens do PDF (Galeria do RELINT)
            import re
            import hashlib
            stem_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', file_path.stem)
            stem_clean = re.sub(r'_+', '_', stem_clean).strip('_')
            safe_hash = hashlib.md5(file_path.name.encode('utf-8', errors='replace')).hexdigest()[:8]
            safe_folder_name = f"{stem_clean[:35]}_{safe_hash}"

            project_root = Path(__file__).resolve().parents[3]
            media_dir = project_root / "data" / "media" / safe_folder_name
            extracted_images = []
            try:
                if hasattr(self.file_parser, "extract_images"):
                    res = self.file_parser.extract_images(file_path, media_dir)
                    if isinstance(res, list):
                        extracted_images = res
            except Exception:
                extracted_images = []

            general_scene_images = []
            for img_info in extracted_images:
                path_str = img_info.get("file_path", "")
                caption_str = img_info.get("caption", "")
                if path_str:
                    general_scene_images.append({"path": path_str, "caption": caption_str})

            parsed_participants = []
            for p in filtered_participants:
                p_dict = p if isinstance(p, dict) else p.model_dump()
                p_dict["photo_path"] = None
                parsed_participants.append(p_dict)

            response_dict["participants"] = parsed_participants
            response_dict["images"] = general_scene_images

            # Instancia a entidade de domínio principal (RELINT)
            report_data = {
                "source_file": filename,
                **response_dict,
                "content": final_content
            }
            
            try:
                report = schema_model.model_validate(report_data)
            except Exception as model_err:
                if on_progress: on_progress(f"[{filename}] Aviso: IA não seguiu estritamente o Schema. Salvando com reconstrução segura.")
                report = schema_model.model_construct(_fields_set=None, **report_data)

            # Salva o RELINT no banco central — já grava pessoas/relint_participantes pros
            # participantes do report (ver SqliteRepo.save()). Não existe um segundo upsert
            # via person_repo aqui de propósito: havia um laço redundante que duplicava a
            # pessoa (chave calculada com o documento sem limpar pontuação, divergindo da
            # chave já salva acima) — ver auditoria de 2026-09.
            self.database_repo.save(report)

            if rule:
                self.processed_registry.register_processed(filename, rule.name, "confirmed")
            
            elapsed_time = time.time() - start_time
            if on_progress:
                on_progress(f"[{filename}] -> Concluído em {elapsed_time:.2f}s.")
            
            if on_success:
                on_success(report)

            # Transmite o evento SSE em tempo real para atualização instantânea dos clientes Web
            try:
                from backend.api.routers.events import broadcaster
                bm_str = report.bm_group.value if hasattr(report.bm_group, "value") else str(report.bm_group or "Outros")
                broadcaster.broadcast("relint_created", {
                    "id": str(report.id or ""),
                    "source_file": report.source_file or "",
                    "subject": report.subject or "",
                    "bm_group": bm_str,
                    "municipality": report.municipality or ""
                })
            except Exception:
                pass

            return report

        except Exception as e:
            error_msg = f"Erro ao processar {filename}: {str(e)}"
            if rule:
                self.processed_registry.register_processed(filename, rule.name, f"error: {str(e)}")
            if on_error:
                on_error(error_msg)
            return None
