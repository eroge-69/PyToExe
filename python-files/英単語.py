import random

# 単語リストと意味（辞書）
word_dict = {
    "open": "あいている、営業中で",
    "from": "〜から",
    "that": "これは、あれは",
    "this": "これは、この",
    "we": "私たち、私たちが",
    "dictionary": "辞書",
    "correct": "正しい",
    "almost": "ほとんど",
    "wrong": "間違っている",
    "traditional": "伝統的な",
    "a little": "少し、少しは",
    "gift": "贈り物",
    "who": "だれ、だれが",
    "character": "性格、登場人物",
    "know": "知っている、見知っている",
    "idea": "考え、意見",
    "maybe": "たぶん",
    "carry": "運ぶ",
    "get to": "〜に着く",
    "go straight": "まっすぐ行く",
    "street": "通り",
    "turn left": "左へ曲がる、曲がる",
    "on your right": "右側に",
    "at the corner": "その角を",
    "where": "どこに、どこへ"
}

# 単語クイズの問題作成
def get_word_quizzes():
    quizzes = []
    words = random.sample(list(word_dict.keys()), 3)
    for word in words:
        correct = word_dict[word]
        # 選択肢を作成（正解＋不正解2つ）
        choices = [correct]
        wrong_choices = random.sample(
            [v for k, v in word_dict.items() if v != correct], 2
        )
        choices.extend(wrong_choices)
        random.shuffle(choices)
        quizzes.append({"word": word, "choices": choices, "answer": correct})
    return quizzes

# 記述問題を作成
def get_writing_question():
    word = random.choice(list(word_dict.keys()))
    return f"「{word}」を使って英語の文を1つ書いてください。意味：{word_dict[word]}"

# 選択問題を出題
def ask_choice_quiz(quiz):
    print(f"\n「{quiz['word']}」の意味は？")
    for i, choice in enumerate(quiz["choices"], 1):
        print(f"{i}. {choice}")
    try:
        ans = int(input("番号を選んでください：")) - 1
        if quiz["choices"][ans] == quiz["answer"]:
            print("✅ 正解！")
        else:
            print(f"❌ 不正解。正解は「{quiz['answer']}」です。")
    except:
        print("⚠ 入力が無効です。")

# 記述問題を出題
def ask_writing():
    question = get_writing_question()
    print("\n【記述問題】")
    print(question)
    input("あなたの答え：")
    print("📝 入力ありがとうございます！")

# メイン処理
def main():
    round_num = 0
    while True:
        round_num += 1
        print(f"\n====== 第{round_num}ラウンド ======")

        # 英単語選択問題3問
        quizzes = get_word_quizzes()
        for quiz in quizzes:
            ask_choice_quiz(quiz)

        # 記述問題1問
        ask_writing()

        # 続けるか確認
        cont = input("\n次のラウンドに進みますか？ (y/n)：").lower()
        if cont != 'y':
            print("👋 クイズを終了します。お疲れさまでした！")
            break

if __name__ == "__main__":
    main()