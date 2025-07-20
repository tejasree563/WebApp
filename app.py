from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load the trained model
model = joblib.load("random_forest_churn_model.pkl")

@app.route("/", methods=["GET", "POST"])
def predict():
    prediction = None
    if request.method == "POST":
        # Capture form inputs
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

        # Convert to DataFrame
        input_df = pd.DataFrame([user_input])

        # One-hot encoding to match training
        categorical_columns = ['Gender', 'Membership_Status', 'Preferred_Payment_Method', 'Region']
        input_df = pd.get_dummies(input_df, columns=categorical_columns, drop_first=True)

        # Add any missing columns with 0 (needed for unseen categories)
        required_columns = model.feature_names_in_
        for col in required_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[required_columns]

        # Make prediction
        pred = model.predict(input_df)[0]
        prediction = "Will Churn" if pred == 1 else "Will Not Churn"

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
