#API key for CMC 6743d92f-e074-4b89-81ce-04fca3f6e47b
import time
import csv
from datetime import datetime
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from colorama import init, Fore, Style
import matplotlib.pyplot as plt

init(autoreset=True)
datetime_at_start=datetime.now()
symbol = input("Enter a 3-letter cryptocurrency code in capital letters e.g. BTC for Bitcoin, ETH for Ethereum, SOL for Solana, BNB for Build and Build (Binance) ").upper()
answer = input("Would you like to save data from different instances in different files or same files? Type D for different files. Type S for same files.")
if answer == 'D':
    print("Preference saved")
    csv_file = f"{symbol.lower()}_prices_starting_from{datetime.now().strftime('%Y-%m-%d')}.csv"
if answer == 'S':
    print("Preference saved")
    csv_file = f"{symbol.lower()}_prices.csv"
print(f"\nTracking {symbol} to USD...")

try:
    with open(csv_file, 'x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', f'{symbol} Price (USD)', 'Price Change Summary', 'Market Gist', 'Detected Pattern', 'Accuracy (%)'])
except FileExistsError:
    pass

price_history = []
predictions = []
correct_predictions = 0
total_predictions = 0

def detect_pattern(price_history):
    if len(price_history) < 100:
        return "No Pattern"
    p = price_history[-100:]
    if p[-5] < p[-4] < p[-3] < p[-2] < p[-1]:
        return "Ascending Triangle / Bullish"
    elif p[-5] > p[-4] > p[-3] > p[-2] > p[-1]:
        return "Descending Triangle / Bearish"
    elif p[-5] < p[-4] > p[-3] < p[-2] > p[-1]:
        return "Triple Top / Bearish"
    elif p[-5] > p[-4] < p[-3] > p[-2] < p[-1]:
        return "Triple Bottom / Bullish"
    elif p[-4] < p[-5] and p[-4] < p[-3] and p[-2] > p[-3] and p[-1] < p[-2]:
        return "Head and Shoulders / Bearish"
    elif p[-4] > p[-5] and p[-4] > p[-3] and p[-2] < p[-3] and p[-1] > p[-2]:
        return "Inverted Head and Shoulders / Bullish"
    elif (p[-5] < p[-4] and p[-3] < p[-4] and p[-3] > p[-2] and p[-2] < p[-1]):
        return "Double Bottom / Bullish"
    elif (p[-5] > p[-4] and p[-3] > p[-4] and p[-3] < p[-2] and p[-2] > p[-1]):
        return "Double Top / Bearish"
    elif abs(p[-5] - p[-1]) < 0.2 * p[-5] and (max(p[-5:]) - min(p[-5:])) > 0.05 * p[-5]:
        return "Symmetrical Triangle / Neutral"
    return "No Pattern"

plt.ion()
fig, ax = plt.subplots(figsize=(8, 4))

while True:
    print(f"\nStarting request for {symbol}...")

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': symbol,
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'Accept-Encoding': 'deflate, gzip',
        'X-CMC_PRO_API_KEY': '6743d92f-e074-4b89-81ce-04fca3f6e47b',  # Reminder to insert api key
    }

    try:
        response = requests.get(url, headers=headers, params=parameters, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data['data'][symbol]['quote']['USD']['price']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - {symbol} Price: ${price:.2f}")
        price_history.append(price)
        if len(price_history) > 100:
            price_history.pop(0)

        if len(predictions) > 0:
            prev_prediction, prev_price = predictions.pop(0)
            actual_change = price - prev_price
            if ("Bullish" in prev_prediction and actual_change > 0) or ("Bearish" in prev_prediction and actual_change < 0):
                correct_predictions += 1
            total_predictions += 1

        if len(price_history) == 100:
            differences = [price_history[i+1] - price_history[i] for i in range(9)]
            diff_strings = ["{:+.2f}".format(d) for d in differences]
            positive_count = sum(1 for d in differences if d > 0)
            if positive_count >= 6:
                market_gist = "Bullish"
            elif positive_count <= 3:
                market_gist = "Bearish"
            else:
                weights = list(range(1, 100))
                weighted_sum = sum(weights[i] * differences[i] for i in range(9))
                market_gist = "Bullish" if weighted_sum > 0 else "Bearish"

            pattern = detect_pattern(price_history)
            if "Bullish" in pattern:
                market_gist += " + Pattern Bullish Influence"
            elif "Bearish" in pattern:
                market_gist += " + Pattern Bearish Influence"

            predictions.append((market_gist, price))
            accuracy = (correct_predictions / total_predictions * 100) if total_predictions else 0
            accuracy_str = f"{accuracy:.2f}%"
            total_change = sum(differences)
            print("Correct Predicitons:", correct_predicitons)
            wrong_predictions = total_predictions - correct_predictions
            print("Wrong Predictions:", wrong_predictions)

            color = Fore.GREEN if "Bullish" in market_gist else Fore.RED
            print(f"Price differences: {', '.join(diff_strings)}")
            print(color + f"Market Gist: {market_gist} ({total_change:+.2f})")
            print(Fore.YELLOW + f"Detected Pattern: {pattern}")
            print(Fore.CYAN + f"Prediction Accuracy: {accuracy_str}")
            print(Style.RESET_ALL + "-" * 40)

            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, f"{price:.2f}", ' / '.join(diff_strings), f"{market_gist} ({total_change:+.2f})", pattern, accuracy_str])

            ax.clear()
            ax.plot(price_history, marker='o', linestyle='-', color='red')
            ax.set_title(f"{symbol} Price History - Last 10 Points\nPattern: {pattern}")
            ax.set_xlabel("Point")
            ax.set_ylabel(f"{symbol} Price (USD)")
            ax.grid(True)
            fig.tight_layout()
            fig.canvas.draw()
            plt.pause(60)
        else:
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, f"{price:.2f}", '', '', '', ''])
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(Fore.RED + f"Request failed. Check Wi-Fi.: {e}")
    except requests.HTTPError as http_err:
        if response.status_code == 429:
            print(Fore.YELLOW + "Rate limit exceeded. Waiting 10 min...")
            time.sleep(60)
        else:
            print(Fore.RED + f"HTTP error occurred. Error code: {http_err}")
    except Exception as err:
        print(Fore.RED + f"An Error Occurred. Error code: {err}")
