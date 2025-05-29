import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from python_bitvavo_api.bitvavo import Bitvavo
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import queue

# Laad omgevingsvariabelen
load_dotenv()

# Bitvavo handelingskosten (0.25% voor maker en taker)
HANDELSKOSTEN_PERCENTAGE = 0.0025  # 0.25%
DAGELIJKS_DOEL_GROEI = 0.02  # 2%
CRYPTO_ASSET = 'BTC-EUR'

# Controleer API keys
if not os.getenv('BITVAVO_API_KEY') or not os.getenv('BITVAVO_API_SECRET'):
    raise ValueError("API keys ontbreken in .env bestand")

class BitvavoBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitvavo Trading Bot - 2% Dagelijkse Groei door MJ v2")
        self.root.geometry("1000x800")
        
        # Initialiseer Bitvavo API
        self.bitvavo = Bitvavo({
            'APIKEY': os.getenv('BITVAVO_API_KEY'),
            'APISECRET': os.getenv('BITVAVO_API_SECRET'),
            'RESTURL': 'https://api.bitvavo.com/v2',
            'WSURL': 'wss://ws.bitvavo.com/v2/',
        })
        
        self.actief = False
        self.berichten_wachtrij = queue.Queue()
        self.geschiedenis_data = []
        self.huidig_saldo = 0
        self.vorige_dag_saldo = 0
        self.start_saldo = 0
        self.start_datum = datetime.now()
        
        # Nieuwe variabelen voor winstbeheer
        self.winst_verkoop_prijs = None  # Prijs waarop winst verkocht is
        self.winst_hoeveelheid_btc = 0   # Hoeveelheid BTC die als winst verkocht is
        self.winst_verkocht_vandaag = False
        self.winst_teruggekocht_vandaag = False
        
        # Maak GUI componenten
        self.maak_widgets()
        
        # Start wachtrij verwerker
        self.root.after(100, self.verwerk_wachtrij)
        
        # Laad initiële gegevens
        self.laad_initiele_data()
    
    def maak_widgets(self):
        # Frame voor bediening
        bediening_frame = ttk.LabelFrame(self.root, text="Bot Bediening", padding=(10, 5))
        bediening_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Start/Stop knop
        self.start_stop_knop = ttk.Button(bediening_frame, text="Start Bot", command=self.wissel_bot)
        self.start_stop_knop.grid(row=0, column=0, padx=5, pady=5)
        
        # Saldo info
        self.saldo_label = ttk.Label(bediening_frame, text="Huidig Saldo: €0.00")
        self.saldo_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Doel info
        self.doel_label = ttk.Label(bediening_frame, text="Dagelijkse Doel: €0.00 (+2%)")
        self.doel_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Status info
        self.status_label = ttk.Label(bediening_frame, text="Status: Inactief")
        self.status_label.grid(row=0, column=3, padx=5, pady=5)
        
        # Winst info
        self.winst_label = ttk.Label(bediening_frame, text="Winstbeheer: Geen actieve winst")
        self.winst_label.grid(row=0, column=4, padx=5, pady=5)
        
        # Frame voor handmatige transacties
        transactie_frame = ttk.LabelFrame(self.root, text="Handmatige Transactie", padding=(10, 5))
        transactie_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Transactie bedrag
        ttk.Label(transactie_frame, text="Bedrag:").grid(row=0, column=0)
        self.transactie_bedrag = ttk.Entry(transactie_frame)
        self.transactie_bedrag.grid(row=0, column=1, padx=5)
        
        # Koop/Verkoop knoppen
        self.koop_knop = ttk.Button(transactie_frame, text="BTC Kopen", command=lambda: self.handmatige_transactie('buy'))
        self.koop_knop.grid(row=0, column=2, padx=5)
        
        self.verkoop_knop = ttk.Button(transactie_frame, text="BTC Verkopen", command=lambda: self.handmatige_transactie('sell'))
        self.verkoop_knop.grid(row=0, column=3, padx=5)
        
        # Frame voor historische data
        geschiedenis_frame = ttk.LabelFrame(self.root, text="Portefeuille Geschiedenis", padding=(10, 5))
        geschiedenis_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Treeview voor historische data
        self.geschiedenis_boom = ttk.Treeview(geschiedenis_frame, columns=('datum', 'saldo', 'doel', 'status'), show='headings')
        self.geschiedenis_boom.heading('datum', text='Datum')
        self.geschiedenis_boom.heading('saldo', text='Saldo (€)')
        self.geschiedenis_boom.heading('doel', text='Doel (€)')
        self.geschiedenis_boom.heading('status', text='Status')
        self.geschiedenis_boom.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(geschiedenis_frame, orient="vertical", command=self.geschiedenis_boom.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.geschiedenis_boom.configure(yscrollcommand=scrollbar.set)
        
        # Frame voor logs
        log_frame = ttk.LabelFrame(self.root, text="Logboek", padding=(10, 5))
        log_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        
        # ScrolledText voor logs
        self.log_tekst = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_tekst.grid(row=0, column=0, sticky="nsew")
        
        # Frame voor grafiek
        grafiek_frame = ttk.LabelFrame(self.root, text="Prestatie Grafiek", padding=(10, 5))
        grafiek_frame.grid(row=0, column=1, rowspan=4, padx=10, pady=10, sticky="nsew")
        
        # Matplotlib figuur
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=grafiek_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configureer grid row/column weights
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
    
    def laad_initiele_data(self):
        """Laad initiële portefeuille data en transactiegeschiedenis"""
        try:
            # Haal huidig saldo op
            saldo_response = self.bitvavo.balance({})
            eur_saldo = next((item for item in saldo_response if item['symbol'] == 'EUR'), None)
            btc_saldo = next((item for item in saldo_response if item['symbol'] == 'BTC'), None)
            
            if eur_saldo and btc_saldo:
                # Haal huidige BTC prijs op
                ticker = self.bitvavo.tickerPrice({'market': CRYPTO_ASSET})
                btc_prijs = float(ticker['price'])
                
                # Bereken totale waarde
                self.huidig_saldo = float(eur_saldo['available']) + (float(btc_saldo['available']) * btc_prijs)
                self.start_saldo = self.huidig_saldo
                self.vorige_dag_saldo = self.huidig_saldo
                
                # Update UI
                self.update_saldo_weergave()
                
                # Laad transactiegeschiedenis
                self.laad_transactie_geschiedenis()
                
                # Update grafiek
                self.update_grafiek()
                
                self.log("Initiële data succesvol geladen")
            else:
                self.log("Fout: Kon startsaldo niet ophalen")
        except Exception as e:
            self.log(f"Fout bij laden initiële data: {str(e)}")
    
    def laad_transactie_geschiedenis(self):
        """Laad transactiegeschiedenis van bestand of API"""
        try:
            # Probeer lokaal opgeslagen geschiedenis te laden
            if os.path.exists('transactie_geschiedenis.json'):
                with open('transactie_geschiedenis.json', 'r') as f:
                    self.geschiedenis_data = json.load(f)
                    # Update vorige dag saldo als er geschiedenis is
                    if self.geschiedenis_data:
                        self.vorige_dag_saldo = float(self.geschiedenis_data[-1]['saldo'])
            else:
                self.geschiedenis_data = []
                
            # Update geschiedenis boom
            self.update_geschiedenis_boom()
        except Exception as e:
            self.log(f"Fout bij laden transactiegeschiedenis: {str(e)}")
    
    def update_geschiedenis_boom(self):
        """Update de geschiedenis boom met huidige data"""
        self.geschiedenis_boom.delete(*self.geschiedenis_boom.get_children())
        
        for entry in self.geschiedenis_data:
            status = "Gehaald" if float(entry['saldo']) >= float(entry['doel']) else "Niet Gehaald"
            self.geschiedenis_boom.insert('', 'end', values=(
                entry['datum'],
                f"€{float(entry['saldo']):.2f}",
                f"€{float(entry['doel']):.2f}",
                status
            ))
    
    def update_saldo_weergave(self):
        """Update de saldo en doel weergaves"""
        vandaag_doel = self.vorige_dag_saldo * (1 + DAGELIJKS_DOEL_GROEI)
        
        self.saldo_label.config(text=f"Huidig Saldo: €{self.huidig_saldo:.2f}")
        self.doel_label.config(text=f"Dagelijkse Doel: €{vandaag_doel:.2f} (+{DAGELIJKS_DOEL_GROEI*100:.1f}%)")
        
        # Controleer of we het doel hebben gehaald
        if self.huidig_saldo >= vandaag_doel:
            self.status_label.config(text="Status: Doel Gehaald", foreground="green")
        else:
            self.status_label.config(text="Status: Doel Niet Gehaald", foreground="red")
        
        # Update winstinfo
        if self.winst_verkoop_prijs:
            winst_info = f"Winst verkocht: {self.winst_hoeveelheid_btc:.6f} BTC @ €{self.winst_verkoop_prijs:.2f}"
            self.winst_label.config(text=winst_info)
        else:
            self.winst_label.config(text="Winstbeheer: Geen actieve winst")
    
    def update_grafiek(self):
        """Update de prestatiegrafiek"""
        self.ax.clear()
        
        if self.geschiedenis_data:
            datums = [datetime.strptime(entry['datum'], '%Y-%m-%d') for entry in self.geschiedenis_data]
            saldos = [float(entry['saldo']) for entry in self.geschiedenis_data]
            doelen = [float(entry['doel']) for entry in self.geschiedenis_data]
            
            self.ax.plot(datums, saldos, label='Werkelijk Saldo', marker='o')
            self.ax.plot(datums, doelen, label='Doel Saldo', linestyle='--')
            
            # Voeg vandaag toe als apart punt
            vandaag_doel = self.vorige_dag_saldo * (1 + DAGELIJKS_DOEL_GROEI)
            self.ax.plot(datetime.now(), self.huidig_saldo, 'ro', label='Vandaag')
            
            self.ax.set_title('Portefeuille Prestatie')
            self.ax.set_xlabel('Datum')
            self.ax.set_ylabel('Saldo (€)')
            self.ax.legend()
            self.ax.grid(True)
            
            # Format x-axis
            self.fig.autofmt_xdate()
            
            self.canvas.draw()
    
    def log(self, bericht):
        """Voeg een bericht toe aan het logboek"""
        tijdstempel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_tekst.insert(tk.END, f"[{tijdstempel}] {bericht}\n")
        self.log_tekst.see(tk.END)
    
    def verwerk_wachtrij(self):
        """Verwerk berichten in de wachtrij"""
        while not self.berichten_wachtrij.empty():
            bericht = self.berichten_wachtrij.get_nowait()
            self.log(bericht)
        self.root.after(100, self.verwerk_wachtrij)
    
    def wissel_bot(self):
        """Start of stop de bot"""
        if not self.actief:
            self.actief = True
            self.start_stop_knop.config(text="Stop Bot")
            self.status_label.config(text="Status: Actief", foreground="blue")
            self.log("Bot gestart")
            
            # Start trading thread
            self.trading_thread = threading.Thread(target=self.draai_trading_strategie, daemon=True)
            self.trading_thread.start()
        else:
            self.actief = False
            self.start_stop_knop.config(text="Start Bot")
            self.status_label.config(text="Status: Gestopt", foreground="orange")
            self.log("Bot gestopt")
    
    def draai_trading_strategie(self):
        """Hoofd trading strategie die streeft naar 2% dagelijkse groei"""
        while self.actief:
            try:
                # Bereken huidig saldo en doel
                vandaag_doel = self.vorige_dag_saldo * (1 + DAGELIJKS_DOEL_GROEI)
                
                # Haal huidige marktprijs op
                ticker = self.bitvavo.tickerPrice({'market': CRYPTO_ASSET})
                huidige_prijs = float(ticker['price'])
                
                # Haal huidig saldo op
                saldo_response = self.bitvavo.balance({})
                eur_saldo = next((item for item in saldo_response if item['symbol'] == 'EUR'), None)
                btc_saldo = next((item for item in saldo_response if item['symbol'] == 'BTC'), None)
                
                if eur_saldo and btc_saldo:
                    beschikbaar_eur = float(eur_saldo['available'])
                    beschikbaar_btc = float(btc_saldo['available'])
                    self.huidig_saldo = beschikbaar_eur + (beschikbaar_btc * huidige_prijs)
                    
                    # Update UI via wachtrij
                    self.berichten_wachtrij.put(f"Huidig saldo: €{self.huidig_saldo:.2f}, Doel: €{vandaag_doel:.2f}")
                    
                    # Controleer of we het doel hebben bereikt
                    if self.huidig_saldo >= vandaag_doel and not self.winst_verkocht_vandaag:
                        # Verkoop de winst (2% van vorige dag saldo)
                        winst_bedrag = self.vorige_dag_saldo * DAGELIJKS_DOEL_GROEI
                        winst_btc = winst_bedrag / huidige_prijs
                        
                        if winst_btc > 0 and beschikbaar_btc >= winst_btc:
                            if self.plaats_order('sell', winst_btc):
                                self.winst_verkoop_prijs = huidige_prijs
                                self.winst_hoeveelheid_btc = winst_btc
                                self.winst_verkocht_vandaag = True
                                self.berichten_wachtrij.put(f"Winst verkocht: {winst_btc:.6f} BTC @ €{huidige_prijs:.2f}")
                    
                    # Controleer of we winst kunnen terugkopen
                    elif (self.winst_verkoop_prijs is not None and 
                          huidige_prijs < self.winst_verkoop_prijs and 
                          not self.winst_teruggekocht_vandaag):
                        
                        # Bereken hoeveel EUR we nodig hebben om de winst terug te kopen
                        benodigde_eur = self.winst_hoeveelheid_btc * huidige_prijs
                        
                        if beschikbaar_eur >= benodigde_eur:
                            if self.plaats_order('buy', self.winst_hoeveelheid_btc):
                                self.berichten_wachtrij.put(f"Winst teruggekocht: {self.winst_hoeveelheid_btc:.6f} BTC @ €{huidige_prijs:.2f}")
                                self.winst_teruggekocht_vandaag = True
                                self.winst_verkoop_prijs = None  # Reset winstbeheer
                    
                    # Update UI
                    self.root.after(0, self.update_saldo_weergave)
                    self.root.after(0, self.update_grafiek)
                
                # Wacht 1 minuut voordat we opnieuw controleren
                time.sleep(60)
                
            except Exception as e:
                self.berichten_wachtrij.put(f"Fout in trading strategie: {str(e)}")
                time.sleep(30)  # Wacht even bij een fout
    
    def plaats_order(self, soort, hoeveelheid):
        """Plaats een order op Bitvavo"""
        if hoeveelheid <= 0:
            return False
        
        try:
            market = CRYPTO_ASSET
            order_type = 'market'  # We gebruiken market orders voor eenvoud
            
            self.berichten_wachtrij.put(f"Plaats {soort} order voor {hoeveelheid:.6f} BTC")
            
            # Plaats de order
            order = self.bitvavo.placeOrder(market, soort, order_type, {
                'amount': str(hoeveelheid),
            })
            
            self.berichten_wachtrij.put(f"Order geplaatst: {order['orderId']}")
            
            # Wacht tot de order is uitgevoerd
            time.sleep(2)  # Simpele implementatie
            
            # Update saldo na order
            self.update_na_transactie()
            return True
            
        except Exception as e:
            self.berichten_wachtrij.put(f"Fout bij plaatsen order: {str(e)}")
            return False
    
    def update_na_transactie(self):
        """Update saldo na een transactie"""
        try:
            # Haal huidig saldo op
            saldo_response = self.bitvavo.balance({})
            eur_saldo = next((item for item in saldo_response if item['symbol'] == 'EUR'), None)
            btc_saldo = next((item for item in saldo_response if item['symbol'] == 'BTC'), None)
            
            if eur_saldo and btc_saldo:
                # Haal huidige BTC prijs op
                ticker = self.bitvavo.tickerPrice({'market': CRYPTO_ASSET})
                huidige_prijs = float(ticker['price'])
                
                # Bereken nieuw saldo
                self.huidig_saldo = float(eur_saldo['available']) + (float(btc_saldo['available']) * huidige_prijs)
                
                # Update UI
                self.root.after(0, self.update_saldo_weergave)
                self.root.after(0, self.update_grafiek)
                
        except Exception as e:
            self.berichten_wachtrij.put(f"Fout bij updaten na transactie: {str(e)}")
    
    def handmatige_transactie(self, soort):
        """Handmatige transactie uitvoeren"""
        try:
            hoeveelheid = float(self.transactie_bedrag.get())
            if hoeveelheid <= 0:
                messagebox.showerror("Fout", "Bedrag moet positief zijn")
                return
            
            self.plaats_order(soort, hoeveelheid)
            
        except ValueError:
            messagebox.showerror("Fout", "Ongeldig bedrag")
    
    def bewaar_geschiedenis(self):
        """Sla de transactiegeschiedenis op"""
        try:
            # Voeg vandaag toe aan de geschiedenis
            vandaag_doel = self.vorige_dag_saldo * (1 + DAGELIJKS_DOEL_GROEI)
            
            vandaag_data = {
                'datum': datetime.now().strftime('%Y-%m-%d'),
                'saldo': self.huidig_saldo,
                'doel': vandaag_doel,
                'status': 'Gehaald' if self.huidig_saldo >= vandaag_doel else 'Niet Gehaald'
            }
            
            # Voeg alleen toe als het een nieuwe dag is
            if not self.geschiedenis_data or self.geschiedenis_data[-1]['datum'] != vandaag_data['datum']:
                self.geschiedenis_data.append(vandaag_data)
                
                # Sla op naar bestand
                with open('transactie_geschiedenis.json', 'w') as f:
                    json.dump(self.geschiedenis_data, f)
                
                # Update UI
                self.root.after(0, self.update_geschiedenis_boom)
                self.root.after(0, self.update_grafiek)
                
                # Update vorige dag saldo voor morgen
                self.vorige_dag_saldo = self.huidig_saldo
                
                # Reset dagelijkse winststatus
                self.winst_verkocht_vandaag = False
                self.winst_teruggekocht_vandaag = False
        except Exception as e:
            self.berichten_wachtrij.put(f"Fout bij opslaan geschiedenis: {str(e)}")
    
    def bij_afsluiten(self):
        """Opschonen bij afsluiten"""
        if self.actief:
            self.actief = False
            self.trading_thread.join(timeout=2)
        
        # Sla geschiedenis op
        self.bewaar_geschiedenis()
        
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BitvavoBotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.bij_afsluiten)
    root.mainloop()