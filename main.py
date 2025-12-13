
import customtkinter as ctk
import threading
import matplotlib.pyplot as plt
from config import *
from utils.binance_api import BinanceAPI
from components.top_nav import TopNavPanel
from components.chart_panel import ChartPanel
from components.left_sidebar import LeftSidebar
from components.right_sidebar import RightSidebar

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class CryptoTerminal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CRYPTOCURRENCY DASHBOARD")
        self.geometry("1600x900")
        self.configure(fg_color=COLOR_BG_MAIN)
        
        self.symbol = DEFAULT_SYMBOL
        self.pair = DEFAULT_PAIR
        self.interval = DEFAULT_INTERVAL
        self.is_running = True

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_nav = TopNavPanel(self, self.change_pair)
        
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_area.grid_columnconfigure(1, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        self.left_panel = LeftSidebar(self.main_area, callback_symbol_change=self.change_pair) 
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.right_panel = RightSidebar(self.main_area)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

        toggle_callbacks = {
            "orderbook": self.right_panel.toggle_orderbook,
            "trades": self.right_panel.toggle_trades,
            "overview": self.left_panel.toggle_overview
        }

        self.chart_panel = ChartPanel(self.main_area, self.change_tf, callbacks_toggle=toggle_callbacks)
        self.chart_panel.grid(row=0, column=1, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.after(500, self.loop_chart)
        self.after(500, self.loop_realtime)
        self.after(500, self.loop_comparison)

    def change_pair(self, pair, symbol):
        self.pair = pair
        self.symbol = symbol
        self.top_nav.update_logo(symbol)
        self.top_nav.set_selected_symbol(symbol) 
        self.loop_chart() 

    def change_tf(self, tf):
        self.interval = tf
        self.loop_chart() 

    def loop_chart(self):
        if not self.is_running: return
        threading.Thread(target=self._fetch_chart, daemon=True).start()
        self.after(60000 if self.interval in ['1h', '4h', '1d'] else 3000, self.loop_chart)

    def _fetch_chart(self):
        df = BinanceAPI.get_klines(self.pair, self.interval)
        self.after(0, lambda: self.chart_panel.update_chart(df))

    def loop_realtime(self):
        if not self.is_running: return
        threading.Thread(target=self._fetch_realtime, daemon=True).start()
        self.after(2000, self.loop_realtime)

    def _fetch_realtime(self):
        ticker, depth, trades = BinanceAPI.get_realtime_data(self.pair)
        all_prices = BinanceAPI.get_all_prices()
        self.after(0, lambda: self._update_ui_realtime(ticker, depth, trades, all_prices))

    def _update_ui_realtime(self, ticker, depth, trades, all_prices):
        self.top_nav.update_data(ticker)
        self.right_panel.update_orderbook(depth)
        self.right_panel.update_trades(trades)
        self.left_panel.update_watchlist(all_prices)

    def loop_comparison(self):
        if not self.is_running: return
        threading.Thread(target=self._fetch_comp, daemon=True).start()
        self.after(60000, self.loop_comparison)

    def _fetch_comp(self):
        data = BinanceAPI.get_comparison_data(DEFAULT_COINS)
        self.after(0, lambda: self.left_panel.update_comparison(data))

    def on_close(self):
        self.is_running = False
        plt.close('all')
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = CryptoTerminal()
    app.mainloop()
