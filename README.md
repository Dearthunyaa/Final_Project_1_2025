# CryptoCurrencyDashboard - Final Project Y1

**CryptoCurrencyDashboard** is a real-time cryptocurrency analysis tool built with Python. It replicates the user experience of professional trading platforms (like Binance) using a desktop GUI.

This project leverages **CustomTkinter** for a modern dark-themed UI, **Matplotlib/Mplfinance** for financial charting, and **Binance WebSockets** for live data streaming without requiring an API key.

---

## Key Features

* **Real-Time Data Streaming:** Connects directly to Binance WebSockets for live price updates, trades, and order book changes.
* **Advanced Charting:**
    * Interactive Candlestick charts using `mplfinance`.
    * Adjustable Timeframes (1m, 15m, 1h, 4h, 1d).
    * Technical Indicators (Moving Averages: MA7, MA25, MA99).
* **Live Order Book:** Visual representation of Bids and Asks with dynamic depth bars.
* **Multi-Coin Comparison:** A normalized performance graph comparing Bitcoin (BTC) against other major altcoins in real-time.
* **Recent Trades:** Live feed of executed market trades.
* **Modern UI:** A clean, dark-themed interface designed for readability and focus.

---

## Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Charting:** Matplotlib, Mplfinance
* **Data Handling:** Pandas, Numpy
* **Network:** Requests (REST API), Websocket-client (Streaming)

---

## Project Structure

```text
ProDashboard/
├── components/             # UI Components (Widgets)
│   ├── __init__.py
│   ├── chart_panel.py      # Main candlestick chart logic
│   ├── left_sidebar.py     # Watchlist & Comparison graph
│   ├── right_sidebar.py    # Order Book & Recent Trades
│   └── top_nav.py          # Navigation, Symbol selection, Price header
│
├── utils/                  # Backend Logic
│   ├── __init__.py
│   └── binance_api.py      # Handles API requests & WebSocket connections
│
├── config.py               # Global settings (Colors, Fonts, Default Coins)
├── main.py                 # Application Entry Point
├── requirements.txt        # Python dependencies
└── README.md               # Project Documentation
```

---

## Installation & Setup

Follow these steps to get the dashboard running on your local machine.

### Step 1: Clone the Repository
Open your terminal (Command Prompt, PowerShell, or Git Bash) and run:
```bash
git clone https://github.com/Dearthunyaa/Final_Project_1_2025.git
cd Final_Project_1_2025
```

### Step 2: Install Dependencies
Install the required Python libraries using pip:
```bash
pip install customtkinter mplfinance matplotlib pandas requests websocket-client Pillow
```