def calculate_values():
    """
    사용자로부터 HP, LP, EP 값을 입력받아 P, R1, R2, R3를 계산하고 출력하는 스크립트입니다.
    결과값은 세 자리마다 콤마(,)로 구분되어 표시됩니다.
    """
    try:
        # 사용자로부터 값 입력받기
        hp = float(input("HP 값을 입력하세요: "))
        lp = float(input("LP 값을 입력하세요: "))
        ep = float(input("EP 값을 입력하세요: "))

        # P 계산
        p = (hp + lp + ep) / 3

        # R1, R2, R3 계산
        r1 = (2 * p) - hp
        r2 = p + (hp - lp)
        r3 = 2 * (p - lp) + hp

        # 결과 출력 (콤마 형식으로)
        print("\n--- 결과 ---")
        print(f"P = {p:,.2f}")
        print(f"R1 = {r1:,.2f}")
        print(f"R2 = {r2:,.2f}")
        print(f"R3 = {r3:,.2f}")

    except ValueError:
        print("유효한 숫자를 입력해 주세요.")
    except ZeroDivisionError:
        print("나눗셈 오류가 발생했습니다. 입력값을 확인해 주세요.")

# 스크립트 실행
if __name__ == "__main__":
    calculate_values()