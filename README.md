# B2B Retail Warehouse CV Compliance Pipeline (UC_017)

An enterprise-grade MLOps and Computer Vision pipeline designed to automate regulatory compliance audits for inbound pallet shipments. The system uses localized text extraction to verify cross-border legal rules (shelf-life thresholds and allergen formatting) before inventory is committed to warehouse management systems.

## 🏗️ System Architecture

The pipeline processes scans through three distinct operational layers:
1. **Vision Core:** OpenCV adaptive binarization filters noise before passing matrices to an EasyOCR Deep Learning engine (CNN + LSTM).
2. **Quality Gate (MLOps):** Evaluates character confidence scores against an environmental data drift threshold, automatically isolating messy or distorted labels to a quarantine directory.
3. **Compliance Engine:** Executes regex lookarounds to verify target-market packaging laws (e.g., explicit bolding of declared allergens and minimum distribution shelf-life windows).

## 🚀 Getting Started

### 1. Environment Setup
Ensure you have Python 3.11+ installed. Install project dependencies:
```bash
pip install -r requirements.txt