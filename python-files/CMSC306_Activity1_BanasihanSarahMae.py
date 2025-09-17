# Activity_1 Computer Architecture and Organization

print("----- STUDENT ACADEMIC RECORD SYSTEM -----")

# 1. Basic Python Syntax - Student Data Variables
full_name = "Sarah Mae C. Banasihan"
year = 3
section = "BSCS 3A - IS"
distance_from_home = 3.5
working_student = False
subjects = ["GEC 107", "GEC 108", "CMSC 204", "ITEC 106", "CSEL 301", "CSEL 302", "PATHFIT 4"]

# Your actual semester grades (1.00 is highest, 4.00 is lowest)
grades = [1.25, 1.50, 1.50, 1.00, 1.50, 1.50, 1.00]
units = [3, 3, 3, 3, 3, 3, 2]
gwa = 1.34
total_units = 20

# Course descriptions for reference
course_descriptions = [
    "Science, Technology and Society",
    "Ethics", 
    "Algorithms and Complexity",
    "Applications Development and Emerging Technologies",
    "Introduction to Graphics and Visual Computing",
    "Introduction to Intelligent Systems",
    "Choice of Dance, Sports, Martial Arts, Group Exercise, Outdoor and Adventure Activities"
]

# Display student information
print("\nStudent Academic Information:")
print(f"Full Name: {full_name}")
print(f"Year: {year}")
print(f"Section: {section}")
print(f"Distance from Home: {distance_from_home} km")
print(f"Working Student: {working_student}")
print(f"GWA: {gwa}")
print(f"Total Units: {total_units}")
print("\nGrading System: 1.00 (Excellent) to 4.00 (Failed)")

# 2. Control Structures

# IF-ELSE with relationship
print("\n--- IF-ELSE Control Structure ---")
if gwa <= 1.45 and len([g for g in grades if g <= 1.25]) >= 2:
    academic_standing = "Outstanding Academic Performance - DOST Scholar"
elif gwa <= 1.75 and working_student:
    academic_standing = "Dean's List with Work Balance - Excellent Performance"  
elif gwa <= 2.00:
    academic_standing = "Honor Roll - Very Good Performance"
else:
    academic_standing = "Good Standing"

print(f"Academic Standing: {academic_standing}")

# Scholarship status
print("Status: DOST Scholar - Department of Science and Technology")

# FOR LOOP with relationship
print("\n--- FOR LOOP Control Structure ---")
print("Processing each course grade:")
perfect_grades = 0
major_subjects = ["CMSC 204", "ITEC 106", "CSEL 301", "CSEL 302"]

for i in range(len(subjects)):
    course = subjects[i]
    grade = grades[i]
    unit = units[i]
    
    # Determine grade classification
    if grade == 1.00:
        grade_level = "PERFECT"
        perfect_grades += 1
    elif grade <= 1.25:
        grade_level = "EXCELLENT"
    elif grade <= 1.75:
        grade_level = "VERY GOOD"
    elif grade <= 2.25:
        grade_level = "GOOD"
    else:
        grade_level = "SATISFACTORY"
    
    # Check if major subject
    subject_type = "MAJOR" if course in major_subjects else "GENERAL"
    
    print(f"{course}: {grade} ({unit} units) - {grade_level} [{subject_type}]")

print(f"\nPerfect Grades (1.00): {perfect_grades} subjects")

# WHILE LOOP with relationship
print("\n--- WHILE LOOP Control Structure ---")
index = 0
weighted_total = 0
unit_total = 0
high_performance_count = 0

print("Calculating weighted GWA verification:")
while index < len(grades):
    current_grade = grades[index]
    current_units = units[index]
    weighted_points = current_grade * current_units
    
    weighted_total += weighted_points
    unit_total += current_units
    
    # Count high performance subjects (grade <= 1.50)
    if current_grade <= 1.50:
        high_performance_count += 1
        print(f"Course {index + 1}: {subjects[index]} = {current_grade} × {current_units} = {weighted_points} (High Performance)")
    
    index += 1

calculated_gwa = weighted_total / unit_total
print(f"\nVerification - Calculated GWA: {calculated_gwa:.2f}")
print(f"Official GWA: {gwa}")
print(f"High Performance Subjects: {high_performance_count}/{len(subjects)}")

# 3. Memory Simulation using List
print("\n--- MEMORY SIMULATION ---")

# Memory storage system
academic_memory = []

# Store complete academic record in memory (CPU writes to memory)
student_record = {
    "personal_info": {
        "name": full_name,
        "year": year,
        "section": section,
        "distance": distance_from_home,
        "working_student": working_student
    },
    "academic_data": {
        "subjects": subjects.copy(),
        "grades": grades.copy(),
        "units": units.copy(),
        "course_descriptions": course_descriptions.copy(),
        "gwa": gwa,
        "total_units": total_units
    },
    "performance_metrics": {
        "perfect_grades": perfect_grades,
        "high_performance_count": high_performance_count,
        "academic_standing": academic_standing
    }
}

# Write to memory
academic_memory.append(student_record)
print("✓ Complete academic record stored in memory")

# Read from memory (CPU retrieval operation)
retrieved_data = academic_memory[0]
print(f"✓ Retrieved student: {retrieved_data['personal_info']['name']}")
print(f"✓ Memory shows GWA: {retrieved_data['academic_data']['gwa']}")

# Update memory with additional calculations (CPU processing)
best_grade = min(retrieved_data['academic_data']['grades'])
worst_grade = max(retrieved_data['academic_data']['grades'])
grade_range = worst_grade - best_grade

# Find best and worst performing subjects
best_subject_index = retrieved_data['academic_data']['grades'].index(best_grade)
worst_subject_index = retrieved_data['academic_data']['grades'].index(worst_grade)

retrieved_data['performance_metrics']['best_grade'] = best_grade
retrieved_data['performance_metrics']['best_subject'] = subjects[best_subject_index]
retrieved_data['performance_metrics']['worst_grade'] = worst_grade  
retrieved_data['performance_metrics']['worst_subject'] = subjects[worst_subject_index]
retrieved_data['performance_metrics']['grade_consistency'] = grade_range

print(f"✓ Updated memory: Best subject is {subjects[best_subject_index]} ({best_grade})")
print(f"✓ Updated memory: Grade consistency range = {grade_range:.2f}")

# Search memory for academic insights (CPU analysis)
dost_scholarship_maintained = retrieved_data['academic_data']['gwa'] <= 2.50
academic_good_standing = retrieved_data['academic_data']['gwa'] <= 3.00

retrieved_data['predictions'] = {
    "dost_scholarship_maintained": dost_scholarship_maintained,
    "academic_good_standing": academic_good_standing,
    "dean_list_qualified": retrieved_data['academic_data']['gwa'] <= 1.50
}

print(f"✓ Memory analysis: DOST Scholarship maintained = {dost_scholarship_maintained}")
print(f"✓ Academic good standing = {academic_good_standing}")

# Display final memory state summary
print("\n--- FINAL MEMORY STATE SUMMARY ---")
memory_data = academic_memory[0]
print(f"Student: {memory_data['personal_info']['name']}")
print(f"Program: Bachelor of Science in Computer Science")
print(f"GWA: {memory_data['academic_data']['gwa']} ({memory_data['performance_metrics']['academic_standing']})")
print(f"Perfect Grades: {memory_data['performance_metrics']['perfect_grades']}")
print(f"Best Subject: {memory_data['performance_metrics']['best_subject']} ({memory_data['performance_metrics']['best_grade']})")
print(f"DOST Scholarship Status: Maintained")
print(f"Dean's List Qualified: {memory_data['predictions']['dean_list_qualified']}")

print("\n=== SYSTEM ANALYSIS COMPLETE ===")
print("CPU successfully processed and analyzed academic data from memory!")
print("Memory contains complete academic profile for DOST Scholar.")