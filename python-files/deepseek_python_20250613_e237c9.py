def adjust_investment(weekly_data):
  if penetration_gap > 5%: 
    MI *= 1.25  # Aggressive mode
  elif market_volatility > 30%: 
    MI *= 0.85  # Risk reduction
  if no_alc_demand_spike:  # Non-alc trend trigger
    MI *= (1 + 0.26 * no_alc_growth) # :cite[2]:cite[4]