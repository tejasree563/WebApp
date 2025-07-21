from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import logging
import os

# ------------------- App Initialization -------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ------------------- Load Model -------------------
try:
    model = joblib.load("random_forest_churn_model.pkl")
    logging.info("Model loaded successfully.")
except FileNotFoundError:
    logging.error("Model file not found.")
    raise RuntimeError("Model file not found.")

# ------------------- Helper Function -------------------
def preprocess_input(data):
    df = pd.DataFrame([data])
    categorical_cols = ['Gender', 'Membership_Status', 'Preferred_Payment_Method', 'Region']
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # Align with model columns
    required_columns = model.feature_names_in_
    df = df.reindex(columns=required_columns, fill_value=0)
    return df

# ------------------- Web Route -------------------
@app.route("/", methods=["GET", "POST"])
def predict_web():
    prediction = None
    if request.method == "POST":
        try:
            # Get form inputs
            user_input = {
                "Age": int(request.form["Age"]),
                "Gender": request.form["Gender"],
                "Annual_Income_USD": float(request.form["Annual_Income_USD"]),
                "Spending_Score": int(request.form["Spending_Score"]),
                "Membership_Status": request.form["Membership_Status"],
                "Preferred_Payment_Method": request.form["Preferred_Payment_Method"],
                "Region": request.form["Region"],
                "Total_Purchases": int(request.form["Total_Purchases"]),
                "Avg_Purchase_Value": float(request.form["Avg_Purchase_Value"]),
                "Satisfaction_Score": float(request.form["Satisfaction_Score"]),
                "Website_Visits_Last_Month": int(request.form["Website_Visits_Last_Month"]),
                "Avg_Time_Per_Visit_Minutes": float(request.form["Avg_Time_Per_Visit_Minutes"]),
                "Support_Tickets_Last_6_Months": int(request.form["Support_Tickets_Last_6_Months"]),
                "Referred_Friends": int(request.form["Referred_Friends"]),
            }

            processed_input = preprocess_input(user_input)
            pred = model.predict(processed_input)[0]
            prediction = "Will Churn" if pred == 1 else "Will Not Churn"

        except Exception as e:
            logging.error("Error during prediction: %s", str(e))
            prediction = "Error in input or model. Please check logs."

    return render_template("index.html", prediction=prediction)

# ------------------- API Route -------------------
@app.route("/api/predict", methods=["POST"])
def predict_api():
    try:
        input_data = request.get_json()
        processed_input = preprocess_input(input_data)
        pred = model.predict(processed_input)[0]
        result = "Will Churn" if pred == 1 else "Will Not Churn"
        return jsonify({"prediction": result})
    except Exception as e:
        logging.error("API prediction error: %s", str(e))
        return jsonify({"error": "Prediction failed"}), 500

# ------------------- Run App -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


