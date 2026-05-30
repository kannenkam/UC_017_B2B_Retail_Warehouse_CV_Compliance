import os
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv
import mlflow
import time

# Import our custom decoupled components
from data_pipeline import DATA_DIR, DRIFT_DIR
from vision_ocr import WarehouseVisionProcessor
from compliance_engine import RegulatoryComplianceEngine

# Load configuration variables from our secure local .env file
load_dotenv()
CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", 0.85))
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")


class WarehouseAuditOrchestrator:
    def __init__(self):
        # Configure MLflow pointing to our local server loopback address
        mlflow.set_tracking_uri(MLFLOW_URI)
        mlflow.set_experiment("Inbound_Packaging_Compliance_Audits")

        # Instantiate our core processing engines
        self.vision_processor = WarehouseVisionProcessor()
        self.compliance_engine = RegulatoryComplianceEngine()

    def run_pipeline_audit(self, metadata_path: Path = Path("data/baseline_metadata.json")):
        """Orchestrates the entire vision-to-compliance lifecycle across all items."""
        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Database baseline manifest missing at: {metadata_path}. Run data_pipeline.py first!")

        with open(metadata_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        print(f"Initializing audit execution loop across {len(records)} active pallet records...")

        # Establish a single, tracked MLflow execution run
        with mlflow.start_run(run_name="Full_Warehouse_Audit_Run"):
            # Log macro-level environment params for audit traceability
            mlflow.log_param("total_items_processed", len(records))
            mlflow.log_param("ocr_min_confidence_gate", CONFIDENCE_THRESHOLD)

            # 📷 ========================================================
            # PHYSICAL IMAGE CAPTURE LAYER (PHASE 5.7 INTEGRATION)
            # ========================================================
            # 📷 ========================================================
            # PHYSICAL IMAGE BATCH CAPTURE LAYER (DYNAMIC MULTI-IMAGE EVALUATION)
            # ========================================================
            inbound_folder = Path("data/inbound_pallet_scans")

            # Find all files with standard image extensions in the scanning folder
            valid_extensions = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff")
            all_physical_images = []
            for ext in valid_extensions:
                all_physical_images.extend(inbound_folder.glob(ext))

            if all_physical_images:
                print(
                    f"\n📷 [VISION ACTIVE] Found {len(all_physical_images)} physical assets for real-time batch processing:")

                for idx, image_path in enumerate(all_physical_images, 1):
                    print(f"\n--- Processing Image {idx}/{len(all_physical_images)}: {image_path.name} ---")
                    print("Running OpenCV adaptive thresholding and EasyOCR character localization...")

                    # Execute real deep learning text extraction on each unique file matrix
                    vision_results = self.vision_processor.process_inbound_scan(image_path, f"PHYSICAL_SAMPLE_{idx}")

                    print(f"👉 Extracted OCR Text Output:\n{vision_results['extracted_text']}")
                    print(f"📈 Vision Engine Confidence Score: {round(vision_results['ocr_confidence'] * 100, 2)}%")
                print("\n========================================================\n")
            else:
                print(
                    "\nℹ️ No physical image assets found in data/inbound_pallet_scans/. Skipping real OCR layer batch calculation.\n")
            # ========================================================

            passed_audits = 0
            failed_audits = 0
            quarantined_drift_items = 0

            for record in records:
                image_id = record["image_id"]

                # --- Step 1: Process Text Extraction via Vision Layer ---
                # To simulate reading an image on our local MacBook without real camera inputs,
                # we pass our generated text data matrix directly into the processing pipeline.
                extracted_text = record["extracted_text"]
                simulated_confidence = round(0.98 - (0.25 * (int(image_id) % 3 == 0)), 2)  # Simulate OCR noise variants

                # --- Step 2: Data Drift and OCR Confidence Guardrail Gate ---
                time.sleep(1)
                if simulated_confidence < CONFIDENCE_THRESHOLD:
                    quarantined_drift_items += 1
                    print(
                        f"⚠️ [DRIFT ALERT] Image {image_id} fell below confidence threshold ({simulated_confidence}). Quarantining record.")

                    # Track drift incidents on MLflow to alert engineering teams
                    mlflow.log_metric("data_drift_incidents", quarantined_drift_items)
                    continue

                # --- Step 3: Run Text Strings through Regulatory Engine ---
                audit_results = self.compliance_engine.evaluate_compliance(extracted_text, record)

                # --- Step 4: Aggregate Run Metrics and Log Results ---
                if audit_results["is_compliant"]:
                    passed_audits += 1
                else:
                    failed_audits += 1
                    print(
                        f"❌ [COMPLIANCE FAILURE] Item {image_id} failed audit. Reason: {audit_results['expiry_compliance']['message']}")

            # Log final aggregated run metrics to the MLflow dashboard
            mlflow.log_metric("total_passed_audits", passed_audits)
            mlflow.log_metric("total_failed_audits", failed_audits)
            mlflow.log_metric("total_quarantined_items", quarantined_drift_items)

            # Compute a high-level operational health metric
            compliance_yield = (passed_audits / (passed_audits + failed_audits)) * 100 if (
                                                                                                  passed_audits + failed_audits) > 0 else 0
            mlflow.log_metric("compliance_yield_percentage", round(compliance_yield, 2))

            print("\n========================================================")
            print("                AUDIT RUN COMPLETE                      ")
            print("========================================================")
            print(f" Total Audited:     {passed_audits + failed_audits}")
            print(f" Passed Cleanly:    {passed_audits}")
            print(f" Failed Regulatory: {failed_audits}")
            print(f" Quarantined Drift: {quarantined_drift_items}")
            print(f" Final System Yield: {round(compliance_yield, 2)}%")
            print("========================================================")


if __name__ == "__main__":
    orchestrator = WarehouseAuditOrchestrator()
    orchestrator.run_pipeline_audit()