import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Farmer(Base):
    __tablename__ = "farmers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    state = Column(String, nullable=False)
    preferred_language = Column(String, default="en")
    land_size_acres = Column(Float, default=0.0)

    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="farmer", cascade="all, delete-orphan")
    logistics_tickets = relationship("LogisticsTicket", back_populates="farmer", cascade="all, delete-orphan")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    status = Column(String, default="In Stock")  # "In Stock" | "Low" | "Out of Stock"
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    farmer = relationship("Farmer", back_populates="inventory_items")

class MandiPrice(Base):
    __tablename__ = "mandi_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, index=True, nullable=False)
    market_name = Column(String, nullable=False)
    price_per_quintal = Column(Float, nullable=False)
    date = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d"))

class LogisticsTicket(Base):
    __tablename__ = "logistics_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    commodity = Column(String, nullable=False)
    weight = Column(String, nullable=False)  # e.g., "50 bags", "2.5 tons"
    target_destination = Column(String, nullable=False)
    tracking_status = Column(String, default="Booked")  # "Booked" | "In Transit" | "Delivered"
    tracking_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farmer = relationship("Farmer", back_populates="logistics_tickets")

# DB Engine and Session Local setup
is_vercel = "VERCEL" in os.environ or os.name != "nt"
db_path = "/tmp/krishisync.db" if is_vercel else "krishisync.db"
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed global MandiPrice reference data
        if db.query(MandiPrice).count() == 0:
            db.add_all([
                MandiPrice(crop_name="Onion", market_name="Mumbai APMC (Vashi)", price_per_quintal=2550.0),
                MandiPrice(crop_name="Onion", market_name="Lasalgaon APMC (Nashik)", price_per_quintal=2300.0),
                MandiPrice(crop_name="Onion", market_name="Pune APMC", price_per_quintal=2400.0),
                MandiPrice(crop_name="Tomato", market_name="Narayangaon APMC (Pune)", price_per_quintal=1900.0),
                MandiPrice(crop_name="Tomato", market_name="Kolar APMC (Karnataka)", price_per_quintal=1800.0),
                MandiPrice(crop_name="Tomato", market_name="Azadpur APMC (Delhi)", price_per_quintal=2200.0),
                MandiPrice(crop_name="Wheat", market_name="Kota APMC (Rajasthan)", price_per_quintal=2700.0),
                MandiPrice(crop_name="Wheat", market_name="Indore APMC (MP)", price_per_quintal=2600.0),
                MandiPrice(crop_name="Wheat", market_name="Bhopal APMC", price_per_quintal=2580.0),
                MandiPrice(crop_name="Cotton", market_name="Amravati APMC (MH)", price_per_quintal=7300.0),
                MandiPrice(crop_name="Cotton", market_name="Rajkot APMC (Gujarat)", price_per_quintal=7150.0),
                MandiPrice(crop_name="Potato", market_name="Agra APMC (UP)", price_per_quintal=1450.0),
                MandiPrice(crop_name="Potato", market_name="Kolkata APMC", price_per_quintal=1600.0)
            ])
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
