
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import *

class LeftSidebar(ctk.CTkFrame):
    def __init__(self, parent, callback_symbol_change):
        super().__init__(parent, fg_color="transparent", width=SIDEBAR_WIDTH)
        self.callback_symbol_change = callback_symbol_change
        
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_watchlist()
        self._create_comparison_graph()

    def _create_watchlist(self):
        wl_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_PANEL, corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        wl_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        h = ctk.CTkFrame(wl_frame, fg_color="transparent", height=30)
        h.pack(fill="x", padx=0, pady=(5, 2))
        ctk.CTkLabel(h, text="Watchlist", font=FONT_BOLD, text_color=COLOR_TEXT_MAIN).pack(side="left", padx=SIDE_PAD)
        
        h_sub = ctk.CTkFrame(wl_frame, fg_color="transparent")
        h_sub.pack(fill="x", padx=0, pady=(0, 2))
        ctk.CTkLabel(h_sub, text="Coin", font=("Arial", 10), text_color=COLOR_TEXT_SUB).pack(side="left", padx=SIDE_PAD+5)
        ctk.CTkLabel(h_sub, text="Price", font=("Arial", 10), text_color=COLOR_TEXT_SUB).pack(side="right", padx=SIDE_PAD+5)

        self.watchlist_container = ctk.CTkFrame(wl_frame, fg_color="transparent")
        self.watchlist_container.pack(fill="both", expand=True, pady=0)

        self.watchlist_widgets = {} 
        for coin in DEFAULT_COINS:
            row = ctk.CTkFrame(self.watchlist_container, fg_color="transparent", height=26, corner_radius=4)
            row.pack(fill="x", pady=1, padx=2)
            row.pack_propagate(False)
            
            lbl_name = ctk.CTkLabel(row, text=f"{coin}", font=FONT_UNIFIED, text_color=COLOR_TEXT_MAIN)
            lbl_name.pack(side="left", padx=SIDE_PAD+5)
            
            lbl_price = ctk.CTkLabel(row, text="---", font=FONT_UNIFIED, text_color=COLOR_TEXT_MAIN)
            lbl_price.pack(side="right", padx=SIDE_PAD+5)

            def on_enter(e, f=row): f.configure(fg_color=COLOR_BTN_DEFAULT)
            def on_leave(e, f=row): f.configure(fg_color="transparent")
            def on_click(e, c=coin): self._on_coin_click(c)
            for widget in [row, lbl_name, lbl_price]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", on_click)
            self.watchlist_widgets[coin+"USDT"] = lbl_price

    def _on_coin_click(self, coin):
        pair = f"{coin}USDT"
        self.callback_symbol_change(pair, coin)

    def _create_comparison_graph(self):
        self.comp_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_PANEL, corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        self.comp_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0))
        
        ctk.CTkLabel(self.comp_frame, text="24h Overview (%)", font=FONT_BOLD, text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=SIDE_PAD, pady=(5, 0))
        
        canvas_cont = ctk.CTkFrame(self.comp_frame, fg_color="transparent")
        canvas_cont.pack(fill="both", expand=True, padx=2, pady=(2, 0))

        self.comp_fig = plt.Figure(dpi=100, facecolor=COLOR_BG_PANEL)
        self.comp_ax = self.comp_fig.add_subplot(111)
        self.comp_ax.set_facecolor(COLOR_BG_PANEL)
        self.comp_fig.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.08)

        self.comp_ax.spines['bottom'].set_color(COLOR_TEXT_SUB)
        self.comp_ax.spines['left'].set_color(COLOR_TEXT_SUB)
        self.comp_ax.spines['top'].set_visible(False)
        self.comp_ax.spines['right'].set_visible(False)
        self.comp_ax.tick_params(axis='x', colors=COLOR_TEXT_SUB, labelsize=0) 
        self.comp_ax.tick_params(axis='y', colors=COLOR_TEXT_SUB, labelsize=7)
        self.comp_ax.grid(True, linestyle=':', linewidth=0.5, color='#333333')

        self.comp_canvas = FigureCanvasTkAgg(self.comp_fig, master=canvas_cont)
        self.comp_canvas.get_tk_widget().configure(highlightthickness=0, borderwidth=0)
        self.comp_canvas.get_tk_widget().pack(fill="both", expand=True)

    def toggle_overview(self, show):
        if show:
            self.comp_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0))
        else:
            self.comp_frame.grid_remove()

    def update_watchlist(self, all_prices):
        if not all_prices: return
        p_map = {x['symbol']: x['price'] for x in all_prices}
        for s, lbl in self.watchlist_widgets.items():
            if s in p_map:
                lbl.configure(text=f"{float(p_map[s]):,.2f}")

    def update_comparison(self, data):
        if not data or not self.comp_frame.winfo_viewable(): return # ไม่ต้องวาดถ้าซ่อนอยู่
        try:
            self.comp_ax.clear()
            self.comp_ax.set_facecolor(COLOR_BG_PANEL)
            self.comp_fig.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.08)
            
            colors = ['#00ff88', '#00d0ff', '#ff0055', '#ffe600', '#aa00ff', '#ff8800', '#ffffff']
            for i, (coin, vals) in enumerate(data.items()):
                if len(vals) > 0:
                    c = colors[i % len(colors)]
                    self.comp_ax.plot(range(len(vals)), vals, label=coin, color=c, linewidth=1.2, alpha=0.9)
            
            self.comp_ax.axhline(0, color='white', linestyle='--', linewidth=0.5, alpha=0.5)
            self.comp_ax.spines['bottom'].set_color(COLOR_TEXT_SUB)
            self.comp_ax.spines['left'].set_color(COLOR_TEXT_SUB)
            self.comp_ax.spines['top'].set_visible(False)
            self.comp_ax.spines['right'].set_visible(False)
            self.comp_ax.tick_params(axis='x', colors=COLOR_TEXT_SUB, labelsize=0)
            self.comp_ax.tick_params(axis='y', colors=COLOR_TEXT_SUB, labelsize=7)
            self.comp_ax.grid(True, linestyle=':', linewidth=0.5, color='#333333', alpha=0.5)

            leg = self.comp_ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, fontsize=7, frameon=False, handlelength=1.0, handletextpad=0.2, columnspacing=0.8)
            for line, text in zip(leg.get_lines(), leg.get_texts()):
                text.set_color(line.get_color())
            
            self.comp_canvas.draw()
        except Exception as e: print(f"Comp draw error: {e}")
