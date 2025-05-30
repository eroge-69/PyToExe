import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font as tkFont
import random

# --- Style Definitions ---
BG_PRIMARY = "#212121"  # Very dark grey, almost black
BG_SECONDARY = "#2C2C2C" # Dark grey
BG_LABELFRAME = "#292929"
FG_PRIMARY = "#E0E0E0"  # Light grey for text
FG_ACCENT = "#A0A0A0"   # Medium grey for less important text / borders
ACCENT_COLOR_A = "#00BFA5" # Teal accent
ACCENT_COLOR_B = "#00A0A0" # Darker Teal for highlights/active
TEXT_INPUT_BG = "#3C3C3C"
TEXT_INPUT_FG = "#E0E0E0"
BUTTON_BG = ACCENT_COLOR_B
BUTTON_FG = "#FFFFFF" # White text on buttons
BUTTON_ACTIVE_BG = ACCENT_COLOR_A
BORDER_COLOR = "#4A4A4A"

FONT_FAMILY_MAIN = "Segoe UI"
FONT_FAMILY_FALLBACK = "Calibri" # Broader compatibility if Segoe UI isn't present
FONT_FAMILY_MONO = "Consolas"
FONT_FAMILY_MONO_FALLBACK = "Courier New"

try:
    # Check if primary font is available
    tk.Label(font=(FONT_FAMILY_MAIN, 10))
    BASE_FONT = FONT_FAMILY_MAIN
except tk.TclError:
    BASE_FONT = FONT_FAMILY_FALLBACK

try:
    tk.Text(font=(FONT_FAMILY_MONO, 10))
    MONO_FONT = FONT_FAMILY_MONO
except tk.TclError:
    MONO_FONT = FONT_FAMILY_MONO_FALLBACK

FONT_NORMAL = (BASE_FONT, 11)
FONT_BOLD = (BASE_FONT, 11, "bold")
FONT_LARGE = (BASE_FONT, 14, "bold")
FONT_XLARGE = (BASE_FONT, 18, "bold")
FONT_SMALL = (BASE_FONT, 9)
FONT_TINY = (BASE_FONT, 8)
FONT_OUTPUT = (MONO_FONT, 10)

# --- Ingredient Class ---
class Ingredient:
    def __init__(self, name, category, min_pct, max_pct, natural_organic_status,
                 benefits=None, ph_impact="neutral", interactions=None, notes="", color=None, scent=None,
                 is_broad_spectrum=False):
        self.name = name
        self.category = category
        self.min_pct = min_pct
        self.max_pct = max_pct
        self.natural_organic_status = natural_organic_status
        self.benefits = benefits if benefits is not None else []
        self.ph_impact = ph_impact
        self.interactions = interactions if interactions is not None else []
        self.notes = notes
        self.color = color
        self.scent = scent
        self.is_broad_spectrum = is_broad_spectrum

    def __repr__(self):
        return f"{self.name} ({self.category})"

# --- Ingredient Database (Reduced for brevity in this example, use your full DB) ---
INGREDIENTS_DB = [
    # --- Emulsifiers (Oil-in-Water) ---
    Ingredient("Glyceryl Stearate SE", "Emulsifier", 3, 7, "None", notes="Common O/W emulsifier"),
    Ingredient("Cetearyl Olivate (and) Sorbitan Olivate (Olivem 1000)", "Emulsifier", 5, 8, "Organic", notes="COSMOS approved, derived from olive oil"),
    Ingredient("Polyglyceryl-3 Polyricinoleate", "Emulsifier", 2, 5, "Natural", notes="Often used in W/O but adaptable for O/W as co-emulsifier"),
    Ingredient("Steareth-21 (and) Steareth-2", "Emulsifier", 3, 6, "None", notes="Robust synthetic emulsifiers"),
    Ingredient("Cetearyl Glucoside", "Emulsifier", 3, 6, "Natural", notes="Mild, good for sensitive skin"),
    Ingredient("Sodium Stearoyl Lactylate", "Emulsifier", 1, 3, "Natural", notes="Co-emulsifier/emulsifier, skin conditioning"),
    Ingredient("Lecithin", "Emulsifier", 1, 3, "Natural", benefits=["emollient"], notes="Can also act as co-emulsifier"),
    # --- Preservatives ---
    Ingredient("Phenoxyethanol (and) Ethylhexylglycerin (Euxyl PE 9010)", "Preservative", 0.5, 1.0, "None", notes="Broad-spectrum, very common", is_broad_spectrum=True),
    Ingredient("Benzyl Alcohol (and) Salicylic Acid (and) Glycerin (and) Sorbic Acid (Geogard ECT)", "Preservative", 0.6, 1.0, "Natural", ph_impact="acidic", notes="COSMOS approved, natural", is_broad_spectrum=True),
    Ingredient("Sodium Benzoate (and) Potassium Sorbate", "Preservative", 0.5, 1.0, "Natural", ph_impact="acidic", notes="Needs acidic pH and often a chelator"),
    Ingredient("Caprylhydroxamic Acid (and) Glyceryl Caprylate (and) Glycerin (Spectrastat)", "Preservative", 1.0, 1.5, "Natural", notes="Broad-spectrum preservation", is_broad_spectrum=True),
    # --- Stabilizers / Thickeners ---
    Ingredient("Xanthan Gum", "Stabilizer", 0.1, 0.5, "Natural", notes="Strong thickener, gelling agent"),
    Ingredient("Carbomer", "Stabilizer", 0.1, 0.5, "None", ph_impact="acidic", notes="Very effective thickener/gelling agent, needs neutralization"),
    Ingredient("Cetyl Alcohol", "Stabilizer", 1, 3, "Natural", benefits=["emollient", "co-emulsifier"]),
    # --- Emollients ---
    Ingredient("Caprylic/Capric Triglyceride", "Emollient", 5, 15, "Natural", benefits=["skin conditioning", "light feel"]),
    Ingredient("Squalane (Plant-derived)", "Emollient", 2, 10, "Natural", benefits=["moisturizing", "skin softening", "biomimetic"]),
    # --- Carrier Oils ---
    Ingredient("Jojoba Oil", "Carrier Oil", 5, 15, "Organic", benefits=["non-comedogenic", "balancing", "moisturizing"]),
    Ingredient("Sweet Almond Oil", "Carrier Oil", 5, 20, "Natural", benefits=["nourishing", "softening", "moisturizing"]),
    # --- Co-Emulsifiers / Humectants ---
    Ingredient("Glycerin", "Co-Emulsifier", 3, 10, "Natural", benefits=["humectant", "moisturizing"]),
    Ingredient("Propanediol", "Co-Emulsifier", 2, 5, "Natural", benefits=["humectant", "solvent"]),
    # --- Active Ingredients ---
    Ingredient("Retinol (encapsulated)", "Active", 0.1, 0.5, "None", benefits=["anti-aging", "collagen boosting", "cell turnover"], interactions=[("Vitamin C (L-Ascorbic Acid)", "Potential instability if not formulated correctly")]),
    Ingredient("Bakuchiol", "Active", 0.5, 1.0, "Natural", benefits=["anti-aging", "retinol alternative", "anti-inflammatory"]),
    Ingredient("Palmitoyl Tripeptide-1 (and) Palmitoyl Tetrapeptide-7 (Matrixyl 3000)", "Active", 1, 5, "None", benefits=["collagen boosting", "firming"]),
    Ingredient("Hyaluronic Acid (Low Molecular Weight)", "Active", 0.1, 1.0, "Natural", benefits=["hydration", "plumping"]),
    Ingredient("Ascorbyl Glucoside (Vitamin C derivative)", "Active", 2, 5, "None", benefits=["antioxidant", "brightening", "collagen production"]),
    Ingredient("Coenzyme Q10 (Ubiquinone)", "Active", 0.1, 0.5, "None", benefits=["antioxidant", "energy production"]),
    Ingredient("Green Tea Extract (Camellia Sinensis Leaf Extract)", "Active", 1, 3, "Natural", benefits=["antioxidant", "anti-inflammatory"]),
    Ingredient("Niacinamide (Vitamin B3)", "Active", 2, 5, "None", benefits=["barrier support", "anti-aging", "redness reduction"], interactions=[("L-Ascorbic Acid (Vitamin C)", "Can form nicotinic acid at high temps/low pH, causing flushing")]),
    Ingredient("Colloidal Oatmeal (Avena Sativa Kernel Flour)", "Active", 1, 5, "Natural", benefits=["soothing", "anti-inflammatory", "skin protectant"]),
    Ingredient("Salicylic Acid", "Active", 0.5, 2.0, "None", ph_impact="acidic", notes="Max 2% in leave-on products in UK.", benefits=["exfoliating", "oil soluble", "anti-inflammatory"]),
    Ingredient("Tea Tree Oil (Melaleuca Alternifolia Leaf Oil)", "Active", 0.5, 1.5, "Natural", benefits=["antimicrobial", "anti-inflammatory"], notes="Can be irritating at higher concentrations. Strong scent."),
    Ingredient("Zinc PCA", "Active", 0.5, 1.5, "None", benefits=["sebum regulating", "anti-bacterial"]),
    Ingredient("Allantoin", "Active", 0.1, 0.5, "Natural", benefits=["soothing", "skin healing", "protectant"]),
    Ingredient("Panthenol (Vitamin B5)", "Active", 1, 5, "None", benefits=["moisturizing", "wound healing", "soothing"]),
    Ingredient("Centella Asiatica Extract (Cica)", "Active", 1, 5, "Natural", benefits=["healing", "soothing", "collagen synthesis"]),
    # --- Crystal Actives ---
    Ingredient("Clear Quartz Powder (Micronized)", "Active", 0.1, 2.0, "Natural", benefits=["light diffusion", "brightening", "aesthetic"], notes="For visual radiance and 'energy' concept."),
    Ingredient("Amethyst Powder (Micronized)", "Active", 0.1, 2.0, "Natural", benefits=["calming aesthetic", "subtle purple hue", "aesthetic"], notes="For a 'calming' feel and subtle color."),
    # --- Pigmentation Color ---
    Ingredient("Iron Oxides (CI 77491)", "Colorant", 0.01, 2.0, "Natural", color="red"),
    Ingredient("Iron Oxides (CI 77492)", "Colorant", 0.01, 2.0, "Natural", color="yellow"),
    Ingredient("Mica", "Colorant", 0.01, 5.0, "Natural", color="shimmer"),
    # --- Scent ---
    Ingredient("Lavender Essential Oil", "Scent", 0.05, 0.5, "Natural", scent="lavender", notes="Contains allergens (Linalool, Limonene). Max levels apply."),
    Ingredient("Geranium Essential Oil", "Scent", 0.05, 0.5, "Natural", scent="geranium", notes="Contains allergens (Citronellol, Geraniol, Linalool). Max levels apply."),
    Ingredient("Sweet Orange Essential Oil", "Scent", 0.05, 0.5, "Natural", scent="orange", notes="Can be photosensitizing; use photosensitizing-free or below max levels."),
    # --- Sunblock (Zinc Oxide for SPF) ---
    Ingredient("Zinc Oxide", "Active", 1, 25, "Natural", benefits=["sunscreen", "UVA/UVB protection", "soothing"], notes="Primary UV filter (requires testing for SPF claim). Also a colorant.")
]
# (Your full INGREDIENTS_DB, UK_PRESERVATIVE_LIMITS, and MAX_TOTAL_PRIMARY_PRESERVATIVE_LOAD should be here)
# For brevity, I'm keeping the DB short in this example. Paste your full DB here.
UK_PRESERVATIVE_LIMITS = {
    "Phenoxyethanol (and) Ethylhexylglycerin (Euxyl PE 9010)": 1.0, 
    "Benzyl Alcohol (and) Salicylic Acid (and) Glycerin (and) Sorbic Acid (Geogard ECT)": 1.0, 
    "Sodium Benzoate (and) Potassium Sorbate": 1.0, 
    "Caprylhydroxamic Acid (and) Glyceryl Caprylate (and) Glycerin (Spectrastat)": 1.5, 
    "Sodium Levulinate (and) Sodium Anisate": 2.0, 
    "Dehydroacetic Acid (and) Benzyl Alcohol (Geogard 221)": 1.0, 
    "Lactobacillus Ferment": 4.0, 
    "Chlorphenesin": 0.3,
    "Gluconolactone (and) Sodium Benzoate (Geogard Ultra)": 2.0, 
    "Potassium Sorbate": 0.6, 
    "Salicylic Acid": 0.5, 
    "Sodium Phytate": 0.2,
    "Tocopherol (Vitamin E)": 0.5,
    "Rosemary Leaf Extract": 0.5,
    "Caprylyl Glycol (and) Ethylhexylglycerin": 1.0,
    "Caprylyl Glycol": 1.0,
    "Glyceryl Caprylate": 1.0,
    "P-Anisic Acid": 0.5,
    "Levulinic Acid": 1.0,
    "Citric Acid": 0.5,
}
MAX_TOTAL_PRIMARY_PRESERVATIVE_LOAD = 2.5

# --- FaceCreamFormulator Class (Keep existing logic) ---
class FaceCreamFormulator:
    def __init__(self, ingredients_db):
        self.ingredients_db = ingredients_db

    def get_filtered_ingredients(self, category_type, natural_organic_choice):
        """Filters ingredients based on category type and natural/organic preference."""
        filtered = []
        for ing in self.ingredients_db:
            is_valid_type = False
            if ing.category in ["Emulsifier", "Preservative", "Stabilizer", "Emollient", "Carrier Oil", "Co-Emulsifier"]:
                is_valid_type = True
            elif ing.category == "Active":
                if ing.name == "Zinc Oxide": # Exclude Zinc Oxide from general active selection
                    continue
                if category_type == "Complex":
                    is_valid_type = True
                else:
                    cream_type_benefits_map = {
                        "Anti wrinkle": ["anti-aging", "collagen boosting", "regenerating", "firming", "plumping", "skin elasticity", "hyperpigmentation", "brightening"],
                        "Psoriasis": ["soothing", "anti-inflammatory", "barrier support", "moisturizing", "skin protectant", "healing"],
                        "Acne": ["exfoliating", "antimicrobial", "sebum regulating", "anti-inflammatory", "oil absorption", "purifying"],
                        "Medical": ["healing", "soothing", "barrier repair", "moisturizing", "skin protectant", "anti-inflammatory"],
                        "Ultra": ["hydration", "moisturizing", "humectant", "plumping", "barrier repair", "cell protection"], # Assuming Ultra means Ultra-Hydrating
                        "Crystal": ["light diffusion", "brightening", "aesthetic", "energizing aesthetic", "calming aesthetic", "shimmer", "luxury appeal", "mineralizing"]
                    }
                    if category_type in cream_type_benefits_map and any(b in ing.benefits for b in cream_type_benefits_map[category_type]):
                        is_valid_type = True
            elif ing.category == "Colorant" and ing.color is not None:
                is_valid_type = True
            elif ing.category == "Scent" and ing.scent is not None:
                is_valid_type = True

            if is_valid_type:
                if natural_organic_choice in ["Natural", "Organic", "Both"]:
                    if ing.natural_organic_status in ["Natural", "Organic", "Both"]:
                        filtered.append(ing)
                elif natural_organic_choice == "All":
                    filtered.append(ing)
        return filtered

    def check_interactions(self, selected_ingredients):
        interactions_found = []
        selected_names = {ing.name for ing in selected_ingredients}
        for ing1 in selected_ingredients:
            for interaction_ing, interaction_type in ing1.interactions:
                if interaction_ing in selected_names:
                    interaction_message = f"Interaction: {ing1.name} and {interaction_ing} - {interaction_type}"
                    if interaction_message not in interactions_found:
                        interactions_found.append(interaction_message)
        return interactions_found

    def formulate_cream(self, cream_type, natural_organic_choice, desired_color=None, desired_scent_1=None, desired_scent_2=None,
                        thickness_level=5, add_shimmer=False, zinc_oxide_pct=0, formula_complexity="Simple"):
        formulation = {}
        selected_ingredients_objects = []
        preservative_warnings = []
        thickness_factor = (thickness_level - 1) / 9.0

        mandatory_categories = {
            "Emulsifier": (3 + (7 - 3) * thickness_factor, 3 + (7 - 3) * thickness_factor),
            "Stabilizer": (0.5 + (3 - 0.5) * (thickness_factor * 0.5), 0.5 + (3 - 0.5) * (0.5 + thickness_factor * 0.5)),
            "Emollient": (5 + (15 - 5) * (thickness_factor * 0.3), 5 + (15 - 5) * (0.7 + thickness_factor * 0.3)),
            "Carrier Oil": (5 + (15 - 5) * (thickness_factor * 0.4), 5 + (15 - 5) * (0.6 + thickness_factor * 0.4)),
            "Co-Emulsifier": (3 + (10 - 3) * (thickness_factor * 0.2), 3 + (10 - 3) * (thickness_factor * 0.2)),
        }
        for category in mandatory_categories:
            min_p, max_p = mandatory_categories[category]
            mandatory_categories[category] = (round(min_p, 2), round(max_p, 2))

        zinc_oxide_ing = next((ing for ing in self.ingredients_db if ing.name == "Zinc Oxide"), None)
        if zinc_oxide_pct > 0 and zinc_oxide_ing:
            final_zinc_pct = max(zinc_oxide_ing.min_pct, min(zinc_oxide_ing.max_pct, zinc_oxide_pct))
            final_zinc_pct = round(final_zinc_pct, 3)
            formulation[zinc_oxide_ing.name] = {"percentage": final_zinc_pct, "ingredient": zinc_oxide_ing}
            selected_ingredients_objects.append(zinc_oxide_ing)
            if final_zinc_pct != zinc_oxide_pct:
                preservative_warnings.append(f"Note: Desired Zinc Oxide was {zinc_oxide_pct}%, adjusted to {final_zinc_pct}% ({zinc_oxide_ing.min_pct}-{zinc_oxide_ing.max_pct}%).")
        elif zinc_oxide_pct > 0 and not zinc_oxide_ing:
            preservative_warnings.append(f"Warning: 'Zinc Oxide' not found, cannot add {zinc_oxide_pct}%.")

        chosen_preservative_obj = None
        preservative_options = [ing for ing in self.get_filtered_ingredients("Complex", natural_organic_choice) if ing.category == "Preservative" and ing.is_broad_spectrum]
        random.shuffle(preservative_options)

        for ing in preservative_options:
            min_p_target, max_p_target = (0.5, 1.0)
            actual_min_pct = max(ing.min_pct, min_p_target)
            actual_max_pct = min(ing.max_pct, max_p_target)

            if ing.name in UK_PRESERVATIVE_LIMITS:
                legal_limit = UK_PRESERVATIVE_LIMITS[ing.name]
                if actual_max_pct > legal_limit:
                    preservative_warnings.append(f"Warning: Max for {ing.name} ({ing.max_pct}%) capped to UK limit {legal_limit}%.")
                    actual_max_pct = legal_limit
                if actual_min_pct > actual_max_pct: # Ensure min is not above legal max
                    actual_min_pct = actual_max_pct

            if actual_max_pct < actual_min_pct : continue # Skip if range is invalid

            pct_candidate = random.uniform(actual_min_pct, actual_max_pct)
            chosen_preservative_pct = round(pct_candidate, 3)
            
            # Final check against legal limit and total load
            if ing.name in UK_PRESERVATIVE_LIMITS:
                chosen_preservative_pct = min(chosen_preservative_pct, UK_PRESERVATIVE_LIMITS[ing.name])
            chosen_preservative_pct = min(chosen_preservative_pct, MAX_TOTAL_PRIMARY_PRESERVATIVE_LOAD)

            if chosen_preservative_pct >= (ing.min_pct if ing.min_pct > 0 else 0.001) : # Ensure it's a usable percentage
                chosen_preservative_obj = ing
                formulation[chosen_preservative_obj.name] = {"percentage": chosen_preservative_pct, "ingredient": chosen_preservative_obj}
                selected_ingredients_objects.append(chosen_preservative_obj)
                break
        
        if not chosen_preservative_obj:
            return {"status": "Error", "message": "Error: No suitable broad-spectrum preservative found or could not fit within limits.", "formulation": {}, "total_percentage": 0, "method": ""}

        for category, (min_p, max_p) in mandatory_categories.items():
            filter_type_for_mandatory = "Complex" # Always use complex for essential categories to ensure availability
            possible_ingredients = self.get_filtered_ingredients(filter_type_for_mandatory, natural_organic_choice)
            category_ingredients = [ing for ing in possible_ingredients if ing.category == category]
            if not category_ingredients: # Fallback if specific natural/organic choice yields no results for mandatory
                category_ingredients = [ing for ing in self.get_filtered_ingredients(filter_type_for_mandatory, "All") if ing.category == category]

            chosen_ing = random.choice(category_ingredients) if category_ingredients else None
            if not chosen_ing:
                return {"status": "Error", "message": f"Error: No suitable {category} found (Natural/Organic: '{natural_organic_choice}', Complexity: '{formula_complexity}').", "formulation": {}, "total_percentage": 0, "method": ""}

            actual_min_pct = max(chosen_ing.min_pct, min_p)
            actual_max_pct = min(chosen_ing.max_pct, max_p)
            actual_pct = round(random.uniform(actual_min_pct, actual_max_pct), 3) if actual_max_pct >= actual_min_pct else actual_max_pct
            
            if chosen_ing.name not in formulation:
                formulation[chosen_ing.name] = {"percentage": actual_pct, "ingredient": chosen_ing}
                selected_ingredients_objects.append(chosen_ing)

        filter_type_for_actives = "Complex" if formula_complexity == "Complex" else cream_type
        active_ingredients_pool = [
            ing for ing in self.get_filtered_ingredients(filter_type_for_actives, natural_organic_choice)
            if ing.category == "Active" and ing.name not in UK_PRESERVATIVE_LIMITS and not ing.is_broad_spectrum
        ]
        num_actives = random.randint(3, 7) if formula_complexity == "Complex" else random.randint(1, 3)
        random.shuffle(active_ingredients_pool)
        for ing in active_ingredients_pool:
            if num_actives <= 0: break
            pct_candidate = random.uniform(ing.min_pct, min(ing.max_pct, 5.0)) # Cap individual actives for sanity
            actual_pct = round(max(pct_candidate, ing.min_pct if ing.min_pct > 0 else 0.001), 3)
            if ing.name not in formulation:
                formulation[ing.name] = {"percentage": actual_pct, "ingredient": ing}
                selected_ingredients_objects.append(ing)
                num_actives -= 1

        if desired_color:
            colorants = [ing for ing in self.get_filtered_ingredients("Complex", natural_organic_choice)
                         if ing.category == "Colorant" and ing.color == desired_color and ing.color != "shimmer"]
            if colorants:
                chosen_colorant = random.choice(colorants)
                pct = random.uniform(chosen_colorant.min_pct, min(chosen_colorant.max_pct, 2.0))
                pct = round(max(pct, chosen_colorant.min_pct if chosen_colorant.min_pct > 0 else 0.001), 3)
                if chosen_colorant.name not in formulation:
                    formulation[chosen_colorant.name] = {"percentage": pct, "ingredient": chosen_colorant}
                    selected_ingredients_objects.append(chosen_colorant)
        
        if add_shimmer:
            shimmer_ingredient = next((ing for ing in self.ingredients_db if ing.name == "Mica" and ing.color == "shimmer"), None)
            if shimmer_ingredient:
                pct = random.uniform(shimmer_ingredient.min_pct, min(shimmer_ingredient.max_pct, 3.0))
                pct = round(max(pct, shimmer_ingredient.min_pct if shimmer_ingredient.min_pct > 0 else 0.001), 3)
                if shimmer_ingredient.name not in formulation:
                     formulation[shimmer_ingredient.name] = {"percentage": pct, "ingredient": shimmer_ingredient}
                     selected_ingredients_objects.append(shimmer_ingredient)

        scent_ingredients_pool = [ing for ing in self.get_filtered_ingredients("Complex", natural_organic_choice) if ing.category == "Scent"]
        processed_scents = set()

        def add_scent_to_formula(scent_name_target, is_primary_scent):
            if not scent_name_target or scent_name_target in processed_scents: return
            
            chosen_scent_obj = next((s for s in scent_ingredients_pool if s.scent == scent_name_target and s.name not in formulation), None)
            if chosen_scent_obj:
                # Use max_pct as the ideal, but cap total scent load
                current_total_scent_pct = sum(data["percentage"] for name, data in formulation.items() if data["ingredient"] and data["ingredient"].category == "Scent")
                remaining_scent_allowance = max(0, (1.0 if formula_complexity == "Simple" else 1.5) - current_total_scent_pct) # Max 1-1.5% total scent
                
                scent_pct_target = chosen_scent_obj.max_pct
                final_scent_pct = round(min(scent_pct_target, remaining_scent_allowance), 3)
                final_scent_pct = max(final_scent_pct, chosen_scent_obj.min_pct if chosen_scent_obj.min_pct > 0 else 0.001)

                if final_scent_pct > 0.0001 and chosen_scent_obj.name not in formulation: # Check if it's worth adding
                    formulation[chosen_scent_obj.name] = {"percentage": final_scent_pct, "ingredient": chosen_scent_obj}
                    selected_ingredients_objects.append(chosen_scent_obj)
                    processed_scents.add(scent_name_target)
                    if final_scent_pct < scent_pct_target and remaining_scent_allowance < scent_pct_target :
                         preservative_warnings.append(f"Note: Scent {chosen_scent_obj.name} at {final_scent_pct}% (was {scent_pct_target}%) due to total scent limit.")

        if desired_scent_1: add_scent_to_formula(desired_scent_1, True)
        if desired_scent_2 and desired_scent_2 != desired_scent_1 : add_scent_to_formula(desired_scent_2, False)

        current_non_water_total = sum(data["percentage"] for data in formulation.values())
        calculated_water_pct = round(100.0 - current_non_water_total, 2)
        
        if calculated_water_pct < 0: # Non-water ingredients > 100%
            # This is a critical issue. Need to scale down non-water ingredients.
            # Simplistic scaling: scale everything except preservative and zinc oxide proportionally.
            # A more sophisticated approach would prioritize or protect certain categories.
            scale_target = 100.0 - (formulation.get(chosen_preservative_obj.name, {"percentage":0})["percentage"] + 
                                    formulation.get(zinc_oxide_ing.name if zinc_oxide_ing else "", {"percentage":0})["percentage"])
            
            scalable_total = sum(data["percentage"] for name, data in formulation.items() 
                                 if name != (chosen_preservative_obj.name if chosen_preservative_obj else "") and 
                                    name != (zinc_oxide_ing.name if zinc_oxide_ing else ""))

            if scalable_total > scale_target and scalable_total > 0: # only scale if needed and possible
                scaling_factor = scale_target / scalable_total
                for name, data in formulation.items():
                    if name != (chosen_preservative_obj.name if chosen_preservative_obj else "") and \
                       name != (zinc_oxide_ing.name if zinc_oxide_ing else ""):
                        original_pct = data["percentage"]
                        scaled_pct = round(original_pct * scaling_factor, 3)
                        # Ensure it doesn't go below ingredient's min_pct if min_pct is significant
                        min_allowable = data["ingredient"].min_pct if data["ingredient"] and data["ingredient"].min_pct > 0.0001 else 0.001
                        formulation[name]["percentage"] = max(scaled_pct, min_allowable if scaled_pct > 0 else 0) # Avoid negative from over-correction
                        if formulation[name]["percentage"] < original_pct:
                             preservative_warnings.append(f"Note: {name} scaled from {original_pct:.3f}% to {formulation[name]['percentage']:.3f}% to fit 100% total.")
            
            current_non_water_total = sum(data["percentage"] for data in formulation.values()) # Recalculate
            calculated_water_pct = round(100.0 - current_non_water_total, 2)

        formulation["Water (Aqua)"] = {"percentage": max(0, calculated_water_pct), "ingredient": None} # Ensure water isn't negative
        if calculated_water_pct < 40 and calculated_water_pct >=0 : # Water still positive but low
             preservative_warnings.append(f"Warning: Water content is low ({calculated_water_pct:.2f}%). Recommended minimum is 40%. May affect stability/texture.")
        elif calculated_water_pct < 0: # After scaling, if water is still negative, it's a big problem
             preservative_warnings.append(f"Critical Warning: Total non-water ingredients ({current_non_water_total:.2f}%) exceeded 100% even after attempted scaling. Water set to 0%. Formula unstable.")

        final_total_percentage = sum(data["percentage"] for data in formulation.values())
        final_total_percentage = round(final_total_percentage, 2)

        # If total is slightly off 100 due to rounding, adjust water
        if abs(final_total_percentage - 100.0) > 0.001 and "Water (Aqua)" in formulation and formulation["Water (Aqua)"]["percentage"] > 0:
            water_adjustment = round(100.0 - final_total_percentage, 2)
            new_water_pct = formulation["Water (Aqua)"]["percentage"] + water_adjustment
            if new_water_pct >= 0: # Only adjust if water remains non-negative
                formulation["Water (Aqua)"]["percentage"] = round(new_water_pct, 2)
                final_total_percentage = sum(data["percentage"] for data in formulation.values())
                final_total_percentage = round(final_total_percentage, 2)
            # else: don't adjust if it makes water negative, accept slight deviation.

        interactions = self.check_interactions(selected_ingredients_objects)
        if preservative_warnings:
            interactions.extend(preservative_warnings)

        method_steps = self.generate_method(formulation)
        status = "Success"
        message = "Cream formulated successfully!"
        if interactions:
            status = "Warning"
            message = "Potential ingredient interactions or regulatory warnings found. Please review."
        if final_total_percentage < 99.5 or final_total_percentage > 100.5: # If total is way off
             status = "Error" if status != "Warning" else "Warning" # Keep warning if already warning
             message += f" Total percentage ({final_total_percentage}%) is significantly off 100%. Review needed."

        return {
            "status": status,
            "message": message,
            "interactions": interactions,
            "formulation": formulation,
            "total_percentage": final_total_percentage,
            "method": method_steps
        }

    def generate_method(self, formulation):
        steps = ["## Simple Cream Making Method (Educational Only):"]
        phases = {"Water Phase (Heat A)": [], "Oil Phase (Heat B)": [], "Cool Down (Phase D - <40°C)": []}
        water_phase_ingredients = ["Water (Aqua)", "Glycerin", "Propanediol", "Butylene Glycol", "Xanthan Gum", "Carbomer", "Sodium Hyaluronate", "Allantoin", "Panthenol"] # Common water phase
        oil_phase_ingredients = ["Emulsifier", "Carrier Oil", "Emollient", "Cetyl Alcohol", "Stearyl Alcohol", "Cetearyl Alcohol"] # Common oil phase (by category or specific name)
        
        water_pct_str = f"{formulation.get('Water (Aqua)', {'percentage':0})['percentage']:.2f}%"
        phases["Water Phase (Heat A)"].append(f"1. Water (Aqua): {water_pct_str}")

        sorted_formulation = sorted(formulation.items(), key=lambda item: (
            0 if item[0] == "Water (Aqua)" else 
            1 if item[1]["ingredient"] and item[1]["ingredient"].category in ["Emulsifier", "Stabilizer"] else
            2 if item[1]["ingredient"] and item[1]["ingredient"].category in ["Emollient", "Carrier Oil"] else
            3 if item[1]["ingredient"] and item[1]["ingredient"].category == "Co-Emulsifier" else
            4 if item[1]["ingredient"] and item[1]["ingredient"].category == "Preservative" else
            5 if item[1]["ingredient"] and item[1]["ingredient"].category == "Active" else
            6 # Others
        , item[0]))

        for name, data in sorted_formulation:
            if name == "Water (Aqua)": continue
            ing = data["ingredient"]
            pct_str = f"{data['percentage']:.3f}%" if data['percentage'] < 0.1 and data['percentage'] > 0 else f"{data['percentage']:.2f}%"
            
            if ing:
                # More robust phase allocation
                if ing.category == "Preservative" or \
                   ing.category == "Active" or \
                   ing.category == "Scent" or \
                   ing.category == "Colorant" or \
                   (ing.category == "Stabilizer" and "polymer" in ing.name.lower()) or \
                   (ing.ph_impact != "neutral" and ing.category != "Preservative"): # pH adjusters, heat sensitive polymers
                    phases["Cool Down (Phase D - <40°C)"].append(f"- {name}: {pct_str}")
                elif ing.category == "Emulsifier" or \
                     ing.category == "Carrier Oil" or \
                     ing.category == "Emollient" or \
                     name in ["Cetyl Alcohol", "Stearyl Alcohol", "Cetearyl Alcohol", "Glyceryl Stearate SE"]:
                    phases["Oil Phase (Heat B)"].append(f"- {name}: {pct_str}")
                elif ing.name in water_phase_ingredients or \
                     ing.category == "Co-Emulsifier" or \
                     (ing.category == "Stabilizer" and "gum" in ing.name.lower()):
                    phases["Water Phase (Heat A)"].append(f"- {name}: {pct_str}")
                else: # Default to cool down if unsure
                    phases["Cool Down (Phase D - <40°C)"].append(f"- {name} (check solubility/stability): {pct_str}")
            else: # Should not happen if ingredient is None but not water
                phases["Cool Down (Phase D - <40°C)"].append(f"- {name} (Category Unknown): {pct_str}")

        if phases["Water Phase (Heat A)"]:
            steps.append("\n### Phase A (Water Phase):")
            steps.extend(phases["Water Phase (Heat A)"])
            steps.append("Combine ingredients. Heat to 70-75°C (158-167°F), stir until uniform.")
        
        if phases["Oil Phase (Heat B)"]:
            steps.append("\n### Phase B (Oil Phase):")
            steps.extend(phases["Oil Phase (Heat B)"])
            steps.append("In a separate beaker, combine ingredients. Heat to 70-75°C, stir until melted and uniform.")
        
        steps.append("\n### Phase C (Emulsification):")
        steps.append("1. When both phases are at 70-75°C, slowly add Phase B (Oil) to Phase A (Water) under continuous high-shear mixing (e.g., stick blender).")
        steps.append("2. Mix for 3-5 minutes until a stable emulsion forms.")
        steps.append("3. Switch to gentle stirring and begin cooling.")

        if phases["Cool Down (Phase D - <40°C)"]:
            steps.append("\n### Phase D (Cool Down - below 40°C / 104°F):")
            steps.append("Once emulsion has cooled to 40°C or below, add the following ingredients one by one, mixing well after each addition:")
            steps.extend(phases["Cool Down (Phase D - <40°C)"])
        
        steps.append("\n### Final Steps:")
        steps.append("1. Check pH (target typically 4.5-6.5, depends on actives/preservative) and adjust if necessary using appropriate pH adjusters (e.g., Citric Acid solution or Sodium Hydroxide solution - use with extreme care).")
        steps.append("2. Mix thoroughly. Transfer to a sanitized container.")
        steps.append("3. Allow to cool completely before capping.")
        return "\n".join(steps)

# --- Tkinter GUI Application ---
class CreamFormulatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Adrian Ford's Cosmic Cream Formulator v2.0")
        master.geometry("1250x850") # Increased size for desktop
        master.configure(bg=BG_PRIMARY)

        self.formulator = FaceCreamFormulator(INGREDIENTS_DB)

        # Initialize variables
        self.selected_thickness_level = tk.IntVar(value=5)
        self.add_shimmer = tk.BooleanVar(value=False)
        self.zinc_oxide_level = tk.DoubleVar(value=0.0)
        self.formula_complexity = tk.StringVar(value="Simple")
        self.cream_type_var = tk.StringVar()
        self.natural_organic_var = tk.StringVar(value="All")
        self.color_var = tk.StringVar(value="none")
        self.scent_var_1 = tk.StringVar(value="none")
        self.scent_var_2 = tk.StringVar(value="none")
        
        self.desired_color = None
        self.desired_scent_1 = None
        self.desired_scent_2 = None

        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # General widget styling
        self.style.configure('.', background=BG_PRIMARY, foreground=FG_PRIMARY, font=FONT_NORMAL, bordercolor=BORDER_COLOR)
        self.style.map('.', background=[('active', BG_SECONDARY)])

        self.style.configure("TFrame", background=BG_PRIMARY)
        self.style.configure("Scrollable.TFrame", background=BG_SECONDARY) # For the content frame inside canvas
        
        self.style.configure("TLabel", background=BG_PRIMARY, foreground=FG_PRIMARY, font=FONT_NORMAL)
        self.style.configure("Header.TLabel", font=FONT_XLARGE, foreground=ACCENT_COLOR_A)
        self.style.configure("Section.TLabel", font=FONT_LARGE, foreground=ACCENT_COLOR_A)
        self.style.configure("Small.TLabel", font=FONT_SMALL, foreground=FG_ACCENT)

        self.style.configure("TButton", font=FONT_BOLD, background=BUTTON_BG, foreground=BUTTON_FG)
        self.style.map("TButton",
                       background=[('active', BUTTON_ACTIVE_BG), ('pressed', ACCENT_COLOR_A)],
                       foreground=[('active', BUTTON_FG)])

        self.style.configure("TRadiobutton", background=BG_PRIMARY, foreground=FG_PRIMARY, font=FONT_NORMAL, indicatorcolor=BG_PRIMARY)
        self.style.map("TRadiobutton",
                       background=[('active', BG_SECONDARY)],
                       indicatorcolor=[('selected', ACCENT_COLOR_A), ('!selected', FG_ACCENT)])
        
        self.style.configure("TCheckbutton", background=BG_PRIMARY, foreground=FG_PRIMARY, font=FONT_NORMAL, indicatorcolor=BG_PRIMARY)
        self.style.map("TCheckbutton",
                       background=[('active', BG_SECONDARY)],
                       indicatorcolor=[('selected', ACCENT_COLOR_A), ('!selected', FG_ACCENT)])

        self.style.configure("TScale", background=BG_PRIMARY, troughcolor=BG_SECONDARY) # troughcolor might not work well with all themes
        self.style.map("TScale", background=[('active', BG_SECONDARY)])

        self.style.configure("TLabelframe", background=BG_LABELFRAME, bordercolor=BORDER_COLOR, relief="solid", borderwidth=1)
        self.style.configure("TLabelframe.Label", background=BG_LABELFRAME, foreground=ACCENT_COLOR_A, font=FONT_BOLD)
        
        self.style.configure("Vertical.TScrollbar", background=BG_SECONDARY, troughcolor=BG_PRIMARY, arrowcolor=FG_PRIMARY)
        self.style.map("Vertical.TScrollbar",
            background=[('active', ACCENT_COLOR_B)],
            arrowcolor=[('pressed', ACCENT_COLOR_A), ('active', ACCENT_COLOR_A)]
        )
        self.style.configure("Horizontal.TPanedWindow", background=ACCENT_COLOR_B) # Sash color
        self.style.configure("Vertical.TPanedWindow", background=ACCENT_COLOR_B)

    def _create_widgets(self):
        # Main layout: PanedWindow for resizable left (inputs) and right (output) panes
        self.paned_window = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL, style="Horizontal.TPanedWindow")
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Left Pane (Inputs) ---
        self.left_pane_container = ttk.Frame(self.paned_window, width=500, style="TFrame") # Fixed width, height will be scrollable
        self.paned_window.add(self.left_pane_container, weight=1) # Adjust weight as needed

        # Canvas for scrolling behavior in the left pane
        self.input_canvas = tk.Canvas(self.left_pane_container, bg=BG_PRIMARY, highlightthickness=0)
        self.input_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.input_scrollbar = ttk.Scrollbar(self.left_pane_container, orient=tk.VERTICAL, command=self.input_canvas.yview, style="Vertical.TScrollbar")
        self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_canvas.configure(yscrollcommand=self.input_scrollbar.set)

        # This frame will contain all the input widgets and be scrolled by the canvas
        self.scrollable_input_frame = ttk.Frame(self.input_canvas, style="Scrollable.TFrame", padding=(15,15))
        self.canvas_frame_id = self.input_canvas.create_window((0, 0), window=self.scrollable_input_frame, anchor="nw")

        self.scrollable_input_frame.bind("<Configure>", self._on_frame_configure_canvas)
        self.input_canvas.bind_all("<MouseWheel>", self._on_mousewheel) # For Windows/macOS mouse wheel scrolling

        # Populate scrollable_input_frame
        current_row = 0

        # Header
        ttk.Label(self.scrollable_input_frame, text="Cosmic Cream Formulator", style="Header.TLabel").grid(row=current_row, column=0, columnspan=2, pady=(0, 20), sticky="w")
        current_row += 1

        # Disclaimer Section
        disclaimer_lf = ttk.Labelframe(self.scrollable_input_frame, text="Important Disclaimer", style="TLabelframe")
        disclaimer_lf.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        current_row += 1
        
        disclaimer_text_widget = tk.Text(disclaimer_lf, wrap=tk.WORD, height=8, font=FONT_SMALL,
                                         bg=TEXT_INPUT_BG, fg=FG_ACCENT, relief=tk.FLAT,
                                         borderwidth=1, highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_COLOR_A, insertbackground=FG_PRIMARY)
        disclaimer_text_content = (
            "LEGAL DISCLAIMER: This is an experimentally generated formula by Adrian Ford for "
            "EDUCATIONAL PURPOSES ONLY. This formula has NOT been safety assessed, stability tested, or "
            "legally approved for cosmetic use or sale. DO NOT ATTEMPT TO MANUFACTURE OR SELL PRODUCTS "
            "BASED ON THIS FORMULA. All ingredient percentages (min_pct, max_pct) in this database are "
            "illustrative estimates and must be VERIFIED against current, official regulatory documents "
            "(e.g., UK Cosmetic Products Regulation amended from EU Regulation 1223/2009). Furthermore, "
            "cosmetic formulation involves complex interactions and requires specialized knowledge. This tool "
            "is a simplified simulation and does not account for all factors like ingredient compatibility, "
            "long-term stability, microbial challenge testing, or potential allergens beyond basic notes. "
            "For any real cosmetic product development or sale, you MUST: 1. Consult a qualified cosmetic "
            "chemist/formulator with relevant expertise. 2. Adhere strictly to all relevant national and "
            "international regulations, including but not limited to Annexes II, III, IV, V, and VI for "
            "ingredient maximums, restrictions, prohibitions, and other specific requirements. 3. Verify all "
            "ingredient maximums, restrictions, prohibitions, and usage requirements from OFFICIAL REGULATORY "
            "SOURCES, which are to change. 4. Conduct a full Cosmetic Product Safety Report (CPSR) "
            "by a certified safety assessor. 5. Ensure Good Manufacturing Practices (GMP) are followed at all "
            "stages of production. 6. Substantiate all product claims with robust scientific evidence. "
            "7. Perform comprehensive stability and compatibility testing on the final product and packaging. "
            "8. Conduct microbial challenge testing to ensure product safety. "
            "The tool's adherence to stated maximums is based on the provided data, not on real-time legal "
            "expertise or comprehensive regulatory analysis. Use this tool responsibly and always prioritize "
            "professional guidance for any commercial or personal use beyond theoretical exploration."
        )
        disclaimer_text_widget.insert(tk.END, disclaimer_text_content)
        disclaimer_text_widget.config(state=tk.DISABLED) # Make it read-only
        disclaimer_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Formula Complexity ---
        complexity_lf = ttk.Labelframe(self.scrollable_input_frame, text="Formula Complexity", style="TLabelframe")
        complexity_lf.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        current_row += 1
        ttk.Radiobutton(complexity_lf, text="Simple", variable=self.formula_complexity, value="Simple", style="TRadiobutton").pack(side=tk.LEFT, padx=10, pady=5, expand=True)
        ttk.Radiobutton(complexity_lf, text="Complex", variable=self.formula_complexity, value="Complex", style="TRadiobutton").pack(side=tk.LEFT, padx=10, pady=5, expand=True)

        # --- Cream Type ---
        cream_type_lf = ttk.Labelframe(self.scrollable_input_frame, text="Cream Type", style="TLabelframe")
        cream_type_lf.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        current_row += 1
        self.cream_types_options = ["Anti wrinkle", "Psoriasis", "Acne", "Medical", "Ultra", "Crystal"]
        self.cream_type_var.set(self.cream_types_options[0]) # Default selection
        for i, ctype in enumerate(self.cream_types_options):
            ttk.Radiobutton(cream_type_lf, text=ctype, variable=self.cream_type_var, value=ctype, style="TRadiobutton").grid(row=i//2, column=i%2, padx=5, pady=2, sticky="w")

        # --- Natural/Organic Preference ---
        nat_org_lf = ttk.Labelframe(self.scrollable_input_frame, text="Natural/Organic Preference", style="TLabelframe")
        nat_org_lf.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        current_row += 1
        self.natural_organic_options_list = ["Natural", "Organic", "Both", "All"]
        for i, status in enumerate(self.natural_organic_options_list):
            ttk.Radiobutton(nat_org_lf, text=status, variable=self.natural_organic_var, value=status, style="TRadiobutton").grid(row=i//2, column=i%2, padx=5, pady=2, sticky="w")

        # --- Thickness ---
        thickness_lf = ttk.Labelframe(self.scrollable_input_frame, text="Thickness Level", style="TLabelframe")
        thickness_lf.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        current_row += 1
        self.thickness_options_map = {
            1: "Very Thin", 2: "Thin-ish", 3: "Thin", 4: "Medium-Thin", 5: "Medium",
            6: "Medium-Heavy", 7: "Heavy", 8: "Very Heavy", 9: "Super Heavy", 10: "Solid",
        }
        self.thickness_label_display = ttk.Label(thickness_lf, text=f"Current: {self.thickness_options_map[self.selected_thickness_level.get()]}", style="Small.TLabel")
        self.thickness_label_display.pack(pady=(5,0))
        ttk.Scale(thickness_lf, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.selected_thickness_level, command=self.update_thickness_label, style="TScale").pack(fill=tk.X, padx=5, pady=(0,5))

        # --- Appearance (Color & Shimmer) ---
        appearance_lf = ttk.Labelframe(self.scrollable_input_frame, text="Appearance", style="TLabelframe")
        appearance_lf.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        current_row += 1
        
        ttk.Label(appearance_lf, text="Pigmentation (Optional):", style="TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=(5,0))
        available_colors_list = sorted(list(set([ing.color for ing in INGREDIENTS_DB if ing.category == "Colorant" and ing.color and ing.color != "shimmer"])))
        self.color_options_list = ["none"] + [c.lower() for c in available_colors_list] # Use lowercase for value
        color_radio_frame = ttk.Frame(appearance_lf, style="TFrame")
        color_radio_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        for i, color_val in enumerate(self.color_options_list):
            ttk.Radiobutton(color_radio_frame, text=color_val.capitalize(), variable=self.color_var, value=color_val, command=self.update_color_selection, style="TRadiobutton").grid(row=i//3, column=i%3, padx=3, pady=1, sticky="w")

        ttk.Checkbutton(appearance_lf, text="Add Shimmer (Mica)", variable=self.add_shimmer, style="TCheckbutton").grid(row=0, column=1, rowspan=2, padx=20, pady=5, sticky="w")

        # --- Sunblock ---
        sunblock_lf = ttk.Labelframe(self.scrollable_input_frame, text="Sunblock (Zinc Oxide %)", style="TLabelframe")
        sunblock_lf.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        current_row += 1
        self.zinc_oxide_label_display = ttk.Label(sunblock_lf, text=f"Current: {self.zinc_oxide_level.get():.0f}%", style="Small.TLabel")
        self.zinc_oxide_label_display.pack(pady=(5,0))
        ttk.Scale(sunblock_lf, from_=0, to=25, resolution=1, orient=tk.HORIZONTAL, variable=self.zinc_oxide_level, command=self.update_zinc_oxide_label, style="TScale").pack(fill=tk.X, padx=5, pady=(0,5))

        # --- Scent ---
        scent_lf = ttk.Labelframe(self.scrollable_input_frame, text="Scent (Optional)", style="TLabelframe")
        scent_lf.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        current_row += 1
        
        ttk.Label(scent_lf, text="First Scent:", style="TLabel").grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
        self.scent_1_frame = ttk.Frame(scent_lf, style="TFrame")
        self.scent_1_frame.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        
        ttk.Label(scent_lf, text="Second Scent:", style="TLabel").grid(row=0, column=1, padx=5, pady=(5,0), sticky="w")
        self.scent_2_frame = ttk.Frame(scent_lf, style="TFrame")
        self.scent_2_frame.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        self.update_scent_radio_buttons(self.scent_1_frame, self.scent_var_1, 1)
        self.update_scent_radio_buttons(self.scent_2_frame, self.scent_var_2, 2)
        scent_lf.columnconfigure(0, weight=1)
        scent_lf.columnconfigure(1, weight=1)

        # --- Formulate Button ---
        self.formulate_button = ttk.Button(self.scrollable_input_frame, text="Formulate Cream!", command=self.run_formulation_with_delay, style="TButton", width=30)
        self.formulate_button.grid(row=current_row, column=0, columnspan=2, pady=25)
        current_row += 1
        
        # Configure column weights for input frame for responsiveness if any
        self.scrollable_input_frame.columnconfigure(0, weight=1)
        self.scrollable_input_frame.columnconfigure(1, weight=1)

        # --- Right Pane (Output) ---
        self.right_pane = ttk.Frame(self.paned_window, style="TFrame", padding=(10,0))
        self.paned_window.add(self.right_pane, weight=2) # Adjust weight as needed

        self.output_text_widget = scrolledtext.ScrolledText(
            self.right_pane, font=FONT_OUTPUT, wrap=tk.WORD, height=25,
            bg=TEXT_INPUT_BG, fg=FG_PRIMARY, relief=tk.FLAT,
            borderwidth=1, highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_COLOR_A, insertbackground=FG_PRIMARY
        )
        self.output_text_widget.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        self.output_text_widget.tag_config("error_tag", foreground="#FF5252") # Bright Red for errors
        self.output_text_widget.tag_config("warning_tag", foreground="#FFC107") # Amber for warnings
        self.output_text_widget.tag_config("header_tag", font=(MONO_FONT, 11, "bold"), foreground=ACCENT_COLOR_A)
        self.output_text_widget.tag_config("subheader_tag", font=(MONO_FONT, 10, "bold"), foreground=ACCENT_COLOR_B)
        self.output_text_widget.config(state=tk.DISABLED) # Start as read-only

    def _on_frame_configure_canvas(self, event=None):
        self.input_canvas.configure(scrollregion=self.input_canvas.bbox("all"))
        # Make the scrollable frame fill the width of the canvas
        self.input_canvas.itemconfig(self.canvas_frame_id, width=self.input_canvas.winfo_width())

    def _on_mousewheel(self, event):
        # Determine if the mouse is over the input_canvas or its children
        widget_under_mouse = self.master.winfo_containing(event.x_root, event.y_root)
        target_canvas = None

        if widget_under_mouse == self.input_canvas or self.input_canvas in widget_under_mouse.winfo_parents() or widget_under_mouse == self.scrollable_input_frame or self.scrollable_input_frame in widget_under_mouse.winfo_parents() :
             target_canvas = self.input_canvas
        
        # Check if mouse is over the output_text_widget (it has its own scrollbars)
        # This part is tricky as ScrolledText handles its own scrolling.
        # For simplicity, we'll only explicitly scroll our canvas.
        # If ScrolledText is focused, its own scrollbar should work.

        if target_canvas:
            if event.num == 5 or event.delta < 0: # Scroll down
                target_canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0: # Scroll up
                target_canvas.yview_scroll(-1, "units")

    def update_thickness_label(self, val):
        current_value = int(float(val))
        self.thickness_label_display.config(text=f"Current: {self.thickness_options_map.get(current_value, f'{current_value} (Custom)')}")

    def update_color_selection(self):
        self.desired_color = self.color_var.get() if self.color_var.get() != "none" else None

    def update_zinc_oxide_label(self, val):
        self.zinc_oxide_label_display.config(text=f"Current: {self.zinc_oxide_level.get():.0f}%")

    def update_scent_selection(self, scent_num, choice):
        if scent_num == 1:
            self.desired_scent_1 = choice if choice != "none" else None
            # If Scent 1 changes, Scent 2 options might need to be re-filtered if they depend on Scent 1
            # For now, assuming they are independent choices other than not being the same.
            if self.desired_scent_1 and self.desired_scent_1 == self.desired_scent_2:
                self.scent_var_2.set("none") # Reset scent 2 if it becomes same as scent 1
                self.desired_scent_2 = None
            self.update_scent_radio_buttons(self.scent_2_frame, self.scent_var_2, 2) # Refresh Scent 2 options
        elif scent_num == 2:
            self.desired_scent_2 = choice if choice != "none" else None

    def update_scent_radio_buttons(self, frame, var, scent_num):
        for widget in frame.winfo_children():
            widget.destroy()

        other_scent_val = None
        if scent_num == 1: other_scent_val = self.scent_var_2.get()
        elif scent_num == 2: other_scent_val = self.scent_var_1.get()
        
        options_to_display = ["none"]
        unique_scents = sorted(list(set([ing.scent for ing in INGREDIENTS_DB if ing.category == "Scent" and ing.scent])))
        
        for scent_val in unique_scents:
            if scent_val == other_scent_val and other_scent_val != "none": # Don't offer the other selected scent
                continue
            options_to_display.append(scent_val)
        
        # Ensure current var value is valid, else reset
        if var.get() not in options_to_display:
            var.set("none")
            if scent_num == 1: self.desired_scent_1 = None
            if scent_num == 2: self.desired_scent_2 = None

        max_scents_per_row = 2 # Adjust for better layout
        for i, scent_option_val in enumerate(options_to_display):
            ttk.Radiobutton(frame, text=scent_option_val.capitalize(), variable=var, value=scent_option_val,
                            command=lambda s=scent_option_val: self.update_scent_selection(scent_num, s),
                            style="TRadiobutton").grid(row=i // max_scents_per_row, column=i % max_scents_per_row, padx=3, pady=1, sticky="w")
        
        for i in range(max_scents_per_row):
            frame.columnconfigure(i, weight=1)

    def run_formulation(self):
        if not self.cream_type_var.get():
            messagebox.showwarning("Input Error", "Please select a cream type!", parent=self.master)
            return

        # Gather all selections
        cream_type = self.cream_type_var.get()
        natural_organic_choice = self.natural_organic_var.get()
        thickness_level = self.selected_thickness_level.get()
        # desired_color already set by update_color_selection
        add_shimmer = self.add_shimmer.get()
        zinc_oxide_pct = self.zinc_oxide_level.get()
        # desired_scent_1 and desired_scent_2 already set

        formula_complexity_val = self.formula_complexity.get()

        self.output_text_widget.config(state=tk.NORMAL)
        self.output_text_widget.delete(1.0, tk.END)
        self.output_text_widget.insert(tk.END, "Generating formula...\n\n", "subheader_tag")
        self.master.update_idletasks() # Refresh UI

        generated_cream = self.formulator.formulate_cream(
            cream_type=cream_type,
            natural_organic_choice=natural_organic_choice,
            desired_color=self.desired_color,
            desired_scent_1=self.desired_scent_1,
            desired_scent_2=self.desired_scent_2,
            thickness_level=thickness_level,
            add_shimmer=add_shimmer,
            zinc_oxide_pct=zinc_oxide_pct,
            formula_complexity=formula_complexity_val
        )

        self.output_text_widget.delete(1.0, tk.END) # Clear "Generating..."

        if generated_cream["status"] == "Error":
            self.output_text_widget.insert(tk.END, generated_cream["message"] + "\n", "error_tag")
            self.output_text_widget.insert(tk.END, "Could not generate formula due to missing ingredients or constraints.\n", "error_tag")
            self.output_text_widget.insert(tk.END, "Please try different selection criteria (e.g., 'All' for Natural/Organic, or 'Complex' Complexity).\n", "error_tag")
        else:
            self.output_text_widget.insert(tk.END, generated_cream["message"] + "\n\n", "subheader_tag" if generated_cream["status"] == "Success" else "warning_tag")

            if generated_cream["status"] == "Warning" and generated_cream["interactions"]:
                self.output_text_widget.insert(tk.END, "--- ALERTS & INTERACTIONS ---\n", "warning_tag")
                for item in generated_cream["interactions"]:
                    self.output_text_widget.insert(tk.END, f"- {item}\n", "warning_tag")
                self.output_text_widget.insert(tk.END, "---------------------------\n\n")

            self.output_text_widget.insert(tk.END, "--- FORMULA ---\n", "header_tag")
            
            # Sort formula for display (Water first, then by category, then alphabetically)
            category_order = ["Water (Aqua)", "Emulsifier", "Co-Emulsifier", "Emollient", "Carrier Oil", "Stabilizer", "Preservative", "Active", "Colorant", "Scent"]
            
            sorted_formula_items = []
            # Ensure Water is first if present
            if "Water (Aqua)" in generated_cream["formulation"]:
                sorted_formula_items.append(("Water (Aqua)", generated_cream["formulation"]["Water (Aqua)"]))
            
            # Sort other ingredients
            other_ingredients = {k: v for k, v in generated_cream["formulation"].items() if k != "Water (Aqua)"}
            
            # Group by category then sort alphabetically within category
            grouped_by_category = {}
            for name, data in other_ingredients.items():
                cat = data["ingredient"].category if data["ingredient"] else "Unknown"
                if cat not in grouped_by_category:
                    grouped_by_category[cat] = []
                grouped_by_category[cat].append((name, data))

            for cat_name in category_order: # Iterate through defined order first
                if cat_name == "Water (Aqua)": continue
                if cat_name in grouped_by_category:
                    for name, data in sorted(grouped_by_category[cat_name], key=lambda x: x[0]): # Sort alphabetically by name
                        sorted_formula_items.append((name, data))
                    del grouped_by_category[cat_name] # Remove processed category

            # Add any remaining categories (shouldn't happen if category_order is comprehensive)
            for cat_name in sorted(grouped_by_category.keys()):
                for name, data in sorted(grouped_by_category[cat_name], key=lambda x: x[0]):
                    sorted_formula_items.append((name, data))

            for name, data in sorted_formula_items:
                pct_val = data['percentage']
                pct_str = f"{pct_val:.3f}%" if 0 < pct_val < 0.01 else f"{pct_val:.2f}%"
                cat_str = f" ({data['ingredient'].category})" if data['ingredient'] else ""
                self.output_text_widget.insert(tk.END, f"{name}{cat_str}: {pct_str}\n")

            self.output_text_widget.insert(tk.END, f"\nTotal Calculated Percentage: {generated_cream['total_percentage']:.2f}%\n\n", "subheader_tag")

            self.output