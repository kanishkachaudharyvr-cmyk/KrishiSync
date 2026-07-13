import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class LogisticsLog(Base):
    __tablename__ = "logistics_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String, nullable=False)
    quantity = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    status = Column(String, default="Scheduled")
    tracking_id = Column(String, unique=True, index=True, nullable=False)

class MarketPrices(Base):
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, index=True, nullable=False)
    market_name = Column(String, nullable=False)
    price_per_quintal = Column(Float, nullable=False)

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)  # annual percentage rate (e.g., 7.0 for 7%)
    due_date = Column(String, nullable=False)      # ISO string or human-readable date (e.g., "2026-10-15")
    status = Column(String, default="Active")      # "Active" | "Repaid" | "Overdue"
