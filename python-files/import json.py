import json
import datetime

class RAWScoreCalculator:
    def __init__(self):
        # Initialize data storage
        self.raw_data = {
            "physical_health": {},
            "mental_emotional": {},
            "lifestyle_behavior": {},
            "social_environmental": {},
            "genetic_wellness": {}
        }

    def display_menu(self):
        print("\n" + "="*50)
        print("REJUVENATE ASSESSMENT OF WELLNESS (RAW) SCORE CALCULATOR")
        print("="*50)
        print("1. Enter Physical Health Data")
        print("2. Enter Mental & Emotional Health Data")
        print("3. Enter Lifestyle & Behavior Data")
        print("4. Enter Social & Environmental Data")
        print("5. Enter Genetic Wellness Data")
        print("6. Calculate RAW Score")
        print("7. Save Data")
        print("8. Load Data")
        print("9. View Current Data")
        print("0. Exit")
        print("="*50)

    def get_numeric_input(self, prompt):
        while True:
            try:
                value = input(prompt)
                return float(value) if value else 0.0
            except ValueError:
                print("Please enter a valid number")

    def enter_physical_data(self):
        print("\n" + "="*50)
        print("PHYSICAL HEALTH PARAMETERS")
        print("="*50)

        self.raw_data['physical_health'] = {
            'bmi': self.get_numeric_input("BMI: "),
            'waist_circumference': self.get_numeric_input("Waist Circumference (cm): "),
            'resting_hr': self.get_numeric_input("Resting Heart Rate (bpm): "),
            'fasting_glucose': self.get_numeric_input("Fasting Glucose (mg/dL): "),
            'vo2_max': self.get_numeric_input("VO₂ Max: "),
            'grip_strength': self.get_numeric_input("Grip Strength (kg): "),
            'sleep_duration': self.get_numeric_input("Sleep Duration (hours): ")
        }
        print("Physical health data saved!")

    def enter_mental_data(self):
        print("\n" + "="*50)
        print("MENTAL & EMOTIONAL HEALTH PARAMETERS")
        print("="*50)

        self.raw_data['mental_emotional'] = {
            'phq9': self.get_numeric_input("PHQ-9 Score (0-27): "),
            'gad7': self.get_numeric_input("GAD-7 Score (0-21): "),
            'pss': self.get_numeric_input("Perceived Stress Score (0-40): "),
            'reaction_time': self.get_numeric_input("Reaction Time (ms): "),
            'resilience': self.get_numeric_input("Resilience Scale Score (0-40): "),
            'sleep_satisfaction': self.get_numeric_input("Sleep Satisfaction (1-10): ")
        }
        print("Mental & emotional health data saved!")

    def enter_lifestyle_data(self):
        print("\n" + "="*50)
        print("LIFESTYLE & BEHAVIOR PARAMETERS")
        print("="*50)

        self.raw_data['lifestyle_behavior'] = {
            'fruit_veg': self.get_numeric_input("Fruit/Vegetable Servings per day: "),
            'daily_steps': self.get_numeric_input("Daily Steps: "),
            'moderate_activity': self.get_numeric_input("Moderate Activity (min/week): "),
            'sedentary_time': self.get_numeric_input("Sedentary Time (hours/day): "),
            'smoking': self.get_numeric_input("Smoking (cigarettes/day): "),
            'alcohol': self.get_numeric_input("Alcohol (drinks/week): "),
            'water_intake': self.get_numeric_input("Water Intake (liters/day): ")
        }
        print("Lifestyle & behavior data saved!")

    def enter_social_data(self):
        print("\n" + "="*50)
        print("SOCIAL & ENVIRONMENTAL WELLNESS")
        print("="*50)

        self.raw_data['social_environmental'] = {
            'social_support': self.get_numeric_input("Social Support Score (1-10): "),
            'loneliness': self.get_numeric_input("Loneliness Scale (1-10): "),
            'work_hours': self.get_numeric_input("Work Hours/Week: "),
            'life_satisfaction': self.get_numeric_input("Life Satisfaction (1-10): ")
        }
        print("Social & environmental data saved!")

    def enter_genetic_data(self):
        print("\n" + "="*50)
        print("GENETIC WELLNESS")
        print("="*50)

        self.raw_data['genetic_wellness'] = {
            'cancer_genes': self.get_numeric_input("Cancer Risk Genes (0-5): "),
            'food_allergy_genes': self.get_numeric_input("Food Allergy Genes (0-5): "),
            'inherited_disease_risk': self.get_numeric_input("Inherited Disease Risk (0-5): ")
        }
        print("Genetic wellness data saved!")

    def calculate_physical_score(self):
        score = 0
        data = self.raw_data['physical_health']

        # BMI scoring (ideal 18.5-24.9)
        bmi = data.get('bmi', 0)
        if 18.5 <= bmi <= 24.9:
            score += 20
        elif 25 <= bmi <= 29.9 or 17 <= bmi < 18.5:
            score += 10
        else:
            score += 5

        # Resting heart rate (ideal 60-100 bpm)
        hr = data.get('resting_hr', 0)
        if 60 <= hr <= 100:
            score += 15
        else:
            score += 5

        # VO2 Max scoring
        vo2_max = data.get('vo2_max', 0)
        if vo2_max >= 50:
            score += 20
        elif vo2_max >= 40:
            score += 15
        else:
            score += 5

        return min(100, score)

    def calculate_mental_score(self):
        score = 0
        data = self.raw_data['mental_emotional']

        # PHQ-9 scoring (lower is better)
        phq9 = data.get('phq9', 0)
        if phq9 <= 4:
            score += 25
        elif phq9 <= 9:
            score += 15
        else:
            score += 5

        # GAD-7 scoring (lower is better)
        gad7 = data.get('gad7', 0)
        if gad7 <= 4:
            score += 25
        elif gad7 <= 9:
            score += 15
        else:
            score += 5

        return min(100, score)

    def calculate_lifestyle_score(self):
        score = 0
        data = self.raw_data['lifestyle_behavior']

        # Physical activity scoring
        steps = data.get('daily_steps', 0)
        if steps >= 10000:
            score += 20
        elif steps >= 5000:
            score += 15
        else:
            score += 5

        # Fruit/vegetable consumption
        fruit_veg = data.get('fruit_veg', 0)
        if fruit_veg >= 5:
            score += 20
        elif fruit_veg >= 3:
            score += 15
        else:
            score += 5

        return min(100, score)

    def calculate_social_score(self):
        score = 0
        data = self.raw_data['social_environmental']

        social_support = data.get('social_support', 0)
        score += social_support * 3

        life_satisfaction = data.get('life_satisfaction', 0)
        score += life_satisfaction * 3

        return min(100, score)

    def calculate_genetic_score(self):
        score = 100
        data = self.raw_data['genetic_wellness']

        # Subtract points based on genetic risk factors
        cancer_risk = data.get('cancer_genes', 0)
        score -= cancer_risk * 5

        inherited_risk = data.get('inherited_disease_risk', 0)
        score -= inherited_risk * 5

        return max(0, score)

    def calculate_total_score(self):
        scores = {
            'physical': self.calculate_physical_score(),
            'mental': self.calculate_mental_score(),
            'lifestyle': self.calculate_lifestyle_score(),
            'social': self.calculate_social_score(),
            'genetic': self.calculate_genetic_score()
        }

        scores['total'] = sum(scores.values())

        return scores

    def display_results(self, scores):
        print("\n" + "="*50)
        print("REJUVENATE ASSESSMENT OF WELLNESS (RAW) SCORE REPORT")
        print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*50)

        print("\nCOMPONENT SCORES:")
        print(f"- Physical Health: {scores['physical']}/100")
        print(f"- Mental & Emotional Health: {scores['mental']}/100")
        print(f"- Lifestyle & Behavior: {scores['lifestyle']}/100")
        print(f"- Social & Environmental: {scores['social']}/100")
        print(f"- Genetic Wellness: {scores['genetic']}/100")
        print(f"\nTOTAL RAW SCORE: {scores['total']}/500")

        print("\nWELLNESS ASSESSMENT:")
        total = scores['total']
        if total >= 400:
            print("Excellent overall wellness - maintain your healthy habits!")
        elif total >= 300:
            print("Good wellness level - focus on areas needing improvement")
        elif total >= 200:
            print("Moderate wellness - consider lifestyle adjustments")
        else:
            print("Needs improvement - consult healthcare professional")

        print("="*50)

    def save_data(self):
        filename = f"raw_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(filename, 'w') as f:
            json.dump(self.raw_data, f, indent=2)
        print(f"Data saved to {filename}")

    def load_data(self):
        filename = input("Enter filename to load: ")
        try:
            with open(filename, 'r') as f:
                self.raw_data = json.load(f)
            print("Data loaded successfully!")
        except FileNotFoundError:
            print("File not found!")
        except json.JSONDecodeError:
            print("Invalid file format!")

    def view_current_data(self):
        print("\nCURRENT DATA:")
        for category, data in self.raw_data.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for key, value in data.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")

    def run(self):
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ")

            if choice == '1':
                self.enter_physical_data()
            elif choice == '2':
                self.enter_mental_data()
            elif choice == '3':
                self.enter_lifestyle_data()
            elif choice == '4':
                self.enter_social_data()
            elif choice == '5':
                self.enter_genetic_data()
            elif choice == '6':
                scores = self.calculate_total_score()
                self.display_results(scores)
            elif choice == '7':
                self.save_data()
            elif choice == '8':
                self.load_data()
            elif choice == '9':
                self.view_current_data()
            elif choice == '0':
                print("Exiting program...")
                break
            else:
                print("Invalid choice. Please try again.")

# Run the application
if __name__ == "__main__":
    app = RAWScoreCalculator()
    app.run()
