
"""
value_betting.py

Modello Poisson con decadimento esponenziale per stimare probabilità 1X2
e cercare potenziali "value bet" (EV > 0) date le quote decimali.

USO DA TERMINALE:
    python value_betting.py --storico storico_partite.csv --prossime prossime_quote.csv --out output.csv

Formato CSV richiesti:
  storico_partite.csv
    date,home_team,away_team,home_goals,away_goals
    2025-01-10,Team A,Team B,2,1
    ...

  prossime_quote.csv
    date,home_team,away_team,home_win_odds,draw_odds,away_win_odds
    2025-08-20,Team A,Team B,1.95,3.40,4.20
    ...

Nota importante:
- Nessun modello può garantire profitti. Le quote includono il margine del bookmaker.
- Gioca responsabilmente. 18+
"""
import argparse
import math
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd
from datetime import datetime

@dataclass
class TeamStrength:
    home_attack: float = 1.0
    away_attack: float = 1.0
    home_defense: float = 1.0
    away_defense: float = 1.0

def _parse_date(s):
    return pd.to_datetime(s).tz_localize(None)

def _exp_weight(dates: pd.Series, half_life_days: float) -> np.ndarray:
    """Ritorna pesi di decadimento esponenziale (0.5^(delta/half_life))."""
    now = dates.max() if len(dates) else pd.Timestamp(datetime.utcnow())
    delta_days = (now - dates).dt.days.clip(lower=0)
    return np.power(0.5, delta_days / half_life_days)

def _safe_div(a: float, b: float, default: float = 0.0) -> float:
    return a / b if b != 0 else default

def _poisson_pmf(k: np.ndarray, lam: float) -> np.ndarray:
    # Usa log per stabilità numerica per k fino a ~20
    k = np.asarray(k, dtype=int)
    pmf = np.exp(k * np.log(lam) - lam - np.array([math.lgamma(x + 1) for x in k]))
    return pmf

def outcome_probabilities(lambda_home: float, lambda_away: float, max_goals: int = 10) -> Tuple[float, float, float]:
    """Probabilità 1 (casa), X (pareggio), 2 (trasferta)"""
    goals = np.arange(0, max_goals + 1)
    p_home = _poisson_pmf(goals, lambda_home)
    p_away = _poisson_pmf(goals, lambda_away)
    matrix = np.outer(p_home, p_away)  # P(i,j)
    p_home_win = np.triu(matrix, k=1).sum()
    p_draw = np.trace(matrix)
    p_away_win = np.tril(matrix, k=-1).sum()
    # Normalizza (taglio ai goal massimi introduce piccolissimo errore)
    total = p_home_win + p_draw + p_away_win
    if total > 0:
        p_home_win /= total
        p_draw /= total
        p_away_win /= total
    return float(p_home_win), float(p_draw), float(p_away_win)

def kelly_fraction(p: float, odds: float) -> float:
    """Kelly ottimale (p*odds - 1)/(odds - 1), troncato [0,1]."""
    if odds <= 1.0:
        return 0.0
    f = (p * odds - 1.0) / (odds - 1.0)
    return float(max(0.0, min(1.0, f)))

def compute_strengths(df_hist: pd.DataFrame, half_life_days: float = 180.0, prior_matches: float = 5.0) -> Tuple[Dict[str, TeamStrength], float, float]:
    df = df_hist.copy()
    df['date'] = df['date'].apply(_parse_date)
    # Pesi
    w = _exp_weight(df['date'], half_life_days)
    df['w'] = w

    # Medie globali (ponderate)
    w_sum = df['w'].sum()
    mu_home = (df['w'] * df['home_goals']).sum() / w_sum
    mu_away = (df['w'] * df['away_goals']).sum() / w_sum

    # Aggregazioni per team (home)
    home_scored = df.groupby('home_team').apply(lambda g: (g['w'] * g['home_goals']).sum())
    home_conceded = df.groupby('home_team').apply(lambda g: (g['w'] * g['away_goals']).sum())
    home_matches = df.groupby('home_team')['w'].sum()
    # (away)
    away_scored = df.groupby('away_team').apply(lambda g: (g['w'] * g['away_goals']).sum())
    away_conceded = df.groupby('away_team').apply(lambda g: (g['w'] * g['home_goals']).sum())
    away_matches = df.groupby('away_team')['w'].sum()

    teams = set(home_matches.index).union(set(away_matches.index))
    strengths: Dict[str, TeamStrength] = {}
    for t in teams:
        hm = home_matches.get(t, 0.0)
        am = away_matches.get(t, 0.0)
        hgs = home_scored.get(t, 0.0)
        hgc = home_conceded.get(t, 0.0)
        ags = away_scored.get(t, 0.0)
        agc = away_conceded.get(t, 0.0)
        # Regolarizzazione (prior su "media di campionato")
        home_attack = ((hgs + prior_matches * mu_home) / (hm + prior_matches)) / mu_home if (hm + prior_matches) > 0 else 1.0
        away_attack = ((ags + prior_matches * mu_away) / (am + prior_matches)) / mu_away if (am + prior_matches) > 0 else 1.0
        home_defense = ((hgc + prior_matches * mu_away) / (hm + prior_matches)) / mu_away if (hm + prior_matches) > 0 else 1.0
        away_defense = ((agc + prior_matches * mu_home) / (am + prior_matches)) / mu_home if (am + prior_matches) > 0 else 1.0
        strengths[t] = TeamStrength(
            home_attack=float(home_attack),
            away_attack=float(away_attack),
            home_defense=float(home_defense),
            away_defense=float(away_defense),
        )
    return strengths, float(mu_home), float(mu_away)

def expected_goals(home_team: str, away_team: str, strengths: Dict[str, TeamStrength], mu_home: float, mu_away: float) -> Tuple[float, float]:
    th = strengths.get(home_team, TeamStrength())
    ta = strengths.get(away_team, TeamStrength())
    lam_home = mu_home * th.home_attack * ta.away_defense
    lam_away = mu_away * ta.away_attack * th.home_defense
    # Evita valori estremi
    lam_home = max(0.05, min(5.0, lam_home))
    lam_away = max(0.05, min(5.0, lam_away))
    return float(lam_home), float(lam_away)

def evaluate_bets(df_hist: pd.DataFrame,
                  df_upc: pd.DataFrame,
                  half_life_days: float = 180.0,
                  max_goals: int = 10,
                  kelly_divisor: float = 2.0) -> pd.DataFrame:
    strengths, mu_h, mu_a = compute_strengths(df_hist, half_life_days=half_life_days)
    rows = []
    for _, r in df_upc.iterrows():
        home = r['home_team']
        away = r['away_team']
        lam_h, lam_a = expected_goals(home, away, strengths, mu_h, mu_a)
        p1, px, p2 = outcome_probabilities(lam_h, lam_a, max_goals=max_goals)
        # Quote
        o1 = float(r['home_win_odds'])
        ox = float(r['draw_odds'])
        o2 = float(r['away_win_odds'])
        # EV per unità
        ev1 = p1 * o1 - 1.0
        evx = px * ox - 1.0
        ev2 = p2 * o2 - 1.0
        # Kelly frazionato
        k1 = kelly_fraction(p1, o1) / kelly_divisor
        kx = kelly_fraction(px, ox) / kelly_divisor
        k2 = kelly_fraction(p2, o2) / kelly_divisor
        date = pd.to_datetime(r['date']).date() if not pd.isna(r['date']) else None
        for sel, p, o, ev, k in [('1', p1, o1, ev1, k1), ('X', px, ox, evx, kx), ('2', p2, o2, ev2, k2)]:
            rows.append({
                'date': date,
                'home_team': home,
                'away_team': away,
                'selection': sel,
                'model_prob': p,
                'fair_odds': (1.0 / p) if p > 0 else np.nan,
                'market_odds': o,
                'edge_ev': ev,
                'kelly_fraction': k,
                'lambda_home': lam_h,
                'lambda_away': lam_a,
                'home_win_prob': p1,
                'draw_prob': px,
                'away_win_prob': p2,
            })
    out = pd.DataFrame(rows)
    out.sort_values(['edge_ev', 'model_prob'], ascending=[False, False], inplace=True)
    return out.reset_index(drop=True)

def run_model_on_files(hist_path: str, upc_path: str, out_path: Optional[str] = None,
                       half_life_days: float = 180.0, max_goals: int = 10, kelly_divisor: float = 2.0) -> pd.DataFrame:
    df_hist = pd.read_csv(hist_path)
    df_upc = pd.read_csv(upc_path)
    res = evaluate_bets(df_hist, df_upc, half_life_days=half_life_days, max_goals=max_goals, kelly_divisor=kelly_divisor)
    if out_path:
        res.to_csv(out_path, index=False)
    return res

def main():
    ap = argparse.ArgumentParser(description="Value betting 1X2 con modello Poisson (decadimento esponenziale)")
    ap.add_argument("--storico", required=True, help="CSV storico partite")
    ap.add_argument("--prossime", required=True, help="CSV prossime partite con quote")
    ap.add_argument("--out", default=None, help="CSV di output (opzionale)")
    ap.add_argument("--half_life", type=float, default=180.0, help="Emivita pesi (giorni), default 180")
    ap.add_argument("--max_goals", type=int, default=10, help="Taglio massimo goal Poisson, default 10")
    ap.add_argument("--kelly_divisor", type=float, default=2.0, help="Kelly frazionato: divide la frazione Kelly (default 2 = mezzo Kelly)")
    args = ap.parse_args()
    df = run_model_on_files(args.storico, args.prossime, out_path=args.out, half_life_days=args.half_life, max_goals=args.max_goals, kelly_divisor=args.kelly_divisor)
    # Stampa riepilogo top 15
    cols = ["date","home_team","away_team","selection","model_prob","market_odds","fair_odds","edge_ev","kelly_fraction"]
    print(df[cols].head(15).to_string(index=False))

if __name__ == "__main__":
    main()
