
import customtkinter as ctk
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from config import *


class ChartPanel(ctk.CTkFrame):
    def __init__(self, parent, callback_tf_change, callbacks_toggle=None):
        super().__init__(parent, fg_color="transparent")
        self.callback_tf_change = callback_tf_change
        self.callbacks_toggle = callbacks_toggle or {}
        self.toggle_states = {}

        self.current_interval = DEFAULT_INTERVAL
        self.tf_buttons = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_toolbar()
        self._create_chart_canvas()

    def _create_toolbar(self):
        toolbar = ctk.CTkFrame(self, height=35, fg_color=COLOR_BG_PANEL,
                               corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        ctk.CTkFrame(toolbar, width=17, height=20,
                     fg_color="transparent").pack(side="left")

        tfs = ["1m", "15m", "1H", "4H", "1D"]
        for tf in tfs:
            btn = ctk.CTkButton(
                toolbar, text=tf, width=30, height=20,
                fg_color=COLOR_ACTIVE if tf.lower(
                ) == self.current_interval.lower() else COLOR_BTN_DEFAULT,
                font=("Arial", 10, "bold"),
                command=lambda t=tf: self._on_tf_click(t)
            )
            btn.pack(side="left", padx=2, pady=5)
            self.tf_buttons[tf] = btn

        ctk.CTkFrame(toolbar, width=15, height=20,
                     fg_color="transparent").pack(side="right")
        self._create_toggle_btn(toolbar, "OB", "orderbook")
        self._create_toggle_btn(toolbar, "Tr", "trades")
        self._create_toggle_btn(toolbar, "Ov", "overview")

    def _create_toggle_btn(self, parent, text, key):
        self.toggle_states[key] = True

        btn = ctk.CTkButton(
            parent, text=text, width=30, height=20,
            font=("Arial", 10, "bold"),
            fg_color=COLOR_ACTIVE,
            hover_color=COLOR_BTN_DEFAULT
        )

        def on_click():
            self.toggle_states[key] = not self.toggle_states[key]
            is_on = self.toggle_states[key]

            btn.configure(
                fg_color=COLOR_ACTIVE if is_on else COLOR_BTN_DEFAULT)

            if key in self.callbacks_toggle:
                self.callbacks_toggle[key](is_on)

        btn.configure(command=on_click)
        btn.pack(side="right", padx=2, pady=5)

    def _on_tf_click(self, tf):
        self.current_interval = tf.lower()
        for key, btn in self.tf_buttons.items():
            if key == tf:
                btn.configure(fg_color=COLOR_ACTIVE)
            else:
                btn.configure(fg_color=COLOR_BTN_DEFAULT)
        self.callback_tf_change(self.current_interval)

    def _create_chart_canvas(self):
        self.chart_frame = ctk.CTkFrame(
            self, fg_color=COLOR_BG_MAIN, border_width=1, border_color=COLOR_BORDER)
        self.chart_frame.grid(row=1, column=0, sticky="nsew")

        self.fig = plt.Figure(dpi=100, facecolor=COLOR_BG_MAIN)
        gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1], figure=self.fig)
        self.ax1 = self.fig.add_subplot(gs[0])
        self.ax2 = self.fig.add_subplot(gs[1], sharex=self.ax1)
        self.fig.subplots_adjust(
            left=0.02, right=0.88, top=0.98, bottom=0.04, hspace=0.05)

        self.chart_canvas = FigureCanvasTkAgg(
            self.fig, master=self.chart_frame)
        self.chart_canvas.get_tk_widget().configure(highlightthickness=0, borderwidth=0)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_chart(self, df):
        if df.empty:
            return
        try:
            self.ax1.clear()
            self.ax2.clear()
            self.fig.patch.set_facecolor(COLOR_BG_MAIN)
            self.ax1.set_facecolor(COLOR_BG_MAIN)
            self.ax2.set_facecolor(COLOR_BG_MAIN)

            ma20 = df['close'].rolling(20).mean()
            ma50 = df['close'].rolling(50).mean()
            v_ma20 = ma20.iloc[-1] if len(ma20) > 0 else 0
            v_ma50 = ma50.iloc[-1] if len(ma50) > 0 else 0

            for ax in [self.ax1, self.ax2]:
                for spine in ax.spines.values():
                    spine.set_edgecolor(COLOR_BORDER)
                    spine.set_linewidth(1)

            self.ax1.yaxis.set_major_locator(
                MaxNLocator(nbins=6, prune='lower'))
            self.ax2.yaxis.set_major_locator(
                MaxNLocator(nbins=3, prune='upper'))

            mc = mpf.make_marketcolors(
                up=COLOR_GREEN, down=COLOR_RED, edge='inherit', wick='inherit',
                volume={'up': "#2e845c", 'down': "#992935"}, alpha=1.0,
            )
            s = mpf.make_mpf_style(
                marketcolors=mc, facecolor=COLOR_BG_MAIN, gridcolor='#333333', gridstyle='dotted',
                rc={'axes.facecolor': COLOR_BG_MAIN, 'figure.facecolor': COLOR_BG_MAIN, 'axes.edgecolor': COLOR_BG_MAIN,
                    'xtick.color': 'white', 'ytick.color': 'white', 'text.color': 'white', 'font.size': 8,
                    'axes.labelcolor': 'white', 'lines.linewidth': 0.8, 'axes.grid': True, 'axes.grid.axis': 'both'}
            )

            mpf.plot(
                df, type='candle', style=s, mav=(20, 50), mavcolors=['#00e5ff', '#ff9900'],
                ax=self.ax1, volume=self.ax2, xrotation=0, datetime_format='%H:%M',
                ylabel="", ylabel_lower="", scale_width_adjustment=dict(volume=0.5)
            )
            self.ax2.set_ylabel("")

            self.ax1.text(0.01, 0.94, f"MA(20): {v_ma20:,.2f}", transform=self.ax1.transAxes,
                          color='#00e5ff', fontsize=9, fontweight='bold', ha='left')
            self.ax1.text(0.01, 0.89, f"MA(50): {v_ma50:,.2f}", transform=self.ax1.transAxes,
                          color='#ff9900', fontsize=9, fontweight='bold', ha='left')

            self.ax1.grid(True, linestyle='dotted', color='#333333', alpha=0.5)
            self.ax1.yaxis.tick_right()
            self.ax1.tick_params(axis='y', colors='white', labelsize=8, pad=5)
            plt.setp(self.ax1.get_xticklabels(), visible=False)

            last_price = df['close'].iloc[-1]
            last_open = df['open'].iloc[-1]
            color_tag = COLOR_GREEN if last_price >= last_open else COLOR_RED
            self.ax1.axhline(last_price, color=color_tag,
                             linestyle='--', linewidth=0.8, alpha=0.8)
            self.ax1.text(
                x=1.005, y=last_price, s=f"{last_price:,.2f}", color='white', fontsize=9, fontweight='bold',
                va='center', ha='left', transform=self.ax1.get_yaxis_transform(),
                bbox=dict(boxstyle="square,pad=0.2", facecolor=color_tag, edgecolor=COLOR_BG_MAIN, alpha=1.0), clip_on=False
            )

            self.ax2.yaxis.tick_right()
            self.ax2.tick_params(axis='y', colors='white', labelsize=8, pad=5)
            self.ax2.tick_params(axis='x', colors='white',
                                 labelsize=8, labelbottom=True, pad=5)
            self.ax2.grid(False)
            for collection in self.ax2.collections:
                collection.set_linewidth(0)

            self.chart_canvas.draw()
        except Exception as e:
            print(f"Chart Drawing Error: {e}")
