import pytest
from pathlib import Path
from src.compliance_engine import RegulatoryComplianceEngine


@pytest.fixture
def compliance_engine():
    """Initializes a fresh compliance engine instance for every test run."""
    return RegulatoryComplianceEngine()


def test_german_market_bold_allergen_pass(compliance_engine):
    """Ensures a cleanly formatted German allergen string passes the legal gate."""
    simulated_text = "Zutaten: Wasser, **Milch**, Zucker. Mindestens haltbar bis: 31.12.2026."
    mock_record = {
        "destination_country": "DE",
        "declared_allergens": ["Milch"],
        "timestamp_inbound": "2026-01-01T08:00:00"
    }

    result = compliance_engine.evaluate_compliance(simulated_text, mock_record)
    assert result["is_compliant"] is True
    assert result["allergen_compliance"]["status"] is True


def test_french_market_missing_bold_fail(compliance_engine):
    """Ensures unbolded allergens are caught immediately as compliance failures."""
    simulated_text = "Ingrédients: Eau, Gluten, Sel. À consommer de préférence avant: 31.12.2026."
    mock_record = {
        "destination_country": "FR",
        "declared_allergens": ["Gluten"],
        "timestamp_inbound": "2026-01-01T08:00:00"
    }

    result = compliance_engine.evaluate_compliance(simulated_text, mock_record)
    assert result["is_compliant"] is False
    assert "Gluten" in result["allergen_compliance"]["faulty_items"]


def test_insufficient_shelf_life_fail(compliance_engine):
    """Ensures products arriving under the regulatory safety buffer are rejected."""
    simulated_text = "Zutaten: Wasser. Mindestens haltbar bis: 16.01.2026."
    mock_record = {
        "destination_country": "DE",
        "declared_allergens": [],
        "timestamp_inbound": "2026-01-01T08:00:00"
    }

    result = compliance_engine.evaluate_compliance(simulated_text, mock_record)
    assert result["is_compliant"] is False
    assert "INSUFFICIENT_SHELF_LIFE" in result["expiry_compliance"]["message"]