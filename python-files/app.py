from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load trained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Dropdown options
sex_options = {0: "Female", 1: "Male"}
cp_options = {0: "Typical Angina", 1: "Atypical Angina", 2: "Non-anginal Pain", 3: "Asymptomatic"}
fbs_options = {0: "False (<= 120 mg/dl)", 1: "True (> 120 mg/dl)"}
restecg_options = {0: "Normal", 1: "ST-T Wave Abnormality", 2: "Left Ventricular Hypertrophy"}
exang_options = {0: "No", 1: "Yes"}
slope_options = {0: "Upsloping", 1: "Flat", 2: "Downsloping"}
ca_options = {0: "0", 1: "1", 2: "2", 3: "3"}
thal_options = {1: "Normal", 2: "Fixed Defect", 3: "Reversible Defect"}

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    probability = None
    input_data = {}

    if request.method == "POST":
        if "clear" in request.form:
            input_data = {}
        elif "predict" in request.form:
            try:
                # Collect inputs
                input_data = request.form.to_dict()

                features = [
                    float(request.form.get("age", 0)),
                    int(request.form.get("sex", 0)),
                    int(request.form.get("cp", 0)),
                    float(request.form.get("trestbps", 0)),
                    float(request.form.get("chol", 0)),
                    int(request.form.get("fbs", 0)),
                    int(request.form.get("restecg", 0)),
                    float(request.form.get("thalach", 0)),
                    int(request.form.get("exang", 0)),
                    float(request.form.get("oldpeak", 0)),
                    int(request.form.get("slope", 0)),
                    int(request.form.get("ca", 0)),
                    int(request.form.get("thal", 1))
                ]

                features = np.array(features).reshape(1, -1)

                prob = model.predict_proba(features)[0][1]
                prediction = "High Risk" if prob > 0.6 else "Low Risk"
                probability = round(prob * 100, 2)

            except Exception as e:
                prediction = f"Error: {str(e)}"

    return render_template(
        "index.html",
        sex_options=sex_options,
        cp_options=cp_options,
        fbs_options=fbs_options,
        restecg_options=restecg_options,
        exang_options=exang_options,
        slope_options=slope_options,
        ca_options=ca_options,
        thal_options=thal_options,
        input_data=input_data,
        prediction=prediction,
        probability=probability
    )


if __name__ == "__main__":
    app.run(debug=True)
