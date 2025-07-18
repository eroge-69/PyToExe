# Student Report Card Generator

# Sample Data Structure
students = {}

# ------------------- Functions -------------------

def calculate_average(marks_dict):
    return sum(marks_dict.values()) / len(marks_dict)

def assign_grade(average):
    if average >= 90:
        return 'A+'
    elif average >= 80:
        return 'A'
    elif average >= 70:
        return 'B'
    elif average >= 60:
        return 'C'
    else:
        return 'D'

def find_subject_toppers(students_dict):
    subject_toppers = {}
    for student, marks in students_dict.items():
        for subject, score in marks.items():
            if subject not in subject_toppers or score > subject_toppers[subject][1]:
                subject_toppers[subject] = (student, score)
    return subject_toppers

def display_student_report(student_name):
    if student_name in students:
        print(f"\nReport for {student_name}")
        marks = students[student_name]
        for subject, score in marks.items():
            print(f"{subject}: {score}")
        avg = calculate_average(marks)
        grade = assign_grade(avg)
        print(f"Average: {avg:.2f}")
        print(f"Grade: {grade}")
    else:
        print("Student not found.")

def students_scoring_above_90(students_dict):
    high_achievers = set()
    for student, marks in students_dict.items():
        for subject, score in marks.items():
            if score > 90:
                high_achievers.add(student)
                break
    return high_achievers

def subject_wise_class_average(students_dict):
    subject_totals = {}
    subject_counts = {}
    for marks in students_dict.values():
        for subject, score in marks.items():
            subject_totals[subject] = subject_totals.get(subject, 0) + score
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
    return {subject: subject_totals[subject] / subject_counts[subject] for subject in subject_totals}

def rank_students_by_score(students_dict):
    score_list = []
    for student, marks in students_dict.items():
        total = sum(marks.values())
        score_list.append((student, total))
    return sorted(score_list, key=lambda x: x[1], reverse=True)

# ------------------- Input Section -------------------

n = int(input("Enter number of students: "))
for _ in range(n):
    name = input("Enter student name: ")
    subjects = {}
    subjects['Math'] = int(input("Math score: "))
    subjects['English'] = int(input("English score: "))
    subjects['Science'] = int(input("Science score: "))
    students[name] = subjects

# ------------------- Output Section -------------------

# Display Reports
for student in students:
    display_student_report(student)

# Subject-wise toppers
print("\n--- Subject-wise Toppers ---")
toppers = find_subject_toppers(students)
for subject, (student, score) in toppers.items():
    print(f"{subject}: {student} with {score}")

# High achievers using sets
print("\n--- Students Scoring Above 90 in Any Subject ---")
high_achievers = students_scoring_above_90(students)
print(high_achievers)

# Using tuples to store immutable subject-score pairs (example use)
print("\n--- Subject Score Tuples ---")
for student, marks in students.items():
    score_tuples = tuple((sub, score) for sub, score in marks.items())
    print(f"{student}: {score_tuples}")

# Subject-wise class average
print("\n--- Subject-wise Class Averages ---")
averages = subject_wise_class_average(students)
for subject, avg in averages.items():
    print(f"{subject}: {avg:.2f}")

# Rank students by total score
print("\n--- Student Rankings by Total Score ---")
rankings = rank_students_by_score(students)
for i, (student, score) in enumerate(rankings, start=1):
    print(f"{i}. {student}: {score}")
.