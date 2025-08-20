import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import requests

# --- Fetch World Bank data (your existing functions) ---
WB_POP = "SP.POP.TOTL"
WB_GDPPC = "NY.GDP.PCAP.CD"

def wb_fetch_indicator(indicator):
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=20000"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    data = r.json()
    rows = []
    for obs in data[1]:
        if not obs["countryiso3code"]:
            continue
        rows.append({
            "iso3": obs["countryiso3code"],
            "country": obs["country"]["value"],
            "year": int(obs["date"]),
            "value": obs["value"]
        })
    df = pd.DataFrame(rows)
    df = df.sort_values(["iso3","year"]).dropna(subset=["value"])
    idx = df.groupby("iso3")["year"].idxmax()
    df = df.loc[idx].reset_index(drop=True)

    # Add Taiwan manually
    if indicator == WB_POP:
        taiwan_value = 23396049
    elif indicator == WB_GDPPC:
        taiwan_value = 84082
    else:
        taiwan_value = None

    taiwan_row = {"iso3":"TWN","country":"Taiwan","year":2023,"value":taiwan_value}
    df = pd.concat([df, pd.DataFrame([taiwan_row])], ignore_index=True)
    df = df.sort_values("country").reset_index(drop=True)
    return df

pop = wb_fetch_indicator(WB_POP)
gdp_pc = wb_fetch_indicator(WB_GDPPC)

df = pd.merge(
    pop[["iso3","country","value"]].rename(columns={"value":"population"}),
    gdp_pc[["iso3","value"]].rename(columns={"value":"gdp_per_capita"}),
    on="iso3", how="inner"
)

# Filter using World Bank metadata
meta = requests.get("https://api.worldbank.org/v2/country?format=json&per_page=400").json()[1]
taiwan = {
    "id": "TWN","iso2Code": "TW","name": "Taiwan",
    "region": {"id": "EAS","iso2code": "Z4","value": "East Asia & Pacific"},
    "adminregion":{"id":"","iso2code":"","value":""},
    "incomeLevel":{"id":"HIC","iso2code":"XD","value":"High income"},
    "lendingType":{"id":"LNX","iso2code":"XX","value":"Not classified"},
    "capitalCity":"Taipei","longitude":"121.5654","latitude":"25.0330"
}
meta.append(taiwan)
countries = {m["id"] for m in meta if m["region"]["id"] != "NA"}
df = df[df["iso3"].isin(countries)].copy()

income_map = {m["id"]: m["incomeLevel"]["id"] for m in meta}
def classify_status(iso3):
    income = income_map.get(iso3)
    if income == 'HIC':
        return 'Developed'
    elif income == 'UMC':
        return 'Upper-middle Developing'
    elif income == 'LMC':
        return 'Lower-middle Developing'
    elif income == 'LIC':
        return 'Least Developed'
    elif income == 'LNX':
        return 'Unknown'
    else:
        return 'Error'
df["status"] = df["iso3"].map(classify_status)
df = df.dropna(subset=["population","gdp_per_capita"])
df = df[(df["population"]>0) & (df["gdp_per_capita"]>0)].copy()
df = df.sort_values("population", ascending=False)

# --- Start Dash App ---
app = dash.Dash(__name__)

# Initial figure
def make_figure(selected=[]):
    fig = go.Figure()
    for _, r in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[r["population"]/1e6],
            y=[r["gdp_per_capita"]],
            mode="markers+text",
            marker=dict(color="green" if r["status"]=="Developed" else
                        "yellow" if r["status"]=="Upper-middle Developing" else
                        "orange" if r["status"]=="Lower-middle Developing" else
                        "red" if r["status"]=="Least Developed" else "grey", size=8),
            text=[r["country"] if r["country"] in selected else None],
            textposition="top center",
            name=r["country"],
            hovertext=[f"{r['country']}\nPopulation: {r['population']:,}\nGDP: ${r['gdp_per_capita']:,}"],
            hoverinfo="text"
        ))
    fig.update_xaxes(type="log", title="Population (millions)")
    fig.update_yaxes(type="log", title="GDP per capita (US$)")
    fig.update_layout(title="Population vs GDP per capita (195 countries)")
    return fig

# Layout
app.layout = html.Div([
    html.H3("Population vs GDP per capita"),
    dcc.Graph(id="scatter-plot", figure=make_figure()),
    html.Div([
        html.Label("Select countries to show labels:"),
        dcc.Dropdown(
            id="country-dropdown",
            options=[{"label": c, "value": c} for c in sorted(df["country"])],
            multi=True
        ),
        html.Button("Update Labels", id="update-btn", n_clicks=0),
        html.Button("Clear Labels", id="clear-btn", n_clicks=0)
    ], style={"width": "50%", "margin":"20px"})
])

# Callback
@app.callback(
    Output("scatter-plot", "figure"),
    [Input("update-btn", "n_clicks"),
     Input("clear-btn", "n_clicks")],
    [State("country-dropdown", "value")]
)
def update_labels(update_clicks, clear_clicks, selected):
    ctx = dash.callback_context
    if not ctx.triggered:
        return make_figure([])
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "clear-btn":
        return make_figure([])
    else:
        return make_figure(selected or [])

if __name__ == "__main__":
    app.run(debug=True)
