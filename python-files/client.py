import asyncio
import csv
import datetime
import json
import os
import re
import sys
import tempfile
import threading
import time
import tkinter as tk
import unicodedata
import uuid
import webbrowser
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote, urlparse

import aiohttp
import customtkinter as ctk
import pandas as pd
import phonenumbers
import psutil
import requests
import undetected_chromedriver as uc
import webview  # For embedded browser CAPTCHA solving
from bs4 import BeautifulSoup, SoupStrainer
from PIL import Image, ImageTk
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.common.exceptions import (JavascriptException,
                                        NoSuchElementException,
                                        NoSuchWindowException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Discord RPC imports
try:
    from pypresence import Presence
    DISCORD_RPC_AVAILABLE = True
except ImportError:
    DISCORD_RPC_AVAILABLE = False
    print("Discord RPC")

# Global variables for scraping
SCRAPING_DATA = {
    'names': [],
    'addresses': [],
    'websites': [],
    'phones': [],
    'keywords': [],
    'opens': [],
    'scraped_urls': set()
}

ZIP_CODE_DATABASE = {
    "Germany": [
        "10115", "20095", "60311", "50667", "70173",  # Berlin, Hamburg, Frankfurt, Cologne, Stuttgart
        "80331", "40213", "45127", "60486",           # Munich, Düsseldorf, Essen, Frankfurt
        "01067", "04109", "06108", "09111", "10178"   # Dresden, Leipzig, Halle, Chemnitz, Berlin
    ],
    "France": [
        "75001", "75008", "13001", "69001", "31000",  # Paris (1st/8th), Marseille, Lyon, Toulouse
        "06000", "33000", "67000", "59000",           # Nice, Bordeaux, Strasbourg, Lille
        "34000", "44000", "54000", "35000"            # Montpellier, Nantes, Nancy, Rennes
    ],
    "Belgium": [
        "1000", "2000", "3000", "4000", "5000",      # Brussels, Antwerp, Leuven, Liège, Namur
        "6000", "7000", "8000", "9000",              # Charleroi, Mons, Bruges, Ghent
        "3500", "8500", "3501"                       # Hasselt, Kortrijk, Genk
    ],
    "Netherlands": [
        "1012", "1071", "2511", "3511", "5011",      # Amsterdam, Amsterdam, The Hague, Utrecht, Eindhoven
        "3011", "1017", "5611", "6211",              # Rotterdam, Amsterdam, Eindhoven, Maastricht
        "7511", "8011", "8911", "9711"               # Enschede, Zwolle, Apeldoorn, Groningen
    ],
    # "Italy": [
    #     "00100", "20121", "50121", "80121", "90121", # Rome, Milan, Florence, Naples, Palermo
    #     "16121", "35121", "37121", "44121",          # Genoa, Padua, Verona, Ferrara
    #     "10121", "30121", "40121"                    # Turin, Venice, Bologna
    # ],
    "Spain": [
        "28001", "08001", "46001", "41001", "48001", # Madrid, Barcelona, Valencia, Seville, Bilbao
        "50001", "15001", "03001", "07001",          # Zaragoza, A Coruña, Alicante, Palma
        "29001", "33001", "36201"                    # Malaga, Oviedo, Vigo
    ],
    "United Kingdom": [
        "EC1A 1BB", "WC2N 5DU", "M1 1AE", "B1 1HQ", # London, London, Manchester, Birmingham
        "G1 1XL", "EH1 1YZ", "L1 8JQ", "LS1 4AP",   # Glasgow, Edinburgh, Liverpool, Leeds
        "CF10 1BH", "BT1 5GS", "S1 2GH"             # Cardiff, Belfast, Sheffield
    ],
    "Sweden": [
        "11120", "11320", "21120", "41120",          # Stockholm, Stockholm, Stockholm, Gothenburg
        "58120", "22220", "75120", "85220",          # Linköping, Malmö, Uppsala, Sundsvall
        "90720", "97120"                             # Umeå, Luleå
    ],
    "Poland": [
        "00001", "30001", "50001", "80001",          # Warsaw, Kraków, Wrocław, Gdańsk
        "40001", "90001", "60001", "70001",          # Katowice, Łódź, Poznań, Szczecin
        "35001", "20001"                             # Rzeszów, Lublin
    ],
    "USA": [
        "10001", "90001", "60601", "77001", "85001", # New York, Los Angeles, Chicago, Houston, Phoenix
        "19101", "33101", "98101", "94101",          # Philadelphia, Miami, Seattle, San Francisco
        "02101", "75201", "19103"                   # Boston, Dallas, Philadelphia
    ]
}

REGION_FULL_NAMES = {
    "Germany": {
        "BE": "Berlin", 
        "HH": "Hamburg", 
        "NW": "North Rhine-Westphalia",
        "HE": "Hesse", 
        "BW": "Baden-Württemberg", 
        "BY": "Bavaria"
    },
    "France": {
        "IDF": "Île-de-France", 
        "PACA": "Provence-Alpes-Côte d'Azur",
        "ARA": "Auvergne-Rhône-Alpes", 
        "OCC": "Occitanie",
        "HDF": "Hauts-de-France", 
        "NAQ": "Nouvelle-Aquitaine"
    },
    "Belgium": {
        "BRU": "Brussels", 
        "VAN": "Antwerp", 
        "VBR": "Flemish Brabant",
        "WLG": "Liège", 
        "WNA": "Namur", 
        "WHT": "Hainaut",
        "VWV": "West Flanders", 
        "OVL": "East Flanders"
    },
    "Netherlands": {
        "NH": "North Holland", 
        "UT": "Utrecht", 
        "NB": "North Brabant", 
        "FR": "Friesland"
    },
    # "Italy": {
    #     "RM": "Rome/Lazio", 
    #     "MI": "Milan/Lombardy", 
    #     "FI": "Florence/Tuscany",
    #     "NA": "Naples/Campania", 
    #     "PA": "Palermo/Sicily", 
    #     "GE": "Genoa/Liguria"
    # },
    "Spain": {
        "MD": "Madrid", 
        "CT": "Catalonia", 
        "VC": "Valencia",
        "AN": "Andalusia", 
        "PV": "Basque Country", 
        "AR": "Aragon"
    },
    "United Kingdom": {
        "LON": "London", 
        "MAN": "Manchester", 
        "BIR": "Birmingham",
        "GLA": "Glasgow", 
        "EDH": "Edinburgh", 
        "LIV": "Liverpool",
        "LDS": "Leeds"
    },
    "Sweden": {
        "AB": "Stockholm", 
        "C": "Gothenburg", 
        "O": "Linköping",
        "M": "Malmö", 
        "U": "Uppsala", 
        "S": "Sundsvall",
        "BD": "Luleå"
    },
    "Poland": {
        "MZ": "Masovian (Warsaw)", 
        "MA": "Lesser Poland (Kraków)",
        "DS": "Lower Silesian (Wrocław)", 
        "PM": "Pomeranian (Gdańsk)",
        "SL": "Silesian (Katowice)", 
        "LD": "Łódź",
        "WP": "Greater Poland (Poznań)", 
        "ZP": "West Pomeranian (Szczecin)"
    },
    "USA": {
        "NY": "New York", 
        "CA": "California", 
        "IL": "Illinois",
        "TX": "Texas", 
        "FL": "Florida", 
        "PA": "Pennsylvania",
        "WA": "Washington", 
        "AZ": "Arizona"
    }
}
# Scraping selectors
SELECTORS = {
    'search_input': '//input[@id="searchboxinput"]',
    'listing_links': '//a[contains(@href, "https://www.google.com/maps/place")]',
    'name': '//h1[contains(@class, "DUwDvf")]',
    'address': '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]',
    'website': '//a[@data-item-id="authority"]',
    'phone': '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]',
    'opens_at': '//div[contains(@class, "MkV9")]//div[contains(@class, "fontBodyMedium")]',
    'opens_at_alt': '//div[contains(@class, "OqCZI")]'  # Alternative selector for opening hours
}

# Add this constant at the top with other constants
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1393414439914569748/mUKH7RiXDyE6B_T3097uciMSzZyGqH0efHvMW3gQPDBllUU7qvV-X2_tqpaOvRnt7BDl"
DISCORD_WEBHOOK_URL_2 = "https://discord.com/api/webhooks/818868536327405630/45K5WhpE5z2qWENhVc4wiw62Td0gxYrPOQqZkyV3AlcYg_kCDuuvDLcMt_Vk5F450Nqe"

# Discord RPC Configuration
DISCORD_RPC_CLIENT_ID = "1392634785813368955"  # Replace with your Discord Application ID
DISCORD_RPC_APP_NAME = "Clients Hunting Tool"
DISCORD_RPC_WEBSITE_URL = "https://clientshunting.com"
DISCORD_RPC_LOGO_URL = "https://cdn.discordapp.com/attachments/844082437332008960/1407864568251809875/logo.png?ex=68a7a78d&is=68a6560d&hm=0ee4c08951092f47cbad6168e9716da8c8ab4800466051ec89f9fd872c4c3bd0&"

# Email regex pattern
email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

def send_to_discord_webhooks(message, files=None):
    """Send message and files to both webhooks"""
    success_count = 0
    
    # Send to first webhook (Captain Hook - primary)
    try:
        if message:
            response1 = requests.post(DISCORD_WEBHOOK_URL, json=message, timeout=10)
            if response1.status_code in [200, 204]:  # Both 200 and 204 are success
                success_count += 1
                print(f"Captain Hook webhook message sent successfully: {response1.status_code}")
            else:
                print(f"Error sending message to Captain Hook webhook: {response1.status_code} - {response1.text}")
        if files:
            response1_file = requests.post(DISCORD_WEBHOOK_URL, files=files, timeout=30)
            if response1_file.status_code in [200, 204]:  # Both 200 and 204 are success
                success_count += 1
                print(f"Captain Hook webhook file sent successfully: {response1_file.status_code}")
            else:
                print(f"Error sending file to Captain Hook webhook: {response1_file.status_code} - {response1_file.text}")
    except Exception as e:
        print(f"Error sending to Captain Hook webhook: {str(e)}")
    
    # Send to second webhook (kids - backup)
    try:
        if message:
            response2 = requests.post(DISCORD_WEBHOOK_URL_2, json=message, timeout=10)
            if response2.status_code in [200, 204]:  # Both 200 and 204 are success
                success_count += 1
                print(f"Kids webhook message sent successfully: {response2.status_code}")
            else:
                print(f"Error sending message to kids webhook: {response2.status_code} - {response2.text}")
        if files:
            response2_file = requests.post(DISCORD_WEBHOOK_URL_2, files=files, timeout=30)
            if response2_file.status_code in [200, 204]:  # Both 200 and 204 are success
                success_count += 1
                print(f"Kids webhook file sent successfully: {response2_file.status_code}")
            else:
                print(f"Error sending file to kids webhook: {response2_file.status_code} - {response2_file.text}")
    except Exception as e:
        print(f"Error sending to kids webhook: {str(e)}")
    
    # Log overall success/failure
    if success_count > 0:
        print(f"Successfully sent to {success_count} webhook(s)")
    else:
        print("Failed to send to any webhooks")
    
    # Return success count for external file cleanup
    return success_count

class DiscordRPCManager:
    """Manages Discord Rich Presence for the application"""
    
    def __init__(self):
        self.rpc = None
        self.is_connected = False
        self.current_activity = "In Menu"
        self.start_time = int(time.time())
        
    def connect(self):
        """Connect to Discord RPC"""
        if not DISCORD_RPC_AVAILABLE:
            return False
            
        try:
            self.rpc = Presence(DISCORD_RPC_CLIENT_ID)
            self.rpc.connect()
            self.is_connected = True
            print("✅ Discord RPC connected successfully")
            return True
        except Exception as e:
            print(f"❌ Discord RPC connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from Discord RPC"""
        if self.rpc and self.is_connected:
            try:
                self.rpc.close()
                self.is_connected = False
                print("🔌 Discord RPC disconnected")
            except Exception as e:
                print(f"❌ Discord RPC disconnect error: {str(e)}")
    
    def update_presence(self, activity, details=None, state=None):
        """Update Discord Rich Presence"""
        if not self.is_connected or not self.rpc:
            return
            
        try:
            # Prepare the presence data
            presence_data = {
                "details": details or f"Using {DISCORD_RPC_APP_NAME}",
                "state": state or activity,
                "large_image": "logo",
                "large_text": DISCORD_RPC_APP_NAME,
                "small_image": "logo",
                "small_text": "Active",
                "start": self.start_time,
                "buttons": [
                    {
                        "label": "Website",
                        "url": DISCORD_RPC_WEBSITE_URL
                    }
                ]
            }
            
            # Update the presence
            self.rpc.update(**presence_data)
            self.current_activity = activity
            print(f"🎮 Discord RPC updated: {activity}")
            
        except Exception as e:
            print(f"❌ Discord RPC update error: {str(e)}")
    
    def set_scraping_activity(self, scraper_name, status="Scraping"):
        """Set activity for scraping operations"""
        if scraper_name == "G":
            scraper_full = "Google Scraper"
        elif scraper_name == "M":
            scraper_full = "Email Scraper"
        elif scraper_name == "A":
            scraper_full = "Amazon Scraper"
        elif scraper_name == "AU":
            scraper_full = "AU Scraper"
        else:
            scraper_full = f"{scraper_name} Scraper"
            
        self.update_presence(
            activity=f"{status} with {scraper_full}",
            details=f"Searching for clients using {scraper_full}",
            state=f"Status: {status}"
        )
    
    def set_menu_activity(self):
        """Set activity for main menu"""
        self.update_presence(
            activity="In Main Menu",
            details=f"Using {DISCORD_RPC_APP_NAME}",
            state="Ready to scrape"
        )
    
    def set_export_activity(self, scraper_name):
        """Set activity for export operations"""
        scraper_full = {
            "G": "Google Scraper",
            "M": "Email Scraper", 
            "A": "Amazon Scraper",
            "AU": "AU Scraper"
        }.get(scraper_name, f"{scraper_name} Scraper")
        
        self.update_presence(
            activity=f"Exporting {scraper_full} Results",
            details=f"Processing and sharing {scraper_full} data",
            state="Exporting to CSV and sharing"
        )

class ModernUI:
    """Modern Dark UI theme with Windows 11 aesthetics"""
    # Colors - modern dark theme
    BG_COLOR = "#1E1E1E"  # Dark background
    SECONDARY_BG = "#252526"  # Slightly lighter background
    ACCENT_COLOR = "#66FF00"  # Lime green from the image
    HOVER_COLOR = "#5AE600"  # Slightly darker lime green for hover
    TEXT_COLOR = "#FFFFFF"  # White text
    INPUT_BG = "#333333"  # Dark input background
    BORDER_COLOR = "#333333"  # Subtle border
    SUCCESS_COLOR = "#13A10E"  # Green
    ERROR_COLOR = "#C42B1C"  # Red
    
    
    # Fonts - modern and clean
    TITLE_FONT = ("Segoe UI", 28, "bold")
    SUBTITLE_FONT = ("Segoe UI", 16)
    NORMAL_FONT = ("Segoe UI", 12)
    SMALL_FONT = ("Segoe UI", 11)
    
    @staticmethod
    def configure_styles():
        style = ttk.Style()
        style.theme_use('clam')
        # Updated ModernUI colors for better HCI
        ModernUI.BG_COLOR = "#1E1E1E"  # Dark background
        ModernUI.SECONDARY_BG = "#252526"  # Slightly lighter background
        ModernUI.ACCENT_COLOR = "#66FF00"  # Lime green from the image
        ModernUI.HOVER_COLOR = "#5AE600"  # Slightly darker lime green for hover
        ModernUI.TEXT_COLOR = "#FFFFFF"  # White text
        ModernUI.INPUT_BG = "#333333"  # Dark input background
        ModernUI.BORDER_COLOR = "#333333"  # Subtle border
        ModernUI.SUCCESS_COLOR = "#4CAF50"  # Green (success)
        ModernUI.ERROR_COLOR = "#F44336"  # Red (error)
        ModernUI.WARNING_COLOR = "#FFC107"  # Yellow (warning)
        ModernUI.DISABLED_COLOR = "#666666"  # Gray (disabled)
        # Configure frame styles
        style.configure('Modern.TFrame', background=ModernUI.BG_COLOR)
        style.configure('Secondary.TFrame', background=ModernUI.SECONDARY_BG)
        
        # Configure label styles
        style.configure('Modern.TLabel',
                       background=ModernUI.BG_COLOR,
                       foreground=ModernUI.TEXT_COLOR,
                       font=ModernUI.NORMAL_FONT)
        style.configure('Title.TLabel',
                       background=ModernUI.BG_COLOR,
                       foreground=ModernUI.TEXT_COLOR,
                       font=ModernUI.TITLE_FONT)
        style.configure('Subtitle.TLabel',
                       background=ModernUI.BG_COLOR,
                       foreground=ModernUI.TEXT_COLOR,
                       font=ModernUI.SUBTITLE_FONT)
        
        # Configure modern button styles with rounded corners
        style.configure('Modern.TButton',
                       background=ModernUI.ACCENT_COLOR,
                       foreground="#000000",  # Black text for lime green background
                       borderwidth=0,
                       focusthickness=0,
                       font=ModernUI.NORMAL_FONT,
                       padding=[20, 10])
        style.map('Modern.TButton',
                 background=[('active', ModernUI.HOVER_COLOR)],
                 foreground=[('active', "#000000")])  # Keep black text on hover
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       fieldbackground=ModernUI.INPUT_BG,
                       foreground=ModernUI.TEXT_COLOR,
                       bordercolor=ModernUI.BORDER_COLOR,
                       borderwidth=1,
                       font=ModernUI.NORMAL_FONT,
                       padding=[10, 8])
        
        # Configure notebook styles
        style.configure('Modern.TNotebook',
                       background=ModernUI.BG_COLOR,
                       borderwidth=0)
        style.configure('Modern.TNotebook.Tab',
                       background=ModernUI.SECONDARY_BG,
                       foreground=ModernUI.TEXT_COLOR,
                       padding=[15, 8],
                       font=ModernUI.NORMAL_FONT)
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', ModernUI.ACCENT_COLOR)],
                 foreground=[('selected', "#000000")])  # Black text for selected tabs
        
        # Configure progressbar
        style.configure('Modern.Horizontal.TProgressbar',
                       background=ModernUI.ACCENT_COLOR,
                       troughcolor=ModernUI.SECONDARY_BG,
                       borderwidth=0,
                       thickness=6)
        
        # Configure Treeview with modern styling
        style.configure('Modern.Treeview',
                       background=ModernUI.SECONDARY_BG,
                       foreground=ModernUI.TEXT_COLOR,
                       fieldbackground=ModernUI.SECONDARY_BG,
                       borderwidth=0,
                       font=ModernUI.NORMAL_FONT,
                       rowheight=50)
        style.configure('Modern.Treeview.Heading',
                       background=ModernUI.BG_COLOR,
                       foreground=ModernUI.TEXT_COLOR,
                       font=("Segoe UI", 12, "bold"))
        style.map('Modern.Treeview',
                 background=[('selected', ModernUI.ACCENT_COLOR)],
                 foreground=[('selected', "#000000")])  # Black text for selected items
        
        # Configure Labelframe with rounded corners
        style.configure('Modern.TLabelframe',
                       background=ModernUI.SECONDARY_BG,
                       foreground=ModernUI.TEXT_COLOR,
                       bordercolor=ModernUI.BORDER_COLOR,
                       font=ModernUI.NORMAL_FONT,
                       relief="solid",
                       borderwidth=1)
        style.configure('Modern.TLabelframe.Label',
                       background=ModernUI.SECONDARY_BG,
                       foreground=ModernUI.TEXT_COLOR,
                       font=("Segoe UI", 12, "bold"))

        # Add new button styles - all using lime green
        style.configure('Start.TButton', 
                       background=ModernUI.ACCENT_COLOR,
                       foreground="#000000")  # Black text
        style.map('Start.TButton',
                 background=[('active', ModernUI.HOVER_COLOR)],
                 foreground=[('active', "#000000")])
        
        style.configure('Stop.TButton', 
                       background=ModernUI.ACCENT_COLOR,
                       foreground="#000000")  # Black text
        style.map('Stop.TButton',
                 background=[('active', ModernUI.HOVER_COLOR)],
                 foreground=[('active', "#000000")])
        
        style.configure('Disabled.TButton', 
                       background=ModernUI.DISABLED_COLOR,
                       foreground=ModernUI.TEXT_COLOR)

class AmazonScraper:
    def __init__(self, callback_log=None, callback_update_progress=None, callback_add_result=None):
        self.is_running = False
        self.log = callback_log or (lambda x: None)
        self.update_progress = callback_update_progress or (lambda x, y: None)
        self.add_result = callback_add_result or (lambda x: None)
        self.processed_stores = set()
        self.driver = None
        self.stop_event = threading.Event()
        
        

        # Country-specific configuration
        self.country_config = {
    "Germany": {
        "domain": "https://www.amazon.de",
        "zip_placeholder": "e.g., 10115 for Berlin",
        "zip_regex": r"^\d{5}$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "10": "BE",  # Berlin
            "20": "HH",  # Hamburg
            "40": "NW",  # North Rhine-Westphalia
            "50": "NW",  # Cologne/Bonn
            "60": "HE",  # Frankfurt
            "70": "BW",  # Stuttgart
            "80": "BY"   # Munich
        }
    },
    "France": {
        "domain": "https://www.amazon.fr",
        "zip_placeholder": "e.g., 75001 for Paris",
        "zip_regex": r"^\d{5}$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "75": "IDF",  # Paris/Île-de-France
            "13": "PACA",  # Provence-Alpes-Côte d'Azur
            "69": "ARA",  # Auvergne-Rhône-Alpes
            "31": "OCC",  # Occitanie
            "59": "HDF",  # Hauts-de-France
            "33": "NAQ"   # Nouvelle-Aquitaine
        }
    },
    "Belgium": {
        "domain": "https://www.amazon.com.be",
        "zip_placeholder": "e.g., 1000 for Brussels",
        "zip_regex": r"^\d{4}$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "1000": "BRU",  # Brussels
            "2000": "VAN",  # Antwerp
            "3000": "VBR",  # Flemish Brabant
            "4000": "WLG",  # Liège
            "5000": "WNA",  # Namur
            "6000": "WHT",  # Hainaut
            "7000": "WHT",  # Hainaut (Charleroi)
            "8000": "VWV",  # West Flanders
            "9000": "OVL"   # East Flanders
        }
    },
    "Netherlands": {
        "domain": "https://www.amazon.nl",
        "zip_placeholder": "e.g., 1012 for Amsterdam",
        "zip_regex": r"^\d{4}$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "10": "NH",  # North Holland
            "30": "UT",  # Utrecht
            "50": "NB",  # North Brabant
            "80": "FR"   # Friesland
        }
    },
    # "Italy": {
    #     "domain": "https://www.amazon.it",
    #     "zip_placeholder": "e.g., 00100 for Rome",
    #     "zip_regex": r"^\d{5}$",
    #     "selectors": {
    #         "search_box": "twotabsearchtextbox",
    #         "location_popover": "nav-global-location-popover-link",
    #         "zip_input": "GLUXZipUpdateInput",
    #         "product": "div.s-result-item",
    #         "product_link": "a.a-link-normal.s-no-outline",
    #         "rating_count": "span.a-size-base.s-underline-text",
    #         "byline_info": "bylineInfo",
    #         "seller_profile": "sellerProfileTriggerId",
    #         "seller_info": "page-section-detail-seller-info"
    #     },
    #     "zip_to_region": {
    #         "00": "RM",  # Rome/Lazio
    #         "20": "MI",  # Milan/Lombardy
    #         "50": "FI",  # Florence/Tuscany
    #         "80": "NA",  # Naples/Campania
    #         "90": "PA",  # Palermo/Sicily
    #         "16": "GE"   # Genoa/Liguria
    #     }
    # },
    "Spain": {
        "domain": "https://www.amazon.es",
        "zip_placeholder": "e.g., 28001 for Madrid",
        "zip_regex": r"^\d{5}$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "28": "MD",  # Madrid
            "08": "CT",  # Catalonia
            "46": "VC",  # Valencia
            "41": "AN",  # Andalusia
            "48": "PV",  # Basque Country
            "50": "AR",  # Aragon
            "03": "VC"   # Alicante/Valencia
        }
    },
    "United Kingdom": {
        "domain": "https://www.amazon.co.uk",
        "zip_placeholder": "e.g., EC1A 1BB for London",
        "zip_regex": r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "EC": "LON",  # London
            "WC": "LON",  # London
            "M": "MAN",   # Manchester
            "B": "BIR",   # Birmingham
            "G": "GLA",   # Glasgow
            "EH": "EDH",  # Edinburgh
            "L": "LIV",   # Liverpool
            "LS": "LDS"   # Leeds
        }
    },
    "Sweden": {
        "domain": "https://www.amazon.se",
        "zip_placeholder": "e.g., 111 20 for Stockholm",
        "zip_regex": r"^\d{3}\s?\d{2}$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "111": "AB",  # Stockholm
            "113": "AB",  # Stockholm
            "211": "AB",  # Stockholm
            "411": "C",   # Gothenburg
            "581": "O",   # Linköping
            "222": "M",   # Malmö
            "751": "U",   # Uppsala
            "852": "S"   # Sundsvall
        }
    },
    "Poland": {
        "domain": "https://www.amazon.pl",
        "zip_placeholder": "e.g., 00-001 for Warsaw",
        "zip_regex": r"^\d{2}-\d{3}$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "00": "MZ",  # Masovian (Warsaw)
            "30": "MA",  # Lesser Poland (Kraków)
            "50": "DS",  # Lower Silesian (Wrocław)
            "80": "PM",  # Pomeranian (Gdańsk)
            "40": "SL",  # Silesian (Katowice)
            "90": "LD",  # Łódź
            "60": "WP",  # Greater Poland (Poznań)
            "70": "ZP"   # West Pomeranian (Szczecin)
        }
    },
    
    
    "USA": {
        "domain": "https://www.amazon.com",
        "zip_placeholder": "e.g., 10001 for New York",
        "zip_regex": r"^\d{5}(-\d{4})?$",
        "selectors": {
            "search_box": "twotabsearchtextbox",
            "location_popover": "nav-global-location-popover-link",
            "zip_input": "GLUXZipUpdateInput",
            "product": "div.s-result-item",
            "product_link": "a.a-link-normal.s-no-outline",
            "rating_count": "span.a-size-base.s-underline-text",
            "byline_info": "bylineInfo",
            "seller_profile": "sellerProfileTriggerId",
            "seller_info": "page-section-detail-seller-info"
        },
        "zip_to_region": {
            "100": "NY",  # New York
            "900": "CA",  # California
            "606": "IL",  # Illinois
            "770": "TX",  # Texas
            "331": "FL",  # Florida
            "191": "PA",  # Pennsylvania
            "981": "WA",  # Washington
            "850": "AZ"   # Arizona
        }
    }
}

    def close_cookie_banner(self):
        """Attempt to close any cookie consent banners"""
        try:
            # Try different selectors for cookie banners
            selectors = [
                ("#sp-cc-accept", By.CSS_SELECTOR),  # Amazon accept button
                ("#onetrust-accept-btn-handler", By.CSS_SELECTOR),  # OneTrust banner
                ("button[aria-label='Accept Cookies']", By.CSS_SELECTOR),
                ("button#truste-consent-button", By.CSS_SELECTOR),
                ("button.fc-cta-consent", By.CSS_SELECTOR),
                ("button.cookie-notice-close", By.CSS_SELECTOR),
                ("button.close-cookies", By.CSS_SELECTOR),
                ("button.cookie-close", By.CSS_SELECTOR),
            ]

            for selector, by in selectors:
                try:
                    accept_button = WebDriverWait(self.driver, 1).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    accept_button.click()
                    self.log("Closed cookie banner")
                    time.sleep(0.5)
                    return True
                except:
                    continue
            return False
        except Exception as e:
            self.log(f"Error closing cookie banner: {str(e)}")
            return False
    def get_region_from_zip(self, country, zip_code):
        """Get region code from ZIP code based on country-specific rules"""
        if not country or not zip_code:
            return None
            
        config = self.country_config.get(country, {})
        zip_to_region = config.get("zip_to_region", {})
        
        # Clean the ZIP code
        clean_zip = ''.join(filter(str.isalnum, str(zip_code))).upper()
        
        if country == "United Kingdom":
            # Extract postal district code (first alphabetical part)
            match = re.search(r"^([A-Z]{1,2})", clean_zip)
            if match:
                prefix = match.group(1)
                # Try 2-letter codes first
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
                # Then try 1-letter codes
                if prefix[0] in zip_to_region:
                    return zip_to_region[prefix[0]]
        
        elif country == "Poland":
            # Extract first 2 digits before dash
            if '-' in clean_zip:
                prefix = clean_zip.split('-')[0]
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
            elif len(clean_zip) >= 2:
                prefix = clean_zip[:2]
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
                    
        elif country == "Sweden":
            # Take first 3 digits
            if len(clean_zip) >= 3:
                prefix = clean_zip[:3]
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
                    
        elif country == "Netherlands":
            # Take first 2 digits
            if len(clean_zip) >= 2:
                prefix = clean_zip[:2]
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
                    
        elif country == "Italy":
            # Take first 2 digits
            if len(clean_zip) >= 2:
                prefix = clean_zip[:2]
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
                    
        elif country == "Spain":
            # Take first 2 digits
            if len(clean_zip) >= 2:
                prefix = clean_zip[:2]
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
                    
        elif country == "Austria":
            # Take first 2 digits
            if len(clean_zip) >= 2:
                prefix = clean_zip[:2]
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
                    
        elif country == "Switzerland":
            # Take first 2 digits
            if len(clean_zip) >= 2:
                prefix = clean_zip[:2]
                if prefix in zip_to_region:
                    return zip_to_region[prefix]
                    
        else:
            if country in ["USA", "Germany"]:
                # For USA/Germany: Match first digits
                for prefix, region in zip_to_region.items():
                    if zip_code.startswith(prefix):
                        return region
            elif country in ["Belgium", "France"]:
                # For Belgium/France: Exact match
                return zip_to_region.get(zip_code[:len(next(iter(zip_to_region.keys())))])
            
        return None

    def init_driver(self):
        """Initialize Chrome WebDriver with optimized settings"""
        if self.driver:
            return True
            
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        options.add_argument("--mute-audio")
        options.add_argument("--disable-infobars")

        prefs = {
            "profile.default_content_setting_values.images": 2,
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.automatic_downloads": 2,
            "profile.default_content_setting_values.media_stream": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
        }
        options.add_experimental_option("prefs", prefs)

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            self.driver.implicitly_wait(0.1)
            return True
        except Exception as e:
            self.log(f"Error initializing WebDriver: {str(e)}")
            return False

    def is_page_loaded(self):
        """Check if the page is fully loaded"""
        return self.driver.execute_script("return document.readyState") == "complete"

    def handle_captcha(self, captcha_url):
        """Show captcha in UI and get user solution"""
        self.captcha_solution = None
        self.captcha_event = threading.Event()
        
        # Notify UI to show captcha
        if self.captcha_callback:
            self.captcha_callback(captcha_url)
        
        # Wait for user input (timeout after 5 minutes)
        self.captcha_event.wait(300)
        return self.captcha_solution


    def set_location(self, domain, zip_code, country):
        """Set the location for the Amazon store using country-specific selectors"""
        try:
            if not self.init_driver():
                return False
                
            config = self.country_config.get(country, {})
            selectors = config.get("selectors", {})
            
            self.driver.get(domain)
            
            # Handle captcha if present
            try:
                captcha_image = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='captcha']"))
                )
                if captcha_image:
                    captcha_url = captcha_image.get_attribute("src")
                    self.log(f"Captcha detected: {captcha_url}")
                    
                    # Solve captcha through UI
                    solution = self.handle_captcha(captcha_url)
                    if not solution:
                        self.log("Captcha not solved, skipping location set")
                        return False
                    
                    # Enter captcha solution
                    captcha_input = self.driver.find_element(By.ID, "captchacharacters")
                    captcha_input.send_keys(solution)
                    
                    # Submit captcha
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    submit_button.click()
                    time.sleep(2)
            except (NoSuchElementException, TimeoutException):
                self.log("No captcha detected")
            
            # Set location - updated selectors and flow
            try:
                # Click the location popover
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, selectors["location_popover"]))
                ).click()
                
                # Switch to the location modal
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "GLUXZipUpdate"))
                )
                
                # Enter ZIP code
                zip_input = self.driver.find_element(By.ID, selectors["zip_input"])
                zip_input.clear()
                zip_input.send_keys(zip_code)
                
                # Click apply button
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "GLUXZipUpdate"))
                ).click()
                
                # Wait for location to update
                time.sleep(3)
                self.log(f"Location set to {zip_code}")
                return True
                
            except (NoSuchElementException, TimeoutException) as e:
                self.log(f"Error setting location: {str(e)}")
                # Try alternative method if first fails
                try:
                    self.driver.get(f"{domain}?location={zip_code}")
                    time.sleep(2)
                    self.log(f"Used alternative method to set location to {zip_code}")
                    return True
                except:
                    return False

        except Exception as e:
            self.log(f"Error in set_location: {str(e)}")
            return False
    def open_new_tab(self, keyword):
        """Open a new tab and search for the keyword"""
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.search_keyword(keyword)

    def search_keyword(self, keyword):
        """Search for a keyword on Amazon"""
        retries = 5
        for attempt in range(retries):
            try:
                self.driver.get(self.country_config[self.current_country]['domain'])
                search_box = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
                )
                search_box.clear()
                search_box.send_keys(keyword)
                search_box.send_keys(Keys.RETURN)
                time.sleep(1)
                self.log(f"Searched for keyword: {keyword}")
                return
            except (NoSuchElementException, TimeoutException):
                self.log(f"Attempt {attempt + 1}/{retries} failed. Reloading page...")
                self.driver.refresh()
                time.sleep(1)
        
        self.log("Error: Unable to find the search box after multiple attempts.")

    def scrape_product_links(self, max_pages=2, max_rating_count=300):
        """Scrape product links from search results"""
        product_links = []
        rating_counts = []
        current_page = 1

        while True:
            if self.stop_event.is_set():
                self.log("Stopping scraping.")
                break

            try:
                if not self.is_page_loaded():
                    self.log("Page not fully loaded yet.")
                    continue

                # Wait for product elements
                product_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, ".s-main-slot .s-result-item")
                    )
                )
                self.log(f"Scraping Page: {current_page}")

                for product_element in product_elements:
                    if self.stop_event.is_set():
                        self.log("Stopping scraping.")
                        break

                    try:
                        # Get product link
                        product_link = product_element.find_element(
                            By.CSS_SELECTOR, "a.a-link-normal.s-no-outline"
                        ).get_attribute("href")
                        
                        # Get rating count if available - with improved parsing
                        try:
                            rating_count_element = product_element.find_element(
                                By.CSS_SELECTOR, "span.a-size-base.s-underline-text"
                            )
                            rating_count_text = rating_count_element.text if rating_count_element else ""
                            
                            # Clean and convert the rating count text to integer
                            if rating_count_text:
                                # Remove commas, dots, and any non-numeric characters except digits
                                cleaned_text = ''.join(c for c in rating_count_text if c.isdigit())
                                rating_count = int(cleaned_text) if cleaned_text else 0
                            else:
                                rating_count = 0
                            
                            if rating_count < int(max_rating_count):
                                rating_counts.append(rating_count)
                                product_links.append(product_link)
                                self.log(f"Link found: {len(product_links)} - {rating_count} ratings")
                        except NoSuchElementException:
                            rating_counts.append(0)
                            product_links.append(product_link)
                            self.log(f"Link found (no rating): {len(product_links)}")
                            
                    except NoSuchElementException:
                        self.log("Error extracting product data")

                # Navigate to next page if available
                if max_pages == "max" or current_page < int(max_pages):
                    try:
                        # Close any cookie banners first
                        self.close_cookie_banner()
                        
                        next_page_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, "a.s-pagination-item.s-pagination-next")
                            )
                        )
                        
                        # Scroll to the button and click using JavaScript
                        self.driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
                        self.driver.execute_script("arguments[0].click();", next_page_button)
                        
                        current_page += 1
                        time.sleep(2)  # Wait for page to load
                    except (NoSuchElementException, TimeoutException):
                        self.log("No more pages available.")
                        break
                    except Exception as e:
                        self.log(f"Error navigating to next page: {str(e)}")
                        break
                else:
                    break

            except Exception as e:
                self.log(f"Error scraping product links: {str(e)}")
                break

        return product_links, rating_counts

    def scrape_store_info(self, product_link, rating, index):
        # Initialize variables for both US and non-US flows
        brand_name = "N/A"
        store_name = "N/A"
        phone_number = "N/A"
        store_rating = f"{rating}"
        email = "N/A"
        business_address = "N/A"
        region = self.get_region_from_zip(self.current_country, self.current_zip)

        try:
            self.driver.get(product_link)
            WebDriverWait(self.driver, 10).until(lambda d: self.is_page_loaded())

            # IMPROVED BRAND NAME EXTRACTION
            brand_name = "N/A"
            try:
                # 1. Try bylineInfo
                byline_elem = self.driver.find_element(By.ID, "bylineInfo")
                byline_text = byline_elem.text.strip()
                # Filter out generic Amazon text
                if byline_text and not byline_text.lower().startswith("visit the amazon store"):
                    brand_name = byline_text
            except Exception:
                pass
            # 2. Try product details table for 'Brand'
            if brand_name == "N/A" or not brand_name or brand_name.lower().startswith("visit the amazon store"):
                try:
                    # Try both possible tables
                    tables = self.driver.find_elements(By.XPATH, "//table[contains(@id, 'productDetails') or contains(@class, 'prodDetTable')]")
                    for table in tables:
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        for row in rows:
                            ths = row.find_elements(By.TAG_NAME, "th")
                            tds = row.find_elements(By.TAG_NAME, "td")
                            if ths and tds and 'brand' in ths[0].text.strip().lower():
                                brand_candidate = tds[0].text.strip()
                                if brand_candidate:
                                    brand_name = brand_candidate
                                    break
                        if brand_name != "N/A":
                            break
                except Exception:
                    pass
            # 3. Fallback: Try parsing from product title
            if brand_name == "N/A" or not brand_name or brand_name.lower().startswith("visit the amazon store"):
                try:
                    title_elem = self.driver.find_element(By.ID, "productTitle")
                    title_text = title_elem.text.strip()
                    if title_text:
                        # Heuristic: take first word if it's capitalized and not a generic word
                        first_word = title_text.split()[0]
                        if first_word and first_word[0].isupper() and first_word.lower() not in ["amazon", "the"]:
                            brand_name = first_word
                except Exception:
                    pass
            # END IMPROVED BRAND NAME EXTRACTION

            if brand_name in self.processed_stores:
                self.log(f"Already Processed: {brand_name}")
                # Update statistics for skipped items
                try:
                    if hasattr(self, 'update_progress') and callable(self.update_progress):
                        self.update_progress(0, f"Skipped: {brand_name}")
                except:
                    pass
                return None

            self.processed_stores.add(brand_name)
            self.log(f"{index}: {brand_name}")
            
            # Update statistics for processed items
            try:
                if hasattr(self, 'update_progress') and callable(self.update_progress):
                    self.update_progress(50, f"Processing: {brand_name}")
            except:
                pass

            # US-SPECIFIC LOGIC
            if self.current_country == "USA":
                # Use the US-specific scraping method
                return self.scrape_store_info_us(product_link, rating, index, brand_name)
                
            # NON-US LOGIC (Original flow for other countries)
            page_source = self.driver.page_source
            if "sellerProfileTriggerId" in page_source:
                try:
                    seller_profile_link = self.driver.find_element(
                        By.ID, "sellerProfileTriggerId"
                    )
                    
                    if "amazon" in seller_profile_link.text.lower():
                        self.log(f"Seller is Amazon, skipping {brand_name}")
                        return (brand_name, store_name, phone_number, store_rating, email, business_address, region)

                    
                    self.driver.execute_script("arguments[0].click();", seller_profile_link)
                    WebDriverWait(self.driver, 5).until(lambda d: self.is_page_loaded())

                except (NoSuchElementException, TimeoutException) as e:
                    self.log(f"Error clicking seller profile: {str(e)}")
                    return (brand_name, store_name, phone_number, store_rating, email, business_address, region)

            else:
                self.log(f"No seller profile found for {brand_name}")
                return (brand_name, store_name, phone_number, store_rating, email, business_address, region)


            # COMMON: Seller details extraction
            try:
                seller_info = self.driver.find_element(
                By.ID, "page-section-detail-seller-info"
                )
                seller_details = self.get_seller_details(seller_info)
                
                # Map extracted details
                store_name = seller_details.get("business_name", "N/A")
                phone_number = seller_details.get("phone_number", "N/A")
                email = seller_details.get("email", "N/A")
                business_address = seller_details.get("business_address", "N/A")
                # Get business address and region
                business_address, region = self.get_business_address(seller_info, region)
                
                # If region not found in address, use ZIP-based region
                if region == "N/A":
                    region = self.get_region_from_zip(self.current_country, self.current_zip)
            except NoSuchElementException:
                self.log(f"Seller details not found for {brand_name}")

            return (brand_name, store_name, phone_number, store_rating, email, business_address, region)


        except (NoSuchElementException, TimeoutException) as e:
            self.log(f"Error scraping store info: {str(e)}")
            return (brand_name, store_name, phone_number, store_rating, email, business_address, region)


    def scrape_store_info_us(self, product_link, rating, index, brand_name):
        store_name = brand_name  # For US, brand name is often the store name
        phone_number = "N/A"
        store_rating = f"{rating}"
        email = "N/A"
        business_address = "N/A"
        
        region = self.get_region_from_zip(self.current_country, self.current_zip)

        try:
            # US-SPECIFIC: Check for seller profile
            page_source = self.driver.page_source
            if "sellerProfileTriggerId" in page_source:
                try:
                    seller_profile_link = self.driver.find_element(
                        By.ID, "sellerProfileTriggerId"
                    )
                    
                    # Scroll into view and click
                    self.driver.execute_script("arguments[0].scrollIntoView();", seller_profile_link)
                    self.driver.execute_script("arguments[0].click();", seller_profile_link)
                    WebDriverWait(self.driver, 5).until(lambda d: self.is_page_loaded())

                    # US-SPECIFIC: Extract seller info using consistent method
                    try:
                        seller_info = self.driver.find_element(
                By.ID, "page-section-detail-seller-info"
                        )
                        seller_details = self.get_seller_details(seller_info)
                        
                        # Map extracted details
                        store_name = seller_details.get("business_name", "N/A")
                        phone_number = seller_details.get("phone_number", "N/A")
                        email = seller_details.get("email", "N/A")
                        business_address = seller_details.get("business_address", "N/A")
                                    
                        # Get business address and region
                        business_address, region = self.get_business_address(seller_info, region)
                        
                        # If region not found in address, use ZIP-based region
                        if region == "N/A":
                            region = self.get_region_from_zip(self.current_country, self.current_zip)

                    except (NoSuchElementException, TimeoutException):
                        self.log(f"Seller details not found for {brand_name}")

                    # US-SPECIFIC: Extract additional contact details
                    additional_phone, additional_email = self.extract_about_seller()
                    
                    # Combine phone numbers
                    if phone_number == "N/A":
                        phone_number = additional_phone
                    elif additional_phone != "N/A":
                        phone_number = f"{phone_number}, {additional_phone}".strip(", ")
                    
                    # Combine emails
                    if email == "N/A":
                        email = additional_email
                    elif additional_email != "N/A":
                        email = f"{email}, {additional_email}".strip(", ")
                    
                    # Format phone numbers
                    phone_number = self.format_all_phone_numbers(phone_number.split(", "))
                    email = self.fix_email_duplicates(email)
                    
                    return (brand_name, store_name, phone_number, store_rating, email, business_address, region)

                except (NoSuchElementException, TimeoutException) as e:
                    self.log(f"Error interacting with seller profile: {str(e)}")
            else:
                self.log(f"No seller profile found for {brand_name}")

        except Exception as e:
            self.log(f"Error in US-specific scraping: {str(e)}")
        
        # If we get here, try to fall back to ZIP-based region
        if region == "N/A":
            region = self.get_region_from_zip(self.current_country, self.current_zip)
        
        return (brand_name, store_name, phone_number, store_rating, email, business_address, region)

    # ADDITIONAL HELPER METHODS FOR US SCRAPING
    def extract_about_seller(self):
        """US-specific: Extract contact info from 'About Seller' section"""
        try:
            about_seller_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".spp-expander.about-seller")
                )
            )
            
            # Handle "See more" button if present
            try:
                see_more_button = self.driver.find_element(
                    By.CSS_SELECTOR, ".spp-expander-header.a-link-expander"
                )
                hidden_content = self.driver.find_element(
                    By.CSS_SELECTOR, ".spp-expander-more-content.hide-content"
                )
                if see_more_button and hidden_content:
                    see_more_button.click()
                    WebDriverWait(self.driver, 5).until(
                        EC.invisibility_of_element_located(
                            (By.CSS_SELECTOR, ".spp-expander-more-content.hide-content")
                        )
                    )
            except NoSuchElementException:
                pass

            # Extract text and find contact info
            section_text = about_seller_element.text.strip()
            email_matches = re.findall(r"[\w\.-]+@[\w\.-]+", section_text)
            email = ", ".join(email_matches) if email_matches else "N/A"
            
            phone_matches = re.findall(
                r"\+?\d{1,4}?[\s-]?\(?\d{1,4}?\)?[\s-]?\d{1,4}[\s-]?\d{1,4}[\s-]?\d{1,4}",
                section_text,
            )
            phone_number = ", ".join([match for match in phone_matches if match]) if phone_matches else "N/A"

            return phone_number, email

        except (TimeoutException, NoSuchElementException):
            return "N/A", "N/A"

    def format_all_phone_numbers(self, phone_numbers):
        """Format list of phone numbers to international format"""
        formatted_numbers = []
        for number in phone_numbers:
            if number.strip():  # Skip empty strings
                formatted = self.format_phone_number_with_country_code(number)
                if formatted != "N/A":
                    formatted_numbers.append(formatted)
        
        return ", ".join(formatted_numbers) if formatted_numbers else "N/A"

    def fix_email_duplicates(self, email_text):
        """Remove duplicate emails from a comma-separated string"""
        if email_text == "N/A":
            return "N/A"
        
        emails = [self.normalize_email(e) for e in email_text.split(", ")]
        unique_emails = list(set(emails))
        return ", ".join(unique_emails)

    def normalize_email(self, email):
        """Clean and standardize email format"""
        return email.strip().lower()

    def normalize_phone_number(self, phone_number):
        """Remove non-numeric characters from phone number"""
        return "".join(c for c in phone_number if c.isdigit() or c == "+")

    def format_phone_number_with_country_code(self, phone_number):
        """Convert phone number to E.164 format"""
        normalized = self.normalize_phone_number(phone_number)
        if not normalized:
            return "N/A"
        
        try:
            # Handle US numbers specifically
            if normalized.startswith("+") or normalized.startswith("1"):
                parsed = phonenumbers.parse(normalized, "US")
            else:
                # For international numbers
                parsed = phonenumbers.parse(normalized, None)
                
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except:
            return "N/A"
    
    def get_seller_details(self, seller_info):
        """Extract all seller details using universal structural patterns"""
        details = {
            "business_name": "N/A",
            "phone_number": "N/A",
            "email": "N/A",
            "business_address": "N/A",
            "region": "N/A"
        }
        
        try:
            # Find all information rows
            rows = seller_info.find_elements(By.XPATH, ".//div[contains(@class, 'a-row') and contains(@class, 'a-spacing-none')]")
            
            # Track when we find the address section
            in_address_section = False
            address_lines = []
            
            for row in rows:
                try:
                    # Get all spans in this row
                    spans = row.find_elements(By.XPATH, ".//span")
                    if not spans:
                        continue
                        
                    # Get text of all spans
                    texts = [span.text.strip() for span in spans]
                    full_text = " ".join(texts).lower()
                    
                    # BUSINESS NAME: Enhanced detection with label-value pattern
                    label = texts[0].lower() if texts else ""
                    value = texts[-1]
                    
                    # Handle different label formats for business name
                    if "business name" in label or "business name:" in full_text:
                        details["business_name"] = value
                    elif "nom commercial" in label or "nom commercial:" in full_text:  # Belgium French
                        details["business_name"] = value
                    elif "nome dell'azienda" in label or "ragione sociale" in label:  # Italian
                        details["business_name"] = value
                    elif "raison sociale" in label:  # French
                        details["business_name"] = value
                    # Fallback to full text matching
                    elif any(kw in full_text for kw in ["business name", "nazwa firmy", "företagsnamn", 
                                                        "bedrijfsnaam", "företag", "firma", "firmenname"]):
                        details["business_name"] = value
                    
                    # PHONE: Existing patterns work well
                    elif any(kw in full_text for kw in ["phone", "telefon", "telefoon", "nummer", "téléphone", "tel"]):
                        details["phone_number"] = value
                    
                    # EMAIL: Existing patterns work well
                    elif any(kw in full_text for kw in ["email", "e-mail", "e-post", "mail"]):
                        details["email"] = value
                    
                    # ADDRESS: Start of address section
                    elif any(kw in full_text for kw in ["address", "adres", "adresse", "dirección"]):
                        in_address_section = True
                        address_lines = []
                    
                    # Address continuation lines
                    elif "indent-left" in row.get_attribute("class") and in_address_section:
                        address_lines.append(texts[0])
                    
                    # End of address section
                    elif in_address_section and not row.get_attribute("class"):
                        in_address_section = False
                
                except Exception as e:
                    self.log(f"Error processing row: {str(e)}")
                    continue
            
            # Process collected address
            if address_lines:
                details["business_address"] = ", ".join(address_lines)
                
                # Extract region from last line
                last_line = address_lines[-1].upper()
                if len(last_line) == 2 and last_line.isalpha():
                    details["region"] = last_line
                else:
                    country_map = {
                        "POLAND": "PL", "SPAIN": "ES", "SWEDEN": "SE",
                        "NETHERLANDS": "NL", "ITALY": "IT", "FRANCE": "FR",
                        "GERMANY": "DE", "BELGIUM": "BE", "AUSTRIA": "AT",
                        "UNITED KINGDOM": "GB", "UK": "GB", "GB": "GB",
                        "BELGIQUE": "BE", "BELGIE": "BE",  # Belgium
                        "ITALIE": "IT", "ITALIA": "IT",    # Italy
                        "FRANKREICH": "FR", "FRANCE": "FR" # France
                    }
                    for name, code in country_map.items():
                        if name in last_line:
                            details["region"] = code
                            break
            
            return details
            
        except Exception as e:
            self.log(f"Error extracting seller details: {str(e)}")
            return details
    
    def get_business_address(self, seller_info, region):
        """Extract business address and country code (used as region)"""
        try:
            address_elements = seller_info.find_elements(
                By.XPATH, ".//div[contains(@class, 'indent-left')]"
            )
            full_address = ", ".join([elem.text.strip() for elem in address_elements])
            
            # Default values
            region =region
            
            if full_address:
                # Split address and look for country code at the end
                parts = [p.strip() for p in full_address.split(',')]
                if parts:
                    last_part = parts[-1].strip().upper()
                    # Check if it's a valid 2-letter country code
                    if len(last_part) == 2 and last_part.isalpha():
                        region = last_part  # Use country code as region
            
            return full_address, region
            
        except Exception as e:
            self.log(f"Error getting address: {str(e)}")
            return "N/A", region

    def normalize_text(self, text):
        """Normalize text to remove unsupported characters and clean brand names"""
        if text is None:
            return "N/A"
        try:
            normalized = (
                unicodedata.normalize("NFKD", str(text))
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
            
            # Clean brand names - remove "Visit the" and "Store" prefixes
            if normalized and isinstance(normalized, str):
                normalized = normalized.strip()
                if normalized.lower().startswith('visit the '):
                    normalized = normalized[len('visit the '):]
                if normalized.lower().endswith(' store'):
                    normalized = normalized[:-len(' store')]
                normalized = normalized.strip()
            
            return normalized
        except Exception as e:
            self.log(f"Error normalizing text: {str(e)}")
            return "Invalid Data"

    def save_to_csv(self, data, filename):
        """Save scraped data to CSV file"""
        try:
            file_exists = os.path.isfile(filename)
            
            with open(filename, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                
                if not file_exists:
                    writer.writerow([
                        "Brand Name", "Store Name", "Product Link", 
                        "Phone Number", "Whatsapp", "Email", "Rating", 
                        "Keyword", "Rating Filter", "Zip Code", "Business Address", "Region"
                    ])

                existing_stores = set()
                if file_exists:
                    with open(filename, mode="r", encoding="utf-8") as read_file:
                        reader = csv.reader(read_file)
                        next(reader, None)  # Skip header
                        for row in reader:
                            if row:
                                existing_stores.add(row[1])  # Store names are in column 1

                for record in data:
                    try:
                        (
                            brand_name,
                            store_name,
                            product_link,
                            phone_number,
                            email,
                            store_rating,
                            keyword,
                            rating_count_entry,
                            zipcode,
                            business_address,
                            region,
                        ) = record

                        # Skip if essential fields are missing
                        if store_name == "N/A" and phone_number == "N/A" and email == "N/A":
                            continue

                        # Normalize data
                        sanitized_data = [
                            self.normalize_text(brand_name),
                            self.normalize_text(store_name),
                            self.normalize_text(product_link),
                            self.normalize_text(phone_number),
                            self.normalize_text(email),
                            self.normalize_text(store_rating),
                            self.normalize_text(keyword),
                            self.normalize_text(rating_count_entry),
                            self.normalize_text(zipcode),
                            str(self.normalize_text(business_address)),
                            self.normalize_text(region)
                        ]

                        # Avoid duplicates
                        if sanitized_data[1] not in existing_stores:
                            whatsapp_links = ", ".join([
                                f"https://wa.me/{num.replace(' ', '').replace('-', '')}"
                                for num in sanitized_data[3].split(", ")
                            ])
                            sanitized_data.insert(4, whatsapp_links)
                            writer.writerow(sanitized_data)
                            existing_stores.add(sanitized_data[1])

                    except Exception as e:
                        self.log(f"Error processing record: {str(e)}")

            self.log(f"Data saved to {filename}")
            return True
            
        except Exception as e:
            self.log(f"Error saving to CSV: {str(e)}")
            return False

    def start_scraping(self, keywords, country, max_pages, min_rating_count, zip_code):
        """Start the scraping process"""
        self.is_running = True
        self.stop_event.clear()
        self.processed_stores.clear()
        self.current_country = country
        # Store current ZIP for region lookup
        self.current_zip = zip_code 
        try:
            if not self.init_driver():
                self.log("Failed to initialize browser")
                return False
                
            domain = self.country_config[country]['domain']
            self.log(f"Starting scraping for country: {country} ({domain})")
            
            # Set location if zip code provided
            if zip_code:
                if not self.set_location(domain, zip_code, country):
                    self.log("Failed to set location")
                    return False

            total_keywords = len(keywords)
            all_data = []
            
            for keyword_idx, keyword in enumerate(keywords):
                if self.stop_event.is_set():
                    break
                    
                keyword = keyword.strip()
                if not keyword:
                    continue
                    
                # Update progress
                self.update_progress(
                    (keyword_idx / total_keywords) * 100,
                    f"Processing keyword {keyword_idx + 1}/{total_keywords}: {keyword}"
                )
                
                # Search for keyword
                if keyword_idx == 0:
                    self.open_new_tab(keyword)
                else:
                    self.search_keyword(keyword)
                
                # Scrape product links
                product_links, rating_counts = self.scrape_product_links(
                    max_pages=max_pages,
                    max_rating_count=min_rating_count
                )
                
                # Scrape store info for each product
                total_links = len(product_links)
                keyword_data = []
                
                for idx, product_link in enumerate(product_links):
                    if self.stop_event.is_set():
                        break
                        
                    # Update progress
                    self.update_progress(
                        ((keyword_idx + (idx / total_links)) / total_keywords) * 100,
                        f"Processing product {idx + 1}/{total_links} for {keyword}"
                    )
                    
                    # Scrape store info - may return None if duplicate
                    info = self.scrape_store_info(product_link, rating_counts[idx], idx + 1)
                    if not info:
                        continue
                    (
                        brand_name,
                        store_name,
                        phone_number,
                        store_rating,
                        email,
                        business_address,
                        region
                    ) = info
                    # Skip entries lacking essential data
                    if store_name == "N/A" and phone_number == "N/A" and email == "N/A":
                        continue
                    # Add to results with region
                    result = {
                        "Brand": brand_name,
                        "Store Name": store_name,
                        "Phone": phone_number,
                        "Email": email,
                        "Rating": store_rating,
                        "Address": business_address,
                        "Region": region,
                        "Product Link": product_link,
                        "Keyword": keyword,
                    }
                    keyword_data.append(result)
                    self.add_result(result)
                    
                all_data.extend(keyword_data)
                
                # Save intermediate results
                if keyword_data:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"amazon_results_{country}_{timestamp}.csv"
                    self.save_to_csv([
                        (
                            item["Brand"], item["Store Name"], item["Product Link"],
                            item["Phone"], item["Email"], item["Rating"],
                            item["Keyword"], min_rating_count, zip_code,
                            item["Address"], item["Region"]
                        )
                        for item in keyword_data
                    ], filename)
                    
            self.log("Scraping completed successfully.")
            return True
            
        except Exception as e:
            self.log(f"Error during scraping: {str(e)}")
            return False
            
        finally:
            self.is_running = False
            self.update_progress(0, "Ready")

    def stop_scraping(self):
        """Stop the scraping process"""
        self.log("Stopping scraping...")
        self.stop_event.set()
        self.is_running = False
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass

    def update_progress(self, value):
        # This method is no longer used - progress is handled by ProgressWindow
        pass

    def _update_progress(self, value):
        # This method is no longer used - progress is handled by ProgressWindow
        pass

class ProgressWindow:
    """Separate window to show scraping progress and details"""
    def __init__(self, app, scraper_type):
        # Keep a reference to the main app (for webhook updates)
        self.app = app
        
        # Create window using app root
        self.window = tk.Toplevel(app.root)
        self.window.title(f"{scraper_type} Progress")
        
        # Make it full screen for better visibility
        self.window.state('zoomed')  # Windows full screen
        self.window.configure(bg=ModernUI.BG_COLOR)
        self.window.resizable(True, True)
        
        # Make it modal but allow interaction with main window
        self.window.transient(app.root)
        self.window.grab_set()
        
        # Set minimum size for better usability
        self.window.minsize(1000, 700)
        
        # Flag to track if window is still active
        self.is_active = True
        
        # Map scraper type to short code
        scraper_type_map = {
            "Google Maps Scraper": "G",
            "Email Scraper": "M",
            "Amazon Scraper": "A",
            "AU Scraper": "AU"
        }
        self.scraper_type = scraper_type_map.get(scraper_type, scraper_type)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.window, style='Modern.TFrame', padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text=f"{self.scraper_type} Progress", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Close button
        close_btn = ttk.Button(header_frame, text="✕", command=self.window.destroy,
                              style='Modern.TButton', width=5)
        close_btn.pack(side='right')
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", 
                                      padding=20, style='Modern.TLabelframe')
        progress_frame.pack(fill='x', pady=(0, 20))
        
        # Overall progress
        self.overall_progress_var = tk.DoubleVar(value=0)
        self.overall_progress_bar = ttk.Progressbar(progress_frame, 
                                                   variable=self.overall_progress_var,
                                                   style='Modern.Horizontal.TProgressbar',
                                                   length=700)
        self.overall_progress_bar.pack(fill='x', pady=(0, 10))
        
        self.overall_progress_label = ttk.Label(progress_frame, 
                                              text="Initializing...", 
                                              style='Modern.TLabel')
        self.overall_progress_label.pack()
        
        # Current task progress
        task_frame = ttk.Frame(progress_frame, style='Modern.TFrame')
        task_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Label(task_frame, text="Current Task:", style='Modern.TLabel').pack(anchor='w')
        
        self.task_progress_var = tk.DoubleVar(value=0)
        self.task_progress_bar = ttk.Progressbar(task_frame, 
                                               variable=self.task_progress_var,
                                               style='Modern.Horizontal.TProgressbar',
                                               length=700)
        self.task_progress_bar.pack(fill='x', pady=(5, 10))
        
        self.task_progress_label = ttk.Label(task_frame, 
                                           text="Ready", 
                                           style='Modern.TLabel')
        self.task_progress_label.pack()
        
        # Statistics section
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", 
                                   padding=20, style='Modern.TLabelframe')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Create grid for stats
        stats_grid = ttk.Frame(stats_frame, style='Modern.TFrame')
        stats_grid.pack(fill='x')
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        stats_grid.grid_columnconfigure(2, weight=1)
        stats_grid.grid_columnconfigure(3, weight=1)
        
        # Stats labels
        self.stats_labels = {}
        stats_data = [
            ("Total Processed", "0"),
            ("Success", "0"),
            ("Failed", "0"),
            ("Remaining", "0")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            ttk.Label(stats_grid, text=label, style='Modern.TLabel').grid(row=0, column=i, pady=5)
            self.stats_labels[label] = ttk.Label(stats_grid, text=value, 
                                               style='Title.TLabel', 
                                               foreground=ModernUI.ACCENT_COLOR)
            self.stats_labels[label].grid(row=1, column=i, pady=5)
        
        # Details section
        details_frame = ttk.LabelFrame(main_frame, text="Details", 
                                     padding=20, style='Modern.TLabelframe')
        details_frame.pack(fill='both', expand=True)
        
        # Create notebook for different detail views
        self.details_notebook = ttk.Notebook(details_frame, style='Modern.TNotebook')
        self.details_notebook.pack(fill='both', expand=True)
        
        # Log tab
        log_frame = ttk.Frame(self.details_notebook, style='Modern.TFrame', padding=10)
        self.details_notebook.add(log_frame, text="Log")
        
        self.log_text = tk.Text(log_frame, font=("Consolas", 10),
                               bg=ModernUI.SECONDARY_BG, fg=ModernUI.TEXT_COLOR,
                               relief="solid", borderwidth=1,
                               insertbackground=ModernUI.TEXT_COLOR)
        self.log_text.pack(side='left', fill='both', expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        log_scrollbar.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Results preview tab removed - keeping only log for cleaner interface
        
    def update_overall_progress(self, value, text):
        """Update overall progress bar and label"""
        if not self.is_active:
            return
            
        def _update_overall():
            try:
                if hasattr(self, 'window') and self.window.winfo_exists() and self.is_active:
                    self.overall_progress_var.set(value)
                    self.overall_progress_label.config(text=text)
            except:
                pass  # Window was destroyed
        
        # Ensure we're in the main thread
        if threading.current_thread() is threading.main_thread():
            _update_overall()
        else:
            try:
                if hasattr(self, 'window') and self.window.winfo_exists() and self.is_active:
                    self.window.after(0, _update_overall)
            except:
                pass  # Window was destroyed
        
    def update_task_progress(self, value, text):
        """Update current task progress bar and label"""
        if not self.is_active:
            return
            
        def _update_task():
            try:
                if hasattr(self, 'window') and self.window.winfo_exists() and self.is_active:
                    self.task_progress_var.set(value)
                    self.task_progress_label.config(text=text)
            except:
                pass  # Window was destroyed
        
        # Ensure we're in the main thread
        if threading.current_thread() is threading.main_thread():
            _update_task()
        else:
            try:
                if hasattr(self, 'window') and self.window.winfo_exists() and self.is_active:
                    self.window.after(0, _update_task)
            except:
                pass  # Window was destroyed
        
    def update_stats(self, stats_dict):
        """Update statistics display"""
        if not self.is_active:
            return
            
        def _update_stats():
            try:
                if hasattr(self, 'window') and self.window.winfo_exists() and self.is_active:
                    for label, value in stats_dict.items():
                        if label in self.stats_labels:
                            self.stats_labels[label].config(text=str(value))
                    
                    # Send custom webhook update with stats and latest results sample if available
                    if hasattr(self, 'scraper_type') and hasattr(self, 'app'):
                        sample_data = None
                        try:
                            if self.scraper_type == 'G' and hasattr(self.app, 'names_list'):
                                sample_data = [
                                    f"{self.app.names_list[-1]} - {self.app.address_list[-1]}"
                                ] if self.app.names_list and self.app.address_list else None
                            elif self.scraper_type == 'M' and hasattr(self.app, 'email_list'):
                                sample_data = [self.app.email_list[-1]] if self.app.email_list else None
                            elif self.scraper_type == 'A' and hasattr(self.app, 'a_scraped_results'):
                                if self.app.a_scraped_results:
                                    last = self.app.a_scraped_results[-1]
                                    sample_data = [f"{last.get('Brand','N/A')} - {last.get('Website','N/A')}"]
                            elif self.scraper_type == 'AU' and hasattr(self.app, 'au_results_tree'):
                                items = self.app.au_results_tree.get_children()
                                if items:
                                    vals = self.app.au_results_tree.item(items[-1], 'values')
                                    sample_data = [f"{vals[1]} - {vals[2]}"] if len(vals) >= 3 else None
                        except Exception:
                            sample_data = None
                        self.app.send_custom_webhook_update(self.scraper_type, "progress", data=sample_data, stats=stats_dict)
            except:
                pass  # Window was destroyed
        
        # Ensure we're in the main thread
        if threading.current_thread() is threading.main_thread():
            _update_stats()
        else:
            try:
                if hasattr(self, 'window') and self.window.winfo_exists() and self.is_active:
                    self.window.after(0, _update_stats)
            except:
                pass  # Window was destroyed
        
    def add_log(self, message):
        """Add a log message"""
        if not self.is_active:
            return
            
        def _add_log():
            try:
                if hasattr(self, 'window') and self.window.winfo_exists() and self.is_active:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
                    self.log_text.see(tk.END)
            except:
                pass  # Window was destroyed
        
        # Ensure we're in the main thread
        if threading.current_thread() is threading.main_thread():
            _add_log()
        else:
            try:
                if hasattr(self, 'window') and self.window.winfo_exists() and self.is_active:
                    self.window.after(0, _add_log)
            except:
                pass  # Window was destroyed
        
    # add_result method removed - results preview no longer needed
        
    def close(self):
        """Close the progress window"""
        self.is_active = False
        try:
            if hasattr(self, 'window') and self.window.winfo_exists():
                self.window.destroy()
        except:
            pass

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clients Hunting Tool")
        # Make the window full screen by default
        self.root.state('zoomed')
        # Set minimum window size
        self.root.minsize(1440, 900)  # Increased minimum size
        self.root.configure(bg=ModernUI.BG_COLOR)
        
        # Set current version
        self.VERSION = "1.0.0"
        
        # Apply modern UI styles
        ModernUI.configure_styles()
        
        # Load config
        self.config = self.load_config()
        
        # Get HWID
        self.hwid = self.get_hwid()
        
        # Create main container
        self.main_container = ttk.Frame(root, style='Modern.TFrame')
        self.main_container.pack(fill='both', expand=True)
        
        # Create auth frame (login/register)
        self.auth_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        self.auth_frame.pack(fill='both', expand=True)
        
        # Create dashboard frame (hidden initially)
        self.dashboard_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        
        # Setup auth UI
        self.setup_auth_ui()
        
        # Setup dashboard UI
        self.setup_dashboard_ui()
        
        # User data
        self.user_data = {
            "username": "",
            "key": "",
            "expires_at": None,
            "level": 0  # Default level 0 (no access)
        }
        
        # Initialize scraping flags
        self.is_scraping = False
        self.is_a_scraping = False
        self.is_au_scraping = False
        self.is_email_scraping = False
        
        # Initialize Discord RPC
        self.discord_rpc = DiscordRPCManager()
        self.discord_rpc.connect()
        
        # Check for updates
        self.check_for_updates()
    
    def load_config(self):
        try:
            # Try to load from config.py first
            from config import API_BASE_URL
            return {"Server": {"Url": API_BASE_URL}}
        except:
            # Default config if config.py not available
            return {"Server": {"Url": "https://toollc.vercel.app"}}
    def get_hwid(self):
        """Get a unique hardware ID for this machine"""
        return str(uuid.getnode())

    def setup_auth_ui(self):
        # Remove and recreate auth_frame as CTkFrame
        if hasattr(self, 'auth_frame'):
            self.auth_frame.destroy()
        self.auth_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color=ModernUI.BG_COLOR)
        self.auth_frame.pack(fill='both', expand=True)

        # Create a centered container for the login form
        center_container = ctk.CTkFrame(self.auth_frame, corner_radius=0, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.5, anchor='center')

        # Logo placeholder - centered at the top
        logo_frame = ctk.CTkFrame(center_container, corner_radius=0, fg_color="transparent")
        logo_frame.pack(pady=(0, 30))
        
        # Logo placeholder (you can replace this with actual logo image)
        logo_label = ctk.CTkLabel(logo_frame, text="🔍", font=("Segoe UI", 48), 
                                 text_color=ModernUI.ACCENT_COLOR)
        logo_label.pack()
        
        # App title
        title_label = ctk.CTkLabel(logo_frame, text="Clients Hunting Tool", 
                                  font=("Segoe UI", 32, "bold"), 
                                  text_color=ModernUI.TEXT_COLOR)
        title_label.pack(pady=(10, 0))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(logo_frame, text="Professional Lead Generation Platform", 
                                     font=("Segoe UI", 14), 
                                     text_color=ModernUI.TEXT_COLOR)
        subtitle_label.pack(pady=(5, 0))

        # Main form container with rounded corners and shadow effect
        form_container = ctk.CTkFrame(center_container, corner_radius=20, 
                                     fg_color=ModernUI.SECONDARY_BG,
                                     border_width=1,
                                     border_color=ModernUI.BORDER_COLOR)
        form_container.pack(padx=40, pady=20)

        # Form header
        form_header = ctk.CTkFrame(form_container, corner_radius=0, fg_color="transparent")
        form_header.pack(fill='x', padx=30, pady=(30, 20))

        # Toggle buttons with better styling
        toggle_frame = ctk.CTkFrame(form_header, corner_radius=15, fg_color=ModernUI.BG_COLOR)
        toggle_frame.pack(fill='x')
        
        self.login_toggle = ctk.CTkButton(toggle_frame, text="Login", 
                                         command=lambda: self.toggle_auth_mode("login"), 
                                         corner_radius=15, 
                                         fg_color=ModernUI.ACCENT_COLOR, 
                                         text_color="#000000",
                                         font=("Segoe UI", 14, "bold"),
                                         height=40)
        self.login_toggle.pack(side='left', fill='x', expand=True, padx=(5, 2), pady=5)
        
        self.signup_toggle = ctk.CTkButton(toggle_frame, text="Signup", 
                                          command=lambda: self.toggle_auth_mode("signup"), 
                                          corner_radius=15, 
                                          fg_color=ModernUI.BG_COLOR, 
                                          text_color=ModernUI.TEXT_COLOR,
                                          font=("Segoe UI", 14),
                                          height=40)
        self.signup_toggle.pack(side='right', fill='x', expand=True, padx=(2, 5), pady=5)

        # Login and signup forms (only one visible at a time)
        self.login_form = ctk.CTkFrame(form_container, corner_radius=0, fg_color="transparent")
        self.signup_form = ctk.CTkFrame(form_container, corner_radius=0, fg_color="transparent")
        self.setup_login_form_ctk()
        self.setup_signup_form_ctk()
        self.login_form.pack(fill='both', expand=True, padx=30, pady=(0, 30))

        # Settings button in top-right corner
        settings_button = ctk.CTkButton(self.auth_frame, text="⚙️", 
                                       command=self.show_settings, 
                                       width=50, 
                                       corner_radius=25, 
                                       fg_color=ModernUI.ACCENT_COLOR, 
                                       text_color="#000000",
                                       font=("Segoe UI", 16))
        settings_button.place(relx=0.95, rely=0.05, anchor='ne')

        # Status bar at bottom
        status_frame = ctk.CTkFrame(self.auth_frame, corner_radius=0, fg_color=ModernUI.BG_COLOR)
        status_frame.pack(fill='x', side='bottom')
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to connect")
        status_label = ctk.CTkLabel(status_frame, textvariable=self.status_var, 
                                   font=("Segoe UI", 11),
                                   text_color=ModernUI.TEXT_COLOR)
        status_label.pack(side='left', padx=20, pady=8)

    def toggle_auth_mode(self, mode):
        # Visually update toggle buttons
        if mode == "login":
            self.signup_form.pack_forget()
            self.login_form.pack(fill='both', expand=True, padx=30, pady=(0, 30))
            self.login_toggle.configure(fg_color=ModernUI.ACCENT_COLOR, text_color="#000000", font=("Segoe UI", 14, "bold"))
            self.signup_toggle.configure(fg_color=ModernUI.BG_COLOR, text_color=ModernUI.TEXT_COLOR, font=("Segoe UI", 14))
        else:
            self.login_form.pack_forget()
            self.signup_form.pack(fill='both', expand=True, padx=30, pady=(0, 30))
            self.signup_toggle.configure(fg_color=ModernUI.ACCENT_COLOR, text_color="#000000", font=("Segoe UI", 14, "bold"))
            self.login_toggle.configure(fg_color=ModernUI.BG_COLOR, text_color=ModernUI.TEXT_COLOR, font=("Segoe UI", 14))

    def setup_login_form_ctk(self):
        for widget in self.login_form.winfo_children():
            widget.destroy()
        
        # Form title
        form_title = ctk.CTkLabel(self.login_form, text="Welcome Back", 
                                 font=("Segoe UI", 24, "bold"), 
                                 text_color=ModernUI.TEXT_COLOR)
        form_title.pack(pady=(0, 10))
        
        # Form subtitle
        form_subtitle = ctk.CTkLabel(self.login_form, text="Enter your license key to continue", 
                                   font=("Segoe UI", 12), 
                                   text_color=ModernUI.TEXT_COLOR)
        form_subtitle.pack(pady=(0, 30))
        
        # License Key input
        key_label = ctk.CTkLabel(self.login_form, text="License Key", 
                                font=("Segoe UI", 14, "bold"), 
                                text_color=ModernUI.TEXT_COLOR)
        key_label.pack(anchor="w", pady=(0, 8))
        
        self.login_key_entry = ctk.CTkEntry(self.login_form, 
                                           width=350, 
                                           height=45,
                                           corner_radius=10,
                                           font=("Segoe UI", 14),
                                           placeholder_text="Enter your license key...")
        self.login_key_entry.pack(fill='x', pady=(0, 25))
        
        # Login button
        login_button = ctk.CTkButton(self.login_form, 
                                   text="Login", 
                                   command=self.login, 
                                   width=350,
                                   height=45,
                                   corner_radius=10, 
                                   fg_color=ModernUI.ACCENT_COLOR, 
                                   text_color="#000000",
                                   font=("Segoe UI", 16, "bold"))
        login_button.pack(fill='x', pady=(0, 20))
        
        # Load saved key
        self.load_saved_key()

    def setup_signup_form_ctk(self):
        for widget in self.signup_form.winfo_children():
            widget.destroy()
        
        # Form title
        form_title = ctk.CTkLabel(self.signup_form, text="Create Account", 
                                 font=("Segoe UI", 24, "bold"), 
                                 text_color=ModernUI.TEXT_COLOR)
        form_title.pack(pady=(0, 10))
        
        # Form subtitle
        form_subtitle = ctk.CTkLabel(self.signup_form, text="Register with your license key", 
                                   font=("Segoe UI", 12), 
                                   text_color=ModernUI.TEXT_COLOR)
        form_subtitle.pack(pady=(0, 30))
        
        # Username input
        username_label = ctk.CTkLabel(self.signup_form, text="Username", 
                                     font=("Segoe UI", 14, "bold"), 
                                     text_color=ModernUI.TEXT_COLOR)
        username_label.pack(anchor="w", pady=(0, 8))
        
        self.username_entry = ctk.CTkEntry(self.signup_form, 
                                          width=350, 
                                          height=45,
                                          corner_radius=10,
                                          font=("Segoe UI", 14),
                                          placeholder_text="Enter your username...")
        self.username_entry.pack(fill='x', pady=(0, 20))
        
        # License Key input
        key_label = ctk.CTkLabel(self.signup_form, text="License Key", 
                                font=("Segoe UI", 14, "bold"), 
                                text_color=ModernUI.TEXT_COLOR)
        key_label.pack(anchor="w", pady=(0, 8))
        
        self.register_key_entry = ctk.CTkEntry(self.signup_form, 
                                              width=350, 
                                              height=45,
                                              corner_radius=10,
                                              font=("Segoe UI", 14),
                                              placeholder_text="Enter your license key...")
        self.register_key_entry.pack(fill='x', pady=(0, 25))
        
        # Signup button
        signup_button = ctk.CTkButton(self.signup_form, 
                                     text="Create Account", 
                                     command=self.register, 
                                     width=350,
                                     height=45,
                                     corner_radius=10, 
                                     fg_color=ModernUI.ACCENT_COLOR, 
                                     text_color="#000000",
                                     font=("Segoe UI", 16, "bold"))
        signup_button.pack(fill='x', pady=(0, 20))

    def update_status(self, message, color=None):
        self.status_var.set(message)
        # Optional: Set color if style is configured for it
        # self.status_label.config(foreground=color or ModernUI.TEXT_COLOR)

    def login(self):
        key = self.login_key_entry.get()
        if not key:
            messagebox.showerror("Error", "Please enter a license key.")
            return

        self.update_status("Logging in...")
        try:
            response = requests.post(
                f"{self.config['Server']['Url']}/api/verify",
                json={"key": key, "hwid": self.hwid},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.user_data.update({
                    "username": data.get("username"),
                    "key": key,
                    "expires_at": data.get("expires_at"),
                    "level": data.get("level", 0)
                })
                self.save_key(key)
                self.update_status("Login successful!")
                self.show_dashboard(self.user_data['username'], self.user_data['level'])
            else:
                error_message = response.json().get("message", "Unknown error")
                messagebox.showerror("Login Failed", f"Error: {error_message}")
                self.update_status("Login failed.")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Error", f"Could not connect to the server: {e}")
            self.update_status("Connection error.")

    def register(self):
        username = self.username_entry.get()
        key = self.register_key_entry.get()

        if not username or not key:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        self.update_status("Registering...")
        try:
            response = requests.post(
                f"{self.config['Server']['Url']}/api/register",
                json={"username": username, "key": key, "hwid": self.hwid},
                timeout=10
            )

            if response.status_code == 201:
                messagebox.showinfo("Success", "Registration successful! You can now log in.")
                self.update_status("Registration successful.")
                self.toggle_auth_mode('login')
            else:
                error_message = response.json().get("message", "Unknown error")
                messagebox.showerror("Registration Failed", f"Error: {error_message}")
                self.update_status("Registration failed.")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Error", f"Could not connect to the server: {e}")
            self.update_status("Connection error.")

    def save_key(self, key):
        try:
            with open("saved_key.txt", "w") as f:
                f.write(key)
        except Exception as e:
            print(f"Could not save key: {e}")

    def load_saved_key(self):
        try:
            with open("saved_key.txt", "r") as f:
                key = f.read().strip()
                if key:
                    self.login_key_entry.insert(0, key)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Could not load key: {e}")
    
    def setup_dashboard_ui(self):
        # Header with user info and logout button
        header_frame = ttk.Frame(self.dashboard_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', padx=20, pady=10)
        
        self.welcome_label = ttk.Label(header_frame, text="Welcome, User", style='Title.TLabel')
        self.welcome_label.pack(side='left')
        
        button_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        button_frame.pack(side='right')
        
        settings_button = ttk.Button(button_frame, text="⚙️", style='Modern.TButton',
                                    command=self.show_settings)
        settings_button.pack(side='left', padx=5)
        
        logout_button = ttk.Button(button_frame, text="Logout", style='Modern.TButton',
                                  command=self.logout)
        logout_button.pack(side='left', padx=5)
        
        # License info with days and progress bar
        license_container = ttk.Frame(self.dashboard_frame, style='Secondary.TFrame')
        license_container.pack(fill='x', padx=20, pady=10)
        
        license_title = ttk.Label(license_container, text="License Status", style='Title.TLabel')
        license_title.pack(pady=(10, 5))
        
        self.days_label = ttk.Label(license_container, text="Days remaining: Calculating...", style='Modern.TLabel')
        self.days_label.pack(pady=5)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(license_container, variable=self.progress_var, 
                                           style='Modern.Horizontal.TProgressbar',
                                           length=700)
        self.progress_bar.pack(pady=5)
        
        self.progress_label = ttk.Label(license_container, text="", style='Modern.TLabel')
        self.progress_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.dashboard_notebook = ttk.Notebook(self.dashboard_frame, style='Modern.TNotebook')
        self.dashboard_notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create frames for each scraper tab - these are just containers
        self.g_scraper_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')
        self.m_scraper_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')
        self.a_scraper_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')
        self.au_scraper_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')

    def show_dashboard(self, username, level):
        self.current_user = username
        self.auth_frame.pack_forget()
        self.dashboard_frame.pack(fill='both', expand=True)
        
        self.welcome_label.config(text=f"Welcome to Clients Hunting Tool, {username}!")
        
        # Update Discord RPC for dashboard
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_menu_activity()
        
        # Calculate and display license progress
        days_text, days_remaining, progress = self.calculate_license_progress()
        self.days_label.config(text=f"Days remaining: {days_text}")
        self.progress_var.set(progress)
        
        # Color code the progress bar
        if days_remaining <= 0:
            self.progress_label.config(text="License Expired", foreground="red")
        elif days_remaining <= 7:
            self.progress_label.config(text="License Expiring Soon", foreground="orange")
        else:
            self.progress_label.config(text=f"License Active - {progress:.1f}% remaining", foreground="green")
        
        # Clear existing tabs
        for tab in self.dashboard_notebook.tabs():
            self.dashboard_notebook.forget(tab)
            
        # Lazily create tab content if it doesn't exist
        if not hasattr(self, 'g_scraper_widgets_created'):
            self.create_gscraper_tab()
            self.g_scraper_widgets_created = True
            
        if not hasattr(self, 'm_scraper_widgets_created'):
            self.create_mscraper_tab()
            self.m_scraper_widgets_created = True

        if not hasattr(self, 'a_scraper_widgets_created'):
            self.create_a_scraper_tab()
            self.a_scraper_widgets_created = True

        if not hasattr(self, 'au_scraper_widgets_created'):
            self.create_au_scraper_tab()
            self.au_scraper_widgets_created = True

        # Get permissions
        g_access, m_access, a_access, au_access = self.get_permissions_from_level(level)
        
        # Add tabs based on permissions
        if g_access:
            self.dashboard_notebook.add(self.g_scraper_frame, text='G Scraper')
        
        if m_access:
            self.dashboard_notebook.add(self.m_scraper_frame, text='M Scraper')
        
        if a_access:
            self.dashboard_notebook.add(self.a_scraper_frame, text='A Scraper')
        
        if au_access:
            self.dashboard_notebook.add(self.au_scraper_frame, text='AU Scraper')
            
        # If no tabs are available, show a message
        if not self.dashboard_notebook.tabs():
            no_access_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')
            ttk.Label(no_access_frame, text="Your license doesn't provide access to any features.\nPlease upgrade your license.", 
                     style='Modern.TLabel').place(relx=0.5, rely=0.5, anchor='center')
            self.dashboard_notebook.add(no_access_frame, text='No Access')

    def get_permissions_from_level(self, level):
        """
        Determines feature access based on user level.
        Level 1: Access to G Scraper only
        Level 2: Access to M Scraper only
        Level 3: Access to A Scraper only
        Level 4: Access to A Scraper only
        Level 5: Access to AU Scraper only
        Level 6: Access to all scrapers (G, M, A, AU)
        """
        g_scraper_access = False
        m_scraper_access = False
        a_scraper_access = False
        au_scraper_access = False
        if level == 1:
            g_scraper_access = True
        elif level == 2:
            m_scraper_access = True
        elif level == 3:
            a_scraper_access = True
        elif level == 4:
            a_scraper_access = True
        elif level == 5:
            au_scraper_access = True
        elif level == 6:
            g_scraper_access = True
            m_scraper_access = True
            a_scraper_access = True
            au_scraper_access = True
        return g_scraper_access, m_scraper_access, a_scraper_access, au_scraper_access

    def setup_captcha_handler(self):
        self.captcha_window = None
        self.captcha_entry = None
        self.current_captcha_url = None
        
    def show_captcha_popup(self, captcha_url):
        """Show captcha image in popup window"""
        # Create window if it doesn't exist
        if not hasattr(self, 'captcha_window') or not self.captcha_window.winfo_exists():
            self.captcha_window = tk.Toplevel(self.root)
            self.captcha_window.title("Solve Captcha")
            self.captcha_window.geometry("400x300")
            self.captcha_window.resizable(False, False)
            
            # Download and show captcha image
            self.captcha_image_label = tk.Label(self.captcha_window)
            self.captcha_image_label.pack(pady=10)
            
            # Captcha input
            input_frame = ttk.Frame(self.captcha_window)
            input_frame.pack(pady=10)
            
            ttk.Label(input_frame, text="Enter Captcha:").pack(side='left', padx=5)
            self.captcha_entry = ttk.Entry(input_frame, width=20)
            self.captcha_entry.pack(side='left', padx=5)
            
            # Submit button
            submit_btn = ttk.Button(self.captcha_window, text="Submit", 
                                    command=self.submit_captcha_solution,
                                    style='Modern.TButton')
            submit_btn.pack(pady=10)
        
        # Update captcha image
        try:
            response = requests.get(captcha_url, stream=True)
            img = Image.open(response.raw)
            photo = ImageTk.PhotoImage(img)
            self.captcha_image_label.configure(image=photo)
            self.captcha_image_label.image = photo
        except Exception as e:
            self.captcha_image_label.configure(text=f"Error loading captcha: {str(e)}")
        
        # Clear previous entry and show window
        self.captcha_entry.delete(0, tk.END)
        self.captcha_window.deiconify()
        self.captcha_window.grab_set()
    def submit_captcha_solution(self):
        """Send captcha solution back to scraper"""
        solution = self.captcha_entry.get().strip()
        if solution and self.amazon_scraper:
            self.amazon_scraper.captcha_solution = solution
            self.amazon_scraper.captcha_event.set()
        
        if self.captcha_window:
            self.captcha_window.destroy()

    def logout(self):
        # Disconnect Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.disconnect()
        
        # Hide dashboard and show auth frame
        self.dashboard_frame.pack_forget()
        self.auth_frame.pack(fill='both', expand=True)
    
    def show_settings(self):
        # Create settings popup
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("800x600")
        settings_window.configure(bg=ModernUI.BG_COLOR)
        settings_window.resizable(False, False)
        
        # Make it modal
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content with vertical scroll
        container = ttk.Frame(settings_window, style='Modern.TFrame')
        container.pack(fill='both', expand=True)

        canvas = tk.Canvas(container, bg=ModernUI.BG_COLOR, highlightthickness=0)
        vscroll = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        content_frame = ttk.Frame(canvas, style='Modern.TFrame')
        content_window = canvas.create_window((0, 0), window=content_frame, anchor='nw')

        def _on_content_configure(event):
            try:
                canvas.configure(scrollregion=canvas.bbox('all'))
            except Exception:
                pass

        def _on_canvas_configure(event):
            try:
                canvas.itemconfigure(content_window, width=event.width)
            except Exception:
                pass

        content_frame.bind('<Configure>', _on_content_configure)
        canvas.bind('<Configure>', _on_canvas_configure)

        # Add padding inside scrollable content
        pad = ttk.Frame(content_frame, style='Modern.TFrame', padding=(30, 30, 30, 30))
        pad.pack(fill='both', expand=True)
        content_frame = pad
        
        ttk.Label(content_frame, text="Application Settings", style='Title.TLabel').pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # General Settings Tab
        general_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(general_frame, text='General')
        
        # Version info
        version_frame = ttk.Frame(general_frame, style='Modern.TFrame')
        version_frame.pack(fill='x', pady=10)
        ttk.Label(version_frame, text="Version:", style='Modern.TLabel').pack(side='left')
        ttk.Label(version_frame, text=self.VERSION, style='Modern.TLabel').pack(side='right')
        
        # HWID info - using a text widget for better display
        hwid_frame = ttk.Frame(general_frame, style='Modern.TFrame')
        hwid_frame.pack(fill='x', pady=10)
        ttk.Label(hwid_frame, text="HWID:", style='Modern.TLabel').pack(side='left')
        
        # Create a text widget with a border for better visibility
        hwid_text = tk.Text(hwid_frame, height=1, width=30, font=ModernUI.NORMAL_FONT, 
                           bg=ModernUI.INPUT_BG, fg=ModernUI.TEXT_COLOR,
                           relief="solid", borderwidth=1)
        hwid_text.pack(side='right', padx=(10, 0))
        hwid_text.insert("1.0", self.hwid)
        hwid_text.configure(state="disabled")  # Make it read-only
        
        # Discord Webhook Settings Tab
        webhook_frame = ttk.Frame(notebook, style='Modern.TFrame')
        notebook.add(webhook_frame, text='Discord Webhook')
        
        # Webhook settings
        webhook_label = ttk.Label(webhook_frame, text="Custom Discord Webhook", style='Subtitle.TLabel')
        webhook_label.pack(pady=(0, 15))
        
        webhook_desc = ttk.Label(webhook_frame, 
                                text="Add your Discord webhook URL to receive live scraping updates and statistics directly to your Discord channel.",
                                style='Modern.TLabel', wraplength=500)
        webhook_desc.pack(pady=(0, 20))
        
        # Webhook URL card
        url_card = ttk.LabelFrame(webhook_frame, text="Webhook URL", padding=15, style='Modern.TLabelframe')
        url_card.pack(fill='x', pady=(0, 15))
        
        url_row = ttk.Frame(url_card, style='Modern.TFrame')
        url_row.pack(fill='x')
        
        self.webhook_url_var = tk.StringVar()
        self.webhook_url_entry = ttk.Entry(url_row,
                                           textvariable=self.webhook_url_var,
                                           style='Modern.TEntry')
        self.webhook_url_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # We'll load saved webhook after building all controls
        
        # Actions row
        url_actions = ttk.Frame(url_card, style='Modern.TFrame')
        url_actions.pack(fill='x', pady=(10, 0))
        
        save_button = ttk.Button(url_actions, text="Save / Update", command=self.save_custom_webhook, style='Modern.TButton')
        save_button.pack(side='left')
        
        test_button = ttk.Button(url_actions, text="Test", command=self.test_custom_webhook, style='Modern.TButton')
        test_button.pack(side='left', padx=(10, 0))
        
        def copy_webhook():
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.webhook_url_var.get())
                self.webhook_status_label.config(text="Copied to clipboard", foreground="green")
            except Exception:
                self.webhook_status_label.config(text="Copy failed", foreground="red")
            self.webhook_status_label.after(2000, lambda: self.webhook_status_label.config(text=""))
        
        copy_button = ttk.Button(url_actions, text="Copy", command=copy_webhook, style='Modern.TButton')
        copy_button.pack(side='left', padx=(10, 0))
        
        def clear_webhook():
            self.webhook_url_var.set("")
            self.save_custom_webhook()
            try:
                self.webhook_url_entry.configure(state='normal')
            except Exception:
                pass
            self.webhook_status_label.config(text="Webhook cleared", foreground="orange")
            self.webhook_status_label.after(2000, lambda: self.webhook_status_label.config(text=""))
        
        clear_button = ttk.Button(url_actions, text="Clear", command=clear_webhook, style='Modern.TButton')
        clear_button.pack(side='left', padx=(10, 0))
        
        def toggle_edit():
            try:
                current_state = str(self.webhook_url_entry.cget('state'))
                if current_state == 'disabled':
                    self.webhook_url_entry.configure(state='normal')
                    edit_button.configure(text='Lock')
                else:
                    if self.webhook_url_var.get().strip():
                        self.webhook_url_entry.configure(state='disabled')
                        edit_button.configure(text='Edit')
                    else:
                        self.webhook_status_label.config(text="Enter a webhook before locking", foreground="orange")
                        self.webhook_status_label.after(2000, lambda: self.webhook_status_label.config(text=""))
            except Exception:
                pass
        
        edit_button = ttk.Button(url_actions, text="Edit", command=toggle_edit, style='Modern.TButton')
        edit_button.pack(side='left', padx=(10, 0))
        
        # Helper text
        ttk.Label(url_card, text="Example: https://discord.com/api/webhooks/...", style='Modern.TLabel').pack(anchor='w', pady=(8, 0))
        
        # Webhook options card
        options_frame = ttk.LabelFrame(webhook_frame, text="Webhook Options", padding=15, style='Modern.TLabelframe')
        options_frame.pack(fill='x', pady=10)

        # Enable/disable webhook with explicit Enable/Disable buttons
        self.webhook_enabled_var = tk.BooleanVar(value=True)
        enable_row = ttk.Frame(options_frame, style='Modern.TFrame')
        enable_row.pack(fill='x', pady=(0, 10))
        ttk.Label(enable_row, text="Live Updates", style='Modern.TLabel').pack(side='left')

        def set_enabled(enabled: bool):
            self.webhook_enabled_var.set(bool(enabled))
            # Visual feedback: active button disabled, inactive enabled
            try:
                if enabled:
                    enable_btn.state(['disabled'])
                    disable_btn.state(['!disabled'])
                else:
                    disable_btn.state(['disabled'])
                    enable_btn.state(['!disabled'])
            except Exception:
                pass

        enable_btn = ttk.Button(enable_row, text="Enable", style='Modern.TButton', command=lambda: set_enabled(True), width=12)
        enable_btn.pack(side='right')
        disable_btn = ttk.Button(enable_row, text="Disable", style='Modern.TButton', command=lambda: set_enabled(False), width=12)
        disable_btn.pack(side='right', padx=(10, 0))

        # Initialize buttons to match current state
        set_enabled(self.webhook_enabled_var.get())
        
        # Update frequency (time-based) - button group
        self.webhook_frequency_var = tk.StringVar(value="realtime")
        frequency_frame = ttk.LabelFrame(options_frame, text="Update Frequency", padding=10, style='Modern.TLabelframe')
        frequency_frame.pack(fill='x', pady=(0, 10))

        freq_container = ttk.Frame(frequency_frame, style='Modern.TFrame')
        freq_container.pack(fill='x')

        def set_frequency(value: str):
            # Coerce legacy/saved unsupported values to 'realtime'
            if value not in ('realtime', 'every 1 min', 'every 5 min', 'every 10 min'):
                value = 'realtime'
            self.webhook_frequency_var.set(value)
            # Visually indicate selection by disabling active button
            try:
                for btn, val in [
                    (realtime_btn, 'realtime'),
                    (one_btn, 'every 1 min'),
                    (five_btn, 'every 5 min'),
                    (ten_btn, 'every 10 min'),
                ]:
                    if value == val:
                        btn.state(['disabled'])
                    else:
                        btn.state(['!disabled'])
            except Exception:
                pass

        realtime_btn = ttk.Button(freq_container, text="Realtime", style='Modern.TButton', command=lambda: set_frequency('realtime'))
        realtime_btn.pack(side='left', padx=10, pady=5)
        one_btn = ttk.Button(freq_container, text="1 min", style='Modern.TButton', command=lambda: set_frequency('every 1 min'))
        one_btn.pack(side='left', padx=10, pady=5)
        five_btn = ttk.Button(freq_container, text="5 min", style='Modern.TButton', command=lambda: set_frequency('every 5 min'))
        five_btn.pack(side='left', padx=10, pady=5)
        ten_btn = ttk.Button(freq_container, text="10 min", style='Modern.TButton', command=lambda: set_frequency('every 10 min'))
        ten_btn.pack(side='left', padx=10, pady=5)
        # Removed 'Completion only' button to keep layout within frame
        
        # What to send (button toggles instead of checkmarks)
        self.webhook_send_stats_var = tk.BooleanVar(value=True)
        self.webhook_send_data_var = tk.BooleanVar(value=True)
        self.webhook_send_errors_var = tk.BooleanVar(value=True)

        toggles = ttk.Frame(options_frame, style='Modern.TFrame')
        toggles.pack(fill='x', pady=(5, 0))

        def update_toggle(btn, is_on, base_text):
            try:
                btn.configure(text=f"{base_text} - {'On' if is_on else 'Off'}")
            except Exception:
                pass

        def toggle_stats():
            self.webhook_send_stats_var.set(not self.webhook_send_stats_var.get())
            update_toggle(stats_btn, self.webhook_send_stats_var.get(), 'Statistics')

        def toggle_data():
            self.webhook_send_data_var.set(not self.webhook_send_data_var.get())
            update_toggle(data_btn, self.webhook_send_data_var.get(), 'Data samples')

        def toggle_errors():
            self.webhook_send_errors_var.set(not self.webhook_send_errors_var.get())
            update_toggle(errors_btn, self.webhook_send_errors_var.get(), 'Errors')

        stats_btn = ttk.Button(toggles, text="Statistics - On", style='Modern.TButton', command=toggle_stats, width=18)
        stats_btn.grid(row=0, column=0, sticky='w', padx=(0, 12))
        data_btn = ttk.Button(toggles, text="Data samples - On", style='Modern.TButton', command=toggle_data, width=18)
        data_btn.grid(row=0, column=1, sticky='w', padx=(0, 12))
        errors_btn = ttk.Button(toggles, text="Errors - On", style='Modern.TButton', command=toggle_errors, width=14)
        errors_btn.grid(row=0, column=2, sticky='w')
        
        # Status label
        self.webhook_status_label = ttk.Label(webhook_frame, text="", style='Modern.TLabel')
        self.webhook_status_label.pack(pady=10)
        
        # Finally load saved webhook and sync button states
        self.load_custom_webhook()
        try:
            # Sync enable/disable buttons
            if 'enable_btn' in locals() and 'disable_btn' in locals():
                if self.webhook_enabled_var.get():
                    enable_btn.state(['disabled'])
                    disable_btn.state(['!disabled'])
                else:
                    disable_btn.state(['disabled'])
                    enable_btn.state(['!disabled'])
            # Sync frequency active button
            if 'set_frequency' in locals():
                set_frequency(self.webhook_frequency_var.get())
        except Exception:
            pass
        
        # Close button
        close_button = ttk.Button(content_frame, text="Close", style='Modern.TButton',
                                 command=settings_window.destroy)
        close_button.pack(pady=20)
    
    def load_custom_webhook(self):
        """Load saved custom webhook settings"""
        try:
            if os.path.exists("webhook_settings.json"):
                with open("webhook_settings.json", "r") as f:
                    settings = json.load(f)
                    url = settings.get("webhook_url", "")
                    self.webhook_url_var.set(url)
                    self.webhook_enabled_var.set(settings.get("enabled", True))
                    self.webhook_frequency_var.set(settings.get("frequency", "realtime"))
                    self.webhook_send_stats_var.set(settings.get("send_stats", True))
                    self.webhook_send_data_var.set(settings.get("send_data", True))
                    self.webhook_send_errors_var.set(settings.get("send_errors", True))
                    # Auto-lock input if webhook exists
                    try:
                        if url:
                            self.webhook_url_entry.configure(state='disabled')
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error loading webhook settings: {str(e)}")
    
    def save_custom_webhook(self):
        """Save custom webhook settings"""
        try:
            # Normalize values to plain types for JSON persistence
            settings = {
                "webhook_url": (self.webhook_url_var.get() or "").strip(),
                "enabled": bool(self.webhook_enabled_var.get()),
                "frequency": self.webhook_frequency_var.get() or "realtime",
                "send_stats": bool(self.webhook_send_stats_var.get()),
                "send_data": bool(self.webhook_send_data_var.get()),
                "send_errors": bool(self.webhook_send_errors_var.get())
            }
            
            with open("webhook_settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            
            self.webhook_status_label.config(text="✅ Settings saved successfully!", foreground="green")
            self.webhook_status_label.after(3000, lambda: self.webhook_status_label.config(text=""))
            
            # Lock input if URL present
            try:
                if settings.get("webhook_url", "").strip():
                    self.webhook_url_entry.configure(state='disabled')
            except Exception:
                pass
            
        except Exception as e:
            self.webhook_status_label.config(text=f"❌ Error saving settings: {str(e)}", foreground="red")
            self.webhook_status_label.after(3000, lambda: self.webhook_status_label.config(text=""))
    
    def test_custom_webhook(self):
        """Test the custom webhook"""
        webhook_url = self.webhook_url_var.get().strip()
        if not webhook_url:
            self.webhook_status_label.config(text="❌ Please enter a webhook URL", foreground="red")
            return
        
        try:
            test_message = {
                "username": "Clients Hunting Tool",
                "avatar_url": DISCORD_RPC_LOGO_URL,
                "embeds": [{
                    "title": "🔧 Webhook Test",
                    "description": "Your custom webhook is working correctly! You will now receive live updates during scraping.",
                    "color": 0x00ff00,
                    "fields": [
                        {"name": "Status", "value": "✅ Connected", "inline": True},
                        {"name": "User", "value": self.user_data.get("username", "Unknown"), "inline": True},
                        {"name": "Timestamp", "value": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
                    ],
                    "footer": {"text": "Clients Hunting Tool - Custom Webhook"}
                }]
            }
            
            response = requests.post(webhook_url, json=test_message, timeout=10)
            if response.status_code in [200, 204]:
                self.webhook_status_label.config(text="✅ Webhook test successful!", foreground="green")
            else:
                self.webhook_status_label.config(text=f"❌ Webhook test failed: {response.status_code}", foreground="red")
                
        except Exception as e:
            self.webhook_status_label.config(text=f"❌ Webhook test failed: {str(e)}", foreground="red")
        
        self.webhook_status_label.after(3000, lambda: self.webhook_status_label.config(text=""))
    
    def send_custom_webhook_update(self, scraper_type, message_type, data=None, stats=None):
        """Send update to custom webhook. Reads live UI state if available; falls back to saved JSON."""
        try:
            # 1) Prefer in-memory UI state (so user doesn't have to press Save for live run)
            settings = {}
            if hasattr(self, 'webhook_url_var'):
                settings["webhook_url"] = (self.webhook_url_var.get() or "").strip()
            if hasattr(self, 'webhook_enabled_var'):
                settings["enabled"] = bool(self.webhook_enabled_var.get())
            if hasattr(self, 'webhook_frequency_var'):
                settings["frequency"] = self.webhook_frequency_var.get() or "realtime"
            if hasattr(self, 'webhook_send_stats_var'):
                settings["send_stats"] = bool(self.webhook_send_stats_var.get())
            if hasattr(self, 'webhook_send_data_var'):
                settings["send_data"] = bool(self.webhook_send_data_var.get())
            if hasattr(self, 'webhook_send_errors_var'):
                settings["send_errors"] = bool(self.webhook_send_errors_var.get())

            # 2) Merge with saved JSON (as fallback/defaults)
            try:
                if os.path.exists("webhook_settings.json"):
                    with open("webhook_settings.json", "r") as f:
                        file_settings = json.load(f)
                        for k, v in file_settings.items():
                            settings.setdefault(k, v)
            except Exception:
                pass

            # Defaults if still missing
            settings.setdefault("enabled", True)
            settings.setdefault("frequency", "realtime")
            settings.setdefault("send_stats", True)
            settings.setdefault("send_data", True)
            settings.setdefault("send_errors", True)

            webhook_url = (settings.get("webhook_url") or "").strip()
            if not webhook_url:
                return  # nothing to send to
            # If disabled, still allow 'start' and 'completion' so users see session lifecycle
            if not settings.get("enabled", True) and message_type not in ("start", "completion"):
                return  # allow completion to go through even if they toggled mid-run
            
            # Check frequency (time-based)
            frequency = settings.get("frequency", "realtime")
            now_ts = time.time()
            if not hasattr(self, 'webhook_last_sent_ts'):
                self.webhook_last_sent_ts = {}
            interval_map = {
                "realtime": 0,
                "every 1 min": 60,
                "every 5 min": 300,
                "every 10 min": 600
            }
            interval = interval_map.get(frequency, 0)  # unknown strings default to realtime

            # Enforce interval per scraper/message type
            key = f"{scraper_type}:{message_type}"
            last_ts = self.webhook_last_sent_ts.get(key, 0)
            # If realtime (interval=0), allow every progress
            if interval and (now_ts - last_ts) < interval and message_type != "completion":
                return
            
            # Create embed based on message type
            embed = self.create_webhook_embed(scraper_type, message_type, data, stats, settings)
            
            webhook_message = {
                "username": "Clients Hunting Tool",
                "avatar_url": DISCORD_RPC_LOGO_URL,
                "embeds": [embed]
            }
            
            resp = requests.post(webhook_url, json=webhook_message, timeout=10)
            # consider both 200 and 204 as success; don't spam prints
            if resp.status_code in (200, 204):
                self.webhook_last_sent_ts[key] = now_ts
            self.webhook_last_sent_ts[key] = now_ts
            
        except Exception as e:
            print(f"Error sending custom webhook update: {str(e)}")
    
    def create_webhook_embed(self, scraper_type, message_type, data=None, stats=None, settings=None):
        """Create Discord embed for webhook message"""
        scraper_names = {
            "G": "Google Scraper",
            "M": "Email Scraper", 
            "A": "Amazon Scraper",
            "AU": "AU Scraper"
        }
        
        scraper_name = scraper_names.get(scraper_type, f"{scraper_type} Scraper")
        
        if message_type == "start":
            embed = {
                "title": f"🚀 {scraper_name} Started",
                "description": f"Scraping session has begun for **{scraper_name}**",
                "color": 0x00ff00,
                "fields": [
                    {"name": "User", "value": self.user_data.get("username", "Unknown"), "inline": True},
                    {"name": "Status", "value": "🟢 Running", "inline": True},
                    {"name": "Timestamp", "value": datetime.datetime.now().strftime("%H:%M:%S"), "inline": True}
                ],
                "footer": {"text": "Live updates enabled"}
            }
        
        elif message_type == "progress":
            embed = {
                "title": f"📊 {scraper_name} Progress",
                "description": f"Live statistics from **{scraper_name}**",
                "color": 0x0099ff,
                "fields": []
            }
            
            if stats and settings.get("send_stats", True):
                for key, value in stats.items():
                    embed["fields"].append({"name": key, "value": str(value), "inline": True})
            
            if data and settings.get("send_data", True):
                # Add sample data (first 3 results)
                sample_data = data[:3] if len(data) > 3 else data
                if sample_data:
                    data_text = "\n".join([f"• {item}" for item in sample_data])
                    embed["fields"].append({"name": "📋 Latest Results", "value": data_text, "inline": False})
            
            embed["footer"] = {"text": f"Updated at {datetime.datetime.now().strftime('%H:%M:%S')}"}
        
        elif message_type == "completion":
            embed = {
                "title": f"✅ {scraper_name} Completed",
                "description": f"Scraping session completed for **{scraper_name}**",
                "color": 0x00ff00,
                "fields": [
                    {"name": "User", "value": self.user_data.get("username", "Unknown"), "inline": True},
                    {"name": "Status", "value": "✅ Finished", "inline": True},
                    {"name": "Timestamp", "value": datetime.datetime.now().strftime("%H:%M:%S"), "inline": True}
                ],
                "footer": {"text": "Results ready for export"}
            }
            
            if stats:
                for key, value in stats.items():
                    embed["fields"].append({"name": key, "value": str(value), "inline": True})
        
        elif message_type == "error":
            embed = {
                "title": f"❌ {scraper_name} Error",
                "description": f"An error occurred during **{scraper_name}** execution",
                "color": 0xff0000,
                "fields": [
                    {"name": "Error", "value": str(data) if data else "Unknown error", "inline": False},
                    {"name": "User", "value": self.user_data.get("username", "Unknown"), "inline": True},
                    {"name": "Timestamp", "value": datetime.datetime.now().strftime("%H:%M:%S"), "inline": True}
                ],
                "footer": {"text": "Error notification"}
            }
        
        else:
            embed = {
                "title": f"ℹ️ {scraper_name} Update",
                "description": str(data) if data else "General update",
                "color": 0xffff00,
                "footer": {"text": f"Updated at {datetime.datetime.now().strftime('%H:%M:%S')}"}
            }
        
        return embed
    
    def check_for_updates(self):
        """Check if an update is available"""
        try:
            response = requests.get(
                f"{self.config['Server']['Url']}/api/check_update",
                params={"version": self.VERSION},
                timeout=5  # Set a timeout to avoid hanging the startup
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("update_available"):
                    latest_version = data.get("latest_version")
                    download_url = data.get("download_url", "https://clientshunting.com")
                    
                    # Show update notification
                    result = messagebox.askyesno(
                        "Update Available", 
                        f"A new version ({latest_version}) is available. Would you like to visit the download page?",
                        icon='info'
                    )
                    
                    if result:
                        # Open download URL in browser
                        webbrowser.open(download_url)
        except Exception as e:
            # Silently fail on startup - don't bother user if update check fails
            print(f"Update check failed: {str(e)}")

    def create_gscraper_tab(self):
        # Initialize data storage
        self.names_list = []
        self.address_list = []
        self.website_list = []
        self.phones_list = []
        self.keyword_list = []
        self.open_list = []
        self.scraped_urls = set()
        self.is_scraping = False
        self.output_file = "result.csv"
        self.serial_counter = 1  # Initialize serial number counter

        # Create main container with padding
        main_container = ttk.Frame(self.g_scraper_frame, style='Modern.TFrame', padding=25)
        main_container.pack(fill="both", expand=True)

        # Header with title and description
        header_frame = ttk.Frame(main_container, style='Modern.TFrame')
        header_frame.pack(fill="x", pady=(0, 30))
        
        ttk.Label(header_frame, text="Google Maps Scraper", 
                 style='Title.TLabel').pack(side="left")
        
        ttk.Label(header_frame, 
                 text="Extract business information from Google Maps", 
                 style='Subtitle.TLabel').pack(side="left", padx=25)

        # Control panels container
        controls_container = ttk.Frame(main_container, style='Modern.TFrame')
        controls_container.pack(fill="x", pady=(0, 25))
        controls_container.grid_columnconfigure(0, weight=2)
        controls_container.grid_columnconfigure(1, weight=1)

        # Search Settings Panel
        search_frame = ttk.LabelFrame(controls_container, text="Search Settings", 
                                    padding=20, style='Modern.TLabelframe')
        search_frame.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        ttk.Label(search_frame, 
                 text="Enter keywords separated by commas",
                 style='Modern.TLabel').pack(anchor="w", pady=(0, 10))
        
        self.keyword_input = tk.Text(search_frame, height=3,
                                   font=ModernUI.NORMAL_FONT,
                                   relief="solid", 
                                   borderwidth=1,
                                   bg=ModernUI.INPUT_BG,
                                   fg=ModernUI.TEXT_COLOR,
                                   insertbackground=ModernUI.TEXT_COLOR)
        self.keyword_input.pack(fill="x")

        # Output Settings Panel
        output_frame = ttk.LabelFrame(controls_container, text="Output Settings", 
                                    padding=20, style='Modern.TLabelframe')
        output_frame.grid(row=0, column=1, sticky="ew")

        ttk.Label(output_frame, 
                 text="Select where to save the results",
                 style='Modern.TLabel').pack(anchor="w", pady=(0, 10))
        
        file_container = ttk.Frame(output_frame, style='Modern.TFrame')
        file_container.pack(fill="x")
        
        self.file_entry = ttk.Entry(file_container, 
                                  style='Modern.TEntry')
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.file_entry.insert(0, "result.csv")

        browse_btn = ttk.Button(file_container, 
                              text="Browse", 
                              command=self.browse_file, 
                              style='Modern.TButton')
        browse_btn.pack(side="right")

        # Control Buttons Panel
        buttons_frame = ttk.Frame(main_container, style='Modern.TFrame')
        buttons_frame.pack(fill="x", pady=25)

        # Center-align the buttons
        buttons_container = ttk.Frame(buttons_frame, style='Modern.TFrame')
        buttons_container.pack(anchor="center")

        # Modern styled buttons
        self.start_button = ttk.Button(buttons_container, 
                                     text="Start", 
                                     command=self.start_scraping, 
                                     style='Modern.TButton')
        self.start_button.pack(side="left", padx=10)

        self.stop_button = ttk.Button(buttons_container, 
                                    text="Stop", 
                                    command=self.stop_scraping, 
                                    state="disabled",
                                    style='Modern.TButton')
        self.stop_button.pack(side="left", padx=10)

        reset_button = ttk.Button(buttons_container, 
                                text="Reset", 
                                command=self.reset_fields, 
                                style='Modern.TButton')
        reset_button.pack(side="left", padx=10)

        # Progress and Status Section - REMOVED - using separate progress window now

        # Results Section
        results_frame = ttk.Frame(main_container, style='Modern.TFrame')
        results_frame.pack(fill="both", expand=True, pady=(25, 0))

        # Create notebook for Results and Log
        results_notebook = ttk.Notebook(results_frame, style='Modern.TNotebook')
        results_notebook.pack(fill="both", expand=True)

        # Results Table Tab
        table_frame = ttk.Frame(results_notebook, style='Modern.TFrame', padding=15)
        results_notebook.add(table_frame, text="Results")

        # Create a frame for the tree and scrollbars
        tree_frame = ttk.Frame(table_frame, style='Modern.TFrame')
        tree_frame.pack(fill="both", expand=True)
        
        # Configure the table with proper column widths
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Serial", "Name", "Website", "Phone", "Keyword", "Opens At", "Address"),
            show="headings",
            style="Modern.Treeview",
            height=25  # Set a fixed height for better display
        )

        # Configure column widths proportionally
        column_widths = {
            "Serial": 60,
            "Name": 200,
            "Website": 250,
            "Phone": 150,
            "Keyword": 150,
            "Opens At": 150,
            "Address": 300
        }

        # Set fixed column widths
        for col, width in column_widths.items():
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=width, minwidth=width, stretch=True)

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)

        # Configure the tree with scrollbars
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # Pack everything with proper fill and expand
        self.tree.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")

        # Log Tab
        log_frame = ttk.Frame(results_notebook, style='Modern.TFrame', padding=15)
        results_notebook.add(log_frame, text="Log")

        # Configure log window
        self.log_window = tk.Text(log_frame,
                                font=("Consolas", 11),
                                bg=ModernUI.SECONDARY_BG,
                                fg=ModernUI.TEXT_COLOR,
                                relief="solid",
                                borderwidth=1,
                                insertbackground=ModernUI.TEXT_COLOR)
        self.log_window.pack(fill="both", expand=True)

        # Add scrollbar to log
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical",
                                    command=self.log_window.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.log_window.configure(yscrollcommand=log_scrollbar.set)

        # Add status label
        self.status_label = ttk.Label(main_container, 
                                    text="Status: Ready",
                                    style='Modern.TLabel')
        self.status_label.pack(pady=(10, 0))

        # Progress bar removed - now using separate progress window

    def browse_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(tk.END, file_path)

    def start_scraping(self):
        # Get keywords
        keywords = self.keyword_input.get("1.0", tk.END).strip().split(",")
        keywords = [kw.strip() for kw in keywords if kw.strip()]

        if not keywords:
            messagebox.showerror("Error", "Please enter valid keywords.")
            return

        self.output_file = self.file_entry.get() if self.file_entry.get() else "result.csv"

        # Clear previous data
        self.names_list.clear()
        self.address_list.clear()
        self.website_list.clear()
        self.phones_list.clear()
        self.keyword_list.clear()
        self.open_list.clear()
        self.scraped_urls.clear()

        # Clear UI
        self.log_window.delete("1.0", tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Update UI state
        self.is_scraping = True
        self.start_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        self.status_label["text"] = "Status: Scraping..."

        # Open progress window
        self.progress_window = ProgressWindow(self, "Google Maps Scraper")
        self.progress_window.add_log("Starting Google Maps scraping...")
        self.progress_window.update_stats({
            "Total Processed": "0",
            "Success": "0", 
            "Failed": "0",
            "Remaining": str(len(keywords))
        })

        # Update Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_scraping_activity("G", "Starting")
        
        # Send custom webhook start notification (always allowed)
        self.send_custom_webhook_update("G", "start")
        
        # Start scraping in a new thread
        threading.Thread(target=self._run_scraper, args=(keywords,), daemon=True).start()

    def _run_scraper(self, keywords):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()

                total_keywords = len(keywords)
                for idx, keyword in enumerate(keywords, 1):
                    if not self.is_scraping:
                        break

                    try:
                        # Update progress window
                        overall_progress = (idx / total_keywords) * 100
                        self.progress_window.update_overall_progress(overall_progress, f"Processing keyword {idx}/{total_keywords}")
                        self.progress_window.update_task_progress(0, f"Starting: {keyword}")
                        self.progress_window.add_log(f"Scraping for keyword: {keyword}")
                        
                        page.goto("https://www.google.com/maps", timeout=60000)
                        page.wait_for_timeout(2000)

                        # Search for the specified query
                        search_box = page.locator(SELECTORS['search_input'])
                        search_box.click()
                        search_box.fill(keyword)
                        page.keyboard.press("Enter")
                        
                        # Wait for results and initial load
                        page.wait_for_selector(SELECTORS['listing_links'], timeout=30000)
                        page.wait_for_timeout(3000)

                        scroll_count = 0
                        last_listing_count = 0
                        max_scrolls = 10

                        while self.is_scraping and scroll_count < max_scrolls:
                            listings = page.locator(SELECTORS['listing_links'])
                            listing_count = listings.count()

                            if listing_count == 0:
                                self.log("No listings found.")
                                break

                            if listing_count == last_listing_count:
                                scroll_count += 1
                            else:
                                scroll_count = 0
                                last_listing_count = listing_count

                            for i in range(listing_count):
                                if not self.is_scraping:
                                    break

                                try:
                                    listing = listings.nth(i)
                                    href = listing.get_attribute("href")

                                    if href in self.scraped_urls:
                                        continue

                                    # Ensure listing is visible
                                    listing.scroll_into_view_if_needed()
                                    page.wait_for_timeout(1000)
                                    
                                    # Try clicking with retry mechanism
                                    max_retries = 3
                                    for _ in range(max_retries):
                                        try:
                                            listing.click(timeout=5000)
                                            break
                                        except:
                                            page.mouse.wheel(0, 100)
                                            page.wait_for_timeout(1000)
                                    
                                    page.wait_for_timeout(2000)

                                    # Extract data with improved error handling
                                    data = {
                                        "name": "N/A",
                                        "address": "N/A",
                                        "website": "N/A",
                                        "phone": "N/A",
                                        "opens_at": "N/A"
                                    }

                                    try:
                                        data["name"] = page.locator(SELECTORS['name']).inner_text(timeout=2000)
                                    except:
                                        self.log("Could not extract name")

                                    try:
                                        data["address"] = page.locator(SELECTORS['address']).inner_text(timeout=2000)
                                    except:
                                        self.log("Could not extract address")

                                    try:
                                        data["website"] = page.locator(SELECTORS['website']).inner_text(timeout=2000)
                                    except:
                                        self.log("Could not extract website")

                                    try:
                                        data["phone"] = page.locator(SELECTORS['phone']).inner_text(timeout=2000)
                                    except:
                                        self.log("Could not extract phone")

                                    try:
                                        # Try both opening hours selectors
                                        opens_at = "N/A"
                                        try:
                                            opens_at = page.locator(SELECTORS['opens_at']).inner_text(timeout=2000)
                                        except:
                                            try:
                                                opens_at = page.locator(SELECTORS['opens_at_alt']).inner_text(timeout=2000)
                                            except:
                                                pass
                                        
                                        if opens_at != "N/A":
                                            opens_at = opens_at.split("⋅")[-1].strip()
                                        data["opens_at"] = opens_at
                                    except:
                                        self.log("Could not extract opening hours")

                                    # Save data
                                    self.names_list.append(data["name"])
                                    self.address_list.append(data["address"])
                                    self.website_list.append(data["website"])
                                    self.phones_list.append(data["phone"])
                                    self.keyword_list.append(keyword)
                                    self.open_list.append(data["opens_at"])
                                    self.scraped_urls.add(href)

                                    # Update UI
                                    self.update_log_table(
                                        data["name"], data["website"], data["phone"],
                                        keyword, data["opens_at"], data["address"]
                                    )
                                    
                                    # Update progress window
                                    self.progress_window.add_log(f"Scraped: {data['name']}")
                                    
                                    # Update statistics safely
                                    try:
                                        current_success = int(self.progress_window.stats_labels["Success"].cget("text")) + 1
                                        current_processed = int(self.progress_window.stats_labels["Total Processed"].cget("text")) + 1
                                        self.progress_window.update_stats({
                                            "Success": str(current_success),
                                            "Total Processed": str(current_processed)
                                        })
                                    except:
                                        # If stats update fails, just continue
                                        pass

                                except Exception as e:
                                    # Update progress window for errors
                                    self.progress_window.add_log(f"Error processing listing: {str(e)}")
                                    try:
                                        current_failed = int(self.progress_window.stats_labels["Failed"].cget("text")) + 1
                                        current_processed = int(self.progress_window.stats_labels["Total Processed"].cget("text")) + 1
                                        self.progress_window.update_stats({
                                            "Failed": str(current_failed),
                                            "Total Processed": str(current_processed)
                                        })
                                    except:
                                        # If stats update fails, just continue
                                        pass
                                    continue

                            # Scroll to load more results
                            page.mouse.wheel(0, 2000)
                            page.wait_for_timeout(2000)

                        # Update progress after each keyword - REMOVED - using progress window now

                    except Exception as e:
                        self.log(f"Error processing keyword {keyword}: {str(e)}")
                        continue

                # Save results
                if self.names_list:
                    self.progress_window.add_log("Saving results to CSV...")
                    self.save_to_csv()
                    self.progress_window.add_log("Scraping completed successfully!")
                    self.progress_window.update_overall_progress(100, "Scraping completed!")
                    self.progress_window.update_task_progress(100, "All done!")
                else:
                    self.progress_window.add_log("No results found to save.")
                    self.progress_window.update_overall_progress(100, "No results found")

        except Exception as e:
            self.progress_window.add_log(f"Error during scraping: {str(e)}")
            self.progress_window.update_overall_progress(0, "Error occurred")
        finally:
            self.is_scraping = False
            self.root.after(0, self._scraping_finished)

    def stop_scraping(self):
        self.is_scraping = False
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"
        self.status_label["text"] = "Status: Stopped"
        self.log("Scraping stopped.")

    def reset_fields(self):
        self.keyword_input.delete(1.0, tk.END)
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, "result.csv")
        self.log_window.delete(1.0, tk.END)
        self.status_label["text"] = "Status: Ready"
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Reset serial counter
        self.serial_counter = 1

    def save_to_csv(self):
        try:
            self.log("Saving data, please wait...")
            
            # Update Discord RPC for export
            if hasattr(self, 'discord_rpc'):
                self.discord_rpc.set_export_activity("G")
            
            # Create serial numbers for the data
            serial_numbers = list(range(1, len(self.names_list) + 1))
            
            df = pd.DataFrame({
                'Serial': serial_numbers,
                'Name': self.names_list,
                'Address': self.address_list,
                'Website': self.website_list,
                'Phone': self.phones_list,
                'Keyword': self.keyword_list,
                'Opens At': self.open_list
            })
            df.drop_duplicates(subset=['Name', 'Address'], inplace=True)
            df.to_csv(self.output_file, index=False)
            
            # Automatically share results
            try:
                self.send_to_discord()
                self.log("Results automatically shared")
            except Exception as webhook_error:
                self.log(f"Error sharing results: {str(webhook_error)}")
                
            self.log("Data is Saved.")
            messagebox.showinfo("Success", f"Results saved to {self.output_file}")
        except Exception as e:
            self.log(f"Error saving results: {str(e)}")

    def update_log_table(self, name, website, phone, keyword, open_at, address):
        """Update the results table with new data"""
        # Use after method to update UI from a different thread
        self.root.after(0, lambda: self._update_table(name, website, phone, keyword, open_at, address))

    def _update_table(self, name, website, phone, keyword, open_at, address):
        """Actually update the table (called in main thread)"""
        try:
            # Clean and prepare values
            values = [
                str(self.serial_counter),  # Serial number
                str(name).strip() if name else "N/A",
                str(website).strip() if website else "N/A",
                str(phone).strip() if phone else "N/A",
                str(keyword).strip() if keyword else "N/A",
                str(open_at).strip() if open_at else "N/A",
                str(address).strip() if address else "N/A"
            ]
            
            # Insert new row
            item_id = self.tree.insert("", "end", values=values)
            
            # Increment serial counter
            self.serial_counter += 1
            
            # Ensure the new item is visible
            self.tree.see(item_id)
            
            # Update the tree view
            self.tree.update_idletasks()
        except Exception as e:
            self.log(f"Error updating results table: {str(e)}")

    def log(self, message):
        # Use after method to update UI from a different thread
        self.root.after(0, lambda: self._log(message))

    def _log(self, message):
        self.log_window.insert(tk.END, f"{message}\n")
        self.log_window.see(tk.END)

    def update_progress(self, value):
        # Use after method to update UI from a different thread
        self.root.after(0, lambda: self._update_progress(value))

    def _update_progress(self, value):
        # Use after method to update UI from a different thread
        self.progress["value"] = value

    def send_to_discord(self):
        """Send scraped data to webhook"""
        try:
            # Create embed fields for webhook message
            total_results = len(self.names_list)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a temporary file with all results
            temp_file = "temp_webhook_data.txt"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("=== GOOGLE MAPS SCRAPING RESULTS ===\n\n")
                for i in range(total_results):
                    f.write(f"Result #{i+1}\n")
                    f.write(f"Name: {self.names_list[i]}\n")
                    f.write(f"Address: {self.address_list[i]}\n")
                    f.write(f"Website: {self.website_list[i]}\n")
                    f.write(f"Phone: {self.phones_list[i]}\n")
                    f.write(f"Opening Hours: {self.open_list[i]}\n")
                    f.write(f"Keyword: {self.keyword_list[i]}\n")
                    f.write("=" * 50 + "\n\n")

            # Create the main message content
            message = {
                "username": "Chakka",
                "avatar_url": "https://cdn.discordapp.com/emojis/1096607655482622053.webp?size=96",
                "embeds": [{
                    "title": "Google Maps Scraping Results",
                    "color": 3447003,
                    "fields": [
                        {
                            "name": "Total Results",
                            "value": str(total_results),
                            "inline": True
                        },
                        {
                            "name": "Timestamp",
                            "value": current_time,
                            "inline": True
                        },
                        {
                            "name": "Keywords Used",
                            "value": ", ".join(set(self.keyword_list)) or "N/A",
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": f"Scraped by {self.user_data['username']}"
                    }
                }]
            }

            # First, send the summary message
            send_to_discord_webhooks(message)

            # Then, send the file with all results
            with open(temp_file, 'rb') as f:
                files = {
                    'file': ('results.txt', f, 'text/plain')
                }
                send_to_discord_webhooks(None, files)

            # Also send the CSV file
            with open(self.output_file, 'rb') as f:
                files = {
                    'file': (os.path.basename(self.output_file), f, 'text/csv')
                }
                send_to_discord_webhooks(None, files)
            
            self.log("Results shared successfully")
        except Exception as e:
            self.log(f"Error : {str(e)}")
            raise

    def _scraping_finished(self):
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"
        self.status_label["text"] = "Status: Ready"
        
        # Update Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_menu_activity()
        
        # Send custom webhook completion notification (always allowed)
        completion_stats = {
            "Total Results": len(self.names_list),
            "Success": len([n for n in self.names_list if n != "N/A"]),
            "Failed": len([n for n in self.names_list if n == "N/A"]),
            "Keywords Processed": len(self.keyword_list)
        }
        self.send_custom_webhook_update("G", "completion", stats=completion_stats)
        
        # Close progress window if it exists
        if hasattr(self, 'progress_window') and self.progress_window:
            self.progress_window.close()
            self.progress_window = None

    def create_mscraper_tab(self):
        # Initialize data storage
        self.email_names_list = []
        self.email_website_list = []
        self.email_list = []
        self.email_keyword_list = []
        self.is_email_scraping = False
        self.email_output_file = "email_results.csv"
        self.input_websites_df = None  # Store the loaded DataFrame
        self.email_serial_counter = 1  # Initialize serial number counter

        # Create main container with padding
        main_container = ttk.Frame(self.m_scraper_frame, style='Modern.TFrame', padding=25)
        main_container.pack(fill="both", expand=True)

        # Header with title and description
        header_frame = ttk.Frame(main_container, style='Modern.TFrame')
        header_frame.pack(fill="x", pady=(0, 30))
        
        ttk.Label(header_frame, text="Email Scraper", 
                 style='Title.TLabel').pack(side="left")
        
        ttk.Label(header_frame, 
                 text="Extract email addresses from websites in CSV/Excel files", 
                 style='Subtitle.TLabel').pack(side="left", padx=25)

        # Control panels container
        controls_container = ttk.Frame(main_container, style='Modern.TFrame')
        controls_container.pack(fill="x", pady=(0, 25))
        controls_container.grid_columnconfigure(0, weight=2)
        controls_container.grid_columnconfigure(1, weight=1)

        # Input File Settings Panel
        input_frame = ttk.LabelFrame(controls_container, text="Input File Settings", 
                                    padding=20, style='Modern.TLabelframe')
        input_frame.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        ttk.Label(input_frame, 
                 text="Select CSV/Excel file containing website URLs",
                 style='Modern.TLabel').pack(anchor="w", pady=(0, 10))
        
        input_file_container = ttk.Frame(input_frame, style='Modern.TFrame')
        input_file_container.pack(fill="x")
        
        self.input_file_entry = ttk.Entry(input_file_container, 
                                        style='Modern.TEntry')
        self.input_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        input_browse_btn = ttk.Button(input_file_container, 
                                    text="Browse", 
                                    command=self.browse_input_file, 
                                    style='Modern.TButton')
        input_browse_btn.pack(side="right")

        # Column selection container
        self.column_frame = ttk.Frame(input_frame, style='Modern.TFrame')
        self.column_frame.pack(fill="x", pady=(15, 0))

        # Website column selection
        website_frame = ttk.Frame(self.column_frame, style='Modern.TFrame')
        website_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(website_frame, 
                 text="Website URL Column:",
                 style='Modern.TLabel').pack(side="left", padx=(0, 10))

        self.website_column_var = tk.StringVar()
        self.website_column_combo = ttk.Combobox(website_frame, 
                                               textvariable=self.website_column_var,
                                               state="readonly",
                                               style='Modern.TCombobox')
        self.website_column_combo.pack(side="left", fill="x", expand=True)

        # Name column selection
        name_frame = ttk.Frame(self.column_frame, style='Modern.TFrame')
        name_frame.pack(fill="x")

        ttk.Label(name_frame, 
                 text="Name Column:",
                 style='Modern.TLabel').pack(side="left", padx=(0, 10))

        self.name_column_var = tk.StringVar()
        self.name_column_combo = ttk.Combobox(name_frame, 
                                           textvariable=self.name_column_var,
                                           state="readonly",
                                           style='Modern.TCombobox')
        self.name_column_combo.pack(side="left", fill="x", expand=True)

        # Output Settings Panel
        output_frame = ttk.LabelFrame(controls_container, text="Output Settings", 
                                    padding=20, style='Modern.TLabelframe')
        output_frame.grid(row=0, column=1, sticky="ew")

        ttk.Label(output_frame, 
                 text="Select where to save the results",
                 style='Modern.TLabel').pack(anchor="w", pady=(0, 10))
        
        file_container = ttk.Frame(output_frame, style='Modern.TFrame')
        file_container.pack(fill="x")
        
        self.email_file_entry = ttk.Entry(file_container, 
                                       style='Modern.TEntry')
        self.email_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.email_file_entry.insert(0, "email_results.csv")

        browse_btn = ttk.Button(file_container, 
                              text="Browse", 
                              command=self.browse_email_file, 
                              style='Modern.TButton')
        browse_btn.pack(side="right")

        # Control Buttons Panel
        buttons_frame = ttk.Frame(main_container, style='Modern.TFrame')
        buttons_frame.pack(fill="x", pady=25)

        # Center-align the buttons
        buttons_container = ttk.Frame(buttons_frame, style='Modern.TFrame')
        buttons_container.pack(anchor="center")

        # Modern styled buttons
        self.email_start_button = ttk.Button(buttons_container, 
                                     text="Start", 
                                     command=self.start_email_scraping, 
                                     style='Modern.TButton')
        self.email_start_button.pack(side="left", padx=10)

        self.email_stop_button = ttk.Button(buttons_container, 
                                    text="Stop", 
                                    command=self.stop_email_scraping, 
                                    state="disabled",
                                    style='Modern.TButton')
        self.email_stop_button.pack(side="left", padx=10)

        reset_button = ttk.Button(buttons_container, 
                            text="Reset", 
                            command=self.reset_email_fields, 
                            style='Modern.TButton')
        reset_button.pack(side="left", padx=10)

        # Progress and Status Section - REMOVED - using separate progress window now

        # Results Section
        results_frame = ttk.Frame(main_container, style='Modern.TFrame')
        results_frame.pack(fill="both", expand=True, pady=(25, 0))

        # Create notebook for Results and Log
        results_notebook = ttk.Notebook(results_frame, style='Modern.TNotebook')
        results_notebook.pack(fill="both", expand=True)

        # Results Table Tab
        table_frame = ttk.Frame(results_notebook, style='Modern.TFrame', padding=15)
        results_notebook.add(table_frame, text="Results")

        # Create a frame for the tree and scrollbars
        tree_frame = ttk.Frame(table_frame, style='Modern.TFrame')
        tree_frame.pack(fill="both", expand=True)
        
        # Configure the table with proper column widths
        self.email_tree = ttk.Treeview(
            tree_frame,
            columns=("Serial", "Name", "Website", "Emails"),
            show="headings",
            style="Modern.Treeview",
            height=25  # Set a fixed height for better display
        )

        # Configure column widths proportionally
        column_widths = {
            "Serial": 60,
            "Name": 200,
            "Website": 300,
            "Emails": 400
        }

        # Set fixed column widths
        for col, width in column_widths.items():
            self.email_tree.heading(col, text=col, anchor="w")
            self.email_tree.column(col, width=width, minwidth=width, stretch=True)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.email_tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.email_tree.xview)

        # Configure the tree with scrollbars
        self.email_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # Pack everything with proper fill and expand
        self.email_tree.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")

        # Log Tab
        log_frame = ttk.Frame(results_notebook, style='Modern.TFrame', padding=15)
        results_notebook.add(log_frame, text="Log")

        # Configure log window
        self.email_log_window = tk.Text(log_frame,
                                font=("Consolas", 11),
                                bg=ModernUI.SECONDARY_BG,
                                fg=ModernUI.TEXT_COLOR,
                                relief="solid",
                                borderwidth=1,
                                insertbackground=ModernUI.TEXT_COLOR)
        self.email_log_window.pack(fill="both", expand=True)

        # Add scrollbar to log
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical",
                                command=self.email_log_window.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.email_log_window.configure(yscrollcommand=log_scrollbar.set)

        # Add status label
        self.email_status_label = ttk.Label(main_container, 
                                    text="Status: Ready",
                                    style='Modern.TLabel')
        self.email_status_label.pack(pady=(10, 0))

        # Progress bar removed - using separate progress window now

    def browse_email_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.email_file_entry.delete(0, tk.END)
            self.email_file_entry.insert(tk.END, file_path)

    def start_email_scraping(self):
        if self.input_websites_df is None:
            messagebox.showerror("Error", "Please load a CSV or Excel file first")
            return
            
        if not self.website_column_var.get():
            messagebox.showerror("Error", "Please select the website URL column")
            return

        self.email_output_file = self.email_file_entry.get() if self.email_file_entry.get() else "email_results.csv"

        # Get websites from the selected column
        websites = self.input_websites_df[self.website_column_var.get()].dropna().tolist()
        
        if not websites:
            messagebox.showerror("Error", "No website URLs found in the selected column")
            return

        # Clear previous data
        self.email_names_list.clear()
        self.email_website_list.clear()
        self.email_list.clear()
        self.email_keyword_list.clear()

        # Clear UI
        self.email_log_window.delete("1.0", tk.END)
        for item in self.email_tree.get_children():
            self.email_tree.delete(item)

        # Update UI state
        self.is_email_scraping = True
        self.email_start_button["state"] = "disabled"
        self.email_stop_button["state"] = "normal"
        self.email_status_label["text"] = "Status: Scraping..."

        # Open progress window
        self.email_progress_window = ProgressWindow(self, "Email Scraper")
        self.email_progress_window.add_log("Starting Email scraping...")
        self.email_progress_window.update_stats({
            "Total Processed": "0",
            "Success": "0", 
            "Failed": "0",
            "Remaining": str(len(websites))
        })

        # Update Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_scraping_activity("M", "Starting")
        
        # Send custom webhook start notification (always allowed)
        self.send_custom_webhook_update("M", "start")
        
        # Start scraping in a new thread
        threading.Thread(target=self._run_email_scraper, args=(websites,), daemon=True).start()

    def stop_email_scraping(self):
        self.is_email_scraping = False
        self.email_start_button["state"] = "normal"
        self.email_stop_button["state"] = "disabled"
        self.email_status_label["text"] = "Status: Stopped"
        self.email_log("Scraping stopped.")

    def reset_email_fields(self):
        self.email_keyword_input.delete(1.0, tk.END)
        self.email_file_entry.delete(0, tk.END)
        self.email_file_entry.insert(0, "email_results.csv")
        self.email_log_window.delete(1.0, tk.END)
        self.email_status_label["text"] = "Status: Ready"
        for item in self.email_tree.get_children():
            self.email_tree.delete(item)
        # Reset serial counter
        self.email_serial_counter = 1

    def is_system_healthy(self):
        # Check both memory and CPU usage
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        if mem.percent > 75:  # Keep memory threshold at 75% for stability
            self.email_log("High memory usage detected (>75%). Restarting browser...")
            return False
        if cpu > 95:  # Increased CPU threshold to 95%
            self.email_log("High CPU usage detected (>95%). Restarting browser...")
            return False
        return True

    def run_browser_session(self):
        import os
        import tempfile
        user_data_dir = tempfile.mkdtemp()
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')  # Enable headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')  # Added for better performance
        options.add_argument('--disable-software-rasterizer')  # Added for better performance
        options.add_argument('--disable-extensions')  # Added for better performance
        options.add_argument('--disable-logging')  # Reduce logging overhead
        options.add_argument('--log-level=3')  # Minimal logging
        options.add_argument('--disable-images')  # Skip loading images
        options.add_argument('--blink-settings=imagesEnabled=false')  # Disable image loading
        options.add_argument(f'--user-data-dir={user_data_dir}')
        try:
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(30)  # Set page load timeout
            driver.implicitly_wait(5)  # Set implicit wait time
            return driver
        except Exception as e:
            self.email_log(f"Error initializing browser: {str(e)}")
            return None

    def fetch_emails_from_website(self, driver, website):
        """Fetch emails and phones from main page and contact pages"""
        try:
            all_emails = []
            all_phones = []
            
            # First, scrape the main page
            self.log_a_message(f"Scraping main page: {website}")
            main_emails, main_phones = self._scrape_page_for_contacts(driver, website)
            all_emails.extend(main_emails)
            all_phones.extend(main_phones)
            
            # Then, look for and scrape contact pages
            contact_emails, contact_phones = self._scrape_contact_pages(driver, website)
            all_emails.extend(contact_emails)
            all_phones.extend(contact_phones)
            
            # Remove duplicates and return
            unique_emails = list(set(all_emails))
            unique_phones = list(set(all_phones))
            
            self.log_a_message(f"Total found - Emails: {len(unique_emails)}, Phones: {len(unique_phones)}")
            return self.filter_emails(unique_emails), self.filter_phones(unique_phones)
            
        except Exception as e:
            self.log_a_message(f"Error fetching emails/phones from {website}: {str(e)}")
            return [], []
    
    def _scrape_page_for_contacts(self, driver, url):
        """Scrape a single page for emails and phone numbers"""
        try:
            driver.get(url)
            time.sleep(1)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser', parse_only=SoupStrainer(['a', 'p', 'div', 'span']))
            
            # Find all text content
            text_content = ' '.join(tag.get_text() for tag in soup.find_all(['p', 'div', 'span']))
            
            # Find all emails using regex
            emails = email_regex.findall(text_content)
            
            # Find all phone numbers using improved regex
            phone_regex = re.compile(r'''
                (?:(?:\+|00)\d{1,3}[\s\-\.]*)?   # country code, optional
                (?:\(?\d{2,4}\)?[\s\-\.]*)?      # area code, optional
                (?:\d[\d\s\-\.]{8,}\d)           # main number, at least 10 digits total
            ''', re.VERBOSE)
            phones = phone_regex.findall(text_content)
            
            # Filter phone numbers
            def is_real_phone(num):
                digits = re.sub(r'\D', '', num)
                if len(digits) < 10:
                    return False
                if len(digits) >= 10:
                    digit_list = [int(d) for d in digits[:10]]
                    if len(set(digit_list)) <= 3:
                        return False
                    if len(set(digit_list)) <= 2:
                        return False
                return True
            
            phones = [p for p in phones if is_real_phone(p)]
            
            # Check for mailto links
            mailto_emails = [
                link.get('href')[7:] 
                for link in soup.find_all('a', href=lambda x: x and x.startswith('mailto:'))
            ]
            
            # Combine and return
            all_emails = list(set(emails + mailto_emails))
            all_phones = list(set(phones))
            
            return all_emails, all_phones
            
        except Exception as e:
            self.log_a_message(f"Error scraping page {url}: {str(e)}")
            return [], []
    
    def _scrape_contact_pages(self, driver, website):
        """Find and scrape contact pages for additional emails and phones"""
        try:
            contact_emails = []
            contact_phones = []
            
            # First, get the main page to find contact links
            driver.get(website)
            time.sleep(1)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Common contact page patterns
            contact_patterns = [
                'contact', 'kontakt', 'contato', 'contacto', 'kontakt', 'iletişim',
                'about', 'about-us', 'aboutus', 'about_us',
                'info', 'information', 'kontaktformular', 'contact-form',
                'reach-us', 'get-in-touch', 'connect', 'support',
                'help', 'faq', 'customer-service', 'customer-support',
                'sales', 'support', 'service', 'assistance', 'help-center',
                'contact-us', 'get-in-touch', 'write-to-us', 'email-us',
                'phone', 'call', 'telephone', 'toll-free', '1-800'
            ]
            
            # Find contact links
            contact_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                # Check if link text or href contains contact-related keywords
                if any(pattern in href or pattern in text for pattern in contact_patterns):
                    contact_links.append(link.get('href'))
            
            # Convert relative URLs to absolute URLs
            from urllib.parse import urljoin, urlparse
            base_url = website.rstrip('/')
            absolute_contact_links = []
            
            for link in contact_links:
                try:
                    if link.startswith('http'):
                        absolute_contact_links.append(link)
                    elif link.startswith('/'):
                        absolute_contact_links.append(urljoin(base_url, link))
                    elif link.startswith('#'):
                        # Skip anchor links
                        continue
                    else:
                        absolute_contact_links.append(urljoin(base_url + '/', link))
                except Exception as e:
                    self.log_a_message(f"Error processing link {link}: {str(e)}")
                    continue
            
            # Remove duplicates and filter out invalid URLs
            unique_contact_links = []
            seen_urls = set()
            
            for link in absolute_contact_links:
                try:
                    # Normalize URL
                    parsed = urlparse(link)
                    normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
                    
                    # Skip if we've already seen this URL or if it's invalid
                    if normalized_url in seen_urls or not parsed.netloc:
                        continue
                    
                    # Skip if it's the same as the main website
                    main_parsed = urlparse(website)
                    main_normalized = f"{main_parsed.scheme}://{main_parsed.netloc}".rstrip('/')
                    if normalized_url.startswith(main_normalized) and len(normalized_url) == len(main_normalized):
                        continue
                    
                    seen_urls.add(normalized_url)
                    unique_contact_links.append(link)
                    
                    # Limit to first 3 contact pages to avoid too many requests
                    if len(unique_contact_links) >= 3:
                        break
                        
                except Exception as e:
                    self.log_a_message(f"Error processing contact link {link}: {str(e)}")
                    continue
            
            if unique_contact_links:
                self.log_a_message(f"Found {len(unique_contact_links)} contact pages to check")
                
                for i, contact_url in enumerate(unique_contact_links, 1):
                    try:
                        self.log_a_message(f"Checking contact page {i}/{len(unique_contact_links)}: {contact_url}")
                        
                        # Check if the page is accessible
                        try:
                            driver.get(contact_url)
                            time.sleep(1)
                            
                            # Check if page loaded successfully
                            if "404" in driver.title.lower() or "not found" in driver.title.lower():
                                self.log_a_message(f"Contact page {contact_url} returned 404, skipping")
                                continue
                                
                        except Exception as e:
                            self.log_a_message(f"Could not access contact page {contact_url}: {str(e)}")
                            continue
                        
                        emails, phones = self._scrape_page_for_contacts(driver, contact_url)
                        
                        if emails or phones:
                            self.log_a_message(f"Found on contact page: {len(emails)} emails, {len(phones)} phones")
                        else:
                            self.log_a_message(f"No contact info found on contact page")
                            
                        contact_emails.extend(emails)
                        contact_phones.extend(phones)
                        
                        # Small delay between requests to be respectful
                        time.sleep(1)
                        
                    except Exception as e:
                        self.log_a_message(f"Error scraping contact page {contact_url}: {str(e)}")
                        continue
            else:
                self.log_a_message("No contact pages found")
            
            return contact_emails, contact_phones
            
        except Exception as e:
            self.log_a_message(f"Error finding contact pages: {str(e)}")
            return [], []
    def filter_emails(self, emails):
        valid_emails = []
        for email in emails:
            if email and '@' in email and '.' in email:
                valid_emails.append(email)
        return list(set(valid_emails))  # Remove duplicates
    def filter_phones(self, phones):
        valid_phones = []
        for phone in phones:
            digits = re.sub(r'\D', '', phone)
            # Only accept numbers with at least 10 digits and that start with +, 0, or a digit
            if len(digits) >= 10 and (phone.strip().startswith(('+', '0')) or phone.strip()[0].isdigit()):
                # Additional validation to filter out calendar dates and sequential numbers
                if len(digits) >= 10:
                    digit_list = [int(d) for d in digits[:10]]
                    # Skip if too many repeated digits (likely calendar/table numbers)
                    if len(set(digit_list)) <= 3:
                        continue
                    # Skip if it's a simple pattern like 1234567890 or 1111111111
                    if len(set(digit_list)) <= 2:
                        continue
                    # Skip if it looks like a date pattern (01 02 03...)
                    if len(digits) >= 20 and len(set(digit_list)) <= 5:
                        continue
                valid_phones.append(phone)
        return list(set(valid_phones))

    def handle_google_captcha(self, search_url):
        # In head mode: show a popup instructing the user to solve the CAPTCHA in the browser
        import tkinter as tk
        popup = tk.Toplevel(self.root)
        popup.title("Solve CAPTCHA")
        popup.geometry("400x150")
        label = tk.Label(popup, text="SOLVE THE CAPTCHA in the browser window,\nthen close this popup to continue.", font=("Segoe UI", 14), wraplength=380)
        label.pack(pady=30)
        btn = tk.Button(popup, text="Continue", command=popup.destroy, font=("Segoe UI", 12, "bold"))
        btn.pack(pady=10)
        popup.grab_set()
        self.root.wait_window(popup)

    def search_store_on_google(self, driver, name):
        """Search for a store's website on Google, open the first non-blacklisted link (skip amazon.com, ebay.com, etc.)"""
        try:
            from urllib.parse import urlparse
            brand_raw = name.strip()
            # Remove 'Visit the ' from start and ' Store' from end (case-insensitive)
            brand = brand_raw
            if brand.lower().startswith('visit the '):
                brand = brand[len('visit the '):]
            if brand.lower().endswith(' store'):
                brand = brand[:-len(' store')]
            brand = brand.strip()
            search_query = brand
            search_url = f"https://www.google.com/search?q={quote(search_query)}"
            self.log_a_message(f"Searching Google for: {brand}")
            driver.get(search_url)
            time.sleep(2)
            # CAPTCHA DETECTION
            if 'recaptcha' in driver.page_source.lower() or "i'm not a robot" in driver.page_source.lower():
                self.log_a_message("Google CAPTCHA detected. Waiting for user to solve it.")
                self.handle_google_captcha(search_url)
                driver.get(search_url)
                time.sleep(2)
            selectors = [
                "div.g div.yuRUbf > a[href]",
                "div.g a[href]",
                "a[href]"
            ]
            blacklisted_domains = [
                'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
                'youtube.com', 'yelp.com', 'yellowpages.com', 'google.com',
                'pinterest.com', 'tiktok.com', 'crunchbase.com', 'bloomberg.com',
                'indeed.com', 'glassdoor.com', 'ebay.com',
                'zhidao.baidu.com', 'baidu.com', 'support.google.com',
                'imdb.com', 'wikipedia.org', 'quora.com', 'reddit.com', 'stackoverflow.com',
                'tripadvisor.com', 'foursquare.com', 'trustpilot.com', 'yahoo.com', 'ask.com',
                'mapquest.com', 'maps.google.com', 'apple.com/maps', 'openstreetmap.org',
                'britannica.com', 'britannica.org', 'alibaba.com', 'aliexpress.com', 'etsy.com',
                'shopify.com', 'bigcommerce.com', 'weebly.com', 'wix.com', 'wordpress.com',
                'tumblr.com', 'blogspot.com', 'medium.com', 'bilibili.com', 'vk.com', 'naver.com',
                'baike.baidu.com', 'baike.com', 'sogou.com', 'sohu.com', '163.com', 'qq.com',
                'mail.ru', 'yandex.ru', 'live.com', 'msn.com', 'bing.com', 'duckduckgo.com',
                'rottentomatoes.com', 'metacritic.com', 'fandango.com', 'letterboxd.com', 'allmovie.com',
                'tvguide.com', 'boxofficemojo.com', 'movieinsider.com', 'the-numbers.com', 'filmaffinity.com',
                'movieweb.com', 'screenrant.com', 'collider.com', 'looper.com', 'ew.com', 'variety.com',
                'hollywoodreporter.com', 'deadline.com',
                # Add aggregator/manuals sites
                'manuals.plus', 'manualslib.com', 'manualsdir.com', 'manualsonline.com',
                'manualsworld.com', 'manualspdf.com', 'manualspoint.com', 'manualslib.org',
                'techradar.com', 'zdnet.com', 'cnet.com', 'pcmag.com', 'tomshardware.com',
                'anandtech.com', 'arstechnica.com', 'theverge.com', 'engadget.com',
                'gizmodo.com', 'lifehacker.com', 'mashable.com', 'techcrunch.com',
                'wired.com', 'recode.net', 'venturebeat.com', 'readwrite.com',
                'brandshop.co.uk', 'walmart.com', 'target.com', 'bestbuy.com',
                'newegg.com', 'microcenter.com', 'frys.com', 'bjs.com',
                'costco.com', 'samsclub.com', 'homedepot.com', 'lowes.com', 'ubuy.ge' 'walmart.com' 'walmart.ge'
            ]
            allowed_tlds = ['.com', '.net', '.org']
            brand_lower = brand.lower()
            fallback_url = None
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    self.log_a_message(f"Selector '{selector}' found {len(elements)} links.")
                    for element in elements:
                        try:
                            url = element.get_attribute('href')
                            if not url:
                                continue
                            parsed = urlparse(url)
                            domain = parsed.netloc.lower().replace('www.', '').split(':')[0]
                            self.log_a_message(f"Candidate URL: {url} (domain: {domain})")
                            if any(bad in domain for bad in blacklisted_domains) or 'amazon' in domain:
                                continue
                            # Only accept if domain contains brand name and ends with allowed TLD
                            domain_main = domain.split('.')[-2] if '.' in domain else domain
                            tld = '.' + domain.split('.')[-1] if '.' in domain else ''
                            if brand_lower in domain_main and tld in allowed_tlds:
                                self.log_a_message(f"Selected website: {url} (domain contains brand and allowed TLD)")
                                return url
                            # Fallback: first non-blacklisted
                            if not fallback_url:
                                fallback_url = url
                        except Exception as e:
                            self.log_a_message(f"Error parsing candidate URL: {e}")
                            continue
                except Exception as e:
                    self.log_a_message(f"Error with selector '{selector}': {e}")
                    continue
            # Fallback: try with 'website' appended
            search_url = f"https://www.google.com/search?q={quote(brand + ' website')}"
            driver.get(search_url)
            time.sleep(2)
            # CAPTCHA DETECTION for fallback
            if 'recaptcha' in driver.page_source.lower() or "i'm not a robot" in driver.page_source.lower():
                self.log_a_message("Google CAPTCHA detected. Waiting for user to solve it.")
                self.handle_google_captcha(search_url)
                driver.get(search_url)
                time.sleep(2)
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, "div.g a[href]")
                self.log_a_message(f"Fallback selector found {len(elements)} links.")
                for element in elements:
                    try:
                        url = element.get_attribute('href')
                        if not url:
                            continue
                        parsed = urlparse(url)
                        domain = parsed.netloc.lower().replace('www.', '').split(':')[0]
                        self.log_a_message(f"Candidate URL: {url} (domain: {domain})")
                        if any(bad in domain for bad in blacklisted_domains) or 'amazon' in domain:
                            continue
                        # Only accept if domain contains brand name and ends with allowed TLD
                        domain_main = domain.split('.')[-2] if '.' in domain else domain
                        tld = '.' + domain.split('.')[-1] if '.' in domain else ''
                        if brand_lower in domain_main and tld in allowed_tlds:
                            self.log_a_message(f"Selected website: {url} (domain contains brand and allowed TLD)")
                            return url
                        # Fallback: first non-blacklisted
                        if not fallback_url:
                            fallback_url = url
                    except Exception as e:
                        self.log_a_message(f"Error parsing candidate URL: {e}")
                        continue
            except Exception as e:
                self.log_a_message(f"Error in fallback selector: {e}")
                pass
            if fallback_url:
                self.log_a_message(f"No domain matched brand and TLD, using first non-blacklisted: {fallback_url}")
                return fallback_url
            self.log_a_message(f"No website found for: {brand}")
            return None
        except Exception as e:
            self.log_a_message(f"Error searching Google: {str(e)}")
            return None

    def _run_email_scraper(self, websites):
        try:
            driver = None
            try:
                driver = self.run_browser_session()
                if not driver:
                    self.email_progress_window.add_log("Failed to initialize browser. Exiting.")
                    return

                total_websites = len(websites)
                selected_column = self.website_column_var.get()
                is_website_column = any(keyword in selected_column.lower() for keyword in ['website', 'url', 'site', 'web'])
                
                for idx, website_or_name in enumerate(self.input_websites_df[selected_column].dropna(), 1):
                    if not self.is_email_scraping:
                        break

                    # Update progress window
                    progress = (idx / total_websites) * 100
                    self.email_progress_window.update_overall_progress(progress, f"Processing {idx}/{total_websites}")
                    self.email_progress_window.update_task_progress(0, f"Processing: {website_or_name}")

                    try:
                        # Handle the entry based on whether it's a website URL or a name
                        website_or_name = str(website_or_name).strip()
                        
                        if is_website_column:
                            # Direct website URL processing
                            if not website_or_name:
                                self.email_progress_window.add_log(f"Skipping: Empty website URL")
                                continue
                                
                            if not website_or_name.startswith(('http://', 'https://')):
                                website_or_name = f'https://{website_or_name}'
                                
                            self.email_progress_window.add_log(f"Processing website {idx}/{total_websites}: {website_or_name}")
                            website_url = website_or_name
                            
                        else:
                            # Name-based website search
                            self.email_progress_window.add_log(f"Searching for website of: {website_or_name} ({idx}/{total_websites})")
                            website_url = self.search_store_on_google(driver, website_or_name)
                            
                            if not website_url:
                                self.email_progress_window.add_log(f"No website found for: {website_or_name}")
                                self.email_names_list.append(website_or_name)
                                self.email_website_list.append("No website found")
                                self.email_list.append("No emails found")
                                self.update_email_table(website_or_name, "No website found", [])
                                
                                # Update progress window stats
                                try:
                                    current_failed = int(self.email_progress_window.stats_labels["Failed"].cget("text")) + 1
                                    current_processed = int(self.email_progress_window.stats_labels["Total Processed"].cget("text")) + 1
                                    remaining = int(self.email_progress_window.stats_labels["Remaining"].cget("text")) - 1
                                    self.email_progress_window.update_stats({
                                        "Failed": str(current_failed),
                                        "Total Processed": str(current_processed),
                                        "Remaining": str(remaining)
                                    })
                                except:
                                    pass
                                continue

                        # Check system health and restart browser if needed
                        if not self.is_system_healthy():
                            self.email_progress_window.add_log("High system usage detected. Restarting browser...")
                            driver.quit()
                            time.sleep(1)
                            driver = self.run_browser_session()
                            if not driver:
                                self.email_progress_window.add_log("Failed to restart browser. Exiting.")
                                break

                        # Fetch emails with retry mechanism
                        max_retries = 2
                        emails = []
                        for retry in range(max_retries):
                            try:
                                self.email_progress_window.update_task_progress(50, f"Fetching emails from {website_url}")
                                emails = self.fetch_emails_from_website(driver, website_url)
                                if emails:  # If we found emails, break the retry loop
                                    break
                                elif retry < max_retries - 1:  # If no emails found and we have retries left
                                    self.email_progress_window.add_log("No emails found, retrying...")
                                    time.sleep(1)
                            except Exception as e:
                                if retry < max_retries - 1:
                                    self.email_progress_window.add_log(f"Retry {retry + 1}: {str(e)}")
                                    time.sleep(1)
                                else:
                                    raise e
                        
                        # Store data
                        self.email_names_list.append(website_or_name)
                        self.email_website_list.append(website_url)
                        self.email_list.append(", ".join(emails) if emails else "No emails found")
                        
                        # Update UI
                        self.update_email_table(website_or_name, website_url, emails)
                        self.email_progress_window.add_log(f"Found {len(emails)} emails from {website_url}")
                        
                        # Update progress window stats
                        try:
                            if emails:
                                current_success = int(self.email_progress_window.stats_labels["Success"].cget("text")) + 1
                            else:
                                current_success = int(self.email_progress_window.stats_labels["Success"].cget("text"))
                                
                            current_processed = int(self.email_progress_window.stats_labels["Total Processed"].cget("text")) + 1
                            remaining = int(self.email_progress_window.stats_labels["Remaining"].cget("text")) - 1
                            
                            self.email_progress_window.update_stats({
                                "Success": str(current_success),
                                "Total Processed": str(current_processed),
                                "Remaining": str(remaining)
                            })
                        except:
                            pass
                        
                        self.email_progress_window.update_task_progress(100, f"Completed: {website_or_name}")
                        
                    except Exception as e:
                        self.email_progress_window.add_log(f"Error processing {website_or_name}: {str(e)}")
                        # Still store the error result
                        self.email_names_list.append(website_or_name)
                        self.email_website_list.append("Error processing website")
                        self.email_list.append("Error: " + str(e))
                        self.update_email_table(website_or_name, "Error", [])
                        
                        # Update progress window stats for error
                        try:
                            current_failed = int(self.email_progress_window.stats_labels["Failed"].cget("text")) + 1
                            current_processed = int(self.email_progress_window.stats_labels["Total Processed"].cget("text")) + 1
                            remaining = int(self.email_progress_window.stats_labels["Remaining"].cget("text")) - 1
                            self.email_progress_window.update_stats({
                                "Failed": str(current_failed),
                                "Total Processed": str(current_processed),
                                "Remaining": str(remaining)
                            })
                        except:
                            pass
                        continue
                
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
            
            # Save results
            if self.email_website_list:
                self.email_progress_window.add_log("Saving results to CSV...")
                self.save_email_results()
                self.email_progress_window.add_log("Email scraping completed successfully!")
                self.email_progress_window.update_overall_progress(100, "Email scraping completed!")
                self.email_progress_window.update_task_progress(100, "All done!")
            else:
                self.email_progress_window.add_log("No results found to save.")
                self.email_progress_window.update_overall_progress(100, "No results found")
            
        except Exception as e:
            self.email_progress_window.add_log(f"Fatal error in email scraper: {str(e)}")
            self.email_progress_window.update_overall_progress(0, "Error occurred")
        finally:
            self.is_email_scraping = False
            self.root.after(0, self._email_scraping_finished)

    def update_email_table(self, name, website, emails):
        """Update the results table with new data"""
        self.root.after(0, lambda: self._update_email_table(name, website, emails))

    def _update_email_table(self, name, website, emails):
        """Actually update the table (called in main thread)"""
        try:
            # Clean and prepare values
            values = [
                str(self.email_serial_counter),  # Serial number
                str(name).strip() if name else "N/A",
                str(website).strip() if website else "N/A",
                ", ".join(emails) if emails else "No emails found"
            ]
            
            # Insert new row
            item_id = self.email_tree.insert("", "end", values=values)
            
            # Increment serial counter
            self.email_serial_counter += 1
            
            # Ensure the new item is visible
            self.email_tree.see(item_id)
            
            # Update the tree view
            self.email_tree.update_idletasks()
        except Exception as e:
            self.email_log(f"Error updating results table: {str(e)}")

    def email_log(self, message):
        """Log a message to the email log window"""
        self.root.after(0, lambda: self._email_log(message))

    def _email_log(self, message):
        """Actually log the message (called in main thread)"""
        self.email_log_window.insert(tk.END, f"{message}\n")
        self.email_log_window.see(tk.END)

    # Progress update methods removed - using separate progress window now

    def save_email_results(self):
        """Save scraped email data to CSV file"""
        try:
            self.email_log("Saving results...")
            # Create serial numbers for the data
            serial_numbers = list(range(1, len(self.email_names_list) + 1))
            
            df = pd.DataFrame({
                'Serial': serial_numbers,
                'Name': self.email_names_list,
                'Website': self.email_website_list,
                'Emails': self.email_list
            })
            df.drop_duplicates(inplace=True)
            df.to_csv(self.email_output_file, index=False)
            
            # Automatically share results
            try:
                self.send_email_results_to_discord()
                self.email_log("Results automatically shared")
            except Exception as webhook_error:
                self.email_log(f"Error sharing results: {str(webhook_error)}")
            
            self.email_log(f"Results saved to {self.email_output_file}")
            messagebox.showinfo("Success", f"Results saved to {self.email_output_file}")
        except Exception as e:
            self.email_log(f"Error saving results: {str(e)}")

    def send_email_results_to_discord(self):
        """Send email scraping results to webhook"""
        try:
            total_results = len(self.email_names_list)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a temporary file with all results
            temp_file = "temp_email_data.txt"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("=== EMAIL SCRAPING RESULTS ===\n\n")
                for i in range(total_results):
                    f.write(f"Result #{i+1}\n")
                    f.write(f"Name: {self.email_names_list[i]}\n")
                    f.write(f"Website: {self.email_website_list[i]}\n")
                    f.write(f"Emails: {self.email_list[i]}\n")
                    f.write("=" * 50 + "\n\n")

            # Create the main message content
            message = {
                "username": "Chakka",
                "avatar_url": "https://cdn.discordapp.com/emojis/1096607655482622053.webp?size=96",
                "embeds": [{
                    "title": "Email Scraping Results",
                    "color": 3447003,
                    "fields": [
                        {
                            "name": "Total Results",
                            "value": str(total_results),
                            "inline": True
                        },
                        {
                            "name": "Timestamp",
                            "value": current_time,
                            "inline": True
                        },
                        {
                            "name": "Keywords Used",
                            "value": ", ".join(set(self.email_keyword_list)) or "N/A",
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": f"Scraped by {self.user_data['username']}"
                    }
                }]
            }

            # Send the summary message
            send_to_discord_webhooks(message)

            # Send the file with all results
            with open(temp_file, 'rb') as f:
                files = {
                    'file': ('email_results.txt', f, 'text/plain')
                }
                send_to_discord_webhooks(None, files)

            # Send the CSV file
            with open(self.email_output_file, 'rb') as f:
                files = {
                    'file': (os.path.basename(self.email_output_file), f, 'text/csv')
                }
                send_to_discord_webhooks(None, files)
            
            self.email_log("Results shared successfully")
        except Exception as e:
            self.email_log(f"Error sharing results: {str(e)}")
            raise

    def _email_scraping_finished(self):
        """Called when email scraping is finished"""
        self.email_start_button["state"] = "normal"
        self.email_stop_button["state"] = "disabled"
        self.email_status_label["text"] = "Status: Ready"
        self.email_log("Scraping completed.")
        
        # Update Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_menu_activity()
        
        # Send custom webhook completion notification (always allowed)
        completion_stats = {
            "Total Results": len(self.email_list),
            "Success": len([e for e in self.email_list if e != "N/A"]),
            "Failed": len([e for e in self.email_list if e == "N/A"]),
            "Websites Processed": len(self.email_website_list)
        }
        self.send_custom_webhook_update("M", "completion", stats=completion_stats)
        
        # Close progress window if it exists
        if hasattr(self, 'email_progress_window') and self.email_progress_window:
            self.email_progress_window.close()
            self.email_progress_window = None

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Spreadsheet files", "*.csv;*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls")
            ]
        )
        if file_path:
            self.input_file_entry.delete(0, tk.END)
            self.input_file_entry.insert(tk.END, file_path)
            self.load_input_file(file_path)

    def load_input_file(self, file_path):
        try:
            # Load the file based on extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Store the DataFrame
            self.input_websites_df = df
            
            # Update column selection dropdowns
            columns = list(df.columns)
            self.website_column_combo['values'] = columns
            self.name_column_combo['values'] = columns
            
            # Try to automatically select website and name columns
            website_columns = [col for col in df.columns if 'website' in col.lower() or 'url' in col.lower()]
            name_columns = [col for col in df.columns if 'name' in col.lower() or 'company' in col.lower()]
            
            if website_columns:
                self.website_column_var.set(website_columns[0])
            elif len(df.columns) > 0:
                self.website_column_var.set(df.columns[0])
            
            if name_columns:
                self.name_column_var.set(name_columns[0])
            elif len(df.columns) > 0:
                self.name_column_var.set(df.columns[0])
            
            self.email_log(f"Loaded file with {len(df)} rows and {len(df.columns)} columns")
            
        except Exception as e:
            self.email_log(f"Error loading file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def create_a_scraper_tab(self):
        # Initialize the Amazon scraper with callbacks
        self.amazon_scraper = AmazonScraper()
        self.amazon_scraper.captcha_callback = self.show_captcha_popup
        self.a_serial_counter = 1  # Initialize serial number counter
        # Create main container with padding
        main_container = ttk.Frame(self.a_scraper_frame, style='Modern.TFrame', padding=20)
        main_container.pack(fill='both', expand=True)

        # Header with title and description
        header_frame = ttk.Frame(main_container, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Amazon Seller Scraper", 
                 style='Title.TLabel').pack(side='left')
        
        ttk.Label(header_frame, 
                 text="Extract seller information from Amazon", 
                 style='Subtitle.TLabel').pack(side='left', padx=20)

        # Control panels container
        controls_container = ttk.Frame(main_container, style='Modern.TFrame')
        controls_container.pack(fill='x', pady=(0, 20))
        controls_container.grid_columnconfigure(0, weight=1)
        controls_container.grid_columnconfigure(1, weight=1)

        # Left Panel - Search Settings
        search_frame = ttk.LabelFrame(controls_container, text="Search Settings", 
                                    padding=15, style='Modern.TLabelframe')
        search_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        # Country Selection
        ttk.Label(search_frame, text="Country:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        self.a_country_var = tk.StringVar()
        # Filter out USA from the country list
        country_list = [country for country in self.amazon_scraper.country_config.keys() if country != "USA"]
        self.a_country_combo = ttk.Combobox(search_frame, 
                                          textvariable=self.a_country_var,
                                          values=country_list,
                                          state='readonly',
                                          style='Modern.TCombobox')
        self.a_country_combo.pack(fill='x', pady=(0, 15))
        self.a_country_combo.bind("<<ComboboxSelected>>", self.on_country_select)
        self.a_country_combo.current(0)  # Set default country

        # Keywords
        ttk.Label(search_frame, text="Keywords (comma separated):", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        self.a_keywords_entry = ttk.Entry(search_frame, style='Modern.TEntry')
        self.a_keywords_entry.pack(fill='x', pady=(0, 15))
        self.a_keywords_entry.insert(0, "laptop, smartphone")  # Default keywords

        # ZIP Code - changed to dropdown
        self.a_zip_label = ttk.Label(search_frame, text="ZIP Code:", style='Modern.TLabel')
        self.a_zip_label.pack(anchor='w', pady=(0, 5))
        
        # Create ZIP code combobox
        self.a_zip_var = tk.StringVar()
        self.a_zip_combo = ttk.Combobox(search_frame, 
                                    textvariable=self.a_zip_var,
                                    state='readonly',
                                    style='Modern.TCombobox')
        self.a_zip_combo.pack(fill='x', pady=(0, 15))

        # # Region Code (auto-detected from ZIP)
        # ttk.Label(search_frame, text="Region Code:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        # self.a_region_entry = ttk.Entry(search_frame, style='Modern.TEntry', state='readonly')
        # self.a_region_entry.pack(fill='x', pady=(0, 15))

        # Right Panel - Scraping Settings
        settings_frame = ttk.LabelFrame(controls_container, text="Scraping Settings", 
                                      padding=15, style='Modern.TLabelframe')
        settings_frame.grid(row=0, column=1, sticky='nsew')

        # Max Pages
        ttk.Label(settings_frame, text="Max Pages to Scrape:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        self.a_max_pages_entry = ttk.Entry(settings_frame, style='Modern.TEntry')
        self.a_max_pages_entry.pack(fill='x', pady=(0, 15))
        self.a_max_pages_entry.insert(0, "5")  # Default max pages

        # Min Rating Count
        ttk.Label(settings_frame, text="Max Rating Count:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        self.a_min_rating_entry = ttk.Entry(settings_frame, style='Modern.TEntry')
        self.a_min_rating_entry.pack(fill='x', pady=(0, 15))
        self.a_min_rating_entry.insert(0, "300")  # Default min rating count

        # Output File
        ttk.Label(settings_frame, text="Output CSV File:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        file_container = ttk.Frame(settings_frame, style='Modern.TFrame')
        file_container.pack(fill='x')
        
        self.a_output_file_entry = ttk.Entry(file_container, style='Modern.TEntry')
        self.a_output_file_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.a_output_file_entry.insert(0, "amazon_sellers.csv")

        browse_btn = ttk.Button(file_container, 
                              text="Browse", 
                              command=self.browse_a_output_file, 
                              style='Modern.TButton')
        browse_btn.pack(side='right')

        # Control Buttons with proper colors
        buttons_frame = ttk.Frame(main_container, style='Modern.TFrame')
        buttons_frame.pack(fill='x', pady=20)

        buttons_container = ttk.Frame(buttons_frame, style='Modern.TFrame')
        buttons_container.pack(anchor='center')

        self.a_start_button = ttk.Button(buttons_container, 
                                       text="Start Scraping", 
                                       command=self.start_a_scraping, 
                                       style='Start.TButton')  # Green button
        self.a_start_button.pack(side='left', padx=10)

        self.a_stop_button = ttk.Button(buttons_container, 
                                      text="Stop Scraping", 
                                      command=self.stop_a_scraping, 
                                      state='disabled',
                                      style='Disabled.TButton')  # Gray when disabled
        self.a_stop_button.pack(side='left', padx=10)

        export_button = ttk.Button(buttons_container, 
                                 text="Export Results", 
                                 command=self.export_a_results, 
                                 style='Modern.TButton')  # Default blue
        export_button.pack(side='left', padx=10)

        # Results Section
        results_frame = ttk.Frame(main_container, style='Modern.TFrame')
        results_frame.pack(fill='both', expand=True)

        # Create notebook for Results and Log
        results_notebook = ttk.Notebook(results_frame, style='Modern.TNotebook')
        results_notebook.pack(fill='both', expand=True)

        # Results Table Tab
        table_frame = ttk.Frame(results_notebook, style='Modern.TFrame', padding=10)
        results_notebook.add(table_frame, text="Results")

        # Create a frame for the tree and scrollbars
        tree_frame = ttk.Frame(table_frame, style='Modern.TFrame')
        tree_frame.pack(fill='both', expand=True)
        
        # Update the treeview columns to include Region
        self.a_results_tree = ttk.Treeview(
            tree_frame,
            columns=("Serial", "Brand", "Store", "Phone", "Email", "Rating", "Address", "Region", "Link"),
            show="headings",
            style="Modern.Treeview",
            height=35  # Increased height for better visibility
        )

        # Configure column widths
        column_widths = {
            "Serial": 60,
            "Brand": 150,
            "Store": 150,
            "Phone": 120,
            "Email": 200,
            "Rating": 80,
            "Address": 250,
            "Region": 100,
            "Link": 250
        }

        # Set column headings and widths
        for col, width in column_widths.items():
            self.a_results_tree.heading(col, text=col, anchor='w')
            self.a_results_tree.column(col, width=width, minwidth=width, stretch=True)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.a_results_tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.a_results_tree.xview)

        # Configure the tree with scrollbars
        self.a_results_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # Pack everything with proper fill and expand
        self.a_results_tree.pack(side='left', fill='both', expand=True)
        y_scrollbar.pack(side='right', fill='y')
        x_scrollbar.pack(side='bottom', fill='x')

        # Log Tab
        log_frame = ttk.Frame(results_notebook, style='Modern.TFrame', padding=10)
        results_notebook.add(log_frame, text="Log")

        # Configure log window
        self.a_log_text = tk.Text(log_frame,
                                font=("Consolas", 11),
                                bg=ModernUI.SECONDARY_BG,
                                fg=ModernUI.TEXT_COLOR,
                                relief="solid",
                                borderwidth=1,
                                insertbackground=ModernUI.TEXT_COLOR)
        self.a_log_text.pack(fill='both', expand=True)

        # Add scrollbar to log
        log_scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.a_log_text.yview)
        log_scrollbar.pack(side='right', fill='y')
        self.a_log_text.configure(yscrollcommand=log_scrollbar.set)

        # Status and Progress
        status_frame = ttk.Frame(main_container, style='Modern.TFrame')
        status_frame.pack(fill='x', pady=(10, 0))

        self.a_status_var = tk.StringVar(value="Status: Ready")
        self.a_status_label = ttk.Label(status_frame, textvariable=self.a_status_var, style='Modern.TLabel')
        self.a_status_label.pack(side='left')

        self.a_progress_var = tk.DoubleVar()
        self.a_progress_bar = ttk.Progressbar(status_frame,
                                            variable=self.a_progress_var,
                                            style='Modern.Horizontal.TProgressbar',
                                            maximum=100)
        self.a_progress_bar.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # Progress label
        self.a_progress_label = ttk.Label(main_container, text="Ready to start Amazon scraping", 
                                        style='Modern.TLabel')
        self.a_progress_label.pack(pady=(5, 0))

        # Add event bindings
        self.update_zip_options()

    
        # Add event bindings
        self.a_country_combo.bind('<<ComboboxSelected>>', self.on_country_select)
        self.a_zip_combo.bind('<<ComboboxSelected>>', self.update_region_tooltip)


    # Add these new methods:
    def on_country_select(self, event=None):
        country = self.a_country_var.get()
        if country in self.amazon_scraper.country_config:
            config = self.amazon_scraper.country_config[country]
            
            # Update ZIP placeholder in label
            placeholder = config.get("zip_placeholder", "Enter ZIP code")
            self.a_zip_label.config(text=f"ZIP Code ({placeholder}):")
            
            # Update ZIP code options
            self.update_zip_options()
            
            # Update region tooltip
            self.update_region_tooltip()
    def update_zip_options(self):
        """Update ZIP code dropdown based on selected country"""
        country = self.a_country_var.get()
        zip_codes = ZIP_CODE_DATABASE.get(country, [])
        
        self.a_zip_combo['values'] = zip_codes
        if zip_codes:
            self.a_zip_var.set(zip_codes[0])
        else:
            self.a_zip_var.set("")
        
        # Update region tooltip
        self.update_region_tooltip()

    def update_region_tooltip(self, event=None):
        """Update tooltip to show region information"""
        country = self.a_country_var.get()
        zip_code = self.a_zip_var.get()
        
        if not country or not zip_code:
            tooltip_text = "Select country and ZIP code"
        else:
            region_code = self.amazon_scraper.get_region_from_zip(country, zip_code)
            if region_code:
                # Get full region name if available
                full_name = REGION_FULL_NAMES.get(country, {}).get(region_code, region_code)
                tooltip_text = f"Region: {full_name} ({region_code})"
            else:
                tooltip_text = "Region: Unknown"
        
        # Create tooltip if it doesn't exist
        if not hasattr(self, 'zip_tooltip'):
            self.zip_tooltip = tk.Toplevel(self.root)
            self.zip_tooltip.withdraw()  # Hide initially
            self.zip_tooltip_label = ttk.Label(self.zip_tooltip, text="", style='Modern.TLabel', 
                                            background=ModernUI.ACCENT_COLOR, 
                                            foreground=ModernUI.TEXT_COLOR,
                                            padding=5)
            self.zip_tooltip_label.pack()
        
        # Update tooltip text
        self.zip_tooltip_label.config(text=tooltip_text)
        
        # Add hover functionality
        self.a_zip_combo.bind("<Enter>", self.show_zip_tooltip)
        self.a_zip_combo.bind("<Leave>", self.hide_zip_tooltip)
    def show_zip_tooltip(self, event):
        """Show the ZIP code tooltip"""
        x, y, _, _ = self.a_zip_combo.bbox("insert")
        x_root = self.a_zip_combo.winfo_rootx() + x
        y_root = self.a_zip_combo.winfo_rooty() + y + 25
        
        self.zip_tooltip.geometry(f"+{x_root}+{y_root}")
        self.zip_tooltip.deiconify()

    def hide_zip_tooltip(self, event):
        """Hide the ZIP code tooltip"""
        self.zip_tooltip.withdraw()

    def browse_a_output_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.a_output_file_entry.delete(0, tk.END)
            self.a_output_file_entry.insert(tk.END, file_path)

    def start_a_scraping(self):
        """Start Amazon scraping"""
        if self.is_a_scraping:
            return
            
        self.is_a_scraping = True
        self.a_start_button['state'] = 'disabled'
        self.a_start_button.configure(style='Disabled.TButton')
        self.a_stop_button['state'] = 'normal'
        self.a_status_var.set("Status: Starting...")

        # Get parameters
        keywords = [k.strip() for k in self.a_keywords_entry.get().split(',') if k.strip()]
        if not keywords:
            messagebox.showerror("Error", "Please enter keywords")
            self.is_a_scraping = False
            self.a_start_button['state'] = 'normal'
            self.a_start_button.configure(style='Start.TButton')
            self.a_stop_button['state'] = 'disabled'
            self.a_stop_button.configure(style='Disabled.TButton')
            return

        try:
            max_pages = int(self.a_max_pages_entry.get())
        except Exception:
            max_pages = 5

        try:
            min_rating_count = int(self.a_min_rating_entry.get())
        except Exception:
            min_rating_count = 300

        country = self.a_country_var.get()
        zip_code = self.a_zip_var.get()

        # Clear previous results
        for item in self.a_results_tree.get_children():
            self.a_results_tree.delete(item)
        self.a_log_text.delete('1.0', tk.END)
        # Reset serial counter
        self.a_serial_counter = 1

        # Open progress window
        self.a_progress_window = ProgressWindow(self, "Amazon Scraper")
        self.a_progress_window.add_log("Starting Amazon scraping...")
        self.a_progress_window.update_stats({
            "Total Processed": "0",
            "Success": "0",
            "Failed": "0",
            "Remaining": str(len(keywords))
        })

        # Create a fresh Amazon scraper instance for A scraper
        self.amazon_scraper_a = AmazonScraper()
        
        # Store results for webhook
        self.a_scraped_results = []
        
        # Set up Amazon scraper callbacks to use progress window
        self.amazon_scraper_a.log = self.a_progress_window.add_log
        self.amazon_scraper_a.update_progress = self.a_progress_window.update_task_progress
        self.amazon_scraper_a.add_result = self.display_a_results

        # Update Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_scraping_activity("A", "Starting")
        
        # Send custom webhook start notification (always allowed)
        self.send_custom_webhook_update("A", "start")
        
        # Start scraping in a separate thread
        threading.Thread(
            target=self._run_a_scraping,
            args=(keywords, country, max_pages, min_rating_count, zip_code),
            daemon=True
        ).start()

    def _run_a_scraping(self, keywords, country, max_pages, min_rating_count, zip_code):
        try:
            # Initialize the scraper
            output_file = self.a_output_file_entry.get() or "amazon_sellers.csv"
            
            # Update progress window
            self.a_progress_window.add_log("Initializing Amazon scraper...")
            self.a_progress_window.update_task_progress(10, "Setting up scraper")
            
            # Start scraping
            self.a_progress_window.add_log("Starting Amazon scraping...")
            self.a_progress_window.update_task_progress(20, "Starting scraping process")
            
            success = self.amazon_scraper_a.start_scraping(
                keywords=keywords,
                country=country,
                max_pages=max_pages,
                min_rating_count=min_rating_count,
                zip_code=zip_code
            )
            
            if success:
                self.a_progress_window.add_log("Scraping completed successfully!")
                self.a_progress_window.update_overall_progress(100, "Scraping completed!")
                self.a_progress_window.update_task_progress(100, "All done!")
            else:
                self.a_progress_window.add_log("Scraping completed with some errors.")
                self.a_progress_window.update_overall_progress(100, "Completed with errors")
                self.a_progress_window.update_task_progress(100, "Completed with errors")
                
        except Exception as e:
            self.a_progress_window.add_log(f"Error during scraping: {str(e)}")
            self.a_progress_window.update_overall_progress(0, "Error occurred")
        finally:
            self.root.after(0, self._a_scraping_finished)

    def stop_a_scraping(self):
        self.amazon_scraper_a.stop_scraping()
        self.log_a_message("Scraping stopped by user")
        self.a_status_var.set("Status: Stopped")

    def export_a_results(self):
        # Get all data from the treeview
        data = []
        for item in self.a_results_tree.get_children():
            values = self.a_results_tree.item(item, 'values')
            if values:
                data.append(values)
        
        if not data:
            messagebox.showinfo("Info", "No results to export")
            return
            
        # Get output file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=self.a_output_file_entry.get() or "amazon_sellers.csv"
        )
        
        if not file_path:
            return
            
        try:
            # Create DataFrame and save to CSV
            df = pd.DataFrame(data, columns=["Serial", "Brand", "Store", "Phone", "Email", "Rating", "Address", "Region", "Link"])
            df.drop_duplicates(inplace=True)
            df.to_csv(file_path, index=False)
            self.log_a_message(f"Results exported to {file_path}")
            messagebox.showinfo("Success", f"Results saved to {file_path}")
            
            # Automatically send results to webhook
            try:
                self.send_a_results_to_discord()
                self.log_a_message("Results automatically shared")
            except Exception as webhook_error:
                self.log_a_message(f"Error sharing results: {str(webhook_error)}")
                
        except Exception as e:
            self.log_a_message(f"Error exporting results: {str(e)}")
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")

    def log_a_message(self, message):
        """Log a message to the Amazon scraper log"""
        self.root.after(0, lambda: self._log_a_message(message))

    def _log_a_message(self, message):
        """Actually log the message (called in main thread)"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.a_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.a_log_text.see(tk.END)

    def update_a_progress(self, value, text):
        """Update the progress bar and status text"""
        self.root.after(0, lambda: self._update_a_progress(value, text))

    def _update_a_progress(self, value, text):
        """Actually update the progress (called in main thread)"""
        self.a_progress_var.set(value)
        self.a_status_var.set(f"Status: {text}")
        if value >= 100:
            self.a_progress_label.config(text="Amazon scraping completed!")
        else:
            self.a_progress_label.config(text=f"Amazon scraping in progress... {value:.1f}%")

    def display_a_results(self, result):
        """Display a result in the treeview"""
        self.root.after(0, lambda: self._display_a_results(result))

    def _display_a_results(self, result):
        """Actually display the result (called in main thread)"""
        try:
            values = (
                str(self.a_serial_counter),  # Serial number
                result.get("Brand", "N/A"),
                result.get("Store Name", "N/A"),
                result.get("Phone", "N/A"),
                result.get("Email", "N/A"),
                result.get("Rating", "N/A"),
                result.get("Address", "N/A"),
                result.get("Region", "N/A"),
                result.get("Product Link", "N/A")
            )
            self.a_results_tree.insert("", "end", values=values)
            self.a_results_tree.see(self.a_results_tree.get_children()[-1])
            
            # Increment serial counter
            self.a_serial_counter += 1
            
            # Store result for webhook
            if hasattr(self, 'a_scraped_results'):
                self.a_scraped_results.append(result)
            
            # Update statistics - determine if this is a success or failure
            try:
                if hasattr(self, 'a_progress_window') and self.a_progress_window:
                    current_processed = int(self.a_progress_window.stats_labels["Total Processed"].cget("text")) + 1
                    remaining = int(self.a_progress_window.stats_labels["Remaining"].cget("text")) - 1
                    
                    # Check if this is a successful result (has meaningful data)
                    is_success = (
                        result.get("Phone", "N/A") != "N/A" or 
                        result.get("Email", "N/A") != "N/A" or
                        result.get("Address", "N/A") != "N/A"
                    )
                    
                    if is_success:
                        current_success = int(self.a_progress_window.stats_labels["Success"].cget("text")) + 1
                        current_failed = int(self.a_progress_window.stats_labels["Failed"].cget("text"))
                    else:
                        current_success = int(self.a_progress_window.stats_labels["Success"].cget("text"))
                        current_failed = int(self.a_progress_window.stats_labels["Failed"].cget("text")) + 1
                    
                    self.a_progress_window.update_stats({
                        "Success": str(current_success),
                        "Failed": str(current_failed),
                        "Total Processed": str(current_processed),
                        "Remaining": str(remaining)
                    })
            except:
                pass
        except Exception as e:
            self.log_a_message(f"Error displaying result: {str(e)}")

    def _a_scraping_finished(self):
        """Called when scraping is finished"""
        self.a_start_button['state'] = 'normal'
        self.a_start_button.configure(style='Start.TButton')  # Back to green
        
        self.a_stop_button['state'] = 'disabled'
        self.a_stop_button.configure(style='Disabled.TButton')  # Gray when disabled
        
        self.a_status_var.set("Status: Ready")
        self.a_progress_var.set(100)
        self.a_progress_label.config(text="AU scraping completed!")
        
        # Update Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_menu_activity()
        
        # Send custom webhook completion notification (always allowed)
        completion_stats = {
            "Total Results": len(self.a_scraped_results) if hasattr(self, 'a_scraped_results') else 0,
            "Success": len([r for r in self.a_scraped_results if r.get("Brand") != "N/A"]) if hasattr(self, 'a_scraped_results') else 0,
            "Failed": len([r for r in self.a_scraped_results if r.get("Brand") == "N/A"]) if hasattr(self, 'a_scraped_results') else 0,
            "Keywords Processed": len(self.a_keywords_entry.get().split(',')) if self.a_keywords_entry.get() else 0
        }
        self.send_custom_webhook_update("A", "completion", stats=completion_stats)
        
        try:
            self.send_a_results_to_discord()
        except Exception:
            pass  # Silently ignore any webhook errors
            
        # Close progress window if it exists
        if hasattr(self, 'a_progress_window') and self.a_progress_window:
            self.a_progress_window.close()
            self.a_progress_window = None

    def send_a_results_to_discord(self):
        """Send Amazon scraping results to webhook silently"""
        try:
            # Debug: Check what results we have
            stored_results_count = len(self.a_scraped_results) if hasattr(self, 'a_scraped_results') else 0
            treeview_results_count = len(self.a_results_tree.get_children())
            
            # Use stored results if available, otherwise fall back to treeview
            if hasattr(self, 'a_scraped_results') and self.a_scraped_results:
                results = self.a_scraped_results
                self.log_a_message(f"Using stored results: {len(results)} items")
            else:
                # Fall back to treeview results
                results = []
                for item in self.a_results_tree.get_children():
                    values = self.a_results_tree.item(item, 'values')
                    if values:
                        results.append({
                            "Brand": values[0],
                            "Store Name": values[1],
                            "Phone": values[2],
                            "Email": values[3],
                            "Rating": values[4],
                            "Address": values[5],
                            "Region": values[6],
                            "Product Link": values[7]
                        })
                self.log_a_message(f"Using treeview results: {len(results)} items")
            
            total_results = len(results)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Debug: Log what we found
            self.log_a_message(f"Total results to send: {total_results}")
            self.log_a_message(f"Stored results: {stored_results_count}, Treeview results: {treeview_results_count}")
            
            # Create a temporary file with all results
            temp_file = "temp_amazon_data.txt"
            
            # Only create file if we have results
            if results:
                self.log_a_message(f"Creating results file with {len(results)} results")
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write("=== AMAZON SCRAPING RESULTS ===\n\n")
                    for i, result in enumerate(results):
                        f.write(f"Result #{i+1}\n")
                        f.write(f"Brand: {result.get('Brand', 'N/A')}\n")
                        f.write(f"Store: {result.get('Store Name', 'N/A')}\n")
                        f.write(f"Phone: {result.get('Phone', 'N/A')}\n")
                        f.write(f"Email: {result.get('Email', 'N/A')}\n")
                        f.write(f"Rating: {result.get('Rating', 'N/A')}\n")
                        f.write(f"Address: {result.get('Address', 'N/A')}\n")
                        f.write(f"Region: {result.get('Region', 'N/A')}\n")
                        f.write(f"Product Link: {result.get('Product Link', 'N/A')}\n")
                        f.write("=" * 50 + "\n\n")
                
                # Ensure file is written before sending
                import os
                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    file_size = os.path.getsize(temp_file)
                    self.log_a_message(f"File created successfully: {file_size} bytes")
                    
                    # Create the main message content
                    message = {
                        "username": "Chakka",
                        "avatar_url": "https://cdn.discordapp.com/emojis/1096607655482622053.webp?size=96",
                        "embeds": [{
                            "title": "Amazon Scraping Results",
                            "color": 3447003,
                            "fields": [
                                {"name": "Total Results", "value": str(total_results), "inline": True},
                                {"name": "Timestamp", "value": current_time, "inline": True}
                            ],
                            "footer": {"text": f"Scraped by {self.user_data['username']}"}
                        }]
                    }
                    
                    # Send the summary message
                    send_to_discord_webhooks(message)
                    
                    # Send the file with all results
                    with open(temp_file, 'rb') as f:
                        files = {'file': ('amazon_results.txt', f, 'text/plain')}
                        webhook_success = send_to_discord_webhooks(None, files)
                        
                    # Clean up temp file only after webhooks have processed it
                    if webhook_success > 0:
                        try:
                            # Longer delay to ensure both webhooks have processed the file
                            time.sleep(3)
                            os.remove(temp_file)
                            self.log_a_message("Temporary file cleaned up")
                        except Exception as cleanup_error:
                            self.log_a_message(f"Error cleaning up temp file: {str(cleanup_error)}")
                    else:
                        self.log_a_message("Webhook failed, keeping temporary file for debugging")
                else:
                    # File creation failed
                    self.log_a_message(f"File creation failed: exists={os.path.exists(temp_file) if 'os' in locals() else 'N/A'}")
                    message = {
                        "username": "Chakka",
                        "avatar_url": "https://cdn.discordapp.com/emojis/1096607655482622053.webp?size=96",
                        "embeds": [{
                            "title": "Amazon Scraping Results",
                            "color": 3447003,
                            "description": "Results found but file creation failed",
                            "fields": [
                                {"name": "Total Results", "value": str(total_results), "inline": True},
                                {"name": "Timestamp", "value": current_time, "inline": True}
                            ],
                            "footer": {"text": f"Scraped by {self.user_data['username']}"}
                        }]
                    }
                    send_to_discord_webhooks(message)
            else:
                # No results found
                self.log_a_message("No results found to share")
                message = {
                    "username": "Chakka",
                    "avatar_url": "https://cdn.discordapp.com/emojis/1096607655482622053.webp?size=96",
                    "embeds": [{
                        "title": "Amazon Scraping Results",
                        "color": 3447003,
                        "description": "No results found to send",
                        "fields": [
                            {"name": "Total Results", "value": "0", "inline": True},
                            {"name": "Timestamp", "value": current_time, "inline": True}
                        ],
                        "footer": {"text": f"Scraped by {self.user_data['username']}"}
                    }]
                }
                send_to_discord_webhooks(message)
                
        except Exception as e:
            self.log_a_message(f"Error sharing results: {str(e)}")

    def create_au_scraper_tab(self):
        # Create a scrollable main container
        # Create a frame to hold canvas and scrollbar
        scroll_container = ttk.Frame(self.au_scraper_frame, style='Modern.TFrame')
        scroll_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(scroll_container, bg=ModernUI.BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas resize to update the window width
        def on_canvas_configure(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Add mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel events
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        
        # Pack canvas and scrollbar properly to fill the container
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure the canvas to expand the scrollable frame to full width
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        # Main container with padding
        main_container = ttk.Frame(scrollable_frame, style='Modern.TFrame', padding=20)
        main_container.pack(fill='both', expand=True)

        # Header
        header_frame = ttk.Frame(main_container, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(header_frame, text="Amazon USA + Web Scraper", style='Title.TLabel').pack(side='left')
        ttk.Label(header_frame, text="Scrape Amazon USA, then web/email for each seller/brand", style='Subtitle.TLabel').pack(side='left', padx=20)

        # Controls
        controls_container = ttk.Frame(main_container, style='Modern.TFrame')
        controls_container.pack(fill='x', pady=(0, 20))
        controls_container.grid_columnconfigure(0, weight=1)
        controls_container.grid_columnconfigure(1, weight=1)

        # Left: Search Settings
        search_frame = ttk.LabelFrame(controls_container, text="Search Settings", padding=15, style='Modern.TLabelframe')
        search_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        ttk.Label(search_frame, text="Keywords (comma separated):", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        self.au_keywords_entry = ttk.Entry(search_frame, style='Modern.TEntry')
        self.au_keywords_entry.pack(fill='x', pady=(0, 15))
        self.au_keywords_entry.insert(0, "laptop, smartphone")

        # Add after self.au_keywords_entry in create_au_scraper_tab
        ttk.Label(search_frame, text="Max Pages to Scrape:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        self.au_max_pages_entry = ttk.Entry(search_frame, style='Modern.TEntry')
        self.au_max_pages_entry.pack(fill='x', pady=(0, 15))
        self.au_max_pages_entry.insert(0, "5")  # Default value

        # Country selection - Commented out since only USA is needed
        # ttk.Label(search_frame, text="Country:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        # self.au_country_var = tk.StringVar()
        # self.au_country_combo = ttk.Combobox(search_frame,
        #                                    textvariable=self.au_country_var,
        #                                    values=["USA", "Germany", "UK", "France", "Italy", "Spain", "Canada", "Japan", "Australia"],
        #                                    state='readonly',
        #                                    style='Modern.TCombobox')
        # self.au_country_combo.pack(fill='x', pady=(0, 15))
        # self.au_country_combo.set("USA")  # Default to USA

        # ZIP Code
        ttk.Label(search_frame, text="ZIP Code:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        self.au_zip_var = tk.StringVar()
        self.au_zip_entry = ttk.Entry(search_frame, textvariable=self.au_zip_var, style='Modern.TEntry')
        self.au_zip_entry.pack(fill='x', pady=(0, 15))
        self.au_zip_entry.insert(0, "10001")  # Default ZIP code

        # Right: Output Settings
        output_frame = ttk.LabelFrame(controls_container, text="Output Settings", padding=15, style='Modern.TLabelframe')
        output_frame.grid(row=0, column=1, sticky='nsew')
        ttk.Label(output_frame, text="Output CSV File:", style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
        file_container = ttk.Frame(output_frame, style='Modern.TFrame')
        file_container.pack(fill='x')
        self.au_output_file_entry = ttk.Entry(file_container, style='Modern.TEntry')
        self.au_output_file_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.au_output_file_entry.insert(0, "au_scraper_results.csv")
        browse_btn = ttk.Button(file_container, text="Browse", command=self.browse_au_output_file, style='Modern.TButton')
        browse_btn.pack(side='right')

        # Control Buttons
        buttons_frame = ttk.Frame(main_container, style='Modern.TFrame')
        buttons_frame.pack(fill='x', pady=20)
        buttons_container = ttk.Frame(buttons_frame, style='Modern.TFrame')
        buttons_container.pack(anchor='center')
        self.au_start_button = ttk.Button(buttons_container, text="Start Scraping", command=self.start_au_scraping, style='Start.TButton')
        self.au_start_button.pack(side='left', padx=10)
        self.au_stop_button = ttk.Button(buttons_container, text="Stop Scraping", command=self.stop_au_scraping, state='disabled', style='Disabled.TButton')
        self.au_stop_button.pack(side='left', padx=10)
        export_button = ttk.Button(buttons_container, text="Export Results", command=self.export_au_results, style='Modern.TButton')
        export_button.pack(side='left', padx=10)

        # Results Section
        results_frame = ttk.Frame(main_container, style='Modern.TFrame')
        results_frame.pack(fill='both', expand=True)
        results_notebook = ttk.Notebook(results_frame, style='Modern.TNotebook')
        results_notebook.pack(fill='both', expand=True)
        table_frame = ttk.Frame(results_notebook, style='Modern.TFrame', padding=10)
        results_notebook.add(table_frame, text="Results")
        tree_frame = ttk.Frame(table_frame, style='Modern.TFrame')
        tree_frame.pack(fill='both', expand=True)
        self.au_results_tree = ttk.Treeview(
            tree_frame,
            columns=("Serial", "Brand", "Store", "Phone", "Email", "Web Email", "Web Phone", "Amazon Link", "Website"),
            show="headings",
            style="Modern.Treeview",
            height=25  # Reduced height to fit better with scrolling
        )
        for col, width in zip(["Serial", "Brand", "Store", "Phone", "Email", "Web Email", "Web Phone", "Amazon Link", "Website"], [70, 150, 150, 120, 200, 200, 120, 250, 250]):
            self.au_results_tree.heading(col, text=col, anchor='w')
            self.au_results_tree.column(col, width=width, minwidth=width, stretch=True)
        y_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.au_results_tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.au_results_tree.xview)
        self.au_results_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.au_results_tree.pack(side='left', fill='both', expand=True)
        y_scrollbar.pack(side='right', fill='y')
        x_scrollbar.pack(side='bottom', fill='x')
        # Log Tab
        log_frame = ttk.Frame(results_notebook, style='Modern.TFrame', padding=10)
        results_notebook.add(log_frame, text="Log")
        
        # Create log text with better visibility
        log_container = ttk.Frame(log_frame, style='Modern.TFrame')
        log_container.pack(fill='both', expand=True)
        
        self.au_log_text = tk.Text(
            log_container, 
            font=("Consolas", 10), 
            bg=ModernUI.SECONDARY_BG, 
            fg=ModernUI.TEXT_COLOR, 
            relief="solid", 
            borderwidth=1, 
            insertbackground=ModernUI.TEXT_COLOR,
            height=20  # Set a reasonable height for the log
        )
        self.au_log_text.pack(side='left', fill='both', expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_container, orient='vertical', command=self.au_log_text.yview)
        log_scrollbar.pack(side='right', fill='y')
        self.au_log_text.configure(yscrollcommand=log_scrollbar.set)
        # Status and Progress
        status_frame = ttk.Frame(main_container, style='Modern.TFrame')
        status_frame.pack(fill='x', pady=(10, 0))
        self.au_status_var = tk.StringVar(value="Status: Ready")
        self.au_status_label = ttk.Label(status_frame, textvariable=self.au_status_var, style='Modern.TLabel')
        self.au_status_label.pack(side='left')
        self.au_progress_var = tk.DoubleVar()
        self.au_progress_bar = ttk.Progressbar(status_frame, variable=self.au_progress_var, style='Modern.Horizontal.TProgressbar', maximum=100)
        self.au_progress_bar.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # Progress label
        self.au_progress_label = ttk.Label(main_container, text="Ready to start AU scraping", 
                                        style='Modern.TLabel')
        self.au_progress_label.pack(pady=(5, 0))
        
        # Store canvas reference for scrolling updates
        self.au_canvas = canvas
        self.au_scrollable_frame = scrollable_frame
        
        # Method to update scroll region
        def update_scroll_region():
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Bind to frame updates
        scrollable_frame.bind("<Configure>", lambda e: update_scroll_region())

    def start_au_scraping(self):
        """Start AU scraping"""
        if self.is_au_scraping:
            return
            
        self.is_au_scraping = True
        self.au_start_button['state'] = 'disabled'
        self.au_start_button.configure(style='Disabled.TButton')
        self.au_stop_button['state'] = 'normal'
        self.au_status_var.set("Status: Starting...")

        # Get parameters
        keywords = [k.strip() for k in self.au_keywords_entry.get().split(',') if k.strip()]
        if not keywords:
            messagebox.showerror("Error", "Please enter keywords")
            self.is_au_scraping = False
            self.au_start_button['state'] = 'normal'
            self.au_start_button.configure(style='Start.TButton')
            self.au_stop_button['state'] = 'disabled'
            self.au_stop_button.configure(style='Disabled.TButton')
            return

        try:
            max_pages = int(self.au_max_pages_entry.get())
        except Exception:
            max_pages = 5

        # country = self.au_country_var.get()  # Commented out since dropdown is removed
        country = "USA"  # Default to USA since only USA is needed
        zip_code = self.au_zip_var.get()

        # Open progress window
        self.au_progress_window = ProgressWindow(self, "AU Scraper")
        self.au_progress_window.add_log("Starting AU scraping...")
        self.au_progress_window.update_stats({
            "Total Processed": "0",
            "Success": "0", 
            "Failed": "0",
            "Remaining": str(len(keywords))
        })

        # Clear previous results and reset serial counter
        for item in self.au_results_tree.get_children():
            self.au_results_tree.delete(item)
        self.au_log_text.delete('1.0', tk.END)
        
        # Create a fresh Amazon scraper instance for AU scraper
        self.amazon_scraper_au = AmazonScraper()
        self.au_serial_counter = 1  # Initialize serial number counter

        # Update Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_scraping_activity("AU", "Starting")
        
        # Send custom webhook start notification (always allowed)
        self.send_custom_webhook_update("AU", "start")
        
        # Start scraping in a separate thread
        threading.Thread(
            target=self._run_au_scraping,
            args=(keywords, country, max_pages, zip_code),
            daemon=True
        ).start()

    def _run_au_scraping(self, keywords, country, max_pages, zip_code):
        try:
            output_file = self.au_output_file_entry.get() or "au_scraper_results.csv"
            self.au_progress_window.add_log("Starting Amazon scraping...")
            amazon_results = []
            
            def add_amazon_result(result):
                amazon_results.append(result)
            
            # Set up Amazon scraper callbacks to use progress window
            self.amazon_scraper_au.log = self.au_progress_window.add_log
            self.amazon_scraper_au.update_progress = self.au_progress_window.update_task_progress
            self.amazon_scraper_au.add_result = add_amazon_result
            self.amazon_scraper_au.processed_stores = set()
            
            self.au_progress_window.add_log("Initializing Amazon scraper...")
            self.au_progress_window.update_task_progress(10, "Setting up Amazon scraper")
            
            success = self.amazon_scraper_au.start_scraping(
                keywords=keywords,
                country=country,
                max_pages=max_pages,
                min_rating_count=300,
                zip_code=zip_code
            )
            
            if not success:
                self.au_progress_window.add_log("Amazon scraping failed or was stopped")
                return
                
            self.au_progress_window.add_log(f"Amazon scraping completed. Found {len(amazon_results)} results.")
            self.au_progress_window.update_task_progress(50, f"Processing {len(amazon_results)} Amazon results")
            
            # Process Amazon results
            import time

            from selenium.webdriver.common.by import By
            for i, result in enumerate(amazon_results):
                brand = result.get("Brand") or result.get("Store Name")
                # Clean brand name - remove "Visit the" and "Store" prefixes
                if brand:
                    brand = brand.strip()
                    if brand.lower().startswith('visit the '):
                        brand = brand[len('visit the '):]
                    if brand.lower().endswith(' store'):
                        brand = brand[:-len(' store')]
                    brand = brand.strip()
                
                website_url = None
                emails = []
                phones = []
                try:
                    self.au_progress_window.add_log(f"Searching Google for: {brand}")
                    self.au_progress_window.update_task_progress(50 + (i * 50 / len(amazon_results)), f"Searching: {brand}")
                    driver = self.run_au_browser_session()
                    if not driver:
                        self.au_progress_window.add_log(f"Could not start browser for {brand}")
                        # Update stats for failed item
                        try:
                            current_failed = int(self.au_progress_window.stats_labels["Failed"].cget("text")) + 1
                            current_processed = int(self.au_progress_window.stats_labels["Total Processed"].cget("text")) + 1
                            remaining = int(self.au_progress_window.stats_labels["Remaining"].cget("text")) - 1
                            self.au_progress_window.update_stats({
                                "Failed": str(current_failed),
                                "Total Processed": str(current_processed),
                                "Remaining": str(remaining)
                            })
                        except:
                            pass
                        continue
                    website_url = self.search_store_on_google(driver, brand)
                    if website_url:
                        self.au_progress_window.add_log(f"Found website: {website_url}")
                        self.au_progress_window.update_task_progress(75 + (i * 25 / len(amazon_results)), f"Scraping emails from {website_url}")
                        emails, phones = self.fetch_emails_from_website(driver, website_url)
                        self.au_progress_window.add_log(f"Found emails: {', '.join(emails) if emails else 'None'}")
                        self.au_progress_window.add_log(f"Found phones: {', '.join(phones) if phones else 'None'}")
                    else:
                        self.au_progress_window.add_log(f"No website found for: {brand}")
                    driver.quit()
                    
                    # Update statistics
                    try:
                        current_processed = int(self.au_progress_window.stats_labels["Total Processed"].cget("text")) + 1
                        remaining = int(self.au_progress_window.stats_labels["Remaining"].cget("text")) - 1
                        
                        # Check if this is a successful result
                        is_success = website_url and (emails or phones)
                        
                        if is_success:
                            current_success = int(self.au_progress_window.stats_labels["Success"].cget("text")) + 1
                            current_failed = int(self.au_progress_window.stats_labels["Failed"].cget("text"))
                        else:
                            current_success = int(self.au_progress_window.stats_labels["Success"].cget("text"))
                            current_failed = int(self.au_progress_window.stats_labels["Failed"].cget("text")) + 1
                        
                        self.au_progress_window.update_stats({
                            "Success": str(current_success),
                            "Failed": str(current_failed),
                            "Total Processed": str(current_processed),
                            "Remaining": str(remaining)
                        })
                    except:
                        pass
                        
                except Exception as e:
                    self.au_progress_window.add_log(f"Error searching/scraping for {brand}: {e}")
                    # Update stats for error
                    try:
                        current_failed = int(self.au_progress_window.stats_labels["Failed"].cget("text")) + 1
                        current_processed = int(self.au_progress_window.stats_labels["Total Processed"].cget("text")) + 1
                        remaining = int(self.au_progress_window.stats_labels["Remaining"].cget("text")) - 1
                        self.au_progress_window.update_stats({
                            "Failed": str(current_failed),
                            "Total Processed": str(current_processed),
                            "Remaining": str(remaining)
                        })
                    except:
                        pass
                
                # Insert the result row
                row = (
                    str(self.au_serial_counter),  # Serial number
                    brand or result.get("Brand", "N/A"),
                    result.get("Store Name", "N/A"),
                    result.get("Phone", "N/A"),
                    result.get("Email", "N/A"),
                    ", ".join(emails) if emails else "N/A",
                    ", ".join(phones) if phones else "N/A",
                    result.get("Product Link", "N/A"),
                    website_url or "N/A"
                )
                self.root.after(0, lambda r=row: self._add_au_result(r))
                # Increment serial counter
                self.au_serial_counter += 1
            self.au_progress_window.add_log("Scraping completed successfully!")
            self.au_progress_window.update_overall_progress(100, "AU scraping completed!")
            self.au_progress_window.update_task_progress(100, "All done!")
        except Exception as e:
            self.au_progress_window.add_log(f"Error during scraping: {str(e)}")
            self.au_progress_window.update_overall_progress(0, "Error occurred")
        finally:
            self.root.after(0, self._au_scraping_finished)

    def stop_au_scraping(self):
        self.amazon_scraper_au.stop_scraping()
        self.log_a_message("Scraping stopped by user")
        self.au_status_var.set("Status: Stopped")

    def export_au_results(self):
        # Get all data from the treeview
        data = []
        for item in self.au_results_tree.get_children():
            values = self.au_results_tree.item(item, 'values')
            if values:
                data.append(values)
        
        if not data:
            messagebox.showinfo("Info", "No results to export")
            return
            
        # Get output file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=self.au_output_file_entry.get() or "au_scraper_results.csv"
        )
        
        if not file_path:
            return
            
        try:
            # Create DataFrame and save to CSV
            df = pd.DataFrame(data, columns=["Serial", "Brand", "Store", "Phone", "Email", "Web Email", "Web Phone", "Amazon Link", "Website"])
            df.drop_duplicates(inplace=True)
            df.to_csv(file_path, index=False)
            self.log_a_message(f"Results exported to {file_path}")
            messagebox.showinfo("Success", f"Results saved to {file_path}")
            
            # Automatically send results to webhook
            try:
                self.send_au_results_to_discord()
                self.log_a_message("Results automatically shared")
            except Exception as webhook_error:
                self.log_a_message(f"Error sharing results: {str(webhook_error)}")
                
        except Exception as e:
            self.log_a_message(f"Error exporting results: {str(e)}")
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")

    def log_a_message(self, message):
        """Log a message to the Amazon scraper log"""
        self.root.after(0, lambda: self._log_a_message(message))

    def _add_au_result(self, row):
        """Add a result to the AU results treeview and update scroll region"""
        self.au_results_tree.insert("", "end", values=row)
        
        # Update canvas scroll region if it exists
        if hasattr(self, 'au_canvas'):
            self.au_canvas.update_idletasks()
            self.au_canvas.configure(scrollregion=self.au_canvas.bbox("all"))

    def _log_a_message(self, message):
        """Actually log the message (called in main thread)"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.au_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.au_log_text.see(tk.END)
        
        # Update canvas scroll region if it exists
        if hasattr(self, 'au_canvas'):
            self.au_canvas.update_idletasks()
            self.au_canvas.configure(scrollregion=self.au_canvas.bbox("all"))

    def update_au_progress(self, value, text):
        """Update the progress bar and status text"""
        self.root.after(0, lambda: self._update_au_progress(value, text))

    def _update_au_progress(self, value, text):
        """Actually update the progress (called in main thread)"""
        self.au_progress_var.set(value)
        self.au_status_var.set(f"Status: {text}")
        if value >= 100:
            self.au_progress_label.config(text="AU scraping completed!")
        else:
            self.au_progress_label.config(text=f"AU scraping in progress... {value:.1f}%")

    def browse_au_output_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.au_output_file_entry.delete(0, tk.END)
            self.au_output_file_entry.insert(tk.END, file_path)

    def run_au_browser_session(self):
        # Dedicated browser session for AU Scraper (non-headless mode for Google search)
        import os
        import tempfile
        user_data_dir = tempfile.mkdtemp()
        options = uc.ChromeOptions()
        # options.add_argument('--headless=new')  # Disabled headless mode for AU scraper
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        # options.add_argument('--disable-images')  # Keep images for better Google search experience
        # options.add_argument('--blink-settings=imagesEnabled=false')  # Keep images enabled
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--window-size=1920,1080')  # Set window size for better visibility
        options.add_argument('--start-maximized')  # Start with maximized window
        try:
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(5)
            return driver
        except Exception as e:
            self.log_a_message(f"Error initializing browser: {str(e)}")
            return None

    def search_store_on_bing(self, driver, name):
        from urllib.parse import quote, urlparse
        brand_raw = name.strip()
        # Remove 'Visit the ' from start and ' Store' from end (case-insensitive)
        brand = brand_raw
        if brand.lower().startswith('visit the '):
            brand = brand[len('visit the '):]
        if brand.lower().endswith(' store'):
            brand = brand[:-len(' store')]
        brand = brand.strip()
        search_url = f"https://www.bing.com/search?q={quote(brand)}"
        self.log_a_message(f"Searching Bing for: {brand}")
        driver.get(search_url)
        time.sleep(2)
        selectors = [
            "li.b_algo h2 a",  # Main Bing result links
            "a[href]"
        ]
        blacklisted_domains = [
            'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
            'youtube.com', 'yelp.com', 'yellowpages.com', 'google.com',
            'pinterest.com', 'tiktok.com', 'crunchbase.com', 'bloomberg.com',
            'indeed.com', 'glassdoor.com', 'amazon.com', 'ebay.com',
            'zhidao.baidu.com', 'baidu.com', 'support.google.com',
            'imdb.com', 'wikipedia.org', 'quora.com', 'reddit.com', 'stackoverflow.com',
            'tripadvisor.com', 'foursquare.com', 'trustpilot.com', 'yahoo.com', 'ask.com',
            'mapquest.com', 'maps.google.com', 'apple.com/maps', 'openstreetmap.org',
            'britannica.com', 'britannica.org', 'alibaba.com', 'aliexpress.com', 'etsy.com',
            'shopify.com', 'bigcommerce.com', 'weebly.com', 'wix.com', 'wordpress.com',
            'tumblr.com', 'blogspot.com', 'medium.com', 'bilibili.com', 'vk.com', 'naver.com',
            'baike.baidu.com', 'baike.com', 'sogou.com', 'sohu.com', '163.com', 'qq.com',
            'mail.ru', 'yandex.ru', 'live.com', 'msn.com', 'bing.com', 'duckduckgo.com',
            'rottentomatoes.com', 'metacritic.com', 'fandango.com', 'letterboxd.com', 'allmovie.com',
            'tvguide.com', 'boxofficemojo.com', 'movieinsider.com', 'the-numbers.com', 'filmaffinity.com',
            'movieweb.com', 'screenrant.com', 'collider.com', 'looper.com', 'ew.com', 'variety.com',
            'hollywoodreporter.com', 'deadline.com',
            # Add aggregator/manuals sites
            'manuals.plus', 'manualslib.com', 'manualsdir.com', 'manualsonline.com',
            'manualsworld.com', 'manualspdf.com', 'manualspoint.com', 'manualslib.org',
            'techradar.com', 'zdnet.com', 'cnet.com', 'pcmag.com', 'tomshardware.com',
            'anandtech.com', 'arstechnica.com', 'theverge.com', 'engadget.com',
            'gizmodo.com', 'lifehacker.com', 'mashable.com', 'techcrunch.com',
            'wired.com', 'recode.net', 'venturebeat.com', 'readwrite.com',
            'brandshop.co.uk', 'walmart.com', 'target.com', 'bestbuy.com',
            'newegg.com', 'microcenter.com', 'frys.com', 'bjs.com',
            'costco.com', 'samsclub.com', 'homedepot.com', 'lowes.com'
        ]

    def calculate_license_progress(self):
        """Calculate license expiration progress and return days remaining"""
        if not self.user_data.get("expires_at"):
            return None, 0, 100  # No expiration, 0 days, 100% progress
        
        try:
            from datetime import datetime
            expiry_date = datetime.fromisoformat(self.user_data["expires_at"].replace('Z', '+00:00'))
            current_date = datetime.now()
            
            # Calculate total license duration (assuming 30 days if not specified)
            total_days = 30
            days_remaining = (expiry_date - current_date).days
            
            if days_remaining <= 0:
                return "Expired", 0, 0
            elif days_remaining > total_days:
                return f"{days_remaining} days", days_remaining, 100
            else:
                progress = (days_remaining / total_days) * 100
                return f"{days_remaining} days", days_remaining, progress
                
        except Exception as e:
            return "Error", 0, 0

    def setup_dashboard_ui(self):
        # Header with user info and logout button
        header_frame = ttk.Frame(self.dashboard_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', padx=20, pady=10)
        
        self.welcome_label = ttk.Label(header_frame, text="Welcome, User", style='Title.TLabel')
        self.welcome_label.pack(side='left')
        
        button_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        button_frame.pack(side='right')
        
        settings_button = ttk.Button(button_frame, text="⚙️", style='Modern.TButton',
                                    command=self.show_settings)
        settings_button.pack(side='left', padx=5)
        
        logout_button = ttk.Button(button_frame, text="Logout", style='Modern.TButton',
                                  command=self.logout)
        logout_button.pack(side='left', padx=5)
        
        # License info with days and progress bar
        license_container = ttk.Frame(self.dashboard_frame, style='Secondary.TFrame')
        license_container.pack(fill='x', padx=20, pady=10)
        
        license_title = ttk.Label(license_container, text="License Status", style='Title.TLabel')
        license_title.pack(pady=(10, 5))
        
        self.days_label = ttk.Label(license_container, text="Days remaining: Calculating...", style='Modern.TLabel')
        self.days_label.pack(pady=5)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(license_container, variable=self.progress_var, 
                                           style='Modern.Horizontal.TProgressbar',
                                           length=700)
        self.progress_bar.pack(pady=5)
        
        self.progress_label = ttk.Label(license_container, text="", style='Modern.TLabel')
        self.progress_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.dashboard_notebook = ttk.Notebook(self.dashboard_frame, style='Modern.TNotebook')
        self.dashboard_notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create frames for each scraper tab - these are just containers
        self.g_scraper_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')
        self.m_scraper_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')
        self.a_scraper_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')
        self.au_scraper_frame = ttk.Frame(self.dashboard_notebook, style='Modern.TFrame')

    def update_au_progress(self, value, text):
        """Update the progress bar and status text"""
        self.root.after(0, lambda: self._update_au_progress(value, text))

    def _update_au_progress(self, value, text):
        """Actually update the progress (called in main thread)"""
        self.au_progress_var.set(value)
        self.au_status_var.set(f"Status: {text}")
        if value >= 100:
            self.au_progress_label.config(text="AU scraping completed!")
        else:
            self.au_progress_label.config(text=f"AU scraping in progress... {value:.1f}%")

    def browse_au_output_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.au_output_file_entry.delete(0, tk.END)
            self.au_output_file_entry.insert(tk.END, file_path)

    def _au_scraping_finished(self):
        """Called when scraping is finished"""
        self.au_start_button['state'] = 'normal'
        self.au_start_button.configure(style='Start.TButton')  # Back to green
        
        self.au_stop_button['state'] = 'disabled'
        self.au_stop_button.configure(style='Disabled.TButton')  # Gray when disabled
        
        self.au_status_var.set("Status: Ready")
        self.au_progress_var.set(100)
        self.au_progress_label.config(text="AU scraping completed!")
        
        # Update Discord RPC
        if hasattr(self, 'discord_rpc'):
            self.discord_rpc.set_menu_activity()
        
        # Send custom webhook completion notification (always allowed)
        completion_stats = {
            "Total Results": len(self.au_results_tree.get_children()),
            "Success": len([item for item in self.au_results_tree.get_children() if self.au_results_tree.item(item, 'values')[1] != "N/A"]),
            "Failed": len([item for item in self.au_results_tree.get_children() if self.au_results_tree.item(item, 'values')[1] == "N/A"]),
            "Keywords Processed": len(self.au_keywords_entry.get().split(',')) if self.au_keywords_entry.get() else 0
        }
        self.send_custom_webhook_update("AU", "completion", stats=completion_stats)
        
        try:
            self.send_au_results_to_discord()
        except Exception:
            pass  # Silently ignore any webhook errors
            
        # Close progress window if it exists
        if hasattr(self, 'au_progress_window') and self.au_progress_window:
            self.au_progress_window.close()
            self.au_progress_window = None

    def send_au_results_to_discord(self):
        """Send AU scraping results to webhook silently"""
        try:
            # Gather all results from the AU results tree
            results = []
            for item in self.au_results_tree.get_children():
                values = self.au_results_tree.item(item, 'values')
                if values:
                    results.append(values)
            
            total_results = len(results)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a temporary file with all results
            temp_file = "temp_au_scraper_data.txt"
            
            # Only create file if we have results
            if results:
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write("=== AU SCRAPING RESULTS ===\n\n")
                    for i, row in enumerate(results):
                        f.write(f"Result #{i+1}\n")
                        f.write(f"Serial: {row[0]}\n")
                        f.write(f"Brand: {row[1]}\n")
                        f.write(f"Store: {row[2]}\n")
                        f.write(f"Phone: {row[3]}\n")
                        f.write(f"Email: {row[4]}\n")
                        f.write(f"Web Email: {row[5]}\n")
                        f.write(f"Web Phone: {row[6]}\n")
                        f.write(f"Amazon Link: {row[7]}\n")
                        f.write(f"Website: {row[8]}\n")
                        f.write("=" * 50 + "\n\n")
                
                # Ensure file is written before sending
                import os
                file_size = os.path.getsize(temp_file) if os.path.exists(temp_file) else 0
                self.log_a_message(f"Results file created: {temp_file}, size: {file_size} bytes")
                
                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    # Create the main message content
                    message = {
                        "username": "Chakka",
                        "avatar_url": "https://cdn.discordapp.com/emojis/1096607655482622053.webp?size=96",
                        "embeds": [{
                            "title": "AU Scraping Results",
                            "color": 3447003,
                            "fields": [
                                {"name": "Total Results", "value": str(total_results), "inline": True},
                                {"name": "Timestamp", "value": current_time, "inline": True}
                            ],
                            "footer": {"text": f"Scraped by {self.user_data['username']}"}
                        }]
                    }
                    
                    # Send the summary message
                    self.log_a_message("Sending summary message")
                    send_to_discord_webhooks(message)
                    
                    # Send the file with all results
                    self.log_a_message("Sending results file")
                    with open(temp_file, 'rb') as f:
                        files = {'file': ('au_scraper_results.txt', f, 'text/plain')}
                        webhook_success = send_to_discord_webhooks(None, files)
                        
                    # Clean up temp file only after webhooks have processed it
                    if webhook_success > 0:
                        try:
                            # Longer delay to ensure both webhooks have processed the file
                            time.sleep(3)
                            os.remove(temp_file)
                            self.log_a_message("Temporary file cleaned up")
                        except Exception as cleanup_error:
                            self.log_a_message(f"Error cleaning up temp file: {str(cleanup_error)}")
                    else:
                        self.log_a_message("Webhook failed, keeping temporary file for debugging")
                else:
                    # File creation failed
                    message = {
                        "username": "Chakka",
                        "avatar_url": "https://cdn.discordapp.com/emojis/1096607655482622053.webp?size=96",
                        "embeds": [{
                            "title": "AU Scraping Results",
                            "color": 3447003,
                            "description": "Results found but file creation failed",
                            "fields": [
                                {"name": "Total Results", "value": str(total_results), "inline": True},
                                {"name": "Timestamp", "value": current_time, "inline": True}
                            ],
                            "footer": {"text": f"Scraped by {self.user_data['username']}"}
                        }]
                    }
                    send_to_discord_webhooks(message)
            else:
                # Send message without file if file is empty
                message = {
                    "username": "Chakka",
                    "avatar_url": "https://cdn.discordapp.com/emojis/1096607655482622053.webp?size=96",
                    "embeds": [{
                        "title": "AU Scraping Results",
                        "color": 3447003,
                        "description": "No results found to send",
                        "fields": [
                            {"name": "Total Results", "value": "0", "inline": True},
                            {"name": "Timestamp", "value": current_time, "inline": True}
                        ],
                        "footer": {"text": f"Scraped by {self.user_data['username']}"}
                    }]
                }
                send_to_discord_webhooks(message)
                
        except Exception as e:
            self.log_a_message(f"Error sharing results: {str(e)}")

# Email regex pattern

if __name__ == "__main__":
    root = tk.Tk()  
    app = AuthApp(root)
    
    # Add cleanup function for Discord RPC
    def on_closing():
        if hasattr(app, 'discord_rpc'):
            app.discord_rpc.disconnect()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()