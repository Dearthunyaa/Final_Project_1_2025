import customtkinter as ctk
from PIL import Image
import os
from config import *


class TopNavPanel(ctk.CTkFrame):
    def __init__(self, parent, callback_change_pair):
        super().__init__(parent, height=45, fg_color=COLOR_BG_PANEL, corner_radius=0)
        self.callback_change_pair = callback_change_pair

        self.grid(row=0, column=0, sticky="ew")

        self.logo_label = ctk.CTkLabel(self, text="   ", width=30)
        self.logo_label.pack(side="left", padx=(10, 5))

        self.update_logo(DEFAULT_SYMBOL)

        self.ticker_btn = ctk.CTkOptionMenu(
            self,
            values=[f"{c} / USDT" for c in DEFAULT_COINS],
            command=self._on_change,
            fg_color=COLOR_BG_PANEL, button_color=COLOR_BG_PANEL,
            text_color=COLOR_TEXT_MAIN, font=("Roboto", 14, "bold"), width=120
        )
        self.ticker_btn.set(f"{DEFAULT_SYMBOL} / USDT")
        self.ticker_btn.pack(side="left", padx=5)

        self.lbl_price = self._create_stat_label("---", COLOR_GREEN, 14)
        self.lbl_change = self._create_stat_header("24h %", "---")
        self.lbl_high = self._create_stat_header("High", "---")
        self.lbl_low = self._create_stat_header("Low", "---")
        self.lbl_vol = self._create_stat_header("Vol", "---")

    def _create_stat_header(self, title, val):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(side="left", padx=5)
        ctk.CTkLabel(f, text=title, font=("Arial", 10),
                     text_color=COLOR_TEXT_SUB).pack(anchor="w")
        lbl = ctk.CTkLabel(f, text=val, font=(
            "Arial", 10, "bold"), text_color=COLOR_TEXT_MAIN)
        lbl.pack(anchor="w")
        return lbl

    def _create_stat_label(self, text, color, size):
        lbl = ctk.CTkLabel(self, text=text, font=(
            "Roboto", size, "bold"), text_color=color)
        lbl.pack(side="left", padx=10)
        return lbl

    def _on_change(self, selection):
        raw_pair = selection.replace(" / ", "")
        symbol = raw_pair.replace("USDT", "")

        self.update_logo(symbol)
        self.callback_change_pair(raw_pair, symbol)

    def update_logo(self, symbol):
        try:
            image_path = f"{symbol}.png"

            if os.path.exists(image_path):
                pil_image = Image.open(image_path)
                pil_image = pil_image.resize((25, 25))
                self.logo_image = ctk.CTkImage(
                    light_image=pil_image, dark_image=pil_image, size=(25, 25))
                self.logo_label.configure(image=self.logo_image, text="")
            else:
                self.logo_label.configure(
                    image=None, text=symbol, font=("Arial", 12, "bold"))
        except Exception as e:
            print(f"Logo error: {e}")
            self.logo_label.configure(image=None, text=symbol)

    def update_data(self, ticker_data):
        if not ticker_data:
            return
        p = float(ticker_data['lastPrice'])
        c = float(ticker_data['priceChangePercent'])
        color = COLOR_GREEN if c >= 0 else COLOR_RED

        self.lbl_price.configure(text=f"{p:,.2f}", text_color=color)
        self.lbl_change.configure(text=f"{c:+.2f}%", text_color=color)
        self.lbl_high.configure(text=f"{float(ticker_data['highPrice']):,.2f}")
        self.lbl_low.configure(text=f"{float(ticker_data['lowPrice']):,.2f}")
        self.lbl_vol.configure(
            text=f"{float(ticker_data['quoteVolume'])/1000000:.2f}M")

    def set_selected_symbol(self, symbol):
        self.ticker_btn.set(f"{symbol} / USDT")
