from flask import Flask, render_template_string, request, send_file, redirect, url_for, flash
import requests
import ijson
import csv
from datetime import datetime, timedelta, timezone
import tempfile
import os
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for flash messages

timestamp = time.strftime("%Y%m%d-%H%M%S")

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwOTg2ZjFlYWMwZDE0MzUxODViZWFiNzM0NzFlMDIyYyIsImlhdCI6MTc1MDU1OTIzOCwiZXhwIjoyMDY1OTE5MjM4fQ.rIpdWW9wT67z6QDuCZ8DeAMOS1hTO7n3BhOeLkAN3No"
BASE_URL = "https://kbckyasands.myatessmon.com"

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Entity Data Export</title>
  <!-- jQuery -->
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <!-- Select2 CSS -->
  <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
  <!-- Select2 JS -->
  <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    .select2-container { width: 400px !important; }
    label { display: block; margin-top: 1rem; margin-bottom: 0.5rem; }
  </style>
</head>
<body>
  <h2>Select Entity & Export Data</h2>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <ul style="color:red;">
        {% for msg in messages %}
          <li>{{ msg }}</li>
        {% endfor %}
      </ul>
    {% endif %}
  {% endwith %}
  <form method="POST" action="/export">
    <label for="entity">Entity:</label>
    <select id="entity" name="entity" required>
      <option value="" disabled selected>Select entity...</option>
      {% for e in entities %}
        <option value="{{ e }}">{{ e }}</option>
      {% endfor %}
    </select>

    <label for="start_date">Start Date:</label>
    <input type="date" id="start_date" name="start_date" required>

    <label for="start_time">Start Time (HH:MM:SS):</label>
    <input type="time" step="1" id="start_time" name="start_time" value="00:00:00" required>

    <label for="end_date">End Date:</label>
    <input type="date" id="end_date" name="end_date" required>

    <label for="end_time">End Time (HH:MM:SS):</label>
    <input type="time" step="1" id="end_time" name="end_time" value="23:59:59" required>

    <label for="interval">Interval (minutes):</label>
    <input type="number" id="interval" name="interval" min="1" value="30" required>

    <br><br>
    <button type="submit">Export CSV</button>
  </form>

<script>
  $(document).ready(function() {
    $('#entity').select2({
      placeholder: "Select entity...",
      allowClear: true
    });
  });
</script>
</body>
</html>
"""

def fetch_entities():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.get(f"{BASE_URL}/api/states", headers=headers, timeout=15)
    resp.raise_for_status()
    entities = [item["entity_id"] for item in resp.json()]
    return sorted(entities)

@app.route("/", methods=["GET"])
def index():
    try:
        entities = fetch_entities()
    except Exception as e:
        entities = []
        flash(f"Failed to load entities: {e}")
    return render_template_string(HTML, entities=entities)

@app.route("/export", methods=["POST"])
def export():
    entity = request.form.get("entity")
    start_date = request.form.get("start_date")
    start_time = request.form.get("start_time")
    end_date = request.form.get("end_date")
    end_time = request.form.get("end_time")
    interval_min = request.form.get("interval")

    if not all([entity, start_date, start_time, end_date, end_time, interval_min]):
        flash("All fields are required.")
        return redirect(url_for("index"))

    try:
        interval_min = int(interval_min)
        start_dt = datetime.fromisoformat(f"{start_date}T{start_time}").replace(tzinfo=timezone.utc)
        end_dt = datetime.fromisoformat(f"{end_date}T{end_time}").replace(tzinfo=timezone.utc)
    except Exception as e:
        flash(f"Invalid date/time or interval: {e}")
        return redirect(url_for("index"))

    if end_dt < start_dt:
        flash("End datetime must be after start datetime.")
        return redirect(url_for("index"))

    output_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    output_csv_name = output_csv.name
    output_csv.close()

    # Write CSV header
    with open(output_csv_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "state", "unit"])

    cur_day = start_dt.date()
    end_day = end_dt.date()

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    while cur_day <= end_day:
        next_day = cur_day + timedelta(days=1)
        # Construct URL for the day range
        url = (f"{BASE_URL}/api/history/period/"
               f"{cur_day}T00:00:00Z?filter_entity_id={entity}&end_time={next_day}T00:00:00Z")

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.content
        except Exception as e:
            flash(f"Failed to fetch data for {cur_day}: {e}")
            return redirect(url_for("index"))

        # Parse JSON using ijson
        parsed = []
        unit = None
        try:
            import io
            f = io.BytesIO(data)
            items = ijson.items(f, 'item.item')
            for entry in items:
                try:
                    ts = datetime.fromisoformat(entry["last_changed"].replace("Z", "+00:00"))
                    value = float(entry["state"])
                    parsed.append((ts, value))
                    if not unit and "unit_of_measurement" in entry["attributes"]:
                        unit = entry["attributes"]["unit_of_measurement"]
                except Exception:
                    pass
        except Exception as e:
            flash(f"Error parsing JSON: {e}")
            return redirect(url_for("index"))

        parsed.sort()
        result = []
        cur_time = datetime.combine(cur_day, datetime.min.time()).replace(tzinfo=timezone.utc)
        last_value = None
        i = 0
        interval = timedelta(minutes=interval_min)

        day_end_time = datetime.combine(next_day, datetime.min.time()).replace(tzinfo=timezone.utc)
        while cur_time < day_end_time and cur_time <= end_dt:
            while i < len(parsed) and parsed[i][0] <= cur_time:
                last_value = parsed[i][1]
                i += 1
            if cur_time >= start_dt:
                result.append((cur_time.isoformat(), last_value))
            cur_time += interval

        # Append results to CSV
        with open(output_csv_name, "a", newline="") as f:
            writer = csv.writer(f)
            for row in result:
                writer.writerow([row[0], row[1], unit])

        cur_day = next_day

    return send_file(output_csv_name,
                     as_attachment=True,
                     download_name=f"{entity.replace('.', '_')}_{timestamp}.csv",
                     mimetype="text/csv")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

