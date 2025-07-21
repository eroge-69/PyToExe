import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# ============== HELFERFUNKTIONEN ==============
def get_numeric_input(prompt):
    """Fragt den Benutzer nach einer numerischen Eingabe und behandelt Fehler."""
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")

def format_currency(value):
    """Formatiert einen Zahlenwert als Währung in Euro."""
    return f"{value:,.2f} €"

# ============== VISUALISIERUNGSFUNKTIONEN ==============
def create_parameters_image(params, filename='business_case_parameter.png'):
    """Erstellt ein Bild mit einer Zusammenfassung aller Eingabeparameter."""
    fig, ax = plt.subplots(figsize=(8, 11))
    ax.axis('off')
    fig.suptitle('Zusammenfassung der Parameter', fontsize=16, y=0.98)
    y_pos = 0.95
    
    ax.text(0.05, y_pos, f"Erstellt von:", weight='bold'); ax.text(0.5, y_pos, params['creator'])
    y_pos -= 0.05
    ax.text(0.05, y_pos, f"Erstelldatum:", weight='bold'); ax.text(0.5, y_pos, params['creation_time'])
    y_pos -= 0.05
    ax.text(0.05, y_pos, f"Business Unit:", weight='bold'); ax.text(0.5, y_pos, params['bu_choice'].capitalize())
    y_pos -= 0.05
    ax.text(0.05, y_pos, f"Produktionsland:", weight='bold'); ax.text(0.5, y_pos, params['country'].capitalize())
    y_pos -= 0.05
    ax.text(0.05, y_pos, f"Inflationsrate (fix):", weight='bold'); ax.text(0.5, y_pos, f"{params['inflation_rate']:.2%}")
    y_pos -= 0.05
    ax.text(0.05, y_pos, f"Erster Verkauf nach Projektstart:", weight='bold'); ax.text(0.5, y_pos, f"{params['sales_delay_months']} Monate")
    y_pos -= 0.1

    sections = {
        "Fixe Stundensätze (€/h)": params['rates'], "Einmalige Projektkosten": params['project_costs'],
        "Daten pro Einheit (Jahr 1)": params['unit_data'], "Absatzplanung (Einheiten)": params['sales_plan']
    }
    for title, data in sections.items():
        ax.text(0.05, y_pos, title, weight='bold', fontsize=12); y_pos -= 0.06
        for label, value in data.items():
            ax.text(0.1, y_pos, label); ax.text(0.5, y_pos, value); y_pos -= 0.04
        y_pos -= 0.02
    plt.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close(fig)

def create_cost_structure_charts(project_costs_data, unit_costs_data, filename='business_case_kostenstruktur.png'):
    """Erstellt zwei Donut-Diagramme für die Kostenstruktur."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    labels1, values1 = list(project_costs_data.keys()), list(project_costs_data.values())
    ax1.pie(values1, labels=labels1, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4), pctdistance=0.8)
    ax1.set_title('Zusammensetzung der Projektkosten', pad=20)
    labels2, values2 = list(unit_costs_data.keys()), list(unit_costs_data.values())
    ax2.pie(values2, labels=labels2, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4), pctdistance=0.8)
    ax2.set_title('Zusammensetzung der variablen Stückkosten (Jahr 1)', pad=20)
    fig.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close(fig)

def create_main_analysis_chart(df_results, kpis, filename='business_case_analyse.png'):
    """Erstellt das Haupt-Analyse-Chart inklusive aller relevanten KPIs."""
    fig = plt.figure(figsize=(12, 11))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 2])

    ax1 = fig.add_subplot(gs[0, 0])
    bar_colors = ['lightcoral' if val < 0 else 'skyblue' for val in df_results['Jährl. Nettogewinn (€)']]
    ax1.bar(df_results['Jahr'], df_results['Jährl. Nettogewinn (€)'], label='Jährlicher Nettogewinn/-verlust', color=bar_colors)
    ax1.set_ylabel('Jährlicher Nettogewinn/-verlust in €'); ax1.set_title('Finanzanalyse über 10 Jahre (mit Inflation)', fontsize=16, pad=20)
    
    ax2 = ax1.twinx()
    ax2.plot(df_results['Jahr'], df_results['Kum. Nettogewinn (€)'], label='Kumulativer Nettogewinn', color='red', marker='o')
    ax2.set_ylabel('Kumulativer Betrag in €')
    ax2.axhline(y=0, color='grey', linestyle='--')
    
    lines, labels = ax1.get_legend_handles_labels(); lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')
    ax1.tick_params(axis='x', rotation=45)

    ax3 = fig.add_subplot(gs[1, 0])
    ax3.axis('off')
    
    if kpis['db_prozent'] >= kpis['target_margin']:
        ziel_erreicht_text, ziel_erreicht_color = "ZIEL ERREICHT", "green"
    elif kpis['db_prozent'] >= kpis['target_margin'] * 0.95:
        ziel_erreicht_text, ziel_erreicht_color = "AKZEPTABEL", "orange"
    else:
        ziel_erreicht_text, ziel_erreicht_color = "ZIEL VERFEHLT", "red"
    
    y_pos, line_height = 0.98, 0.09
    
    ax3.text(0.01, y_pos, f"--- Deckungsbeitrags-Analyse (Business Unit: {kpis['bu_choice']}) ---", ha='left', va='top', fontsize=11, weight='bold')
    y_pos -= line_height
    ax3.text(0.01, y_pos, f"Errechneter DB1 ({kpis['start_year']}): {kpis['db_einheit']} ({kpis['db_prozent']:.2f} %) | Ziel-DB1: {kpis['target_margin']:.2f} %", ha='left', va='top', fontsize=10)
    ax3.text(0.65, y_pos, f"► {ziel_erreicht_text}", ha='left', va='top', fontsize=10, color=ziel_erreicht_color, weight='bold')
    y_pos -= (line_height * 1.2)

    ax3.text(0.01, y_pos, f"--- Zusammenfassung & KPIs ---", ha='left', va='top', fontsize=11, weight='bold')
    y_pos -= line_height
    ax3.text(0.01, y_pos, f"Gesamte Projektkosten: {kpis['projektkosten']} | Nettogewinn (Gesamt): {kpis['nettogewinn']}", ha='left', va='top', fontsize=10)
    y_pos -= line_height
    ax3.text(0.01, y_pos, f"Amortisation: {kpis['payback']} | Break-Even (total über 10J): {kpis['break_even_total']:,.0f} Einheiten", ha='left', va='top', fontsize=10)
    y_pos -= (line_height * 1.2)

    ax3.text(0.01, y_pos, f"--- Szenario-Analyse ---", ha='left', va='top', fontsize=11, weight='bold')
    y_pos -= line_height
    ax3.text(0.01, y_pos, f"Gewinn im Best-Case: {kpis['best_case']} | Gewinn im Worst-Case: {kpis['worst_case']}", ha='left', va='top', fontsize=10)
    
    if kpis.get('opt_scenarios'):
        s = kpis['opt_scenarios']
        y_pos -= (line_height * 1.2)
        ax3.text(0.01, y_pos, f"--- ZIEL VERFEHLT: Optimierungs-Szenarien (Basis {kpis['start_year']}) ---", ha='left', va='top', fontsize=11, weight='bold', color='red')
        y_pos -= line_height
        ax3.text(0.01, y_pos, f"1. Nur Materialkosten senken auf: {format_currency(s['new_material_cost'])}", ha='left', va='top', fontsize=10)
        y_pos -= line_height
        ax3.text(0.01, y_pos, f"2. Nur Produktionszeit senken auf: {s['new_prod_time']:.1f} min/Stk.", ha='left', va='top', fontsize=10)
    
    if kpis.get('cost_buffer'):
        b = kpis['cost_buffer']
        y_pos -= (line_height * 1.2)
        ax3.text(0.01, y_pos, f"--- ZIEL ERREICHT/AKZEPTABEL: Puffer-Analyse (Basis {kpis['start_year']}) ---", ha='left', va='top', fontsize=11, weight='bold', color='green')
        y_pos -= line_height
        ax3.text(0.01, y_pos, f"Die Materialkosten können um {format_currency(b['buffer_euros'])} auf bis zu {format_currency(b['max_material_cost'])} steigen.", ha='left', va='top', fontsize=10)

    fig.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close(fig)

def create_tornado_chart(sensitivity_results, base_profit, filename='business_case_sensitivitaet.png'):
    labels, low_values, high_values = list(sensitivity_results.keys()), np.array([res[0] for res in sensitivity_results.values()]), np.array([res[1] for res in sensitivity_results.values()])
    ranges = high_values - low_values
    sorted_indices = np.argsort(ranges)
    labels, low_values, high_values = [labels[i] for i in sorted_indices], low_values[sorted_indices], high_values[sorted_indices]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(labels, high_values - base_profit, left=base_profit, color='lightgreen', label='Positiver Einfluss')
    ax.barh(labels, low_values - base_profit, left=base_profit, color='lightcoral', label='Negativer Einfluss')
    ax.axvline(x=base_profit, color='black', linestyle='--', label=f'Basis-Gewinn ({format_currency(base_profit)})')
    ax.set_xlabel('Gesamtgewinn in €'); ax.set_title('Sensitivitätsanalyse des Gesamtgewinns (+/- 10%)', pad=20)
    ax.legend(); ax.grid(True, which='major', axis='x', linestyle='--')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close(fig)

def create_table_image(df, filename='business_case_annual_breakdown.png'):
    """Erstellt ein Bild mit der detaillierten Jahrestabelle."""
    df_display = df.copy()
    for col in df_display.columns:
        if isinstance(df_display[col].iloc[0], (int, float)):
             if "€" in col:
                 df_display[col] = df_display[col].apply(lambda x: f'{x:,.2f}')
             elif "Einheiten" in col:
                 df_display[col] = df_display[col].apply(lambda x: f'{x:,.0f}')
    
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.axis('off')
    ax.set_title('Detaillierte jährliche Aufschlüsselung', fontsize=16, pad=20)
    
    table = ax.table(cellText=df_display.values, colLabels=df_display.columns, loc='center', cellLoc='left')
    table.set_fontsize(9)
    table.scale(1, 1.8)
    
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#40466e')

    plt.savefig(filename, bbox_inches='tight', dpi=150)
    plt.close(fig)

# ============== BERECHNUNGSFUNKTIONEN ==============
def run_profit_calculation(params, inflation_rate):
    """Berechnet den Gesamtgewinn über 10 Jahre unter Berücksichtigung der Inflation und Verkaufsverzögerung."""
    total_project_cost = (params['effort_rd_hours'] * params['hourly_rate_rd']) + params['other_rd_cost'] + (params['effort_pm_hours'] * params['hourly_rate_pm']) + (params['effort_production_setup_hours'] * params['hourly_rate_production'])
    net_sales_price = params['list_price_per_unit'] * (1 - (params['average_discount'] / 100))
    total_gross_margin = 0
    y1_revenue_factor = max(0, 12 - params['sales_delay_months']) / 12.0

    for i, sales in enumerate(params['unit_sales'].values()):
        inflated_material_cost = params['material_cost_per_unit'] * ((1 + inflation_rate) ** i)
        inflated_prod_cost = (params['production_minutes_per_unit'] / 60) * params['hourly_rate_production'] * ((1 + inflation_rate) ** i)
        current_gross_margin_per_unit = net_sales_price - (inflated_material_cost + inflated_prod_cost)
        if i == 0:
            total_gross_margin += (sales * current_gross_margin_per_unit) * y1_revenue_factor
        else:
            total_gross_margin += sales * current_gross_margin_per_unit
    return total_gross_margin - total_project_cost

def run_scenario_and_sensitivity_analysis(base_params, inflation_rate):
    """Führt Szenario- und Sensitivitätsanalysen durch (mit Inflation)."""
    scenarios, sensitivity_results = {}, {}
    best_params, worst_params = base_params.copy(), base_params.copy()
    best_params['material_cost_per_unit'] *= 0.9; best_params['unit_sales'] = {k: v * 1.15 for k, v in base_params['unit_sales'].items()}
    scenarios['Best-Case'] = run_profit_calculation(best_params, inflation_rate)
    worst_params['material_cost_per_unit'] *= 1.1; worst_params['unit_sales'] = {k: v * 0.85 for k, v in base_params['unit_sales'].items()}
    scenarios['Worst-Case'] = run_profit_calculation(worst_params, inflation_rate)
    vars_to_test = {'Listenpreis': 'list_price_per_unit', 'Materialkosten': 'material_cost_per_unit', 'Absatzmenge': 'unit_sales', 'Produktionszeit': 'production_minutes_per_unit'}
    base_profit = run_profit_calculation(base_params, inflation_rate)
    for label, key in vars_to_test.items():
        low_params, high_params = base_params.copy(), base_params.copy()
        if key == 'unit_sales':
            low_params[key], high_params[key] = {k: v * 0.9 for k, v in base_params[key].items()}, {k: v * 1.1 for k, v in base_params[key].items()}
        else:
            low_params[key], high_params[key] = low_params[key] * 0.9, high_params[key] * 1.1
        low_profit, high_profit = run_profit_calculation(low_params, inflation_rate), run_profit_calculation(high_params, inflation_rate)
        if 'kosten' in label.lower() or 'zeit' in label.lower():
             sensitivity_results[label] = (high_profit, low_profit)
        else:
             sensitivity_results[label] = (low_profit, high_profit)
    return scenarios, sensitivity_results, base_profit

def calculate_target_scenarios(params, target_margin_percent):
    net_sales_price = params['list_price_per_unit'] * (1 - (params['average_discount'] / 100))
    if net_sales_price == 0: return None, None
    target_gm_euros = net_sales_price * (target_margin_percent / 100)
    current_prod_cost = (params['production_minutes_per_unit'] / 60) * params['hourly_rate_production']
    current_material_cost = params['material_cost_per_unit']
    new_material_cost = net_sales_price - current_prod_cost - target_gm_euros
    new_prod_cost = net_sales_price - current_material_cost - target_gm_euros
    new_prod_time = (new_prod_cost / params['hourly_rate_production']) * 60 if params['hourly_rate_production'] > 0 else float('inf')
    cost_buffer = new_material_cost - current_material_cost
    return {'new_material_cost': new_material_cost, 'new_prod_time': new_prod_time}, \
           {'max_material_cost': new_material_cost, 'buffer_euros': cost_buffer}

# ============== HAUPTFUNKTION ==============
def main():
    now = datetime.now()
    creation_time_str = now.strftime("%d.%m.%Y %H:%M:%S")
    start_year = now.year
    INFLATION_RATE = 0.02
    print(f"--- Business Case Rechner (Vollversion) ---\nErstelldatum: {creation_time_str}\n")
    
    creator_name = input("Wer erstellt dieses Dokument? Bitte Namen eingeben: ")
    print()

    target_margins = {'industry': 70, 'portable': 65, 'environmental': 76}
    while True:
        bu_choice = input(f"Für welche Business Unit ist die Analyse? ({', '.join(target_margins.keys())}): ").strip().lower()
        if bu_choice in target_margins:
            target_margin = target_margins[bu_choice]; break
        else: print("Ungültige Eingabe.")
    print(f"Business Unit '{bu_choice.capitalize()}' mit Ziel-Deckungsbeitrag von {target_margin}% ausgewählt.\n")

    while True:
        country = input("Soll in Deutschland oder Italien produziert werden? (deutschland/italien): ").strip().lower()
        if country in ["deutschland", "italien"]:
            hourly_rate_production = 34.22 if country == "deutschland" else 27.80; break
        else: print("Ungültige Eingabe.")
    print(f"Produktionsstundensatz für {country.capitalize()} festgelegt: {hourly_rate_production:.2f} €/h\n")
    hourly_rate_rd, hourly_rate_pm = 67.80, 67.80
    
    print("--- Eingaben für den Business Case ---")
    sales_delay_months = get_numeric_input("1. Erster Verkauf nach Projektstart (Monate): ")
    effort_rd_hours = get_numeric_input("2. F&E-Gesamtaufwand (Stunden): ")
    other_rd_cost = get_numeric_input("3. Sonstige F&E-Kosten (€): ")
    effort_pm_hours = get_numeric_input("4. PM-Gesamtaufwand (Stunden): ")
    effort_production_setup_hours = get_numeric_input("5. Produktions-Setup-Aufwand (Stunden): ")
    list_price_per_unit = get_numeric_input("6. Listenpreis pro Einheit (€): ")
    average_discount = get_numeric_input("7. Durchschnittlicher Rabatt (%): ")
    material_cost_per_unit = get_numeric_input("8. Materialkosten pro Einheit (€): ")
    production_minutes_per_unit = get_numeric_input("9. Produktionsaufwand pro Einheit (Minuten): ")
    print(f"\n10. Jährliche Absatzplanung (beginnend mit {start_year}):")
    unit_sales = {start_year + i: int(get_numeric_input(f"    Verkaufsmenge {start_year + i}: ")) for i in range(10)}
    print("-" * 40 + "\nBerechnung wird durchgeführt...\n" + "-" * 40)

    base_params = {
        'hourly_rate_rd': hourly_rate_rd, 'hourly_rate_pm': hourly_rate_pm, 'hourly_rate_production': hourly_rate_production,
        'effort_rd_hours': effort_rd_hours, 'other_rd_cost': other_rd_cost, 'effort_pm_hours': effort_pm_hours,
        'effort_production_setup_hours': effort_production_setup_hours, 'list_price_per_unit': list_price_per_unit,
        'average_discount': average_discount, 'material_cost_per_unit': material_cost_per_unit,
        'production_minutes_per_unit': production_minutes_per_unit, 'unit_sales': unit_sales,
        'sales_delay_months': sales_delay_months
    }
    
    total_project_cost = (effort_rd_hours * hourly_rate_rd) + other_rd_cost + (effort_pm_hours * hourly_rate_pm) + (effort_production_setup_hours * hourly_rate_production)

    params_for_image = {
        'creator': creator_name, 'creation_time': creation_time_str, 'country': country, 'bu_choice': bu_choice,
        'inflation_rate': INFLATION_RATE, 'sales_delay_months': sales_delay_months,
        'rates': { "F&E Stundensatz:": f"{hourly_rate_rd:.2f} €", "PM Stundensatz:": f"{hourly_rate_pm:.2f} €", "Produktion Stundensatz:": f"{hourly_rate_production:.2f} €" },
        'project_costs': { "F&E-Aufwand:": f"{effort_rd_hours} h", "Sonstige F&E-Kosten:": format_currency(other_rd_cost), "PM-Aufwand:": f"{effort_pm_hours} h", "Produktions-Setup:": f"{effort_production_setup_hours} h" },
        'unit_data': { "Listenpreis:": format_currency(list_price_per_unit), "Rabatt:": f"{average_discount:.1f} %", "Materialkosten:": format_currency(material_cost_per_unit), "Produktionszeit:": f"{production_minutes_per_unit} min" },
        'sales_plan': {f"{year}:": f"{int(sales):,} Stk." for year, sales in unit_sales.items()}
    }
    create_parameters_image(params_for_image)
    print("Info: Eine Zusammenfassung der Parameter wurde als 'business_case_parameter.png' gespeichert.")

    project_cost_y1, project_cost_y2 = total_project_cost * 0.30, total_project_cost * 0.70
    net_sales_price_per_unit = list_price_per_unit * (1 - (average_discount / 100))
    base_production_cost_per_unit = (production_minutes_per_unit / 60) * hourly_rate_production
    
    gross_margin_per_unit_y1 = net_sales_price_per_unit - (material_cost_per_unit + base_production_cost_per_unit)
    gross_margin_percentage_y1 = (gross_margin_per_unit_y1 / net_sales_price_per_unit) * 100 if net_sales_price_per_unit > 0 else 0

    results, cumulative_net_profit = [], 0
    payback_period_details, is_payback_calculated = "Nicht innerhalb von 10 Jahren", False
    y1_revenue_factor = max(0, 12 - sales_delay_months) / 12.0
    
    for i, (year, annual_sales_units) in enumerate(unit_sales.items()):
        old_cumulative_profit = cumulative_net_profit
        inflated_material_cost = material_cost_per_unit * ((1 + INFLATION_RATE) ** i)
        inflated_prod_cost = base_production_cost_per_unit * ((1 + INFLATION_RATE) ** i)
        gross_margin_per_unit = net_sales_price_per_unit - (inflated_material_cost + inflated_prod_cost)
        annual_gross_margin = annual_sales_units * gross_margin_per_unit
        if i == 0:
            annual_gross_margin *= y1_revenue_factor
        
        if i == 0: project_cost_annual = project_cost_y1
        elif i == 1: project_cost_annual = project_cost_y2
        else: project_cost_annual = 0
        annual_net_profit = annual_gross_margin - project_cost_annual
            
        cumulative_net_profit += annual_net_profit
        
        results.append({
            "Jahr": year, "Verkaufte Einheiten": annual_sales_units,
            "Umsatz p.E. (€)": net_sales_price_per_unit, "Materialkosten p.E. (€)": inflated_material_cost,
            "Produktionskosten p.E. (€)": inflated_prod_cost, "DB p.E. (€)": gross_margin_per_unit,
            "Gesamt DB (€)": annual_gross_margin, "Projektkosten-Anteil (€)": project_cost_annual,
            "Jährl. Nettogewinn (€)": annual_net_profit, "Kum. Nettogewinn (€)": cumulative_net_profit
        })
        
        if not is_payback_calculated and cumulative_net_profit > 0:
            profit_this_year = cumulative_net_profit - old_cumulative_profit
            needed_to_break_even = -old_cumulative_profit
            if profit_this_year > 0:
                months, years_passed = round((needed_to_break_even / profit_this_year) * 12), i
                if months >= 12: years_passed += 1; months = 0
                payback_period_details, is_payback_calculated = f"{years_passed} Jahre und {months} Monate", True

    df_details = pd.DataFrame(results)
    final_net_profit = df_details["Kum. Nettogewinn (€)"].iloc[-1]
    
    scenarios, sensitivity_data, base_profit_for_tornado = run_scenario_and_sensitivity_analysis(base_params, INFLATION_RATE)
    break_even_units_total = total_project_cost / gross_margin_per_unit_y1 if gross_margin_per_unit_y1 > 0 else float('inf')
    
    acceptable_margin = target_margin * 0.95
    if gross_margin_percentage_y1 >= target_margin: ziel_erreicht_text = "ZIEL ERREICHT"
    elif gross_margin_percentage_y1 >= acceptable_margin: ziel_erreicht_text = "AKZEPTABEL"
    else: ziel_erreicht_text = "ZIEL VERFEHLT"
    
    print(f"\n--- Deckungsbeitrags-Analyse (Business Unit: {bu_choice.capitalize()}) ---")
    print(f"Errechneter DB1 ({start_year}): {format_currency(gross_margin_per_unit_y1)} ({gross_margin_percentage_y1:.2f} %) | Ziel-DB1: {target_margin:.2f} %  ►  {ziel_erreicht_text}\n")
    
    opt_scenarios, cost_buffer_scenario = None, None
    if ziel_erreicht_text == "ZIEL VERFEHLT":
        opt_scenarios, _ = calculate_target_scenarios(base_params, target_margin)
        if opt_scenarios:
            print(f"--- ZIEL VERFEHLT: Optimierungs-Szenarien (Basis {start_year}) ---")
            print(f"1. Nur Materialkosten senken auf: {format_currency(opt_scenarios['new_material_cost'])}")
            print(f"2. Nur Produktionszeit senken auf: {opt_scenarios['new_prod_time']:.1f} min/Stk.\n")
    elif ziel_erreicht_text in ["ZIEL ERREICHT", "AKZEPTABEL"]:
        _, cost_buffer_scenario = calculate_target_scenarios(base_params, target_margin)
        if cost_buffer_scenario and cost_buffer_scenario['buffer_euros'] > 0:
            print(f"--- ZIEL ERREICHT/AKZEPTABEL: Puffer-Analyse (Basis {start_year}) ---")
            print(f"Die Materialkosten könnten um {format_currency(cost_buffer_scenario['buffer_euros'])} auf bis zu {format_currency(cost_buffer_scenario['max_material_cost'])} steigen, bevor das Ziel verfehlt wird.\n")
    
    create_table_image(df_details)
    print("Info: Die detaillierte Aufschlüsselung wurde als 'business_case_annual_breakdown.png' gespeichert.\n")
            
    kpis_for_chart = {
        'projektkosten': format_currency(total_project_cost), 'db_einheit': format_currency(gross_margin_per_unit_y1), 
        'db_prozent': gross_margin_percentage_y1, 'nettogewinn': format_currency(final_net_profit), 
        'payback': payback_period_details, 'break_even_total': break_even_units_total, 
        'best_case': format_currency(scenarios['Best-Case']), 'worst_case': format_currency(scenarios['Worst-Case']), 
        'bu_choice': bu_choice.capitalize(), 'target_margin': target_margin, 
        'opt_scenarios': opt_scenarios, 'cost_buffer': cost_buffer_scenario, 'start_year': start_year
    }
    
    create_main_analysis_chart(df_details, kpis_for_chart)
    create_cost_structure_charts({'F&E': (effort_rd_hours * hourly_rate_rd) + other_rd_cost, 'PM': (effort_pm_hours * hourly_rate_pm), 'Produktions-Setup': (effort_production_setup_hours * hourly_rate_production)}, {'Material': material_cost_per_unit, 'Produktionskosten': base_production_cost_per_unit})
    create_tornado_chart(sensitivity_data, base_profit_for_tornado)
    print("--- Grafische Auswertung ---")
    print("Die Analyse wurde erfolgreich in 5 Bilddateien gespeichert.")

if __name__ == '__main__':
    main()