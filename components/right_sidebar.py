import customtkinter as ctk
from config import *


class RightSidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent", width=SIDEBAR_WIDTH)
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_orderbook()
        self._create_trades()

    def _create_orderbook(self):
        self.ob_frame = ctk.CTkFrame(
            self, fg_color=COLOR_BG_PANEL, corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        self.ob_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        ctk.CTkLabel(self.ob_frame, text="OrderBook", font=FONT_BOLD,
                     text_color=COLOR_TEXT_MAIN).pack(pady=5, anchor="w", padx=SIDE_PAD)

        self.ob_container = ctk.CTkFrame(self.ob_frame, fg_color="transparent")
        self.ob_container.pack(fill="both", expand=True)
        self.ob_rows = []
        for _ in range(ROW_LIMIT):
            c = ctk.CTkCanvas(self.ob_container, height=20,
                              bg=COLOR_BG_PANEL, highlightthickness=0)
            c.pack(fill="x", padx=5, pady=1)
            self.ob_rows.append(c)

    def _create_trades(self):
        self.tr_frame = ctk.CTkFrame(
            self, fg_color=COLOR_BG_PANEL, corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        self.tr_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0))

        ctk.CTkLabel(self.tr_frame, text="Recent Trades", font=FONT_BOLD,
                     text_color=COLOR_TEXT_MAIN).pack(pady=5, anchor="w", padx=SIDE_PAD)

        self.tr_container = ctk.CTkFrame(self.tr_frame, fg_color="transparent")
        self.tr_container.pack(fill="both", expand=True)
        self.tr_labels = []
        for _ in range(ROW_LIMIT):
            l = ctk.CTkLabel(self.tr_container, text="",
                             font=FONT_UNIFIED, anchor="w")
            l.pack(fill="x", padx=10, pady=0)
            self.tr_labels.append(l)

    def toggle_orderbook(self, show):
        if show:
            self.ob_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        else:
            self.ob_frame.grid_remove()

    def toggle_trades(self, show):
        if show:
            self.tr_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0))
        else:
            self.tr_frame.grid_remove()

    def update_orderbook(self, depth_data):
        if not depth_data or not self.ob_frame.winfo_viewable():
            return

        bids = depth_data.get('bids', [])
        asks = depth_data.get('asks', [])
        if not bids or not asks:
            return

        max_vol_bid = sum([float(x[1]) for x in bids[:ROW_LIMIT]])
        max_vol_ask = sum([float(x[1]) for x in asks[:ROW_LIMIT]])
        max_vol = max(max_vol_bid, max_vol_ask) if max_vol_bid > 0 else 1.0

        half = ROW_LIMIT // 2
        asks_slice = asks[:half][::-1]
        bids_slice = bids[:half]

        display_data = [(float(p), float(q), False) for p, q in asks_slice] + \
                       [(float(p), float(q), True) for p, q in bids_slice]

        for i, canvas in enumerate(self.ob_rows):
            canvas.delete("all")
            if i < len(display_data):
                price, vol, is_bid = display_data[i]
                self._draw_bar(canvas, price, vol, max_vol, is_bid)

    def _draw_bar(self, canvas, p, q, max_v, is_bid):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        bar_w = (q / max_v) * w * 0.8

        color_bg = "#0f2e22" if is_bid else "#38141a"
        color_fg = COLOR_GREEN if is_bid else COLOR_RED

        canvas.create_rectangle(w - bar_w, 0, w, h, fill=color_bg, outline="")
        canvas.create_text(
            5, h/2, anchor="w", text=f"{p:,.2f}", fill=color_fg, font=("Consolas", 10, "bold"))
        canvas.create_text(
            w-5, h/2, anchor="e", text=f"{q:.4f}", fill=COLOR_TEXT_MAIN, font=("Consolas", 10))

    def update_trades(self, trades_list):
        if not trades_list or not self.tr_frame.winfo_viewable():
            return

        for i, lbl in enumerate(self.tr_labels):
            if i < len(trades_list):
                t = trades_list[i]
                p = float(t['p'])
                q = float(t['q'])
                is_buyer_maker = t['m']
                color = COLOR_RED if is_buyer_maker else COLOR_GREEN

                lbl.configure(text=f"{p:,.2f}      {q:.4f}", text_color=color)
            else:
                lbl.configure(text="")
