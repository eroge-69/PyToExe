# app_sales_potential.py
import os
from datetime import datetime
import pandas as pd
import numpy as np

# Try Streamlit (UI). If not installed, fallback to CLI mode.
try:
    import streamlit as st
    _HAS_STREAMLIT = True
except Exception:
    _HAS_STREAMLIT = False

# Try Plotly for interactive charts.
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    _HAS_PLOTLY = True
except Exception:
    _HAS_PLOTLY = False

# reproducibility
np.random.seed(42)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------- Data generation --------------------
def generate_fake_data(filename="market_data.xlsx", months_count=12):
    """
    Генерирует фиктивные данные:
    - Competitors (Наш бренд и конкуренты)
    - Products: наши SKU с помесячными продажами + конкурентные листинги с ценами
    - CategorySummary: общий рынок (volume, revenue)
    Сохраняет Excel в outputs/ и возвращает путь, либо возвращает dict DataFrame'ов при ошибке записи.
    """
    # Competitors
    competitors = pd.DataFrame({
        "CompetitorID": [0, 1, 2, 3],
        "Name": ["Наш бренд", "Конкурент A", "Конкурент B", "Конкурент C"]
    })

    # Months: last `months_count` months ending with current month
    end = pd.to_datetime(datetime.now().replace(day=1))
    months = pd.date_range(end=end, periods=months_count, freq="MS")
    month_labels = months.strftime("%Y-%m").tolist()

    # Our SKUs
    our_products_master = [
        {"ProductID": 1, "CompetitorID": 0, "ProductName": "Продукт A", "Category": "Категория 1", "BasePrice": 95},
        {"ProductID": 2, "CompetitorID": 0, "ProductName": "Продукт B", "Category": "Категория 1", "BasePrice": 100},
        {"ProductID": 3, "CompetitorID": 0, "ProductName": "Продукт C", "Category": "Категория 1", "BasePrice": 110},
    ]

    products_rows = []
    for idx_month, month in enumerate(months):
        month_str = month.strftime("%Y-%m")
        for prod in our_products_master:
            pid = prod["ProductID"]
            price = prod["BasePrice"]
            if prod["ProductName"] == "Продукт A":
                seasonal = 1 + 0.5 * np.sin((idx_month / 12.0) * 2 * np.pi)
                noise = np.random.normal(0, 0.05)
                vol = max(0, int(800 * seasonal * (1 + noise)))
            elif prod["ProductName"] == "Продукт B":
                trend = 1 + 0.01 * idx_month
                noise = np.random.normal(0, 0.04)
                vol = max(0, int(1000 * trend * (1 + noise)))
            else:
                trend = 1 + 0.05 * idx_month
                noise = np.random.normal(0, 0.06)
                vol = max(0, int(300 * trend * (1 + noise)))

            rev = vol * price * (1 + np.random.normal(0, 0.02))

            products_rows.append({
                "ProductID": pid,
                "CompetitorID": prod["CompetitorID"],
                "ProductName": prod["ProductName"],
                "Category": prod["Category"],
                "Price": price,
                "SalesMonth": month_str,
                "YourSalesVolume": vol,
                "YourSalesRevenue": round(rev, 2)
            })

    # Competitor listings (prices only)
    competitor_listings = [
        {"ProductID": 10, "CompetitorID": 1, "ProductName": "Конкурентный товар X", "Category": "Категория 1", "Price": 110},
        {"ProductID": 11, "CompetitorID": 1, "ProductName": "Конкурентный товар Y", "Category": "Категория 1", "Price": 130},
        {"ProductID": 12, "CompetitorID": 1, "ProductName": "Конкурентный товар Z", "Category": "Категория 1", "Price": 98},
        {"ProductID": 20, "CompetitorID": 2, "ProductName": "Конкурентный товар M", "Category": "Категория 1", "Price": 90},
        {"ProductID": 21, "CompetitorID": 2, "ProductName": "Конкурентный товар N", "Category": "Категория 1", "Price": 105},
        {"ProductID": 30, "CompetitorID": 3, "ProductName": "Конкурентный товар Q", "Category": "Категория 1", "Price": 120},
        {"ProductID": 31, "CompetitorID": 3, "ProductName": "Конкурентный товар W", "Category": "Категория 1", "Price": 99},
    ]

    df_products = pd.DataFrame(products_rows)
    df_competitor_listings = pd.DataFrame(competitor_listings)
    df_competitor_listings["SalesMonth"] = pd.NA
    df_competitor_listings["YourSalesVolume"] = pd.NA
    df_competitor_listings["YourSalesRevenue"] = pd.NA

    products_df = pd.concat([df_products, df_competitor_listings], ignore_index=True, sort=False)

    our_total_volume = df_products["YourSalesVolume"].sum()
    our_total_revenue = df_products["YourSalesRevenue"].sum()
    total_market_volume = int(our_total_volume * 20) if our_total_volume > 0 else 100000
    total_market_revenue = round(our_total_revenue * 20.0, 2) if our_total_revenue > 0 else 1000000.0

    category_summary = pd.DataFrame({
        "Category": ["Категория 1"],
        "TotalMarketVolume": [total_market_volume],
        "TotalMarketRevenue": [total_market_revenue],
        "CategoryMarketShare": [0.15],
        "PeriodStart": [month_labels[0] + "-01"],
        "PeriodEnd": [month_labels[-1] + "-28"]
    })

    excel_path = os.path.join(OUTPUT_DIR, filename)
    try:
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            competitors.to_excel(writer, sheet_name="Competitors", index=False)
            products_df.to_excel(writer, sheet_name="Products", index=False)
            category_summary.to_excel(writer, sheet_name="CategorySummary", index=False)
        return excel_path
    except Exception:
        return {"Competitors": competitors, "Products": products_df, "CategorySummary": category_summary}


# -------------------- Model --------------------
class MarketPotentialModel:
    def __init__(self, data_source, category_market_share=0.15, forecast_horizon_months=6,
                 price_weight_median_vs_mean=0.6, new_product_price_adjustment_factor=1.0,
                 output_dir=OUTPUT_DIR):
        self.data_source = data_source
        self.category_market_share = float(category_market_share)
        self.forecast_horizon_months = int(forecast_horizon_months)
        self.price_weight_median_vs_mean = float(price_weight_median_vs_mean)
        self.new_product_price_adjustment_factor = float(new_product_price_adjustment_factor)

        self.competitors = None
        self.products = None
        self.category_summary = None
        self.monthly_sales_df = pd.DataFrame()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        if isinstance(self.data_source, dict):
            self.competitors = self.data_source.get("Competitors")
            self.products = self.data_source.get("Products")
            self.category_summary = self.data_source.get("CategorySummary")
            return
        self.competitors = pd.read_excel(self.data_source, sheet_name="Competitors")
        self.products = pd.read_excel(self.data_source, sheet_name="Products")
        self.category_summary = pd.read_excel(self.data_source, sheet_name="CategorySummary")

    def analyze_trend(self):
        if self.category_summary is None or self.products is None:
            return 0.0, 0.0, pd.DataFrame()
        cat = self.category_summary["Category"].iloc[0]
        our = self.products[(self.products["CompetitorID"] == 0) & (self.products["Category"] == cat)].copy()
        if our.empty:
            return 0.0, 0.0, pd.DataFrame()
        our["SalesMonth"] = pd.to_datetime(our["SalesMonth"], format="%Y-%m", errors="coerce")
        monthly = our.groupby("SalesMonth").agg({"YourSalesVolume": "sum", "YourSalesRevenue": "sum"}).reset_index().sort_values("SalesMonth")
        if monthly.empty:
            return 0.0, 0.0, monthly
        monthly["VolumePctChange"] = monthly["YourSalesVolume"].pct_change().fillna(0.0)
        monthly["RevenuePctChange"] = monthly["YourSalesRevenue"].pct_change().fillna(0.0)
        avg_volume_growth = float(monthly["VolumePctChange"].mean())
        avg_revenue_growth = float(monthly["RevenuePctChange"].mean())
        self.monthly_sales_df = monthly.copy()
        return avg_volume_growth, avg_revenue_growth, monthly

    def forecast_your_sales(self, monthly_df_base, avg_volume_growth, avg_revenue_growth, forecast_horizon=None):
        if monthly_df_base is None or monthly_df_base.empty:
            return 0.0, 0.0
        if "YourSalesVolume" not in monthly_df_base.columns or "YourSalesRevenue" not in monthly_df_base.columns:
            return 0.0, 0.0
        last_volume = float(monthly_df_base["YourSalesVolume"].iloc[-1])
        last_revenue = float(monthly_df_base["YourSalesRevenue"].iloc[-1])
        horizon = int(forecast_horizon) if forecast_horizon is not None else self.forecast_horizon_months
        forecast_vol = last_volume * ((1 + avg_volume_growth) ** horizon)
        forecast_rev = last_revenue * ((1 + avg_revenue_growth) ** horizon)
        return forecast_vol, forecast_rev

    def estimate_total_market(self):
        if self.category_summary is None or self.category_summary.empty:
            return 0, 0.0
        total_vol = int(self.category_summary["TotalMarketVolume"].iloc[0])
        total_rev = float(self.category_summary["TotalMarketRevenue"].iloc[0])
        return total_vol, total_rev

    def estimate_competitor_shares(self, forecast_vol, forecast_rev, target_market_share=None):
        total_market_vol, total_market_rev = self.estimate_total_market()
        if total_market_vol <= 0 or total_market_rev <= 0:
            return 0.0, 0.0, pd.DataFrame()
        your_share_vol = float(forecast_vol) / float(total_market_vol)
        your_share_rev = float(forecast_rev) / float(total_market_rev)
        cur_target = float(target_market_share) if target_market_share is not None else self.category_market_share
        remaining_share_vol = max(0.0, cur_target - your_share_vol)
        remaining_share_rev = max(0.0, cur_target - your_share_rev)
        competitors_ids = []
        if self.competitors is not None:
            competitors_ids = self.competitors[self.competitors["CompetitorID"] != 0]["CompetitorID"].unique().tolist()
        count_comp = len(competitors_ids)
        per_comp_share_vol = (remaining_share_vol / count_comp) if count_comp > 0 else 0.0
        per_comp_share_rev = (remaining_share_rev / count_comp) if count_comp > 0 else 0.0
        comp_shares = pd.DataFrame({
            "CompetitorID": competitors_ids,
            "EstimatedShareVolume": [per_comp_share_vol] * count_comp,
            "EstimatedShareRevenue": [per_comp_share_rev] * count_comp
        })
        return your_share_vol, your_share_rev, comp_shares

    def recommend_price(self, price_adjustment_factor=None):
        if self.category_summary is None or self.products is None:
            return None
        cat = self.category_summary["Category"].iloc[0]
        cat_products = self.products[(self.products["Category"] == cat) & (self.products["CompetitorID"] != 0)]
        if cat_products.empty:
            return None
        prices = cat_products["Price"].dropna()
        if prices.empty:
            return None
        median_price = float(prices.median())
        mean_price = float(prices.mean())
        adjust = float(price_adjustment_factor) if price_adjustment_factor is not None else self.new_product_price_adjustment_factor
        recommended_price = (self.price_weight_median_vs_mean * median_price + (1 - self.price_weight_median_vs_mean) * mean_price) * adjust
        stats = {
            "median": median_price,
            "mean": mean_price,
            "min": float(prices.min()),
            "max": float(prices.max()),
            "recommended_price": round(float(recommended_price), 2),
            "distribution": prices
        }
        return stats

    def recommend_assortment(self):
        if self.products is None or self.category_summary is None:
            return []
        cat = self.category_summary["Category"].iloc[0]
        cat_products = self.products[self.products["Category"] == cat]
        our_names = set(cat_products[cat_products["CompetitorID"] == 0]["ProductName"].dropna().unique())
        competitor_products = cat_products[cat_products["CompetitorID"] != 0]
        competitor_unique = list(set(competitor_products["ProductName"].dropna().unique()) - our_names)
        return competitor_unique

    def estimate_market_potential(self, your_share_vol, your_share_rev, target_market_share=None):
        total_market_vol, total_market_rev = self.estimate_total_market()
        if total_market_vol <= 0 or total_market_rev <= 0:
            return 0.0, 0.0
        cur_target = float(target_market_share) if target_market_share is not None else self.category_market_share
        potential_share_vol = max(0.0, cur_target - your_share_vol)
        potential_share_rev = max(0.0, cur_target - your_share_rev)
        potential_vol = total_market_vol * potential_share_vol
        potential_rev = total_market_rev * potential_share_rev
        return potential_vol, potential_rev

    # ---------------- Plotly visualization helpers ----------------
    def plot_monthly_sales(self, monthly_df, title="Месячные продажи — объем и выручка"):
        if not _HAS_PLOTLY or monthly_df is None or monthly_df.empty:
            return None
        df = monthly_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["SalesMonth"]):
            df["SalesMonth"] = pd.to_datetime(df["SalesMonth"], format="%Y-%m", errors="coerce")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df["SalesMonth"], y=df["YourSalesVolume"], mode="lines+markers", name="Объем (шт.)", line=dict(color="#2b8cbe")))
        fig.add_trace(go.Scatter(x=df["SalesMonth"], y=df["YourSalesRevenue"], mode="lines+markers", name="Выручка", line=dict(color="#2ca25f")), secondary_y=True)
        fig.update_layout(title=title, xaxis_title="Месяц", hovermode="x unified", height=520)
        fig.update_yaxes(title_text="Объем (шт.)", secondary_y=False)
        fig.update_yaxes(title_text="Выручка", secondary_y=True)
        return fig

    def plot_price_distribution(self, price_stats, title="Распределение цен конкурентов"):
        if not _HAS_PLOTLY or price_stats is None:
            return None
        prices = price_stats.get("distribution")
        if prices is None or len(prices) == 0:
            return None
        fig = go.Figure()
        fig.add_trace(go.Box(x=prices, name="Цены конкурентов", marker_color="#9ecae1", boxpoints="all", jitter=0.3))
        rec = price_stats.get("recommended_price")
        if rec is not None:
            fig.add_vline(x=rec, line_dash="dash", line_color="red")
            fig.add_annotation(x=rec, y=0.98, yref="paper", showarrow=False, text=f"Рекоменд. цена: {rec}", font=dict(color="red"))
        fig.update_layout(title=title, xaxis_title="Цена", showlegend=False, height=320)
        return fig

    def plot_competitor_share_pie(self, comp_shares, your_share_vol, title="Проектное распределение долей рынка"):
        if not _HAS_PLOTLY:
            return None
        labels = []
        values = []
        if comp_shares is None or comp_shares.empty:
            labels = ["Мы (проекция)"]
            values = [float(your_share_vol)]
        else:
            labels = ["Мы (проекция)"]
            values = [float(your_share_vol)]
            for _, r in comp_shares.iterrows():
                labels.append(f"Конкурент {int(r['CompetitorID'])}")
                values.append(float(r["EstimatedShareVolume"]))
        if sum(values) <= 0:
            return None
        fig = px.pie(values=values, names=labels, title=title, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textinfo="percent+label")
        return fig

    def plot_potential(self, potential_vol, potential_rev, title="Потенциал рынка"):
        if not _HAS_PLOTLY:
            return None
        df = pd.DataFrame({
            "Метрика": ["Потенциальный объем", "Потенциальная выручка"],
            "Значение": [potential_vol, potential_rev],
            "Тип": ["Объем", "Выручка"]
        })
        fig = px.bar(df, x="Метрика", y="Значение", color="Тип", title=title,
                     color_discrete_map={"Объем": "#6a51a3", "Выручка": "#238b45"})
        fig.update_layout(showlegend=False, height=360)
        return fig

    # ---------------- Main ----------------
    def analyze(self, visualize=True):
        if self.competitors is None:
            self.load_data()
        avg_vol_growth, avg_rev_growth, monthly_df = self.analyze_trend()
        self.monthly_sales_df = monthly_df.copy() if not monthly_df.empty else monthly_df
        forecast_vol, forecast_rev = self.forecast_your_sales(self.monthly_sales_df, avg_vol_growth, avg_rev_growth)
        your_share_vol, your_share_rev, comp_shares = self.estimate_competitor_shares(forecast_vol, forecast_rev)
        price_stats = self.recommend_price()
        recommended_assortment = self.recommend_assortment()
        potential_vol, potential_rev = self.estimate_market_potential(your_share_vol, your_share_rev)

        figs = {}
        if visualize and _HAS_PLOTLY:
            figs["monthly_sales"] = self.plot_monthly_sales(self.monthly_sales_df)
            figs["price_dist"] = self.plot_price_distribution(price_stats)
            figs["share_pie"] = self.plot_competitor_share_pie(comp_shares, your_share_vol)
            figs["potential"] = self.plot_potential(potential_vol, potential_rev)

        return {
            "месячная_таблица": self.monthly_sales_df,
            "ср_ежемесячный_рост_объёма": avg_vol_growth,
            "ср_ежемесячный_рост_выручки": avg_rev_growth,
            "прогноз_объёма": forecast_vol,
            "прогноз_выручки": forecast_rev,
            "наша_доля_объема": your_share_vol,
            "наша_доля_выручки": your_share_rev,
            "доли_конкурентов": comp_shares,
            "рекомендуемая_цена": price_stats,
            "рекомендуемое_ассортиментное_пополнение": recommended_assortment,
            "потенциал_объём": potential_vol,
            "потенциал_выручка": potential_rev,
            "figures": figs,
            "output_dir": self.output_dir
        }

    def perform_what_if_analysis(self, what_if_avg_volume_growth, what_if_avg_revenue_growth,
                                 what_if_category_market_share, what_if_price_adjustment_factor,
                                 what_if_forecast_horizon):
        base_monthly = self.monthly_sales_df.copy() if not self.monthly_sales_df.empty else pd.DataFrame()
        forecast_vol_wi, forecast_rev_wi = self.forecast_your_sales(
            base_monthly, what_if_avg_volume_growth, what_if_avg_revenue_growth, forecast_horizon=what_if_forecast_horizon
        )
        your_share_vol_wi, your_share_rev_wi, comp_shares_wi = self.estimate_competitor_shares(
            forecast_vol_wi, forecast_rev_wi, target_market_share=what_if_category_market_share
        )
        price_stats_wi = self.recommend_price(price_adjustment_factor=what_if_price_adjustment_factor)
        potential_vol_wi, potential_rev_wi = self.estimate_market_potential(your_share_vol_wi, your_share_rev_wi, target_market_share=what_if_category_market_share)

        figs_wi = {}
        if _HAS_PLOTLY:
            figs_wi["monthly_sales_wi"] = self.plot_monthly_sales(base_monthly, title=f"Месячные продажи (Что-если, гориз. {what_if_forecast_horizon} мес.)")
            if not base_monthly.empty:
                last_month = pd.to_datetime(base_monthly["SalesMonth"].iloc[-1], format="%Y-%m", errors="coerce")
                try:
                    forecast_month = last_month + pd.DateOffset(months=int(what_if_forecast_horizon))
                except Exception:
                    forecast_month = last_month
                figs_wi["monthly_sales_wi"].add_trace(go.Scatter(
                    x=[forecast_month], y=[forecast_vol_wi], mode="markers", marker=dict(color="red", size=10, symbol="star"),
                    name=f"Прогноз объёма ({what_if_forecast_horizon} мес.)"
                ), secondary_y=False)
                figs_wi["monthly_sales_wi"].add_trace(go.Scatter(
                    x=[forecast_month], y=[forecast_rev_wi], mode="markers", marker=dict(color="orange", size=10, symbol="star"),
                    name=f"Прогноз выручки ({what_if_forecast_horizon} мес.)"
                ), secondary_y=True)
            figs_wi["price_dist_wi"] = self.plot_price_distribution(price_stats_wi, title="Распределение цен (Что-если)")
            figs_wi["share_pie_wi"] = self.plot_competitor_share_pie(comp_shares_wi, your_share_vol_wi, title="Доли рынка (Что-если)")
            figs_wi["potential_wi"] = self.plot_potential(potential_vol_wi, potential_rev_wi, title="Потенциал (Что-если)")

        return {
            "прогноз_объёма_wi": forecast_vol_wi,
            "прогноз_выручки_wi": forecast_rev_wi,
            "наша_доля_объема_wi": your_share_vol_wi,
            "наша_доля_выручки_wi": your_share_rev_wi,
            "доли_конкурентов_wi": comp_shares_wi,
            "рекомендуемая_цена_wi": price_stats_wi,
            "потенциал_объём_wi": potential_vol_wi,
            "потенциал_выручка_wi": potential_rev_wi,
            "figures_wi": figs_wi
        }


# -------------------- CLI fallback --------------------
def run_cli_mode():
    print("Запуск в CLI режиме.")
    ds = generate_fake_data("market_data.xlsx", months_count=12)
    model = MarketPotentialModel(ds)
    res = model.analyze(visualize=_HAS_PLOTLY)
    print("\n=== Краткая сводка ===")
    print(f"Средн. ежем. рост объёма: {res['ср_ежемесячный_рост_объёма']:.2%}")
    print(f"Средн. ежем. рост выручки: {res['ср_ежемесячный_рост_выручки']:.2%}")
    print(f"Прогноз объёма через {model.forecast_horizon_months} мес.: {res['прогноз_объёма']:.0f} шт.")
    print(f"Прогноз выручки через {model.forecast_horizon_months} мес.: {res['прогноз_выручки']:.2f}")
    if res["рекомендуемая_цена"]:
        rp = res["рекомендуемая_цена"]
        print(f"Рекомендуемая цена: {rp['recommended_price']} (медиана {rp['median']}, средняя {rp['mean']:.2f})")
    print(f"Рекомендуемое пополнение ассортимента: {res['рекомендуемое_ассортиментное_пополнение']}")
    print(f"Потенциал (объём): {res['потенциал_объём']:.0f}")
    print(f"Потенциал (выручка): {res['потенциал_выручка']:.2f}")
    print(f"Outputs folder: {res['output_dir']}")


# -------------------- Streamlit UI --------------------
def run_streamlit_app():
    st.set_page_config(page_title="Анализ потенциала рынка", layout="wide")
    st.title("Анализ потенциала рынка — демонстрация")
    st.markdown("Интерактивное приложение. Все подписи — на русском языке.")

    # Sidebar: parameters
    st.sidebar.header("Параметры данных и модели")
    months_count = st.sidebar.slider("Число исторических месяцев", 6, 36, 12)
    base_forecast = st.sidebar.slider("Горизонт прогноза (мес.)", 1, 24, 6)
    base_target_share = st.sidebar.slider("Целевая доля категории (%)", 1, 50, 15) / 100.0
    base_price_weight = st.sidebar.slider("Вес медианы в рекоменд. цене", 0.0, 1.0, 0.6, 0.05)
    base_price_adj = st.sidebar.number_input("Множитель для рекоменд. цены", 0.5, 2.0, 1.0, 0.05)

    if "data_source" not in st.session_state:
        st.session_state["data_source"] = None
    if "base_model" not in st.session_state:
        st.session_state["base_model"] = None
    if "base_results" not in st.session_state:
        st.session_state["base_results"] = None
    if "what_if_results" not in st.session_state:
        st.session_state["what_if_results"] = None

    if st.sidebar.button("Сгенерировать тестовые данные"):
        ds = generate_fake_data("market_data.xlsx", months_count=months_count)
        st.session_state["data_source"] = ds
        st.session_state["base_model"] = None
        st.session_state["base_results"] = None
        st.session_state["what_if_results"] = None
        st.sidebar.success("Данные сгенерированы и сохранены в outputs/ (если запись доступна).")

    if st.sidebar.button("Запустить базовый анализ"):
        if st.session_state["data_source"] is None:
            st.session_state["data_source"] = generate_fake_data("market_data.xlsx", months_count=months_count)
        model = MarketPotentialModel(
            st.session_state["data_source"],
            category_market_share=base_target_share,
            forecast_horizon_months=base_forecast,
            price_weight_median_vs_mean=base_price_weight,
            new_product_price_adjustment_factor=base_price_adj
        )
        with st.spinner("Выполняю анализ..."):
            res = model.analyze(visualize=_HAS_PLOTLY)
        st.session_state["base_model"] = model
        st.session_state["base_results"] = res
        st.session_state["what_if_results"] = None
        st.success("Базовый анализ завершен.")

    base_res = st.session_state.get("base_results")
    if base_res:
        st.subheader("Базовый анализ — сводка")
        c1, c2, c3 = st.columns(3)
        c1.metric("Средн. ежем. рост объёма", f"{base_res['ср_ежемесячный_рост_объёма']:.2%}")
        c2.metric("Средн. ежем. рост выручки", f"{base_res['ср_ежемесячный_рост_выручки']:.2%}")
        c3.metric(f"Прогноз объёма ({base_forecast} мес.)", f"{base_res['прогноз_объёма']:.0f}")

        st.markdown("### Месячные продажи (наши SKU)")
        monthly = base_res["месячная_таблица"]
        if monthly is not None and not monthly.empty:
            disp = monthly.copy()
            if pd.api.types.is_datetime64_any_dtype(disp["SalesMonth"]):
                disp["SalesMonth"] = disp["SalesMonth"].dt.strftime("%Y-%m")
            st.dataframe(disp.style.format({"YourSalesVolume": "{:,.0f}", "YourSalesRevenue": "{:,.2f}"}), use_container_width=True)
            st.download_button("Скачать CSV (месячные продажи)", disp.to_csv(index=False).encode("utf-8-sig"), "monthly_sales.csv", "text/csv")

        st.markdown("### Рекомендации")
        rp = base_res.get("рекомендуемая_цена")
        if rp:
            st.info(f"Рекомендуемая цена: {rp['recommended_price']} (медиана {rp['median']}, средняя {rp['mean']:.2f})")
        st.write("Рекомендуемое пополнение ассортимента:", base_res.get("рекомендуемое_ассортиментное_пополнение", []))

        st.markdown("### Потенциал рынка")
        st.write(f"Потенциальный объём: {base_res['потенциал_объём']:.0f} шт.")
        st.write(f"Потенциальная выручка: {base_res['потенциал_выручка']:.2f}")

        st.markdown("### Графики")
        figs = base_res.get("figures", {})
        if figs.get("monthly_sales") is not None:
            st.plotly_chart(figs["monthly_sales"], use_container_width=True)
        if figs.get("price_dist") is not None:
            st.plotly_chart(figs["price_dist"], use_container_width=True)
        if figs.get("share_pie") is not None:
            st.plotly_chart(figs["share_pie"], use_container_width=True)
        if figs.get("potential") is not None:
            st.plotly_chart(figs["potential"], use_container_width=True)

        # What-if
        st.markdown("---")
        st.header("Модуль 'Что-если' (What-If)")

        base_avg_vol = base_res["ср_ежемесячный_рост_объёма"]
        base_avg_rev = base_res["ср_ежемесячный_рост_выручки"]

        wi_col1, wi_col2 = st.columns(2)
        vol_change_pct = wi_col1.slider("Изменение среднего роста объёма (%)", -50.0, 50.0, 0.0, 0.5) / 100.0
        rev_change_pct = wi_col2.slider("Изменение среднего роста выручки (%)", -50.0, 50.0, 0.0, 0.5) / 100.0

        wi_target_share = st.slider("Новая целевая доля категории (%)", 1, 50, int(base_target_share * 100)) / 100.0
        wi_price_adj = st.number_input("Множитель рекоменд. цены (Что-если)", 0.5, 2.0, base_price_adj, 0.05)
        wi_forecast_horizon = st.slider("Новый горизонт прогноза (мес.)", 1, 24, base_forecast)

        final_vol_growth = base_avg_vol * (1 + vol_change_pct)
        final_rev_growth = base_avg_rev * (1 + rev_change_pct)

        if st.button("Выполнить 'Что-если' анализ"):
            model_instance = st.session_state["base_model"]
            if model_instance is None:
                st.error("Сначала запустите базовый анализ.")
            else:
                with st.spinner("Выполняю 'Что-если'..."):
                    wi_res = model_instance.perform_what_if_analysis(
                        what_if_avg_volume_growth=final_vol_growth,
                        what_if_avg_revenue_growth=final_rev_growth,
                        what_if_category_market_share=wi_target_share,
                        what_if_price_adjustment_factor=wi_price_adj,
                        what_if_forecast_horizon=wi_forecast_horizon
                    )
                st.session_state["what_if_results"] = wi_res
                st.success("Что-если анализ готов.")

        wi_res = st.session_state.get("what_if_results")
        if wi_res:
            st.subheader("Результаты 'Что-если' анализа")
            w1, w2, w3 = st.columns(3)
            w1.metric("Прогноз объёма (Что-если)", f"{wi_res['прогноз_объёма_wi']:.0f}")
            w2.metric("Прогноз выручки (Что-если)", f"{wi_res['прогноз_выручки_wi']:.2f}")
            rp_wi = wi_res.get("рекомендуемая_цена_wi")
            if rp_wi:
                w3.metric("Рекоменд. цена (Что-если)", f"{rp_wi['recommended_price']}")
            st.markdown("#### Графики (Что-если)")
            figs_wi = wi_res.get("figures_wi", {})
            if figs_wi.get("monthly_sales_wi") is not None:
                st.plotly_chart(figs_wi["monthly_sales_wi"], use_container_width=True)
            if figs_wi.get("price_dist_wi") is not None:
                st.plotly_chart(figs_wi["price_dist_wi"], use_container_width=True)
            if figs_wi.get("share_pie_wi") is not None:
                st.plotly_chart(figs_wi["share_pie_wi"], use_container_width=True)
            if figs_wi.get("potential_wi") is not None:
                st.plotly_chart(figs_wi["potential_wi"], use_container_width=True)

    else:
        st.info("Нажмите 'Сгенерировать тестовые данные' и затем 'Запустить базовый анализ' в боковой панели.")


# -------------------- Entrypoint --------------------
def main():
    if _HAS_STREAMLIT:
        run_streamlit_app()
    else:
        print("Streamlit не установлен. Запуск в CLI режиме.")
        run_cli_mode()


if __name__ == "__main__":
    main()