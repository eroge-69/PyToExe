import pandas as pd

# Create a workout log template with planned sets/reps and space for actual performance
workouts = {
    'Week': [],
    'Day': [],
    'Exercise': [],
    'Target Sets': [],
    'Target Reps': [],
    'Weight Used': [],
    'Reps Achieved': []
}

# Define exercises and target ranges
plan = {
    'Day 1 – Upper Body (Strength)': [
        ('Barbell Bench Press', '4', '5'),
        ('Pull-Ups', '4', '6-8'),
        ('Incline Dumbbell Press', '3', '8-10'),
        ('Barbell Rows', '4', '6-8'),
        ('Dumbbell Lateral Raises', '3', '12-15'),
        ('Face Pulls (cable)', '3', '12-15'),
        ('Optional Bicep Curls', '3', '10-12')
    ],
    'Day 2 – Lower Body (Strength)': [
        ('Barbell Back Squat', '4', '5'),
        ('Romanian Deadlift', '4', '6-8'),
        ('Leg Press', '3', '10-12'),
        ('Walking Lunges (Dumbbells)', '3', '10 per leg'),
        ('Seated/Lying Leg Curl', '3', '12-15'),
        ('Standing Calf Raises', '4', '12-15')
    ],
    'Day 3 – Upper Body (Hypertrophy)': [
        ('Dumbbell Bench Press', '4', '8-12'),
        ('Lat Pulldown (wide grip)', '4', '10-12'),
        ('Seated Dumbbell Shoulder Press', '3', '10-12'),
        ('Chest-Supported Row', '3', '10-12'),
        ('Cable Lateral Raises', '3', '12-15'),
        ('Cable Rope Face Pulls', '3', '12-15'),
        ('Incline Dumbbell Curls', '3', '10-12'),
        ('Tricep Rope Pushdowns', '3', '12-15')
    ],
    'Day 4 – Lower Body (Hypertrophy)': [
        ('Front Squats or Goblet Squats', '4', '8-10'),
        ('Romanian Deadlifts (lighter)', '4', '8-12'),
        ('Bulgarian Split Squats', '3', '10 per leg'),
        ('Hip Thrusts (Barbell)', '4', '10-12'),
        ('Leg Extension', '3', '12-15'),
        ('Seated Calf Raises', '4', '12-15')
    ]
}

# Populate the dictionary for Week 1
for day, exercises in plan.items():
    for ex in exercises:
        workouts['Week'].append('Week 1')
        workouts['Day'].append(day)
        workouts['Exercise'].append(ex[0])
        workouts['Target Sets'].append(ex[1])
        workouts['Target Reps'].append(ex[2])
        workouts['Weight Used'].append('')
        workouts['Reps Achieved'].append('')

# Convert to DataFrame
df = pd.DataFrame(workouts)

# Save to Excel
file_path = '/mnt/data/upper_lower_workout_tracker.xlsx'
df.to_excel(file_path, index=False)

file_path
