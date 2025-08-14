import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
from plotly import subplots
import plotly.graph_objects as go
import datetime

# Kreiert eine Instanz von tkinter
root = tk.Tk()
root.withdraw()

# öffnet den Explorer und die gewünschte Datei kann ausgewählt werden
file_path = filedialog.askopenfilename()
file_name = file_path.rsplit('/')[-1].rsplit('.')[0]

# Einlesen der Datei mit Kopfzeile
file_raw = pd.read_csv(file_path, sep=";", header=0)

# Prüfen, ob die Spalte "AT" existiert
if "AT" not in file_raw.columns:
    print("Spalte 'AT' nicht gefunden. Bitte prüfen Sie die Datei.")
    exit()

# Extrahieren der relevanten Spalten
# Annahme: "Seriennummer", "Montagedatum", Spalte 42 (Leistung), "AT" (Strom)
maes_file = file_raw.loc[:, ["Seriennummer", "Montagedatum", file_raw.columns[41], "AT"]]

# Seriennummern und Montagedaten extrahieren
serial_nr = maes_file.iloc[:, 0].astype(str).values.tolist()
test_dates_raw = maes_file.iloc[:, 1].astype(str).values.tolist()
test_dates = [datetime.datetime.strptime(element, '%Y%m%d').strftime('%d.%m.%Y') for element in test_dates_raw]

# Messdaten extrahieren
power_maes = maes_file.iloc[:, 2].to_numpy()
current_maes = maes_file.iloc[:, 3].to_numpy()

# Schreiben von Metadaten in ein Array
meta_data = np.stack((test_dates, serial_nr, power_maes, current_maes), axis=-1)

# Berechnung von Mittelwert und Standardabweichung
power_mean = np.mean(power_maes)
current_mean = np.mean(current_maes)

power_std = np.std(power_maes)
current_std = np.std(current_maes)

# Grenzwerte nach Shewhart (±3σ)
power_upper_boundry = power_mean + 3 * power_std
power_lower_boundry = power_mean - 3 * power_std

current_upper_boundry = current_mean + 3 * current_std
current_lower_boundry = current_mean - 3 * current_std

# Visualisierung
fig = subplots.make_subplots(rows=2, subplot_titles=("Leistungsmessungen", "Strommessungen (AT)"),
                             shared_xaxes=True, vertical_spacing=0.15)

# Scatterplots
fig.add_trace(go.Scatter(y=power_maes,
                         mode='markers',
                         marker_color='blue',
                         name='Leistungsmessung',
                         customdata=meta_data),
              row=1, col=1)

fig.add_trace(go.Scatter(y=current_maes,
                         mode='markers',
                         marker_color='green',
                         name='Strommessung (AT)',
                         customdata=meta_data),
              row=2, col=1)

# Hover-Information
hover_text = "<br>".join([
    "Pruefdatum: %{customdata[0]}",
    "Serialnummer: %{customdata[1]}",
    "Leistungsmesswert: %{customdata[2]}W",
    "Strommesswert: %{customdata[3]}A"
])

fig.update_traces(hovertemplate=hover_text, row=1, col=1)
fig.update_traces(hovertemplate=hover_text, row=2, col=1)
fig.update_xaxes(showspikes=True, spikemode="across", spikecolor='black', spikethickness=1)

# Grenzlinien
fig.add_hline(y=power_upper_boundry, line_width=3, line_color="red",
              annotation_text=f"Oberer Grenzwert = {power_upper_boundry:.0f}W",
              annotation_position="top right",
              annotation=dict(font_weight="bold"),
              row=1, col=1)

fig.add_hline(y=power_lower_boundry, line_width=3, line_color="red",
              annotation_text=f"Unterer Grenzwert = {power_lower_boundry:.0f}W",
              annotation_position="bottom right",
              annotation=dict(font_weight="bold"),
              row=1, col=1)

fig.add_hline(y=current_upper_boundry, line_width=3, line_color="red",
              annotation_text=f"Oberer Grenzwert = {current_upper_boundry:.1f}A",
              annotation_position="top right",
              annotation=dict(font_weight="bold"),
              row=2, col=1)

fig.add_hline(y=current_lower_boundry, line_width=3, line_color="red",
              annotation_text=f"Unterer Grenzwert = {current_lower_boundry:.1f}A",
              annotation_position="bottom right",
              annotation=dict(font_weight="bold"),
              row=2, col=1)

# Schattierte Grenzbereiche
fig.add_hrect(y0=power_upper_boundry, y1=1000000, line_width=0, fillcolor="red", opacity=0.1, row=1, col=1)
fig.add_hrect(y0=0, y1=power_lower_boundry, line_width=0, fillcolor="red", opacity=0.1, row=1, col=1)

fig.add_hrect(y0=current_upper_boundry, y1=1000000, line_width=0, fillcolor="red", opacity=0.1, row=2, col=1)
fig.add_hrect(y0=0, y1=current_lower_boundry, line_width=0, fillcolor="red", opacity=0.1, row=2, col=1)

# Achsenbeschriftung und Bereich
fig.update_xaxes(title_text="Nummer der Messung", range=[-5, len(power_maes)+5], row=1, col=1)
fig.update_yaxes(title_text="Leistung [W]",
                 range=[power_lower_boundry - 0.2 * abs(power_lower_boundry),
                        power_upper_boundry + 0.2 * abs(power_upper_boundry)],
                 row=1, col=1)

fig.update_xaxes(title_text="Nummer der Messung", range=[-5, len(current_maes)+5], row=2, col=1)
fig.update_yaxes(title_text="Stromstärke [A]",
                 range=[current_lower_boundry - 0.2 * abs(current_lower_boundry),
                        current_upper_boundry + 0.2 * abs(current_upper_boundry)],
                 row=2, col=1)

# Dokumentationslink
fig.add_annotation(text="Dokumentation siehe Confluence (<a href='https://trumpf.atlassian.net/wiki/spaces/TCHPT/pages/611649253/Grenzwerte+f+r+Endpr+fung'>link</a>)",
                   xref="paper", yref="paper",
                   x=0.05, y=0.05, showarrow=False)

# Anzeige der Grafik
fig.show()
