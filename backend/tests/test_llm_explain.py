"""Unit test: OpenRouter enrich falls back without API key."""

from app.ai_engine import RuleInput, RuleResult, predict_irrigation
from app.llm_explain import enrich_explanation


def test_enrich_without_key_keeps_rule_text(monkeypatch):
    monkeypatch.setattr("app.llm_explain.settings.openrouter_api_key", "")
    inp = RuleInput(soil_moisture=22, air_temperature=34, rainfall_probability=5)
    base = predict_irrigation(inp)
    out = enrich_explanation(inp, base)
    assert out.irrigation_needed == base.irrigation_needed
    assert out.confidence_score == base.confidence_score
    assert out.explanation == base.explanation
    assert out.irrigation_duration == base.irrigation_duration


def test_enrich_does_not_change_safety_numbers_on_fake_llm(monkeypatch):
    monkeypatch.setattr("app.llm_explain.settings.openrouter_api_key", "test-key")

    def fake_call(_key, _inp, result: RuleResult):
        return "LLM Türkçe açıklama: nem düşük olduğu için sulama öneriliyor. Onay gerekir."

    monkeypatch.setattr("app.llm_explain._call_openrouter", fake_call)
    inp = RuleInput(soil_moisture=22, air_temperature=34, rainfall_probability=5)
    base = predict_irrigation(inp)
    out = enrich_explanation(inp, base)
    assert out.irrigation_needed is True
    assert out.confidence_score == base.confidence_score
    assert out.risk_level == base.risk_level
    assert "LLM Türkçe" in out.explanation
