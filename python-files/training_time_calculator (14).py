import math

# Helper function to parse numbers like 1.138m, 1,138,000, 2B, 1Qa, 1Qi etc.
def parse_number(s):
    try:
        s = s.replace(",", "").strip().lower()
        if 'k' in s:
            return float(s.replace('k','')) * 1_000
        elif 'm' in s:
            return float(s.replace('m','')) * 1_000_000
        elif 'b' in s:
            return float(s.replace('b','')) * 1_000_000_000
        elif 't' in s:
            return float(s.replace('t','')) * 1_000_000_000_000
        elif 'q' in s:
            if 'qi' in s:  # quintillion
                return float(s.replace('qi','')) * 1_000_000_000_000_000_000
            else:  # quadrillion
                return float(s.replace('q','')) * 1_000_000_000_000_000
        else:
            return float(s)
    except:
        return None

# Format seconds to human-readable string
def format_time(seconds):
    seconds = int(seconds)
    if seconds < 1:
        return '0s'
    parts = []
    days = seconds // 86400
    if days > 0: parts.append(f"{days}d")
    seconds %= 86400
    hours = seconds // 3600
    if hours > 0: parts.append(f"{hours}h")
    seconds %= 3600
    minutes = seconds // 60
    if minutes > 0: parts.append(f"{minutes}m")
    seconds %= 60
    if seconds > 0: parts.append(f"{seconds}s")
    return ' '.join(parts)

# Zone data for each stat
zones = {
    'bt': [
        ('Ice Bathtub', 100, 5, 1.25),
        ('Fire Pit', 10_000, 10, 1.25),
        ('Iceberg', 100_000, 20, 1.25),
        ('Tornado', 1_000_000, 50, 1.25),
        ('Volcano', 10_000_000, 100, 1.25),
        ('Hellfire Pit', 1_000_000_000, 2000, 1.25),
        ('Green Acid Pool', 100_000_000_000, 40000, 1.25),
        ('Red Acid Pool', 10_000_000_000_000, 800000, 1.25)
    ],
    'fs': [
        ('Rock', 100, 10, 1),
        ('Crystal', 100_000, 100, 1),
        ('Blue God Star', 1_000_000_000, 2000, 1),
        ('Green God Star', 100_000_000_000, 40000, 1),
        ('Red God Star', 10_000_000_000_000, 800000, 1)
    ],
    'pp': [
        ('First Lawn', 1_000_000, 100, 1.5),
        ('Second Lawn', 1_000_000_000, 10000, 1.5),
        ('Bridge', 1_000_000_000_000, 1_000_000, 1.5),
        ('Waterfall', 1_000_000_000_000_000, 100_000_000, 1.5)
    ]
}

# Multiplier costs and tokens per minute
token_costs = {
    2: 100, 4: 200, 8: 500, 16: 1000, 32: 2000, 64: 5000, 128: 10000, 256: 15000,
    512: 20000, 1024: 50000, 2048: 100000, 4096: 200000, 8192: 500000, 16384: 1000000,
    32768: 2000000, 65536: 5000000, 131072: 10000000
}

tokens_per_minute = 5

# Safe input function
def get_input(prompt, choices=None, allow_empty=False):
    while True:
        try:
            val = input(prompt).strip()
            if allow_empty and val == '':
                return None
            if choices and val not in choices:
                print(f"Invalid choice. Must be one of: {', '.join(choices)}")
                continue
            return val
        except Exception as e:
            print(f"Input error: {e}")

try:
    # Choose stat type
    print("Select your stat:")
    print("1. FS")
    print("2. BT")
    print("3. PP")
    stat_choice = get_input("Enter number: ", choices=['1','2','3'])

    stat = {'1':'fs','2':'bt','3':'pp'}[stat_choice]

    # List zones for selected stat
    print(f"\nSelect {stat.upper()} zone (for multiplier reference):")
    for i, (name, req, mult, tick) in enumerate(zones[stat], 1):
        print(f"{i}. {name}")

    while True:
        try:
            zone_choice = int(get_input("Enter number: ")) - 1
            if 0 <= zone_choice < len(zones[stat]):
                break
            else:
                print("Choice out of range.")
        except:
            print("Enter a valid number.")

    zone_name, zone_req, zone_mult, tick_len = zones[stat][zone_choice]

    # Current and target stat
    while True:
        current_stat_input = get_input(f"Enter your current {stat.upper()} stat: ")
        current_stat = parse_number(current_stat_input)
        if current_stat is not None:
            break
        print("Enter a valid number.")

    while True:
        target_stat_input = get_input(f"Enter your target {stat.upper()} stat: ")
        target_stat = parse_number(target_stat_input)
        if target_stat is not None and target_stat > current_stat:
            break
        print("Target must be a valid number higher than current stat.")

    # Multiplier input
    while True:
        personal_mult_input = get_input("Enter your current personal multiplier (1 to 131072): ")
        personal_mult = parse_number(personal_mult_input.replace('x','').replace(' ','').lower())
        if personal_mult is not None and 1 <= personal_mult <= 131072:
            break
        print("Multiplier must be between 1 and 131072.")

    flying_bonus = 1
    if stat == 'pp':
        fly = get_input("Are you flying? (y/n): ", choices=['y','n'])
        if fly == 'y':
            flying_bonus = 10

    # Base calculation
    total_gain_per_tick = zone_mult * personal_mult * flying_bonus
    stat_time = 0
    current_amount = current_stat

    while current_amount < target_stat:
        current_amount += total_gain_per_tick
        stat_time += tick_len

    print(f"\n--- {zone_name} ({stat.upper()}) ---")
    print(f"Time to reach target stat ({target_stat_input}) from current stat ({current_stat_input}) at current multiplier: {format_time(stat_time)}")

    # Optimal multiplier simulation
    do_upgrade = get_input("Do you want to simulate optimal multiplier upgrades? (y/n): ", choices=['y','n'])
    if do_upgrade == 'y':
        while True:
            current_tokens_input = get_input("Enter how many tokens you currently have: ")
            tokens = parse_number(current_tokens_input)
            if tokens is not None:
                break
            print("Enter a valid number.")

        while True:
            max_mult_input = get_input("Enter the maximum multiplier you want to simulate (e.g., 131072): ")
            max_mult = parse_number(max_mult_input)
            if max_mult is not None and max_mult >= personal_mult:
                break
            print("Enter a valid maximum multiplier greater than or equal to your current multiplier.")

        current_amount = current_stat
        mult = personal_mult
        total_time_opt = 0
        upgrade_history = []

        available_mults = sorted([m for m in token_costs.keys() if m > mult and m <= max_mult])

        tick_seconds = tick_len
        while current_amount < target_stat:
            gain_per_tick = zone_mult * mult * flying_bonus
            current_amount += gain_per_tick
            total_time_opt += tick_seconds

            tokens += (tick_seconds / 60) * tokens_per_minute

            if available_mults:
                next_mult = available_mults[0]
                cost = token_costs[next_mult]
                if tokens >= cost:
                    tokens -= cost
                    mult = next_mult
                    upgrade_history.append((format_time(total_time_opt), mult))
                    available_mults.pop(0)

        print(f"\n--- Optimal Multiplier Simulation ---")
        print(f"Time to reach target stat ({target_stat_input}) with optimal upgrades: {format_time(total_time_opt)}")
        print(f"Multiplier upgrades occurred at times: {upgrade_history}")

        if available_mults:
            next_mult = available_mults[0]
            remaining_tokens = max(0, token_costs[next_mult] - tokens)
            if remaining_tokens > 0:
                time_to_next_mult = (remaining_tokens / tokens_per_minute) * 60
                print(f"Time needed to reach next multiplier ({next_mult}x): {format_time(time_to_next_mult)}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

input("\nPress Enter to exit...")