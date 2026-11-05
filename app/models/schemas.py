# app/models/schemas.py
from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime
from app.core.database import Base

class TradeLogModel(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    buy_order_id = Column(String, index=True)
    sell_order_id = Column(String, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    executed_at = Column(DateTime, default=datetime.datetime.utcnow)