# -*- coding: utf-8 -*-
"""
Garantia: a camada determinística incondicional de EtlService.process_file()
(date_of_fact, time_of_fact, relint_type, main_fact — roda para os dois motores) nunca
sobrescreve um valor já resolvido por um pass anterior (LLM ou determinístico), nem perde
tempo tentando recalcular algo que já foi decidido.

Hoje nenhum pass real preenche esses 4 campos antes dessa fase (por isso o guard
"só preenche se vazio" nunca é exercitado em produção) — este teste simula, via um
LlmPipeline falso, o cenário em que um pass futuro já os resolveu, para travar a garantia
antes que ela seja necessária de verdade.
"""
from pathlib import Path
from unittest.mock import Mock

import backend.task_manager.etl.etl_service as etl_service_module
from backend.engine.extractors.base import ExtractionResult
from backend.engine.extractors.llm.rules.relint_rule import RelintRule
from backend.task_manager.etl.etl_service import EtlService


class FakeAlreadyResolvedPipeline:
    """Substitui LlmPipeline simulando um pass que já resolveu os 4 campos da Fase B."""

    def __init__(self, processor=None) -> None:
        pass

    def extract(self, text, filename="", rule=None, pre_extracted_entities=None, **kwargs) -> ExtractionResult:
        return ExtractionResult(
            data={
                "subject": "Assunto de teste",
                "summary": "Resumo de teste já resolvido.",
                "content": text,
                "date_of_fact": "JÁ_RESOLVIDO_DATA",
                "time_of_fact": "JÁ_RESOLVIDO_HORA",
                "relint_type": "JÁ_RESOLVIDO_TIPO",
                "main_fact": "JÁ_RESOLVIDO_FATO",
            },
            extraction_method="Ollama (IA)",
            alerts=[],
            success=True,
        )


def _build_service(monkeypatch) -> EtlService:
    monkeypatch.setattr(etl_service_module, "LlmPipeline", FakeAlreadyResolvedPipeline, raising=False)
    # LlmPipeline é importado localmente dentro de process_file() a partir do módulo
    # original — precisa ser substituído lá também para o "from ... import LlmPipeline"
    # local pegar o fake em vez do real.
    import backend.engine.extractors.llm.pipeline as llm_pipeline_module
    monkeypatch.setattr(llm_pipeline_module, "LlmPipeline", FakeAlreadyResolvedPipeline)

    mock_parser = Mock()
    mock_parser.extract_text.return_value = "Texto de teste do RELINT."
    mock_db = Mock()
    mock_db.exists_by_source_file.return_value = False
    mock_registry = Mock()
    mock_registry.is_processed.return_value = False
    mock_person_repo = Mock()

    return EtlService(
        file_parser=mock_parser,
        llm_processor=Mock(),
        database_repo=mock_db,
        processed_registry=mock_registry,
        person_repo=mock_person_repo,
        use_llm=True,
    )


def test_fase_b_nunca_sobrescreve_campos_ja_resolvidos(monkeypatch):
    service = _build_service(monkeypatch)
    rule = RelintRule()

    report = service.process_file(file_path=Path("dummy.pdf"), rule=rule)

    assert report is not None
    assert report.date_of_fact == "JÁ_RESOLVIDO_DATA"
    assert report.time_of_fact == "JÁ_RESOLVIDO_HORA"
    # relint_type passa por um field_validator em IncidentReport (normalize_relint_type) que
    # sempre roda, independente da origem do valor — aqui só normaliza a caixa (.title()) por
    # não bater com nenhum dos 3 valores fechados do enum. O conteúdo (não recalculado por
    # classify_relint_type) é o que a garantia desta fase realmente protege.
    assert report.relint_type == "Já_Resolvido_Tipo"
    assert report.main_fact == "JÁ_RESOLVIDO_FATO"


def test_fase_b_nao_perde_tempo_recalculando_o_que_ja_foi_resolvido(monkeypatch):
    service = _build_service(monkeypatch)
    rule = RelintRule()

    # Substitui as funções determinísticas por mocks — se a Fase B respeitar o guard
    # "só preenche se vazio", nenhuma delas deve ser chamada.
    mock_extract_date = Mock(return_value="NUNCA_DEVERIA_RODAR")
    mock_extract_time = Mock(return_value="NUNCA_DEVERIA_RODAR")
    mock_classify_relint_type = Mock(return_value="NUNCA_DEVERIA_RODAR")
    monkeypatch.setattr(etl_service_module, "extract_date_of_fact", mock_extract_date)
    monkeypatch.setattr(etl_service_module, "extract_time_of_fact", mock_extract_time)
    monkeypatch.setattr(etl_service_module, "classify_relint_type", mock_classify_relint_type)

    report = service.process_file(file_path=Path("dummy.pdf"), rule=rule)

    assert report is not None
    mock_extract_date.assert_not_called()
    mock_extract_time.assert_not_called()
    mock_classify_relint_type.assert_not_called()
    # main_fact não tem uma função dedicada para mockar (é derivação direta de 'summary'),
    # mas o valor final ainda precisa bater com o que já veio resolvido.
    assert report.main_fact == "JÁ_RESOLVIDO_FATO"
