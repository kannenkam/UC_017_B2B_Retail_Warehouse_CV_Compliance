import pytest
import json
from pathlib import Path
from src.orchestrator import WarehouseAuditOrchestrator


@pytest.fixture
def temp_metadata_file(tmp_path):
    """Creates a temporary mock baseline data file for pipeline safety testing."""
    mock_records = [
        {
            "image_id": "999999",
            "destination_country": "DE",
            "declared_allergens": [],
            "timestamp_inbound": "2026-01-01T08:00:00",
            "extracted_text": "Zutaten: Wasser. Mindestens haltbar bis: 31.12.2026."
        }
    ]

    file_path = tmp_path / "test_baseline_metadata.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(mock_records, f)
    return file_path


def test_orchestrator_end_to_end_execution(temp_metadata_file):
    """Verifies that the entire pipeline execution block runs completely without crashing."""
    # Initialize our production audit system architecture
    orchestrator = WarehouseAuditOrchestrator()

    # Run the orchestrator using our temporary mock metadata database file
    try:
        orchestrator.run_pipeline_audit(metadata_path=temp_metadata_file)
        execution_success = True
    except Exception as e:
        print(f"Pipeline crashed with exception: {e}")
        execution_success = False

    assert execution_success is True