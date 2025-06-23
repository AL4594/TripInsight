# Script de préparation pour PCA + clustering + export Pickle

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import joblib
import os

# Création du dossier de sortie
os.makedirs("models", exist_ok=True)

# 1. Charger les données
input_path = "data/Trip.csv"
df = pd.read_csv(input_path)

# 2. Sélectionner les colonnes numériques pertinentes
features = ['nature', 'adventure', 'nightlife', 'seclusion', 'cuisine', 'culture', 'beaches', 'wellness']
X = df[features].copy()

# 3. Standardisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. PCA (2 composantes)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# 5. Clustering (facultatif)
kmeans = KMeans(n_clusters=5, random_state=42)
kmeans.fit(X_pca)

# 6. Ajouter les résultats au DataFrame
city_data = df.copy()
city_data['PC1'] = X_pca[:, 0]
city_data['PC2'] = X_pca[:, 1]
city_data['cluster'] = kmeans.predict(X_pca)

# 7. Sauvegardes
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(pca, "models/pca.pkl")
joblib.dump(kmeans, "models/kmeans.pkl")
city_data.to_csv("models/city_data.csv", index=False)

print("Tous les fichiers ont été sauvegardés dans le dossier 'models'")
