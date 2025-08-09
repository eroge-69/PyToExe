import random

# Word banks for generating text
subjects = [
    "The working class", 
    "The bourgeoisie", 
    "Capital", 
    "Labor", 
    "The means of production", 
    "The proletariat", 
    "The capitalist system"
]

verbs = [
    "inevitably transforms", 
    "is subjugated by", 
    "liberates itself from", 
    "is consolidated through", 
    "is alienated by", 
    "is shaped by", 
    "is dismantled through"
]

objects = [
    "the historical process", 
    "class struggle", 
    "the contradictions of capitalism", 
    "material conditions", 
    "the dialectical forces of history", 
    "economic exploitation", 
    "political domination"
]

connectors = [
    "As a result,", 
    "Therefore,", 
    "Consequently,", 
    "In this way,", 
    "Thus,", 
    "Hence,"
]

conclusions = [
    "the transformation of society becomes inevitable.",
    "the old order begins to collapse under its own weight.",
    "the path to emancipation reveals itself.",
    "the revolutionary moment draws near.",
    "collective action becomes the only viable solution."
]

# Functions to build sentences
def generate_sentence():
    s = random.choice(subjects)
    v = random.choice(verbs)
    o = random.choice(objects)
    return f"{s} {v} {o}."

def generate_transition_sentence():
    connector = random.choice(connectors)
    conclusion = random.choice(conclusions)
    return f"{connector} {conclusion}"

def generate_paragraph(sentence_count=5):
    paragraph = []
    for i in range(sentence_count - 1):
        if i % 2 == 0:
            paragraph.append(generate_sentence())
        else:
            paragraph.append(generate_transition_sentence())
    paragraph.append(generate_transition_sentence())
    return " ".join(paragraph)

# Run the generator once
print(generate_paragraph(7))
