# train_model.py

"""
This script trains a machine learning model to predict the time it takes to close service requests.
The model uses features such as issue category, weekday, month, and hour of ticket creation.
The trained model is saved to a file for later use.
"""

import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# 1) Load the transformed data
"""
Load the transformed service request data from the SQLite database.
The data is expected to include ticket creation and closure timestamps.
"""
conn = sqlite3.connect("commonwealth_connect.db")
df = pd.read_sql("SELECT * FROM service_requests_transformed", conn, parse_dates=[
    'ticket_created_date_time','ticket_closed_date_time'
])
conn.close()

# 2) Keep only rows where we actually closed the ticket
"""
Filter the dataset to include only rows where both ticket creation and closure timestamps are available.
"""
df = df.dropna(subset=['ticket_closed_date_time','ticket_created_date_time'])

# 3) Prepare target
"""
Calculate the target variable: time to close the ticket in hours.
This is derived from the difference between ticket closure and creation timestamps.
"""
df['time_to_close_hours'] = (
    df['ticket_closed_date_time'] - df['ticket_created_date_time']
).dt.total_seconds() / 3600.0

# 4) Select features
"""
Define the features to be used for training the model:
- Categorical: issue category, weekday of ticket creation
- Numeric: month and hour of ticket creation
"""
features = [
    'issue_category',
    'ticket_created_date_time_weekday',
    'ticket_created_date_time_month',
    'ticket_created_date_time_hour'
]
X = df[features]
y = df['time_to_close_hours']

# 5) Build a pipeline
"""
Create a machine learning pipeline:
- Preprocessing: One-hot encode categorical features
- Model: Random Forest Regressor
"""
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), ['issue_category','ticket_created_date_time_weekday']),
], remainder='passthrough')

model = Pipeline([
    ("preproc", preprocessor),
    ("reg", RandomForestRegressor(n_estimators=100, random_state=42))
])

# 6) Train/test split & fit
"""
Split the data into training and testing sets, then train the model on the training data.
Evaluate the model using the R² score on the test data.
"""
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)
print("Test R² score:", model.score(X_test, y_test))

# 7) Persist the model
"""
Save the trained model to a file using joblib for later use.
"""
joblib.dump(model, "time_to_close_model.joblib")
print("Model saved to time_to_close_model.joblib")
