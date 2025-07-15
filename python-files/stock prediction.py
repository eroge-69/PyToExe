import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

print("📊 Welcome to Stock Price Predictor (AI Powered)")
stock_symbol = input("Enter the stock symbol (e.g. TCS.NS, INFY.NS): ").strip()

# ----- Step 1: Download Stock Data -----
try:
    stock = yf.Ticker(stock_symbol)
    data = stock.history(period="1y")
    data = data[["Close"]]
    if data.empty:
        print("❌ No data found. Check the stock symbol.")
        exit()
except Exception as e:
    print(f"Error fetching data: {e}")
    exit()

# ----- Step 2: Prepare Data -----
future_days = 10
data['Prediction'] = data[['Close']].shift(-future_days)

X = np.array(data.drop(['Prediction'], axis=1))[:-future_days]
y = np.array(data['Prediction'])[:-future_days]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# ----- Step 3: Train Model -----
model = LinearRegression()
model.fit(X_train, y_train)

# ----- Step 4: Predict -----
X_future = np.array(data.drop(['Prediction'], axis=1)[-future_days:])
predictions = model.predict(X_future)

# ----- Step 5: Get Current Price -----
current_price = data['Close'].iloc[-1]
print(f"\n📌 Current Price of {stock_symbol.upper()}: ₹{current_price:.2f}")

# ----- Step 6: Show Predictions -----
print(f"\n🔮 Predicted Prices for Next {future_days} Days:")
prediction_dates = []
prediction_values = []

for i, price in enumerate(predictions, 1):
    future_date = (datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d")
    print(f"{future_date}: ₹{price:.2f}")
    prediction_dates.append(future_date)
    prediction_values.append(round(price, 2))

# ----- Step 7: Export to Excel -----
df_export = pd.DataFrame({
    "Date": prediction_dates,
    "Predicted Price": prediction_values
})

# Add current price as header/info
current_row = pd.DataFrame([["Current", round(current_price, 2)]], columns=["Date", "Predicted Price"])
df_export = pd.concat([current_row, df_export], ignore_index=True)

file_name = f"Stock_Prediction_{stock_symbol.replace('.', '_')}.xlsx"
df_export.to_excel(file_name, index=False)
print(f"\n✅ Prediction saved to Excel file: {file_name}")

# ----- Step 8: Plot Graph -----
valid = data[-future_days:].copy()
valid['Predictions'] = predictions

plt.figure(figsize=(10, 5))
plt.title(f"{stock_symbol.upper()} Price Prediction")
plt.plot(data['Close'], label="Historical Price")
plt.plot(valid['Predictions'], label="Predicted Price", color='red')
plt.xlabel("Date")
plt.ylabel("Price (INR)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
