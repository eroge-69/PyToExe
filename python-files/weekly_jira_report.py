import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- Configuration (Replace with your actual values) ---
jira_domain = "https://yourcompany.atlassian.net"
jira_email = "your.email@company.com"
jira_api_token = "your_api_token"
assignee = "your.email@company.com"

smtp_server = "smtp.yourcompany.com"
smtp_port = 587
smtp_username = "your.email@company.com"
smtp_password = "your_email_password"
recipient_email = "your.email@company.com"

# --- Date Range: Last Thursday to This Thursday ---
today = datetime.now()
last_thursday = today - timedelta(days=(today.weekday() - 3) % 7 + 7)
this_thursday = last_thursday + timedelta(days=7)
start_date = last_thursday.strftime("%Y-%m-%d")
end_date = this_thursday.strftime("%Y-%m-%d")

# --- JQL Query using statusCategoryChangedDate ---
jql = (
    f'assignee = "{assignee}" AND '
    f'type in (Story, Epic) AND '
    f'statusCategoryChangedDate >= "{start_date}" AND '
    f'statusCategoryChangedDate <= "{end_date}" AND '
    f'statusCategory = Done '
    f'ORDER BY statusCategoryChangedDate DESC'
)

# --- Jira API Request ---
url = f"{jira_domain}/rest/api/3/search"
headers = {"Accept": "application/json"}
auth = (jira_email, jira_api_token)
params = {
    "jql": jql,
    "fields": "key,status,summary,assignee",
    "maxResults": 50
}

response = requests.get(url, headers=headers, auth=auth, params=params)
issues = response.json().get("issues", [])

# --- Format HTML Table ---
html_table = "<h3>Completed Stories (Last Thursday to This Thursday)</h3>"
html_table += "<table border='1' cellpadding='5' cellspacing='0'>"
html_table += "<tr><th>Story ID</th><th>Status</th><th>Title</th><th>Assignee</th></tr>"

for issue in issues:
    key = issue["key"]
    status = issue["fields"]["status"]["name"]
    title = issue["fields"]["summary"]
    assignee_name = issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned"
    html_table += f"<tr><td>{key}</td><td>{status}</td><td>{title}</td><td>{assignee_name}</td></tr>"

html_table += "</table>"

# --- Send Email ---
msg = MIMEMultipart("alternative")
msg["Subject"] = "Weekly Jira Report - Completed Stories"
msg["From"] = smtp_username
msg["To"] = recipient_email
msg.attach(MIMEText(html_table, "html"))

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, recipient_email, msg.as_string())

print("Email sent successfully.")
