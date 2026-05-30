# Preprocessing with OpenCV and text localization via EasyOCR

import os
import cv2
import easyocr
import numpy as np
from pathlib import Path
import mlflow


class WarehouseVisionProcessor:
    def __init__(self):
        # Initialize EasyOCR reader for German, French, and English text spaces
        # download will trigger automatically on the first execution run
        self.reader = easyocr.Reader(['de', 'fr', 'en'], gpu=False)

    def preprocess_image(self, image_path: Path) -> np.ndarray:
        """Applies advanced computer vision preprocessing filters to boost OCR accuracy."""
        # Read image in grayscale
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Could not load image asset at: {image_path}")

        # Apply adaptive thresholding to eliminate shadows and uneven warehouse lighting
        processed_img = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return processed_img

    def extract_text_from_matrix(self, image_matrix: np.ndarray) -> tuple[str, float]:
        """Runs local character localization and outputs string blobs with confidence intervals."""
        # EasyOCR reads the image matrix directly
        results = self.reader.readtext(image_matrix)

        text_segments = []
        confidences = []

        for (bbox, text, prob) in results:
            text_segments.append(text)
            confidences.append(prob)

        # Calculate overall baseline confidence score for the image scan
        mean_confidence = float(np.mean(confidences)) if confidences else 0.0
        combined_text = " ".join(text_segments)

        return combined_text, mean_confidence

    def process_inbound_scan(self, image_path: Path, image_id: str) -> dict:
        """Processes an incoming image scan and logs baseline performance metrics to MLflow."""
        try:
            # Preprocess and execute text extraction
            cleaned_matrix = self.preprocess_image(image_path)
            extracted_text, confidence = self.extract_text_from_matrix(cleaned_matrix)

            # Log vision engine stats directly into the current active MLflow experiment run
            mlflow.log_metric(f"ocr_confidence_{image_id}", confidence)

            return {
                "image_id": image_id,
                "extracted_text": extracted_text,
                "ocr_confidence": confidence,
                "status": "SUCCESS"
            }
        except Exception as e:
            return {
                "image_id": image_id,
                "extracted_text": "",
                "ocr_confidence": 0.0,
                "status": f"FAILED: {str(e)}"
            }


if __name__ == "__main__":
    print("Vision OCR module compiled successfully. Awaiting orchestration pipeline execution.")