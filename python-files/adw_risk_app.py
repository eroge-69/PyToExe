"""
ADW Risk Assessment Demo Application

This script generates a synthetic accident dataset representing
construction‑site incidents involving accidents during walking (ADW) and
computes hierarchical risk indices based on association rule mining
concepts.  It produces three levels of risk metrics:

* L1 (environment → ADW): a lift value comparing the probability of an ADW
  accident given an environmental condition versus the baseline
  probability of an ADW accident.
* L2 (environment × work → ADW): a lift value comparing the conditional
  probability of an ADW accident given both environment and work type to
  the probability of an ADW accident given only the environment.
* L3 (environment × work × activity → ADW): a lift value comparing the
  conditional probability of an ADW accident given the specific
  environment, work and activity combination to the probability of an
  ADW accident given the corresponding environment and work.

In addition to computing these metrics, the application prints a
hierarchical risk tree with hazard objects and evaluates a sample
project schedule, calculating a time‑window–specific risk index and
listing associated hazard objects.  A risk time series chart is
generated and saved as a PNG file.  The synthetic accident dataset is
also saved as a CSV file for reference.

This script is intended to be bundled as an executable (e.g., with
PyInstaller) for demonstration purposes.  It does not rely on GUI
libraries such as Tkinter; instead it prints results to the console and
stores outputs to files.  Running the script will generate all
necessary data and outputs.
"""

from __future__ import annotations

import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def generate_synthetic_dataset(num_records: int = 200, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic accident dataset.

    Each record represents an accident occurring under a specific
    environmental condition (weather/temperature), work type (공종), activity
    (세부활동), and hazard object.  An ADW label (True/False) indicates
    whether the accident involves walking.  The data is generated with
    mildly skewed probabilities to create meaningful risk patterns.

    Parameters
    ----------
    num_records : int, optional
        Number of synthetic accident records to generate, by default 200.
    seed : int, optional
        Random seed for reproducibility, by default 42.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns: ``env``, ``work``, ``activity``,
        ``hazard``, ``adw`` (bool).  ``env`` encodes the environmental
        condition as a combination of weather and temperature category.
    """
    random.seed(seed)
    np.random.seed(seed)

    # Define categorical values for environment (weather conditions and
    # temperature levels).  To keep things simple we merge weather and
    # temperature into a single environment category.
    weather_conditions = [
        "맑음",  # sunny
        "비",    # rain
        "눈",    # snow
        "흐림",  # cloudy
        "바람",  # windy
    ]
    temperature_levels = [
        "극한추위",  # extreme cold
        "추움",    # cold
        "온화",    # mild
        "더움",    # hot
        "극한더위",  # extreme heat
    ]

    # Define work categories (공종) and their corresponding activities
    # (세부활동).  These pairs are loosely inspired by construction site
    # tasks but kept simple for demonstration.
    work_to_activities: Dict[str, List[str]] = {
        "토공": ["굴착", "흙다짐"],      # earthwork: excavation, soil compaction
        "철근": ["재단", "조립"],        # rebar: cutting, assembly
        "콘크리트": ["타설", "양생"],    # concrete: pouring, curing
        "전기": ["배선", "조명설치"],    # electrical: wiring, lighting install
        "미장": ["바름", "마감"],        # plastering: applying, finishing
    }

    # Possible hazard objects encountered during accidents
    hazard_objects = [
        "낙하물",  # falling object
        "미끄럼",  # slipping
        "넘어짐",  # tripping
        "충돌",    # collision
        "끼임",    # caught/between
        "추락",    # fall
    ]

    # Function to generate an ADW label with biased probabilities
    # depending on the environment and work/activity.  This bias
    # introduces patterns that the risk analysis will later reveal.
    def sample_adw(env: str, work: str, activity: str) -> bool:
        base_prob = 0.2  # baseline probability of an ADW accident
        # Increase risk for rain and snow conditions
        if "비" in env or "눈" in env:
            base_prob += 0.15
        # Increase risk for slippery tasks like concrete pouring and
        # plastering
        if work in {"콘크리트", "미장"}:
            base_prob += 0.1
        # Some activities are particularly risky
        if activity in {"굴착", "타설", "바름"}:
            base_prob += 0.05
        # Ensure probability is between 0 and 0.95
        prob = min(max(base_prob, 0.0), 0.95)
        return random.random() < prob

    records = []
    for _ in range(num_records):
        weather = random.choice(weather_conditions)
        temperature = random.choice(temperature_levels)
        env = f"{weather}/{temperature}"
        work = random.choice(list(work_to_activities.keys()))
        activity = random.choice(work_to_activities[work])
        hazard = random.choice(hazard_objects)
        adw_label = sample_adw(env, work, activity)
        records.append(
            {
                "env": env,
                "work": work,
                "activity": activity,
                "hazard": hazard,
                "adw": adw_label,
            }
        )

    df = pd.DataFrame(records)
    return df


def compute_hierarchical_risks(
    df: pd.DataFrame,
) -> Tuple[
    Dict[str, float],
    Dict[Tuple[str, str], float],
    Dict[Tuple[str, str, str], float],
    Dict[str, Dict[str, Dict[str, List[str]]]],
]:
    """Compute hierarchical lift‑based risk indices and hazard mappings.

    For each level of categorisation (environment, environment × work,
    environment × work × activity) compute a lift value measuring how
    strongly the category combination is associated with ADW accidents
    relative to the appropriate baseline.  Also build a hazard object
    mapping for each combination.

    Parameters
    ----------
    df : pandas.DataFrame
        Accident dataset with columns ``env``, ``work``, ``activity``,
        ``hazard`` and boolean ``adw``.

    Returns
    -------
    tuple
        A tuple containing four elements:

        * ``l1_risk`` – mapping from environment → L1 lift.
        * ``l2_risk`` – mapping from (environment, work) → L2 lift.
        * ``l3_risk`` – mapping from (environment, work, activity) → L3 lift.
        * ``hazard_map`` – nested mapping hazard_map[env][work][activity]
          = list of hazard objects associated with ADW accidents for that
          combination.
    """
    # Overall probability of an ADW accident
    total_records = len(df)
    total_adw = df["adw"].sum()
    p_adw = total_adw / total_records if total_records > 0 else 0.0

    # Containers for counts
    env_counts: Dict[str, int] = defaultdict(int)
    env_adw_counts: Dict[str, int] = defaultdict(int)
    env_work_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    env_work_adw_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    env_work_activity_counts: Dict[Tuple[str, str, str], int] = defaultdict(int)
    env_work_activity_adw_counts: Dict[Tuple[str, str, str], int] = defaultdict(int)
    hazard_map: Dict[str, Dict[str, Dict[str, List[str]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    # Populate counts and hazard mapping
    for _, row in df.iterrows():
        env = row["env"]
        work = row["work"]
        activity = row["activity"]
        hazard = row["hazard"]
        adw_flag = bool(row["adw"])

        env_counts[env] += 1
        env_work_counts[(env, work)] += 1
        env_work_activity_counts[(env, work, activity)] += 1

        if adw_flag:
            env_adw_counts[env] += 1
            env_work_adw_counts[(env, work)] += 1
            env_work_activity_adw_counts[(env, work, activity)] += 1
            # Record hazard objects associated with ADW accidents
            hazard_list = hazard_map[env][work][activity]
            if hazard not in hazard_list:
                hazard_list.append(hazard)

    # Compute L1 lifts: environment → ADW
    l1_risk: Dict[str, float] = {}
    for env, count in env_counts.items():
        p_env = env_adw_counts[env] / count if count > 0 else 0.0
        # Avoid division by zero if no ADW accidents overall
        l1_lift = (p_env / p_adw) if p_adw > 0 else 0.0
        l1_risk[env] = l1_lift

    # Compute L2 lifts: environment × work → ADW
    l2_risk: Dict[Tuple[str, str], float] = {}
    for (env, work), count in env_work_counts.items():
        count_env_work_adw = env_work_adw_counts[(env, work)]
        count_env_work_total = count
        # Probability of ADW given (env, work)
        p_env_work = (
            count_env_work_adw / count_env_work_total
            if count_env_work_total > 0
            else 0.0
        )
        # Probability of ADW given env
        p_env = env_adw_counts[env] / env_counts[env] if env_counts[env] > 0 else 0.0
        l2_lift = (p_env_work / p_env) if p_env > 0 else 0.0
        l2_risk[(env, work)] = l2_lift

    # Compute L3 lifts: environment × work × activity → ADW
    l3_risk: Dict[Tuple[str, str, str], float] = {}
    for (env, work, activity), count in env_work_activity_counts.items():
        count_env_work_activity_adw = env_work_activity_adw_counts[(env, work, activity)]
        p_env_work_activity = (
            count_env_work_activity_adw / count
            if count > 0
            else 0.0
        )
        # Probability of ADW given (env, work)
        count_env_work = env_work_counts[(env, work)]
        p_env_work = (
            env_work_adw_counts[(env, work)] / count_env_work
            if count_env_work > 0
            else 0.0
        )
        l3_lift = (p_env_work_activity / p_env_work) if p_env_work > 0 else 0.0
        l3_risk[(env, work, activity)] = l3_lift

    return l1_risk, l2_risk, l3_risk, hazard_map


def print_risk_tree(
    l1_risk: Dict[str, float],
    l2_risk: Dict[Tuple[str, str], float],
    l3_risk: Dict[Tuple[str, str, str], float],
    hazard_map: Dict[str, Dict[str, Dict[str, List[str]]]],
    max_envs: int | None = None,
    max_works: int | None = None,
    max_activities: int | None = None,
) -> None:
    """Print a hierarchical risk tree with hazard objects.

    The tree lists each environment along with its L1 lift, followed by
    work types and their L2 lifts, and finally activities and their
    corresponding L3 lifts.  Hazard objects associated with ADW
    accidents for each (env, work, activity) combination are also
    displayed.

    Parameters
    ----------
    l1_risk : dict
        Mapping from environment → L1 lift.
    l2_risk : dict
        Mapping from (environment, work) → L2 lift.
    l3_risk : dict
        Mapping from (environment, work, activity) → L3 lift.
    hazard_map : dict
        Nested mapping from environment → work → activity → list of
        hazard objects.
    max_envs : int or None
        Maximum number of environments to print (useful for large
        datasets), or ``None`` to print all.
    max_works : int or None
        Maximum number of work types per environment to print, or
        ``None`` for all.
    max_activities : int or None
        Maximum number of activities per work to print, or ``None`` for
        all.
    """
    # Sort environments by descending risk
    sorted_envs = sorted(l1_risk.items(), key=lambda x: x[1], reverse=True)
    for env_idx, (env, l1) in enumerate(sorted_envs):
        if max_envs is not None and env_idx >= max_envs:
            break
        print(f"환경 {env}: L1 위험지수(향상도) = {l1:.3f}")
        # Get work types associated with this environment
        works = {work for (e, work) in l2_risk if e == env}
        # Sort work types by descending L2 risk
        sorted_works = sorted(
            works,
            key=lambda w: l2_risk.get((env, w), 0.0),
            reverse=True,
        )
        for work_idx, work in enumerate(sorted_works):
            if max_works is not None and work_idx >= max_works:
                break
            l2 = l2_risk.get((env, work), 0.0)
            print(f"  ├─ 공종 {work}: L2 위험지수(향상도) = {l2:.3f}")
            activities = {
                act
                for (e, w, act) in l3_risk.keys()
                if e == env and w == work
            }
            # Sort activities by descending L3 risk
            sorted_acts = sorted(
                activities,
                key=lambda a: l3_risk.get((env, work, a), 0.0),
                reverse=True,
            )
            for act_idx, act in enumerate(sorted_acts):
                if max_activities is not None and act_idx >= max_activities:
                    break
                l3 = l3_risk.get((env, work, act), 0.0)
                hazard_list = hazard_map.get(env, {}).get(work, {}).get(act, [])
                hazards_str = ", ".join(hazard_list) if hazard_list else "(없음)"
                print(
                    f"    └─ 활동 {act}: L3 위험지수(향상도) = {l3:.3f} | 유해 객체: {hazards_str}"
                )


def generate_demo_schedule(
    start_date: datetime,
    num_days: int,
    env_options: Iterable[str],
    work_to_activities: Dict[str, List[str]],
    seed: int = 0,
) -> pd.DataFrame:
    """Generate a demonstration construction schedule.

    Each day in the schedule contains multiple tasks defined by a work
    type and activity with an associated number of workers.  The
    environment for each day is sampled from ``env_options``.

    Parameters
    ----------
    start_date : datetime
        Starting date of the schedule.
    num_days : int
        Number of days to generate.
    env_options : iterable of str
        Possible environmental conditions (must match keys in L1 risk
        mapping).
    work_to_activities : dict
        Mapping from work types to available activities.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns ``date``, ``env``, ``work``, ``activity``,
        and ``workers``.  Each row represents a task scheduled for a
        specific day under a given environment.
    """
    random.seed(seed)
    records = []
    current_date = start_date
    env_list = list(env_options)
    for _ in range(num_days):
        env = random.choice(env_list)
        # Generate between 2 and 4 tasks per day
        num_tasks = random.randint(2, 4)
        works = random.sample(list(work_to_activities.keys()), k=num_tasks)
        for work in works:
            activity = random.choice(work_to_activities[work])
            workers = random.randint(1, 10)
            records.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "env": env,
                    "work": work,
                    "activity": activity,
                    "workers": workers,
                }
            )
        current_date += timedelta(days=1)
    schedule_df = pd.DataFrame(records)
    return schedule_df


def evaluate_schedule_risk(
    schedule_df: pd.DataFrame,
    l1_risk: Dict[str, float],
    l2_risk: Dict[Tuple[str, str], float],
    l3_risk: Dict[Tuple[str, str, str], float],
    hazard_map: Dict[str, Dict[str, Dict[str, List[str]]]],
    default_risk: float | None = None,
) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
    """Evaluate time‑window risk for a given schedule.

    For each date in the schedule, compute a weighted average risk
    (weighted by the number of workers) using the available hierarchical
    risk indices.  If a specific combination (env, work, activity) has
    an L3 risk value it is used; otherwise L2 (env, work) or L1 (env)
    values are used as fallback.  The function also collects hazard
    objects associated with scheduled tasks.

    Parameters
    ----------
    schedule_df : pandas.DataFrame
        Schedule with columns ``date``, ``env``, ``work``, ``activity``,
        and ``workers``.
    l1_risk, l2_risk, l3_risk : dict
        Hierarchical risk mappings as returned from
        ``compute_hierarchical_risks``.
    hazard_map : dict
        Hazard object mapping from environment → work → activity → list
        of hazards.
    default_risk : float or None, optional
        Risk value to use if no hierarchical value exists for a given
        combination.  If ``None`` (default), tasks without risk data
        contribute zero risk.

    Returns
    -------
    tuple
        A pair of dictionaries:

        * ``risk_by_date`` – mapping from date string → average risk for
          that day.
        * ``hazards_by_date`` – mapping from date string → list of
          hazard objects associated with tasks on that day.
    """
    risk_by_date: Dict[str, float] = {}
    hazards_by_date: Dict[str, List[str]] = {}

    grouped = schedule_df.groupby("date")
    for date, group in grouped:
        weighted_sum = 0.0
        total_workers = 0
        hazard_set = set()
        for _, row in group.iterrows():
            env = row["env"]
            work = row["work"]
            activity = row["activity"]
            workers = row["workers"]
            # Determine the most specific risk value available
            risk = None
            if (env, work, activity) in l3_risk:
                risk = l3_risk[(env, work, activity)]
            elif (env, work) in l2_risk:
                risk = l2_risk[(env, work)]
            elif env in l1_risk:
                risk = l1_risk[env]
            else:
                risk = default_risk
            if risk is None:
                risk = 0.0
            weighted_sum += risk * workers
            total_workers += workers
            # Collect hazard objects for this task
            hazards = hazard_map.get(env, {}).get(work, {}).get(activity, [])
            for h in hazards:
                hazard_set.add(h)
        avg_risk = (weighted_sum / total_workers) if total_workers > 0 else 0.0
        risk_by_date[date] = avg_risk
        hazards_by_date[date] = sorted(hazard_set)
    return risk_by_date, hazards_by_date


def plot_risk_time_series(
    risk_by_date: Dict[str, float],
    output_path: str = "risk_time_series.png",
) -> None:
    """Plot a time series of risk values and save it as a PNG.

    Parameters
    ----------
    risk_by_date : dict
        Mapping from date string → risk value.  Dates should be in
        chronological order or convertible to datetime.
    output_path : str, optional
        Path to save the resulting PNG image, by default
        ``"risk_time_series.png"``.
    """
    # Sort by date to ensure chronological order
    dates = sorted(risk_by_date.keys())
    risks = [risk_by_date[date] for date in dates]
    # Convert date strings to datetime objects for plotting
    date_objs = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
    plt.figure(figsize=(8, 4))
    plt.plot(date_objs, risks, marker="o")
    plt.title("Time Window별 보행 중 사고 위험지수")
    plt.xlabel("날짜 (Date)")
    plt.ylabel("평균 위험지수 (Lift)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    """Entry point for the demo application.

    Generates synthetic data, computes hierarchical risk indices, prints
    a risk tree, evaluates a demonstration schedule and produces a
    time‑series risk plot.  All data and outputs are saved into the
    current working directory.
    """
    # Generate synthetic accident dataset
    df = generate_synthetic_dataset(num_records=200, seed=42)
    # Save dataset for inspection
    dataset_path = "accident_data.csv"
    df.to_csv(dataset_path, index=False)

    # Compute hierarchical risks and hazard mapping
    l1_risk, l2_risk, l3_risk, hazard_map = compute_hierarchical_risks(df)

    # Print risk tree to the console
    print("=" * 80)
    print("보행 중 사고 위험 계층 트리 (예시 데이터 기반)")
    print("=" * 80)
    print_risk_tree(l1_risk, l2_risk, l3_risk, hazard_map)
    print()

    # Build demonstration schedule
    unique_envs = set(df["env"])
    work_to_activities = {
        work: sorted(df[df["work"] == work]["activity"].unique().tolist())
        for work in df["work"].unique()
    }
    start_date = datetime.now().date()
    schedule_df = generate_demo_schedule(
        start_date=datetime(start_date.year, start_date.month, start_date.day),
        num_days=10,
        env_options=unique_envs,
        work_to_activities=work_to_activities,
        seed=1,
    )
    schedule_path = "demo_schedule.csv"
    schedule_df.to_csv(schedule_path, index=False)

    # Evaluate schedule risk
    risk_by_date, hazards_by_date = evaluate_schedule_risk(
        schedule_df, l1_risk, l2_risk, l3_risk, hazard_map, default_risk=0.0
    )

    # Print schedule risk summary
    print("=" * 80)
    print("데모 스케줄 위험 분석 결과")
    print("=" * 80)
    for date in sorted(risk_by_date.keys()):
        risk_value = risk_by_date[date]
        hazard_list = hazards_by_date.get(date, [])
        hazards_str = ", ".join(hazard_list) if hazard_list else "(해당 없음)"
        print(
            f"{date}: 평균 위험지수 = {risk_value:.3f} | 연관 유해 객체: {hazards_str}"
        )
    print()

    # Plot risk time series
    chart_path = "risk_time_series.png"
    plot_risk_time_series(risk_by_date, output_path=chart_path)
    print(f"시간별 위험지수 그래프가 '{chart_path}' 파일로 저장되었습니다.")
    print(f"사고 사례 데이터는 '{dataset_path}' 파일로 저장되었습니다.")
    print(f"데모 스케줄은 '{schedule_path}' 파일로 저장되었습니다.")


if __name__ == "__main__":
    main()