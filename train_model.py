# =============================================
#  Smart Diet Planner - Random Forest Model Training
# =============================================

import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# ---------------------------------------------
# 1. Setup paths
# ---------------------------------------------
DATA_PATH = "data/synthetic_diet_dataset_encoded.csv"
MODEL_DIR = "model"
MODEL_FILE = os.path.join(MODEL_DIR, "diet_model.pkl")
SCALER_FILE = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_FILE = os.path.join(MODEL_DIR, "meal_encoder.pkl")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------------------------------------
# 2. Load Dataset
# ---------------------------------------------
print("📂 Loading dataset...")
df = pd.read_csv(DATA_PATH)

# Handle missing values
df.replace("", np.nan, inplace=True)
df.fillna(df.mean(numeric_only=True), inplace=True)

# ---------------------------------------------
# 3. Encode categorical columns if present
# ---------------------------------------------
if "gender" in df.columns:
    df["gender"] = LabelEncoder().fit_transform(df["gender"].astype(str))

if "chronic_disease" in df.columns:
    df["chronic_disease"] = LabelEncoder().fit_transform(df["chronic_disease"].astype(str))

# ---------------------------------------------
# 4. Split features and target
# ---------------------------------------------
X = df.drop(["Meal_Plan", "Meal_Plan_Encoded"], axis=1)
y = df["Meal_Plan_Encoded"]

# Encode target labels
meal_encoder = LabelEncoder()
y = meal_encoder.fit_transform(y)

# Save target encoder for Flask app
joblib.dump(meal_encoder, ENCODER_FILE)

# ---------------------------------------------
# 5. Train-test split
# ---------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------------------------------
# 6. Feature scaling
# ---------------------------------------------
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
joblib.dump(scaler, SCALER_FILE)

# ---------------------------------------------
# 7. Train Random Forest model
# ---------------------------------------------
print("🌲 Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=120,       # Number of trees
    max_depth=12,           # Limit depth to prevent overfitting
    class_weight="balanced",
    random_state=42
)
model.fit(X_train, y_train)

# ---------------------------------------------
# 8. Evaluate model
# ---------------------------------------------
y_pred = model.predict(X_test)

print("\n✅ Model Evaluation Results:")
print("Accuracy:", round(accuracy_score(y_test, y_pred), 3))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# ---------------------------------------------
# 9. Confusion Matrix Visualization
# ---------------------------------------------
encoded_to_meal = df.drop_duplicates(subset=['Meal_Plan_Encoded']) \
                    .set_index('Meal_Plan_Encoded')['Meal_Plan'] \
                    .sort_index().to_dict()
class_labels = [encoded_to_meal[i] for i in sorted(df['Meal_Plan_Encoded'].unique())]

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=class_labels, yticklabels=class_labels)
plt.xlabel("Predicted Meal Plan")
plt.ylabel("True Meal Plan")
plt.title("Confusion Matrix - Random Forest")
plt.show()

# ---------------------------------------------
# 10. Save model
# ---------------------------------------------
joblib.dump(model, MODEL_FILE)
print(f"\n💾 Model saved successfully as: {MODEL_FILE}")
print("💾 Scaler and encoder also saved in model/ folder.")

print("\n✅ Training completed successfully!")
