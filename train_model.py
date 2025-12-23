import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Load your CSV
df = pd.read_csv("student_data.csv")

# ----------------------------------------
# CREATE TARGET COLUMN (Pass / Fail)
# ----------------------------------------
def generate_result(row):
    if row["semester_score"] >= 60 and row["attendance"] >= 75:
        return 1  # Pass
    else:
        return 0  # Fail

df["result"] = df.apply(generate_result, axis=1)

# ----------------------------------------
# FEATURES & TARGET
# ----------------------------------------
X = df[["semester_score", "study_hours", "attendance"]]
y = df["result"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save model
pickle.dump(model, open("model.pkl", "wb"))

print("✅ Model trained and model.pkl saved successfully")
