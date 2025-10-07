import os
import csv
import datetime
import yfinance as yf
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- Einstellungen ---
SAVE_PATH = r"C:\DAX_Forecast"
CSV_FILE = os.path.join(SAVE_PATH, "dax_forecast_log.csv")

# --- Hilfsfunktionen ---

def get_yfinance_change(ticker, period="2d"):
    """Berechnet prozentuale Veränderung zwischen letztem Schluss und aktuellem Kurs"""
    data = yf.download(ticker, period=period, interval="15m", progress=False)
    if len(data) < 2:
        return 0.0
    prev_close = data["Close"].iloc[-2]
    last = data["Close"].iloc[-1]
    change = (last - prev_close) / prev_close * 100
    return round(change, 2)

def get_sentiment_from_news():
    """Einfaches News-Sentiment von Yahoo Finance"""
    url = "https://finance.yahoo.com/rss/topstories"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return 0.0
    analyzer = SentimentIntensityAnalyzer()
    text = r.text.lower()
    sentiment = analyzer.polarity_scores(text)["compound"]
    return round(sentiment * 100, 2)

# --- Hauptberechnung ---
def calculate_probability():
    dax = get_yfinance_change("^GDAXI")
    nikkei = get_yfinance_change("^N225")
    hang_seng = get_yfinance_change("^HSI")
    sp_fut = get_yfinance_change("ES=F")
    news_sent = get_sentiment_from_news()

    # Gewichtungen – empirisch angepasst
    score = (
        0.40 * dax +
        0.20 * ((nikkei + hang_seng) / 2) +
        0.25 * sp_fut +
        0.15 * (news_sent / 10)
    )

    prob_up = 1 / (1 + pow(2.71828, -score / 2))
    prob_down = 1 - prob_up
    return round(prob_up * 100, 2), round(prob_down * 100, 2), dax, nikkei, hang_seng, sp_fut, news_sent

# --- Logging ---
def log_result():
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    now = datetime.datetime.now()
    prob_up, prob_down, dax, nikkei, hang_seng, sp_fut, news_sent = calculate_probability()

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["Datum", "Prob_Up(%)", "Prob_Down(%)", "DAX(%)", "Nikkei(%)", "HangSeng(%)", "S&P_Fut(%)", "News_Sent"])
        writer.writerow([now.strftime("%Y-%m-%d"), prob_up, prob_down, dax, nikkei, hang_seng, sp_fut, news_sent])

    print(f"[{now.strftime('%Y-%m-%d %H:%M')}] DAX steigt: {prob_up}% | fällt: {prob_down}%")
    print(f"DAX={dax:.2f}%  Nikkei={nikkei:.2f}%  HangSeng={hang_seng:.2f}%  S&P_Fut={sp_fut:.2f}%  News={news_sent:.2f}")

if __name__ == "__main__":
    log_result()
