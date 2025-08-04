for i in range(n_sims):
    rev_growth = draw(lognormal_mu, lognormal_sigma)
    margin     = draw(beta_alpha, beta_beta)
    capex_pct  = draw(tri_low, tri_mode, tri_high)
    wacc       = draw(pert_low, pert_mode, pert_high)
    g          = draw(tri_g_low, tri_g_high, tri_g_high)
    exit_mult  = draw(lognorm_mu_mult, lognorm_sigma_mult)

    for t in range(1, T+1):
        revenue[t] = revenue[t-1]*(1+rev_growth)
        ebitda[t]  = revenue[t]*margin
        # build the rest of FCF …

    if perpetuity_flag:
        TV = FCF[T]*(1+g)/(wacc-g)
    else:
        TV = ebitda[T]*exit_mult

    EV[i] = np.npv(wacc, FCF[1:T]) + TV/(1+wacc)**T
