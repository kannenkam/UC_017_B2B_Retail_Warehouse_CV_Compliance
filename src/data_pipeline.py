# Local asset pipeline (generates synthetic & pulls from HF)
import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from pydantic import BaseModel, Field

# Ensure our local workspace directory structure exists
DATA_DIR = Path("data/inbound_pallet_scans")
DRIFT_DIR = Path("data/drift_quarantine")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DRIFT_DIR.mkdir(parents=True, exist_ok=True)


# Define our robust enterprise database validation schema
class ProductMetadata(BaseModel):
    image_id: str = Field(..., description="Unique barcode string identifier")
    product_name: str = Field(..., description="Metro own-brand item label")
    destination_country: str = Field(..., description="Target distribution market (DE, FR, PL)")
    supplier_id: str = Field(..., description="Global vendor registration tracking ID")
    batch_lot_number: str = Field(..., description="Isolated production run identifier")
    timestamp_inbound: str = Field(..., description="ISO timestamp of arrival at warehouse")
    declared_allergens: list[str] = Field(..., description="Allergens requiring explicit bolding")
    minimum_shelf_life_days: int = Field(..., description="Legal threshold buffer for the category")
    extracted_text: str = Field(..., description="Simulated raw OCR text read from packaging back")


# Constants for synthetic generation arrays
METRO_BRANDS = [
    "METRO Chef Whole Milk", "METRO Premium Basmati Rice",
    "METRO Chef Cream Cheese", "METRO Fine Life Chopped Tomatoes",
    "METRO Chef Frozen Atlantic Salmon", "RIOBA Espresso Beans"
]
COUNTRIES = ["DE", "FR", "PL"]
ALLERGEN_POOL = ["Milch", "Nüsse", "Gluten", "Soja", "Ei"]


def generate_simulated_ocr_text(product: str, country: str, allergens: list[str], valid_expiry: bool) -> str:
    """Generates a realistic unstructured OCR text string representing the back of packaging."""
    # Compute expiration date relative to our current execution context
    base_date = datetime.now()
    days_offset = random.randint(95, 180) if valid_expiry else random.randint(5, 45)
    expiry_date = (base_date + timedelta(days=days_offset)).strftime("%d.%m.%Y")

    # Simulate high-quality markdown bolding vs non-bolding errors
    formatted_allergens = []
    for a in allergens:
        # 15% chance a production failure occurs and the allergen misses mandatory bolding format
        if random.random() > 0.15:
            formatted_allergens.append(f"**{a}**")
        else:
            formatted_allergens.append(a)

    allergen_str = ", ".join(formatted_allergens) if formatted_allergens else "Keine"

    if country == "DE":
        text = f"METRO AG Quality Assurance. Produkt: {product}. Zutaten: Wasser, {allergen_str}, Salz. Mindestens haltbar bis: {expiry_date}. Hergestellt in Deutschland."
    elif country == "FR":
        text = f"METRO AG France. Produit: {product}. Ingrédients: Eau, {allergen_str}, Sel. À consommer de préférence avant le: {expiry_date}."
    else:
        text = f"METRO AG Polska. Produkt: {product}. Składniki: Woda, {allergen_str}, Sól. Najlepiej spożyć przed: {expiry_date}."

    return text


def build_production_dataset(count: int = 105):
    """Generates 100+ robust data validation records for local system evaluation."""
    records = []
    current_time = datetime.utcnow().isoformat()

    for i in range(count):
        barcode = f"400222{100000 + i}"
        product = random.choice(METRO_BRANDS)
        country = random.choice(COUNTRIES)
        # Select 0 to 2 random allergens for this product run
        num_allergens = random.randint(0, 2)
        selected_allergens = random.sample(ALLERGEN_POOL, num_allergens)

        # Inject controlled anomalies (e.g., 10% of items arriving with insufficient shelf life)
        is_valid_expiry = random.random() > 0.10

        ocr_text = generate_simulated_ocr_text(product, country, selected_allergens, is_valid_expiry)

        record = ProductMetadata(
            image_id=barcode,
            product_name=product,
            destination_country=country,
            supplier_id=f"SUPP-{random.randint(5000, 9999)}",
            batch_lot_number=f"LOT-{datetime.now().year}-X{random.randint(10, 99)}",
            timestamp_inbound=current_time,
            declared_allergens=selected_allergens,
            minimum_shelf_life_days=90,
            extracted_text=ocr_text
        )
        records.append(record.model_dump())

    # Persist dataset manifest as our central source of truth
    output_path = Path("data/baseline_metadata.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)

    print(f"Successfully generated {count} production-grade baseline records at: {output_path}")


if __name__ == "__main__":
    #build_production_dataset()
    build_production_dataset(count=200)  # Changed from 105 to 200 for a longer system profile