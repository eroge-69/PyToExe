import tkinter as tk

# --- Logic Functions ---

def get_crop_recommendation(season):
    crops = {
        "summer": ["Maize", "Cotton", "Paddy", "Groundnut"],
        "winter": ["Wheat", "Mustard", "Barley", "Peas"],
        "monsoon": ["Rice", "Sugarcane", "Jute", "Soybean"]
    }
    return crops.get(season.lower(), ["No info for that season."])

def get_fertilizer(crop):
    recommendations = {
        "wheat": "Use NPK 120:60:40 kg/ha",
        "rice": "Use Urea and DAP in split doses",
        "cotton": "Use 100:50:50 NPK and micronutrients",
        "maize": "Urea and Potash are good choices"
    }
    return recommendations.get(crop.lower(), "No fertilizer data for that crop.")

def get_disease_tip(crop):
    tips = {
        "wheat": "Use fungicide for rust; ensure proper spacing.",
        "rice": "Prevent blast disease by draining fields.",
        "cotton": "Use neem-based pesticide for whiteflies."
    }
    return tips.get(crop.lower(), "No disease info for that crop.")

# --- GUI Functions ---

def process_query():
    query = input_entry.get().lower()
    response = ""

    if "crop" in query or "फसल" in query:
        season = season_entry.get()
        crops = get_crop_recommendation(season)
        response = f"🌱 Recommended crops for {season.capitalize()}: {', '.join(crops)}"

    elif "fertilizer" in query or "उर्वरक" in query:
        crop = crop_entry.get()
        response = f"🧪 Fertilizer for {crop.capitalize()}: {get_fertilizer(crop)}"

    elif "disease" in query or "रोग" in query:
        crop = crop_entry.get()
        response = f"🛡️ Disease tips for {crop.capitalize()}: {get_disease_tip(crop)}"

    elif "weather" in query or "मौसम" in query:
        response = "☀️ Weather info: Hot in summer, cool in winter, rainy in monsoon."

    else:
        response = "❗ Please ask about crops, fertilizers, disease or weather."

    output_label.config(text=response)

# --- GUI Setup ---

root = tk.Tk()
root.title("🌾 KrishiBot – Agriculture Assistant")
root.geometry("500x400")

tk.Label(root, text="👨‍🌾 Welcome to KrishiBot!", font=("Arial", 16)).pack(pady=10)
tk.Label(root, text="Ask about crops, fertilizers, disease tips, or weather").pack()

input_entry = tk.Entry(root, width=50)
input_entry.pack(pady=5)

tk.Label(root, text="Season (summer/winter/monsoon):").pack()
season_entry = tk.Entry(root)
season_entry.pack(pady=5)

tk.Label(root, text="Crop Name:").pack()
crop_entry = tk.Entry(root)
crop_entry.pack(pady=5)

tk.Button(root, text="Ask KrishiBot", command=process_query, bg="green", fg="white").pack(pady=10)

output_label = tk.Label(root, text="", wraplength=450, fg="blue", font=("Arial", 12))
output_label.pack(pady=20)

root.mainloop()
