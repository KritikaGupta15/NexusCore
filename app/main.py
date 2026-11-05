# app/main.py
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.engine.order_book import OrderBook, Order
from app.core.database import engine, Base, get_db
from app.models.schemas import TradeLogModel
from contextlib import asynccontextmanager
from typing import List
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup on shutdown
    await engine.dispose()

# Initialize FastAPI app
app = FastAPI(title="NexusCore HFT Matching Engine", version="1.0.0", lifespan=lifespan)

# Enable CORS for frontend dashboard communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

# Global in-memory order book instance
order_book = OrderBook()

@app.websocket("/ws/book")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        snapshot = order_book.get_book_snapshot()
        await websocket.send_text(json.dumps({"type": "BOOK_SNAPSHOT", "data": snapshot}))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class OrderRequest(BaseModel):
    order_id: str
    side: str  # "BUY" or "SELL"
    price: float
    quantity: int

@app.post("/api/v1/orders", summary="Submit a limit order and persist trades")
async def submit_order(order_req: OrderRequest, db: AsyncSession = Depends(get_db)):
    if order_req.side not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Side must be either 'BUY' or 'SELL'")
    
    order = Order(
        order_id=order_req.order_id,
        side=order_req.side,
        price=order_req.price,
        quantity=order_req.quantity
    )
    
    # Execute matching in-memory for microsecond speed
    trades = order_book.add_order(order)
    
    # Persist executed trades to PostgreSQL asynchronously
    for t in trades:
        db_trade = TradeLogModel(
            buy_order_id=t.buy_order_id,
            sell_order_id=t.sell_order_id,
            price=t.price,
            quantity=t.quantity
        )
        db.add(db_trade)
    
    if trades:
        await db.commit()

    # Broadcast updated book snapshot & new trade events to connected UI clients
    snapshot = order_book.get_book_snapshot()
    await manager.broadcast({
        "type": "ORDER_UPDATE",
        "book": snapshot,
        "new_trades": [
            {
                "buy_order_id": t.buy_order_id,
                "sell_order_id": t.sell_order_id,
                "price": t.price,
                "quantity": t.quantity
            } for t in trades
        ]
    })

    return {
        "status": "success",
        "remaining_quantity": order.quantity,
        "trades_executed": len(trades),
        "trades": [
            {
                "buy_order_id": t.buy_order_id,
                "sell_order_id": t.sell_order_id,
                "price": t.price,
                "quantity": t.quantity
            } for t in trades
        ]
    }

@app.get("/api/v1/book", summary="Get live order book depth")
async def get_book():
    return order_book.get_book_snapshot()