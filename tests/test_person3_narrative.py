"""Unit tests for Person 3 LLM Narrative Engine and Persona Adaptation."""
import pytest
from src.llm.narrative import NarrativeGenerator
from src.personalization.personas import PERSONAS, get_persona_details
from app.mock_data import DEMO_SCENARIOS

def test_persona_registry():
    assert "Executive" in PERSONAS
    assert "Regional Manager" in PERSONAS
    assert "Analyst" in PERSONAS
    
    exec_info = get_persona_details("Executive")
    assert exec_info["title"] == "CFO / C-Suite Executive"
    assert "Revenue" in exec_info["kpi_focus"]

def test_narrative_generator_executive():
    gen = NarrativeGenerator()
    scenario_a = DEMO_SCENARIOS["Scenario A: Strong Evidence (Revenue Drop)"]
    narrative = gen.generate(scenario_a, "Executive")
    
    assert "[EXECUTIVE SUMMARY]" in narrative
    assert "Revenue" in narrative
    assert "89%" in narrative or "HIGH" in narrative

def test_narrative_generator_abstention():
    gen = NarrativeGenerator()
    scenario_c = DEMO_SCENARIOS["Scenario C: Sparse History (New KPI Launch)"]
    narrative = gen.generate(scenario_c, "Analyst")
    
    assert "[ABSTENTION ADVISORY]" in narrative
    assert "sparse" in narrative.lower()

def test_narrative_generator_ambiguity():
    gen = NarrativeGenerator()
    scenario_b = DEMO_SCENARIOS["Scenario B: Ambiguous Evidence (Multiple Competing Drivers)"]
    narrative = gen.generate(scenario_b, "Regional Manager")
    
    assert "Revenue" in narrative
