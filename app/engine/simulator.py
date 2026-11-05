# app/engine/simulator.py
import asyncio
import random
import time
from app.engine.order_book import OrderBook, Order

async def run_simulation(num_orders: int = 10000):
    book = OrderBook()
    print(f"🚀 Starting NexusCore High-Throughput Simulation with {num_orders:,} orders...")
    
    start_time = time.perf_counter()
    total_trades = 0

    sides = ["BUY", "SELL"]
    base_price = 100.0

    for i in range(num_orders):
        order_id = f"ord_{i}"
        side = random.choice(sides)
        # Random price fluctuation around base price
        price = round(base_price + random.uniform(-2.0, 2.0), 2)
        quantity = random.randint(1, 50)

        order = Order(order_id=order_id, side=side, price=price, quantity=quantity)
        trades = book.add_order(order)
        total_trades += len(trades)

        # Yield control periodically to simulate real async event loop traffic
        if i % 1000 == 0:
            await asyncio.sleep(0.001)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    throughput = num_orders / elapsed_time

    print("\n" + "="*40)
    print("📊 NEXUSCORE STRESS TEST RESULTS")
    print("="*40)
    print(f"Total Orders Processed : {num_orders:,}")
    print(f"Total Trades Executed  : {total_trades:,}")
    print(f"Time Elapsed           : {elapsed_time:.4f} seconds")
    print(f"Engine Throughput      : {throughput:,.2f} orders/sec")
    print("="*40 + "\n")

if __name__ == "__main__":
    asyncio.run(run_simulation(10000))