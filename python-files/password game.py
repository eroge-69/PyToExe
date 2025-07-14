import random
import string

def generate_secret_password():
    """
    ランダムな秘密のパスワードを生成します。
    大文字アルファベット3文字から5文字の範囲です。
    """
    length = random.randint(3, 5)
    password = ''.join(random.choices(string.ascii_uppercase, k=length))
    return password

def convert_to_numeric_code(password):
    """
    アルファベットのパスワードを2桁の数字コードに変換します。
    例: 'A' -> '01', 'B' -> '02', ..., 'Z' -> '26'
    """
    numeric_code = ""
    for char in password:
        # Aを1として、アルファベット順に番号を割り振る
        numeric_code += str(ord(char) - ord('A') + 1).zfill(2)
    return numeric_code

def play_password_game():
    """
    秘密のパスワード当てゲームを実行します。
    """
    secret_password = generate_secret_password()
    secret_numeric_code = convert_to_numeric_code(secret_password)

    print("----------------------------------------------------------------")
    print("           秘密のパスワード当てゲームへようこそ！")
    print("----------------------------------------------------------------")
    print("コンピューターが秘密のパスワードを生成しました。")
    print("このパスワードは、アルファベットの大文字のみで構成され、")
    print("長さは3文字から5文字です。")

    # ここに秘密のパスワードの数字コードのみを表示します
    print(f"\n【ヒント】秘密の数字コード: {secret_numeric_code}")

    print("\nさあ、この数字コードから元のパスワードを推測して当ててみましょう！")


    while True:
        try:
            user_input = input("\nパスワードを入力してください: ").strip().upper()

            # 入力されたパスワードがアルファベット大文字のみかチェック
            if not user_input.isalpha() or not user_input.isupper():
                print("エラー: パスワードはアルファベットの大文字のみで入力してください。")
                continue

            user_numeric_code = convert_to_numeric_code(user_input)

            # ユーザーが入力したパスワードとその数字コードも表示します
            print(f"あなたの入力: {user_input} (数字コード: {user_numeric_code})")

            if user_numeric_code == secret_numeric_code:
                print("----------------------------------------------------------------")
                print("パスワードが一致しました！アクセス可能です。おめでとうございます！")
                print("----------------------------------------------------------------")
                print(f"正解のパスワードは '{secret_password}' でした！")
                break
            else:
                print("パスワードが違います。再入力してください。")
        except KeyboardInterrupt:
            print("\nゲームを中断しました。")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            print("もう一度お試しください。")

if __name__ == "__main__":
    play_password_game()