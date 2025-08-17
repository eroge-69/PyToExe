import requests

# ===== CONFIG =====
"WEBHOOK_URL = https://discord.com/api/webhooks/1406757743737573558/DfEiuPdmasBylXAs2k83W7jR0ddvTFGAiMGJ_JRldPJspAKjcK-DJitTEbqJYXexORwU"  # pune aici webhook-ul tău

# ===== FUNCTII =====
def send_result_to_discord(name, age, score, total, result):
    data = {
        "content": f"📢 Rezultat Test Maturitate\n👤 Nume: **{name}**\n🎂 Vârsta: **{age}**\n✅ Răspunsuri corecte: **{score}/{total}**\n🏆 Rezultat final: **{result}**"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Eroare la trimiterea pe Discord: {e}")

# ===== TEST =====
def test_maturitate():
    print("=== TEST DE MATURITATE (FiveM Roleplay) ===")
    name = input("Numele tău: ")
    age = input("Introdu vârsta ta: ")

    questions = [
        {
            "q": "Ce trebuie să faci într-un server de Roleplay?",
            "options": ["A. Te comporți ca în viața reală", "B. Te lupți cu toată lumea", "C. Distrugi totul"],
            "correct": "A"
        },
        {
            "q": "Cum trebuie să te comporți în zonele publice?",
            "options": ["A. Vorbești normal și respecți regulile", "B. Țipi și faci haos", "C. Îți bați joc de alți jucători"],
            "correct": "A"
        },
        {
            "q": "Dacă vezi un player care încalcă regulile?",
            "options": ["A. Îl raportezi la staff", "B. Îl ignori", "C. Îl bați fără motiv"],
            "correct": "A"
        },
        {
            "q": "Ce înseamnă termenul 'Powergaming' în RP?",
            "options": ["A. Să faci acțiuni imposibile în realitate", "B. Să respecți regulile jocului", "C. Să îți faci propria poveste realistă"],
            "correct": "A"
        },
        {
            "q": "Ce înseamnă 'Metagaming'?",
            "options": ["A. Folosirea informațiilor din afara jocului în RP", "B. O regulă despre arme", "C. O metodă de a câștiga bani în joc"],
            "correct": "A"
        },
        {
            "q": "Dacă ești arestat de poliție în RP, ce faci?",
            "options": ["A. Cooperezi și respecți RP-ul", "B. Fugi cu bug-uri", "C. Începi să urli în chat"],
            "correct": "A"
        },
        {
            "q": "Cum trebuie să vorbești pe voice chat în RP?",
            "options": ["A. Ca și cum ai fi personajul tău", "B. Ca în realitate, despre orice", "C. Nu contează, vorbești cum vrei"],
            "correct": "A"
        },
        {
            "q": "Dacă un jucător nou greșește regulile, ce faci?",
            "options": ["A. Îi explici și îl ajuți", "B. Îți bați joc de el", "C. Îl elimini imediat"],
            "correct": "A"
        },
        {
            "q": "Ce înseamnă NLR (New Life Rule)?",
            "options": ["A. După ce mori, uiți tot ce s-a întâmplat", "B. Ai voie să te răzbuni imediat", "C. Poți continua povestea ca și cum nimic nu s-a întâmplat"],
            "correct": "A"
        },
        {
            "q": "Ce faci dacă vezi un bug care îți aduce avantaje?",
            "options": ["A. Îl raportezi la staff", "B. Îl folosești pentru bani", "C. Îl spui doar prietenilor"],
            "correct": "A"
        }
    ]

    score = 0
    for i, q in enumerate(questions, 1):
        print(f"\nÎntrebarea {i}: {q['q']}")
        for opt in q["options"]:
            print(opt)
        answer = input("Răspunsul tău (A/B/C): ").strip().upper()

        if answer == q["correct"]:
            print("✅ Corect!")
            score += 1
        else:
            print("❌ Greșit!")

    total = len(questions)

    # Rezultat final în funcție de scor
    if score == total:
        result = "Ai trecut testul de maturitate cu nota maximă 🎉"
    elif score >= 7:
        result = "Ai trecut testul de maturitate 👍"
    elif score >= 4:
        result = "Ai nevoie de mai multă experiență în RP 🙂"
    else:
        result = "Nu ai trecut testul ❌"

    print(f"\n=== REZULTAT FINAL ===\n{result} (Scor: {score}/{total})")

    # Trimitem pe Discord
    send_result_to_discord(name, age, score, total, result)


# ===== MAIN =====
if __name__ == "__main__":
    test_maturitate()