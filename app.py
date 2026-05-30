import gradio as gr
import json
import traceback
from pathlib import Path
from src.vision_ocr import WarehouseVisionProcessor
from src.compliance_engine import RegulatoryComplianceEngine

# Initialize our core components
vision_processor = WarehouseVisionProcessor()
compliance_engine = RegulatoryComplianceEngine()


def run_cloud_audit(input_image, destination_country, declared_allergens_text):
    """Web app interface wrapper with maximum error diagnostic reporting."""
    if input_image is None:
        return "⚠️ Please upload an image asset to execute the vision layer audit."

    try:
        # 1. Parse manual text inputs for declared allergens
        allergens_list = [a.strip() for a in declared_allergens_text.split(",") if a.strip()]

        # 2. Build our system metadata record
        mock_record = {
            "destination_country": destination_country,
            "declared_allergens": allergens_list,
            "timestamp_inbound": "2026-05-30T12:00:00"
        }

        # 3. Process the image using the required (path, image_id) signature
        image_path = Path(input_image)
        vision_results = vision_processor.process_inbound_scan(image_path, "HF_UI_TEST")

        if not vision_results or "extracted_text" not in vision_results:
            return f"❌ Vision Engine Error: Returned invalid data.\nReceived: {vision_results}"

        # 4. Pass arguments exactly like the passing unit tests do (positional)
        compliance_results = compliance_engine.evaluate_compliance(
            vision_results["extracted_text"],
            mock_record
        )

        # 5. Structure a clean consolidated payload for the user interface display
        output_payload = {
            "Vision Insights": {
                "Confidence Score": f"{round(vision_results.get('ocr_confidence', 0) * 100, 2)}%",
                "Extracted Text Snippet": vision_results["extracted_text"][:300] + "..." if len(
                    vision_results["extracted_text"]) > 300 else vision_results["extracted_text"]
            },
            "Regulatory Audit Decision": {
                "Is Compliant": compliance_results.get("is_compliant", False),
                "Allergen Check Status": compliance_results.get("allergen_compliance", {}).get("status", False),
                "Faulty Target Areas Found": compliance_results.get("allergen_compliance", {}).get("faulty_items", []),
                "Expiry Metrics": compliance_results.get("expiry_compliance", {}).get("message", "N/A")
            }
        }

        return json.dumps(output_payload, indent=2)

    except Exception as e:
        # Capture the deep internal exception traceback and display it perfectly in the UI
        full_stack = traceback.format_exc()
        error_details = {
            "Status": "💥 Deep Pipeline Crash Context",
            "Error Type": str(type(e).__name__),
            "Error Message": str(e),
            "Full Stack Trace": full_stack.split("\n")  # Keeps the clean readable list format
        }
        return json.dumps(error_details, indent=2)


# --- Define the Gradio UI Layout Block ---
with gr.Blocks(title="B2B Warehouse CV Audit Station") as demo:
    gr.Markdown("# 🏬 B2B Retail Warehouse Computer Vision Compliance Station")
    gr.Markdown(
        "Drop an inbound product packaging label scan below to execute real-time Deep Learning character localization and cross-border regulatory rule validation.")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="filepath", label="Inbound Packaging Scan Image File")
            country_input = gr.Dropdown(choices=["DE", "FR", "UK"], value="DE",
                                        label="Target Distribution Country (Regulatory Profile)")
            allergen_input = gr.Textbox(placeholder="e.g., Milch, Gluten, Soy",
                                        label="Declared Inventory Allergens (Comma Separated)")
            submit_btn = gr.Button("Run Compliance Audit Pipeline", variant="primary")

        with gr.Column():
            output_display = gr.Code(language="json", label="Pipeline Audit Output Log Matrix")

    submit_btn.click(
        fn=run_cloud_audit,
        inputs=[image_input, country_input, allergen_input],
        outputs=output_display
    )

if __name__ == "__main__":
    demo.launch()