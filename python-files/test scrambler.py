import random

LETTERS = 'abcdefgh'

def main(input_filename = 'input.txt', output_filename = 'output.txt', number_of_variants = 4):
    scrambled_tests = get_scrambled_tests_from_file(input_filename, number_of_variants)
    output_string = ''
    for scrambled_test in scrambled_tests:
        output_string += get_string_from_scrambled_test(scrambled_test) + '\f'
    with open(output_filename, mode='w', encoding='utf-8') as f:
        f.write(output_string)

def get_scrambled_tests_from_file(filename = 'input.txt', number_of_variants = 4):
    original_test = get_test_from_file(filename)
    output = []
    for i in range(1, number_of_variants + 1):
        output.append(get_scrambled_test(original_test, i))
    return output


def get_test_from_file(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
        test = []
        current_question = {'question': '', 'wrong_answers': [], 'right_answer': False}
        for line in lines:
            if len(line) == 0:
                continue
            if line[0] != '\t':
                if current_question['right_answer']:
                    test.append(current_question)
                current_question = {'question': line, 'wrong_answers': [], 'right_answer': False}
            else:
                answer = line[1:]
                if current_question['right_answer']:
                    current_question['wrong_answers'].append(answer)
                else:
                    current_question['right_answer'] = answer
        if current_question['right_answer']:
            test.append(current_question)
    return test
            

def get_scrambled_test(original_test, test_number):
    scrambled_test = {'test_number': test_number, 'questions': []}
    shuffled_test = shuffle_list(original_test)
    for question in shuffled_test:
        if question['right_answer'] == False:
            continue
        scrambled_question = {'question': question['question'], 'answers': shuffle_list(question['wrong_answers'] + [question['right_answer']]), 'right_answer': question['right_answer']}
        scrambled_test['questions'].append(scrambled_question)
    return scrambled_test
                              
def get_string_from_scrambled_test(scrambled_test):
    test_string = 'Questions for version ' + str(scrambled_test['test_number']) + ':'
    answer_key_string = '\fAnswer key for version ' + str(scrambled_test['test_number']) + ':'
    question_number = 1
    for question in scrambled_test['questions']:
        test_string += '\n\n'
        test_string += str(question_number) + '. ' + question['question']
        test_string += create_answers_string(question['answers'])
        answer_key_string += create_answer_key_string(question, question_number)
        question_number += 1
    return test_string + answer_key_string

def create_answers_string(answers):
    output = '\n'
    for i in range(0, len(answers)):
        output += LETTERS[i] + '. '
        output += answers[i] + '\n'
    return output
        
        
def create_answer_key_string(question, question_number):
    output = '\n' + str(question_number) + '. '
    i = question['answers'].index(question['right_answer'])
    output += LETTERS[i]
    return output

def shuffle_list(to_shuffle):
    l = to_shuffle.copy()
    output = []
    while len(l):
        i = random.randint(0, len(l) - 1)
        output.append(l[i])
        l = l[0:i] + l[i+1:]
    return output

main()
