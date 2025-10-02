import random
from nltk.corpus import wordnet

def print_banner():
    banner = r"""
    ================================
            DORK GENERATOR
              Author: @exobest1
    ================================
    """
    print(banner)

def generate_keywords(input_file, output_file):
    with open(input_file, 'r') as file:
        keywords = [line.strip() for line in file.readlines()]

    generated_keywords = set()

    for keyword in keywords:
        generated_keywords.add(keyword)

        generated_keywords.add(keyword + " tips")
        generated_keywords.add("how to " + keyword)
        generated_keywords.add(keyword + " guide")
        generated_keywords.add("best " + keyword)
        generated_keywords.add("buy " + keyword)

        synonyms = wordnet.synsets(keyword)
        for syn in synonyms:
            for lemma in syn.lemmas():
                generated_keywords.add(lemma.name())

    with open(output_file, 'w') as file:
        for kw in generated_keywords:
            file.write(kw + '\n')

    print(f"Generated {len(generated_keywords)} keywords and saved to {output_file}")

print_banner()
input_file = 'keywords.txt'  
output_file = 'gen_keywords.txt' 
generate_keywords(input_file, output_file)