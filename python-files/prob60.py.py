import argparse
import math
import random
from typing import List

def comb(n, k):
    return math.comb(n, k)

def binomial_tail(n: int, p: float, k: int) -> float:
    if not (0 <= p <= 1):
        raise ValueError("Xác suất p phải nằm trong khoảng [0, 1]")
    if k <= 0:
        return 1.0
    return sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(k, n + 1))

def varying_tail(ps: List[float], k: int) -> float:
    n = len(ps)
    dp = [0.0] * (n + 1)
    dp[0] = 1.0
    for p in ps:
        new_dp = [0.0] * (n + 1)
        for j in range(n):
            new_dp[j] += dp[j] * (1 - p)
            new_dp[j + 1] += dp[j] * p
        dp = new_dp
    return sum(dp[k:])

def prob_no_streak(n: int, p: float, r: int) -> float:
    dp = [0.0] * r
    dp[0] = 1.0
    for _ in range(n):
        new_dp = [0.0] * r
        for t in range(r):
            new_dp[0] += dp[t] * (1 - p)
            if t + 1 < r:
                new_dp[t + 1] += dp[t] * p
        dp = new_dp
    return sum(dp)

def streak_prob(n: int, p: float, r: int) -> float:
    return 1.0 - prob_no_streak(n, p, r)

def montecarlo(n: int, p: float, trials: int, event_fn) -> float:
    count = 0
    for _ in range(trials):
        seq = [1 if random.random() < p else 0 for _ in range(n)]
        if event_fn(seq):
            count += 1
    return count / trials

def example_event_at_least_k(k):
    return lambda seq: sum(seq) >= k

def parse_args():
    parser = argparse.ArgumentParser(description="Tính xác suất trong n ngày.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # binomial
    bin_parser = subparsers.add_parser("binomial", help="Xác suất >= k thành công với xác suất cố định mỗi ngày.")
    bin_parser.add_argument("--n", type=int, default=60)
    bin_parser.add_argument("--p", type=float, required=True)
    bin_parser.add_argument("--k", type=int, required=True)

    # varying
    var_parser = subparsers.add_parser("varying", help="Xác suất >= k với danh sách xác suất mỗi ngày.")
    var_parser.add_argument("--ps", type=float, nargs='+', required=True)
    var_parser.add_argument("--k", type=int, help="Số lần thành công tối thiểu")

    # streak
    str_parser = subparsers.add_parser("streak", help="Xác suất có chuỗi liên tiếp >= r.")
    str_parser.add_argument("--n", type=int, default=60)
    str_parser.add_argument("--p", type=float, required=True)
    str_parser.add_argument("--r", type=int, required=True)

    # montecarlo
    mc_parser = subparsers.add_parser("montecarlo", help="Mô phỏng Monte Carlo")
    mc_parser.add_argument("--n", type=int, default=60)
    mc_parser.add_argument("--p", type=float, required=True)
    mc_parser.add_argument("--trials", type=int, default=100000)
    mc_parser.add_argument("--k", type=int, help="Sử dụng event: >= k thành công")

    return parser.parse_args()

def main():
    args = parse_args()

    try:
        if args.command == "binomial":
            prob = binomial_tail(args.n, args.p, args.k)
            print(f"Xác suất >= {args.k} thành công trong {args.n} ngày (p = {args.p}): {prob:.8f}")

        elif args.command == "varying":
            ps = args.ps
            n = len(ps)
            if any(p < 0 or p > 1 for p in ps):
                raise ValueError("Mỗi xác suất trong --ps phải nằm trong [0, 1].")

            if args.k is not None:
                prob = varying_tail(ps, args.k)
                print(f"Xác suất >= {args.k} thành công trong {n} ngày: {prob:.8f}")
            else:
                print(f"Số ngày: {n}. Các xác suất p_i được cung cấp.")
                for k in [0, 1, n // 10, n // 4, n // 2, n]:
                    prob = varying_tail(ps, k)
                    print(f"  Xác suất >= {k} thành công: {prob:.8f}")

        elif args.command == "streak":
            prob = streak_prob(args.n, args.p, args.r)
            print(f"Xác suất có chuỗi liên tiếp >= {args.r} trong {args.n} ngày (p = {args.p}): {prob:.8f}")

        elif args.command == "montecarlo":
            if args.k is None:
                raise ValueError("Tham số --k bắt buộc để xác định event >= k thành công.")
            event_fn = example_event_at_least_k(args.k)
            prob = montecarlo(args.n, args.p, args.trials, event_fn)
            print(f"[Monte Carlo] P(>= {args.k} thành công trong {args.n} ngày): {prob:.6f}")

        else:
            print("Lệnh không hợp lệ. Dùng --help để xem hướng dẫn.")

    except Exception as e:
        print(f"LỖI: {e}")

if __name__ == "__main__":
    main()
