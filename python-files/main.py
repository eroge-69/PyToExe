import sys
import math
from typing import List, Tuple

import numpy as np
from scipy import interpolate
from numpy.polynomial import Polynomial

def read_pairs() -> Tuple[np.ndarray, np.ndarray]:
    while True:
        try:
            n = int(input("Введите количество пар (3–20): ").strip())
            if 3 <= n <= 20:
                break
            print("Число должно быть от 3 до 20.")
        except ValueError:
            print("Некорректный ввод. Введите целое число.")
    xs = []
    ys = []
    print("Введите пары X и Y (через пробел). Пример: 1 25")
    i = 1
    while len(xs) < n:
        s = input(f"{i}) ").strip()
        parts = s.split()
        if len(parts) != 2:
            print("Введите ровно два числа через пробел.")
            continue
        try:
            x = float(parts[0])
            y = float(parts[1])
        except ValueError:
            print("Некорректные числа.")
            continue
        xs.append(x)
        ys.append(y)
        i += 1
    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)
    if len(np.unique(xs)) != len(xs):
        print("X должны быть уникальны. Повторите ввод.")
        return read_pairs()
    order = np.argsort(xs)
    return xs[order], ys[order]

def read_query_xs() -> np.ndarray:
    while True:
        try:
            m = int(input("Сколько X для экстраполяции (1–20)? ").strip())
            if 1 <= m <= 20:
                break
            print("Число должно быть от 1 до 20.")
        except ValueError:
            print("Некорректный ввод. Введите целое число.")
    qxs = []
    i = 1
    print("Введите X для экстраполяции (по одному):")
    while len(qxs) < m:
        s = input(f"{i}) ").strip()
        try:
            qx = float(s)
        except ValueError:
            print("Некорректное число.")
            continue
        qxs.append(qx)
        i += 1
    return np.array(qxs, dtype=float)

def fit_polynomial(xs: np.ndarray, ys: np.ndarray, degree: int) -> Polynomial:
    coeffs = np.polyfit(xs, ys, deg=degree)
    coeffs_low = coeffs[::-1]
    return Polynomial(coeffs_low)

def piecewise_linear(xs: np.ndarray, ys: np.ndarray, query_xs: np.ndarray) -> List[float]:
    f = interpolate.interp1d(xs, ys, kind='linear', fill_value='extrapolate', assume_sorted=True)
    return f(query_xs).tolist()

def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return float('nan')
    return 1.0 - ss_res / ss_tot

def predict_and_r2(xs: np.ndarray, ys: np.ndarray, qxs: np.ndarray):
    models = [
        ("Полином 3-й степени", 3),
        ("Полином 4-й степени", 4),
        ("Полином 5-й степени", 5),
        ("Полином 6-й степени", 6),
    ]
    results = {}
    for name, deg in models:
        max_deg = min(deg, len(xs) - 1)
        try:
            p = fit_polynomial(xs, ys, max_deg)
            preds_on_query = p(qxs).tolist()
            preds_on_train = p(xs)
            r2 = r2_score(ys, preds_on_train)
            results[name] = {
                "y_pred": preds_on_query,
                "r2": r2
            }
        except Exception:
            results[name] = {
                "y_pred": [math.nan] * len(qxs),
                "r2": math.nan
            }
    # кусочно-линейная аппроксимация
    try:
        pw_preds_query = piecewise_linear(xs, ys, qxs)
        pw_preds_train = piecewise_linear(xs, ys, xs)
        r2_pw = r2_score(ys, np.array(pw_preds_train))
    except Exception:
        pw_preds_query = [math.nan] * len(qxs)
        r2_pw = math.nan
    results["Кусочно-линейная аппроксимация"] = {
        "y_pred": pw_preds_query,
        "r2": r2_pw
    }
    return results

def format_int_safe(val):
    try:
        if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
            return "NaN"
        return str(int(round(val)))
    except Exception:
        return "NaN"

def print_blocked_results(qxs: np.ndarray, results: dict):
    for name, data in results.items():
        print(f"\n=== {name} ===")
        r2 = data.get("r2", math.nan)
        if isinstance(r2, float) and not (math.isnan(r2) or math.isinf(r2)):
            print(f"R^2 = {r2:.3f}")
        else:
            print("R^2 = NaN")
        for x, y in zip(qxs, data["y_pred"]):
            print(f"X = {format_int_safe(x):>8}  =>  Y = {format_int_safe(y):>8}")
    print()

def main_loop():
    print("Экстраполяция Y — ввод 3–20 пар X,Y. (Ctrl+C для выхода.)")
    try:
        while True:
            xs, ys = read_pairs()
            qxs = read_query_xs()
            results = predict_and_r2(xs, ys, qxs)
            print_blocked_results(qxs, results)
            again = input("Новый расчет? (y/n): ").strip().lower()
            if again != 'y':
                print("Выход.")
                break
    except KeyboardInterrupt:
        print("\nПрервано пользователем. Выход.")
        sys.exit(0)

if __name__ == "__main__":
    try:
        import numpy  # noqa: F401
        import scipy  # noqa: F401
    except Exception:
        print("Требуются numpy и scipy. Установите их: pip install numpy scipy")
        sys.exit(1)
    main_loop()