import requests
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading

# API endpoints
GAMERPOWER_API = "https://www.gamerpower.com/api/giveaways"
CHEAPSHARK_API = "https://www.cheapshark.com/api/1.0/deals"

class GameDealsApp:
    def __init__(self, root):
        self.root = root
        root.title("Ultimate Game Deals & Free Giveaways Finder")
        root.geometry("900x650")
        root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tabs
        self.free_tab = ttk.Frame(self.notebook)
        self.deals_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.free_tab, text='🎁 Free Giveaways')
        self.notebook.add(self.deals_tab, text='💰 Game Deals')

        self.setup_free_tab()
        self.setup_deals_tab()

        # Load data
        self.load_free_giveaways()
        self.load_game_deals()

        # Auto-refresh every 5 mins
        self.root.after(5 * 60 * 1000, self.auto_refresh)

    # ---------- FREE GIVEAWAYS TAB ----------
    def setup_free_tab(self):
        frame = self.free_tab

        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', pady=5)

        ttk.Label(control_frame, text="Search:").pack(side='left', padx=(0, 5))
        self.free_search_var = tk.StringVar()
        free_search_entry = ttk.Entry(control_frame, textvariable=self.free_search_var, width=30)
        free_search_entry.pack(side='left')
        free_search_entry.bind('<Return>', lambda e: self.filter_free())

        ttk.Button(control_frame, text="Filter", command=self.filter_free).pack(side='left', padx=5)

        ttk.Label(control_frame, text="Platform:").pack(side='left', padx=(15,5))
        self.platform_var = tk.StringVar(value="all")
        platforms = ['all', 'pc', 'steam', 'epic-games-store', 'gog', 'origin', 'ubisoft']
        platform_menu = ttk.OptionMenu(control_frame, self.platform_var, 'all', *platforms, command=lambda e: self.load_free_giveaways())
        platform_menu.pack(side='left')

        # Treeview setup
        columns = ('Title', 'Platforms', 'Value (USD)', 'Expires', 'Link')
        self.free_tree = ttk.Treeview(frame, columns=columns, show='headings', height=25)
        for col in columns[:-1]:
            self.free_tree.heading(col, text=col)
            self.free_tree.column(col, width=150, anchor='w')
        self.free_tree.heading('Link', text='Link')
        self.free_tree.column('Link', width=50, anchor='center')

        self.free_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.free_tree.bind('<Double-1>', self.open_selected_free)
        
        ttk.Button(frame, text="Copy Selected Link", command=self.copy_free_link).pack(pady=5)

    def load_free_giveaways(self):
        def fetch():
            try:
                platform = self.platform_var.get()
                url = GAMERPOWER_API
                if platform != 'all':
                    url += f"?platform={platform}"
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                self.free_giveaways = resp.json()
                self.filtered_free_giveaways = self.free_giveaways
                self.show_free(self.free_giveaways)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load giveaways: {e}")

        threading.Thread(target=fetch, daemon=True).start()

    def show_free(self, giveaways):
        self.free_tree.delete(*self.free_tree.get_children())
        for g in giveaways:
            title = g.get('title', 'N/A')
            platforms = ", ".join(g.get('platforms', []))
            value = g.get('worth', 'N/A')
            expires = g.get('end_date', 'N/A')
            link = g.get('open_giveaway_url', '')
            self.free_tree.insert('', 'end', values=(title, platforms, value, expires, "Open"))

    def filter_free(self):
        keyword = self.free_search_var.get().lower()
        filtered = [g for g in self.free_giveaways if keyword in g.get('title','').lower()]
        self.filtered_free_giveaways = filtered
        self.show_free(filtered)

    def open_selected_free(self, event):
        item = self.free_tree.selection()
        if item:
            index = self.free_tree.index(item[0])
            giveaway = self.filtered_free_giveaways[index]
            link = giveaway.get('open_giveaway_url')
            if link:
                webbrowser.open(link)

    def copy_free_link(self):
        item = self.free_tree.selection()
        if item:
            index = self.free_tree.index(item[0])
            giveaway = self.filtered_free_giveaways[index]
            link = giveaway.get('open_giveaway_url')
            if link:
                self.root.clipboard_clear()
                self.root.clipboard_append(link)
                messagebox.showinfo("Copied", "Giveaway link copied to clipboard!")

    # ---------- GAME DEALS TAB ----------
    def setup_deals_tab(self):
        frame = self.deals_tab

        control_frame = ttk.Frame(frame)
        control_frame.pack(fill='x', pady=5)

        ttk.Label(control_frame, text="Search:").pack(side='left', padx=(0, 5))
        self.deal_search_var = tk.StringVar()
        deal_search_entry = ttk.Entry(control_frame, textvariable=self.deal_search_var, width=30)
        deal_search_entry.pack(side='left')
        deal_search_entry.bind('<Return>', lambda e: self.load_game_deals())

        ttk.Label(control_frame, text="Sort by:").pack(side='left', padx=(15,5))
        self.sort_var = tk.StringVar(value="Deal Rating")
        sort_options = ['Deal Rating', 'Price', 'Savings']
        sort_menu = ttk.OptionMenu(control_frame, self.sort_var, 'Deal Rating', *sort_options, command=lambda e: self.load_game_deals())
        sort_menu.pack(side='left')

        # Treeview setup
        columns = ('Title', 'Store', 'Sale Price', 'Normal Price', 'Savings (%)', 'Link')
        self.deals_tree = ttk.Treeview(frame, columns=columns, show='headings', height=25)
        widths = [250, 100, 100, 100, 100, 50]
        for col, width in zip(columns, widths):
            self.deals_tree.heading(col, text=col)
            self.deals_tree.column(col, width=width, anchor='w' if col == 'Title' else 'center')

        self.deals_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.deals_tree.bind('<Double-1>', self.open_selected_deal)
        ttk.Button(frame, text="Copy Selected Link", command=self.copy_deal_link).pack(pady=5)

    def load_game_deals(self):
        def fetch():
            try:
                query = self.deal_search_var.get().strip()
                sort_map = {
                    'Deal Rating': 'dealRating',
                    'Price': 'price',
                    'Savings': 'savings'
                }
                sort_by = sort_map.get(self.sort_var.get(), 'dealRating')
                params = {
                    'storeID': '1',  # Steam store by default; can be expanded to choose
                    'sortBy': sort_by,
                    'desc': '1',
                    'pageSize': '50',
                    'title': query if query else None,
                }
                # Remove None values
                params = {k: v for k, v in params.items() if v is not None}
                resp = requests.get(CHEAPSHARK_API, params=params, timeout=15)
                resp.raise_for_status()
                self.game_deals = resp.json()
                self.show_deals(self.game_deals)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load game deals: {e}")

        threading.Thread(target=fetch, daemon=True).start()

    def show_deals(self, deals):
        self.deals_tree.delete(*self.deals_tree.get_children())
        self.current_deals = deals
        for d in deals:
            title = d.get('title', 'N/A')
            store = d.get('storeID', 'N/A')
            sale_price = f"${d.get('salePrice', 'N/A')}"
            normal_price = f"${d.get('normalPrice', 'N/A')}"
            savings = f"{d.get('savings', '0')[:4]}%" if 'savings' in d else '0%'
            deal_link = f"https://www.cheapshark.com/redirect?dealID={d.get('dealID')}"
            self.deals_tree.insert('', 'end', values=(title, store, sale_price, normal_price, savings, "Open"))

    def open_selected_deal(self, event):
        item = self.deals_tree.selection()
        if item:
            index = self.deals_tree.index(item[0])
            deal = self.current_deals[index]
            deal_link = f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}"
            webbrowser.open(deal_link)

    def copy_deal_link(self):
        item = self.deals_tree.selection()
        if item:
            index = self.deals_tree.index(item[0])
            deal = self.current_deals[index]
            deal_link = f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}"
            self.root.clipboard_clear()
            self.root.clipboard_append(deal_link)
            messagebox.showinfo("Copied", "Deal link copied to clipboard!")

    def auto_refresh(self):
        self.load_free_giveaways()
        self.load_game_deals()
        self.root.after(5 * 60 * 1000, self.auto_refresh)  # Refresh every 5 minutes

if __name__ == "__main__":
    root = tk.Tk()
    app = GameDealsApp(root)
    root.mainloop()
