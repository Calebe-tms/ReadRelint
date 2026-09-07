import pytest
from unittest.mock import patch, MagicMock
from backend.engine.extractors.llm.ollama_client import OllamaClient

@patch("backend.engine.extractors.llm.ollama_client.requests.post")
def test_ollama_client_success(mock_post):
    # Mock da resposta de sucesso da API HTTP do Ollama
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '{"subject": "Tráfico de Drogas", "date_of_fact": "15/07/2026", "bm_group": "Outros", "summary": "Resumo...", "participants": [{"name": "José", "nickname": "Zezinho", "document": "123"}]}'
    }
    mock_post.return_value = mock_response

    client = OllamaClient(model_name="llama3")
    result = client.process_text("Texto bruto do RELINT")

    assert isinstance(result, dict)
    assert result["subject"] == "Tráfico de Drogas"
    assert result["date_of_fact"] == "15/07/2026"
    assert result["bm_group"] == "Outros"
    assert len(result["participants"]) == 1
    assert result["participants"][0]["name"] == "José"

    mock_post.assert_called_once()


@patch("backend.engine.extractors.llm.ollama_client.requests.post")
def test_ollama_client_failure(mock_post):
    # Simula erro de conexão/timeout
    mock_post.side_effect = Exception("Connection refused")

    client = OllamaClient()
    with pytest.raises(Exception):
        client.process_text("Texto bruto")

