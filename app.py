from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import joblib
import os

# Load models and data once
scaler = joblib.load("models/scaler.pkl")
pca = joblib.load("models/pca.pkl")
kmeans = joblib.load("models/kmeans.pkl")
city_data = pd.read_csv("models/city_data.csv")  # Must include PC1, PC2

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")  # optional UI

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.json  # Expected as JSON
        user_df = pd.DataFrame([user_input])[scaler.feature_names_in_]

        user_scaled = scaler.transform(user_df)
        user_pca = pca.transform(user_scaled)

        city_data['distance'] = np.linalg.norm(
            city_data[['PC1', 'PC2']].values - user_pca, axis=1
        )

        top = city_data.sort_values(by='distance').head(5)
        return jsonify(top[['city', 'country', 'distance']].to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
