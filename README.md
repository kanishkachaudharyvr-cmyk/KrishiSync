# KrishiSync 🌾

**KrishiSync** is a production-ready, voice-enabled agricultural ERP (Enterprise Resource Planning) and assistant platform designed specifically for farmers. It provides an intuitive, high-performance web dashboard coupled with a stateful AI agent driven by the Google Antigravity SDK and Sarvam AI regional speech-to-text API, enabling hands-free operation in multiple local languages.

---

## 🚀 Key Features

1. **🌾 Mandi & Finance Hub**: 
   - Compares live APMC market rates per quintal (seeded with Onion, Tomato, Wheat, Cotton, Potato, etc.).
   - Visualizes price trends using Chart.js interactive charts.
   - Tracks farmer crop loan timelines, repayment deadlines, and annual interest rates.

2. **🏥 Crop Health & Weather Advisory**:
   - Provides localized weather forecasts, humidity tracking, and weather condition monitoring.
   - Issues critical yellow warnings and localized pest prevention strategies based on current environmental metrics.

3. **📦 Inventory & Logistics Dispatch**:
   - Tracks stock levels of agricultural inputs (Urea, NPK fertilizers, seeds, organic compost) with visual progress bars.
   - Coordinates transport booking and logistics dispatch logs with assigned driver profiles, vehicles, and real-time ETAs.

4. **🎙️ KrishiSync AI Voice Assistant**:
   - Floating recording action widget enabling regional speech commands (transcribed and translated via Sarvam AI API).
   - Canvas-based audio waveform visualization using the HTML5 Web Audio API.
   - Highlights target dashboard components in real-time as stateful actions occur.
   - Provides fallback text command input.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Tailwind CSS, Chart.js, FontAwesome, Web Audio API (`MediaRecorder`, `AudioContext`, frequency analyser).
- **Backend**: Python 3 (FastAPI, Uvicorn, HTTPX for API routing).
- **Database**: SQLite (via SQLAlchemy 2.0 ORM) with automatic schema initialization and mock seeding.
- **AI Agent Framework**: Google Antigravity SDK (`google-antigravity`) with stateful tool actions.
- **Speech Layer**: Sarvam AI API for regional voice transcription, translating Indian language speech to English queries.

---

## 📁 Repository Structure

```
krishisync/
├── app.py           # FastAPI application & Antigravity Agent tools
├── models.py        # SQLAlchemy database schemas
├── index.html       # Unified frontend dashboard
├── requirements.txt # Python package dependencies
├── vercel.json      # Vercel deployment configuration
└── README.md        # Documentation
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

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd krishisync
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python app.py
   ```

4. **Open in browser**:
   Navigate to `http://127.0.0.1:8000` to interact with the KrishiSync dashboard.

---

## ☁️ Deploying on Vercel

KrishiSync is fully compatible with serverless Python deployment on Vercel.

1. Ensure `vercel.json` is in your project root.
2. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```
3. Deploy the application:
   ```bash
   vercel
   ```
4. Set environment variables on the Vercel dashboard:
   - `SARVAM_API_KEY`
   - `GOOGLE_APPLICATION_CREDENTIALS` (as JSON string or file mapping)
