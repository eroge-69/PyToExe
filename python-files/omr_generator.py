import random
import csv

def generate_omr_responses(num_students, num_questions, options):
    """
    Generates random OMR responses.
    
    :param num_students: Number of students (each row represents one student's responses)
    :param num_questions: Number of questions on the OMR sheet
    :param options: List of possible answer options (e.g., ['A', 'B', 'C', 'D'])
    :return: A list of lists, where each inner list represents responses for one student.
    """
    responses = []
    for _ in range(num_students):
        # For each student, randomly choose one option per question.
        student_responses = [random.choice(options) for _ in range(num_questions)]
        responses.append(student_responses)
    return responses

def write_to_csv(responses, filename):
    """
    Writes the generated responses to a CSV file.
    
    :param responses: The list of student responses.
    :param filename: The name of the CSV file to write.
    """
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        # Create a header row for questions (Q1, Q2, Q3, …)
        header = ["Student"] + [f"Q{i+1}" for i in range(len(responses[0]))]
        writer.writerow(header)
        
        # Write each student's responses with a student label.
        for i, res in enumerate(responses):
            writer.writerow([f"Student_{i+1}"] + res)

if __name__ == '__main__':
    # Ask for the number of students and questions.
    try:
        num_students = int(input("Enter the number of students: "))
        num_questions = int(input("Enter the number of questions: "))
    except ValueError:
        print("Please enter valid integer numbers for students and questions.")
        exit(1)
    
    # Ask for the answer options. Use default options if input is empty.
    user_options = input("Enter answer options separated by commas (default A,B,C,D): ")
    options = [option.strip() for option in user_options.split(",")] if user_options.strip() else ["A", "B", "C", "D"]

    # Generate responses and write them to a CSV file.
    responses = generate_omr_responses(num_students, num_questions, options)
    output_file = "omr_responses.csv"
    write_to_csv(responses, output_file)
    
    print(f"OMR responses generated and saved to {output_file}")
