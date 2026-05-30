# Regex and language verification analytics logic
import re
from datetime import datetime
from pathlib import Path
import yaml


class RegulatoryComplianceEngine:
    def __init__(self, config_path: Path = Path("config/regulatory_rules.yaml")):
        self.config_path = config_path
        self.rules = self.load_regulatory_rules()

    def load_regulatory_rules(self) -> dict:
        """Loads market-specific legal thresholds. Defaults to strict base rules if file missing."""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

        # Fallback hardcoded production baselines if YAML is not yet initialized
        return {
            "DE": {"required_languages": ["de"], "allergen_formatting": "markdown_bold", "min_shelf_life_days": 90},
            "FR": {"required_languages": ["fr"], "allergen_formatting": "markdown_bold", "min_shelf_life_days": 90},
            "PL": {"required_languages": ["pl"], "allergen_formatting": "markdown_bold", "min_shelf_life_days": 90}
        }

    def verify_allergen_formatting(self, text: str, declared_allergens: list[str]) -> tuple[bool, list[str]]:
        """
        Validates that every single declared allergen is explicitly formatted in Markdown bolding.
        Example: '**Milch**' passes, while 'Milch' triggers a regulatory compliance failure.
        """
        missing_or_invalid_allergens = []

        for allergen in declared_allergens:
            # Pattern checks for the exact allergen word wrapped inside double asterisks
            pattern = rf"\*\*{re.escape(allergen)}\*\*"
            if not re.search(pattern, text, re.IGNORECASE):
                missing_or_invalid_allergens.append(allergen)

        is_compliant = len(missing_or_invalid_allergens) == 0
        return is_compliant, missing_or_invalid_allergens

    def verify_expiry_date(self, text: str, arrival_timestamp: str, min_days_required: int) -> tuple[bool, str]:
        """
        Locates expiration dates within unstructured text, parses them, and checks
        if the product meets Metro's strict minimum shelf-life buffer.
        """
        # Look for standard European date format: DD.MM.YYYY
        date_match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", text)
        if not date_match:
            return False, "EXPIRY_DATE_NOT_FOUND"

        try:
            expiry_date_str = date_match.group(0)
            expiry_date = datetime.strptime(expiry_date_str, "%d.%m.%Y")

            # Parse inbound arrival time (strip out ISO timezone Z if present)
            arrival_date_str = arrival_timestamp.split("T")[0]
            arrival_date = datetime.strptime(arrival_date_str, "%Y-%m-%d")

            # Calculate actual remaining shelf life
            remaining_days = (expiry_date - arrival_date).days

            if remaining_days < min_days_required:
                return False, f"INSUFFICIENT_SHELF_LIFE: {remaining_days} days remaining (Requires {min_days_required})"

            return True, f"VALID_SHELF_LIFE: {remaining_days} days remaining"

        except Exception as e:
            return False, f"DATE_PARSING_ERROR: {str(e)}"

    def evaluate_compliance(self, extracted_text: str, database_record: dict) -> dict:
        """Runs the complete compliance check suite against an extracted text block."""
        country = database_record.get("destination_country", "DE")
        declared_allergens = database_record.get("declared_allergens", [])
        arrival_ts = database_record.get("timestamp_inbound", datetime.utcnow().isoformat())

        # Fetch country-specific rules
        country_rules = self.rules.get(country, self.rules["DE"])
        min_days = country_rules.get("min_shelf_life_days", 90)

        # Run independent verification steps
        allergens_ok, faulty_allergens = self.verify_allergen_formatting(extracted_text, declared_allergens)
        expiry_ok, expiry_msg = self.verify_expiry_date(extracted_text, arrival_ts, min_days)

        # Overall status is a PASS only if all regulatory gates clear successfully
        overall_compliance = allergens_ok and expiry_ok

        return {
            "image_id": database_record.get("image_id"),
            "is_compliant": overall_compliance,
            "allergen_compliance": {
                "status": allergens_ok,
                "faulty_items": faulty_allergens
            },
            "expiry_compliance": {
                "status": expiry_ok,
                "message": expiry_msg
            },
            "audit_timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    print("Regulatory Compliance Engine compiled successfully. Awaiting rule execution matrix.")