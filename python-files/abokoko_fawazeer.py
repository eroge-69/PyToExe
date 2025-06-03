
import random

fawazeer = [
    ("علي", "ما هو الشيء الذي لا يمشي إلا بالضرب؟", "المسمار"),
    ("منى", "ما هو الشيء الذي كلما أخذت منه يكبر؟", "الحفرة"),
    ("سامي", "شيء إذا أضفت له ماء كبر وإذا جف صغر، ما هو؟", "الإسفنج"),
    ("نهى", "ما هو الشيء الذي يسمع بلا أذن ويتكلم بلا لسان؟", "التليفون"),
]

while True:
    name, question, answer = random.choice(fawazeer)
    print(f"{name} سأل: {question}")
    user_answer = input("إجابتك: ").strip()
    if user_answer == answer:
        print("إجابة صحيحة 🎉")
    else:
        print(f"غلط! الإجابة الصحيحة هي: {answer}")
    if input("تحب فزورة تانية؟ (نعم/لا): ").strip().lower() != "نعم":
        print("مع السلامة يا نجم 🖐️")
        break
