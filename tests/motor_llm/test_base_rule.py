import pytest
from backend.engine.extractors.llm.rules.base_rule import IncidentRule
from backend.core.entities import IncidentReport

class DummyRule(IncidentRule):
    @property
    def name(self) -> str:
        return "Dummy"

    @property
    def db_name(self) -> str:
        return "dummy.json"

    @property
    def keywords(self) -> list[str]:
        return ["palavra", "chave"]

    @property
    def questions(self) -> dict:
        return {"q1": "pergunta?"}

def test_incident_rule_defaults():
    rule = DummyRule()
    
    assert rule.name == "Dummy"
    assert rule.db_name == "dummy.json"
    
    # Teste de default validations
    assert rule.validate_qa_results({"qualquer": "coisa"}) is True
    assert rule.get_schema_model() == IncidentReport
    assert rule.get_bm_group("teste.pdf", "Assunto") is None

def test_incident_rule_matches_filter():
    rule = DummyRule()
    
    # Textos que devem dar match
    assert rule.matches_filter("Aqui tem uma PALAVRA solta") is True
    assert rule.matches_filter("A CHAVE para o sucesso") is True
    
    # Textos que NÃO devem dar match
    assert rule.matches_filter("texto sem k-e-y-w-o-r-d") is False
    assert rule.matches_filter("") is False
