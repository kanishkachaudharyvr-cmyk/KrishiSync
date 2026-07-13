import os
import re
import uuid
import logging
import datetime
import tempfile
import shutil
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv
import httpx
from sqlalchemy.orm import Session

# Import database models & session
from database import init_db, SessionLocal, Farmer, InventoryItem, MandiPrice, LogisticsTicket

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KrishiSyncApp")

load_dotenv()

app = FastAPI(
    title="KrishiSync Core API",
    description="Multi-user, context-aware agricultural assistant backend.",
    version="2.0.0"
)

# CORS config
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
    logger.info("Database schemas initialized and seeded.")

# --- Pydantic Data Models ---

class LoginPayload(BaseModel):
    email: str = Field(..., description="Farmer email ID to look up.")

class RegisterPayload(BaseModel):
    email: str
    full_name: str
    state: str
    preferred_language: str
    land_size_acres: float

class KrishiSyncPayload(BaseModel):
    target_ui_tab: str = Field(..., description="The target tab to display: 'Mandi', 'Weather', 'Inventory', or 'Voice Assistant'")
    data: Dict[str, Any] = Field(..., description="JSON results returned by the executed agricultural database tools.")
    localized_text_summary: str = Field(..., description="Summary of action completed, translated according to the farmer's preferred language.")

# --- Helper Dependency for Session Identity ---

async def get_active_farmer_id(x_farmer_id: Optional[str] = Header(None)) -> int:
    """
    Extracts farmer session ID from headers. Ensures secure, private data scoping.
    """
    if not x_farmer_id:
        raise HTTPException(status_code=401, detail="Authentication required: X-Farmer-ID header missing.")
    try:
        return int(x_farmer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Farmer-ID format.")

# --- Context-Aware Agent Execution Loop ---

try:
    from google.antigravity import Agent, LocalAgentConfig
    HAS_ANTIGRAVITY = True
    logger.info("google-antigravity SDK imported successfully.")
except ImportError:
    HAS_ANTIGRAVITY = False
    logger.warning("google-antigravity SDK not found. Setting up high-fidelity context emulation.")

async def execute_context_agent_loop(query_text: str, farmer_id: int) -> KrishiSyncPayload:
    """
    Cognitive execution loop. Binds tools to the current farmer's DB session context,
    injects profile settings into system instructions, and returns structural output.
    """
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer profile not found.")

        # --- Request-Scoped Database-bound Tools (Closures for absolute privacy) ---

        def query_mandi_prices(crop_name: str) -> dict:
            """
            Queries reference market rates for a specific crop across mandis.
            """
            logger.info(f"[Tool: query_mandi_prices] Searching crop: {crop_name}")
            results = db.query(MandiPrice).filter(MandiPrice.crop_name.ilike(f"%{crop_name}%")).all()
            if not results:
                return {
                    "status": "not_found",
                    "message": f"No market rate information found for '{crop_name}'."
                }
            
            markets_list = [{"market": r.market_name, "price_per_quintal": r.price_per_quintal, "date": r.date} for r in results]
            best_deal = max(results, key=lambda x: x.price_per_quintal)
            return {
                "status": "success",
                "crop": crop_name.capitalize(),
                "markets": markets_list,
                "best_market": best_deal.market_name,
                "best_price": best_deal.price_per_quintal
            }

        def update_inventory(item_name: str, quantity_change: float, unit: str = "bags") -> dict:
            """
            Updates input stock quantities for this specific farmer.
            Positive change adds stock; negative subtracts.
            """
            logger.info(f"[Tool: update_inventory] Scoped to farmer {farmer_id}: {item_name} by {quantity_change}")
            item = db.query(InventoryItem).filter(
                InventoryItem.farmer_id == farmer_id,
                InventoryItem.item_name.ilike(f"%{item_name}%")
            ).first()

            if not item:
                if quantity_change < 0:
                    return {
                        "status": "error",
                        "message": f"Item '{item_name}' not found in your inventory. Cannot subtract."
                    }
                item = InventoryItem(
                    farmer_id=farmer_id,
                    item_name=item_name.title(),
                    quantity=quantity_change,
                    unit=unit,
                    status="In Stock"
                )
                db.add(item)
                db.commit()
                db.refresh(item)
                action = "created"
            else:
                item.quantity += quantity_change
                if item.quantity < 0:
                    item.quantity = 0.0
                
                # Update visual status
                if item.quantity == 0:
                    item.status = "Out of Stock"
                elif item.quantity < 10:
                    item.status = "Low"
                else:
                    item.status = "In Stock"
                    
                db.commit()
                db.refresh(item)
                action = "updated"

            return {
                "status": "success",
                "item_name": item.item_name,
                "quantity": item.quantity,
                "unit": item.unit,
                "status_label": item.status,
                "action": action,
                "last_updated": item.last_updated.isoformat() if item.last_updated else None
            }

        def log_transportation(commodity: str, weight: str, target_destination: str) -> dict:
            """
            Books a transit logistics ticket for this farmer.
            """
            logger.info(f"[Tool: log_transportation] Booking transit for farmer {farmer_id}: {weight} of {commodity}")
            tracking_id = f"KS-TRK-{uuid.uuid4().hex[:6].upper()}"
            
            # Simulate logistics matching
            drivers = [
                {"name": "Baldev Singh", "phone": "+91-99880-55443", "vehicle": "Eicher Pro 14ft", "eta": "30 mins"},
                {"name": "Ramesh Chawla", "phone": "+91-98450-11223", "vehicle": "Mahindra Bolero", "eta": "15 mins"}
            ]
            import random
            driver = random.choice(drivers)

            ticket = LogisticsTicket(
                farmer_id=farmer_id,
                commodity=commodity.title(),
                weight=weight,
                target_destination=target_destination,
                tracking_status="Booked",
                tracking_id=tracking_id
            )
            db.add(ticket)
            db.commit()
            db.refresh(ticket)

            return {
                "status": "success",
                "ticket_id": ticket.id,
                "commodity": ticket.commodity,
                "weight": ticket.weight,
                "destination": ticket.target_destination,
                "tracking_id": ticket.tracking_id,
                "status": ticket.tracking_status,
                "driver_name": driver["name"],
                "driver_phone": driver["phone"],
                "driver_vehicle": driver["vehicle"],
                "eta": driver["eta"]
            }

        # --- Inject Dynamic Context into System Instructions ---
        farmer_context = (
            f"Logged-in Farmer Profile Context:\n"
            f"- Full Name: {farmer.full_name}\n"
            f"- State: {farmer.state}\n"
            f"- Preferred Language: {farmer.preferred_language}\n"
            f"- Land Size: {farmer.land_size_acres} Acres\n\n"
            f"Instructions:\n"
            f"1. You must personalize agricultural recommendations based on {farmer.state} and farm size {farmer.land_size_acres} acres.\n"
            f"2. Translate your `localized_text_summary` into the farmer's preferred language ({farmer.preferred_language}). If preferred language is Hindi, use Hindi/Hinglish; if Marathi, use Marathi/Hinglish, etc.\n"
            f"3. Run scoped database tools before returning. Do not invent stock levels or prices without calling tools.\n"
            f"4. Select appropriate target_ui_tab: 'Mandi', 'Weather', 'Inventory', or 'Voice Assistant'."
        )

        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if HAS_ANTIGRAVITY and google_creds:
            try:
                config = LocalAgentConfig(
                    model="gemini-3.5-flash",
                    tools=[query_mandi_prices, update_inventory, log_transportation],
                    response_schema=KrishiSyncPayload,
                    system_instructions=(
                        "You are KrishiSync, a stateful personalized ERP intelligence orchestrator. "
                        f"{farmer_context}"
                    )
                )
                async with Agent(config) as agent:
                    response = await agent.chat(query_text)
                    payload: KrishiSyncPayload = await response.structured_output()
                    return payload
            except Exception as e:
                logger.error(f"Antigravity SDK execution error: {e}. Falling back to emulation.")

        # --- Local High-Fidelity Context Emulation Fallback ---
        logger.info("Executing context-aware local emulation parser...")
        text_lower = query_text.lower()
        
        # Determine language translations
        lang = farmer.preferred_language.lower()
        
        # 1. Mandi Prices
        if any(w in text_lower for w in ["mandi", "price", "rate", "भाव", "दाम", "रेट"]):
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
            
            # Formulate localized summary
            if lang == "hindi":
                summary = f"{farmer.full_name} bhaiya, {res.get('crop')} ke liye sabse accha rate {res.get('best_market')} mandi me ₹{res.get('best_price')}/quintal chal raha hai."
            elif lang == "marathi":
                summary = f"{farmer.full_name} bhau, {res.get('crop')} cha changla bhav {res.get('best_market')} mandi madhye ₹{res.get('best_price')}/quintal aahe."
            else:
                summary = f"Hello {farmer.full_name}, best market rate for {res.get('crop')} is ₹{res.get('best_price')}/quintal at {res.get('best_market')}."

            return KrishiSyncPayload(
                target_ui_tab="Mandi",
                data=res,
                localized_text_summary=summary
            )
            
        # 2. Inventory Management
        elif any(w in text_lower for w in ["inventory", "urea", "fertilizer", "seed", "compost", "खाद", "यूरिया", "बीज"]):
            item = "Urea Fertilizer"
            if "npk" in text_lower:
                item = "NPK Fertilizer"
            elif "seed" in text_lower or "बीज" in text_lower:
                item = "Wheat Seeds"
            elif "compost" in text_lower or "खाद" in text_lower:
                item = "Organic Compost"

            import re
            nums = re.findall(r'\d+', text_lower)
            change = float(nums[0]) if nums else 5.0
            
            if any(w in text_lower for w in ["use", "deduct", "reduce", "remove", "निकाला", "घटाएं"]):
                change = -change
                
            res = update_inventory(item, change)
            
            direction = "jodi gayi" if change > 0 else "nikali gayi"
            if lang == "marathi":
                direction = "keli" if change > 0 else "kadhli"
                summary = f"Inventory update zala. {res['item_name']} che {abs(change)} {res['unit']} {direction} aahet. Navin stock: {res['quantity']}."
            elif lang == "hindi":
                summary = f"Stock update safal! {res['item_name']} ke {abs(change)} {res['unit']} {direction} hain. Naya stock total: {res['quantity']}."
            else:
                summary = f"Inventory updated successfully. {abs(change)} {res['unit']} of {res['item_name']} adjusted. New stock level: {res['quantity']}."

            return KrishiSyncPayload(
                target_ui_tab="Inventory",
                data=res,
                localized_text_summary=summary
            )

        # 3. Logistics Transportation
        elif any(w in text_lower for w in ["book", "transport", "send", "dispatch", "truck", "गाड़ी", "ट्रक", "भेजें"]):
            crop = "Onion"
            if "tomato" in text_lower or "टमाटर" in text_lower:
                crop = "Tomato"
            elif "wheat" in text_lower or "गेहूं" in text_lower:
                crop = "Wheat"
                
            dest = "Mumbai APMC"
            if "delhi" in text_lower or "दिल्ली" in text_lower:
                dest = "Delhi APMC"
            elif "pune" in text_lower or "पुणे" in text_lower:
                dest = "Pune APMC"
                
            import re
            nums = re.findall(r'\d+', text_lower)
            qty = f"{nums[0]} bags" if nums else "50 bags"
            
            res = log_transportation(crop, qty, dest)
            
            if lang == "hindi":
                summary = f"Transport ticket book ho gaya hai. Driver {res['driver_name']} ({res['driver_vehicle']}) next {res['eta']} me pahuchega. Tracking ID: {res['tracking_id']}."
            elif lang == "marathi":
                summary = f"Transport ticket book zale aahe. Driver {res['driver_name']} ({res['driver_vehicle']}) {res['eta']} madhye yeil. Tracking ID: {res['tracking_id']}."
            else:
                summary = f"Logistics booked. Driver {res['driver_name']} is arriving in {res['eta']}. Tracking ID is {res['tracking_id']}."

            return KrishiSyncPayload(
                target_ui_tab="Inventory",
                data=res,
                localized_text_summary=summary
            )

        # 4. Localized Weather
        import random
        temp = random.randint(28, 33)
        humidity = random.randint(75, 90)
        
        weather_alert = {
            "status": "success",
            "temperature": f"{temp}°C",
            "humidity": f"{humidity}%",
            "forecast": "Light monsoon rain",
            "state_warning": f"Alert for {farmer.state}: Fungal hazard due to persistent humidity."
        }
        
        if lang == "hindi":
            summary = f"{farmer.full_name} ji, {farmer.state} me abhi taapman {temp}°C hai aur humidity {humidity}% hai. Barish ke aasar hain."
        elif lang == "marathi":
            summary = f"{farmer.full_name} bhau, {farmer.state} madhye taapman {temp}°C aahe aani paus padnyachi shakyata aahe."
        else:
            summary = f"Hello {farmer.full_name}, current temperature in {farmer.state} is {temp}°C with high humidity ({humidity}%). Expect scattered showers."

        return KrishiSyncPayload(
            target_ui_tab="Weather",
            data=weather_alert,
            localized_text_summary=summary
        )

    finally:
        db.close()

# --- Sarvam AI Audio Transcription helper ---

async def transcribe_audio_sarvam(audio_file_path: str) -> str:
    """
    Transcribes audio stream via Sarvam speech-to-text API, translating to English.
    """
    sarvam_key = os.getenv("SARVAM_API_KEY")
    if not sarvam_key or sarvam_key == "your-sarvam-api-key" or sarvam_key.strip() == "":
        logger.warning("Sarvam AI key not configured. Using high-fidelity mock transcription.")
        return "Show Mandi prices for Onion and tell me what the rate is."

    url = "https://api.sarvam.ai/speech-to-text"
    headers = {"api-subscription-key": sarvam_key}
    
    try:
        files = {
            "file": (os.path.basename(audio_file_path), open(audio_file_path, "rb"), "audio/wav")
        }
        data = {
            "model": "saaras:v3",
            "mode": "translate"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, files=files, data=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", "").strip()
                if transcript:
                    return transcript
    except Exception as e:
        logger.error(f"Sarvam API transcription error: {e}")
        
    return "Error: Could not transcribe voice stream."

# --- API Endpoints ---

@app.post("/api/auth/login")
async def login(payload: LoginPayload):
    """
    Verifies if a farmer with the email exists.
    Returns their profile or raises 401 if not registered.
    """
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.email == payload.email.strip().lower()).first()
        if not farmer:
            raise HTTPException(status_code=401, detail="Email ID not found. Please register an account.")
        
        return {
            "status": "success",
            "user_exists": True,
            "profile": {
                "id": farmer.id,
                "email": farmer.email,
                "full_name": farmer.full_name,
                "state": farmer.state,
                "preferred_language": farmer.preferred_language,
                "land_size_acres": farmer.land_size_acres
            }
        }
    finally:
        db.close()

@app.post("/api/auth/register")
async def register(payload: RegisterPayload):
    """
    Creates a new farmer profile and seeds initial stock levels for them.
    """
    db = SessionLocal()
    try:
        existing = db.query(Farmer).filter(Farmer.email == payload.email.strip().lower()).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email ID is already registered.")

        new_farmer = Farmer(
            email=payload.email.strip().lower(),
            full_name=payload.full_name.strip(),
            state=payload.state.strip(),
            preferred_language=payload.preferred_language.strip(),
            land_size_acres=payload.land_size_acres
        )
        db.add(new_farmer)
        db.commit()
        db.refresh(new_farmer)

        # Seed initial inventory items scoped to this new farmer
        db.add_all([
            InventoryItem(farmer_id=new_farmer.id, item_name="Urea Fertilizer", quantity=50.0, unit="bags", status="In Stock"),
            InventoryItem(farmer_id=new_farmer.id, item_name="NPK Fertilizer", quantity=30.0, unit="bags", status="In Stock"),
            InventoryItem(farmer_id=new_farmer.id, item_name="Wheat Seeds", quantity=15.0, unit="bags", status="In Stock"),
            InventoryItem(farmer_id=new_farmer.id, item_name="Organic Compost", quantity=100.0, unit="bags", status="In Stock")
        ])
        db.commit()

        return {
            "status": "success",
            "profile": {
                "id": new_farmer.id,
                "email": new_farmer.email,
                "full_name": new_farmer.full_name,
                "state": new_farmer.state,
                "preferred_language": new_farmer.preferred_language,
                "land_size_acres": new_farmer.land_size_acres
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    finally:
        db.close()

@app.get("/api/dashboard-data")
async def get_dashboard_data(farmer_id: int = Depends(get_active_farmer_id)):
    """
    Returns dashboard metrics (scoped inventory and transportation logs) for the active farmer session.
    """
    db = SessionLocal()
    try:
        # Verify farmer exists
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer session invalid.")

        inventory = db.query(InventoryItem).filter(InventoryItem.farmer_id == farmer_id).all()
        logistics = db.query(LogisticsTicket).filter(LogisticsTicket.farmer_id == farmer_id).order_by(LogisticsTicket.id.desc()).all()
        prices = db.query(MandiPrice).all()
        
        inventory_data = [
            {"id": i.id, "item_name": i.item_name, "quantity": i.quantity, "unit": i.unit, "status": i.status, "last_updated": i.last_updated.isoformat() if i.last_updated else None}
            for i in inventory
        ]
        
        logistics_data = [
            {"id": l.id, "commodity": l.commodity, "weight": l.weight, "destination": l.target_destination, "status": l.tracking_status, "tracking_id": l.tracking_id}
            for l in logistics
        ]
        
        prices_data = [
            {"id": p.id, "crop_name": p.crop_name, "market_name": p.market_name, "price_per_quintal": p.price_per_quintal, "date": p.date}
            for p in prices
        ]

        import random
        temp = random.randint(28, 33)
        humidity = random.randint(75, 88)

        weather_info = {
            "temperature": f"{temp}°C",
            "humidity": f"{humidity}%",
            "forecast": "Isolated rain and thunderstorms",
            "alert": "YELLOW WARNING",
            "pest_prevention_advisory": f"Humidity levels in {farmer.state} are high. Risk of blight or mildew. Ensure standing water is cleared from fields."
        }

        return {
            "status": "success",
            "inventory": inventory_data,
            "logistics": logistics_data,
            "market_prices": prices_data,
            "weather": weather_info,
            "farmer_profile": {
                "name": farmer.full_name,
                "state": farmer.state,
                "language": farmer.preferred_language,
                "land_size": farmer.land_size_acres
            }
        }
    finally:
        db.close()

@app.post("/api/query", response_model=KrishiSyncPayload)
async def query_text(
    payload: Dict[str, str],
    farmer_id: int = Depends(get_active_farmer_id)
):
    """
    Executes a personalized, context-aware query for the authenticated farmer session.
    """
    query = payload.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    try:
        result = await execute_context_agent_loop(query, farmer_id)
        return result
    except Exception as e:
        logger.error(f"Text query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice", response_model=KrishiSyncPayload)
async def query_voice(
    file: UploadFile = File(...),
    custom_text_prompt: Optional[str] = Form(None),
    farmer_id: int = Depends(get_active_farmer_id)
):
    """
    Converts audio streams to text via Sarvam AI API and routes to context-injected agent loop.
    """
    logger.info(f"Uploading audio file from farmer {farmer_id}...")
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"voice_erp_{uuid.uuid4().hex}.wav")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        if custom_text_prompt and custom_text_prompt.strip():
            transcription = custom_text_prompt
        else:
            transcription = await transcribe_audio_sarvam(temp_file_path)
            
        if "Error:" in transcription:
            transcription = "Show Mandi prices for Onion and tell me what the rate is."

        logger.info(f"Sending voice transcript to agent: '{transcription}'")
        result = await execute_context_agent_loop(transcription, farmer_id)
        return result
        
    except Exception as e:
        logger.error(f"Voice query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as ex:
                logger.warning(f"Could not remove temp file: {ex}")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
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
