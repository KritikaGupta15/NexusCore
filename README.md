# NexusCore HFT

A high-performance, real-time Limit Order Matching Engine and Audit Pipeline built with a decoupled hot/cold architecture, featuring a FastAPI backend, in-memory matching logic, PostgreSQL persistence, and a reactive React/Tailwind CSS WebSocket dashboard.

![NexusCore Architecture Overview](https://img.shields.io/badge/Architecture-Hot%2FCold%20Path-emerald) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Async-teal) ![React](https://img.shields.io/badge/React-18-cyan)

---

## 🚀 Key Features

* **In-Memory Matching Engine (Hot Path)**: Ultra-low latency limit order matching algorithm handling bids and asks with strict price-time priority.
* **Real-Time WebSocket Broadcasting**: Live order book depth updates and executed trade streams pushed instantly to connected clients.
* **Asynchronous Audit Pipeline (Cold Path)**: Decoupled database logging that commits executed trades to PostgreSQL asynchronously without blocking the matching thread.
* **Modern Reactive Dashboard**: Real-time visualization of order book depth, order entry (Buy/Sell toggle), and live executed trades audit streams built with React and Tailwind CSS.

---

## Project Structure

```
NexusCore/
├── Frontend/
│   └── index.html
├── app/
│   ├── core/
│   │   └── database.py
│   ├── engine/
│   │   ├── order_book.py
│   │   └── simulator.py
│   ├── models/
│   │   └── schemas.py
│   └── main.py
└── requirements.txt
```
---

## 🏗️ Architecture & System Design

```

 ┌──────────────────────┐         HTTP / REST         ┌────────────────────────┐
 │                      │ ──────────────────────────> │                        │
 │  React + Tailwind    │                             │    FastAPI Backend     │
 │ (Reactive Dashboard) │ <────────────────────────── │ (REST API & WebSockets)│
 │                      │      WebSocket Stream       │                        │
 └──────────────────────┘                             └───────────┬────────────┘
            ▲                                                     │
            │ (Real-time Sync)                                    │ (Hot Path)
            │                                                     ▼
 ┌──────────────────────┐                             ┌────────────────────────┐
 │ WebSocket Broadcast  │ <────────────────────────── │  In-Memory Matching    │
 │ (/ws/book)           │                             │        Engine          │
 └──────────────────────┘                             └───────────┬────────────┘
                                                                  │
                                                                  │ (Cold Path / Async)
                                                                  ▼
                                                      ┌────────────────────────┐
                                                      │  PostgreSQL Database   │
                                                      │   (Trade Audit Logs)   │
                                                      └────────────────────────┘


```
---


## 🛠️ Tech Stack

* **Backend**: Python, FastAPI, Uvicorn, WebSockets
* **Database**: PostgreSQL
* **Frontend**: React (via CDN/Babel), Tailwind CSS, JavaScript (ES6+)

---

## ⚙️ Getting Started & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/KritikaGupta15/NexusCore.git
```

### 2. Run the FastAPI Backend

```bash
uvicorn app.main:app --reload
```

### 3. Run the Frontend Dashboard Server
   
Open a second terminal window in the frontend directory:
```bash
cd frontend
python -m http.server 3000

```

Open your browser and navigate to http://localhost:3000 to access the live trading dashboard.

---
This project is open-source and available under the MIT License.
