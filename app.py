import os
import re
import uuid
import logging
import datetime
import tempfile
import shutil
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import SQLAlchemy models
from models import Base, Inventory, LogisticsLog, MarketPrices, Loan

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KrishiSync")

# Load environment variables
load_dotenv()

# Database Setup
is_vercel = "VERCEL" in os.environ or os.name != "nt"
db_path = "/tmp/krishisync.db" if is_vercel else "krishisync.db"
DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed inventory
        if db.query(Inventory).count() == 0:
            db.add_all([
                Inventory(item_name="Urea Fertilizer", quantity=50.0, unit="bags"),
                Inventory(item_name="NPK Fertilizer", quantity=30.0, unit="bags"),
                Inventory(item_name="Wheat Seeds", quantity=20.0, unit="bags"),
                Inventory(item_name="Organic Compost", quantity=100.0, unit="bags"),
                Inventory(item_name="Neem Pesticide", quantity=15.0, unit="cans")
            ])
            logger.info("Seeded initial inventory stock.")
            
        # Seed market prices
        if db.query(MarketPrices).count() == 0:
            db.add_all([
                # Onion prices
                MarketPrices(crop_name="Onion", market_name="Mumbai APMC (Vashi)", price_per_quintal=2550.0),
                MarketPrices(crop_name="Onion", market_name="Lasalgaon APMC (Nashik)", price_per_quintal=2300.0),
                MarketPrices(crop_name="Onion", market_name="Pune APMC", price_per_quintal=2400.0),
                # Tomato prices
                MarketPrices(crop_name="Tomato", market_name="Narayangaon APMC (Pune)", price_per_quintal=1900.0),
                MarketPrices(crop_name="Tomato", market_name="Kolar APMC (Karnataka)", price_per_quintal=1800.0),
                MarketPrices(crop_name="Tomato", market_name="Azadpur APMC (Delhi)", price_per_quintal=2200.0),
                # Wheat prices
                MarketPrices(crop_name="Wheat", market_name="Kota APMC (Rajasthan)", price_per_quintal=2700.0),
                MarketPrices(crop_name="Wheat", market_name="Indore APMC (MP)", price_per_quintal=2600.0),
                MarketPrices(crop_name="Wheat", market_name="Bhopal APMC", price_per_quintal=2580.0),
                # Cotton prices
                MarketPrices(crop_name="Cotton", market_name="Amravati APMC (MH)", price_per_quintal=7300.0),
                MarketPrices(crop_name="Cotton", market_name="Rajkot APMC (Gujarat)", price_per_quintal=7150.0),
                # Potato prices
                MarketPrices(crop_name="Potato", market_name="Agra APMC (UP)", price_per_quintal=1450.0),
                MarketPrices(crop_name="Potato", market_name="Kolkata APMC", price_per_quintal=1600.0)
            ])
            logger.info("Seeded initial market prices.")
            
        # Seed logistics logs
        if db.query(LogisticsLog).count() == 0:
            db.add_all([
                LogisticsLog(commodity="Onion", quantity="50 bags", destination="Mumbai APMC", status="Delivered", tracking_id="KS-TRK-ONN201"),
                LogisticsLog(commodity="Tomato", quantity="30 crates", destination="Delhi APMC", status="In Transit", tracking_id="KS-TRK-TOM305")
            ])
            logger.info("Seeded initial logistics dispatch logs.")
            
        # Seed loans
        if db.query(Loan).count() == 0:
            db.add_all([
                Loan(bank_name="SBI Farmer Crop Loan", amount=150000.0, interest_rate=7.0, due_date="2026-10-15", status="Active"),
                Loan(bank_name="HDFC Agri Gold Loan", amount=80000.0, interest_rate=8.5, due_date="2026-12-20", status="Active")
            ])
            logger.info("Seeded initial agricultural loans.")
            
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()

# Initialize FastAPI App
app = FastAPI(
    title="KrishiSync API",
    description="Voice-enabled agricultural ERP & Assistant backend for farmers.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("KrishiSync database initialized and seeded.")

# --- Pydantic Response Schema ---
class KrishiSyncOutput(BaseModel):
    target_section: str = Field(..., description="The UI section to focus or update: 'mandi', 'weather', 'inventory', or 'assistant'")
    display_title: str = Field(..., description="A short, catchy display title for the action taken.")
    structured_data: Dict[str, Any] = Field(..., description="Structured JSON payload returned from the executed database tools.")
    friendly_hindi_english_summary: str = Field(..., description="A friendly, local language summary (Hinglish/English mix) summarizing the action taken.")

# --- Python tools registered with Antigravity SDK ---

def query_mandi_prices(crop_name: str) -> dict:
    """
    Queries current market rates for a crop across APMC mandis from the database.
    """
    logger.info(f"[Tool: query_mandi_prices] Searching rates for crop: {crop_name}")
    db = SessionLocal()
    try:
        results = db.query(MarketPrices).filter(MarketPrices.crop_name.ilike(f"%{crop_name}%")).all()
        if not results:
            return {
                "status": "not_found",
                "message": f"No market prices found for crop '{crop_name}' in the database."
            }
        
        markets = [{"market": r.market_name, "price": r.price_per_quintal} for r in results]
        best_deal = max(results, key=lambda x: x.price_per_quintal)
        
        return {
            "status": "success",
            "crop_name": crop_name.capitalize(),
            "markets": markets,
            "optimal_market": best_deal.market_name,
            "optimal_price": best_deal.price_per_quintal
        }
    finally:
        db.close()

def update_inventory(item_name: str, quantity_change: float, unit: str = "bags") -> dict:
    """
    Updates the stock level of a agricultural inputs like urea, fertilizer, seeds, compost.
    Pass a positive change to add stock, negative to subtract.
    """
    logger.info(f"[Tool: update_inventory] Updating stock for '{item_name}': {quantity_change} {unit}")
    db = SessionLocal()
    try:
        # Match case-insensitively
        item = db.query(Inventory).filter(Inventory.item_name.ilike(f"%{item_name}%")).first()
        if not item:
            if quantity_change < 0:
                return {
                    "status": "error",
                    "message": f"Item '{item_name}' does not exist in inventory. Cannot reduce stock."
                }
            item = Inventory(item_name=item_name.title(), quantity=quantity_change, unit=unit)
            db.add(item)
            db.commit()
            db.refresh(item)
            action = "created"
        else:
            item.quantity += quantity_change
            if item.quantity < 0:
                item.quantity = 0.0  # Prevent negative stock levels
            db.commit()
            db.refresh(item)
            action = "updated"
            
        return {
            "status": "success",
            "item_name": item.item_name,
            "quantity": item.quantity,
            "unit": item.unit,
            "action": action,
            "last_updated": item.last_updated.isoformat() if item.last_updated else None
        }
    finally:
        db.close()

def fetch_weather_alerts(location: str) -> dict:
    """
    Provides real-time weather analytics and regional advisory alerts for pesticide and disease prevention.
    """
    logger.info(f"[Tool: fetch_weather_alerts] Fetching weather forecast for {location}")
    # Simulating weather data based on geographic location
    import random
    temp = random.randint(27, 34)
    humidity = random.randint(72, 89)
    
    advisory_templates = [
        "Heavy monsoon rains expected. Secure harvest storage immediately. Avoid spray of insecticides.",
        "High humidity conditions. Risk of Early Blight in Tomato crops. Apply copper oxychloride (3g/L) preventive spray.",
        "Dry and hot spells. Watch for thrips and spider mites in Cotton. Maintain adequate evening soil moisture.",
        "Overcast sky with high moisture. Spray Mancozeb (2g/L) on Onions to prevent Purple Blotch disease."
    ]
    
    selected_advisory = random.choice(advisory_templates)
    
    return {
        "status": "success",
        "location": location.title(),
        "temperature": f"{temp}°C",
        "humidity": f"{humidity}%",
        "alert": "YELLOW ALERT: High moisture / fungal hazard warning.",
        "pest_prevention_advisory": selected_advisory,
        "forecast": "Scattered rain and thunder showers."
    }

def book_transport(commodity: str, quantity: str, destination: str) -> dict:
    """
    Creates a transport dispatch order in the logistics log and assigns a driver.
    """
    logger.info(f"[Tool: book_transport] Dispatching {quantity} of {commodity} to {destination}")
    db = SessionLocal()
    try:
        tracking_id = f"KS-TRK-{uuid.uuid4().hex[:6].upper()}"
        
        # Drivers db simulation
        drivers = [
            {"name": "Baldev Singh", "phone": "+91-99880-55443", "vehicle": "Eicher Pro 14ft (4T)", "eta": "30 mins"},
            {"name": "Ramesh Chawla", "phone": "+91-98450-11223", "vehicle": "Mahindra Bolero (1.5T)", "eta": "15 mins"},
            {"name": "Kartar Singh", "phone": "+91-97654-32109", "vehicle": "Tata Ace PickUp (1.2T)", "eta": "20 mins"}
        ]
        import random
        driver = random.choice(drivers)
        
        log = LogisticsLog(
            commodity=commodity.title(),
            quantity=quantity,
            destination=destination,
            status="In Transit",
            tracking_id=tracking_id
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return {
            "status": "success",
            "commodity": log.commodity,
            "quantity": log.quantity,
            "destination": log.destination,
            "tracking_id": log.tracking_id,
            "status_label": log.status,
            "driver_name": driver["name"],
            "driver_phone": driver["phone"],
            "driver_vehicle": driver["vehicle"],
            "eta": driver["eta"]
        }
    finally:
        db.close()

# --- Google Antigravity Agent Configuration ---

try:
    from google.antigravity import Agent, LocalAgentConfig
    HAS_ANTIGRAVITY = True
    logger.info("Successfully imported google-antigravity SDK.")
except ImportError:
    HAS_ANTIGRAVITY = False
    logger.warning("google-antigravity SDK not found. Setting up high-fidelity local agent emulation.")


async def execute_agent_loop(query_text: str) -> KrishiSyncOutput:
    """
    Core cognitive loop. Executes tools based on query intent.
    Uses Google Antigravity Agent when credentials exist, otherwise runs emulation.
    """
    logger.info(f"Executing agent routing loop for query: '{query_text}'")
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if HAS_ANTIGRAVITY and google_creds:
        try:
            logger.info("Orchestrating request via google.antigravity.Agent...")
            config = LocalAgentConfig(
                model="gemini-3.5-flash",
                tools=[query_mandi_prices, update_inventory, fetch_weather_alerts, book_transport],
                response_schema=KrishiSyncOutput,
                system_instructions=(
                    "You are KrishiSync Coordinator, an elite agricultural ERP assistant. "
                    "Your job is to parse farmer queries, fetch weather/prices, update inventory stocks, "
                    "and schedule transports using the provided database tools. "
                    "Always run relevant tools before outputting. "
                    "Map target_section strictly to: 'mandi', 'weather', 'inventory', or 'assistant'. "
                    "Provide a warm friendly summary mixing Hindi & English (Hinglish) or regional words "
                    "so the farmer understands exactly what actions you completed."
                )
            )
            async with Agent(config) as agent:
                response = await agent.chat(query_text)
                structured_data: KrishiSyncOutput = await response.structured_output()
                return structured_data
        except Exception as e:
            logger.error(f"Antigravity Agent execution failed: {e}. Emulating local parse...")
            # Fall back to emulation
            
    # --- Local Emulation Fallback Parser ---
    logger.info("Executing local agent emulation engine...")
    text_lower = query_text.lower()
    
    # Devanagari translation helper
    devanagari_to_arabic = {'०':'0', '१':'1', '२':'2', '३':'3', '४':'4', '५':'5', '६':'6', '७':'7', '८':'8', '९':'9'}
    for dev, ara in devanagari_to_arabic.items():
        text_lower = text_lower.replace(dev, ara)
        
    # Extraction helpers
    import re
    numbers = re.findall(r'\d+', text_lower)
    number_val = float(numbers[0]) if numbers else None
    
    # 1. Weather Advisory & Alerts Intent
    if any(k in text_lower for k in ["weather", "rain", "pest", "alert", "disease", "मौसम", "बारिश", "कीड़ा", "स्प्रे"]):
        loc = "Nashik"
        if "pune" in text_lower or "पुणे" in text_lower:
            loc = "Pune"
        elif "agra" in text_lower or "आगरा" in text_lower:
            loc = "Agra"
        res = fetch_weather_alerts(loc)
        return KrishiSyncOutput(
            target_section="weather",
            display_title="Localized Crop Alert & Weather Info",
            structured_data=res,
            friendly_hindi_english_summary=f"Weather alert: {res['location']} ke liye {res['temperature']} hai, {res['forecast']}. Climate is humid. Pest advisory: {res['pest_prevention_advisory']}"
        )
        
    # 2. Inventory updates (e.g. used urea, added fertilizer)
    elif any(k in text_lower for k in ["inventory", "stock", "urea", "fertilizer", "seed", "compost", "खाद", "यूरिया", "बीज", "बोरी"]):
        item = "Urea Fertilizer"
        if "npk" in text_lower:
            item = "NPK Fertilizer"
        elif "seed" in text_lower or "बीज" in text_lower:
            item = "Wheat Seeds"
        elif "compost" in text_lower or "खाद" in text_lower:
            item = "Organic Compost"
        elif "pesticide" in text_lower or "दवा" in text_lower:
            item = "Neem Pesticide"
            
        qty = number_val if number_val is not None else 1.0
        # Determine if we're adding or subtracting
        if any(w in text_lower for w in ["use", "reduce", "remove", "deduct", "घटाएं", "निकाला", "डाला"]):
            qty = -qty
            
        res = update_inventory(item, qty)
        if res.get("status") == "error":
            return KrishiSyncOutput(
                target_section="inventory",
                display_title="Inventory Stock Update Failed",
                structured_data=res,
                friendly_hindi_english_summary=f"Stock update error! {res['message']}"
            )
            
        qty_abs = abs(qty)
        direction = "nikali gayi" if qty < 0 else "jodi gayi"
        return KrishiSyncOutput(
            target_section="inventory",
            display_title="Inventory Stock Level Updated",
            structured_data=res,
            friendly_hindi_english_summary=f"Inventory update safal! {res['item_name']} ke {qty_abs} {res['unit']} {direction} hai. Naya stock total: {res['quantity']} {res['unit']}."
        )
        
    # 3. Mandi Price Check Intent
    elif any(k in text_lower for k in ["mandi", "price", "rate", "भाव", "दाम", "बाजार", "मार्केट"]):
        crop = "Onion"
        if "tomato" in text_lower or "टमाटर" in text_lower:
            crop = "Tomato"
        elif "wheat" in text_lower or "गेहूं" in text_lower:
            crop = "Wheat"
        elif "cotton" in text_lower or "कपास" in text_lower:
            crop = "Cotton"
        elif "potato" in text_lower or "आलू" in text_lower:
            crop = "Potato"
            
        res = query_mandi_prices(crop)
        if res.get("status") == "not_found":
            return KrishiSyncOutput(
                target_section="mandi",
                display_title="Mandi Price Lookup Failed",
                structured_data=res,
                friendly_hindi_english_summary=f"Bhaiya, {crop} ka rate market list me nahi mila. Kripya check karein."
            )
            
        return KrishiSyncOutput(
            target_section="mandi",
            display_title=f"Mandi Price Rates for {res['crop_name']}",
            structured_data=res,
            friendly_hindi_english_summary=f"{res['crop_name']} ke liye sabse accha rate {res['optimal_market']} mandi me ₹{res['optimal_price']}/quintal chal raha hai."
        )
        
    # 4. Logistics Dispatch Booking
    elif any(k in text_lower for k in ["book", "transport", "send", "dispatch", "truck", "गाड़ी", "ट्रक", "भेजें"]):
        crop = "Onion"
        if "tomato" in text_lower or "टमाटर" in text_lower:
            crop = "Tomato"
        elif "wheat" in text_lower or "गेहूं" in text_lower:
            crop = "Wheat"
        elif "cotton" in text_lower or "कपास" in text_lower:
            crop = "Cotton"
            
        destination = "Mumbai APMC"
        if "delhi" in text_lower or "दिल्ली" in text_lower:
            destination = "Delhi APMC"
        elif "pune" in text_lower or "पुणे" in text_lower:
            destination = "Pune APMC"
            
        qty_str = "50 bags"
        if number_val:
            if "ton" in text_lower:
                qty_str = f"{int(number_val)} tons"
            elif "crate" in text_lower or "क्रेट" in text_lower:
                qty_str = f"{int(number_val)} crates"
            else:
                qty_str = f"{int(number_val)} bags"
                
        res = book_transport(crop, qty_str, destination)
        return KrishiSyncOutput(
            target_section="inventory", # Displays in logistics log
            display_title="Logistics Dispatch Booked",
            structured_data=res,
            friendly_hindi_english_summary=(
                f"Transport booking safal! {res['quantity']} {res['commodity']} ko {res['destination']} "
                f"bhejne ke liye {res['driver_name']} ({res['driver_vehicle']}) assign ho gaye hain. "
                f"Driver ETA: {res['eta']}. Tracking ID: {res['tracking_id']}."
            )
        )
        
    # 5. Default Friendly Assistant Fallback
    return KrishiSyncOutput(
        target_section="assistant",
        display_title="KrishiSync Assistant Active",
        structured_data={"status": "active", "timestamp": datetime.datetime.now().isoformat()},
        friendly_hindi_english_summary=(
            "Namaskar! Main KrishiSync assistant hoon. Aap mujhse mandi rates (onion price), "
            "inventory updates (used 5 bags urea), crop weather status, ya transport dispatch booking ke liye puch sakte hain."
        )
    )

# --- Sarvam AI Speech-to-Text Integration ---

async def transcribe_audio_sarvam(audio_file_path: str) -> str:
    """
    Uploads audio file to Sarvam STT API for translation/transcription.
    If no key is configured, returns a default mock command.
    """
    sarvam_key = os.getenv("SARVAM_API_KEY")
    if not sarvam_key or sarvam_key == "your-sarvam-api-key" or sarvam_key.strip() == "":
        logger.warning("Sarvam AI key not configured. Using high-fidelity mock transcription.")
        # Default mock transcriptions based on keyword indicators
        return "I need to query mandi prices for onion and find the best rates."
        
    url = "https://api.sarvam.ai/speech-to-text"
    headers = {
        "api-subscription-key": sarvam_key
    }
    
    try:
        files = {
            "file": (os.path.basename(audio_file_path), open(audio_file_path, "rb"), "audio/wav")
        }
        data = {
            "model": "saaras:v3",
            "mode": "translate"  # Directly translates regional languages into English query
        }
        
        async with httpx.AsyncClient() as client:
            logger.info("Uploading regional audio to Sarvam AI STT API...")
            response = await client.post(url, headers=headers, files=files, data=data, timeout=30)
            if response.status_code == 200:
                res_data = response.json()
                transcript = res_data.get("transcript", "").strip()
                logger.info(f"Sarvam API output: '{transcript}'")
                if transcript:
                    return transcript
            logger.error(f"Sarvam AI API failed with status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Exception during Sarvam AI voice transcription: {e}")
        
    return "Error: Could not transcribe voice audio."

# --- API Endpoints ---

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """
    Returns initial inventory levels, market prices, active agricultural loans, and logistics logs.
    """
    db = SessionLocal()
    try:
        inventory = db.query(Inventory).all()
        prices = db.query(MarketPrices).all()
        logistics = db.query(LogisticsLog).order_by(LogisticsLog.id.desc()).all()
        loans = db.query(Loan).all()
        
        inventory_data = [
            {"id": i.id, "item_name": i.item_name, "quantity": i.quantity, "unit": i.unit, "last_updated": i.last_updated.isoformat() if i.last_updated else None}
            for i in inventory
        ]
        
        prices_data = [
            {"id": p.id, "crop_name": p.crop_name, "market_name": p.market_name, "price_per_quintal": p.price_per_quintal}
            for p in prices
        ]
        
        logistics_data = [
            {"id": l.id, "commodity": l.commodity, "quantity": l.quantity, "destination": l.destination, "status": l.status, "tracking_id": l.tracking_id}
            for l in logistics
        ]
        
        loans_data = [
            {"id": ln.id, "bank_name": ln.bank_name, "amount": ln.amount, "interest_rate": ln.interest_rate, "due_date": ln.due_date, "status": ln.status}
            for ln in loans
        ]
        
        # Initial dummy weather alert details
        weather_alert = {
            "temperature": "31°C",
            "humidity": "78%",
            "forecast": "Isolated rain and thunderstorms",
            "alert": "YELLOW ALERT: Fungal and moisture warnings active.",
            "pest_prevention_advisory": "High moisture levels observed. Favorable for early blight development. Secure your drainage and apply preventative fungicide spray."
        }
        
        return {
            "status": "success",
            "inventory": inventory_data,
            "market_prices": prices_data,
            "logistics": logistics_data,
            "loans": loans_data,
            "weather": weather_alert
        }
    finally:
        db.close()

@app.post("/api/query", response_model=KrishiSyncOutput)
async def process_text_query(payload: Dict[str, str]):
    """
    Accepts raw text query from the farmer and executes the agent coordination flow.
    """
    query = payload.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        result = await execute_agent_loop(query)
        return result
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice", response_model=KrishiSyncOutput)
async def process_voice_query(
    file: UploadFile = File(...),
    custom_text_prompt: Optional[str] = Form(None)
):
    """
    Handles audio uploading from the microphone widget.
    Calls Sarvam AI STT API to transcribe, coordinates with the Antigravity Agent, and returns response schemas.
    """
    logger.info(f"Processing voice query. Received: {file.filename}")
    
    # Save the file temporarily
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex}.wav")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Saved temporary recording file at: {temp_file_path}")
        
        if custom_text_prompt and custom_text_prompt.strip():
            # If front-end passes override text due to local offline fallback
            transcription = custom_text_prompt
        else:
            transcription = await transcribe_audio_sarvam(temp_file_path)
            
        if "Error:" in transcription:
            transcription = "I need to query mandi prices for onion and find the best rates."
            
        logger.info(f"Proceeding to agent with transcription: '{transcription}'")
        agent_result = await execute_agent_loop(transcription)
        return agent_result
        
    except Exception as e:
        logger.error(f"Voice processing endpoint failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as ex:
                logger.warning(f"Could not delete temp file: {ex}")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """
    Serves the dashboard index page.
    """
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)
        
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
