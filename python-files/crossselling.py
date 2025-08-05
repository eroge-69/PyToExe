from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from google.oauth2 import service_account
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Ruta al archivo de credenciales
credentials_path = 'credentials.json'

# Inicializar cliente de GA4
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = BetaAnalyticsDataClient(credentials=credentials)

# Configurar solicitud a GA4
property_id = '284680893'
request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[
        Dimension(name="pagePath"),
        Dimension(name="pagePathPlusQueryString"),
        Dimension(name="pageReferrer"),
        Dimension(name="pageLocation"),
        Dimension(name="sessionSourceMedium"),
    ],
    metrics=[
        Metric(name="screenPageViews"),
        Metric(name="activeUsers"),
        Metric(name="newUsers"),
        Metric(name="screenPageViewsPerUser"),
        Metric(name="eventCount")
    ],
    date_ranges=[DateRange(start_date="30daysAgo", end_date="today")]
)

# Ejecutar reporte
response = client.run_report(request)

# Preparar datos para Google Sheets
headers = [header.name for header in list(response.dimension_headers)] + [header.name for header in list(response.metric_headers)]
rows = []
for row in response.rows:
    row_data = [dim.value for dim in row.dimension_values] + [met.value for met in row.metric_values]
    rows.append(row_data)

# Conectar con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
sheet_credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
gc = gspread.authorize(sheet_credentials)

# Abrir hoja y actualizar
spreadsheet = gc.open_by_key("14HwFA9Pv1NpQonjdCRsMQcbhRtAlDcZmdxXbWU2W5mM")
worksheet = spreadsheet.worksheet("Cross-selling2.0")

worksheet.clear()
worksheet.update([headers] + rows)


print("✅ Google Sheet actualizado con datos de GA4.")


