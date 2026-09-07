import json
import collections
from datetime import datetime
import threading
from pathlib import Path
from queue import Queue, Empty
from typing import Callable, Optional, Set

from backend.engine.parsers.pdf_reader import PdfReader
from backend.engine.extractors.llm.ollama_client import OllamaClient
from backend.database.sqlite_repo import SqliteRepo
from backend.database.sqlite_person_repo import SqlitePersonRepo
from backend.task_manager.watcher.folder_watcher import FolderWatcher
from backend.task_manager.etl.etl_service import EtlService
from backend.engine.extractors.llm.rules.relint_rule import RelintRule
from backend.task_manager.registry.json_processed_registry import JsonProcessedRegistry
from desktop.controllers.web_app_manager import WebAppManager

class MainController:
    """
    Controlador principal que orquestra a lógica de negócio, a fila de processamento,
    as chamadas à LLM e o monitoramento de pastas (FolderWatcher).
    As interações com a interface gráfica (UI) são feitas por meio de callbacks injetados.
    """
    def __init__(self):
        # Configuração do Estado da Aplicação
        self.monitoring_path: str = ""
        self.is_monitoring: bool = False
        self.watcher: Optional[FolderWatcher] = None
        self.worker_thread: Optional[threading.Thread] = None

        # Desempenho e Estatísticas
        self.processing_queue: Queue = Queue()
        self.total_bytes: int = 0
        self.processed_bytes: int = 0
        self.processed_count: int = 0
        self.skipped_count: int = 0
        self.total_discovered: int = 0
        self.confirmed_homicides_count: int = 0
        self.rule_filtered_count: int = 0
        self.llm_sent_count: int = 0
        self.total_files_in_folder: int = 0
        self.current_filename: str = ""

        # Contadores específicos da sessão atual para o relatório estático
        self.session_confirmed_count: int = 0
        self.session_pre_filtered_count: int = 0
        self.session_post_llm_filtered_count: int = 0
        self.session_skipped_files: Set[str] = set()

        # Injeção de Dependências do Domínio e Aplicação (SQLite)
        self.pdf_reader = PdfReader()
        self.use_llm: bool = True
        self.llm_processor = OllamaClient()
        # Fixo em RelintRule (schema genérico) DE PROPÓSITO — não é um TODO pendente.
        # As 7 classes Rule especializadas (backend/engine/extractors/llm/rules/) NÃO devem ser
        # ativadas aqui: a extração de especialidade já é resolvida de forma independente por
        # classify_bm_group() + SpecialtyExtractor (ver ADR-0094/ADR-0095 em docs/adr/). Reativar essas
        # Rules reintroduziria o schema monolítico legado em paralelo ao pipeline multi-pass atual.
        self.active_rule = RelintRule()
        
        project_root = Path(__file__).resolve().parents[2]
        db_path = project_root / "data" / "relints.db"
        self.settings_path = project_root / "data" / "app_settings.json"
        self.db_repo = SqliteRepo(db_path)
        self.person_repo = SqlitePersonRepo(db_path)
        self.processed_registry = JsonProcessedRegistry(project_root / "data" / "processed_registry.json")
        
        self.etl_service = EtlService(
            file_parser=self.pdf_reader, 
            llm_processor=self.llm_processor, 
            database_repo=self.db_repo, 
            processed_registry=self.processed_registry,
            person_repo=self.person_repo,
            use_llm=self.use_llm
        )

        self.recent_logs = collections.deque(maxlen=200)

        # Gerenciador do servidor web
        self.web_app_manager = WebAppManager(log_callback=self.log)

        # Callbacks para atualizar a UI (devem ser configurados pela view)
        self.on_log_message: Optional[Callable[[str], None]] = None
        self.on_stats_updated: Optional[Callable[[], None]] = None

        # Registra a instância para acesso pelos endpoints da API REST
        from backend.api.dependencies import set_main_controller
        set_main_controller(self)

        # Carrega as configurações (inclusive a última pasta monitorada)
        self._load_settings()

    def _load_settings(self):
        try:
            if self.settings_path.exists():
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    last_path = data.get("last_monitoring_path", "")
                    if last_path and Path(last_path).exists() and Path(last_path).is_dir():
                        self.inspect_folder(last_path)
        except Exception as exc:
            self.log(f"Aviso ao carregar configurações: {exc}")

    def _save_settings(self):
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump({"last_monitoring_path": self.monitoring_path}, f, indent=2)
        except Exception as exc:
            self.log(f"Aviso ao salvar configurações: {exc}")

    def set_use_llm(self, use_llm: bool) -> bool:
        """
        Alterna a utilização da LLM (IA local) no serviço de ETL.
        Quando ativado (True), executa um teste de conexão em tempo real com o Ollama.
        Retorna True se ativado com sucesso ou False se falhar.
        """
        if use_llm:
            if hasattr(self.llm_processor, "check_connection"):
                self.log("🔍 Testando conexão com o Ollama local...")
                is_ok, msg = self.llm_processor.check_connection()
                if not is_ok:
                    self.log(f"⚠️ {msg}")
                    self.log("💡 Mantendo modo de extração rápida sem IA (Regex). Inicie o Ollama e tente ligar novamente.")
                    self.use_llm = False
                    if hasattr(self, "etl_service"):
                        self.etl_service.use_llm = False
                    return False
                else:
                    self.log(f"✅ {msg}")
            
            self.use_llm = True
            if hasattr(self, "etl_service"):
                self.etl_service.use_llm = True
            self.log("🟢 Modo de extração via IA Local (Ollama) ATIVADO.")
            return True
        else:
            self.use_llm = False
            if hasattr(self, "etl_service"):
                self.etl_service.use_llm = False
            self.log("⚡ Modo de extração rápida (Regex / Sem IA) ATIVADO.")
            return True

    def log(self, message: str):
        """Salva o log no buffer de histórico e dispara o callback de log se configurado."""
        from datetime import datetime
        now_str = datetime.now().strftime("%H:%M:%S")
        entry = f"[{now_str}] {message}"
        if hasattr(self, "recent_logs"):
            self.recent_logs.append(entry)
        if self.on_log_message:
            self.on_log_message(message)

    def update_ui(self):
        """Dispara o callback de atualização da UI."""
        if self.on_stats_updated:
            self.on_stats_updated()

    def reset_and_reprocess_all(self):
        """
        Interrompe o monitoramento, limpa o banco de dados SQLite, a tabela de pessoas,
        o registro de histórico e a pasta de mídias extraídas, e reinicia a leitura
        completa de todos os arquivos da pasta selecionada.
        """
        self.log("🔄 Iniciando Reset Completo da Base de Dados e Re-leitura de RELINTs...")
        if self.is_monitoring:
            self.stop_monitoring()

        # 1. Limpa o banco de dados relacional
        try:
            self.db_repo.clear_all()
            self.person_repo.clear_all()
            self.log("🧹 Banco de dados relacional (relints.db) zerado.")
        except Exception as exc:
            self.log(f"⚠️ Aviso ao limpar banco: {exc}")

        # 2. Limpa o registro de histórico
        try:
            self.processed_registry.clear()
            self.log("🧹 Histórico de controle de arquivos zerado.")
        except Exception as exc:
            self.log(f"⚠️ Aviso ao limpar registro de histórico: {exc}")

        # 3. Limpa arquivos de mídia salvos
        try:
            import shutil
            project_root = Path(__file__).resolve().parents[2]
            media_dir = project_root / "data" / "media"
            if media_dir.exists():
                shutil.rmtree(media_dir)
                media_dir.mkdir(parents=True, exist_ok=True)
                self.log("🧹 Galeria de mídias/fotos em data/media/ limpada.")
        except Exception as exc:
            self.log(f"⚠️ Aviso ao limpar pasta de mídias: {exc}")

        # 4. Reseta contadores e reinicia o monitoramento se houver pasta selecionada
        self.processed_count = 0
        self.total_discovered = 0
        self.total_bytes = 0
        self.processed_bytes = 0
        self.skipped_count = 0
        self.rule_filtered_count = 0
        self.llm_sent_count = 0
        self.total_files_in_folder = 0
        self.current_filename = ""
        self.update_ui()

        if self.monitoring_path and Path(self.monitoring_path).exists():
            self.log(f"🚀 Reiniciando varredura e leitura do zero em: {self.monitoring_path}")
            self.start_monitoring()
        else:
            self.log("⚠️ Selecione uma pasta para iniciar a re-leitura.")

    def set_monitoring_path(self, path: str):
        self.monitoring_path = path
        self.inspect_folder(path)

    def inspect_folder(self, path: str, async_exec: bool = True):
        """
        Inspeciona a pasta selecionada imediatamente ao escolher o diretório,
        calculando o total de PDFs e quantos já constam no banco de dados de forma assíncrona.
        """
        self.monitoring_path = path
        self._save_settings()

        def _do_inspect():
            try:
                folder = Path(path)
                if folder.exists() and folder.is_dir():
                    existing_pdfs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
                    total_files = len(existing_pdfs)
                    db_files_set = self.db_repo.get_all_source_filenames() if hasattr(self.db_repo, "get_all_source_filenames") else {r.source_file for r in self.db_repo.get_all()}
                    already_in_db = [f for f in existing_pdfs if f.name in db_files_set]
                    skipped = len(already_in_db)
                    
                    self.total_files_in_folder = total_files
                    self.skipped_count = skipped
                    self.total_discovered = max(0, total_files - skipped)
            except Exception as exc:
                self.log(f"Aviso ao inspecionar pasta: {exc}")
            finally:
                self.update_ui()

        if async_exec:
            threading.Thread(target=_do_inspect, daemon=True).start()
        else:
            _do_inspect()

    def toggle_monitoring(self):
        """Inicia ou para o monitoramento de diretório."""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """Inicializa o monitoramento de forma não-bloqueante em segundo plano para resposta instantânea."""
        self.is_monitoring = True
        self.current_filename = ""
        self.log("🚀 Comando de início recebido. Inicializando varredura de diretório em segundo plano...")
        self.update_ui()

        # Inicia a tarefa de varredura e consumo de fila em segundo plano (não-bloqueante)
        init_thread = threading.Thread(target=self._async_start_monitoring_task, daemon=True)
        init_thread.start()

    def _async_start_monitoring_task(self):
        """Tarefa executada em thread secundária para varredura e inicialização do monitor."""
        self.skipped_count = 0
        self.total_files_in_folder = 0
        self.rule_filtered_count = 0
        self.llm_sent_count = 0
        self.processed_bytes = 0
        
        self.session_confirmed_count = 0
        self.session_pre_filtered_count = 0
        self.session_post_llm_filtered_count = 0
        self.session_skipped_files = set()
        
        # Esvazia a fila de trabalhos pendentes
        while not self.processing_queue.empty():
            try:
                self.processing_queue.get_nowait()
            except Empty:
                break

        try:
            folder = Path(self.monitoring_path)
            if not folder.exists() or not folder.is_dir():
                self.is_monitoring = False
                self.log(f"⚠️ Pasta de monitoramento inválida: {self.monitoring_path}")
                self.update_ui()
                return

            existing_pdfs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
            self.total_files_in_folder = len(existing_pdfs)

            to_process_pdfs = []
            
            # Otimização O(1): busca em memória dos arquivos já cadastrados
            db_files_set = self.db_repo.get_all_source_filenames() if hasattr(self.db_repo, "get_all_source_filenames") else {r.source_file for r in self.db_repo.get_all()}
            all_registry_records = self.processed_registry.get_all_records()
            to_remove_from_registry = []

            for pdf_file in existing_pdfs:
                if not self.is_monitoring:
                    return

                in_db = pdf_file.name in db_files_set
                
                if not in_db:
                    if pdf_file.name in all_registry_records:
                        to_remove_from_registry.append(pdf_file.name)
                else:
                    self.skipped_count += 1
                    self.session_skipped_files.add(pdf_file.name)
                    continue

                to_process_pdfs.append(pdf_file)
                try:
                    self.total_bytes += pdf_file.stat().st_size
                except Exception:
                    pass
                self.processing_queue.put(pdf_file)

            if to_remove_from_registry:
                if hasattr(self.processed_registry, "remove_records_bulk"):
                    self.processed_registry.remove_records_bulk(to_remove_from_registry, self.active_rule.name)
                else:
                    for fn in to_remove_from_registry:
                        self.processed_registry.remove_record(fn, self.active_rule.name)
            
            self.total_discovered = len(to_process_pdfs)
            self.update_ui()
            
            if existing_pdfs:
                self.log("=" * 60)
                self.log(f">> Varredura inicial concluída em: {self.monitoring_path}")
                self.log(f">> Encontrados {len(existing_pdfs)} arquivos PDF.")
                self.log(f">> [OK] {self.skipped_count} arquivos já analisados pulados.")
                self.log(f">> [FILA] {self.total_discovered} novos arquivos para IA.")
                self.log("=" * 60)

            self.watcher = FolderWatcher(folder_path=folder, callback=self.on_pdf_detected)
            self.watcher.start()
            
            self.worker_thread = threading.Thread(target=self.process_queue_worker, daemon=True)
            self.worker_thread.start()
            
            self.log("Serviço de monitoramento de diretório INICIADO.")
            self.update_ui()
            
        except Exception as e:
            self.is_monitoring = False
            self.log(f"Erro ao iniciar monitoramento: {e}")
            self.update_ui()

    def stop_monitoring(self):
        """Interrompe o monitoramento de diretório e esvazia a fila de leitura imediatamente."""
        self.is_monitoring = False
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
        
        # Esvazia a fila pendente para pausar a leitura de imediato
        try:
            with self.processing_queue.mutex:
                self.processing_queue.queue.clear()
        except Exception:
            pass

        # Aguarda a finalização limpa da thread trabalhadora se ainda estiver rodando
        if hasattr(self, "worker_thread") and self.worker_thread and self.worker_thread.is_alive():
            try:
                self.worker_thread.join(timeout=0.3)
            except Exception:
                pass
            self.worker_thread = None

        self.current_filename = ""
        self.update_ui()
        self.log("⏸️ Serviço de monitoramento e fila de leitura PARADOS imediatamente.")

    def on_pdf_detected(self, file_path: Path):
        """Callback acionado pelo FolderWatcher ao identificar novo PDF."""
        in_db = self.db_repo.exists_by_source_file(file_path.name)
        
        if not in_db:
            self.processed_registry.remove_record(file_path.name, self.active_rule.name)
        else:
            self.skipped_count += 1
            self.session_skipped_files.add(file_path.name)
            self.log(f"[{file_path.name}] Já cadastrado no banco relints.json. Pulando.")
            self.update_ui()
            return


        self.log(f"Novo arquivo detectado pelo monitor: {file_path.name}")
        self.total_discovered += 1
        self.total_files_in_folder += 1
        try:
            self.total_bytes += file_path.stat().st_size
        except Exception:
            pass
        self.processing_queue.put(file_path)
        self.update_ui()

    def process_queue_worker(self):
        """Consome a fila de arquivos PDF executando o ETL em uma thread."""
        while self.is_monitoring:
            try:
                file_path = self.processing_queue.get(timeout=1.0)
            except Empty:
                continue

            self.current_filename = file_path.name
            try:
                current_file_size = file_path.stat().st_size
            except Exception:
                current_file_size = 0
                
            self.update_ui()
            
            self.etl_service.process_file(
                file_path=file_path,
                rule=self.active_rule,
                on_progress=self.log,
                on_error=self.log,
                on_success=self.increment_confirmed,
                on_filtered=self.increment_filtered,
                on_sent_to_llm=self.increment_llm_sent,
                on_llm_disconnected=self.handle_llm_disconnection
            )
            
            self.processed_count += 1
            self.processed_bytes += current_file_size
            self.current_filename = ""
            self.update_ui()
            self.processing_queue.task_done()

    def handle_llm_disconnection(self, reason: str = ""):
        """
        Trata a resposta demorada ou indisponibilidade pontual do Ollama no arquivo atual.
        Realiza o fallback gracioso para Regex sem desligar a chave global de IA do monitoramento.
        """
        self.log(f"⚠️ [AVISO IA] Resposta demorada do Ollama no arquivo atual. Efetuando leitura via Regex (Sem IA) para continuar o fluxo.")

    def increment_confirmed(self, report):
        self.confirmed_homicides_count += 1
        self.session_confirmed_count += 1
        self.update_ui()

    def increment_filtered(self, filename: str):
        self.rule_filtered_count += 1
        status = self.processed_registry.get_all_records().get(filename, {}).get(self.active_rule.name)
        if status == "filtered_pre_llm":
            self.session_pre_filtered_count += 1
        elif status == "filtered_post_llm":
            self.session_post_llm_filtered_count += 1
        self.update_ui()

    def increment_llm_sent(self, filename: str):
        self.llm_sent_count += 1
        self.update_ui()

    def reprocess_file_history(self, filename: str, rule_name: str):
        """Limpa arquivo do banco e histórico e reprocessa imediatamente o PDF especificado."""
        self.processed_registry.remove_record(filename, rule_name)
        deleted = self.db_repo.delete_by_source_file(filename)
        if deleted:
            self.log(f"[{filename}] Removido do banco de dados para reprocessamento.")
            if self.confirmed_homicides_count > 0:
                self.confirmed_homicides_count -= 1
            if self.session_confirmed_count > 0:
                self.session_confirmed_count -= 1

        if filename in self.session_skipped_files:
            self.session_skipped_files.discard(filename)
            if self.skipped_count > 0:
                self.skipped_count -= 1

        if self.monitoring_path:
            file_path = Path(self.monitoring_path) / filename
            if file_path.exists():
                if self.is_monitoring:
                    self.log(f"[{filename}] Adicionado novamente à fila de monitoramento.")
                    self.total_discovered += 1
                    try:
                        self.total_bytes += file_path.stat().st_size
                    except Exception:
                        pass
                    self.processing_queue.put(file_path)
                    self.update_ui()
                else:
                    self.log(f"🚀 Reprocessando imediatamente o arquivo: {filename}...")
                    def _reprocess_job():
                        self.current_filename = filename
                        self.update_ui()
                        self.etl_service.process_file(
                            file_path=file_path,
                            rule=self.active_rule,
                            on_progress=self.log,
                            on_error=self.log,
                            on_success=self.increment_confirmed,
                            on_filtered=self.increment_filtered,
                            on_sent_to_llm=self.increment_llm_sent,
                            on_llm_disconnected=self.handle_llm_disconnection
                        )
                        self.current_filename = ""
                        self.processed_count += 1
                        self.update_ui()
                        self.log(f"✅ Reprocessamento de {filename} concluído com sucesso!")

                    threading.Thread(target=_reprocess_job, daemon=True).start()
            else:
                self.log(f"⚠️ Arquivo {filename} não encontrado no diretório: {self.monitoring_path}")
        else:
            self.log(f"⚠️ Selecione um diretório para reprocessar {filename}.")
            
        self.update_ui()

    def open_web_dashboard(self) -> None:
        """Abre o Painel Web (FastAPI + SPA) no navegador padrão."""
        self.web_app_manager.open()

    def close_web_dashboard(self) -> None:
        """Encerra o servidor web."""
        self.web_app_manager.close()

    def destroy(self) -> None:
        """Libera recursos ao fechar a aplicação."""
        if self.is_monitoring and self.watcher:
            self.watcher.stop()
        self.web_app_manager.destroy()
