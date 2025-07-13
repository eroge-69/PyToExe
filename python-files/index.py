import tkinter as tk
from tkinter import messagebox, scrolledtext
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Training data: full sentences per trait (just 10 per trait for demo)
training_sentences = [
    # Openness
    "I love exploring new ideas and artistic creativity.",
    "Reading books about philosophy and abstract concepts excites me.",
    "I enjoy imagining innovative solutions to problems.",
    "Traveling and experiencing different cultures fascinates me.",
    "I often daydream about fantasy worlds and stories.",
    "I like trying experimental art and design.",
    "I am curious and open to novel experiences.",
    "I enjoy music, poetry, and literature.",
    "My mind is always full of creative thoughts.",
    "I appreciate aesthetics and unique perspectives.",
    "I want to be an editor",
    "I want to be a vlogger",

    # Conscientiousness
    "I am very organized and always make detailed plans.",
    "I complete my tasks on time and with great care.",
    "I like to keep my schedule structured and follow routines.",
    "Being responsible and reliable is very important to me.",
    "I work hard and focus on achieving my goals.",
    "I am disciplined and pay attention to details.",
    "I prefer a clean and methodical work environment.",
    "I set deadlines and make sure I meet them.",
    "I keep track of my habits to improve productivity.",
    "Planning ahead and following through is how I operate.",

    # Extraversion
    "I enjoy socializing and meeting new people.",
    "I am talkative and energetic in groups.",
    "Being the center of attention excites me.",
    "I love participating in parties and events.",
    "I am outgoing and enthusiastic in my activities.",
    "I like working in teams and engaging with others.",
    "People say I am cheerful and friendly.",
    "I feel energized by being around others.",
    "I enjoy public speaking and leading groups.",
    "I am spontaneous and love dynamic environments.",

    # Agreeableness
    "I am kind and always willing to help others.",
    "I care deeply about people’s feelings and wellbeing.",
    "Being cooperative and supportive is natural to me.",
    "I am patient and forgiving in difficult situations.",
    "I enjoy volunteering and contributing to the community.",
    "People say I am empathetic and nurturing.",
    "I listen carefully and try to understand others.",
    "I prefer peaceful and harmonious environments.",
    "I am loyal and trustworthy to my friends.",
    "I like working as part of a team to help others.",

    # Neuroticism
    "I often feel anxious and worry about the future.",
    "I can get moody and sensitive easily.",
    "Stressful situations make me feel nervous and tense.",
    "I sometimes struggle with self-doubt and insecurity.",
    "I tend to overthink problems and feel overwhelmed.",
    "I am shy and avoid confrontation.",
    "I get irritated or upset more than others.",
    "I feel vulnerable and emotionally fragile at times.",
    "I find it hard to handle pressure without stress.",
    "I sometimes withdraw when I feel distressed."
]

# Corresponding labels for each sentence
training_labels = [
    "Openness", "Openness", "Openness", "Openness", "Openness",
    "Openness", "Openness", "Openness", "Openness", "Openness",
    "Openness", "Openness",

    "Conscientiousness", "Conscientiousness", "Conscientiousness", "Conscientiousness", "Conscientiousness",
    "Conscientiousness", "Conscientiousness", "Conscientiousness", "Conscientiousness", "Conscientiousness",

    "Extraversion", "Extraversion", "Extraversion", "Extraversion", "Extraversion",
    "Extraversion", "Extraversion", "Extraversion", "Extraversion", "Extraversion",

    "Agreeableness", "Agreeableness", "Agreeableness", "Agreeableness", "Agreeableness",
    "Agreeableness", "Agreeableness", "Agreeableness", "Agreeableness", "Agreeableness",

    "Neuroticism", "Neuroticism", "Neuroticism", "Neuroticism", "Neuroticism",
    "Neuroticism", "Neuroticism", "Neuroticism", "Neuroticism", "Neuroticism"
]

CAREER_SUGGESTIONS = {
    "Openness": [
        # Original
        "Artist", "Writer", "Graphic Designer", "Musician", "Architect",
        "Creative Director", "Philosopher", "Research Scientist", "Travel Blogger", "Film Critic", "Editor",
        # Added from ICT
        "Software Developer", "Data Scientist", "UI/UX Designer", "Game Developer",
        # Added from Entertainment
        "Actor", "Director", "Animator", "Composer",
        # Added from Education
        "College Professor", "Curriculum Developer"
    ],
    "Conscientiousness": [
        # Original
        "Accountant", "Engineer", "Project Manager", "Surgeon", "Data Analyst",
        "Auditor", "Pharmacist", "Quality Control Inspector", "IT Manager", "Civil Engineer",
        # Added from Finance
        "Financial Analyst", "Tax Consultant", "Risk Manager", "Financial Planner",
        # Added from Manufacturing
        "Production Manager", "Industrial Engineer", "Logistics Coordinator",
        # Added from Healthcare
        "Healthcare Administrator", "Medical Assistant"
    ],
    "Extraversion": [
        # Original
        "Salesperson", "Teacher", "Public Relations Manager", "Flight Attendant", "Event Planner",
        "Marketing Executive", "Customer Service Rep", "Radio DJ", "Sports Coach", "Recruiter",
        # Added from Hospitality
        "Restaurant Manager", "Hotel Manager", "Bartender", "Concierge",
        # Added from Education
        "School Counselor", "Kindergarten Teacher",
        # Added from Entertainment
        "TV Presenter", "Radio Host", "Talent Agent"
    ],
    "Agreeableness": [
        # Original
        "Nurse", "Social Worker", "Counselor", "Therapist", "Human Resources Specialist",
        "Volunteer Coordinator", "Kindergarten Teacher", "Veterinarian", "School Counselor", "Life Coach",
        # Added from Healthcare
        "Physical Therapist", "Speech-Language Pathologist", "Dietitian",
        # Added from Education
        "Special Education Teacher", "Education Coordinator",
        # Added Social & Community fields (similar to Agreeableness)
        "Community Service Manager", "Nonprofit Program Manager"
    ],
    "Neuroticism": [
        # Original
        "Artist", "Researcher", "Poet", "Academic Researcher",
        "Librarian", "Translator", "Data Entry Clerk", "Medical Coder", "Lab Technician",
        # Added calming or independent jobs from Education and ICT
        "Archivist", "Technical Writer", "Library Technician",
        # Added some healthcare tech roles
        "Medical Laboratory Scientist", "Clinical Research Coordinator"
    ]
}

FIELD_KEYWORDS = {
    "ICT": ["ict", "information technology", "software", "programming", "coding", "computer", "technology", "it"],
    "Healthcare": ["health", "nurse", "doctor", "medical", "therapy", "clinic", "pharmacy", "patient"],
    "Education": ["teacher", "education", "school", "learning", "student", "classroom", "tutor"],
    "Hospitality": ["cooking", "chef", "restaurant", "hotel", "hospitality", "food", "catering", "waiter", "bartender"],
    "Agriculture": ["farming", "soil", "crop", "livestock", "agriculture", "farm", "horticulture"],
    "Finance": ["banking", "investment", "audit", "finance", "accounting", "tax", "budget", "loan"],
    "Manufacturing": ["factory", "assembly", "logistics", "manufacturing", "production", "machinery", "warehouse"],
    "Entertainment": ["actor", "film", "music", "theater", "entertainment", "concert", "show", "dance", "cinema"],
    "Sports": ["sport", "athlete", "coach", "fitness", "training", "exercise", "gym", "physical education"],
    "Journalism": ["journalist", "reporter", "news", "media", "broadcast", "editorial", "press", "correspondent", "writing", "writer", "article", "report", "journalism"]

}

FIELD_JOBS = {
    "ICT": [
        "Software Developer", "IT Manager", "System Administrator", "Network Engineer",
        "Programmer", "Data Analyst", "Computer Technician", "Web Developer",
        "Cybersecurity Specialist", "Database Administrator", "Cloud Engineer",
        "Mobile App Developer", "DevOps Engineer", "UI/UX Designer", "Game Developer",
        "IT Support Specialist", "Information Security Analyst", "Software Tester",
        "Solutions Architect", "Business Analyst", "Hardware Engineer",
        "Machine Learning Engineer", "AI Specialist", "Blockchain Developer",
        "Computer Systems Analyst", "Network Architect", "Data Scientist",
        "IT Consultant", "Software Engineer"
    ],
    "Healthcare": [
        "Nurse", "Doctor", "Pharmacist", "Therapist", "Medical Coder",
        "Lab Technician", "Healthcare Administrator", "Physical Therapist",
        "Radiologic Technologist", "Occupational Therapist", "Medical Assistant",
        "Dental Hygienist", "Anesthesiologist", "Surgeon", "Psychologist",
        "Dietitian", "Speech-Language Pathologist", "Respiratory Therapist",
        "Paramedic", "Optometrist", "Chiropractor", "Phlebotomist",
        "Clinical Research Coordinator", "Veterinarian", "Medical Laboratory Scientist",
        "Nuclear Medicine Technologist", "Genetic Counselor", "Emergency Medical Technician",
        "Biomedical Engineer", "Health Educator"
    ],
    "Education": [
        "Teacher", "Tutor", "School Counselor", "Kindergarten Teacher", "Education Coordinator",
        "Special Education Teacher", "School Principal", "Curriculum Developer", "Instructional Designer",
        "College Professor", "Educational Consultant", "Librarian", "Education Administrator",
        "Speech Therapist", "Teaching Assistant", "Adult Education Instructor", "Early Childhood Educator",
        "Guidance Counselor", "Substitute Teacher", "ESL Teacher", "Coach", "Academic Advisor",
        "Test Administrator", "Online Tutor", "Education Program Manager",
        "Vocational Trainer", "School Psychologist", "Education Policy Analyst",
        "Reading Specialist", "School Social Worker"
    ],
    "Hospitality": [
        "Chef", "Baker", "Restaurant Manager", "Hotel Manager", "Sous Chef",
        "Baker", "Catering Manager", "Waiter", "Waitress", "Bartender",
        "Concierge", "Housekeeper", "Event Coordinator", "Barista",
        "Food and Beverage Manager", "Sommelier", "Travel Agent",
        "Tour Guide", "Cruise Director", "Front Desk Clerk",
        "Casino Host", "Banquet Manager", "Guest Services Manager",
        "Hospitality Trainer", "Room Service Attendant", "Kitchen Assistant",
        "Hotel Sales Manager", "Restaurant Host", "Food Critic",
        "Kitchen Manager", "Pastry Chef"
    ],
    "Agriculture": [
        "Agronomist", "Farm Manager", "Agricultural Technician", "Horticulturist",
        "Livestock Manager", "Soil Scientist", "Crop Consultant", "Rancher",
        "Agricultural Engineer", "Farm Equipment Operator", "Irrigation Specialist",
        "Plant Breeder", "Food Scientist", "Agricultural Economist",
        "Veterinary Technician", "Agri-business Manager", "Fertilizer Technician",
        "Greenhouse Manager", "Farm Labor Supervisor", "Extension Agent",
        "Aquaculture Technician", "Forester", "Pest Control Advisor",
        "Agricultural Inspector", "Seed Production Specialist", "Organic Farm Specialist",
        "Bee Keeper", "Compost Specialist", "Agricultural Sales Representative",
        "Landscape Architect"
    ],
    "Finance": [
        "Financial Analyst", "Accountant", "Investment Banker", "Auditor",
        "Tax Consultant", "Budget Analyst", "Stock Broker", "Credit Analyst",
        "Loan Officer", "Risk Manager", "Financial Planner", "Treasury Analyst",
        "Insurance Underwriter", "Actuary", "Compliance Officer",
        "Financial Controller", "Mortgage Advisor", "Payroll Specialist",
        "Private Equity Analyst", "Portfolio Manager", "Wealth Manager", "Fund Manager",
        "Corporate Finance Analyst", "Bank Teller", "Cash Manager", "Cost Estimator",
        "Financial Advisor", "Quantitative Analyst", "Operations Analyst",
        "Credit Manager", "Business Analyst", "Financial Examiner", "Billing Specialist"
    ],
    "Manufacturing": [
        "Production Manager", "Quality Control Inspector", "Manufacturing Engineer",
        "Assembly Line Worker", "Logistics Coordinator", "Warehouse Manager",
        "Machinist", "CNC Operator", "Industrial Engineer", "Supply Chain Analyst",
        "Safety Manager", "Maintenance Technician", "Packaging Specialist",
        "Plant Manager", "Material Handler", "Inventory Control Specialist",
        "Process Engineer", "Tool and Die Maker", "Manufacturing Technician",
        "Fabricator", "Operations Manager", "Production Planner", "Welder",
        "Industrial Designer", "Quality Assurance Manager", "Machine Operator",
        "Automation Engineer", "Product Developer", "Shipping Coordinator", "Lean Manufacturing Specialist"
    ],
    "Entertainment": [
        "Actor", "Musician", "Director", "Producer", "Screenwriter",
        "Dancer", "Choreographer", "Cinematographer", "Composer", "Sound Engineer",
        "Video Editor", "Lighting Technician", "Stage Manager", "Makeup Artist",
        "Set Designer", "Animator", "Special Effects Artist", "Casting Director",
        "Talent Agent", "Film Critic", "Broadcast Technician", "TV Presenter",
        "Radio Host", "Voice Actor", "Magician", "Comedian", "Theater Technician",
        "Photographer", "Music Producer", "Event Coordinator"
    ],
    "Sports": [
    "Athlete", "Coach", "Fitness Trainer", "Sports Psychologist", "Physical Education Teacher",
    "Sports Commentator", "Athletic Trainer", "Sports Agent", "Referee", "Sports Nutritionist",
    "Gym Instructor", "Strength and Conditioning Coach", "Sports Scientist", "Rehabilitation Specialist",
    "Sports Official", "Exercise Physiologist", "Kinesiologist", "Sports Journalist", "Team Manager",
    "Scout", "Personal Trainer", "Lifeguard", "Yoga Instructor", "Dance Instructor",
    "Sports Medicine Doctor", "Massage Therapist", "Sports Marketing Manager", "Athletic Director",
    "Event Coordinator", "Sports Photographer"
],

    "Journalism": [
        "journalist", "reporter", "news", "media", "broadcast", "editorial", "press",
        "correspondent", "writing", "writer", "article", "report", "journalism"
    ],
}


# Train vectorizer and classifier
vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(training_sentences)
classifier = MultinomialNB()
classifier.fit(X_train, training_labels)

def predict_traits(text):
    X_test = vectorizer.transform([text])
    probs = classifier.predict_proba(X_test)[0]
    traits = classifier.classes_
    return dict(zip(traits, probs))

def suggest_jobs(trait_scores, top_n=2, user_text="", field_weight=3.0, max_field_jobs=20, max_total_jobs=20):
    # Sort traits by probability descending
    sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
    top_traits = [trait for trait, _ in sorted_traits[:top_n]]
    user_text_lower = user_text.lower()

    # Detect fields based on keywords in user text
    detected_fields = [field for field, keywords in FIELD_KEYWORDS.items()
                       if any(keyword in user_text_lower for keyword in keywords)]

    # Gather jobs related to top traits
    trait_jobs = []
    for trait in top_traits:
        trait_jobs.extend(CAREER_SUGGESTIONS.get(trait, []))
    trait_jobs = list(dict.fromkeys(trait_jobs))  # remove duplicates

    if detected_fields:
        field = detected_fields[0]  # prioritize first detected field
        field_jobs = FIELD_JOBS.get(field, [])

        # Score dictionary: job -> score
        job_scores = {}

        # Assign scores to field jobs (boosted)
        for job in field_jobs[:max_field_jobs]:  # limit how many field jobs to consider
            job_scores[job] = field_weight

        # Assign scores to trait jobs (lower weight)
        for job in trait_jobs:
            if job in job_scores:
                job_scores[job] += 1  # if already field job, add smaller increment
            else:
                job_scores[job] = 1

        # Sort by score descending
        sorted_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top max_total_jobs jobs (default 20)
        return [job for job, score in sorted_jobs[:max_total_jobs]]

    else:
        # No field detected, return trait jobs only (limit 10)
        return trait_jobs[:10]

def on_analyze():
    text = input_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Input Needed", "Please enter a paragraph describing your personality and interests.")
        return

    trait_scores = predict_traits(text)
    top_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
    trait_text = "\n".join([f"{trait}: {score:.2f}" for trait, score in top_traits])

    jobs = suggest_jobs(trait_scores, user_text=text)
    jobs_text = "\n".join(jobs)

    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "Predicted Personality Trait Scores:\n")
    result_text.insert(tk.END, trait_text + "\n\n")
    result_text.insert(tk.END, "Suggested Careers:\n")
    result_text.insert(tk.END, jobs_text)
    result_text.config(state=tk.DISABLED)

# GUI Setup
root = tk.Tk()
root.title("Personality and Career Suggestion Tool")

tk.Label(root, text="Enter a paragraph about your personality and interests:").pack(padx=10, pady=5)
input_text = scrolledtext.ScrolledText(root, width=60, height=8)
input_text.pack(padx=10, pady=5)

analyze_button = tk.Button(root, text="Analyze and Suggest Careers", command=on_analyze)
analyze_button.pack(pady=10)

result_text = scrolledtext.ScrolledText(root, width=60, height=20, state=tk.DISABLED)
result_text.pack(padx=10, pady=5)

root.mainloop()
