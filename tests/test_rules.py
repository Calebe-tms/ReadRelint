import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
from backend.engine.extractors.llm.rules.relint_rule import RelintRule
from backend.task_manager.etl.etl_service import EtlService

def test_etl_service_with_rule_skips_processing():
    # Mocking dependencies - agora o processo NÃO pula e processa tudo
    mock_parser = Mock()
    mock_parser.extract_text.return_value = "Furto de veículo na garagem da residência."
    
    mock_llm = Mock()
    mock_llm.process_text.return_value = {"main_fact": "furto", "content": "Texto do furto."}
    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = False
    
    mock_registry = Mock()
    mock_registry.is_processed.return_value = False
    mock_person_repo = Mock()
    mock_municipality_repo = Mock()
    mock_municipality_repo.get_by_name.return_value = None

    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry, mock_person_repo)
    rule = RelintRule()
    
    progress_calls = []
    def on_progress(msg):
        progress_calls.append(msg)
        
    filtered_calls = []
    sent_calls = []

    # Executa o processamento do arquivo
    report = service.process_file(
        file_path=Path("dummy_furto.pdf"),
        rule=rule,
        on_progress=on_progress,
        on_filtered=lambda f: filtered_calls.append(f),
        on_sent_to_llm=lambda f: sent_calls.append(f)
    )
    
    # Não deve retornar None pois não há mais descarte
    assert report is not None
    assert report.content == "Furto de veículo na garagem da residência."
    # Pipeline multi-pass: Síntese, Localização, Especialidade e Registro (sem o Pass 1 legado)
    assert mock_llm.process_text.call_count == 4
    mock_db.save.assert_called_once()
    assert len(filtered_calls) == 0
    assert len(sent_calls) == 1

def test_etl_service_with_rule_processes_matching_file():
    mock_parser = Mock()
    mock_parser.extract_text.return_value = "Suspeito desferiu tiros e cometeu homicídio."
    
    mock_llm = Mock()
    mock_llm.process_text.return_value = {"main_fact": "homicídio consumado", "content": "Resumo estruturado do homicídio."}
    
    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = False
    
    mock_registry = Mock()
    mock_registry.is_processed.return_value = False
    mock_person_repo = Mock()
    mock_municipality_repo = Mock()
    mock_municipality_repo.get_by_name.return_value = None

    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry, mock_person_repo)
    rule = RelintRule()
    
    filtered_calls = []
    sent_calls = []
 
    report = service.process_file(
        file_path=Path("dummy_homicidio.pdf"),
        rule=rule,
        on_filtered=lambda f: filtered_calls.append(f),
        on_sent_to_llm=lambda f: sent_calls.append(f)
    )
    
    assert report is not None
    assert report.content == "Suspeito desferiu tiros e cometeu homicídio."
    # Pipeline multi-pass: Síntese, Localização, Especialidade e Registro (sem o Pass 1 legado)
    assert mock_llm.process_text.call_count == 4
    # O banco de dados deve ter sido salvo
    mock_db.save.assert_called_once()
    assert len(filtered_calls) == 0
    assert len(sent_calls) == 1
 
def test_etl_service_with_rule_discards_post_llm_false_positive():
    mock_parser = Mock()
    # Contém palavra de homicídio
    mock_parser.extract_text.return_value = "Foi registrado um homicídio consumado no local."
    
    mock_llm = Mock()
    # A LLM avalia semanticamente que é lesão leve, mas o ETL não descarta mais nada
    mock_llm.process_text.return_value = {"main_fact": "lesão corporal leve", "content": "Apenas lesão leve."}
    
    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = False
    
    mock_registry = Mock()
    mock_registry.is_processed.return_value = False
    mock_person_repo = Mock()
    mock_municipality_repo = Mock()
    mock_municipality_repo.get_by_name.return_value = None

    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry, mock_person_repo)
    rule = RelintRule()
    
    filtered_calls = []
    sent_calls = []
    progress_calls = []
 
    report = service.process_file(
        file_path=Path("dummy_homicidio_falso.pdf"),
        rule=rule,
        on_progress=lambda m: progress_calls.append(m),
        on_filtered=lambda f: filtered_calls.append(f),
        on_sent_to_llm=lambda f: sent_calls.append(f)
    )
    
    assert report is not None
    assert report.content == "Foi registrado um homicídio consumado no local."
    # Pipeline multi-pass: Síntese, Localização, Especialidade e Registro (sem o Pass 1 legado)
    assert mock_llm.process_text.call_count == 4
    mock_db.save.assert_called_once()
    assert len(filtered_calls) == 0
    assert len(sent_calls) == 1

def test_etl_service_skips_when_already_processed_in_registry():
    mock_parser = Mock()
    mock_llm = Mock()
    mock_db = Mock()
    
    mock_registry = Mock()
    mock_registry.is_processed.return_value = True
    mock_person_repo = Mock()
    mock_municipality_repo = Mock()

    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry, mock_person_repo)
    rule = RelintRule()
    
    progress_calls = []
    report = service.process_file(
        file_path=Path("dummy_already_processed.pdf"),
        rule=rule,
        on_progress=lambda m: progress_calls.append(m)
    )
    
    assert report is None
    # Nenhuma leitura de texto bruto ou chamada LLM deve acontecer
    mock_parser.extract_text.assert_not_called()
    mock_llm.process_text.assert_not_called()
    # Deve conter log informando que foi pulado pelo histórico
    assert any("Já processado" in msg for msg in progress_calls)

def test_etl_service_skips_when_exists_in_database():
    mock_parser = Mock()
    mock_llm = Mock()
    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = True

    mock_registry = Mock()
    mock_registry.is_processed.return_value = False
    mock_person_repo = Mock()
    mock_municipality_repo = Mock()

    service = EtlService(mock_parser, mock_llm, mock_db, mock_registry, mock_person_repo)
    rule = RelintRule()

    progress_calls = []
    report = service.process_file(
        file_path=Path("dummy_already_in_db.pdf"),
        rule=rule,
        on_progress=lambda m: progress_calls.append(m)
    )

    assert report is None
    mock_parser.extract_text.assert_not_called()
    mock_llm.process_text.assert_not_called()
    assert any("Já cadastrado no banco" in msg for msg in progress_calls)


