from flask import Flask, render_template_string, request, jsonify
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins for public API access

# Database configuration
DATABASE_PATH = "database.db"

def init_database():
    """Initialize the database if it doesn't exist"""
    if not os.path.exists(DATABASE_PATH):
        conn = sqlite3.connect(DATABASE_PATH)
        conn.close()
        print(f"Database created: {DATABASE_PATH}")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

# Initialize database on startup
init_database()

# Embedded HTML for the query dashboard
QUERY_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Query Tool</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .query-form {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .result-table {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .sql-input {
            font-family: 'Courier New', monospace;
            min-height: 100px;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">Database Query Tool</h1>
                
                <!-- Query Form -->
                <div class="query-form">
                    <form method="POST" action="/query">
                        <div class="mb-3">
                            <label for="query" class="form-label">SQL Query:</label>
                            <textarea 
                                class="form-control sql-input" 
                                id="query" 
                                name="query" 
                                rows="4" 
                                placeholder="Enter your SQL query here...">{% if request.form.get('query') %}{{ request.form.get('query') }}{% endif %}</textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Execute Query</button>
                        <a href="/" class="btn btn-secondary">Back to Dashboard</a>
                    </form>
                </div>

                <!-- Messages -->
                {% if message %}
                <div class="alert alert-success" role="alert">
                    {{ message }}
                </div>
                {% endif %}

                {% if error %}
                <div class="alert alert-danger" role="alert">
                    <strong>Error:</strong> {{ error }}
                </div>
                {% endif %}

                <!-- Results Table -->
                {% if result and columns %}
                <div class="result-table">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover mb-0">
                            <thead class="table-dark">
                                <tr>
                                    {% for column in columns %}
                                    <th>{{ column }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in result %}
                                <tr>
                                    {% for column in columns %}
                                    <td>{{ row[column] }}</td>
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endif %}

                <!-- Sample Queries -->
                <div class="mt-4">
                    <h5>Sample Queries:</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h6 class="card-title">Create Table</h6>
                                    <code class="small">CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);</code>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h6 class="card-title">Insert Data</h6>
                                    <code class="small">INSERT INTO users (name, email) VALUES ('John', 'john@example.com');</code>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h6 class="card-title">Select Data</h6>
                                    <code class="small">SELECT * FROM users;</code>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h6 class="card-title">Show Tables</h6>
                                    <code class="small">SELECT name FROM sqlite_master WHERE type='table';</code>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
      
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Just redirect to /query for simplicity
    return query_dashboard()

@app.route("/query", methods=["GET", "POST"])
def query_dashboard():
    """Web form for SQL query execution"""
    result = None
    error = None
    columns = []
    message = ""

    if request.method == "POST":
        query = request.form.get("query")
        
        if query:
            try:
                conn = get_db_connection()
                cursor = conn.execute(query)
                
                if cursor.description:  # SELECT-type queries
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [dict(row) for row in rows]  # Convert to list of dicts
                else:
                    conn.commit()
                    message = "✅ Query executed successfully (no result set)"
                
                conn.close()
            except Exception as e:
                error = str(e)
                print(f"Query error: {error}")
        else:
            error = "Please enter a SQL query"

    return render_template_string(
        QUERY_DASHBOARD_HTML,
        result=result,
        columns=columns,
        error=error,
        message=message,
        request=request
    )

@app.route("/run-sql", methods=["POST"])
def run_sql():
    """API endpoint for SQL query execution"""
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.execute(query)
        
        if cursor.description:  # SELECT-like query
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            conn.close()
            return jsonify({"results": result})
        else:  # INSERT/UPDATE/DELETE/etc
            conn.commit()
            conn.close()
            return jsonify({"message": "Query executed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/metadata")
def api_metadata():
    """Get database metadata"""
    try:
        conn = get_db_connection()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "database": DATABASE_PATH,
            "tables": tables,
            "message": "Database metadata retrieved successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api_documentation")
def api_documentation():
    """API documentation page"""
    return "<h1>API Documentation</h1><p>Use /run-sql (POST) to run SQL queries. Use /api/metadata to get DB info.</p>"

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)