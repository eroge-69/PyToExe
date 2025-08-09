#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hypixel SkyBlock RNG & Slayer Calculator (Tkinter)
Version: v4.6.2 (2025-08-09)

This build restores and improves the price fallback chain and adds item labels:

- Rates / Profit table now shows an **Item** column so you can see which row is which.
- Unified price fallback for every drop:
  Cofl BIN → Cofl SOLD → Hypixel Bazaar (sell) → skyblock.bz Instasell → alert.
  (If no explicit Bazaar ID for an item, we auto-derive one from the item name, e.g.
   'Subzero Inverter' → 'SUBZERO_INVERTER'.)
- Clear debug messages when we fall back (e.g. "No AH price for Subzero Inverter…").
- After Refresh Prices, a popup lists any items we couldn't resolve.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import threading, math, webbrowser, re, time, random, statistics

try:
    import requests
except ImportError:
    requests = None

APP_TITLE = "Hypixel SkyBlock RNG & Slayer Calculator"
APP_VERSION = "v4.6.2"
APP_WIDTH = 1320
APP_HEIGHT = 900

# -------------------------------
# Utility
# -------------------------------

def percent_to_float(pct):
    try:
        return float(str(pct).replace(',', ''))
    except Exception:
        return 0.0

def one_in_to_percent(one_in_str):
    try:
        denom = float(str(one_in_str).replace(",", ""))
        if denom <= 0: return 0.0
        return 100.0 / denom
    except Exception:
        return 0.0

def effective_drop_chance(base_percent, magic_find=0.0, is_pet=False, pet_luck=0.0):
    base = float(base_percent)
    mf = float(magic_find)
    pl = float(pet_luck)
    if is_pet:
        return base * (1.0 + mf/100.0) * (1.0 + pl/100.0)
    if base < 5.0:
        return base * (1.0 + mf/100.0)
    return base

def kills_for_probability(p_drop_percent, target_prob_percent):
    p = max(min(p_drop_percent / 100.0, 0.999999), 1e-12)
    target = max(min(target_prob_percent / 100.0, 0.999999), 1e-12)
    n = math.log(1.0 - target) / math.log(1.0 - p)
    return max(1.0, n)

def fmt_num(n):
    try:
        n = float(n)
        if n >= 1e9: return f"{n/1e9:.2f}B"
        if n >= 1e6: return f"{n/1e6:.2f}M"
        if n >= 1e3: return f"{n/1e3:.2f}k"
        if n.is_integer(): return f"{int(n)}"
        return f"{n:.2f}"
    except Exception:
        return str(n)

def cofl_tag_sanitize(tag):
    return str(tag).replace(" ", "").upper()

def default_bz_id_from_name(name: str) -> str:
    return re.sub(r'[^A-Z0-9]+', '_', str(name).upper()).strip('_')

# -------------------------------
# Presets (RNGesus/extreme rares already present)
# -------------------------------

RARE_DROPS = {
    "Revenant Horror": [
        {"item":"Warden Heart", "tier":"V", "base_pct": 100.0/7246.38, "one_in": 7246.38, "cofl_tag":"WARDEN_HEART", "source":"https://wiki.hypixel.net/Warden_Heart"},
        {"item":"Shard Of The Shredded", "tier":"V", "base_pct": 100.0/1814.88, "one_in": 1814.88, "cofl_tag":"SHARD_OF_THE_SHREDDED", "source":"https://wiki.hypixel.net/Shard_Of_The_Shredded"},
        {"item":"Scythe Blade", "tier":"V", "base_pct": 100.0/968.05, "one_in": 968.05, "cofl_tag":"SCYTHE_BLADE", "source":"https://wiki.hypixel.net/Scythe_Blade"},
        {"item":"Scythe Blade", "tier":"IV", "base_pct": 100.0/1761.0, "one_in": 1761.0, "cofl_tag":"SCYTHE_BLADE", "source":"https://wiki.hypixel.net/Scythe_Blade"},
    ],
    "Tarantula Broodfather": [
        {"item":"Digested Mosquito", "tier":"IV", "base_pct": 100.0/1718.14, "one_in": 1718.14, "cofl_tag":"DIGESTED_MOSQUITO", "source":"https://wiki.hypixel.net/Digested_Mosquito"},
        {"item":"Digested Mosquito", "tier":"V", "base_pct": 100.0/1404.3, "one_in": 1404.3, "cofl_tag":"DIGESTED_MOSQUITO", "source":"https://wiki.hypixel.net/Digested_Mosquito"},
        {"item":"Tarantula Talisman", "tier":"III", "base_pct": 100.0/1274.68, "one_in": 1274.68, "cofl_tag":"TARANTULA_TALISMAN", "source":"https://wiki.hypixel.net/Tarantula_Talisman"},
        {"item":"Tarantula Talisman", "tier":"IV", "base_pct": 100.0/598.576, "one_in": 598.576, "cofl_tag":"TARANTULA_TALISMAN", "source":"https://wiki.hypixel.net/Tarantula_Talisman"},
        {"item":"Fly Swatter", "tier":"III", "base_pct": 100.0/1252.7, "one_in": 1252.7, "cofl_tag":"FLY_SWATTER", "source":"https://wiki.hypixel.net/Fly_Swatter"},
        {"item":"Fly Swatter", "tier":"IV", "base_pct": 100.0/589.42, "one_in": 589.42, "cofl_tag":"FLY_SWATTER", "source":"https://wiki.hypixel.net/Fly_Swatter"},
    ],
    "Sven Packmaster": [
        {"item":"Overflux Capacitor", "tier":"IV", "base_pct": 100.0/2465.4, "one_in": 2465.4, "cofl_tag":"OVERFLUX_CAPACITOR", "source":"https://wiki.hypixel.net/Overflux_Capacitor"},
        {"item":"Red Claw Egg", "tier":"III", "base_pct": 100.0/2431.0, "one_in": 2431.0, "cofl_tag":"RED_CLAW_EGG", "source":"https://wiki.hypixel.net/Red_Claw_Egg"},
        {"item":"Red Claw Egg", "tier":"IV", "base_pct": 100.0/821.8, "one_in": 821.8, "cofl_tag":"RED_CLAW_EGG", "source":"https://wiki.hypixel.net/Red_Claw_Egg"},
    ],
    "Voidgloom Seraph": [
        {"item":"Judgement Core", "tier":"IV", "base_pct": 100.0/1771.12, "one_in": 1771.12, "cofl_tag":"JUDGEMENT_CORE", "source":"https://wiki.hypixel.net/Judgement_Core"},
        {"item":"Exceedingly Rare Ender Artifact Upgrader", "tier":"IV", "base_pct": 100.0/3542.25, "one_in": 3542.25, "cofl_tag":"EXCEEDINGLY_RARE_ENDER_ARTIFACT_UPGRADER", "source":"https://wiki.hypixel.net/Exceedingly_Rare_Ender_Artifact_Upgrade"},
        {"item":"Handy Blood Chalice", "tier":"IV", "base_pct": 100.0/566.76, "one_in": 566.76, "cofl_tag":"HANDY_BLOOD_CHALICE", "source":"https://wiki.hypixel.net/Handy_Blood_Chalice"},
        {"item":"Pocket Espresso Machine", "tier":"IV", "base_pct": 100.0/257.62, "one_in": 257.62, "cofl_tag":"POCKET_ESPRESSO_MACHINE", "source":"https://wiki.hypixel.net/Pocket_Espresso_Machine"},
    ],
    "Inferno Demonlord": [
        {"item":"High Class Archfiend Dice", "tier":"IV", "base_pct": 100.0/394.68, "one_in": 394.68, "cofl_tag":"HIGH_CLASS_ARCHFIEND_DICE", "source":"https://wiki.hypixel.net/High_Class_Archfiend_Dice"},
        {"item":"Wilson's Engineering Plans", "tier":"IV", "base_pct": 100.0/1163.76, "one_in": 1163.76, "cofl_tag":"WILSON_ENGINEERING_PLANS", "source":"https://wiki.hypixel.net/Wilson%27s_Engineering_Plans"},
        {"item":"Subzero Inverter", "tier":"IV", "base_pct": 100.0/1163.76, "one_in": 1163.76, "cofl_tag":"SUBZERO_INVERTER", "source":"https://wiki.hypixel.net/Subzero_Inverter"},
    ],
    "Riftstalker Bloodfiend": [
        {"item":"McGrubber's Burger", "tier":"IV", "base_pct": 1.22, "one_in": 100.0/1.22, "cofl_tag":"MCGRUBBERS_BURGER", "source":"https://wiki.hypixel.net/Riftstalker_Bloodfiend"},
        {"item":"Unfanged Vampire Part", "tier":"IV", "base_pct": 1.22, "one_in": 100.0/1.22, "cofl_tag":"UNFANGED_VAMPIRE_PART", "source":"https://wiki.hypixel.net/Riftstalker_Bloodfiend"},
        {"item":"Sangria Dye", "tier":"IV", "base_pct": 100.0/40000.0, "one_in": 40000.0, "cofl_tag":"DYE_SANGRIA", "source":"https://wiki.hypixel.net/Riftstalker_Bloodfiend"},
    ]
}

# Moderate (1–10%) approximate drops; format similar to RARE_DROPS but 'cofl_tag' or 'bz_id'
MODERATE_DROPS = {
    "Inferno Demonlord": [
        {"item":"Duplex I Book", "tier":"IV", "base_pct": 1.8, "cofl_tag":"ENCHANTMENT_ULTIMATE_REITERATE_1",
         "alt_tags":["ENCHANTMENT_ULTIMATE_REITERATE_1","ENCHANTMENT_ULTIMATE_REITERATE_1"], "bz_id":"ENCHANTMENT_ULTIMATE_REITERATE_1"},
        {"item":"Mana Disintegrator", "tier":"IV", "base_pct": 3.6, "cofl_tag":"MANA_DISINTEGRATOR"},
        {"item":"Scorched Power Crystal", "tier":"IV", "base_pct": 3.0, "cofl_tag":"SCORCHED_Power_CRYSTAL".upper()},
    ],
    "Voidgloom Seraph": [
        {"item":"Null Atom", "tier":"III", "base_pct": 3.7, "bz_id":"NULL_ATOM"},
        {"item":"Null Atom", "tier":"IV", "base_pct": 4.9, "bz_id":"NULL_ATOM"},
        {"item":"Transmission Tuner", "tier":"III", "base_pct": 2.5, "cofl_tag":"TRANSMISSION_TUNER"},
        {"item":"Mana Steal I Book", "tier":"III", "base_pct": 4.0, "cofl_tag":"ENCHANTMENT_MANA_STEAL_1"},
    ],
    "Sven Packmaster": [
        {"item":"Furball", "tier":"IV", "base_pct": 1.5, "cofl_tag":"FURBALL"},
        {"item":"Spirit Rune I", "tier":"IV", "base_pct": 5.0, "cofl_tag":"RUNE_SPIRIT_1"},
    ],
    "Tarantula Broodfather": [
        {"item":"Spider Catalyst", "tier":"IV", "base_pct": 1.0, "cofl_tag":"SPIDER_CATALYST"},
        {"item":"Bite Rune I", "tier":"IV", "base_pct": 5.0, "cofl_tag":"RUNE_BITE_1"},
    ],
    "Revenant Horror": [
        {"item":"Undead Catalyst", "tier":"IV", "base_pct": 1.5, "cofl_tag":"UNDEAD_CATALYST"},
        {"item":"Pestilence Rune I", "tier":"III", "base_pct": 5.0, "cofl_tag":"RUNE_PESTILENCE_1"},
    ],
}

# Common loot averages per boss (Bazaar items); chance=1.0 for guaranteed, else probability
COMMON_LOOT = {
    "Inferno Demonlord": {
        "I":  [{"name":"[Common] Derelict Ashe","bz_id":"DERELICT_ASHE","avg_qty":7,"chance":1.0}],
        "II": [{"name":"[Common] Derelict Ashe","bz_id":"DERELICT_ASHE","avg_qty":17,"chance":1.0},
               {"name":"[Common] Ench. Blaze Powder","bz_id":"ENCHANTED_BLAZE_POWDER","avg_qty":1.5,"chance":0.2}],
        "III":[{"name":"[Common] Derelict Ashe","bz_id":"DERELICT_ASHE","avg_qty":70,"chance":1.0},
               {"name":"[Common] Ench. Blaze Powder","bz_id":"ENCHANTED_BLAZE_POWDER","avg_qty":3,"chance":0.2}],
        "IV":[{"name":"[Common] Derelict Ashe","bz_id":"DERELICT_ASHE","avg_qty":128,"chance":1.0},
               {"name":"[Common] Ench. Blaze Powder","bz_id":"ENCHANTED_BLAZE_POWDER","avg_qty":8,"chance":0.2}],
    },
    "Voidgloom Seraph": {
        "I":  [{"name":"[Common] Null Sphere","bz_id":"NULL_SPHERE","avg_qty":2.5,"chance":1.0}],
        "II": [{"name":"[Common] Null Sphere","bz_id":"NULL_SPHERE","avg_qty":19,"chance":1.0}],
        "III":[{"name":"[Common] Null Sphere","bz_id":"NULL_SPHERE","avg_qty":70,"chance":1.0}],
        "IV":[{"name":"[Common] Null Sphere","bz_id":"NULL_SPHERE","avg_qty":130,"chance":1.0}],
    },
    "Revenant Horror": {
        "I":  [{"name":"[Common] Revenant Flesh","bz_id":"REVENANT_FLESH","avg_qty":2,"chance":1.0}],
        "II": [{"name":"[Common] Revenant Flesh","bz_id":"REVENANT_FLESH","avg_qty":14,"chance":1.0},
               {"name":"[Common] Foul Flesh","bz_id":"FOUL_FLESH","avg_qty":1,"chance":0.2}],
        "III":[{"name":"[Common] Revenant Flesh","bz_id":"REVENANT_FLESH","avg_qty":40,"chance":1.0},
               {"name":"[Common] Foul Flesh","bz_id":"FOUL_FLESH","avg_qty":1.5,"chance":0.2}],
        "IV":[{"name":"[Common] Revenant Flesh","bz_id":"REVENANT_FLESH","avg_qty":57,"chance":1.0},
               {"name":"[Common] Foul Flesh","bz_id":"FOUL_FLESH","avg_qty":2.5,"chance":0.2}],
        "V":  [{"name":"[Common] Revenant Flesh","bz_id":"REVENANT_FLESH","avg_qty":64,"chance":1.0},
               {"name":"[Common] Foul Flesh","bz_id":"FOUL_FLESH","avg_qty":3.5,"chance":0.2}],
    },
    "Tarantula Broodfather": {
        "I":  [{"name":"[Common] Tarantula Web","bz_id":"TARANTULA_WEB","avg_qty":3,"chance":1.0},
               {"name":"[Common] Toxic Arrow Poison","bz_id":"TOXIC_ARROW_POISON","avg_qty":6,"chance":0.2}],
        "II": [{"name":"[Common] Tarantula Web","bz_id":"TARANTULA_WEB","avg_qty":6,"chance":1.0},
               {"name":"[Common] Toxic Arrow Poison","bz_id":"TOXIC_ARROW_POISON","avg_qty":7,"chance":0.2}],
        "III":[{"name":"[Common] Tarantula Web","bz_id":"TARANTULA_WEB","avg_qty":24,"chance":1.0},
               {"name":"[Common] Toxic Arrow Poison","bz_id":"TOXIC_ARROW_POISON","avg_qty":24,"chance":0.2}],
        "IV":[{"name":"[Common] Tarantula Web","bz_id":"TARANTULA_WEB","avg_qty":40,"chance":1.0},
               {"name":"[Common] Toxic Arrow Poison","bz_id":"TOXIC_ARROW_POISON","avg_qty":40,"chance":0.2}],
        "V":  [{"name":"[Common] Tarantula Web","bz_id":"TARANTULA_WEB","avg_qty":64,"chance":1.0},
               {"name":"[Common] Toxic Arrow Poison","bz_id":"TOXIC_ARROW_POISON","avg_qty":64,"chance":0.2}],
    },
    "Sven Packmaster": {
        "I":  [{"name":"[Common] Wolf Tooth","bz_id":"WOLF_TOOTH","avg_qty":2,"chance":1.0}],
        "II": [{"name":"[Common] Wolf Tooth","bz_id":"WOLF_TOOTH","avg_qty":14,"chance":1.0},
               {"name":"[Common] Hamster Wheel","bz_id":"HAMSTER_WHEEL","avg_qty":1,"chance":0.2}],
        "III":[{"name":"[Common] Wolf Tooth","bz_id":"WOLF_TOOTH","avg_qty":40,"chance":1.0},
               {"name":"[Common] Hamster Wheel","bz_id":"HAMSTER_WHEEL","avg_qty":3,"chance":0.2}],
        "IV":[{"name":"[Common] Wolf Tooth","bz_id":"WOLF_TOOTH","avg_qty":57,"chance":1.0},
               {"name":"[Common] Hamster Wheel","bz_id":"HAMSTER_WHEEL","avg_qty":4.5,"chance":0.2}],
    },
}

SLAYER_COSTS = {
    "Revenant Horror": {"I":2000, "II":7500, "III":20000, "IV":50000, "V":100000},
    "Tarantula Broodfather": {"I":2000, "II":7500, "III":20000, "IV":50000, "V":100000},
    "Sven Packmaster": {"I":2000, "II":7500, "III":20000, "IV":50000},
    "Voidgloom Seraph": {"I":2000, "II":7500, "III":20000, "IV":50000},
    "Inferno Demonlord": {"I":10000, "II":25000, "III":60000, "IV":150000},
}

# -------------------------------
# Fetchers
# -------------------------------

class AHPriceFetcher:
    def __init__(self, debug_callback=None, prefer="auto"):
        self.debug = debug_callback or (lambda msg: None)
        self.prefer = prefer  # 'auto'|'bin'|'sold'
        self.moul_cache = None

    def _req_json(self, url, **kwargs):
        if not requests:
            self.debug("The 'requests' module is not installed. Run: pip install requests")
            return None, None
        timeout = kwargs.pop("timeout", 12)
        try:
            r = requests.get(url, timeout=timeout, **kwargs)
            if r.status_code != 200:
                self.debug(f"GET {url} -> HTTP {r.status_code}")
                return None, r.status_code
            try:
                return r.json(), r.status_code
            except Exception:
                self.debug(f"GET {url} -> invalid JSON")
                return None, r.status_code
        except Exception as ex:
            self.debug(f"GET {url} failed: {ex}")
            return None, None

    def _cofl_active_bin(self, tag):
        tag = cofl_tag_sanitize(tag)
        url = f"https://sky.coflnet.com/api/auctions/tag/{tag}/active/bin"
        data, code = self._req_json(url, params={"limit": 20})
        if code == 400:
            self.debug(f"No active BINs right now for {tag} — falling back to SOLD.")
        if not isinstance(data, list) or not data:
            return None, "cofl-bin", None
        best = None
        for a in data:
            price = None
            for key in ("startingBid","starting_price","price","buyItNowPrice","highest_bid_amount"):
                if isinstance(a.get(key), (int,float)):
                    price = float(a[key]); break
            if price is None: continue
            cnt = a.get("count") or 1
            try:
                cnt = float(cnt)
                if cnt <= 0: cnt = 1.0
            except Exception:
                cnt = 1.0
            per = price / cnt
            if best is None or per < best:
                best = per
        return (best if best else None), "cofl-bin", None

    def _cofl_sold(self, tag):
        tag = cofl_tag_sanitize(tag)
        url = f"https://sky.coflnet.com/api/auctions/tag/{tag}/sold"
        data, _ = self._req_json(url, params={"limit": 250})
        if not isinstance(data, list) or not data:
            return None, "cofl-sold", None
        prices = []
        for a in data:
            p = None
            for key in ("highestBidAmount","price","finalPrice","highest_bid_amount","startingBid"):
                if isinstance(a.get(key), (int,float)):
                    p = float(a[key]); break
            if p is None: continue
            cnt = a.get("count") or 1
            try:
                cnt = float(cnt)
                if cnt <= 0: cnt = 1.0
            except Exception:
                cnt = 1.0
            prices.append(p / cnt)
        if not prices:
            return None, "cofl-sold", None
        prices.sort()
        p25_idx = max(0, int(len(prices)*0.25)-1)
        p50_idx = max(0, int(len(prices)*0.50)-1)
        return prices[p25_idx], "cofl-sold", prices[p50_idx]

    def _moulberry_lbin(self, tag):
        if self.moul_cache is None:
            url = "https://moulberry.codes/lowestbin.json"
            data, _ = self._req_json(url, timeout=15)
            if not isinstance(data, dict):
                time.sleep(1.0)
                data, _ = self._req_json(url, timeout=20)
                self.moul_cache = data if isinstance(data, dict) else {}
            else:
                self.moul_cache = data
        key = cofl_tag_sanitize(tag)
        val = self.moul_cache.get(key)
        if isinstance(val, (int,float)):
            return float(val), "moul-lbin", None
        return None, "moul-lbin", None

    def get_price_for_tag(self, tag):
        prefer = (self.prefer or "auto").lower()
        order = {
            "bin": [self._cofl_active_bin, self._cofl_sold, self._moulberry_lbin],
            "sold": [self._cofl_sold, self._cofl_active_bin, self._moulberry_lbin],
            "auto": [self._cofl_active_bin, self._cofl_sold, self._moulberry_lbin],
        }.get(prefer, [self._cofl_active_bin, self._cofl_sold, self._moulberry_lbin])
        for fn in order:
            price, src, median = fn(tag)
            if isinstance(price, (int,float)) and price > 0:
                if median is None:
                    _, _, median = self._cofl_sold(tag)
                return price, src, median
        return None, None, None

def fetch_hypixel_bazaar(product_id: str, kind: str = "sell", debug=lambda m: None):
    if not requests:
        return None
    url = "https://api.hypixel.net/v2/skyblock/bazaar"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code != 200:
            debug(f"Hypixel Bazaar status {r.status_code}")
            return None
        js = r.json()
        prod = js.get("products", {}).get(product_id.upper())
        if not isinstance(prod, dict):
            return None
        quick = prod.get("quick_status", {})
        val = quick.get("sellPrice" if kind=="sell" else "buyPrice")
        return float(val) if isinstance(val,(int,float)) else None
    except Exception as ex:
        debug(f"Hypixel Bazaar error: {ex}")
        return None

def fetch_bz_instaprice_from_page(product_id: str, kind: str = "sell", debug=lambda m: None):
    if not requests:
        return None
    pid = str(product_id).strip().upper().replace(" ", "_")
    url = f"https://www.skyblock.bz/product/{pid}"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code != 200:
            debug(f"skyblock.bz status {r.status_code} for {pid}")
            return None
        text = r.text
        if kind == "sell":
            m = re.search(r"Instasell Price\s*([\d,\.]+)\s*coins", text, re.IGNORECASE)
        else:
            m = re.search(r"Instabuy Price\s*([\d,\.]+)\s*coins", text, re.IGNORECASE)
        if not m:
            return None
        val = float(m.group(1).replace(",", ""))
        return val
    except Exception as ex:
        debug(f"skyblock.bz error: {ex}")
        return None

# -------------------------------
# Theme
# -------------------------------

class Theme:
    DARK = {
        "bg": "#0f141a",
        "surface": "#151b23",
        "sunken": "#121820",
        "text": "#e6edf3",
        "muted": "#9aa4b2",
        "accent": "#58f0c4",
        "accent_text": "#0a0f14",
        "border": "#202938",
        "row": ("#161d26", "#131920"),
        "select_bg": "#14856b",
        "select_fg": "#e6edf3",
    }
    LIGHT = {
        "bg": "#f5f7fb",
        "surface": "#ffffff",
        "sunken": "#eef1f6",
        "text": "#0b1623",
        "muted": "#4b5563",
        "accent": "#0ea5e9",
        "accent_text": "#ffffff",
        "border": "#e5e7eb",
        "row": ("#ffffff", "#f3f6fb"),
        "select_bg": "#cdeafe",
        "select_fg": "#0b1623",
    }

def style_apply(style: ttk.Style, palette):
    style.theme_use("clam")
    style.configure(".", background=palette["bg"], foreground=palette["text"], fieldbackground=palette["surface"])

    style.configure("TLabel", background=palette["bg"], foreground=palette["text"])
    style.configure("TFrame", background=palette["bg"])
    style.configure("Sunken.TFrame", background=palette["sunken"], relief="flat")

    style.configure("Card.TLabelframe", background=palette["surface"], bordercolor=palette["border"], relief="flat")
    style.configure("Card.TLabelframe.Label", background=palette["surface"], foreground=palette["muted"])

    style.configure("TButton", background=palette["surface"], foreground=palette["text"], borderwidth=0, padding=8)
    style.map("TButton", background=[("active", palette["sunken"])], relief=[("pressed", "sunken")])
    style.configure("Accent.TButton", background=palette["accent"], foreground=palette["accent_text"], padding=10)
    style.map("Accent.TButton", background=[("active", palette["accent"])], foreground=[("active", palette["accent_text"])])

    style.configure("TEntry", fieldbackground=palette["surface"], foreground=palette["text"], insertcolor=palette["accent"])
    style.map("TEntry", fieldbackground=[("disabled", palette["sunken"]), ("readonly", palette["surface"]), ("focus", palette["surface"])],
              foreground=[("disabled", palette["muted"])], insertcolor=[("focus", palette["accent"])])

    style.configure("TCombobox", fieldbackground=palette["surface"], background=palette["surface"], foreground=palette["text"])
    style.map("TCombobox",
              fieldbackground=[("readonly", palette["surface"]), ("!readonly", palette["surface"]), ("focus", palette["surface"])],
              background=[("active", palette["sunken"]), ("readonly", palette["surface"])],
              foreground=[("readonly", palette["text"])],
              selectbackground=[("readonly", palette["select_bg"]), ("!readonly", palette["select_bg"])],
              selectforeground=[("readonly", palette["select_fg"]), ("!readonly", palette["select_fg"])],
              arrowcolor=[("!disabled", palette["muted"]), ("pressed", palette["accent"])])

    try:
        style.configure("TComboboxPopdownFrame", background=palette["surface"], bordercolor=palette["border"])
        style.configure("TListbox", background=palette["surface"], foreground=palette["text"],
                        selectbackground=palette["select_bg"], selectforeground=palette["select_fg"])
    except Exception:
        pass

    style.configure("TNotebook", background=palette["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=palette["surface"], foreground=palette["muted"], padding=[12,6])
    style.map("TNotebook.Tab", background=[("selected", palette["accent"])], foreground=[("selected", palette["accent_text"])])

    style.configure("Treeview", background=palette["surface"], fieldbackground=palette["surface"], foreground=palette["text"],
                    borderwidth=0, rowheight=28)
    style.map("Treeview", background=[("selected", palette["accent"])], foreground=[("selected", palette["accent_text"])])
    style.configure("Treeview.Heading", background=palette["sunken"], foreground=palette["muted"], relief="flat")
    style.configure("TSeparator", background=palette["border"])

# -------------------------------
# Debug window (lazy)
# -------------------------------

class DebugWindow(tk.Toplevel):
    def __init__(self, master, palette):
        super().__init__(master)
        self.title("Debug Log")
        self.geometry("920x420+120+80")
        self.configure(bg=palette["bg"])
        self.palette = palette

        bar = ttk.Frame(self, style="Sunken.TFrame")
        bar.pack(fill="x", padx=10, pady=(10,6))
        ttk.Button(bar, text="Clear", command=self.clear).pack(side="left")
        ttk.Button(bar, text="Copy All", command=self.copy_all).pack(side="left", padx=8)
        self.var_paused = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Pause logging", variable=self.var_paused).pack(side="right")

        self.text = tk.Text(self, wrap="word", height=20, bg=palette["sunken"], fg=palette["text"],
                            insertbackground=palette["accent"], relief="flat", padx=10, pady=10)
        self.text.pack(fill="both", expand=True, padx=10, pady=(0,10))

        sub = ttk.Label(self, text="Network + fallback details appear here. Open via View → Debug Log anytime.",
                        foreground=palette["muted"])
        sub.pack(anchor="w", padx=12, pady=(0,10))

    def clear(self):
        self.text.delete("1.0", "end")

    def copy_all(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.text.get("1.0", "end-1c"))
        except Exception:
            pass

    def log(self, msg: str):
        if self.var_paused.get():
            return
        def _append():
            self.text.insert("end", str(msg) + "\n")
            self.text.see("end")
        self.after(0, _append)

# -------------------------------
# Price Manager shared across frames
# -------------------------------

class PriceManager:
    def __init__(self, debug_cb, prefer="auto", ignore_outliers=True, outlier_pct=15.0):
        self.debug = debug_cb
        self.ah = AHPriceFetcher(debug_callback=self.debug, prefer=prefer)
        self.cache = {}  # key -> dict(price, src, median, is_outlier)
        self.ignore_outliers = ignore_outliers
        self.outlier_pct = outlier_pct

    def set_preference(self, prefer):
        self.ah.prefer = prefer

    def set_outlier_policy(self, ignore: bool, pct: float):
        self.ignore_outliers = ignore
        self.outlier_pct = pct

    def _key_for(self, *, tag=None, bz_id=None):
        return ("AH", cofl_tag_sanitize(tag)) if tag else ("BZ", (bz_id or "").upper())

    def get(self, *, tag=None, bz_id=None):
        key = self._key_for(tag=tag, bz_id=bz_id)
        return self.cache.get(key)

    def fetch(self, *, tag=None, bz_id=None):
        key = self._key_for(tag=tag, bz_id=bz_id)
        if key in self.cache:
            return self.cache[key]

        price, src, median = None, "", None
        if tag:
            price, src, median = self.ah.get_price_for_tag(tag)
        elif bz_id:
            pid = bz_id.upper()
            hyp = fetch_hypixel_bazaar(pid, kind="sell", debug=self.debug)
            if isinstance(hyp,(int,float)):
                price, src = hyp, "bz-hyp:sell"
            else:
                sb = fetch_bz_instaprice_from_page(pid, kind="sell", debug=self.debug)
                if isinstance(sb,(int,float)):
                    price, src = sb, "bz-sb:sell"

        is_outlier = False
        if isinstance(price,(int,float)) and isinstance(median,(int,float)) and median > 0:
            dev = abs(price - median) / median * 100.0
            if dev > self.outlier_pct:
                is_outlier = True

        info = {"price": price, "src": src, "median": median, "is_outlier": is_outlier}
        self.cache[key] = info
        return info

    def resolve_drop(self, d: dict):
        """Try AH, then Bazaar (Hypixel → skyblock.bz). Emit helpful debug logs."""
        name = d.get("item") or d.get("name") or "Unknown"
        # 1) AH
        tag = d.get("cofl_tag")
        info = None
        if tag:
            info = self.fetch(tag=tag)
            if info.get("price") is None and d.get("alt_tags"):
                for alt in d["alt_tags"]:
                    self.debug(f"No price via {tag}; trying alt tag {alt} for {name}.")
                    info = self.fetch(tag=alt)
                    if info.get("price") is not None:
                        break

        # 2) Bazaar
        if (not info) or (info and info.get("price") is None):
            pid = d.get("bz_id") or default_bz_id_from_name(name)
            self.debug(f"No AH price for {name}. Trying Hypixel Bazaar with auto ID: {pid}")
            info = self.fetch(bz_id=pid)
            if info.get("price") is None:
                self.debug(f"No Hypixel Bazaar price for {pid}. Trying skyblock.bz Instasell page.")
                # fetch() already tried skyblock.bz fallback; if still None, we leave it None
        return info or {"price":None,"src":"","median":None,"is_outlier":False}

# -------------------------------
# UI Frames
# -------------------------------

class SingleDropFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=14, style="TFrame")
        self.build()

    def build(self):
        g = ttk.LabelFrame(self, text="Single Drop Calculator", style="Card.TLabelframe", padding=12)
        g.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.columnconfigure(0, weight=1)
        for c in range(5): g.columnconfigure(c, weight=1)

        self.var_mode = tk.StringVar(value="percent")
        ttk.Radiobutton(g, text="Base chance (%)", variable=self.var_mode, value="percent").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(g, text="Base chance (1 in N)", variable=self.var_mode, value="onein").grid(row=0, column=1, sticky="w")

        self.var_base = tk.StringVar(value="0.06")
        self.var_onein = tk.StringVar(value="1771.12")
        self.var_mf = tk.StringVar(value="100")
        self.var_is_pet = tk.BooleanVar(value=False)
        self.var_pet_luck = tk.StringVar(value="0")
        self.var_target_prob = tk.StringVar(value="50")

        row = 1
        ttk.Label(g, text="Base %:").grid(row=row, column=0, sticky="e")
        ttk.Entry(g, textvariable=self.var_base, width=12).grid(row=row, column=1, sticky="w")
        ttk.Label(g, text="or 1 in N:").grid(row=row, column=2, sticky="e")
        ttk.Entry(g, textvariable=self.var_onein, width=12).grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Label(g, text="Magic Find ✯:").grid(row=row, column=0, sticky="e")
        ttk.Entry(g, textvariable=self.var_mf, width=12).grid(row=row, column=1, sticky="w")
        ttk.Checkbutton(g, text="Pet Drop", variable=self.var_is_pet).grid(row=row, column=2, sticky="w")
        ttk.Label(g, text="Pet Luck ♡:").grid(row=row, column=3, sticky="e")
        ttk.Entry(g, textvariable=self.var_pet_luck, width=12).grid(row=row, column=4, sticky="w")

        row += 1
        ttk.Label(g, text="Target chance over N kills (%):").grid(row=row, column=0, sticky="e")
        ttk.Entry(g, textvariable=self.var_target_prob, width=12).grid(row=row, column=1, sticky="w")

        row += 1
        self.btn_calc = ttk.Button(g, text="Compute", style="Accent.TButton", command=self.compute)
        self.btn_calc.grid(row=row, column=0, pady=8, sticky="w")

        self.lbl_out = ttk.Label(g, text="", anchor="w", justify="left")
        self.lbl_out.grid(row=row+1, column=0, columnspan=5, sticky="w")

    def compute(self):
        base_pct = percent_to_float(self.var_base.get())
        if self.var_mode.get() == "onein":
            base_pct = one_in_to_percent(self.var_onein.get())
        elif base_pct <= 0.0 and self.var_onein.get().strip():
            base_pct = one_in_to_percent(self.var_onein.get())

        mf = percent_to_float(self.var_mf.get())
        pl = percent_to_float(self.var_pet_luck.get())
        eff = effective_drop_chance(base_pct, mf, self.var_is_pet.get(), pl)

        p50 = kills_for_probability(eff, percent_to_float(self.var_target_prob.get()))
        text = (
            f"Base chance: {base_pct:.6f}%  |  Effective with MF: {eff:.6f}%\n"
            f"Kills needed for {self.var_target_prob.get()}% drop chance: ≈ {p50:.2f}"
        )
        self.lbl_out.config(text=text)

class SlayerPresetsFrame(ttk.Frame):
    def __init__(self, master, single_frame: 'SingleDropFrame'):
        super().__init__(master, padding=14, style="TFrame")
        self.single_frame = single_frame
        self.build()

    def build(self):
        lf = ttk.LabelFrame(self, text="Slayer Rare Drop Presets", style="Card.TLabelframe", padding=12)
        lf.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        for c in range(4): lf.columnconfigure(c, weight=1)

        self.var_slayer = tk.StringVar(value="Inferno Demonlord")
        self.var_tier = tk.StringVar(value="IV")
        self.var_item = tk.StringVar(value="Subzero Inverter")
        self.var_mf = tk.StringVar(value="100")

        ttk.Label(lf, text="Slayer:").grid(row=0, column=0, sticky="e")
        cb_slayer = ttk.Combobox(lf, textvariable=self.var_slayer, values=list(RARE_DROPS.keys()), state="readonly", width=24)
        cb_slayer.grid(row=0, column=1, sticky="w")
        cb_slayer.bind("<<ComboboxSelected>>", lambda e: self.refresh_items())

        ttk.Label(lf, text="Tier:").grid(row=0, column=2, sticky="e")
        self.cb_tier = ttk.Combobox(lf, textvariable=self.var_tier, values=["I","II","III","IV","V"], state="readonly", width=5)
        self.cb_tier.grid(row=0, column=3, sticky="w")
        self.cb_tier.bind("<<ComboboxSelected>>", lambda e: self.refresh_items())

        ttk.Label(lf, text="Item:").grid(row=1, column=0, sticky="e")
        self.cb_item = ttk.Combobox(lf, textvariable=self.var_item, values=[], state="readonly", width=36)
        self.cb_item.grid(row=1, column=1, sticky="w", columnspan=3)
        self.cb_item.bind("<<ComboboxSelected>>", lambda e: self.show_selected())

        ttk.Label(lf, text="Magic Find ✯:").grid(row=2, column=0, sticky="e")
        ttk.Entry(lf, textvariable=self.var_mf, width=10).grid(row=2, column=1, sticky="w")

        self.lbl_base = ttk.Label(lf, text="Base: -", justify="left")
        self.lbl_base.grid(row=3, column=0, columnspan=4, sticky="w")
        self.lbl_eff = ttk.Label(lf, text="Effective: -", justify="left")
        self.lbl_eff.grid(row=4, column=0, columnspan=4, sticky="w")
        self.lbl_src = ttk.Label(lf, text="Source: -", justify="left", foreground="#9aa4b2")
        self.lbl_src.grid(row=5, column=0, columnspan=4, sticky="w")

        btns = ttk.Frame(lf, style="TFrame")
        btns.grid(row=6, column=0, columnspan=4, sticky="w", pady=6)
        ttk.Button(btns, text="Apply to Single Drop", command=self.apply_to_single).pack(side="left", padx=4)
        ttk.Button(btns, text="Open Wiki Page", command=self.open_wiki).pack(side="left", padx=4)

        self.refresh_items()
        self.show_selected()

    def _current_selection(self):
        slayer = self.var_slayer.get()
        tier = self.var_tier.get()
        item = self.var_item.get()
        options = [d for d in RARE_DROPS.get(slayer, []) if d["tier"] == tier]
        sel = None
        for d in options:
            if d["item"] == item:
                sel = d; break
        if sel is None and options:
            sel = options[0]
        return sel

    def refresh_items(self):
        slayer = self.var_slayer.get()
        tier = self.var_tier.get()
        items = sorted({d["item"] for d in RARE_DROPS.get(slayer, []) if d["tier"] == tier})
        if not items:
            items = ["(no rare items recorded for this tier)"]
        self.cb_item.configure(values=items)
        self.var_item.set(items[0])
        self.show_selected()

    def show_selected(self):
        sel = self._current_selection()
        if not sel:
            self.lbl_base.config(text="Base: -")
            self.lbl_eff.config(text="Effective: -")
            return
        mf = percent_to_float(self.var_mf.get())
        eff = effective_drop_chance(sel["base_pct"], magic_find=mf)
        base_line = f"Base: {sel['base_pct']:.6f}%  (~1 in {sel['one_in']:.2f})"
        eff_line  = f"Effective with MF {mf:.1f}: {eff:.6f}%  (~1 in {1.0/(eff/100.0):.2f})"
        self.lbl_base.config(text=base_line)
        self.lbl_eff.config(text=eff_line)
        self.lbl_src.config(text=f"Source: {sel.get('source','-')}")

    def apply_to_single(self):
        sel = self._current_selection()
        if not sel: return
        self.single_frame.var_mode.set("percent")
        self.single_frame.var_base.set(f"{sel['base_pct']:.6f}")
        self.single_frame.var_onein.set(f"{sel['one_in']:.2f}")
        messagebox.showinfo("Applied", f"Sent '{sel['item']}' base chance to Single Drop tab.")

    def open_wiki(self):
        sel = self._current_selection()
        if not sel: return
        src = sel.get("source")
        if not src: return
        url = src if src.startswith("http") else "https://" + src
        webbrowser.open(url)

class RatesFrame(ttk.Frame):
    def __init__(self, master, price_mgr: PriceManager, palette):
        super().__init__(master, padding=14, style="TFrame")
        self.mgr = price_mgr
        self.palette = palette
        self.price_cache = {}    # name -> dict(price,src,median,is_outlier)
        self.build()

    def set_palette(self, palette):
        self.palette = palette
        self.tree.tag_configure("odd", background=self.palette["row"][0])
        self.tree.tag_configure("even", background=self.palette["row"][1])

    def _current_drops(self, include_common=False, include_moderate=True):
        sl = self.var_slayer.get()
        tr = self.var_tier.get()
        drops = [d for d in RARE_DROPS.get(sl, []) if d["tier"] == tr]
        if include_moderate:
            drops += [d for d in MODERATE_DROPS.get(sl, []) if d["tier"] == tr]
        if include_common:
            for c in COMMON_LOOT.get(sl, {}).get(tr, []):
                drops.append({"item": c["name"], "tier": tr, "base_pct": 100.0 * c["chance"],
                              "is_common": True, "avg_qty": c["avg_qty"], "bz_id": c["bz_id"]})
        return drops

    def build(self):
        top = ttk.LabelFrame(self, text="Rates / Profit (coins per hour)", style="Card.TLabelframe", padding=12)
        top.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        for c in range(10): top.columnconfigure(c, weight=1)

        self.var_slayer = tk.StringVar(value="Inferno Demonlord")
        self.var_tier = tk.StringVar(value="IV")
        self.var_mf = tk.StringVar(value="100")
        self.var_spawn_s = tk.StringVar(value="30")
        self.var_kill_s = tk.StringVar(value="60")
        self.var_aatrox_half = tk.BooleanVar(value=False)
        self.var_custom_cost = tk.StringVar(value="")
        self.var_base_loot_extra = tk.StringVar(value="0")
        self.var_price_pref = tk.StringVar(value="auto")
        self.var_ignore_outliers = tk.BooleanVar(value=True)

        ttk.Label(top, text="Slayer:").grid(row=0, column=0, sticky="e")
        cb_slayer = ttk.Combobox(top, textvariable=self.var_slayer, values=list(RARE_DROPS.keys()), state="readonly", width=24)
        cb_slayer.grid(row=0, column=1, sticky="w")
        cb_slayer.bind("<<ComboboxSelected>>", lambda e: self.refresh_drops())

        ttk.Label(top, text="Tier:").grid(row=0, column=2, sticky="e")
        cb_tier = ttk.Combobox(top, textvariable=self.var_tier, values=["I","II","III","IV","V"], state="readonly", width=5)
        cb_tier.grid(row=0, column=3, sticky="w")
        cb_tier.bind("<<ComboboxSelected>>", lambda e: self.refresh_drops())

        ttk.Label(top, text="Magic Find ✯:").grid(row=0, column=4, sticky="e")
        ttk.Entry(top, textvariable=self.var_mf, width=10).grid(row=0, column=5, sticky="w")

        ttk.Label(top, text="Spawn time (s):").grid(row=1, column=0, sticky="e")
        ttk.Entry(top, textvariable=self.var_spawn_s, width=10).grid(row=1, column=1, sticky="w")
        ttk.Label(top, text="Kill time (s):").grid(row=1, column=2, sticky="e")
        ttk.Entry(top, textvariable=self.var_kill_s, width=10).grid(row=1, column=3, sticky="w")
        ttk.Checkbutton(top, text="Aatrox -50% quest cost", variable=self.var_aatrox_half).grid(row=1, column=4, sticky="w")
        ttk.Label(top, text="Extra baseline coins/boss:").grid(row=1, column=5, sticky="e")
        ttk.Entry(top, textvariable=self.var_base_loot_extra, width=12).grid(row=1, column=6, sticky="w")

        ttk.Label(top, text="Override quest cost (coins):").grid(row=2, column=0, sticky="e")
        ttk.Entry(top, textvariable=self.var_custom_cost, width=14).grid(row=2, column=1, sticky="w")

        ttk.Button(top, text="Refresh Prices", style="Accent.TButton", command=self.refresh_prices).grid(row=2, column=2, sticky="w")
        ttk.Button(top, text="Compute Coins/h", style="Accent.TButton", command=self.compute).grid(row=2, column=3, sticky="w")
        ttk.Button(top, text="Simulate 1h (100 runs)", command=self.simulate).grid(row=2, column=4, sticky="w")

        ttk.Label(top, text="AH Price Preference:").grid(row=2, column=5, sticky="e")
        cb_pref = ttk.Combobox(top, textvariable=self.var_price_pref, values=["auto","bin","sold"], state="readonly", width=8)
        cb_pref.grid(row=2, column=6, sticky="w")
        ttk.Checkbutton(top, text="Ignore ±15% outliers", variable=self.var_ignore_outliers).grid(row=2, column=7, sticky="w")

        warn_text = "Pricing order: Cofl BIN → SOLD → Hypixel Bazaar (sell) → skyblock.bz Instasell → alert. Common bazaar loot auto-added."
        ttk.Label(self, text=warn_text, foreground="#9aa4b2").grid(row=1, column=0, sticky="w", padx=10)

        self.tree = ttk.Treeview(self, columns=("item","chance","price","source","ex_boss"), show="headings", height=15)
        self.tree.grid(row=2, column=0, sticky="nsew", padx=6, pady=6)
        self.tree.heading("item", text="Item")
        self.tree.heading("chance", text="Chance / Common (eff % / 1 in N or qty)")
        self.tree.heading("price", text="Price (coins)")
        self.tree.heading("source", text="Source")
        self.tree.heading("ex_boss", text="Expected / boss")
        self.tree["displaycolumns"] = ("item","chance","price","source","ex_boss")

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=2, column=1, sticky="ns", pady=6)

        self.tree.tag_configure("odd", background=self.palette["row"][0])
        self.tree.tag_configure("even", background=self.palette["row"][1])

        self.lbl_summary = ttk.Label(self, text="", justify="left", anchor="w")
        self.lbl_summary.grid(row=3, column=0, sticky="w", padx=10)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.refresh_drops()

    def refresh_drops(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        self.price_cache.clear()

        drops = self._current_drops(include_common=True, include_moderate=True)
        for i, d in enumerate(drops):
            key = d["item"]
            self.price_cache[key] = None
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", iid=key, values=(key, "—", "—", "", "—"), tags=(tag,))

        self.lbl_summary.config(text="Set MF and times. Refresh Prices, then Compute or Simulate.")

    def update_tree(self):
        drops = self._current_drops(include_common=True, include_moderate=True)
        mf = percent_to_float(self.var_mf.get())

        for i, d in enumerate(drops):
            name = d["item"]
            price_info = self.price_cache.get(name) or {}
            price = price_info.get("price")
            src = price_info.get("src","")
            out = price_info.get("is_outlier", False)

            if d.get("is_common"):
                qty = d["avg_qty"]
                chance_text = f"100% x {qty:g}" if d["base_pct"]>=100.0 else f"{d['base_pct']:.1f}% x {qty:g}"
                ex = qty * (price or 0.0) * (d["base_pct"]/100.0)
            else:
                eff = effective_drop_chance(d["base_pct"], magic_find=mf)
                eff_frac = max(eff/100.0, 1e-12)
                one_in = 1.0/eff_frac
                chance_text = f"{eff:.6f}%  (1 in {one_in:.2f})"
                ex = eff_frac * (price if isinstance(price,(int,float)) else 0.0)

            if out:
                src = (src or "") + " ⚠"

            tag = "odd" if i % 2 else "even"
            self.tree.item(name, tags=(tag,))
            self.tree.set(name, "item", name)
            self.tree.set(name, "chance", chance_text)
            self.tree.set(name, "price", "—" if price is None else fmt_num(price))
            self.tree.set(name, "source", src)
            self.tree.set(name, "ex_boss", "—" if price is None else fmt_num(ex))

    def refresh_prices(self):
        pref = self.var_price_pref.get().strip().lower() or "auto"
        self.mgr.set_preference(pref)
        self.mgr.set_outlier_policy(self.var_ignore_outliers.get(), 15.0)
        drops = self._current_drops(include_common=True, include_moderate=True)

        unresolved = []

        def worker():
            if requests is None:
                messagebox.showwarning("Missing dependency", "Install 'requests' to enable live price fetching:\n\npip install requests")
                return
            for d in drops:
                name = d["item"]
                info = self.mgr.resolve_drop(d)
                self.price_cache[name] = info
                if info.get("price") is None:
                    unresolved.append(name)

            self.after(0, self.update_tree)
            def done():
                if unresolved:
                    msg = "Couldn't resolve prices for:\n- " + "\n- ".join(unresolved) + "\n\nTip: enter manual values or try again later."
                    messagebox.showwarning("Some prices unresolved", msg)
                else:
                    messagebox.showinfo("Prices", "Price refresh complete.")
            self.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def _bosses_per_hour(self):
        try:
            spawn = float(self.var_spawn_s.get()); kill  = float(self.var_kill_s.get())
            cycle = max(1.0, spawn + kill)
            return 3600.0 / cycle
        except Exception:
            return 0.0

    def _quest_cost(self):
        base_costs = SLAYER_COSTS.get(self.var_slayer.get(), {})
        cost = float(base_costs.get(self.var_tier.get(), 0))
        if self.var_aatrox_half.get():
            cost *= 0.5
        if self.var_custom_cost.get().strip():
            try: cost = float(self.var_custom_cost.get().replace(",", ""))
            except Exception: pass
        return cost

    def _expected_per_boss(self):
        mf = percent_to_float(self.var_mf.get())
        total = 0.0; missing = []
        ignore_outliers = self.var_ignore_outliers.get()
        drops = self._current_drops(include_common=True, include_moderate=True)

        for d in drops:
            name = d["item"]
            info = self.price_cache.get(name) or {}
            price = info.get("price")
            is_out = bool(info.get("is_outlier", False))
            if price is None or (ignore_outliers and is_out):
                if price is None:
                    missing.append(name)
                continue

            if d.get("is_common"):
                qty = d["avg_qty"]; p = d["base_pct"]/100.0
                total += qty * price * p
            else:
                eff = effective_drop_chance(d["base_pct"], magic_find=mf)
                total += (eff/100.0) * price

        try:
            baseline_extra = float(self.var_base_loot_extra.get().replace(",", ""))
        except Exception:
            baseline_extra = 0.0
        total += baseline_extra
        return total, missing

    def compute(self):
        bosses_per_hour = self._bosses_per_hour()
        cost = self._quest_cost()
        expected_per_boss, missing = self._expected_per_boss()
        coins_per_hour = bosses_per_hour * (expected_per_boss - cost)

        summary = [
            f"Bosses/hour: {bosses_per_hour:.2f}  |  Quest cost: {fmt_num(cost)}  |  Expected/boss (inc. common): {fmt_num(expected_per_boss)}",
            f"Estimated coins/hour: {fmt_num(coins_per_hour)}",
        ]
        if missing:
            summary.append(f"Missing prices for: {', '.join(missing)}")
        self.lbl_summary.config(text="\n".join(summary))

    def simulate(self):
        bosses_per_hour = self._bosses_per_hour()
        if bosses_per_hour <= 0:
            messagebox.showerror("Invalid times", "Enter valid spawn/kill times first.")
            return
        cost = self._quest_cost()
        ignore_outliers = self.var_ignore_outliers.get()
        mf = percent_to_float(self.var_mf.get())
        drops = self._current_drops(include_common=True, include_moderate=True)

        def run_once():
            n = int(bosses_per_hour)  # approximate
            total = 0.0
            for _ in range(n):
                try:
                    baseline_extra = float(self.var_base_loot_extra.get().replace(",", ""))
                except Exception:
                    baseline_extra = 0.0
                val = -cost + baseline_extra
                for d in drops:
                    name = d["item"]
                    info = self.price_cache.get(name) or {}
                    price = info.get("price")
                    if price is None or (ignore_outliers and info.get("is_outlier", False)):
                        continue
                    if d.get("is_common"):
                        qty = d["avg_qty"]; p = d["base_pct"]/100.0
                        val += qty * price * p
                    else:
                        eff = effective_drop_chance(d["base_pct"], magic_find=mf)
                        if random.random() < (eff/100.0):
                            val += price
                total += val
            return total

        runs = 100
        results = [run_once() for _ in range(runs)]
        if results:
            mn = min(results); mx = max(results); med = statistics.median(results)
            messagebox.showinfo("Simulation", f"1h simulation (100 runs):\nMin: {fmt_num(mn)}  |  Median: {fmt_num(med)}  |  Max: {fmt_num(mx)}")

class CompareFrame(ttk.Frame):
    def __init__(self, master, price_mgr: PriceManager, palette):
        super().__init__(master, padding=14, style="TFrame")
        self.mgr = price_mgr
        self.palette = palette
        self.rows = []  # list of dicts
        self.build()

    def build(self):
        top = ttk.LabelFrame(self, text="Compare Slayers (coins/hour)", style="Card.TLabelframe", padding=12)
        top.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        for c in range(10): top.columnconfigure(c, weight=1)

        self.var_slayer = tk.StringVar(value="Inferno Demonlord")
        self.var_tier = tk.StringVar(value="IV")
        self.var_mf = tk.StringVar(value="100")
        self.var_spawn_s = tk.StringVar(value="30")
        self.var_kill_s = tk.StringVar(value="60")

        ttk.Label(top, text="Slayer:").grid(row=0, column=0, sticky="e")
        ttk.Combobox(top, textvariable=self.var_slayer, values=list(RARE_DROPS.keys()), state="readonly", width=24).grid(row=0, column=1, sticky="w")
        ttk.Label(top, text="Tier:").grid(row=0, column=2, sticky="e")
        ttk.Combobox(top, textvariable=self.var_tier, values=["I","II","III","IV","V"], state="readonly", width=6).grid(row=0, column=3, sticky="w")
        ttk.Label(top, text="MF ✯:").grid(row=0, column=4, sticky="e")
        ttk.Entry(top, textvariable=self.var_mf, width=10).grid(row=0, column=5, sticky="w")
        ttk.Label(top, text="Spawn (s):").grid(row=0, column=6, sticky="e")
        ttk.Entry(top, textvariable=self.var_spawn_s, width=10).grid(row=0, column=7, sticky="w")
        ttk.Label(top, text="Kill (s):").grid(row=0, column=8, sticky="e")
        ttk.Entry(top, textvariable=self.var_kill_s, width=10).grid(row=0, column=9, sticky="w")

        ttk.Button(top, text="Add", style="Accent.TButton", command=self.add_row).grid(row=0, column=10, sticky="w", padx=6)

        self.tree = ttk.Treeview(self, columns=("slayer","tier","mf","rate","coins_h"), show="headings", height=16)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        for col, txt in [("slayer","Slayer"),("tier","Tier"),("mf","MF"),("rate","Bosses/h"),("coins_h","Coins/h")]:
            self.tree.heading(col, text=txt)
        self.tree["displaycolumns"] = ("slayer","tier","mf","rate","coins_h")

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=1, column=1, sticky="ns", pady=6)

        self.tree.tag_configure("odd", background=self.palette["row"][0])
        self.tree.tag_configure("even", background=self.palette["row"][1])

        btns = ttk.Frame(self, style="TFrame"); btns.grid(row=2, column=0, sticky="w", padx=8, pady=(0,8))
        ttk.Button(btns, text="Refresh Prices", style="Accent.TButton", command=self.refresh_prices).pack(side="left", padx=4)
        ttk.Button(btns, text="Compute All", command=self.compute_all).pack(side="left", padx=4)
        ttk.Button(btns, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=4)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def add_row(self):
        row = {
            "slayer": self.var_slayer.get(),
            "tier": self.var_tier.get(),
            "mf": percent_to_float(self.var_mf.get()),
            "spawn": percent_to_float(self.var_spawn_s.get()),
            "kill": percent_to_float(self.var_kill_s.get()),
        }
        iid = f"{row['slayer']}|{row['tier']}|{len(self.rows)}"
        self.rows.append(row)
        tag = "odd" if (len(self.rows)-1) % 2 else "even"
        self.tree.insert("", "end", iid=iid, values=(row["slayer"], row["tier"], row["mf"], "—", "—"), tags=(tag,))

    def remove_selected(self):
        for sel in self.tree.selection():
            try:
                idx = int(sel.split("|")[-1])
                self.rows[idx] = None
            except Exception:
                pass
            self.tree.delete(sel)

    def refresh_prices(self):
        needed = []
        seen = set()
        for row in self.rows:
            if not row: continue
            sl, tr = row["slayer"], row["tier"]
            drops = [d for d in RARE_DROPS.get(sl, []) if d["tier"]==tr]
            drops += [d for d in MODERATE_DROPS.get(sl, []) if d["tier"]==tr]
            for c in COMMON_LOOT.get(sl, {}).get(tr, []):
                drops.append({"item":c["name"],"bz_id":c["bz_id"],"is_common":True,"avg_qty":c["avg_qty"],"base_pct":100.0*c["chance"]})
            for d in drops:
                # key for cache
                k = (d.get("cofl_tag") and ("AH",cofl_tag_sanitize(d.get("cofl_tag")))) or ("BZ",(d.get("bz_id") or default_bz_id_from_name(d.get("item") or d.get("name") or ""))).upper()
                if k in seen: continue
                seen.add(k); needed.append(d)

        def worker():
            if requests is None:
                messagebox.showwarning("Missing dependency", "Install 'requests' to enable live price fetching:\n\npip install requests")
                return
            for d in needed:
                self.mgr.resolve_drop(d)
            self.after(0, lambda: messagebox.showinfo("Prices", "Compare: price refresh complete."))

        threading.Thread(target=worker, daemon=True).start()

    def compute_all(self):
        results = []
        for iid in self.tree.get_children():
            self.tree.set(iid, "rate", "—")
            self.tree.set(iid, "coins_h", "—")

        for idx, row in enumerate(self.rows):
            if not row: continue
            sl, tr, mf, spawn, kill = row["slayer"], row["tier"], row["mf"], row["spawn"], row["kill"]
            if spawn<=0 or kill<=0: continue
            bosses_per_hour = 3600.0 / (spawn + kill)

            base_costs = SLAYER_COSTS.get(sl, {})
            cost = float(base_costs.get(tr, 0))

            total = 0.0
            for c in COMMON_LOOT.get(sl, {}).get(tr, []):
                info = self.mgr.resolve_drop({"item":c["name"], "bz_id":c["bz_id"]})
                price = info.get("price"); is_out = info.get("is_outlier", False)
                if price is None or (self.mgr.ignore_outliers and is_out): continue
                total += c["avg_qty"] * price * c["chance"]

            drops = [d for d in MODERATE_DROPS.get(sl, []) if d["tier"]==tr]
            drops += [d for d in RARE_DROPS.get(sl, []) if d["tier"]==tr]
            for d in drops:
                info = self.mgr.resolve_drop(d)
                price = info.get("price"); is_out = info.get("is_outlier", False)
                if price is None or (self.mgr.ignore_outliers and is_out): continue
                p_eff = effective_drop_chance(d["base_pct"], magic_find=mf)
                total += (p_eff/100.0) * price

            coins_h = bosses_per_hour * (total - cost)
            iid = list(self.tree.get_children())[idx]
            self.tree.set(iid, "rate", f"{bosses_per_hour:.2f}")
            self.tree.set(iid, "coins_h", fmt_num(coins_h))
            results.append(coins_h)

        if results:
            messagebox.showinfo("Compare", f"Best: {fmt_num(max(results))} coins/h")

# -------------------------------
# App
# -------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} ({APP_VERSION})")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(1100, 760)

        try:
            f_default = tkfont.nametofont("TkDefaultFont"); f_default.configure(family="Segoe UI", size=10)
            for name in ("TkMenuFont","TkTextFont","TkHeadingFont","TkTooltipFont"):
                if name in tkfont.names(): tkfont.nametofont(name).configure(family="Segoe UI", size=10)
        except Exception: pass

        self.style = ttk.Style(self)
        self.palette = Theme.DARK.copy()
        style_apply(self.style, self.palette)
        self.configure(bg=self.palette["bg"])

        self.debug_win = None
        self._debug_queue = []

        self.price_mgr = PriceManager(debug_cb=self.debug_log, prefer="auto", ignore_outliers=True, outlier_pct=15.0)

        self._build_menu()

        header = ttk.Frame(self, style="Sunken.TFrame"); header.pack(fill="x", padx=10, pady=(10,6))
        title = ttk.Label(header, text=f"{APP_TITLE} — {APP_VERSION}", font=("Segoe UI", 12, "bold"))
        title.pack(side="left", padx=(6,10))
        ttk.Button(header, text="Open Debug Log", command=self.open_debug, style="Accent.TButton").pack(side="right")

        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.single = SingleDropFrame(nb); nb.add(self.single, text="Single Drop")
        self.slayer = SlayerPresetsFrame(nb, self.single); nb.add(self.slayer, text="Slayer Presets")
        self.rates  = RatesFrame(nb, price_mgr=self.price_mgr, palette=self.palette); nb.add(self.rates, text="Rates / Profit")
        self.compare = CompareFrame(nb, price_mgr=self.price_mgr, palette=self.palette); nb.add(self.compare, text="Compare")

        status = ttk.Frame(self, style="Sunken.TFrame"); status.pack(fill="x", side="bottom")
        ttk.Label(status, text="Tip: EV = (RNG + Moderate + Common) − quest cost. Outliers flagged ⚠ by ±15% vs SOLD median.").pack(side="left", padx=10, pady=6)

    def _build_menu(self):
        menubar = tk.Menu(self)
        view = tk.Menu(menubar, tearoff=0); view.add_command(label="Debug Log", command=self.open_debug)
        menubar.add_cascade(label="View", menu=view)

        theme = tk.Menu(menubar, tearoff=0)
        theme.add_command(label="Dark", command=lambda: self.set_theme("dark"))
        theme.add_command(label="Light", command=lambda: self.set_theme("light"))
        menubar.add_cascade(label="Theme", menu=theme)

        helpm = tk.Menu(menubar, tearoff=0); helpm.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpm)

        self.config(menu=menubar)

    def debug_log(self, msg):
        if self.debug_win and self.debug_win.winfo_exists():
            try: self.debug_win.log(msg)
            except Exception: pass
        else:
            self._debug_queue.append(str(msg))

    def open_debug(self):
        try:
            if not self.debug_win or not self.debug_win.winfo_exists():
                self.debug_win = DebugWindow(self, self.palette)
                for m in self._debug_queue: self.debug_win.log(m)
                self._debug_queue.clear()
            self.debug_win.deiconify(); self.debug_win.lift()
        except Exception:
            self.debug_win = DebugWindow(self, self.palette)

    def set_theme(self, which):
        self.palette = Theme.DARK.copy() if which == "dark" else Theme.LIGHT.copy()
        style_apply(self.style, self.palette)
        self.configure(bg=self.palette["bg"])
        self.rates.set_palette(self.palette)
        for tv in (self.rates.tree, self.compare.tree):
            tv.tag_configure("odd", background=self.palette["row"][0])
            tv.tag_configure("even", background=self.palette["row"][1])
        if self.debug_win and self.debug_win.winfo_exists():
            self.debug_win.configure(bg=self.palette["bg"])
            self.debug_win.text.configure(bg=self.palette["sunken"], fg=self.palette["text"], insertbackground=self.palette["accent"])

    def show_about(self):
        messagebox.showinfo("About", f"{APP_TITLE} {APP_VERSION}\nTkinter tool for Hypixel SkyBlock RNG and Slayer profits.\nIncludes price sanity check, simulator, and compare.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
