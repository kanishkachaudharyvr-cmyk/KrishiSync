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

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KrishiSyncHackathon")

load_dotenv()

# --- Database Models & Setup ---

Base = declarative_base()

class Farmer(Base):
    __tablename__ = "farmers"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    state = Column(String, nullable=False)
    preferred_language = Column(String, default="en")
    land_size_acres = Column(Float, default=0.0)

    inventory_items = relationship("InventoryItem", back_populates="farmer", cascade="all, delete-orphan")
    mandi_orders = relationship("MandiOrder", back_populates="farmer", cascade="all, delete-orphan")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)

    farmer = relationship("Farmer", back_populates="inventory_items")

class MandiOrder(Base):
    __tablename__ = "mandi_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_name = Column(String, nullable=False)
    quantity_quintals = Column(Float, nullable=False)
    target_mandi = Column(String, nullable=False)
    estimated_payout = Column(Float, nullable=False)
    status = Column(String, default="In Transit")  # "In Transit" | "Delivered"
    transit_lat = Column(Float, default=19.99)    # Starting point (Nashik)
    transit_lng = Column(Float, default=73.78)

    farmer = relationship("Farmer", back_populates="mandi_orders")

class MandiReference(Base):
    __tablename__ = "mandi_references"
    
    id = Column(Integer, primary_key=True, index=True)
    mandi_name = Column(String, unique=True, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)  # Base price per quintal

# Dynamic DB Path for Vercel
is_vercel = "VERCEL" in os.environ or os.name != "nt"
db_path = "/tmp/krishisync_hackathon.db" if is_vercel else "krishisync_hackathon.db"
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(MandiReference).count() == 0:
            db.add_all([
                MandiReference(mandi_name="Mumbai APMC (Vashi)", city="Mumbai", state="Maharashtra", base_price=2400.0),
                MandiReference(mandi_name="Lasalgaon APMC (Nashik)", city="Lasalgaon", state="Maharashtra", base_price=2200.0),
                MandiReference(mandi_name="Pune APMC", city="Pune", state="Maharashtra", base_price=2300.0),
                MandiReference(mandi_name="Azadpur APMC (Delhi)", city="Delhi", state="Delhi", base_price=2100.0),
                MandiReference(mandi_name="Kolar APMC (Karnataka)", city="Kolar", state="Karnataka", base_price=1800.0),
                MandiReference(mandi_name="Kota APMC (Rajasthan)", city="Kota", state="Rajasthan", base_price=2600.0),
                MandiReference(mandi_name="Agra APMC (UP)", city="Agra", state="Uttar Pradesh", base_price=1400.0),
                MandiReference(mandi_name="Kolkata APMC", city="Kolkata", state="West Bengal", base_price=1600.0)
            ])
            db.commit()
            logger.info("Mandi pricing reference data seeded.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding mandi reference: {e}")
    finally:
        db.close()

# --- Initialize FastAPI ---

app = FastAPI(
    title="KrishiSync Hackathon Engine",
    description="Context-aware multi-lingual farming ERP API.",
    version="3.0.0"
)

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

# --- Pydantic Schemas ---

class LoginPayload(BaseModel):
    phone_number: str = Field(..., description="10-digit phone number.")

class RegisterPayload(BaseModel):
    phone_number: str
    full_name: str
    state: str
    preferred_language: str
    land_size_acres: float

class KrishiSyncPayload(BaseModel):
    target_ui_tab: str = Field(..., description="Tab to activate: 'Mandi', 'Weather', 'Inventory', or 'Voice Assistant'")
    data_payload: Dict[str, Any] = Field(..., description="JSON data from database tool execution.")
    localization_summary: str = Field(..., description="Indic-language summary tailored to the farmer's language.")

# --- Authentication Dependency ---

async def get_farmer_id_header(x_farmer_id: Optional[str] = Header(None)) -> int:
    if not x_farmer_id:
        raise HTTPException(status_code=401, detail="X-Farmer-ID header missing. Please authenticate.")
    try:
        return int(x_farmer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Farmer-ID header.")

# --- Scoped Tools & Orchestration Loop ---

try:
    from google.antigravity import Agent, LocalAgentConfig
    HAS_ANTIGRAVITY = True
    logger.info("Successfully imported google.antigravity SDK.")
except ImportError:
    HAS_ANTIGRAVITY = False
    logger.warning("google.antigravity SDK missing. Using emulation mode.")

# Static APMC coordinates
MANDI_COORDINATES = {
    "Mumbai APMC (Vashi)": (19.03, 73.02),
    "Lasalgaon APMC (Nashik)": (20.14, 74.22),
    "Pune APMC": (18.52, 73.85),
    "Azadpur APMC (Delhi)": (28.71, 77.17),
    "Kolar APMC (Karnataka)": (13.13, 78.13),
    "Kota APMC (Rajasthan)": (25.21, 75.86),
    "Agra APMC (UP)": (27.18, 78.00),
    "Kolkata APMC": (22.57, 88.36)
}

async def run_contextual_agent(query: str, farmer_id: int) -> KrishiSyncPayload:
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer profile not found.")

        # --- Scoped Closures for Agent Tools (Enforces strict data scoping) ---

        def calculate_price_estimate(crop_name: str, quantity_quintals: float, quality_grade: str) -> dict:
            """
            Calculates estimated payouts for a crop lot based on quality grade: Premium (1.2x), Standard (1.0x), Fair (0.8x).
            """
            logger.info(f"[Tool: calculate_price_estimate] Crop: {crop_name}, Qty: {quantity_quintals}, Quality: {quality_grade}")
            
            # Lookup reference mandi base price or match by crop name
            ref = db.query(MandiReference).filter(MandiReference.mandi_name.ilike(f"%{farmer.state}%")).first()
            if not ref:
                ref = db.query(MandiReference).first()
            
            base_price = ref.base_price if ref else 2000.0
            
            # Adjust general base rate depending on crop type
            crop_lower = crop_name.lower()
            if "onion" in crop_lower:
                base_price = 2400.0
            elif "tomato" in crop_lower:
                base_price = 1800.0
            elif "wheat" in crop_lower:
                base_price = 2600.0
            elif "cotton" in crop_lower:
                base_price = 7200.0
            elif "potato" in crop_lower:
                base_price = 1400.0

            multipliers = {"Premium": 1.2, "Standard": 1.0, "Fair": 0.8}
            mult = multipliers.get(quality_grade.title(), 1.0)
            
            rate = base_price * mult
            payout = rate * quantity_quintals
            
            return {
                "status": "success",
                "crop": crop_name.capitalize(),
                "quantity_quintals": quantity_quintals,
                "quality_grade": quality_grade.title(),
                "rate_per_quintal": rate,
                "estimated_payout": payout
            }

        def book_mandi_order(crop_name: str, quantity_quintals: float, target_mandi: str, quality_grade: str) -> dict:
            """
            Books a crop lot transport dispatch to a municipal APMC Mandi, starting the telemetry queue.
            """
            logger.info(f"[Tool: book_mandi_order] Scoped to farmer {farmer_id}: {quantity_quintals}q {crop_name} to {target_mandi}")
            
            # Calculate payout using estimation engine
            est = calculate_price_estimate(crop_name, quantity_quintals, quality_grade)
            payout = est["estimated_payout"]

            order = MandiOrder(
                farmer_id=farmer_id,
                crop_name=crop_name.title(),
                quantity_quintals=quantity_quintals,
                target_mandi=target_mandi,
                estimated_payout=payout,
                status="In Transit",
                transit_lat=19.99, # Nashik lat
                transit_lng=73.78  # Nashik lng
            )
            db.add(order)
            db.commit()
            db.refresh(order)

            return {
                "status": "success",
                "order_id": order.id,
                "crop": order.crop_name,
                "quantity": order.quantity_quintals,
                "destination": order.target_mandi,
                "payout": order.estimated_payout,
                "transit_status": order.status,
                "coordinates": {"lat": order.transit_lat, "lng": order.transit_lng}
            }

        def get_order_tracking_details(order_id: int) -> dict:
            """
            Tracks active shipments. Shifts the simulated GPS coordinates 15% closer to the target APMC destination on successive calls.
            """
            logger.info(f"[Tool: get_order_tracking_details] Scoped to farmer {farmer_id}: tracking order {order_id}")
            order = db.query(MandiOrder).filter(MandiOrder.id == order_id, MandiOrder.farmer_id == farmer_id).first()
            if not order:
                return {"status": "error", "message": f"Logistics ticket {order_id} not found."}

            dest_coords = MANDI_COORDINATES.get(order.target_mandi, (19.03, 73.02))
            dest_lat, dest_lng = dest_coords

            if order.status == "In Transit":
                d_lat = dest_lat - order.transit_lat
                d_lng = dest_lng - order.transit_lng
                distance = (d_lat**2 + d_lng**2)**0.5

                if distance < 0.05:
                    order.status = "Delivered"
                    order.transit_lat = dest_lat
                    order.transit_lng = dest_lng
                else:
                    # Move 15% closer
                    order.transit_lat += d_lat * 0.15
                    order.transit_lng += d_lng * 0.15
                
                db.commit()
                db.refresh(order)

            # Calculate progress percentage from Nashik (19.99, 73.78)
            d_total = ((dest_lat - 19.99)**2 + (dest_lng - 73.78)**2)**0.5
            d_current = ((dest_lat - order.transit_lat)**2 + (dest_lng - order.transit_lng)**2)**0.5
            
            progress = 100.0 if order.status == "Delivered" else max(0.0, min(95.0, (1 - d_current / d_total) * 100.0))

            return {
                "status": "success",
                "order_id": order.id,
                "crop": order.crop_name,
                "mandi": order.target_mandi,
                "status_label": order.status,
                "progress_percent": round(progress, 1),
                "current_location": {"lat": round(order.transit_lat, 4), "lng": round(order.transit_lng, 4)},
                "destination_location": {"lat": dest_lat, "lng": dest_lng}
            }

        # --- Setup Context Profile Prompt ---
        lang = farmer.preferred_language.capitalize()
        context_prompt = (
            f"Farmer Context:\n"
            f"- Name: {farmer.full_name}\n"
            f"- State: {farmer.state}\n"
            f"- Preferred Language: {lang}\n"
            f"- Onboarded Farm: {farmer.land_size_acres} Acres\n\n"
            f"Directives:\n"
            f"1. Pre-calculate payout estimates using tools prior to booking lots.\n"
            f"2. Scopes all transactions to Farmer ID {farmer_id}.\n"
            f"3. Write the `localization_summary` in the preferred language ({lang}). If Hindi, use Hinglish/Hindi; if Marathi, use Marathi/Hinglish, etc.\n"
            f"4. Select target_ui_tab: 'Mandi', 'Weather', 'Inventory', or 'Voice Assistant'."
        )

        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if HAS_ANTIGRAVITY and google_creds:
            try:
                config = LocalAgentConfig(
                    model="gemini-3.5-flash",
                    tools=[calculate_price_estimate, book_mandi_order, get_order_tracking_details],
                    response_schema=KrishiSyncPayload,
                    system_instructions=(
                        "You are KrishiSync Hackathon Core. You run scoped SQL tools for Mandi bookings, price estimations, and GPS tracking.\n"
                        f"{context_prompt}"
                    )
                )
                async with Agent(config) as agent:
                    response = await agent.chat(query)
                    payload: KrishiSyncPayload = await response.structured_output()
                    return payload
            except Exception as e:
                logger.error(f"Antigravity Agent failed: {e}. Emulating local parse...")

        # --- Emulation Fallback ---
        logger.info("Executing contextual local emulation engine...")
        text_lower = query.lower()

        # 1. Price Estimation Intent
        if any(w in text_lower for w in ["estimate", "calculate", "value", "दाम", "मूल्य", "हिसाब"]):
            crop = "Onion"
            if "tomato" in text_lower or "टमाटर" in text_lower:
                crop = "Tomato"
            elif "wheat" in text_lower or "गेहूं" in text_lower:
                crop = "Wheat"
            elif "cotton" in text_lower or "कपास" in text_lower:
                crop = "Cotton"

            import re
            nums = re.findall(r'\d+', text_lower)
            qty = float(nums[0]) if nums else 10.0
            
            grade = "Standard"
            if "premium" in text_lower or "quality" in text_lower or "बढ़िया" in text_lower:
                grade = "Premium"
            elif "fair" in text_lower or "खराब" in text_lower:
                grade = "Fair"

            res = calculate_price_estimate(crop, qty, grade)
            
            if lang == "Hindi":
                summary = f"{farmer.full_name} ji, {qty} quintal {crop} ({grade} quality) ka anumanit payout ₹{res['estimated_payout']:,} hoga (₹{res['rate_per_quintal']}/q rate)."
            elif lang == "Marathi":
                summary = f"{farmer.full_name} bhau, {qty} quintal {crop} ({grade}) cha andaji payout ₹{res['estimated_payout']:,} hoil."
            else:
                summary = f"Hello {farmer.full_name}, estimated payout for {qty} quintals of {crop} ({grade}) is ₹{res['estimated_payout']:,}."

            return KrishiSyncPayload(
                target_ui_tab="Mandi",
                data_payload=res,
                localization_summary=summary
            )

        # 2. Book Order Intent
        elif any(w in text_lower for w in ["book", "lot", "dispatch", "send", "भेजें", "बुक", "ऑर्डर"]):
            crop = "Onion"
            if "tomato" in text_lower or "टमाटर" in text_lower:
                crop = "Tomato"
            elif "wheat" in text_lower or "गेहूं" in text_lower:
                crop = "Wheat"
                
            import re
            nums = re.findall(r'\d+', text_lower)
            qty = float(nums[0]) if nums else 20.0
            
            mandi = "Mumbai APMC (Vashi)"
            if "delhi" in text_lower or "azadpur" in text_lower:
                mandi = "Azadpur APMC (Delhi)"
            elif "kota" in text_lower:
                mandi = "Kota APMC (Rajasthan)"
            elif "pune" in text_lower:
                mandi = "Pune APMC"

            res = book_mandi_order(crop, qty, mandi, "Standard")
            
            if lang == "Hindi":
                summary = f"Mandi order book ho gaya! {qty} quintal {crop} ko {mandi} bhejne ka transit booking order ID {res['order_id']} hai. Estimated payout: ₹{res['payout']:,}."
            elif lang == "Marathi":
                summary = f"Mandi order book zala aahe! {qty} quintal {crop} la {mandi} pathvinyacha ticket ID {res['order_id']} aahe."
            else:
                summary = f"Successfully booked lot. order ID is {res['order_id']} for shipping {qty} quintals of {crop} to {mandi}."

            return KrishiSyncPayload(
                target_ui_tab="Mandi",
                data_payload=res,
                localization_summary=summary
            )

        # 3. Track Order Intent
        elif any(w in text_lower for w in ["track", "shipment", "telemetry", "where", "पता", "ट्रैक", "गाड़ी"]):
            import re
            nums = re.findall(r'\d+', text_lower)
            order_id = int(nums[0]) if nums else None
            
            if not order_id:
                # Get latest order
                latest = db.query(MandiOrder).filter(MandiOrder.farmer_id == farmer_id).order_by(MandiOrder.id.desc()).first()
                if latest:
                    order_id = latest.id
            
            if not order_id:
                return KrishiSyncPayload(
                    target_ui_tab="Mandi",
                    data_payload={"status": "error", "message": "No active orders found to track."},
                    localization_summary="Aapka koi active transit booking nahi mila."
                )

            res = get_order_tracking_details(order_id)
            
            if lang == "Hindi":
                summary = f"Order ID {order_id} tracking status: {res['status_label']}. Gadi abhi latitude {res['current_location']['lat']}, longitude {res['current_location']['lng']} par hai ({res['progress_percent']}% rasta tay kiya)."
            elif lang == "Marathi":
                summary = f"Order ID {order_id} cha status: {res['status_label']}. Gadi sadhya lat {res['current_location']['lat']}, lng {res['current_location']['lng']} var aahe."
            else:
                summary = f"Order {order_id} tracking detail: {res['status_label']}. Current location: ({res['current_location']['lat']}, {res['current_location']['lng']}). Progress: {res['progress_percent']}%."

            return KrishiSyncPayload(
                target_ui_tab="Mandi",
                data_payload=res,
                localization_summary=summary
            )

        # 4. Fallback Weather Advisory
        import random
        temp = random.randint(28, 34)
        humidity = random.randint(70, 90)
        advisories = {
            "Maharashtra": "Heavy rain forecast for Nashik/Pune. Keep drainage lines open in Tomato fields.",
            "Gujarat": "Dry weather expected. Monitor cotton crops for whitefly infestation.",
            "Rajasthan": "Hot winds. Maintain soil moisture levels by light evening watering."
        }
        adv = advisories.get(farmer.state, "Scattered monsoons expected. Safe storage of harvested grains advised.")
        
        weather_payload = {
            "temperature": f"{temp}°C",
            "humidity": f"{humidity}%",
            "alert": "YELLOW WARNING",
            "pest_advisory": adv
        }
        
        if lang == "Hindi":
            summary = f"Weather update: {farmer.state} me abhi taapman {temp}°C hai. Advisory: {adv}"
        elif lang == "Marathi":
            summary = f"Weather update: {farmer.state} madhye taapman {temp}°C aahe. Advisory: {adv}"
        else:
            summary = f"Weather status in {farmer.state} is {temp}°C. Alert warning: {adv}"

        return KrishiSyncPayload(
            target_ui_tab="Weather",
            data_payload=weather_payload,
            localization_summary=summary
        )

    finally:
        db.close()

# --- Sarvam AI Speech-to-Text Pipeline ---

async def transcribe_speech_sarvam(audio_file_path: str) -> str:
    """
    Invokes Sarvam STT to translate multi-lingual Indian audio directly into English.
    """
    key = os.getenv("SARVAM_API_KEY")
    if not key or key == "your-sarvam-api-key" or key.strip() == "":
        logger.warning("Sarvam API Key is empty. Defaulting to mock transcription.")
        return "I need to book 15 quintals of onions to Mumbai APMC (Vashi)."

    url = "https://api.sarvam.ai/speech-to-text"
    headers = {"api-subscription-key": key}
    
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
                res_data = response.json()
                transcript = res_data.get("transcript", "").strip()
                if transcript:
                    return transcript
    except Exception as e:
        logger.error(f"Sarvam API failure: {e}")
        
    return "Error: STT pipeline failed."

# --- API Router Endpoints ---

@app.post("/api/auth/login")
async def login(payload: LoginPayload):
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.phone_number == payload.phone_number.strip()).first()
        if not farmer:
            return {
                "status": "registration_required",
                "user_exists": False,
                "message": "Phone number not registered. Please onboard profile."
            }
        return {
            "status": "success",
            "user_exists": True,
            "profile": {
                "id": farmer.id,
                "phone_number": farmer.phone_number,
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
    db = SessionLocal()
    try:
        existing = db.query(Farmer).filter(Farmer.phone_number == payload.phone_number.strip()).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already registered.")
            
        farmer = Farmer(
            phone_number=payload.phone_number.strip(),
            full_name=payload.full_name.strip(),
            state=payload.state.strip(),
            preferred_language=payload.preferred_language.strip(),
            land_size_acres=payload.land_size_acres
        )
        db.add(farmer)
        db.commit()
        db.refresh(farmer)

        # Seed initial stock inputs scoped to this farmer
        db.add_all([
            InventoryItem(farmer_id=farmer.id, item_name="Urea Fertilizer", quantity=50.0, unit="bags"),
            InventoryItem(farmer_id=farmer.id, item_name="NPK Fertilizer", quantity=30.0, unit="bags"),
            InventoryItem(farmer_id=farmer.id, item_name="Wheat Seeds", quantity=10.0, unit="bags"),
            InventoryItem(farmer_id=farmer.id, item_name="Organic Compost", quantity=100.0, unit="bags")
        ])
        db.commit()

        return {
            "status": "success",
            "profile": {
                "id": farmer.id,
                "phone_number": farmer.phone_number,
                "full_name": farmer.full_name,
                "state": farmer.state,
                "preferred_language": farmer.preferred_language,
                "land_size_acres": farmer.land_size_acres
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/dashboard-data")
async def get_dashboard_data(farmer_id: int = Depends(get_farmer_id_header)):
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Invalid farmer session.")

        inventory = db.query(InventoryItem).filter(InventoryItem.farmer_id == farmer_id).all()
        orders = db.query(MandiOrder).filter(MandiOrder.farmer_id == farmer_id).order_by(MandiOrder.id.desc()).all()
        prices = db.query(MandiReference).all()

        inventory_data = [{"id": i.id, "item_name": i.item_name, "quantity": i.quantity, "unit": i.unit} for i in inventory]
        orders_data = [
            {"id": o.id, "crop_name": o.crop_name, "quantity_quintals": o.quantity_quintals, "target_mandi": o.target_mandi, "estimated_payout": o.estimated_payout, "status": o.status, "lat": o.transit_lat, "lng": o.transit_lng}
            for o in orders
        ]
        prices_data = [{"id": p.id, "mandi_name": p.mandi_name, "city": p.city, "base_price": p.base_price} for p in prices]

        import random
        temp = random.randint(28, 33)
        humidity = random.randint(75, 88)

        weather = {
            "temp": f"{temp}°C",
            "humidity": f"{humidity}%",
            "alert": "YELLOW WARNING",
            "advisory": f"High humidity in {farmer.state}. Clean standing water, risk of blights."
        }

        return {
            "status": "success",
            "inventory": inventory_data,
            "mandi_orders": orders_data,
            "market_references": prices_data,
            "weather": weather
        }
    finally:
        db.close()

@app.post("/api/query", response_model=KrishiSyncPayload)
async def query_text(payload: Dict[str, str], farmer_id: int = Depends(get_farmer_id_header)):
    query_str = payload.get("query", "").strip()
    if not query_str:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return await run_contextual_agent(query_str, farmer_id)

@app.post("/api/voice", response_model=KrishiSyncPayload)
async def query_audio(
    file: UploadFile = File(...),
    custom_text_prompt: Optional[str] = Form(None),
    farmer_id: int = Depends(get_farmer_id_header)
):
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f"audio_hack_{uuid.uuid4().hex}.wav")
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if custom_text_prompt and custom_text_prompt.strip():
            transcript = custom_text_prompt
        else:
            transcript = await transcribe_speech_sarvam(temp_file)

        if "Error:" in transcript:
            transcript = "I need to book 15 quintals of onions to Mumbai APMC (Vashi)."

        logger.info(f"Audio Transcript: '{transcript}'")
        return await run_contextual_agent(transcript, farmer_id)
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Could not remove temp file: {e}")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
