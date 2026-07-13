# KrishiSync 🌾 — HACKHAZARDS '26 Edition

**KrishiSync** is a comprehensive, secure, multi-lingual agricultural ERP (Enterprise Resource Planning) and AI assistant platform built specifically for Indian farmers. Developed solo for the **HACKHAZARDS '26** hackathon under a tight deadline, it bridges the digital gap for regional farmers by combining a modern, interactive web interface with hands-free Indic voice input.

*   **Live Web App Production URL**: [https://krishisync.vercel.app](https://krishisync.vercel.app)
*   **GitHub Repository**: [https://github.com/kanishkachaudharyvr-cmyk/krishisync](https://github.com/kanishkachaudharyvr-cmyk/krishisync)
*   **Local Backend Server**: `http://127.0.0.1:8000`

---

## 🚀 Key Features

1.  **🌾 Mandi Estimator & Logistics**:
    *   **Smart Calculator**: Simulates and estimates harvest payouts instantly based on crop selection (Onion, Tomato, Wheat, Cotton, Potato) and quality grade (Premium = 1.2x, Standard = 1.0x, Fair = 0.8x).
    *   **Dispatch Bookings**: Books transport orders directly to regional APMC mandis.
    *   **Dynamic Telemetry Geotracking**: Clicking "Track Shipment" programmatically moves the shipment's coordinates (transit lat/lng) 15% closer to its destination, showing a live animated progress bar.
    *   **Chart.js Panel**: Displays dynamic comparative base prices scaled according to the selected crop across different Indian mandis.

2.  **🏥 Crop Health & Weather Alerts**:
    *   Shows real-time weather metrics (Temperature, Humidity, Forecasts).
    *   Generates yellow warnings and pest advisories based on the farmer's state.
    *   Includes high-fidelity visuals of lush fields.

3.  **📦 Stock Control (ERP)**:
    *   Tracks inventory levels of essential farming inputs (Urea, NPK fertilizers, seeds, organic compost) with status bars.

4.  **🎙️ Indic AI Voice Assistant**:
    *   Floating mic layout with live canvas frequency audio visualizer waveform.
    *   Ingests regional voice recordings, transcribing and translating 22+ Indic dialects directly into English.
    *   Navigates and updates dashboard panels dynamically as the farmer speaks.

5.  **✨ Premium Aesthetic Features**:
    *   **Light & Dark Theme Switcher**: Toggle button to switch between deep slate dark theme and clean light theme. Settings are persisted in the browser.
    *   **Cursor Spotlight**: A glowing spotlight gradient follows the cursor behind cards.
    *   **On-Hover Animations**: Glassmorphic panels scale up softly on hover.

---

## 🛠️ Tech Stack

*   **Frontend**: HTML5, Tailwind CSS, Chart.js, FontAwesome, Web Audio API (`MediaRecorder`, `AudioContext`, frequency analyser).
*   **Backend**: Python 3 (FastAPI, Uvicorn, HTTPX for API routing).
*   **Database**: SQLite (via SQLAlchemy 2.0 ORM) with automatic schema initialization and mock seeding.
*   **AI Agent Framework**: Google Antigravity SDK (`google-antigravity`) with stateful tool actions.
*   **Speech Layer**: Sarvam AI API for regional voice transcription, translating Indian language speech to English queries.

---

## 📁 Repository Structure

```
krishisync/
├── app.py                         # Unified FastAPI application, SQLite schemas, & Antigravity Agent tools
├── index.html                     # Responsive single-page dashboard UI (CSS styles, JS handlers)
├── requirements.txt               # Python package dependencies
├── vercel.json                    # Vercel deployment configuration
├── lush_green_farm_field.png      # Generated high-definition farm crop field asset
└── indian_apmc_mandi_market.png   # Generated high-definition wholesale market logistics asset
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory:

```env
# Google Application Credentials (for Antigravity Agent)
GOOGLE_APPLICATION_CREDENTIALS="path/to/your/google-credentials.json"

# Sarvam AI API Key (for Voice STT Layer)
SARVAM_API_KEY="your-sarvam-api-key"
```

*Note: If no API keys or Google Credentials are configured, KrishiSync automatically enters a high-fidelity local emulation mode that simulates agent reasoning and voice translation, ensuring the application remains fully functional for demonstration purposes.*

---

## 💻 Local Setup & Execution

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/kanishkachaudharyvr-cmyk/krishisync.git
    cd krishisync
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the server**:
    ```bash
    python app.py
    ```

4.  **Open in browser**:
    Navigate to `http://127.0.0.1:8000` to interact with the KrishiSync dashboard.
