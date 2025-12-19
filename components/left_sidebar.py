import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import *


class LeftSidebar(ctk.CTkFrame):
    def __init__(self, parent, callback_symbol_change):
        super().__init__(parent, fg_color="transparent", width=SIDEBAR_WIDTH)
        self.callback_symbol_change = callback_symbol_change

        self.grid_propagate(False)

        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=7)
        self.grid_columnconfigure(0, weight=1)

        self._create_watchlist()
        self._create_comparison_graph()

    def _create_watchlist(self):
        wl_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_PANEL,
                                corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        wl_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        header_container = ctk.CTkFrame(wl_frame, fg_color="transparent")
        header_container.pack(fill="x", side="top", pady=(5, 0))

        h = ctk.CTkFrame(header_container, fg_color="transparent", height=30)
        h.pack(fill="x", padx=SIDE_PAD, pady=(5, 0))
        ctk.CTkLabel(h, text="Watchlist", font=FONT_BOLD,
                     text_color=COLOR_TEXT_MAIN).pack(side="left")

        header_row = ctk.CTkFrame(header_container, fg_color="transparent")
        header_row.pack(fill="x", padx=SIDE_PAD, pady=(5, 2))
        ctk.CTkLabel(header_row, text="Coin", width=40, anchor="w", font=(
            "Arial", 10), text_color=COLOR_TEXT_SUB).pack(side="left")
        ctk.CTkLabel(header_row, text="Price", width=60, anchor="e", font=(
            "Arial", 10), text_color=COLOR_TEXT_SUB).pack(side="right")

        self.wl_content = ctk.CTkFrame(wl_frame, fg_color="transparent")
        self.wl_content.pack(fill="both", expand=True, padx=5, pady=5)

        self.watchlist_items = {}
        for coin in DEFAULT_COINS:
            self._add_watchlist_item(coin)

    def _add_watchlist_item(self, coin):
        row = ctk.CTkFrame(self.wl_content, fg_color="transparent")
        row.pack(fill="both", expand=True, pady=0)

        btn = ctk.CTkButton(
            row, text=coin, width=50, height=25,
            fg_color="transparent", hover_color=COLOR_BTN_DEFAULT,
            anchor="w", font=FONT_UNIFIED, text_color=COLOR_TEXT_MAIN
        )
        btn.pack(side="left", padx=(10, 0), anchor="center")
        btn.configure(command=lambda c=coin: self._on_coin_click(c))

        lbl_price = ctk.CTkLabel(
            row, text="---", width=80, anchor="e", font=FONT_UNIFIED, text_color=COLOR_TEXT_MAIN)
        lbl_price.pack(side="right", padx=(0, 10), anchor="center")

        self.watchlist_items[coin] = lbl_price

    def _on_coin_click(self, coin):
        pair = f"{coin}USDT"
        self.callback_symbol_change(pair, coin)

    def _create_comparison_graph(self):
        self.comp_frame = ctk.CTkFrame(
            self, fg_color=COLOR_BG_PANEL, corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        self.comp_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        header_container = ctk.CTkFrame(
            self.comp_frame, fg_color="transparent")
        header_container.pack(fill="x", side="top", pady=(5, 0))

        h = ctk.CTkFrame(header_container, fg_color="transparent", height=30)
        h.pack(fill="x", padx=SIDE_PAD, pady=(10, 0))
        ctk.CTkLabel(h, text="24h Change (%)", font=FONT_BOLD,
                     text_color=COLOR_TEXT_MAIN).pack(side="left")

        self.comp_fig = plt.Figure(
            figsize=(3, 3), dpi=100, facecolor=COLOR_BG_PANEL)
        self.comp_ax = self.comp_fig.add_subplot(111)
        self.comp_ax.set_facecolor(COLOR_BG_PANEL)

        self.comp_canvas = FigureCanvasTkAgg(
            self.comp_fig, master=self.comp_frame)
        self.comp_canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def update_watchlist(self, prices):
        if not prices:
            return
        price_map = {x['symbol']: x['price'] for x in prices}
        for coin, label in self.watchlist_items.items():
            pair = f"{coin}USDT"
            if pair in price_map:
                p = float(price_map[pair])
                label.configure(text=f"{p:,.2f}")

    def update_comparison(self, data):
        if not data:
            return
        self.comp_ax.clear()
        self.comp_ax.set_facecolor(COLOR_BG_PANEL)

        self.comp_fig.subplots_adjust(
            left=0.15, right=0.95, top=0.82, bottom=0.08)

        colors = ['#00ff88', '#00d0ff', '#ff0055',
                  '#ffe600', '#aa00ff', '#ff8800', '#ffffff']
        for i, (coin, vals) in enumerate(data.items()):
            if len(vals) > 0:
                c = colors[i % len(colors)]
                self.comp_ax.plot(range(len(vals)), vals,
                                  label=coin, color=c, linewidth=1.2, alpha=0.9)

        self.comp_ax.axhline(
            0, color='white', linestyle='--', linewidth=0.5, alpha=0.5)
        self.comp_ax.tick_params(colors='white', labelsize=8)
        self.comp_ax.grid(True, linestyle=':', linewidth=0.5, color='#333333')
        for spine in self.comp_ax.spines.values():
            spine.set_edgecolor(COLOR_BORDER)

        self.comp_ax.legend(
            loc='lower left',
            bbox_to_anchor=(0, 1.02),
            fontsize=8,
            frameon=False,
            labelcolor='white',
            ncol=3,
            columnspacing=1.0,
            handletextpad=0.4
        )

        self.comp_canvas.draw()

    def toggle_graph(self, show):
        if show:
            self.comp_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        else:
            self.comp_frame.grid_remove()
