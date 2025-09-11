import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

class SelfLearningAI:
    def __init__(self):
        self.model = LinearRegression()

    def load_data(self, filepath):
        """Load data from a CSV file."""
        self.data = pd.read_csv(filepath)
        self.features = self.data.iloc[:, :-1].values  # All columns except the last one
        self.target = self.data.iloc[:, -1].values     # Last column as target variable
        self.feature_count = self.features.shape[1]
        return {"rows": len(self.data), "features": self.feature_count}

    def train_model(self):
        """Train the model on the data."""
        X_train, X_test, y_train, y_test = train_test_split(self.features, self.target, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        return {"mse": mse}

    def save_model(self, filename):
        """Save the trained model to a file."""
        joblib.dump(self.model, filename)
        return {"filename": filename}

    def load_model(self, filename):
        """Load a trained model from a file."""
        self.model = joblib.load(filename)
        return {"filename": filename}

    def predict(self, input_data):
        """Make predictions based on new input data."""
        input_array = np.array(input_data).reshape(1, -1)
        prediction = self.model.predict(input_array)[0]
        return {"prediction": float(prediction)}

# Create an instance of the AI
ai = SelfLearningAI()

# API endpoints
@app.route('/upload', methods=['POST'])
def upload_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    # Save the file temporarily
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)
    
    # Process the data
    try:
        result = ai.load_data(temp_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/train', methods=['POST'])
def train_model():
    try:
        result = ai.train_model()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if not data or 'input' not in data:
        return jsonify({"error": "No input data provided"}), 400
    
    try:
        result = ai.predict(data['input'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save-model', methods=['POST'])
def save_model():
    data = request.json
    if not data or 'filename' not in data:
        return jsonify({"error": "No filename provided"}), 400
    
    try:
        result = ai.save_model(data['filename'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load-model', methods=['POST'])
def load_model():
    data = request.json
    if not data or 'filename' not in data:
        return jsonify({"error": "No filename provided"}), 400
    
    try:
        result = ai.load_model(data['filename'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
