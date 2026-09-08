import sys
import time
import collections
import threading
import subprocess
import webbrowser
import socket
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para garantir imports absolutos corretos
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QMessageBox, QFileDialog,
    QScrollArea, QFrame, QSplitter, QProgressBar,
    QSystemTrayIcon, QMenu,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import (
    QTextCursor, QCloseEvent, QPainter, QPen, QColor,
    QFont, QIcon, QPixmap, QTextCharFormat, QAction
)

from desktop.controllers.main_controller import MainController
from backend.api.dependencies import get_main_controller

# --- Constantes de Cores e Estilo Minimalista Escuro ---
BG = "#0f0f10"
CARD = "#18181b"
CARD_HOVER = "#202024"
BORDER = "#27272a"
BORDER_SUBTLE = "#333338"
BORDER_FOCUS = "#52525b"
WHITE = "#fafafa"
GREY = "#a1a1aa"
MUTED = "#71717a"

EMERALD = "#10b981"
TEAL = "#14b8a6"
AMBER = "#f59e0b"
RED = "#ef4444"

# --- Estilos de Botões Reutilizáveis com :hover e :pressed ---
BTN_SECONDARY_STYLE = """
QPushButton {
    background-color: #27272a;
    color: #e4e4e7;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #3f3f46;
    border-color: #71717a;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #18181b;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

BTN_PRIMARY_START_STYLE = """
QPushButton {
    background-color: #10b981;
    color: #ffffff;
    border: 1px solid #059669;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #059669;
    border-color: #10b981;
}
QPushButton:pressed {
    background-color: #047857;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

BTN_PRIMARY_PAUSE_STYLE = """
QPushButton {
    background-color: #27272a;
    color: #fbbf24;
    border: 1px solid #78350f;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #3f3f46;
    color: #fef08a;
    border-color: #d97706;
}
QPushButton:pressed {
    background-color: #18181b;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

BTN_LLM_ACTIVE_STYLE = """
QPushButton {
    background-color: #142e23;
    color: #6ee7b7;
    border: 1px solid #047857;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #1d4334;
    border-color: #10b981;
    color: #a7f3d0;
}
QPushButton:pressed {
    background-color: #0f231b;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

BTN_LLM_INACTIVE_STYLE = """
QPushButton {
    background-color: #27272a;
    color: #a1a1aa;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #3f3f46;
    border-color: #71717a;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #18181b;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

BTN_DASHBOARD_START_STYLE = """
QPushButton {
    background-color: #182235;
    color: #93c5fd;
    border: 1px solid #1d4ed8;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #1e2c45;
    border-color: #3b82f6;
    color: #bfdbfe;
}
QPushButton:pressed {
    background-color: #111a29;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

BTN_DASHBOARD_STOP_STYLE = """
QPushButton {
    background-color: #2d1619;
    color: #fca5a5;
    border: 1px solid #991b1b;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #3c1e22;
    border-color: #dc2626;
    color: #fecaca;
}
QPushButton:pressed {
    background-color: #200f12;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

BTN_QUIT_STYLE = """
QPushButton {
    background-color: #27272a;
    color: #f87171;
    border: 1px solid #7f1d1d;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #450a0a;
    border-color: #dc2626;
    color: #fecaca;
}
QPushButton:pressed {
    background-color: #200f12;
}
"""

BTN_SERVICE_START_STYLE = """
QPushButton {
    background-color: #27272a;
    color: #e4e4e7;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    font-weight: 600;
    font-size: 11px;
}
QPushButton:hover {
    background-color: #142e23;
    border-color: #047857;
    color: #6ee7b7;
}
QPushButton:pressed {
    background-color: #18181b;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

BTN_SERVICE_STOP_STYLE = """
QPushButton {
    background-color: #2d1619;
    color: #fca5a5;
    border: 1px solid #7f1d1d;
    border-radius: 6px;
    font-weight: 600;
    font-size: 11px;
}
QPushButton:hover {
    background-color: #3c1e22;
    border-color: #b91c1c;
    color: #fecaca;
}
QPushButton:pressed {
    background-color: #200f12;
}
QPushButton:disabled {
    background-color: #1c1c1f;
    color: #52525b;
    border-color: #27272a;
}
"""

QSS = f"""
QMainWindow, QWidget {{
    background-color: {BG};
    color: {WHITE};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {BG};
}}
QTabBar::tab {{
    background: {CARD};
    color: {GREY};
    padding: 10px 22px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    min-width: 140px;
    font-weight: 600;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    background: {BG};
    color: {WHITE};
    border-bottom: 2px solid {EMERALD};
}}
QTabBar::tab:hover {{
    color: {WHITE};
    background: #202024;
}}
QLineEdit {{
    background-color: #131316;
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px;
    color: {WHITE};
}}
QLineEdit:focus {{
    border-color: {BORDER_FOCUS};
}}
QLineEdit:disabled {{
    background-color: #18181b;
    color: #52525b;
}}
QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background-color: #131316;
    color: {WHITE};
    text-align: center;
    font-weight: 600;
    font-size: 11px;
}}
QProgressBar::chunk {{
    border-radius: 5px;
    background-color: {EMERALD};
}}
QTextEdit {{
    background-color: #09090b;
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: #d4d4d8;
    font-family: Consolas, 'Cascadia Code', monospace;
    font-size: 12px;
    padding: 10px;
    line-height: 1.4;
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {CARD};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #3f3f46;
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: #52525b;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QFrame[card="true"] {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
"""


def format_display_filename(filename: str, max_chars: int = 28) -> str:
    """Extrai com precisão apenas o número/código do RELINT para exibição fixa e concisa."""
    if not filename:
        return ""
    import re
    stem = Path(filename).stem
    match = re.search(r"(RELINT[\s_-]*N?º?[\s_-]*\d+(?:[/-]\d+)?)", stem, re.IGNORECASE)
    if match:
        return match.group(1).replace("_", " ").upper()
    num_match = re.search(r"(\d+[-/]\d+|\d+)", stem)
    if num_match:
        return f"RELINT Nº {num_match.group(1)}"
    if len(filename) <= max_chars:
        return filename
    return f"{stem[:max_chars-6]}...{Path(filename).suffix}"


def create_app_icon() -> QIcon:
    """Cria um ícone vetorial nítido para a aplicação e bandeja do sistema."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#18181b"))
    painter.setPen(QPen(QColor("#27272a"), 2))
    painter.drawEllipse(2, 2, 28, 28)
    painter.setBrush(QColor(EMERALD))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(10, 10, 12, 12)
    painter.end()
    return QIcon(pixmap)


def is_port_in_use(port: int) -> bool:
    """Verifica de forma segura se há algum processo ouvindo na porta informada via socket, sem usar processos externos."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            # Retorna 0 se a conexão for bem sucedida (porta em uso)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False


def kill_port_process(port: int):
    """Encerra com segurança e de forma forçada qualquer processo escutando na porta informada."""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        output = subprocess.check_output(
            f"netstat -ano | findstr :{port}",
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
            startupinfo=startupinfo,
        )
        pids_to_kill = set()
        for line in output.strip().splitlines():
            if "LISTENING" in line:
                parts = line.strip().split()
                pid = parts[-1]
                if pid and pid != "0":
                    pids_to_kill.add(pid)
        for pid in pids_to_kill:
            subprocess.call(
                ["taskkill", "/F", "/T", "/PID", pid],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo,
            )
    except Exception:
        pass


class StatsEmitter(QObject):
    """Emissor para transmissão thread-safe de atualizações de estatísticas e estados de carregamento para a UI."""
    stats_updated = pyqtSignal()
    busy_changed = pyqtSignal(str, bool)


class ServiceWatcher(QObject):
    """Monitor em background para checar status dos servidores sem travar a UI principal."""
    status_checked = pyqtSignal(bool, bool)

    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self._running = True

    def check_once(self):
        is_be = self.controller.web_app_manager.is_running or is_port_in_use(8000)
        is_fe = is_port_in_use(5173)
        self.status_checked.emit(is_be, is_fe)

    def start_polling(self):
        def _loop():
            while self._running:
                try:
                    self.check_once()
                except Exception:
                    pass
                time.sleep(2.5)
        threading.Thread(target=_loop, daemon=True).start()

    def stop(self):
        self._running = False


def make_card(layout: QVBoxLayout | QHBoxLayout) -> QFrame:
    """Cria um QFrame estilizado como card de dashboard."""
    card = QFrame()
    card.setProperty("card", True)
    card.setLayout(layout)
    return card


class MainWindow(QMainWindow):
    """Janela principal do Painel de Controle ReadRelint em PyQt6 com alta performance."""

    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.frontend_process = None
        self._is_quitting = False

        # Cache de status dos serviços
        self._cached_backend_running = False
        self._cached_frontend_running = False

        # Fila de Logs desacoplada para evitar bloqueios no QTextEdit (Batching a 12.5 FPS)
        self._log_queue = collections.deque(maxlen=2000)

        # Rastreamento de ações em background (loading e verificações no console)
        self._active_busy_reasons = {}
        self._is_transitioning_backend = False
        self._is_transitioning_frontend = False
        self._is_transitioning_dashboard = False

        # Configuração de Sinais Thread-Safe
        self._stats_emitter = StatsEmitter()
        self._stats_emitter.stats_updated.connect(self._update_etl_stats)
        self._stats_emitter.busy_changed.connect(self._on_busy_changed)

        self.setWindowTitle("ReadRelint • Painel de Controle")
        self.setWindowIcon(create_app_icon())
        self.setMinimumSize(980, 680)
        self.resize(1080, 720)

        # Injeta callbacks no controller compartilhado
        self.controller.on_log_message = self._queue_log
        self.controller.on_stats_updated = self._emit_stats

        # Constrói UI e aplica estilo
        self._build_ui()
        self.setStyleSheet(QSS)

        # Configuração da Bandeja do Sistema (System Tray)
        self._setup_system_tray()

        # Typewriter Inteligente no console de logs (16ms / ~60 FPS)
        self._typing_current_line = ""
        self._typing_char_idx = 0
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._typewriter_step)
        self._typing_timer.start(16)

        # Timer animador de spinner para indicar leitura ativa (90ms)
        self._spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._spinner_idx = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.timeout.connect(self._animate_reading_spinner)
        self._spinner_timer.start(90)

        # Monitor de serviços assíncrono em background (Zero subprocessos na main thread)
        self._service_watcher = ServiceWatcher(self.controller)
        self._service_watcher.status_checked.connect(self._on_service_status_received)
        self._service_watcher.start_polling()

        # Inicializa estado visual inicial
        self._set_busy("Iniciando ambiente & verificando serviços...", True)
        self._update_etl_stats()
        self._queue_log("Painel de controle iniciado com sucesso.")
        self._initial_llm_check()

    def _setup_system_tray(self):
        """Configura o ícone e menu de contexto na bandeja do sistema."""
        self._tray_icon = QSystemTrayIcon(create_app_icon(), self)
        tray_menu = QMenu()

        # Instancia ações QAction explicitamente para evitar NoneType no PyQt6
        action_open = QAction("📂  Abrir Painel", self)
        action_open.triggered.connect(self.show_and_raise)
        tray_menu.addAction(action_open)

        action_dashboard = QAction("🌐  Abrir Dashboard Web", self)
        action_dashboard.triggered.connect(self._toggle_dashboard_unified)
        tray_menu.addAction(action_dashboard)

        tray_menu.addSeparator()

        action_quit = QAction("⛔  Encerrar Todos os Serviços & Sair", self)
        action_quit.triggered.connect(self._force_quit_app)
        tray_menu.addAction(action_quit)

        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._on_tray_activated)
        self._tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_and_raise()

    def show_and_raise(self):
        """Restaura e foca a janela a partir da bandeja do sistema."""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(8)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab_operation(), "🚀  Operação & Leitura")
        self.tabs.addTab(self._build_tab_reports_and_services(), "📋  Serviços & Relatórios")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        root_layout.addWidget(self.tabs)

    # =========================================================================
    # ABA 1: Operação & Leitura (Split View em 2 Colunas)
    # =========================================================================

    def _build_tab_operation(self) -> QWidget:
        tab = QWidget()
        main_layout = QHBoxLayout(tab)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(16)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Coluna Esquerda: Controle, Barras e Ações com Largura Fixa Estável ---
        left_pane = QWidget()
        left_pane.setFixedWidth(410)
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(12)

        # 1. Card: Seleção de Pasta & Ações de Leitura e Reset
        folder_card_layout = QVBoxLayout()
        folder_card_layout.setContentsMargins(14, 12, 14, 12)
        folder_card_layout.setSpacing(8)

        lbl_folder_title = QLabel("Diretório de Monitoramento dos RELINTs")
        lbl_folder_title.setStyleSheet("font-weight: 700; color: #ffffff;")

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self._txt_path = QLineEdit(
            self.controller.monitoring_path or "Nenhuma pasta selecionada"
        )
        self._txt_path.setReadOnly(True)
        self._txt_path.setPlaceholderText("Selecione a pasta dos PDFs...")

        self._btn_browse = QPushButton("📁  Procurar")
        self._btn_browse.setFixedWidth(96)
        self._btn_browse.setFixedHeight(32)
        self._btn_browse.setStyleSheet(BTN_SECONDARY_STYLE)
        self._btn_browse.clicked.connect(self._pick_directory)

        path_row.addWidget(self._txt_path)
        path_row.addWidget(self._btn_browse)

        self._btn_monitoring = QPushButton("▶  Iniciar Leitura & Monitoramento")
        self._btn_monitoring.setFixedHeight(38)
        self._btn_monitoring.setStyleSheet(BTN_PRIMARY_START_STYLE)
        self._btn_monitoring.clicked.connect(self._toggle_etl_monitoring)

        self._btn_reset = QPushButton("🧹  Limpar Base & Re-processar Tudo")
        self._btn_reset.setFixedHeight(28)
        self._btn_reset.setStyleSheet(BTN_SECONDARY_STYLE)
        self._btn_reset.clicked.connect(self._reset_etl_data)

        folder_card_layout.addWidget(lbl_folder_title)
        folder_card_layout.addLayout(path_row)
        folder_card_layout.addWidget(self._btn_monitoring)
        folder_card_layout.addWidget(self._btn_reset)
        left_layout.addWidget(make_card(folder_card_layout))

        # 2. Card: Barras Lineares Tradicionais de Progresso & Loading Ativo
        bars_card_layout = QVBoxLayout()
        bars_card_layout.setContentsMargins(14, 12, 14, 12)
        bars_card_layout.setSpacing(8)

        lbl_bars_title = QLabel("Progresso da Leitura")
        lbl_bars_title.setStyleSheet("font-weight: 700; color: #ffffff;")
        bars_card_layout.addWidget(lbl_bars_title)

        # Barra 1: Total da Pasta
        row_bar1_hdr = QHBoxLayout()
        lbl_bar1_title = QLabel("Total da Pasta:")
        lbl_bar1_title.setStyleSheet("font-size: 11px; color: #a1a1aa; font-weight: 600;")
        self._lbl_bar1_counts = QLabel("0 / 0 PDFs")
        self._lbl_bar1_counts.setStyleSheet("font-size: 11px; color: #e4e4e7; font-weight: 700;")
        row_bar1_hdr.addWidget(lbl_bar1_title)
        row_bar1_hdr.addStretch()
        row_bar1_hdr.addWidget(self._lbl_bar1_counts)

        self._bar_general = QProgressBar()
        self._bar_general.setFixedHeight(18)
        self._bar_general.setTextVisible(True)
        self._bar_general.setValue(0)

        # Barra 2: Sessão Atual
        row_bar2_hdr = QHBoxLayout()
        lbl_bar2_title = QLabel("Sessão Atual (Novos):")
        lbl_bar2_title.setStyleSheet("font-size: 11px; color: #a1a1aa; font-weight: 600;")
        self._lbl_bar2_counts = QLabel("0 / 0 Novos")
        self._lbl_bar2_counts.setStyleSheet("font-size: 11px; color: #e4e4e7; font-weight: 700;")
        row_bar2_hdr.addWidget(lbl_bar2_title)
        row_bar2_hdr.addStretch()
        row_bar2_hdr.addWidget(self._lbl_bar2_counts)

        self._bar_session = QProgressBar()
        self._bar_session.setFixedHeight(18)
        self._bar_session.setTextVisible(True)
        self._bar_session.setValue(0)

        # Barra de Loading Ativo Indeterminado (Estilo Web)
        self._bar_reading_active = QProgressBar()
        self._bar_reading_active.setFixedHeight(4)
        self._bar_reading_active.setTextVisible(False)
        self._bar_reading_active.setRange(0, 0)
        
        # Preserva o espaço de 4px no layout mesmo quando oculta, evitando pulos na tela
        sp = self._bar_reading_active.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self._bar_reading_active.setSizePolicy(sp)

        self._bar_reading_active.setStyleSheet("""
        QProgressBar {
            background-color: #18181b;
            border: none;
            border-radius: 2px;
        }
        QProgressBar::chunk {
            background-color: #10b981;
            border-radius: 2px;
        }
        """)
        self._bar_reading_active.hide()

        # Status do arquivo atual em caixa de dimensões fixas (sem movimento de layout)
        self._lbl_current = QLabel("⏸️ Fila de leitura pausada")
        self._lbl_current.setStyleSheet(
            f"background-color: #131316; border: 1px solid {BORDER}; border-radius: 6px; color: {GREY}; font-weight: 700; font-size: 12px; padding: 4px 8px;"
        )
        self._lbl_current.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_current.setFixedHeight(34)

        bars_card_layout.addLayout(row_bar1_hdr)
        bars_card_layout.addWidget(self._bar_general)
        bars_card_layout.addLayout(row_bar2_hdr)
        bars_card_layout.addWidget(self._bar_session)
        bars_card_layout.addWidget(self._bar_reading_active)
        bars_card_layout.addWidget(self._lbl_current)

        left_layout.addWidget(make_card(bars_card_layout))

        # 3. Card: Ações Rápidas do Sistema (Abaixo das Barras)
        actions_card_layout = QVBoxLayout()
        actions_card_layout.setContentsMargins(14, 12, 14, 12)
        actions_card_layout.setSpacing(10)

        lbl_actions_title = QLabel("Ações Rápidas & Serviços")
        lbl_actions_title.setStyleSheet("font-weight: 700; color: #ffffff;")

        # Linha 1: Modo IA & Backend FastAPI Dedicado
        actions_row_1 = QHBoxLayout()
        actions_row_1.setSpacing(10)

        # Botão Modo IA
        self._btn_llm_toggle = QPushButton("⚡ IA (Ollama): Ativa")
        self._btn_llm_toggle.setFixedHeight(36)
        self._btn_llm_toggle.setStyleSheet(BTN_LLM_ACTIVE_STYLE)
        self._btn_llm_toggle.clicked.connect(self._toggle_llm_mode)

        actions_row_1.addWidget(self._btn_llm_toggle)

        # Linha 2: Dashboard Web Unificado
        self._btn_open_dashboard = QPushButton("🌐  Iniciar & Abrir Dashboard Completo")
        self._btn_open_dashboard.setFixedHeight(36)
        self._btn_open_dashboard.setStyleSheet(BTN_DASHBOARD_START_STYLE)
        self._btn_open_dashboard.clicked.connect(self._toggle_dashboard_unified)

        # Botão de Encerramento Total posicionado logo abaixo do botão do Dashboard
        btn_quit_all = QPushButton("⛔  Encerrar Todos os Serviços & Sair")
        btn_quit_all.setFixedHeight(34)
        btn_quit_all.setStyleSheet(BTN_QUIT_STYLE)
        btn_quit_all.setToolTip("Encerra todos os servidores (FastAPI, SvelteKit, Monitor) e fecha a aplicação completamente")
        btn_quit_all.clicked.connect(self._force_quit_app)

        actions_card_layout.addWidget(lbl_actions_title)
        actions_card_layout.addLayout(actions_row_1)
        actions_card_layout.addWidget(self._btn_open_dashboard)
        actions_card_layout.addWidget(btn_quit_all)
        left_layout.addWidget(make_card(actions_card_layout))

        left_layout.addStretch()

        # --- Coluna Direita: Console de Leitura em Tempo Real ---
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(10)

        logs_header = QHBoxLayout()
        logs_header.setSpacing(10)

        lbl_logs_title = QLabel("🖥  Console de Leitura em Tempo Real")
        lbl_logs_title.setStyleSheet("font-weight: 700; font-size: 14px; color: #ffffff;")

        # Badge com spinner de status no cabeçalho do console
        self._lbl_console_status = QLabel("")
        self._lbl_console_status.setStyleSheet(
            "font-size: 11px; color: #38bdf8; font-weight: 700; background: #0c4a6e; "
            "border: 1px solid #0284c7; padding: 2px 8px; border-radius: 4px;"
        )
        self._lbl_console_status.hide()

        btn_clear_logs = QPushButton("Limpar")
        btn_clear_logs.setFixedSize(68, 28)
        btn_clear_logs.setStyleSheet(BTN_SECONDARY_STYLE)
        btn_clear_logs.clicked.connect(self._clear_logs)

        logs_header.addWidget(lbl_logs_title)
        logs_header.addWidget(self._lbl_console_status)
        logs_header.addStretch()
        logs_header.addWidget(btn_clear_logs)

        # Barra de progresso indeterminada fina no topo do console de logs
        self._bar_console_loading = QProgressBar()
        self._bar_console_loading.setFixedHeight(3)
        self._bar_console_loading.setTextVisible(False)
        self._bar_console_loading.setRange(0, 0)
        self._bar_console_loading.setStyleSheet("""
        QProgressBar {
            background-color: #18181b;
            border: none;
            border-radius: 1px;
        }
        QProgressBar::chunk {
            background-color: #38bdf8;
            border-radius: 1px;
        }
        """)
        self._bar_console_loading.hide()

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)

        right_layout.addLayout(logs_header)
        right_layout.addWidget(self._bar_console_loading)
        right_layout.addWidget(self._log_view)

        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

        main_layout.addWidget(splitter)
        return tab

    # =========================================================================
    # ABA 2: Serviços & Relatórios
    # =========================================================================

    def _build_tab_reports_and_services(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        # 1. Seção: Diagnóstico dos Serviços Ativos
        services_card_layout = QVBoxLayout()
        services_card_layout.setContentsMargins(14, 12, 14, 12)
        services_card_layout.setSpacing(10)

        lbl_serv_title = QLabel("Diagnóstico de Serviços & Infraestrutura")
        lbl_serv_title.setStyleSheet("font-weight: 700; color: #ffffff; font-size: 13px;")
        services_card_layout.addWidget(lbl_serv_title)

        serv_grid = QHBoxLayout()
        serv_grid.setSpacing(12)

        # Card 1: Backend FastAPI
        vbox_b = QVBoxLayout()
        vbox_b.addWidget(QLabel("Servidor FastAPI (API)"))
        self._lbl_backend_status = QLabel("● Parado")
        self._lbl_backend_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")
        vbox_b.addWidget(self._lbl_backend_status)
        
        self._btn_fastapi_toggle_tab2 = QPushButton("🚀 Iniciar API")
        self._btn_fastapi_toggle_tab2.setFixedHeight(28)
        self._btn_fastapi_toggle_tab2.setStyleSheet(BTN_SERVICE_START_STYLE)
        self._btn_fastapi_toggle_tab2.clicked.connect(self._toggle_fastapi_service)
        vbox_b.addWidget(self._btn_fastapi_toggle_tab2)
        
        serv_grid.addWidget(make_card(vbox_b))

        # Card 2: Frontend SvelteKit
        vbox_f = QVBoxLayout()
        vbox_f.addWidget(QLabel("Frontend (SvelteKit)"))
        self._lbl_frontend_status = QLabel("● Parado")
        self._lbl_frontend_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")
        vbox_f.addWidget(self._lbl_frontend_status)
        
        self._btn_svelte_toggle_tab2 = QPushButton("🚀 Iniciar Svelte")
        self._btn_svelte_toggle_tab2.setFixedHeight(28)
        self._btn_svelte_toggle_tab2.setStyleSheet(BTN_SERVICE_START_STYLE)
        self._btn_svelte_toggle_tab2.clicked.connect(self._toggle_sveltekit_service)
        vbox_f.addWidget(self._btn_svelte_toggle_tab2)
        
        serv_grid.addWidget(make_card(vbox_f))

        # Card Monitor / Pasta
        vbox_m = QVBoxLayout()
        vbox_m.addWidget(QLabel("Status do Monitor"))
        self._lbl_monitor_status = QLabel("● Inativo")
        self._lbl_monitor_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")
        self._lbl_folder_info = QLabel("Pasta: Nenhuma")
        self._lbl_folder_info.setStyleSheet(f"color: {GREY}; font-size: 11px;")
        vbox_m.addWidget(self._lbl_monitor_status)
        vbox_m.addWidget(self._lbl_folder_info)
        serv_grid.addWidget(make_card(vbox_m))

        services_card_layout.addLayout(serv_grid)
        layout.addWidget(make_card(services_card_layout))

        # 2. Seção: Histórico de Relatórios Processados
        reports_header = QHBoxLayout()
        lbl_rep_title = QLabel("Histórico de RELINTs Processados")
        lbl_rep_title.setStyleSheet("font-weight: 700; color: #ffffff; font-size: 13px;")

        btn_refresh_reports = QPushButton("🔄  Atualizar Lista")
        btn_refresh_reports.setFixedSize(120, 28)
        btn_refresh_reports.setStyleSheet(BTN_SECONDARY_STYLE)
        btn_refresh_reports.clicked.connect(self._refresh_reports_clicked)

        reports_header.addWidget(lbl_rep_title)
        reports_header.addStretch()
        reports_header.addWidget(btn_refresh_reports)
        layout.addLayout(reports_header)

        # Scroll com lista compacta de relatórios
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._reports_container = QWidget()
        self._reports_layout = QVBoxLayout(self._reports_container)
        self._reports_layout.setContentsMargins(4, 4, 4, 4)
        self._reports_layout.setSpacing(6)
        self._reports_layout.addStretch()

        scroll.setWidget(self._reports_container)
        layout.addWidget(scroll, stretch=1)

        return tab

    # =========================================================================
    # Ações e Lógica de Operações Não-Bloqueantes com Feedback de Loading
    # =========================================================================

    def _is_dashboard_running(self) -> bool:
        """Verifica de forma rápida e não bloqueante se o dashboard está ativo."""
        return self._cached_backend_running or self._cached_frontend_running

    def _stop_frontend_process(self):
        """Encerra o processo do frontend e garante que nenhum processo permaneça na porta 5173 sem travar a UI."""
        if self.frontend_process:
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                subprocess.call(
                    ["taskkill", "/F", "/T", "/PID", str(self.frontend_process.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    startupinfo=startupinfo,
                )
            except Exception:
                pass
            self.frontend_process = None
        else:
            kill_port_process(5173)
        self._cached_frontend_running = False

    def _toggle_dashboard_unified(self):
        """Inicia e abre o Dashboard no navegador, ou encerra os servidores se já estiver rodando."""
        if self._is_dashboard_running():
            self._btn_open_dashboard.setText("⏳  Encerrando Dashboard...")
            self._btn_open_dashboard.setEnabled(False)
            self._set_busy("Encerrando Dashboard Web...", True)
            QApplication.processEvents()

            def _async_stop():
                try:
                    if self.controller.web_app_manager.is_running:
                        self.controller.close_web_dashboard()
                    self._stop_frontend_process()
                finally:
                    self._cached_backend_running = False
                    self._cached_frontend_running = False
                    self._queue_log("⛔ Servidor Dashboard Web (API & SvelteKit) parado.")
                    self._set_busy("Encerrando Dashboard Web...", False)
                    self._stats_emitter.stats_updated.emit()
                    self._service_watcher.check_once()

            threading.Thread(target=_async_stop, daemon=True).start()
        else:
            self._btn_open_dashboard.setText("⏳  Iniciando Dashboard...")
            self._btn_open_dashboard.setEnabled(False)
            self._set_busy("Iniciando Dashboard Web (FastAPI + SvelteKit)...", True)
            QApplication.processEvents()

            def _async_start():
                try:
                    if not self.controller.web_app_manager.is_running:
                        self.controller.open_web_dashboard()
                        self._cached_backend_running = True
                        self._queue_log("🌐 Servidor Backend FastAPI iniciado.")

                    if not self._cached_frontend_running:
                        kill_port_process(5173)
                        frontend_dir = str(project_root / "frontend")
                        self._queue_log("🚀 Iniciando dev server do SvelteKit...")
                        try:
                            self.frontend_process = subprocess.Popen(
                                "npm run dev",
                                cwd=frontend_dir,
                                shell=True,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                creationflags=subprocess.CREATE_NO_WINDOW,
                            )
                            self._cached_frontend_running = True
                            self._queue_log("🟢 Servidor Frontend SvelteKit ativo em http://localhost:5173")
                        except Exception as exc:
                            self._queue_log(f"⚠️ Falha ao iniciar Frontend: {exc}")

                    time.sleep(0.6)
                    webbrowser.open("http://localhost:5173")
                    self._queue_log("🌐 Abrindo Dashboard no navegador: http://localhost:5173")
                finally:
                    self._set_busy("Iniciando Dashboard Web (FastAPI + SvelteKit)...", False)
                    self._stats_emitter.stats_updated.emit()
                    self._service_watcher.check_once()

            threading.Thread(target=_async_start, daemon=True).start()

    def _toggle_fastapi_service(self):
        """Inicia ou para exclusivamente o servidor backend FastAPI (:8000)."""
        is_running = self.controller.web_app_manager.is_running or is_port_in_use(8000) or self._cached_backend_running
        self._is_transitioning_backend = True
        
        if is_running:
            if hasattr(self, "_btn_fastapi_toggle_tab2"):
                self._btn_fastapi_toggle_tab2.setText("⏳ Parando...")
                self._btn_fastapi_toggle_tab2.setEnabled(False)
            self._set_busy("Parando servidor FastAPI (:8000)...", True)

            def _async_stop():
                try:
                    if self.controller.web_app_manager.is_running:
                        self.controller.close_web_dashboard()
                    kill_port_process(8000)
                finally:
                    self._cached_backend_running = False
                    self._is_transitioning_backend = False
                    self._queue_log("⛔ Servidor Backend FastAPI (:8000) encerrado.")
                    self._set_busy("Parando servidor FastAPI (:8000)...", False)
                    self._service_watcher.check_once()

            threading.Thread(target=_async_stop, daemon=True).start()
        else:
            if hasattr(self, "_btn_fastapi_toggle_tab2"):
                self._btn_fastapi_toggle_tab2.setText("⏳ Iniciando...")
                self._btn_fastapi_toggle_tab2.setEnabled(False)
            self._set_busy("Iniciando servidor FastAPI (:8000)...", True)

            def _async_start():
                try:
                    kill_port_process(8000)
                    self.controller.web_app_manager.start_background_silent()

                    # Aguarda o servidor estar de fato ouvindo na porta 8000 (máx 10 segundos)
                    for _ in range(40):
                        time.sleep(0.25)
                        if is_port_in_use(8000):
                            break

                    self._cached_backend_running = is_port_in_use(8000)
                    if self._cached_backend_running:
                        self._queue_log("🟢 Servidor Backend FastAPI ativo em http://localhost:8000")
                    else:
                        self._queue_log("⚠️ Timeout: servidor FastAPI não respondeu em 10s")
                except Exception as exc:
                    self._queue_log(f"❌ Erro ao iniciar FastAPI: {exc}")
                finally:
                    self._is_transitioning_backend = False
                    self._set_busy("Iniciando servidor FastAPI (:8000)...", False)
                    self._service_watcher.check_once()

            threading.Thread(target=_async_start, daemon=True).start()

    def _toggle_sveltekit_service(self):
        """Inicia ou para exclusivamente o servidor frontend SvelteKit (:5173)."""
        is_running = self._cached_frontend_running or is_port_in_use(5173)
        self._is_transitioning_frontend = True

        if is_running:
            if hasattr(self, "_btn_svelte_toggle_tab2"):
                self._btn_svelte_toggle_tab2.setText("⏳ Parando...")
                self._btn_svelte_toggle_tab2.setEnabled(False)
            self._set_busy("Parando servidor SvelteKit (:5173)...", True)
            
            def _async_stop():
                try:
                    self._stop_frontend_process()
                finally:
                    self._cached_frontend_running = False
                    self._is_transitioning_frontend = False
                    self._queue_log("⛔ Servidor Frontend SvelteKit (:5173) encerrado.")
                    self._set_busy("Parando servidor SvelteKit (:5173)...", False)
                    self._service_watcher.check_once()
            
            threading.Thread(target=_async_stop, daemon=True).start()
        else:
            if hasattr(self, "_btn_svelte_toggle_tab2"):
                self._btn_svelte_toggle_tab2.setText("⏳ Iniciando...")
                self._btn_svelte_toggle_tab2.setEnabled(False)
            self._set_busy("Iniciando servidor SvelteKit (:5173)...", True)

            def _async_start():
                try:
                    kill_port_process(5173)
                    frontend_dir = str(project_root / "frontend")
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    
                    self._queue_log("🚀 Iniciando dev server do SvelteKit...")
                    self.frontend_process = subprocess.Popen(
                        "npm run dev",
                        cwd=frontend_dir,
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        startupinfo=startupinfo,
                    )
                    
                    # Aguarda a porta 5173 responder (máx 15 segundos)
                    for _ in range(60):
                        time.sleep(0.25)
                        if is_port_in_use(5173):
                            break
                            
                    self._cached_frontend_running = is_port_in_use(5173)
                    if self._cached_frontend_running:
                        self._queue_log("🟢 Servidor Frontend SvelteKit ativo em http://localhost:5173")
                    else:
                        self._queue_log("⚠️ Timeout: SvelteKit não respondeu em 15s")
                except Exception as exc:
                    self._queue_log(f"❌ Erro ao iniciar SvelteKit: {exc}")
                finally:
                    self._is_transitioning_frontend = False
                    self._set_busy("Iniciando servidor SvelteKit (:5173)...", False)
                    self._service_watcher.check_once()
                    
            threading.Thread(target=_async_start, daemon=True).start()

    def _toggle_web_service(self):
        """Alterna a inicialização e encerramento unificados do FastAPI + SvelteKit."""
        self._toggle_dashboard_unified()

    def _initial_llm_check(self):
        """Verifica na inicialização se a LLM/Ollama está operacional. Se não estiver, desliga o botão."""
        self._btn_llm_toggle.setText("🧠  Verificando IA...")
        self._btn_llm_toggle.setEnabled(False)
        self._set_busy("Verificando Ollama / IA...", True)

        def _async_check():
            try:
                # Se use_llm estiver True por padrão, testa a conexão e se falhar desliga
                if self.controller.use_llm:
                    self.controller.set_use_llm(True)
            finally:
                self._set_busy("Verificando Ollama / IA...", False)
                self._stats_emitter.stats_updated.emit()

        threading.Thread(target=_async_check, daemon=True).start()

    def _toggle_llm_mode(self):
        self._btn_llm_toggle.setText("⏳  Alternando IA...")
        self._btn_llm_toggle.setEnabled(False)
        self._set_busy("Testando conectividade da IA...", True)
        QApplication.processEvents()

        def _async_toggle_llm():
            try:
                new_mode = not self.controller.use_llm
                self.controller.set_use_llm(new_mode)
            finally:
                self._set_busy("Testando conectividade da IA...", False)
                self._stats_emitter.stats_updated.emit()

        threading.Thread(target=_async_toggle_llm, daemon=True).start()

    def _pick_directory(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Selecione a Pasta dos RELINTs",
            str(project_root),
        )
        if path:
            self.controller.set_monitoring_path(path)
            self._txt_path.setText(path)
            self._lbl_folder_info.setText(f"Pasta: {Path(path).name}")
            self._queue_log(f"📁 Pasta selecionada: {path}")
            self._update_etl_stats()

    def _toggle_etl_monitoring(self):
        if not self.controller.monitoring_path or not Path(self.controller.monitoring_path).exists():
            self._queue_log("⚠️ Selecione uma pasta válida antes de iniciar o monitoramento.")
            return

        if self.controller.is_monitoring:
            self._btn_monitoring.setText("⏳  Pausando Leitura...")
            self._btn_monitoring.setEnabled(False)
            QApplication.processEvents()

            def _async_stop_etl():
                try:
                    self.controller.stop_monitoring()
                finally:
                    self._stats_emitter.stats_updated.emit()

            threading.Thread(target=_async_stop_etl, daemon=True).start()
        else:
            self._btn_monitoring.setText("⏳  Iniciando Varredura...")
            self._btn_monitoring.setEnabled(False)
            QApplication.processEvents()

            def _async_start_etl():
                try:
                    self.controller.start_monitoring()
                finally:
                    self._stats_emitter.stats_updated.emit()

            threading.Thread(target=_async_start_etl, daemon=True).start()

    def _reset_etl_data(self):
        reply = QMessageBox.question(
            self,
            "Aviso de Reset Completo",
            "Isso limpará permanentemente os RELINTs, seus vínculos de participantes e as mídias extraídas.\n"
            "O módulo Gerenciador de Pessoas (App-AJ) não é afetado.\n\nDeseja prosseguir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._btn_reset.setText("⏳  Limpando Base...")
            self._btn_reset.setEnabled(False)
            QApplication.processEvents()

            def _async_reset_data():
                try:
                    self.controller.reset_and_reprocess_all()
                finally:
                    QTimer.singleShot(0, self._finish_reset_btn)

            threading.Thread(target=_async_reset_data, daemon=True).start()

    def _finish_reset_btn(self):
        self._btn_reset.setText("🧹  Limpar Base & Re-processar Tudo")
        self._btn_reset.setEnabled(True)
        self._stats_emitter.stats_updated.emit()

    def _force_quit_app(self):
        """Encerra de fato todos os serviços, threads e finaliza a aplicação completamente com resposta visual instantânea."""
        if self._is_quitting:
            return
        self._is_quitting = True

        # Oculta a janela e o ícone do tray sem piscar (0ms UI thread-safe)
        self.setWindowOpacity(0.0)
        self.hide()
        if hasattr(self, "_tray_icon") and self._tray_icon:
            self._tray_icon.hide()

        self._service_watcher.stop()
        self._typing_timer.stop()
        self._spinner_timer.stop()

        def _async_shutdown():
            try:
                # Para monitoramento
                if hasattr(self.controller, "is_monitoring") and self.controller.is_monitoring:
                    try:
                        self.controller.stop_monitoring()
                    except Exception:
                        pass

                # Para FastAPI backend
                if self.controller.web_app_manager.is_running:
                    try:
                        self.controller.close_web_dashboard()
                    except Exception:
                        pass

                # Para Frontend SvelteKit
                self._stop_frontend_process()
            finally:
                QTimer.singleShot(0, QApplication.quit)

        threading.Thread(target=_async_shutdown, daemon=True).start()

    # =========================================================================
    # Atualização de Estados Visuais & Thread-Safety (60 FPS)
    # =========================================================================

    def _on_service_status_received(self, is_be: bool, is_fe: bool):
        """Recebe o status dos serviços verificado pela thread em background."""
        self._set_busy("Iniciando ambiente & verificando serviços...", False)
        self._cached_backend_running = is_be
        self._cached_frontend_running = is_fe
        self._refresh_service_buttons()

    def _set_busy(self, reason: str, is_busy: bool):
        """Emite sinal thread-safe para atualizar o status de carregamento/verificação no console."""
        if hasattr(self, "_stats_emitter") and self._stats_emitter:
            self._stats_emitter.busy_changed.emit(reason, is_busy)

    def _on_busy_changed(self, reason: str, is_busy: bool):
        """Atualiza a lista interna de tarefas ativas e exibe ou oculta os indicadores do console."""
        if is_busy:
            self._active_busy_reasons[reason] = time.time()
        else:
            self._active_busy_reasons.pop(reason, None)

        has_busy = bool(self._active_busy_reasons)
        if hasattr(self, "_bar_console_loading"):
            self._bar_console_loading.setVisible(has_busy)
        if not has_busy and hasattr(self, "_lbl_console_status"):
            self._lbl_console_status.hide()

    def _animate_reading_spinner(self):
        """Atualiza a animação inline de spinner enquanto um arquivo estiver sendo lido ou serviços estiverem iniciando/verificando."""
        self._spinner_idx = (self._spinner_idx + 1) % len(self._spinner_frames)
        frame = self._spinner_frames[self._spinner_idx]

        # 1. Indicador de Leitura de Arquivo
        if self.controller.current_filename:
            raw_name = self.controller.current_filename
            short_name = format_display_filename(raw_name, max_chars=32)
            self._lbl_current.setText(f"📖 [{frame}] {short_name}")
            self._lbl_current.setToolTip(f"Arquivo em leitura:\n{raw_name}")
            self._lbl_current.setStyleSheet(
                "background-color: #1a1708; border: 1px solid #78350f; border-radius: 6px; color: #f59e0b; font-weight: 700; font-size: 12px; padding: 4px 8px;"
            )
            self._bar_reading_active.show()
        else:
            self._bar_reading_active.hide()

        # 2. Indicador Ativo no Console de Logs (Serviços e Verificações)
        if hasattr(self, "_active_busy_reasons") and self._active_busy_reasons:
            latest_reason = list(self._active_busy_reasons.keys())[-1]
            if hasattr(self, "_lbl_console_status"):
                self._lbl_console_status.setText(f"{frame}  {latest_reason}")
                self._lbl_console_status.show()
            if hasattr(self, "_bar_console_loading"):
                self._bar_console_loading.show()
        else:
            if hasattr(self, "_lbl_console_status"):
                self._lbl_console_status.hide()
            if hasattr(self, "_bar_console_loading"):
                self._bar_console_loading.hide()

    def _refresh_service_buttons(self):
        """Atualiza os textos e cores dos botões de serviço instantaneamente, respeitando transições."""

        # Botão Unificado do Dashboard na Aba 1
        if hasattr(self, "_btn_open_dashboard") and not getattr(self, "_is_transitioning_dashboard", False):
            if self._is_dashboard_running():
                self._btn_open_dashboard.setText("⛔  Parar Dashboard Completo")
                self._btn_open_dashboard.setStyleSheet(BTN_DASHBOARD_STOP_STYLE)
            else:
                self._btn_open_dashboard.setText("🌐  Iniciar & Abrir Dashboard Completo")
                self._btn_open_dashboard.setStyleSheet(BTN_DASHBOARD_START_STYLE)
            self._btn_open_dashboard.setEnabled(True)

        # Botão Dedicado do FastAPI na Aba 2
        if hasattr(self, "_btn_fastapi_toggle_tab2") and not getattr(self, "_is_transitioning_backend", False):
            if self._cached_backend_running:
                self._btn_fastapi_toggle_tab2.setText("⛔ Parar API")
                self._btn_fastapi_toggle_tab2.setStyleSheet(BTN_SERVICE_STOP_STYLE)
            else:
                self._btn_fastapi_toggle_tab2.setText("🚀 Iniciar API")
                self._btn_fastapi_toggle_tab2.setStyleSheet(BTN_SERVICE_START_STYLE)
            self._btn_fastapi_toggle_tab2.setEnabled(True)

        # Botão Dedicado do SvelteKit na Aba 2
        if hasattr(self, "_btn_svelte_toggle_tab2") and not getattr(self, "_is_transitioning_frontend", False):
            if self._cached_frontend_running:
                self._btn_svelte_toggle_tab2.setText("⛔ Parar Svelte")
                self._btn_svelte_toggle_tab2.setStyleSheet(BTN_SERVICE_STOP_STYLE)
            else:
                self._btn_svelte_toggle_tab2.setText("🚀 Iniciar Svelte")
                self._btn_svelte_toggle_tab2.setStyleSheet(BTN_SERVICE_START_STYLE)
            self._btn_svelte_toggle_tab2.setEnabled(True)

        # Backend Status na Aba 2 (Apenas Status)
        if hasattr(self, "_lbl_backend_status"):
            if self._cached_backend_running:
                self._lbl_backend_status.setText("🟢 Rodando (:8000)")
                self._lbl_backend_status.setStyleSheet(f"color: {EMERALD}; font-weight: 700;")
            else:
                self._lbl_backend_status.setText("● Parado")
                self._lbl_backend_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")

        # Frontend Status na Aba 2 (Apenas Status)
        if hasattr(self, "_lbl_frontend_status"):
            if self._cached_frontend_running:
                self._lbl_frontend_status.setText("🟢 Rodando (:5173)")
                self._lbl_frontend_status.setStyleSheet(f"color: {EMERALD}; font-weight: 700;")
            else:
                self._lbl_frontend_status.setText("● Parado")
                self._lbl_frontend_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")

    def _update_etl_stats(self):
        """Atualização ultrarrápida das barras e contadores (< 0.1ms)."""
        total_folder = getattr(self.controller, "total_files_in_folder", 0)
        skipped = getattr(self.controller, "skipped_count", 0)
        processed = getattr(self.controller, "processed_count", 0)

        read_total = min(skipped + processed, total_folder)
        general_percent = int((read_total / total_folder) * 100) if total_folder > 0 else 0
        self._bar_general.setValue(general_percent)
        self._lbl_bar1_counts.setText(f"{read_total} / {total_folder} PDFs ({general_percent}%)")

        discovered = getattr(self.controller, "total_discovered", 0)
        session_percent = int((processed / discovered) * 100) if discovered > 0 else 0
        self._bar_session.setValue(session_percent)
        self._lbl_bar2_counts.setText(f"{processed} / {discovered} Novos ({session_percent}%)")

        # Proteção seletiva de botões de arquivo durante leitura
        is_busy = self.controller.is_monitoring
        if hasattr(self, "_btn_reset") and ("⏳" not in self._btn_reset.text()):
            self._btn_reset.setEnabled(not is_busy)
        if hasattr(self, "_btn_browse"):
            self._btn_browse.setEnabled(not is_busy)

        # Botão de Monitoramento na Aba 1
        if not self._btn_monitoring.isEnabled() or "⏳" not in self._btn_monitoring.text():
            if self.controller.is_monitoring:
                self._btn_monitoring.setText("⏸  Pausar Leitura & Monitoramento")
                self._btn_monitoring.setStyleSheet(BTN_PRIMARY_PAUSE_STYLE)
            else:
                self._btn_monitoring.setText("▶  Iniciar Leitura & Monitoramento")
                self._btn_monitoring.setStyleSheet(BTN_PRIMARY_START_STYLE)
            self._btn_monitoring.setEnabled(True)

        # Botão Modo IA na Aba 1
        if not self._btn_llm_toggle.isEnabled() or "⏳" not in self._btn_llm_toggle.text():
            if self.controller.use_llm:
                self._btn_llm_toggle.setText("⚡ IA (Ollama): Ativa")
                self._btn_llm_toggle.setStyleSheet(BTN_LLM_ACTIVE_STYLE)
            else:
                self._btn_llm_toggle.setText("⚡ Modo Rápido (Sem IA)")
                self._btn_llm_toggle.setStyleSheet(BTN_LLM_INACTIVE_STYLE)
            self._btn_llm_toggle.setEnabled(True)

        # Monitor Status na Aba 2
        if self.controller.is_monitoring:
            self._lbl_monitor_status.setText("● Monitorando Ativo")
            self._lbl_monitor_status.setStyleSheet(f"color: {EMERALD}; font-weight: 700;")
        else:
            self._lbl_monitor_status.setText("● Inativo / Pausado")
            self._lbl_monitor_status.setStyleSheet(f"color: {GREY}; font-weight: 700;")

        if self.controller.monitoring_path:
            self._txt_path.setText(self.controller.monitoring_path)
            self._lbl_folder_info.setText(f"Pasta: {Path(self.controller.monitoring_path).name}")

        # Atualiza labels estáticas caso não haja arquivo ativo
        if not self.controller.current_filename:
            self._lbl_current.setToolTip("")
            if self.controller.is_monitoring:
                self._lbl_current.setText("🟢 Monitorando pasta por novos arquivos...")
                self._lbl_current.setStyleSheet(
                    "background-color: #0f1e17; border: 1px solid #047857; border-radius: 6px; color: #10b981; font-weight: 700; font-size: 12px; padding: 4px 8px;"
                )
            else:
                self._lbl_current.setText("⏸️ Fila de leitura pausada")
                self._lbl_current.setStyleSheet(
                    f"background-color: #131316; border: 1px solid {BORDER}; border-radius: 6px; color: {GREY}; font-weight: 700; font-size: 12px; padding: 4px 8px;"
                )

    def _update_reports_list(self):
        while self._reports_layout.count() > 1:
            item = self._reports_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        try:
            reports = self.controller.db_repo.get_all()
            all_registry = self.controller.processed_registry.get_all_records()
            active_rule = getattr(self.controller.active_rule, "name", "Homicídio")

            processed_db_files = {rpt.source_file for rpt in reports}
            items_to_render = []

            # Sucessos e relatórios salvos no banco de dados
            for rpt in reports:
                ext_method = getattr(rpt, "extraction_method", "") or ""
                is_llm = "Sem IA" not in ext_method and ("Ollama" in ext_method or "IA" in ext_method)
                items_to_render.append({
                    "filename": rpt.source_file,
                    "is_llm": is_llm,
                    "is_error": False,
                    "error_msg": None,
                })

            # Relatórios que falharam na leitura (registrados no histórico com erro)
            for fn, rule_dict in all_registry.items():
                if isinstance(rule_dict, dict) and active_rule in rule_dict:
                    status_str = str(rule_dict[active_rule]).lower()
                    if ("error" in status_str or "falha" in status_str) and fn not in processed_db_files:
                        items_to_render.append({
                            "filename": fn,
                            "is_llm": False,
                            "is_error": True,
                            "error_msg": rule_dict[active_rule],
                        })

            # Inverte para que os últimos processados apareçam no topo
            items_to_render.reverse()


            for item_data in items_to_render:
                fn = item_data["filename"]
                is_llm = item_data["is_llm"]
                is_error = item_data["is_error"]

                if is_error:
                    method_text = "⚙️ Processamento"
                    method_style = "background-color: #27272a; color: #a1a1aa; border: 1px solid #3f3f46; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: 600;"
                    status_text = "🔴 Falha na Leitura"
                    status_style = "background-color: #451a1a; color: #fca5a5; border: 1px solid #dc2626; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: 600;"
                    file_style = "font-weight: 600; font-size: 11px; color: #fca5a5;"
                else:
                    method_text = "⚡ IA (Ollama)" if is_llm else "⚙️ Sem IA (Regex)"
                    method_style = (
                        "background-color: #142e23; color: #6ee7b7; border: 1px solid #047857; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: 600;"
                        if is_llm
                        else "background-color: #27272a; color: #a1a1aa; border: 1px solid #3f3f46; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: 600;"
                    )
                    status_text = "🟢 Lido com Sucesso"
                    status_style = "background-color: #064e3b; color: #a7f3d0; border: 1px solid #059669; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: 600;"
                    file_style = "font-weight: 600; font-size: 11px; color: #ffffff;"

                btn_reprocess_style = """
                QPushButton {
                    background-color: #27272a;
                    color: #6ee7b7;
                    border: 1px solid #047857;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 12px;
                    padding: 4px 12px;
                }
                QPushButton:hover {
                    background-color: #10b981;
                    color: #ffffff;
                    border-color: #10b981;
                }
                QPushButton:pressed {
                    background-color: #047857;
                }
                """

                card_layout = QHBoxLayout()
                card_layout.setContentsMargins(12, 8, 12, 8)
                card_layout.setSpacing(12)

                lbl_file = QLabel(fn)
                lbl_file.setStyleSheet(file_style)
                lbl_file.setWordWrap(True)
                lbl_file.setToolTip(fn)

                badge_method = QLabel(method_text)
                badge_method.setStyleSheet(method_style)
                badge_method.setAlignment(Qt.AlignmentFlag.AlignCenter)

                badge_status = QLabel(status_text)
                badge_status.setStyleSheet(status_style)
                badge_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

                btn_reprocess = QPushButton("🔄  Re-processar")
                btn_reprocess.setToolTip("Executar nova leitura deste relatório")
                btn_reprocess.setFixedHeight(32)
                btn_reprocess.setMinimumWidth(115)
                btn_reprocess.setStyleSheet(btn_reprocess_style)
                filename = fn
                btn_reprocess.clicked.connect(
                    lambda _, f=filename: self._on_reprocess_clicked(f)
                )

                card_layout.addWidget(lbl_file, stretch=1)
                card_layout.addWidget(badge_method)
                card_layout.addWidget(badge_status)
                card_layout.addWidget(btn_reprocess)

                card = QFrame()
                card.setProperty("card", True)
                if is_error:
                    card.setStyleSheet("QFrame[card='true'] { background-color: #1c1010; border: 1px solid #7f1d1d; border-radius: 8px; }")
                card.setLayout(card_layout)
                self._reports_layout.insertWidget(self._reports_layout.count() - 1, card)

        except Exception as exc:
            err_label = QLabel(f"Erro ao carregar relatórios: {exc}")
            err_label.setStyleSheet(f"color: {RED};")
            self._reports_layout.insertWidget(0, err_label)

    def _refresh_reports_clicked(self):
        """Atualiza a lista de relatórios com feedback visual no console de logs."""
        self._set_busy("Atualizando lista de relatórios...", True)
        self._update_reports_list()
        QTimer.singleShot(400, lambda: self._set_busy("Atualizando lista de relatórios...", False))

    def _on_reprocess_clicked(self, filename: str):
        """Executa o reprocessamento assíncrono de um arquivo com feedback visual de carregamento."""
        self._set_busy(f"Reprocessando {filename}...", True)
        self._queue_log(f"🔄 Solicitado reprocessamento do arquivo: {filename}")
        rule_name = getattr(self.controller.active_rule, "name", "Homicídio")

        def _async_reprocess():
            try:
                self.controller.reprocess_file_history(filename, rule_name)
            finally:
                self._set_busy(f"Reprocessando {filename}...", False)
                self._stats_emitter.stats_updated.emit()
                QTimer.singleShot(600, self._update_reports_list)

        threading.Thread(target=_async_reprocess, daemon=True).start()

    # --- Logs Desacoplados com Efeito Typewriter Inteligente ---

    def _queue_log(self, message: str):
        """Enfileira a mensagem de log de forma 100% não bloqueante a partir de qualquer thread."""
        now = time.strftime("%H:%M:%S")
        self._log_queue.append(f"[{now}] {message}")

    def _typewriter_step(self):
        """Efeito de digitação suave com aceleração automática sob alta carga de logs."""
        # Se não há linha atual sendo digitada, busca a próxima da fila
        if not self._typing_current_line:
            if self._log_queue:
                self._typing_current_line = self._log_queue.popleft()
                self._typing_char_idx = 0
                cursor = self._log_view.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                # Garante que começa em nova linha se já houver texto
                text = self._log_view.toPlainText()
                if text and not text.endswith("\n"):
                    cursor.insertText("\n")
                self._log_view.setTextCursor(cursor)
            else:
                return

        # Auto-speed ultra-rápido para concluir o log sincronizado com a leitura
        q_len = len(self._log_queue)
        is_reading = bool(getattr(self.controller, "current_filename", None))

        if not is_reading and q_len > 0:
            chunk_size = 300  # Conclui os logs instantaneamente ao encerrar a leitura
        elif q_len > 10:
            chunk_size = 150
        elif q_len > 3:
            chunk_size = 80
        elif q_len > 1:
            chunk_size = 40
        else:
            chunk_size = 25

        remaining = len(self._typing_current_line) - self._typing_char_idx
        step = min(chunk_size, remaining)

        chunk = self._typing_current_line[self._typing_char_idx : self._typing_char_idx + step]
        self._typing_char_idx += step

        cursor = self._log_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Destaca em vermelho vívido (#ef4444) qualquer mensagem de erro no console
        char_format = QTextCharFormat()
        lower_line = self._typing_current_line.lower()
        if any(kw in lower_line for kw in ["erro", "error", "falha", "failed", "exception", "traceback", "⛔"]):
            char_format.setForeground(QColor("#ef4444"))
            char_format.setFontWeight(700)
        elif any(kw in lower_line for kw in ["aviso", "warning", "alert", "⏳"]):
            char_format.setForeground(QColor("#f59e0b"))
            char_format.setFontWeight(600)
        elif any(kw in lower_line for kw in ["sucesso", "concluí", "conclui", "🟢"]):
            char_format.setForeground(QColor("#10b981"))
            char_format.setFontWeight(600)
        else:
            char_format.setForeground(QColor("#a1a1aa"))

        cursor.setCharFormat(char_format)
        cursor.insertText(chunk)
        self._log_view.setTextCursor(cursor)
        self._log_view.ensureCursorVisible()

        # Finalizou a digitação da linha atual
        if self._typing_char_idx >= len(self._typing_current_line):
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText("\n")
            self._log_view.setTextCursor(cursor)
            self._log_view.ensureCursorVisible()
            self._typing_current_line = ""
            self._typing_char_idx = 0

    def _clear_logs(self):
        self._log_queue.clear()
        self._typing_current_line = ""
        self._typing_char_idx = 0
        self._log_view.clear()

    # --- Callbacks do Controller ---

    def _emit_stats(self):
        """Emite o sinal de atualização de estatísticas de forma thread-safe."""
        try:
            if hasattr(self, "_stats_emitter") and self._stats_emitter:
                self._stats_emitter.stats_updated.emit()
        except Exception:
            pass

    def _on_tab_changed(self, index: int):
        if index == 1:
            self._update_reports_list()


    def closeEvent(self, a0: QCloseEvent | None):
        """Minimiza para a bandeja do sistema ao fechar a janela, a menos que esteja encerrando tudo."""
        if self._is_quitting:
            if a0:
                a0.accept()
            return

        if a0:
            a0.ignore()
        self.hide()
        if hasattr(self, "_tray_icon") and self._tray_icon.isVisible():
            self._tray_icon.showMessage(
                "ReadRelint • Em Execução",
                "O painel continua ativo em segundo plano na bandeja do sistema.",
                QSystemTrayIcon.MessageIcon.Information,
                1500,
            )


def run(auto_start: bool = False):
    """Ponto de entrada para execução da aplicação PyQt6."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)

    controller = get_main_controller()
    window = MainWindow(controller)
    window.show_and_raise()

    if auto_start or "--autostart" in sys.argv:
        # Inicia automaticamente o Dashboard Web (FastAPI + SvelteKit) e abre no navegador
        QTimer.singleShot(400, window._toggle_dashboard_unified)

    sys.exit(app.exec())


if __name__ == "__main__":
    run()

