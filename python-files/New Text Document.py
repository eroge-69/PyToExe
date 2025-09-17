#!/usr/bin/env python3
"""
sales_analysis.py

Single-file data analysis for historical sales CSVs.
Saves a minimal HTML report with inline charts detecting likely reasons
for sales decline: seasonality, price, units, product mix, region/channel, promotions, returns.

Usage:
    python sales_analysis.py sales.csv
"""
import sys
import os
import argparse
import math
import io
import base64
from datetime import datetime
from textwrap import dedent

# Try imports (clear message if missing)
missing = []
try:
    import pandas as pd
except Exception:
    missing.append("pandas")
try:
    import numpy as np
except Exception:
    missing.append("numpy")
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    missing.append("matplotlib")

try:
    from scipy import stats
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

if missing:
    print("Missing packages:", ", ".join(missing))
    print("Install them with: pip install " + " ".join(missing))
    sys.exit(1)

# ---------- Helpers ----------
def save_fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, bbox_inches="tight", dpi=120)
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    return "data:image/png;base64," + b64

def guess_col(cols, candidates):
    cols_low = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_low:
            return cols_low[cand.lower()]
    # partial match
    for cand in candidates:
        for c in cols:
            if cand.lower() in c.lower():
                return c
    return None

def parse_date_column(df):
    # return name of date column or None
    for c in df.columns:
        if np.issubdtype(df[c].dtype, np.datetime64):
            return c
    for c in df.columns:
        if "date" in c.lower():
            try:
                df[c] = pd.to_datetime(df[c], errors='coerce')
                if df[c].notna().sum() > 0:
                    return c
            except Exception:
                continue
    # try to infer from first column if parseable
    first = df.columns[0]
    try:
        df[first] = pd.to_datetime(df[first], errors='coerce')
        if df[first].notna().sum() > 0:
            return first
    except Exception:
        pass
    return None

def welsch_ttest(a, b):
    # return t, df (no p-value unless scipy)
    n1, n2 = len(a), len(b)
    m1, m2 = np.nanmean(a), np.nanmean(b)
    s1, s2 = np.nanvar(a, ddof=1), np.nanvar(b, ddof=1)
    denom = math.sqrt(s1/n1 + s2/n2) if n1>0 and n2>0 else float('inf')
    t = (m1 - m2) / denom if denom>0 else float('nan')
    # Welch-Satterthwaite df
    num = (s1/n1 + s2/n2)**2
    den = 0
    if n1>1:
        den += (s1/n1)**2 / (n1-1)
    if n2>1:
        den += (s2/n2)**2 / (n2-1)
    df = num / den if den>0 else float('nan')
    return t, df

# ---------- Main analysis ----------
def run_analysis(path, out_path="report.html", recent_period_months=3, top_n_products=10):
    df = pd.read_csv(path)
    orig_cols = list(df.columns)
    date_col = parse_date_column(df)
    if date_col is None:
        print("Could not find or parse a date column. Ensure CSV has a date column.")
        sys.exit(1)
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df[df[date_col].notna()].copy()
    cols = df.columns

    # guess common columns
    sales_col = guess_col(cols, ["sales", "revenue", "amount", "total"])
    units_col = guess_col(cols, ["units", "quantity", "qty", "count", "orders"])
    price_col = guess_col(cols, ["price", "unit_price", "avg_price"])
    product_col = guess_col(cols, ["product", "sku", "item", "product_id"])
    region_col = guess_col(cols, ["region", "state", "country", "market"])
    channel_col = guess_col(cols, ["channel", "sales_channel", "platform"])
    promo_col = guess_col(cols, ["promo", "promotion", "is_promo", "discount"])
    returns_col = guess_col(cols, ["return", "returns", "refund"])

    # If sales not present but we have units and price, compute sales
    if sales_col is None and units_col is not None and price_col is not None:
        df["_sales_calc"] = pd.to_numeric(df[units_col], errors='coerce') * pd.to_numeric(df[price_col], errors='coerce')
        sales_col = "_sales_calc"

    if sales_col is None:
        print("Couldn't find a sales/revenue column and couldn't compute sales from units*price.")
        print("Available columns:", orig_cols)
        sys.exit(1)

    df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)
    if units_col:
        df[units_col] = pd.to_numeric(df[units_col], errors='coerce').fillna(0)
    if price_col:
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(np.nan)

    # derive period columns
    df['date'] = df[date_col].dt.date
    df['month'] = df[date_col].dt.to_period('M').dt.to_timestamp()
    df['week'] = df[date_col].dt.to_period('W').dt.start_time

    # daily and monthly aggregates
    daily = df.groupby('date').agg(sales=(sales_col, 'sum'),
                                   units=(units_col, 'sum') if units_col else (sales_col, lambda s: np.nan))
    daily['date'] = pd.to_datetime(daily.index)
    daily = daily.sort_values('date')

    monthly = df.groupby('month').agg(sales=(sales_col, 'sum'),
                                      units=(units_col, 'sum') if units_col else (sales_col, lambda s: np.nan))
    monthly = monthly.sort_index()

    # growth metrics
    def pct(a, b):
        try:
            return (a - b) / b * 100.0 if b != 0 else np.nan
        except Exception:
            return np.nan

    if len(monthly) < 2:
        print("Not enough monthly data for meaningful analysis.")
        sys.exit(1)

    # detect recent and previous periods (last N months vs previous N)
    recent_end = monthly.index.max()
    recent_start = (recent_end - pd.DateOffset(months=recent_period_months-1)).replace(day=1)
    # select recent months
    recent_mask = (monthly.index >= recent_start) & (monthly.index <= recent_end)
    recent_total = monthly.loc[recent_mask, 'sales'].sum()
    prev_start = (recent_start - pd.DateOffset(months=recent_period_months)).replace(day=1)
    prev_end = (recent_start - pd.DateOffset(days=1)).replace(day=1) + pd.DateOffset(days=monthly.index.day.max()-1)
    # simpler prev mask:
    prev_mask = (monthly.index >= prev_start) & (monthly.index < recent_start)
    prev_total = monthly.loc[prev_mask, 'sales'].sum()

    pct_change_recent_vs_prev = pct(recent_total, prev_total)

    # moving average / seasonality
    monthly['ma3'] = monthly['sales'].rolling(3, center=False, min_periods=1).mean()
    monthly['zscore'] = (monthly['sales'] - monthly['sales'].rolling(12, min_periods=3).mean()) / monthly['sales'].rolling(12, min_periods=3).std()
    # find largest drop month
    monthly['pct_change'] = monthly['sales'].pct_change() * 100
    largest_drop = monthly['pct_change'].idxmin()
    largest_drop_val = monthly['pct_change'].min()

    # top products change (if product_col present)
    product_insights = ""
    product_table = None
    if product_col:
        prod = df.groupby(product_col).agg(sales=(sales_col, 'sum'),
                                           units=(units_col, 'sum') if units_col else (sales_col, lambda s: np.nan))
        prod = prod.sort_values('sales', ascending=False)
        total_sales = prod['sales'].sum()
        prod['share_pct'] = prod['sales'] / total_sales * 100
        top_now = prod.head(top_n_products)
        # compute contribution change between periods
        recent_mask_rows = (df[date_col] >= recent_start) & (df[date_col] <= recent_end + pd.offsets.MonthEnd(0))
        prev_mask_rows = (df[date_col] >= prev_start) & (df[date_col] < recent_start)
        recent_by_prod = df[recent_mask_rows].groupby(product_col)[sales_col].sum()
        prev_by_prod = df[prev_mask_rows].groupby(product_col)[sales_col].sum()
        prod_change = pd.DataFrame({
            'recent_sales': recent_by_prod,
            'prev_sales': prev_by_prod
        }).fillna(0)
        prod_change['diff'] = prod_change['recent_sales'] - prod_change['prev_sales']
        prod_change['pct_diff'] = prod_change.apply(lambda r: pct(r['recent_sales'], r['prev_sales']), axis=1)
        prod_change = prod_change.sort_values('diff')
        # top losers among top products
        top_losers = prod_change.loc[prod.index].dropna().sort_values('pct_diff').head(10)
        product_table = {
            'top_products': top_now.reset_index().head(20).to_dict(orient='records'),
            'top_losers': top_losers.reset_index().to_dict(orient='records')
        }
        product_insights = dedent(f"""\
            Top {top_n_products} products account for {top_now['share_pct'].sum():.1f}% of total sales.
            Look at 'top_losers' to find major product-specific declines between recent and previous periods.
        """)

    # region & channel analysis
    region_table = None
    channel_table = None
    if region_col and region_col in df.columns:
        reg = df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)
        region_table = reg.reset_index().head(30).to_dict(orient='records')
    if channel_col and channel_col in df.columns:
        ch = df.groupby(channel_col)[sales_col].sum().sort_values(ascending=False)
        channel_table = ch.reset_index().head(30).to_dict(orient='records')

    # promotions analysis
    promo_insights = ""
    promo_stats = {}
    if promo_col and promo_col in df.columns:
        # try to interpret promo as boolean-ish
        promo_series = df[promo_col].astype(str).str.lower().isin(['1','true','yes','y','t'])
        promo_sales = df.loc[promo_series, sales_col]
        nonpromo_sales = df.loc[~promo_series, sales_col]
        promo_stats['promo_days'] = promo_series.sum()
        promo_stats['promo_sales_total'] = promo_sales.sum()
        promo_stats['nonpromo_sales_total'] = nonpromo_sales.sum()
        promo_stats['promo_avg_per_row'] = promo_sales.mean()
        promo_stats['nonpromo_avg_per_row'] = nonpromo_sales.mean()
        # t-test if scipy available
        if _HAS_SCIPY:
            t_stat, p_val = stats.ttest_ind(promo_sales.dropna(), nonpromo_sales.dropna(), equal_var=False)
            promo_stats['t_stat'] = float(t_stat)
            promo_stats['p_value'] = float(p_val)
        else:
            t, dfree = welsch_ttest(promo_sales.dropna().values, nonpromo_sales.dropna().values)
            # we'll not compute exact p-value without scipy; provide t and df
            promo_stats['t_stat'] = float(t) if not np.isnan(t) else None
            promo_stats['df_est'] = float(dfree) if not np.isnan(dfree) else None
            promo_stats['p_value'] = None
        promo_insights = dedent(f"""\
            Promotion rows: {promo_stats['promo_days']}, promo sales total: {promo_stats['promo_sales_total']:.2f}.
            Mean sale per row during promos: {promo_stats['promo_avg_per_row']:.2f} vs non-promo {promo_stats['nonpromo_avg_per_row']:.2f}.
        """)

    # price effect analysis (correlation)
    price_insights = ""
    price_corr = None
    if price_col:
        # compute correlation of price vs units (if units exists), and price vs sales
        try:
            if units_col:
                corr_price_units = df[[price_col, units_col]].dropna().corr().iloc[0,1]
            else:
                corr_price_units = None
            corr_price_sales = df[[price_col, sales_col]].dropna().corr().iloc[0,1]
            price_corr = {
                'price_units_corr': float(corr_price_units) if corr_price_units is not None else None,
                'price_sales_corr': float(corr_price_sales) if corr_price_sales is not None else None
            }
            price_insights = "Price correlations computed. Positive price-sales correlation might indicate price increases with sales (e.g., premiumization); negative price-units correlation could indicate elasticity (higher price, fewer units)."
        except Exception:
            price_insights = "Price correlation analysis failed due to insufficient data."

    # returns effect
    returns_insights = ""
    if returns_col and returns_col in df.columns:
        df[returns_col] = pd.to_numeric(df[returns_col], errors='coerce').fillna(0)
        total_returns = df[returns_col].sum()
        returns_insights = f"Total returns (sum of {returns_col}) = {total_returns:.2f}. Check whether return spikes coincide with sales dips."

    # Simple anomaly detection: rolling z-score on daily sales
    daily['rolling30'] = daily['sales'].rolling(30, min_periods=7).mean()
    daily['rolling30_std'] = daily['sales'].rolling(30, min_periods=7).std()
    daily['rolling_z'] = (daily['sales'] - daily['rolling30']) / daily['rolling30_std']
    anomalies = daily[daily['rolling_z'] < -2.5]  # strong negative anomalies

    # ---------- Make charts ----------
    assets = {}

    # time series daily
    fig, ax = plt.subplots(figsize=(10,3))
    ax.plot(daily['date'], daily['sales'], label='daily sales')
    ax.plot(daily['date'], daily['rolling30'], label='30d MA', linewidth=1)
    ax.set_title("Daily sales with 30d moving average")
    ax.set_xlabel("")
    ax.set_ylabel("Sales")
    ax.legend(frameon=False)
    assets['daily_ts'] = save_fig_to_base64(fig)

    # monthly series
    fig, ax = plt.subplots(figsize=(10,3))
    ax.bar(monthly.index.to_pydatetime(), monthly['sales'], label='monthly sales')
    ax.plot(monthly.index.to_pydatetime(), monthly['ma3'], label='3mo MA', linewidth=2)
    ax.set_title("Monthly sales and 3-month MA")
    ax.set_xlabel("")
    ax.set_ylabel("Sales")
    ax.legend(frameon=False)
    assets['monthly_ts'] = save_fig_to_base64(fig)

    # top products chart if available
    if product_col and product_table and product_table.get('top_products'):
        prod_df = pd.DataFrame(product_table['top_products']).head(top_n_products)
        fig, ax = plt.subplots(figsize=(8,4))
        ax.barh(prod_df[product_col].astype(str), prod_df['sales'])
        ax.invert_yaxis()
        ax.set_title(f"Top {top_n_products} products by sales (total period)")
        ax.set_xlabel("Sales")
        assets['top_products'] = save_fig_to_base64(fig)

    # region chart
    if region_table:
        reg_df = pd.DataFrame(region_table).head(10)
        fig, ax = plt.subplots(figsize=(8,4))
        ax.barh(reg_df[region_col].astype(str), reg_df['sales'])
        ax.invert_yaxis()
        ax.set_title("Top regions by sales")
        assets['region'] = save_fig_to_base64(fig)

    # channel chart
    if channel_table:
        ch_df = pd.DataFrame(channel_table).head(10)
        fig, ax = plt.subplots(figsize=(8,4))
        ax.barh(ch_df[channel_col].astype(str), ch_df['sales'])
        ax.invert_yaxis()
        ax.set_title("Top channels by sales")
        assets['channel'] = save_fig_to_base64(fig)

    # anomalies heat / list
    anomalies_list = anomalies.reset_index()[['date','sales','rolling_z']].head(50).to_dict(orient='records')

    # ---------- Summary and recommended next steps ----------
    reasons = []
    # check if decline concentrated in units or price or both
    recent_units = monthly.loc[recent_mask, 'units'].sum() if 'units' in monthly.columns else None
    prev_units = monthly.loc[prev_mask, 'units'].sum() if 'units' in monthly.columns else None
    units_pct = pct(recent_units, prev_units) if recent_units is not None and prev_units is not None else None
    if units_pct is not None and not np.isnan(units_pct):
        if units_pct < -5:
            reasons.append(f"Units sold decreased by {units_pct:.1f}% between periods — fewer transactions/volume is a likely driver.")
    # price
    if price_corr is not None:
        if price_corr.get('price_units_corr') is not None and price_corr['price_units_corr'] < -0.2:
            reasons.append("Negative correlation between price and units suggests price increases could have reduced volume (elasticity).")
    # product mix
    if product_table:
        # if top sellers decreased share:
        top_sales_before = None
        # compute share change of top N
        top_idx = [r[product_col] for r in product_table['top_products'][:top_n_products]]
        recent_top = df[recent_mask_rows].groupby(product_col)[sales_col].sum().reindex(top_idx).fillna(0).sum()
        prev_top = df[prev_mask_rows].groupby(product_col)[sales_col].sum().reindex(top_idx).fillna(0).sum() if prev_mask_rows.any() else None
        if prev_top and prev_top > 0:
            share_change = pct(recent_top, prev_top)
            if share_change < -3:
                reasons.append(f"Top {top_n_products} products declined together (top-products sales fell {share_change:.1f}%). Product-mix loss may be a factor.")
    # regions/channels
    if region_table:
        # check if top region dropped
        reg_df_full = pd.DataFrame(region_table)
        # coarse check omitted if insufficient data
    # promotions
    if promo_insights:
        reasons.append("Promotions analysis indicates differences in sales during promo vs non-promo periods — review changes to promo cadence/discounting.")
    if largest_drop_val and not math.isnan(largest_drop_val) and largest_drop_val < -20:
        reasons.append(f"Largest month-over-month drop: {largest_drop_val:.1f}% in {largest_drop.strftime('%Y-%m')} — investigate events/promotions/pricing/stockouts around that month.")

    if not reasons:
        reasons.append("No single dominant reason identified from available columns — see detailed charts and tables for clues (product, region, price, promotions).")

    # ---------- Compose HTML report ----------
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Sales Analysis Report</title>
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial; margin: 28px; color: #111; }}
        header{{margin-bottom:18px}}
        h1 {{ font-size:20px; margin:0 0 6px; }}
        h2 {{ font-size:16px; margin:18px 0 6px; }}
        .muted {{ color:#666; font-size:13px; }}
        .card {{ border-radius:8px; padding:12px; margin-bottom:14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); background:#fff; }}
        img.resp {{ max-width:100%; height:auto; display:block; margin:6px 0; border-radius:6px }}
        table {{ border-collapse:collapse; width:100%; font-size:13px; }}
        th,td {{ text-align:left; padding:6px 8px; border-bottom:1px solid #eee; }}
        .two-col {{ display:flex; gap:12px; }}
        .col {{ flex:1; }}
        pre {{ background:#f7f7f7; padding:8px; border-radius:6px; overflow:auto; }}
      </style>
    </head>
    <body>
      <header>
        <h1>Sales Analysis</h1>
        <div class="muted">Generated: {now} — Input file: {os.path.basename(path)}</div>
      </header>

      <section class="card">
        <h2>Executive summary</h2>
        <p>Total sales — recent {recent_period_months} months: <strong>{recent_total:,.2f}</strong>; previous {recent_period_months} months: <strong>{prev_total:,.2f}</strong> — change: <strong>{pct_change_recent_vs_prev:.1f}%</strong>.</p>
        <ul>
    """
    for r in reasons[:6]:
        html += f"<li>{r}</li>\n"
    html += "</ul></section>"

    # charts
    html += '<section class="card"><h2>Charts</h2>'
    html += f'<div class="two-col"><div class="col"><h3>Daily</h3><img class="resp" src="{assets["daily_ts"]}"></div>'
    html += f'<div class="col"><h3>Monthly</h3><img class="resp" src="{assets["monthly_ts"]}"></div></div>'
    if 'top_products' in assets:
        html += f'<h3>Top products</h3><img class="resp" src="{assets["top_products"]}">'
    if 'region' in assets:
        html += f'<h3>Top regions</h3><img class="resp" src="{assets["region"]}">'
    if 'channel' in assets:
        html += f'<h3>Top channels</h3><img class="resp" src="{assets["channel"]}">'
    html += "</section>"

    # Details
    html += '<section class="card"><h2>Detailed diagnostics</h2>'
    html += f"<h3>Largest month drop</h3><p>{largest_drop.strftime('%Y-%m')} : {largest_drop_val:.1f}%</p>"
    html += "<h3>Anomalies (strong negative daily drops)</h3>"
    if anomalies_list:
        html += "<table><tr><th>date</th><th>sales</th><th>z</th></tr>"
        for a in anomalies_list:
            html += f"<tr><td>{a['date'].strftime('%Y-%m-%d')}</td><td>{a['sales']:.2f}</td><td>{a['rolling_z']:.2f}</td></tr>"
        html += "</table>"
    else:
        html += "<p>No extreme daily negative anomalies detected (rolling z &lt; -2.5).</p>"

    # product tables
    if product_table:
        html += "<h3>Top products (total period)</h3>"
        html += "<table><tr><th>product</th><th>sales</th><th>share%</th></tr>"
        for r in product_table['top_products'][:20]:
            prod_name = r.get(product_col, "")
            html += f"<tr><td>{prod_name}</td><td>{r['sales']:.2f}</td><td>{r.get('share_pct',0):.1f}</td></tr>"
        html += "</table>"

        html += "<h3>Top product losers (recent vs previous)</h3>"
        html += "<table><tr><th>product</th><th>recent_sales</th><th>prev_sales</th><th>pct_diff</th></tr>"
        for r in product_table['top_losers'][:20]:
            html += f"<tr><td>{r.get(product_col,'')}</td><td>{r.get('recent_sales',0):.2f}</td><td>{r.get('prev_sales',0):.2f}</td><td>{r.get('pct_diff',0):.1f}%</td></tr>"
        html += "</table>"

    # region/channel
    if region_table:
        html += "<h3>Region breakdown (top 30)</h3>"
        html += "<table><tr><th>region</th><th>sales</th></tr>"
        for r in region_table:
            html += f"<tr><td>{r[region_col]}</td><td>{r['sales']:.2f}</td></tr>"
        html += "</table>"
    if channel_table:
        html += "<h3>Channel breakdown (top 30)</h3>"
        html += "<table><tr><th>channel</th><th>sales</th></tr>"
        for r in channel_table:
            html += f"<tr><td>{r[channel_col]}</td><td>{r['sales']:.2f}</td></tr>"
        html += "</table>"

    # price and promo
    html += "<h3>Promotions</h3>"
    if promo_insights:
        html += f"<pre>{promo_insights}\nDetailed stats: {promo_stats}</pre>"
    else:
        html += "<p>No promotions column found or insufficient data for promo analysis.</p>"

    html += "<h3>Price correlation</h3>"
    if price_corr:
        html += f"<pre>{price_corr}\n{price_insights}</pre>"
    else:
        html += "<p>No price column found or insufficient data.</p>"

    if returns_insights:
        html += f"<h3>Returns</h3><p>{returns_insights}</p>"

    html += "</section>"

    html += f"<footer class='muted' style='margin-top:18px'>Report generated by sales_analysis.py — minimal UX; modify script for further tests.</footer></body></html>"

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Report saved to {out_path}")

# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description="Quick sales analysis to investigate declines.")
    ap.add_argument("csv", help="Path to sales CSV file")
    ap.add_argument("--out", help="Output HTML report path", default="report.html")
    ap.add_argument("--periods", help="Recent period length in months for comparisons (default 3)", type=int, default=3)
    ap.add_argument("--top", help="Top N products to consider", type=int, default=10)
    args = ap.parse_args()
    if not os.path.exists(args.csv):
        print("CSV file not found:", args.csv)
        sys.exit(1)
    run_analysis(args.csv, out_path=args.out, recent_period_months=args.periods, top_n_products=args.top)

if __name__ == "__main__":
    main()
