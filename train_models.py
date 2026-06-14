import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Ensure the models directory exists
os.makedirs('models', exist_ok=True)

# Seed for reproducibility
np.random.seed(42)

def generate_diabetes_data(n_samples=1000):
    glucose = np.random.normal(120, 30, n_samples)
    blood_pressure = np.random.normal(70, 12, n_samples)
    bmi = np.random.normal(32, 7, n_samples)
    insulin = np.random.normal(80, 40, n_samples)
    age = np.random.normal(33, 11, n_samples)
    
    glucose = np.clip(glucose, 40, 200)
    blood_pressure = np.clip(blood_pressure, 40, 130)
    bmi = np.clip(bmi, 15, 60)
    insulin = np.clip(insulin, 15, 600)
    age = np.clip(age, 18, 90).astype(int)
    
    g_score = (glucose - 100) / 30
    bp_score = (blood_pressure - 70) / 12
    bmi_score = (bmi - 25) / 7
    ins_score = (insulin - 80) / 80
    age_score = (age - 30) / 15
    
    risk_score = 0.5 * g_score + 0.1 * bp_score + 0.3 * bmi_score + 0.1 * ins_score + 0.2 * age_score
    prob = 1 / (1 + np.exp(-risk_score))
    
    outcome = (prob > 0.5).astype(int)
    
    df = pd.DataFrame({
        'Glucose': glucose,
        'BloodPressure': blood_pressure,
        'BMI': bmi,
        'Insulin': insulin,
        'Age': age,
        'Outcome': outcome
    })
    return df

def generate_heart_data(n_samples=1000):
    age = np.random.normal(54, 9, n_samples)
    gender = np.random.binomial(1, 0.67, n_samples)
    cholesterol = np.random.normal(240, 50, n_samples)
    resting_bp = np.random.normal(130, 17, n_samples)
    max_hr = np.random.normal(150, 22, n_samples)
    
    age = np.clip(age, 29, 80).astype(int)
    cholesterol = np.clip(cholesterol, 120, 500)
    resting_bp = np.clip(resting_bp, 90, 200)
    max_hr = np.clip(max_hr, 70, 210)
    
    age_score = (age - 50) / 10
    gen_score = gender * 0.5
    chol_score = (cholesterol - 220) / 50
    bp_score = (resting_bp - 120) / 20
    hr_score = (140 - max_hr) / 20
    
    risk_score = 0.3 * age_score + 0.3 * gen_score + 0.3 * chol_score + 0.2 * bp_score + 0.3 * hr_score
    prob = 1 / (1 + np.exp(-risk_score))
    
    outcome = (prob > 0.5).astype(int)
    
    df = pd.DataFrame({
        'Age': age,
        'Gender': gender,
        'Cholesterol': cholesterol,
        'RestingBP': resting_bp,
        'MaxHR': max_hr,
        'Outcome': outcome
    })
    return df

def generate_kidney_data(n_samples=1000):
    blood_urea = np.random.normal(45, 20, n_samples)
    serum_creatinine = np.random.normal(1.2, 0.6, n_samples)
    hemoglobin = np.random.normal(13.5, 2.0, n_samples)
    blood_pressure = np.random.normal(76, 10, n_samples)
    
    blood_urea = np.clip(blood_urea, 10, 250)
    serum_creatinine = np.clip(serum_creatinine, 0.4, 15.0)
    hemoglobin = np.clip(hemoglobin, 6.0, 18.0)
    blood_pressure = np.clip(blood_pressure, 50, 120)
    
    bu_score = (blood_urea - 40) / 25
    sc_score = (serum_creatinine - 1.0) / 0.8
    hemo_score = (14.0 - hemoglobin) / 2.0
    bp_score = (blood_pressure - 75) / 12
    
    risk_score = 0.2 * bu_score + 0.5 * sc_score + 0.4 * hemo_score + 0.1 * bp_score
    prob = 1 / (1 + np.exp(-risk_score))
    
    outcome = (prob > 0.5).astype(int)
    
    df = pd.DataFrame({
        'BloodUrea': blood_urea,
        'SerumCreatinine': serum_creatinine,
        'Hemoglobin': hemoglobin,
        'BloodPressure': blood_pressure,
        'Outcome': outcome
    })
    return df

def generate_liver_data(n_samples=1000):
    """
    Generates synthetic liver disease risk assessment data.
    Features: Bilirubin, Albumin, Alkaline Phosphatase (ALP), SGOT/AST, Age
    """
    bilirubin = np.random.normal(1.0, 0.5, n_samples)
    albumin = np.random.normal(4.0, 0.6, n_samples)
    alp = np.random.normal(90, 35, n_samples)
    sgot = np.random.normal(35, 25, n_samples)
    age = np.random.normal(45, 15, n_samples)
    
    bilirubin = np.clip(bilirubin, 0.1, 15.0)
    albumin = np.clip(albumin, 1.5, 6.0)
    alp = np.clip(alp, 30, 600)
    sgot = np.clip(sgot, 5, 500)
    age = np.clip(age, 18, 90).astype(int)
    
    # Higher bilirubin, ALP, SGOT, and lower albumin indicates liver dysfunction
    b_score = (bilirubin - 1.2) / 1.0
    a_score = (3.5 - albumin) / 0.5
    alp_score = (alp - 100) / 50
    sgot_score = (sgot - 40) / 20
    age_score = (age - 45) / 20
    
    risk_score = 0.4 * b_score + 0.4 * a_score + 0.15 * alp_score + 0.35 * sgot_score + 0.1 * age_score
    prob = 1 / (1 + np.exp(-risk_score))
    
    outcome = (prob > 0.5).astype(int)
    
    df = pd.DataFrame({
        'Bilirubin': bilirubin,
        'Albumin': albumin,
        'AlkalinePhos': alp,
        'SGOT': sgot,
        'Age': age,
        'Outcome': outcome
    })
    return df

def generate_brain_data(n_samples=1000):
    """
    Generates synthetic brain disease (neurological anomalies) risk assessment data.
    Features: HeadacheIntensity (0-10), CognitiveSymptoms (0/1), SensorimotorSymptoms (0/1), HistoryOfSeizures (0/1), Age
    """
    headache = np.random.normal(3.5, 2.5, n_samples)
    cognitive = np.random.binomial(1, 0.25, n_samples)
    sensorimotor = np.random.binomial(1, 0.20, n_samples)
    seizures = np.random.binomial(1, 0.08, n_samples)
    age = np.random.normal(48, 16, n_samples)
    
    headache = np.clip(headache, 0, 10)
    age = np.clip(age, 18, 90).astype(int)
    
    h_score = (headache - 3.0) / 2.5
    cog_score = cognitive * 0.8
    sens_score = sensorimotor * 0.7
    seiz_score = seizures * 1.2
    age_score = (age - 45) / 15
    
    risk_score = 0.2 * h_score + 0.45 * cog_score + 0.4 * sens_score + 0.6 * seiz_score + 0.15 * age_score
    prob = 1 / (1 + np.exp(-risk_score))
    
    outcome = (prob > 0.5).astype(int)
    
    df = pd.DataFrame({
        'HeadacheIntensity': headache,
        'CognitiveSymptoms': cognitive,
        'SensorimotorSymptoms': sensorimotor,
        'HistoryOfSeizures': seizures,
        'Age': age,
        'Outcome': outcome
    })
    return df

def train_and_evaluate(df, disease_name):
    print(f"\n--- Training Models for {disease_name} ---")
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    scaler_path = f'models/{disease_name.lower().replace(" ", "_")}_scaler.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Saved scaler to {scaler_path}")
    
    models = {
        'Logistic Regression': LogisticRegression(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    performance = {}
    
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        print(f"{name} Metrics:")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1 Score:  {f1:.4f}")
        
        model_filename = f'{disease_name.lower().replace(" ", "_")}_{"lr" if name == "Logistic Regression" else "rf"}.pkl'
        model_path = f'models/{model_filename}'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
            
        performance[name] = {
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'confusion_matrix': cm
        }
        
    return performance

def main():
    # 1. Diabetes
    df_diabetes = generate_diabetes_data()
    diabetes_metrics = train_and_evaluate(df_diabetes, 'Diabetes')
    
    # 2. Heart Disease
    df_heart = generate_heart_data()
    heart_metrics = train_and_evaluate(df_heart, 'Heart Disease')
    
    # 3. Kidney Disease
    df_kidney = generate_kidney_data()
    kidney_metrics = train_and_evaluate(df_kidney, 'Kidney Disease')
    
    # 4. Liver Disease
    df_liver = generate_liver_data()
    liver_metrics = train_and_evaluate(df_liver, 'Liver Disease')
    
    # 5. Brain Disease
    df_brain = generate_brain_data()
    brain_metrics = train_and_evaluate(df_brain, 'Brain Disease')
    
    # Package all metrics together
    all_metrics = {
        'Diabetes': diabetes_metrics,
        'Heart Disease': heart_metrics,
        'Kidney Disease': kidney_metrics,
        'Liver Disease': liver_metrics,
        'Brain Disease': brain_metrics
    }
    
    # Save metrics to JSON
    with open('models/metrics.json', 'w') as f:
        json.dump(all_metrics, f, indent=4)
    print("\nSaved all model performance statistics to models/metrics.json")

if __name__ == '__main__':
    main()
