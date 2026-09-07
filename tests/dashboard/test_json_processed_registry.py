import pytest
import tempfile
import json
from pathlib import Path
from backend.task_manager.registry.json_processed_registry import JsonProcessedRegistry

@pytest.fixture
def temp_registry_file():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        file_path = Path(f.name)
    yield file_path
    if file_path.exists():
        file_path.unlink()

def test_initialization(temp_registry_file):
    # Ensure it initializes correctly even if file doesn't exist
    if temp_registry_file.exists():
        temp_registry_file.unlink()
    
    registry = JsonProcessedRegistry(temp_registry_file)
    assert temp_registry_file.exists()
    assert registry.get_all_records() == {}

def test_register_and_check_processed(temp_registry_file):
    registry = JsonProcessedRegistry(temp_registry_file)
    
    assert registry.is_processed("file1.pdf", "Homicídio") is False
    
    registry.register_processed("file1.pdf", "Homicídio", "sucesso")
    assert registry.is_processed("file1.pdf", "Homicídio") is True
    
    # Check if other rules for the same file are NOT processed
    assert registry.is_processed("file1.pdf", "Roubo") is False
    
    # Check data content
    data = registry.get_all_records()
    assert data["file1.pdf"]["Homicídio"] == "sucesso"

def test_clear_registry(temp_registry_file):
    registry = JsonProcessedRegistry(temp_registry_file)
    registry.register_processed("file1.pdf", "Homicídio", "sucesso")
    
    registry.clear()
    assert registry.get_all_records() == {}

def test_remove_record(temp_registry_file):
    registry = JsonProcessedRegistry(temp_registry_file)
    registry.register_processed("file1.pdf", "Homicídio", "sucesso")
    registry.register_processed("file1.pdf", "Roubo", "sucesso")
    
    registry.remove_record("file1.pdf", "Homicídio")
    
    assert registry.is_processed("file1.pdf", "Homicídio") is False
    assert registry.is_processed("file1.pdf", "Roubo") is True
    
    registry.remove_record("file1.pdf", "Roubo")
    assert "file1.pdf" not in registry.get_all_records()

def test_remove_records_bulk(temp_registry_file):
    registry = JsonProcessedRegistry(temp_registry_file)
    registry.register_processed("file1.pdf", "Homicídio", "sucesso")
    registry.register_processed("file2.pdf", "Homicídio", "sucesso")
    registry.register_processed("file3.pdf", "Roubo", "sucesso")
    
    registry.remove_records_bulk(["file1.pdf", "file2.pdf", "file3.pdf"], "Homicídio")
    
    assert registry.is_processed("file1.pdf", "Homicídio") is False
    assert registry.is_processed("file2.pdf", "Homicídio") is False
    assert registry.is_processed("file3.pdf", "Roubo") is True

def test_user_edits(temp_registry_file):
    registry = JsonProcessedRegistry(temp_registry_file)
    
    assert registry.get_user_edit("file1.pdf", "Homicídio") is None
    
    registry.save_user_edit("file1.pdf", "Homicídio", "Homicídio alterado pelo usuário")
    assert registry.get_user_edit("file1.pdf", "Homicídio") == "Homicídio alterado pelo usuário"

def test_handle_corrupted_json(temp_registry_file):
    # Corrupt the json file manually
    with open(temp_registry_file, "w", encoding="utf-8") as f:
        f.write("{invalid_json: true,")
        
    registry = JsonProcessedRegistry(temp_registry_file)
    
    # It should fallback to empty dict instead of crashing
    assert registry.get_all_records() == {}
    
    # And it should be able to recover by writing new valid data
    registry.register_processed("file1.pdf", "Homicídio", "sucesso")
    assert registry.is_processed("file1.pdf", "Homicídio") is True
