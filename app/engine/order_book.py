# app/engine/order_book.py
from dataclasses import dataclass
from typing import List, Dict
import time

@dataclass
class Order:
    order_id: str
    side: str  # "BUY" or "SELL"
    price: float
    quantity: int
    timestamp: float = time.time()

@dataclass
class Trade:
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: int
    executed_at: float = time.time()

class OrderBook:
    def __init__(self):
        # Bids sorted descending (highest price first), Asks sorted ascending (lowest price first)
        self.bids: List[Order] = []
        self.asks: List[Order] = []
        self.trade_history: List[Trade] = []

    def add_order(self, order: Order) -> List[Trade]:
        executed_trades = []

        if order.side == "BUY":
            # Match against Asks
            while order.quantity > 0 and self.asks and self.asks[0].price <= order.price:
                best_ask = self.asks[0]
                matched_qty = min(order.quantity, best_ask.quantity)
                
                trade = Trade(
                    buy_order_id=order.order_id,
                    sell_order_id=best_ask.order_id,
                    price=best_ask.price,
                    quantity=matched_qty
                )
                executed_trades.append(trade)
                self.trade_history.append(trade)

                order.quantity -= matched_qty
                best_ask.quantity -= matched_qty

                if best_ask.quantity == 0:
                    self.asks.pop(0)

            # If order still has quantity, add to bids (Price-Time priority)
            if order.quantity > 0:
                self.bids.append(order)
                self.bids.sort(key=lambda x: (-x.price, x.timestamp))

        else:  # SELL
            # Match against Bids
            while order.quantity > 0 and self.bids and self.bids[0].price >= order.price:
                best_bid = self.bids[0]
                matched_qty = min(order.quantity, best_bid.quantity)
                
                trade = Trade(
                    buy_order_id=best_bid.order_id,
                    sell_order_id=order.order_id,
                    price=best_bid.price,
                    quantity=matched_qty
                )
                executed_trades.append(trade)
                self.trade_history.append(trade)

                order.quantity -= matched_qty
                best_bid.quantity -= matched_qty

                if best_bid.quantity == 0:
                    self.bids.pop(0)

            # If order still has quantity, add to asks
            if order.quantity > 0:
                self.asks.append(order)
                self.asks.sort(key=lambda x: (x.price, x.timestamp))

        return executed_trades

    def get_book_snapshot(self) -> Dict:
        return {
            "bids": [{"price": o.price, "quantity": o.quantity} for o in self.bids[:5]],
            "asks": [{"price": o.price, "quantity": o.quantity} for o in self.asks[:5]],
            "total_trades_executed": len(self.trade_history)
        }