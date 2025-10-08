"""
Streamlit Betting Analyzer (SIMULATION ONLY)

DESCRIPTION
- Local app for analyzing publicly available match odds and constructing "suggested" tickets for simulation/education only.
- DOES NOT place bets or interact with betting accounts.
- You must be 18+ to use for real betting; this app is intended for learning and backtesting.

FEATURES
- Load odds from: (A) TheOddsAPI (user supplies API key), (B) upload CSV/JSON export from bookmaker, or (C) sample dataset.
- Compute implied probabilities from decimal odds and adjust for bookmaker margin.
- Let the user input "true probability" estimates (or use simple model heuristics) for each match.
- Scan for value bets (true_prob > implied_prob) and show EV.
- Build candidate tickets (single, small accumulators) optimized for balance between EV and hit probability.
- Show percentage chance for accumulator using either implied probabilities or user-supplied true probabilities.
- Export suggested tickets to CSV and save daily snapshots.

REQUIREMENTS
- Python 3.8+
- Install packages: streamlit, pandas, requests, numpy

INSTALL
pip install streamlit pandas requests numpy

RUN
streamlit run streamlit_app.py

USAGE NOTES
- Provide your own API key for TheOddsAPI (https://the-odds-api.com) if you want live odds.
- Alternatively upload a CSV with columns: event_id, sport, home_team, away_team, market, outcome, odds_decimal
- The app will not place bets. It's an analysis tool only.

"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import math
import time
from datetime import datetime

st.set_page_config(page_title="Betting Analyzer (simulation only)", layout="wide")

st.title("Betting Analyzer — simulation / study only")
st.write("This app analyzes odds and suggests tickets for educational purposes. It does NOT place bets.")

# ------------------ Helper functions ------------------

def decimal_to_implied(odds):
    try:
        return 1.0 / float(odds)
    except Exception:
        return np.nan

def remove_margin(implied_probs):
    # simple proportional normalization to remove bookmaker overround
    s = np.nansum(implied_probs)
    if s == 0:
        return implied_probs
    return implied_probs / s

def load_sample_data():
    # small sample dataset built from user's earlier inputs (example)
    rows = [
        {"event_id":"1","sport":"soccer","home":"Čad","away":"Mali","market":"match_winner","outcome":"Mali","odds":1.19},
        {"event_id":"2","sport":"soccer","home":"Slávia TU Košice","away":"Považská Bystrica","market":"double_chance","outcome":"1X","odds":1.63},
        {"event_id":"3","sport":"icehockey","home":"Vimmerby","away":"Björklöven","market":"team_goals","outcome":"Vimmerby>1.5","odds":1.59},
        {"event_id":"4","sport":"soccer","home":"Stredoafr. rep.","away":"Ghana","market":"total_goals","outcome":"under3.5","odds":1.43},
        {"event_id":"5","sport":"soccer","home":"Omán","away":"Katar","market":"team_goals","outcome":"Oman>1.5","odds":1.56},
    ]
    return pd.DataFrame(rows)

# ------------------ Data source selection ------------------
st.sidebar.header("Data source")
source = st.sidebar.selectbox("Choose odds source", ["Sample data", "Upload CSV/JSON", "TheOddsAPI (requires key)"])

df = None

if source == "Sample data":
    df = load_sample_data()
    st.sidebar.info("Loaded sample dataset")

elif source == "Upload CSV/JSON":
    uploaded = st.sidebar.file_uploader("Upload CSV or JSON export", type=["csv","json"])
    if uploaded is not None:
        try:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_json(uploaded)
            st.sidebar.success("File loaded")
        except Exception as e:
            st.sidebar.error(f"Failed to load file: {e}")

else:
    st.sidebar.markdown("Use TheOddsAPI (or similar) to fetch live odds. You need an API key.")
    api_key = st.sidebar.text_input("TheOddsAPI key", value="", type="password")
    sport_key = st.sidebar.text_input("Sport key (e.g. soccer_epl, soccer) - optional", value="")
    if st.sidebar.button("Fetch live odds"):
        if not api_key:
            st.sidebar.error("Enter API key first")
        else:
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{sport_key or 'soccer'} /odds"
                # note: user must adjust endpoint; this call is illustrative only
                st.sidebar.info("Attempting to fetch - app will not place bets. If request fails, check API docs and key.")
                # We'll fallback to sample if fetch fails
                r = requests.get(f"https://api.the-odds-api.com/v4/sports", params={"apiKey":api_key}, timeout=10)
                if r.status_code == 200:
                    st.sidebar.success("Connected to API — fetching sample sports list. For full odds, use appropriate endpoints.")
                    sports = r.json()
                    st.sidebar.write("Available sports (sample):")
                    st.sidebar.write([s.get('key') for s in sports[:20]])
                    st.sidebar.info("For full odds fetch, set correct sport key and endpoint per TheOddsAPI docs.")
                else:
                    st.sidebar.error(f"API request failed: {r.status_code} — {r.text}")
                df = load_sample_data()
            except Exception as e:
                st.sidebar.error(f"Fetch failed: {e}")
                df = load_sample_data()

# ------------------ Data preparation ------------------
if df is None:
    st.info("No data loaded yet — choose a source on the left.")
    st.stop()

# Ensure columns
required_cols = ["event_id","sport","home","away","market","outcome","odds"]
for c in required_cols:
    if c not in df.columns:
        # try to rename common variants
        possible = {"home_team":"home","away_team":"away","odds_decimal":"odds","bookmaker":"market"}
        if c in possible and possible[c] in df.columns:
            df = df.rename(columns={possible[c]: c})

# Clean and compute implied probabilities
df['odds'] = pd.to_numeric(df['odds'], errors='coerce')
df['implied'] = df['odds'].apply(decimal_to_implied)

# Group by event to remove margin
implied_by_event = df.groupby('event_id')['implied'].apply(list).to_dict()

# normalize per event
norm_implied = []
for eid, probs in implied_by_event.items():
    arr = np.array(probs, dtype=float)
    if np.any(np.isnan(arr)):
        norm = arr
    else:
        s = arr.sum()
        if s <= 0:
            norm = arr
        else:
            norm = arr / s
    norm_implied.append((eid, norm))

# create a mapping
norm_map = {}
for eid, norm in norm_implied:
    norm_map[eid] = norm

# attach normalized implied back to df
def get_norm_implied(row):
    arr = norm_map.get(row['event_id'])
    if arr is None:
        return row['implied']
    # find index of this outcome among event rows
    sub = df[df['event_id']==row['event_id']].reset_index()
    try:
        idx = sub[sub['outcome']==row['outcome']].index[0]
        return float(arr[idx])
    except Exception:
        # fallback
        return row['implied']

st.subheader("Loaded matches & odds")

# let user optionally input "true probability" for each row, or use implied
use_user_p = st.checkbox("I will provide my own probability estimates (otherwise implied will be used)")

if use_user_p:
    st.info("Enter your probability estimates in percent in the table. Leave blank to use implied.")
    df['user_p_percent'] = ''
    edited = st.experimental_data_editor(df[['event_id','home','away','outcome','odds','implied','user_p_percent']], num_rows="dynamic")
    # merge back
    df = df.merge(edited[['event_id','outcome','user_p_percent']], on=['event_id','outcome'], how='left')
    def parse_user_p(x, implied):
        try:
            if x is None or x=='' or (isinstance(x,str) and x.strip()==''):
                return implied
            v = float(x)/100.0
            return min(max(v,0.0),1.0)
        except Exception:
            return implied
    df['true_p'] = df.apply(lambda r: parse_user_p(r['user_p_percent'], get_norm_implied(r)), axis=1)
else:
    df['true_p'] = df.apply(lambda r: get_norm_implied(r), axis=1)

# compute edge (true_p - implied)
df['implied_norm'] = df.apply(lambda r: get_norm_implied(r), axis=1)
df['edge'] = df['true_p'] - df['implied_norm']

df_display = df.copy()
df_display['implied_percent'] = (df_display['implied_norm']*100).round(2)
df_display['true_percent'] = (df_display['true_p']*100).round(2)
df_display['edge_percent'] = (df_display['edge']*100).round(2)

st.dataframe(df_display[['event_id','sport','home','away','outcome','odds','implied_percent','true_percent','edge_percent']])

# ------------------ Value scanner ------------------
st.subheader("Value bets scanner")
min_edge = st.slider("Minimum edge (%) to flag as value", -10.0, 50.0, 5.0)
value_bets = df[df['edge'] >= (min_edge/100.0)].copy()

st.write(f"Found {len(value_bets)} value bets with edge >= {min_edge}%")
if len(value_bets)>0:
    st.table(value_bets[['event_id','home','away','outcome','odds','implied_percent','true_percent','edge_percent']])

# ------------------ Ticket builder ------------------
st.subheader("Ticket builder (suggested educational tickets)")
max_legs = st.slider("Max legs per ticket", 1, 4, 3)
strategy = st.radio("Ticket construction strategy", ["Top edge first","Max EV per stake","Balanced (edge + implied)"])

# create candidate legs (prefer value bets)
candidates = df.sort_values(by='edge', ascending=False).reset_index(drop=True)

# helper to compute accumulator implied probability and payout
from itertools import combinations

def acc_payout_and_prob(legs, use_true_p=False):
    prod_odds = 1.0
    probs = 1.0
    for l in legs:
        prod_odds *= l['odds']
        probs *= (l['true_p'] if use_true_p else l['implied_norm'])
    return prod_odds, probs

# build tickets
tickets = []
rows = candidates.to_dict('records')
for r in range(1, max_legs+1):
    for comb in combinations(rows, r):
        prod_odds, prod_prob = acc_payout_and_prob(comb, use_true_p=False)
        prod_odds_true, prod_prob_true = acc_payout_and_prob(comb, use_true_p=True)
        ev = sum([c['true_p'] * (c['odds'] - 1) for c in comb]) # rough EV per leg
        tickets.append({
            'legs': [f"{c['home']} vs {c['away']} : {c['outcome']} ({c['odds']})" for c in comb],
            'combined_odds': round(prod_odds,3),
            'implied_prob': prod_prob,
            'true_prob': prod_prob_true,
            'ev_est': round(ev,3)
        })

tickets_df = pd.DataFrame(tickets)

# sort tickets by strategy
if strategy == 'Top edge first':
    tickets_df = tickets_df.sort_values(by='true_prob', ascending=False)
elif strategy == 'Max EV per stake':
    tickets_df = tickets_df.sort_values(by='ev_est', ascending=False)
else:
    tickets_df = tickets_df.sort_values(by=['true_prob','ev_est'], ascending=[False,False])

st.write(f"Found {len(tickets_df)} candidate tickets")
if len(tickets_df)>0:
    st.dataframe(tickets_df[['legs','combined_odds','implied_prob','true_prob','ev_est']].head(50))

# allow export
if st.button('Export top tickets to CSV'):
    out = tickets_df[['legs','combined_odds','implied_prob','true_prob','ev_est']]
    out.to_csv('suggested_tickets.csv', index=False)
    st.success('Saved suggested_tickets.csv')

# save daily snapshot
if st.button('Save daily snapshot (local)'):
    fname = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(fname, index=False)
    st.success(f"Saved snapshot as {fname}")

st.write('---')
st.write('Reminder: This tool is for education/simulation only. Do not use to place real bets while underage.')

# end of app
