from hazm import *
import os

# آماده‌سازی ابزارها
normalizer = Normalizer()
tokenizer = WordTokenizer()
tagger = POSTagger(model='resources/postagger.model')
parser = DependencyParser(tagger=tagger, lemmatizer=Lemmatizer())

# جملات نمونه
text = "علی معلم است. هوا بسیار سرد بود. او در اتاق تنها شد. پدرم یک مهندس عالی بود."

# پیش‌پردازش متن
sentences = sent_tokenize(normalizer.normalize(text))

for sentence in sentences:
    print(f"\nجمله: {sentence}")
    words = tokenizer.tokenize(sentence)
    tagged = tagger.tag(words)
    tree = parser.parse(words)

    # پیمایش درخت نحوی برای یافتن فعل‌های ربطی و مسندها
    for dep in tree:
        if dep.relation == 'SBJ':  # نهاد
            subject = dep.word
            verb_node = dep.head  # فعل یا کلمه وابسته به نهاد

            # بررسی اینکه فعل ربطی است یا نه
            if verb_node.word in ['است', 'هست', 'بود', 'شد', 'می‌شود', 'خواهد بود']:
                # جستجوی مسند که معمولاً با رابطه 'VC' یا 'COM' (متمم فعلی) در درخت نحوی نشان داده می‌شود
                for possible_pred in tree:
                    if possible_pred.head == verb_node and possible_pred.relation in ['VC', 'COM', 'PCOMP']:
                        predicate = possible_pred.word
                        print(f"نهاد: {subject}، مسند: {predicate}، فعل ربطی: {verb_node.word}")
