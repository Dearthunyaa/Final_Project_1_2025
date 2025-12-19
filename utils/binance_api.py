import requests
import pandas as pd
import threading
import json
import websocket


class BinanceAPI:
    BASE_URL = "https://api.binance.com/api/v3"

    @staticmethod
    def get_klines(symbol, interval, limit=60):
        try:
            url = f"{BinanceAPI.BASE_URL}/klines?symbol={symbol}&interval={interval}&limit={limit}"
            resp = requests.get(url, timeout=3)
            data = resp.json()

            df = pd.DataFrame(data, columns=[
                              'ts', 'open', 'high', 'low', 'close', 'volume', 'ct', 'qav', 'nt', 'tbv', 'tqv', 'ig'])
            df['ts'] = pd.to_datetime(df['ts'], unit='ms')
            df.set_index('ts', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            return df
        except Exception as e:
            print(f"Klines Error: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_all_prices():
        try:
            return requests.get(f"{BinanceAPI.BASE_URL}/ticker/price", timeout=2).json()
        except:
            return []

    @staticmethod
    def get_comparison_data(coins_list):
        data = {}
        try:
            for c in coins_list:
                sym = c + "USDT"
                url = f"{BinanceAPI.BASE_URL}/klines?symbol={sym}&interval=1h&limit=24"
                resp = requests.get(url, timeout=2)
                if resp.status_code == 200:
                    raw = resp.json()
                    closes = [float(x[4]) for x in raw]
                    if closes:
                        start_price = closes[0]
                        data[c] = [((p - start_price) / start_price)
                                   * 100 for p in closes]
        except Exception as e:
            print(f"Comparison Data Error: {e}")
        return data


class BinanceStream:
    def __init__(self, callback_func):
        self.ws = None
        self.callback_func = callback_func
        self.thread = None
        self.is_running = False

    def start(self, symbol):
        self.stop()
        self.is_running = True

        symbol = symbol.lower()
        stream_url = f"wss://stream.binance.com:9443/stream?streams={symbol}@ticker/{symbol}@depth20/{symbol}@aggTrade"

        def run_ws():
            self.ws = websocket.WebSocketApp(
                stream_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            self.ws.run_forever()

        self.thread = threading.Thread(target=run_ws, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def _on_message(self, ws, message):
        if not self.is_running:
            return
        try:
            data = json.loads(message)
            self.callback_func(data)
        except Exception as e:
            print(f"WS Decode Error: {e}")

    def _on_error(self, ws, error):
        print(f"WS Error: {error}")

    def _on_close(self, ws, *args):
        print("WS Connection Closed")
