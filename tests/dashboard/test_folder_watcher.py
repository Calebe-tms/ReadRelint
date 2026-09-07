import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from watchdog.events import FileCreatedEvent, FileMovedEvent
from backend.task_manager.watcher.folder_watcher import FolderWatcher, NewPdfHandler

def test_handler_triggers_callback_for_pdf_created():
    mock_callback = MagicMock()
    handler = NewPdfHandler(mock_callback)
    
    # Simula a criação de um arquivo PDF
    event = FileCreatedEvent(src_path="caminho/documento.pdf")
    
    # Mockamos o time.sleep para o teste ser instantâneo
    with patch("time.sleep", return_value=None):
        handler.on_created(event)
        
    mock_callback.assert_called_once_with(Path("caminho/documento.pdf"))


def test_handler_triggers_callback_for_pdf_moved():
    mock_callback = MagicMock()
    handler = NewPdfHandler(mock_callback)
    
    # Simula a movimentação/renomeação de um arquivo para PDF
    event = FileMovedEvent(src_path="caminho/temp.tmp", dest_path="caminho/boletim.pdf")
    
    with patch("time.sleep", return_value=None):
        handler.on_moved(event)
        
    mock_callback.assert_called_once_with(Path("caminho/boletim.pdf"))


def test_handler_ignores_non_pdf_files():
    mock_callback = MagicMock()
    handler = NewPdfHandler(mock_callback)
    
    # Criação de um arquivo de texto (.txt)
    event_txt = FileCreatedEvent(src_path="caminho/documento.txt")
    
    with patch("time.sleep", return_value=None):
        handler.on_created(event_txt)
        
    mock_callback.assert_not_called()


def test_watcher_raises_error_if_folder_does_not_exist():
    mock_callback = MagicMock()
    watcher = FolderWatcher(Path("diretorio_inexistente_no_disco_123"), mock_callback)
    
    with pytest.raises(FileNotFoundError, match="O diretório para monitoramento não existe"):
        watcher.start()


@patch("backend.task_manager.watcher.folder_watcher.Observer")
def test_watcher_start_stop(mock_observer_class):
    mock_observer = MagicMock()
    mock_observer_class.return_value = mock_observer
    
    mock_callback = MagicMock()
    
    # Mockamos a existência do diretório para permitir a inicialização
    with patch.object(Path, "exists", return_value=True):
        watcher = FolderWatcher(Path("pasta_teste"), mock_callback)
        watcher.start()
        
        mock_observer.schedule.assert_called_once()
        mock_observer.start.assert_called_once()
        
        watcher.stop()
        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once()
