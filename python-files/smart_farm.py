import requests
from datetime import datetime
import random

API_KEY = "7c6c98c7fa6dcadeb7672307941cd69a"
CITY = "Karachi"

crops = {
    "corn": {"days": 90, "cost": 12000, "yield": 700, "price": 35, "season": "summer"},
    "wheat": {"days": 120, "cost": 10000, "yield": 1200, "price": 45, "season": "winter"},
    "rice": {"days": 150, "cost": 15000, "yield": 900, "price": 55, "season": "summer"},
    "tomato": {"days": 80, "cost": 8000, "yield": 600, "price": 80, "season": "all"}
}

crop_choice = input(f"Hi! Which crop are you planning to grow today? {list(crops.keys())}: ").lower()

if crop_choice not in crops:
    print("Oops! That crop is not in our database.")
else:
    crop_info = crops[crop_choice]

    while True:
        try:
            land_size = float(input("Great! How many acres do you have? "))
            if land_size <= 0:
                print("Hmm, land size should be more than zero.")
                continue
            break
        except:
            print("Please enter a number for the land size.")

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print("Sorry, I couldn't fetch the weather data right now.")
    else:
        print(f"\nLet's see how your {crop_choice} might grow in {CITY}.\n")
        print(f"It usually takes about {crop_info['days']} days to grow.")
        print(f"Estimated cost per acre: Rs {crop_info['cost']}")
        print("\nHeads up: This is a prototype. Results aren't guaranteed.\n")

        base_forecast = data["list"][:8]
        simulated_weather = []

        for day in range(30):
            entry = random.choice(base_forecast)
            temp = entry["main"]["temp"] + random.uniform(-3,3)
            weather = entry["weather"][0]["main"]
            simulated_weather.append({"temp": temp, "weather": weather})

        def calculate_penalty(weather_list):
            rain_warning = False
            heat_warning = False
            growth_penalty = 0
            temps = []

            for day_data in weather_list:
                temp = day_data["temp"]
                weather = day_data["weather"]
                temps.append(temp)

                if weather.lower() == "rain":
                    rain_warning = True
                    growth_penalty += 2
                if temp > 38:
                    heat_warning = True
                    growth_penalty += 5

            avg_temp = sum(temps) / len(temps)
            if avg_temp < 20:
                current_season = "winter"
            elif avg_temp > 30:
                current_season = "summer"
            else:
                current_season = "moderate"

            return growth_penalty, rain_warning, heat_warning, current_season

        growth_penalty, rain_warning, heat_warning, current_season = calculate_penalty(simulated_weather)

        if rain_warning:
            print("Looks like rain may occur this month. Growth could be affected.")
        if heat_warning:
            print("High temperatures are expected. Your crop might be stressed.")

        if crop_info["season"] != "all" and crop_info["season"] != current_season:
            print(f"Note: {crop_choice.capitalize()} is usually a {crop_info['season']} crop, but the current season seems {current_season}. Risk of failure is higher.")

        total_days = crop_info["days"] + growth_penalty
        yield_factor = max(0, 1 - (growth_penalty * 0.01))
        yield_est = max(0, crop_info["yield"] * yield_factor * land_size)
        extra_costs = 0.2 * crop_info["cost"] * land_size
        market_factor = 0.85
        revenue = yield_est * crop_info["price"] * market_factor
        profit = revenue - (crop_info["cost"] * land_size + extra_costs)

        print(f"\nExpected Yield: {int(yield_est)} kg")
        print(f"Expected Revenue: Rs {int(revenue)}")
        print(f"Estimated Profit: Rs {int(profit)}")

        best_crop = None
        best_profit = float('-inf')
        for c_name, info in crops.items():
            y_factor = max(0, 1 - (growth_penalty * 0.01))
            y_est = max(0, info["yield"] * y_factor * land_size)
            rev = y_est * info["price"] * market_factor
            prof = rev - (info["cost"] * land_size + 0.2 * info["cost"] * land_size)

            if info["season"] != "all" and info["season"] != current_season:
                prof *= 0.5  # penalize risky-season crops

            if prof > best_profit:
                best_profit = prof
                best_crop = c_name

        print(f"\nBased on this simulation, the crop I’d recommend for you right now is: {best_crop.capitalize()} 🟢")
        print("\nRemember, weather beyond 5 days is estimated. This is a best-effort simulation, not a guarantee.")