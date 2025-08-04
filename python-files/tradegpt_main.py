def main():
    # Sample GPT-style analysis
    import pandas as pd
    data = pd.read_csv('stock_data.csv')
    for index, row in data.iterrows():
        signal = ''
        if row['RSI'] < 30 and row['MACD'] < 0:
            signal = 'Buy'
        elif row['RSI'] > 70 and row['MACD'] > 0:
            signal = 'Sell'
        else:
            signal = 'Hold'
        print(f"{row['Stock']} - {signal}: RSI={row['RSI']}, MACD={row['MACD']}")

if __name__ == "__main__":
    main()
