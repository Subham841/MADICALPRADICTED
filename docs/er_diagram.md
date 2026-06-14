# Entity Relationship (ER) Diagram: MediPredict AI

The database architecture is designed with three core tables. It maps patient registration details to prediction summaries, while storing machine learning evaluation statistics separately to monitor model calibration over time.

## ER Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string username UNIQUE
        string email UNIQUE
        string password_hash
        string role "patient | admin"
        timestamp created_at
    }

    PREDICTION_HISTORY {
        int id PK
        int user_id FK
        string disease_type "Diabetes | Heart Disease | Kidney Disease | Liver Disease"
        string input_data "JSON Text"
        string prediction_result "High Risk | Low Risk"
        float probability
        string model_used "Random Forest | Logistic Regression"
        timestamp created_at
    }

    MODEL_PERFORMANCE {
        int id PK
        string disease_type
        string model_name
        float accuracy
        float precision_score
        float recall
        float f1_score
        string confusion_matrix "JSON Text"
        timestamp trained_at
    }

    USERS ||--o{ PREDICTION_HISTORY : "records"
```

## Schema Structural Breakdown

### 1. `users` Table
- Houses core login details.
- Hashed passwords (`password_hash`) are created using Werkzeug's SHA256 PBKDF2 algorithm.
- `role` controls permission bounds (e.g. patients can only see their own listings; admin can view the overall performance metrics, register users, and inspect global logs).

### 2. `prediction_history` Table
- Connects predictions to a specific user via `user_id`.
- `input_data` stores clinical parameters as a serialized JSON string, preserving flexibility across all four modules (Diabetes, Heart Disease, Kidney Disease, and Liver Disease).

### 3. `model_performance` Table
- Stores testing performance metrics of trained models.
- Loaded dynamically on the admin panel to chart accuracy comparisons.
