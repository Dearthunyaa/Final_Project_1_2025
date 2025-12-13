import customtkinter as ctk
import threading
from collections import deque
from config import *
from utils.binance_api import BinanceAPI, BinanceStream
from components.top_nav import TopNavPanel
from components.chart_panel import ChartPanel
from components.left_sidebar import LeftSidebar
from components.right_sidebar import RightSidebar

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class CryptoTerminal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cryptocurrency Dashboard")
        self.geometry("1600x750")
        self.configure(fg_color=COLOR_BG_MAIN)
        
        self.symbol = DEFAULT_SYMBOL
        self.pair = DEFAULT_PAIR
        self.interval = DEFAULT_INTERVAL
        self.is_running = True
        
        self.trades_buffer = deque(maxlen=25)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_nav = TopNavPanel(self, self.change_pair)
        
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=0)
        self.main_area.grid_columnconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(2, weight=0)

        self.left_panel = LeftSidebar(self.main_area, self.change_pair)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.right_panel = RightSidebar(self.main_area)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        toggle_funcs = {
            "overview": self.left_panel.toggle_graph,
            "orderbook": self.right_panel.toggle_orderbook,
            "trades": self.right_panel.toggle_trades
        }
        
        self.chart_panel = ChartPanel(self.main_area, self.change_interval, callbacks_toggle=toggle_funcs)
        self.chart_panel.grid(row=0, column=1, sticky="nsew")

        self.ws_manager = BinanceStream(self.handle_stream_data)

        self.loop_chart()       
        self.loop_comparison() 
        self.ws_manager.start(self.pair)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_left_sidebar(self, is_visible):
        if is_visible:
            self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        else:
            self.left_panel.grid_remove()

    def on_close(self):
        self.is_running = False
        self.ws_manager.stop()
        self.destroy()

    def change_pair(self, new_pair_str, symbol=None):
        if symbol:
            self.symbol = symbol
            self.pair = f"{symbol}USDT"
        else:
            if " / " in new_pair_str:
                 sym = new_pair_str.split(" / ")[0]
                 self.symbol = sym
                 self.pair = f"{sym}USDT"
            else:
                 self.pair = new_pair_str
                 self.symbol = new_pair_str.replace("USDT", "")

        self.top_nav.update_logo(self.symbol)
        if hasattr(self.top_nav, 'ticker_btn'):
            self.top_nav.ticker_btn.set(f"{self.symbol} / USDT")

        self._fetch_chart()
        self.trades_buffer.clear()
        self.ws_manager.start(self.pair)

    def change_interval(self, new_tf):
        self.interval = new_tf
        self._fetch_chart()

    def loop_chart(self):
        if not self.is_running: return
        threading.Thread(target=self._fetch_chart, daemon=True).start()
        self.after(60000, self.loop_chart)

    def _fetch_chart(self):
        df = BinanceAPI.get_klines(self.pair, self.interval)
        if not df.empty:
            self.after(0, lambda: self.chart_panel.update_chart(df))

    def loop_comparison(self):
        if not self.is_running: return
        threading.Thread(target=self._fetch_comp, daemon=True).start()
        self.after(5000, self.loop_comparison)

    def _fetch_comp(self):
        all_prices = BinanceAPI.get_all_prices()
        comp_data = BinanceAPI.get_comparison_data(DEFAULT_COINS)
        self.after(0, lambda: self._update_left_panel(all_prices, comp_data))

    def _update_left_panel(self, all_prices, comp_data):
        self.left_panel.update_watchlist(all_prices)
        if hasattr(self.left_panel, 'update_comparison'):
            self.left_panel.update_comparison(comp_data)
        elif hasattr(self.left_panel, 'update_graph'):
             self.left_panel.update_graph(comp_data)

    def handle_stream_data(self, payload):
        if not payload or 'data' not in payload: return
        stream_name = payload['stream']
        data = payload['data']
        self.after(0, lambda: self._update_ui_from_ws(stream_name, data))

    def _update_ui_from_ws(self, stream, data):
        if 'ticker' in stream:
            ticker_info = {
                'lastPrice': data['c'],          
                'priceChangePercent': data['P'], 
                'highPrice': data['h'],
                'lowPrice': data['l'],
                'volume': data['v'],       
                'quoteVolume': data['q']   
            }
            self.top_nav.update_data(ticker_info)
        elif 'depth' in stream:
            self.right_panel.update_orderbook(data)
        elif 'aggTrade' in stream:
            self.trades_buffer.appendleft(data)
            self.right_panel.update_trades(list(self.trades_buffer))

if __name__ == "__main__":
    app = CryptoTerminal()
    app.mainloop()
    