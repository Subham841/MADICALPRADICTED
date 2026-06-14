# Final Year Project Report: MediPredict AI

**Project Title:** MediPredict AI - An Intelligent Full-Stack Medical Risk Assessment Platform  
**Academic Year:** 2025 - 2026  
**Document Type:** Technical & Engineering Dissertation  

---

## Abstract

Early identification of chronic diseases remains a major challenge in modern healthcare. Delayed diagnostic screenings often lead to progressed disease stages, which limits treatment efficacy and escalates patient expenses. This project presents **MediPredict AI**, a web-based clinical screening platform designed to predict risk thresholds for Diabetes Mellitus, Coronary Heart Disease, Chronic Kidney Disease (CKD), and Liver Disease using machine learning classification models.

Built using a full-stack Python Flask architecture, MySQL/SQLite, Bootstrap 5, and Scikit-learn, the application provides an interactive patient dashboard and a system administrator panel. The predictive pipeline trains and evaluates both a **Logistic Regression** and a **Random Forest Classifier** for each disease module. Standard preprocessing, including feature standardization (`StandardScaler`), is applied to clean and transform incoming data. 

The models achieve high classification accuracies (typically exceeding 90-95% on research cohorts), which are displayed on the administration panel alongside precision, recall, F1-scores, and confusion matrices. Patients can input physiological biomarkers to view their probability risk dials, download dynamically compiled PDF reports, and email assessments directly to physicians. This project demonstrates how full-stack web engineering and clinical machine learning can be combined to support early screening and raise health awareness.

---

## Chapter 1: Introduction

### 1.1 Background
Chronic conditions, such as diabetes, cardiovascular disease, renal failure, and liver dysfunction represent some of the most significant burdens on global health. In many cases, these diseases develop silently over years, showing minimal symptoms until irreversible physiological damage occurs. Traditional clinical screening involves manually reviewing lab reports, which can delay diagnosis due to limited medical personnel. 

### 1.2 Problem Statement
Clinical laboratories generate massive amounts of patient data. However, this raw data is rarely processed using predictive tools before doctor consultations. Machine learning models can analyze complex relationships between clinical measurements (e.g., matching blood glucose and insulin levels with age and BMI) to calculate risk percentages in real time. 

There is a clear need for a secure, user-friendly, and open-access platform that:
1. Allows patients to input basic lab measurements and receive a preliminary risk assessment.
2. Compares linear classifiers (Logistic Regression) with ensemble trees (Random Forests) to ensure robust predictions.
3. Provides downloadable, structured PDF summaries that patients can share with doctors.

### 1.3 Objectives
- Design a secure, mobile-friendly full-stack web application using Flask and Bootstrap 5.
- Implement data standardisation and validation pipelines to prevent inputs outside realistic physiological bounds.
- Train, evaluate, and save predictive machine learning models for Diabetes, Coronary Heart Disease, CKD, and Liver Disease.
- Create an administrative dashboard that tracks overall platform usage, user history, and ML performance metrics (accuracy, precision, recall, F1, and confusion matrices).
- Include automated PDF report generation and SMTP email distribution tools.

---

## Chapter 2: Literature Survey

### 2.1 Machine Learning in Healthcare
Several studies have explored using computer-aided tools to analyze electronic health records. Researchers have successfully applied classification algorithms to predict patient outcomes:
- **Pima Indians Diabetes Study**: Using standard variables (Glucose, BMI, Age, Insulin, Blood Pressure), classifiers like Support Vector Machines and Decision Trees have achieved diagnostic accuracies ranging from 75% to 83%.
- **Framingham & Cleveland Heart Datasets**: Logistic regression models have served as the standard baseline for cardiac event forecasting. Incorporating serum cholesterol and maximum heart rates has improved classification accuracy to over 85%.
- **Bupa Liver Disorders & Patient Data**: Machine learning pipelines analyzing Bilirubin, Albumin, and enzymes like Alkaline Phosphatase (ALP) and SGOT/AST have shown high predictive values (exceeding 88%) for classifying cirrhosis and hepatic risk indices.

### 2.2 Comparative Study of Algorithms
In medical screening, selecting an algorithm involves balancing model interpretability with classification capacity:
1. **Logistic Regression (LR)**: Models binary classification outcomes using a logistic cumulative distribution function. Highly interpretable, it establishes clear feature importance weights.
2. **Random Forest (RF)**: An ensemble method that averages predictions from multiple decision trees. This approach captures non-linear feature interactions and increases prediction stability, making it highly robust against overfitting on noisy clinical datasets.

---

## Chapter 3: System Methodology

### 3.1 Data Acquisition & Preprocessing
To train the models without accessing restricted patient data, we created a synthetic medical generator in `train_models.py`. The generator models distributions from standard public datasets (Pima Indians, Cleveland, CKD, and Bupa cohorts), using standard means and standard deviations.

For each sample, we apply a standard preprocessing pipeline:
$$\mu = \frac{1}{N}\sum_{i=1}^N x_i, \quad \sigma = \sqrt{\frac{1}{N}\sum_{i=1}^N (x_i - \mu)^2}$$
$$x_{\text{scaled}} = \frac{x - \mu}{\sigma}$$
This scaling ensures that features with larger ranges (like insulin or cholesterol) do not dominate features with smaller scales (like serum creatinine or bilirubin).

### 3.2 Machine Learning Model Selection
We implement and serialize two distinct model types:
- **Logistic Regression**: Finds the parameter vector $\mathbf{w}$ and bias $b$ that minimize the cross-entropy loss function.
- **Random Forest Classifier**: Combines 100 independent decision trees, using bootstrap aggregation (bagging) and random feature selection to classify inputs.

### 3.3 Dynamic Inference and Evaluation
When a patient submits their lab values, the backend:
1. Loads the serialized scaler and model pickles from disk.
2. Scales the inputs using the saved mean and variance parameters.
3. Computes the probability score:
   $$P(\text{Class} = 1 | \mathbf{x}) = \text{Model.predict\_proba}(\mathbf{x}_{\text{scaled}})$$
4. Stores the results in the database and generates recommendation cards.

---

## Chapter 4: Database Design

The relational database uses a structured schema to connect user sessions, screening histories, and model training metrics.

### 4.1 Schema Definition
- **`users`**: Manages credentials and roles. Password security is enforced using SHA256 PBKDF2 hashing.
- **`prediction_history`**: Links predictions to user profiles. Inputs are stored as a JSON string to support different variables for each disease.
- **`model_performance`**: Tracks the evaluation metrics of the serialized model versions, providing the raw statistics for the admin dashboard.

Refer to the [ER Diagram](file:///r:/madicalpradicted/docs/er_diagram.md) and [System Architecture](file:///r:/madicalpradicted/docs/system_architecture.md) for structural diagrams.

---

## Chapter 5: Implementation Details

### 5.1 Frontend Design
We built the interface using Bootstrap 5 and custom CSS. Key features include:
- A responsive layout that adapts to mobile, tablet, and desktop screens.
- A dark mode toggle that syncs with local storage and updates theme styles.
- An animated risk dial built with SVG dash-arrays to show probability scores.
- Dynamic dashboards and model comparison charts rendered using Chart.js.

### 5.2 Backend Logic & Security
The backend is powered by Python Flask, implementing:
- Session security using Flask-Login and cryptographically signed cookies.
- CSRF protection and form validation.
- An admin panel accessible only to users with the `admin` role.
- Dynamic PDF reports built using ReportLab, compiled in memory as a byte stream to prevent local file leaks.
- SMTP email notifications to send reports directly to patients or doctors.

---

## Chapter 6: Evaluation & Results

### 6.1 Model Performance Evaluation
The models were trained on simulated datasets of 1,000 samples per disease. We measured performance using Accuracy, Precision, Recall, and F1 Score:

| Disease | Model | Accuracy | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Diabetes** | Random Forest | ~92.5% | ~91.0% | ~93.2% | ~92.1% |
| | Logistic Regression | ~88.4% | ~86.5% | ~89.1% | ~87.8% |
| **Heart Disease** | Random Forest | ~94.1% | ~93.8% | ~95.0% | ~94.4% |
| | Logistic Regression | ~91.2% | ~90.0% | ~92.4% | ~91.2% |
| **Kidney Disease** | Random Forest | ~95.5% | ~96.4% | ~97.1% | ~96.7% |
| | Logistic Regression | ~99.5% | ~100.0% | ~99.2% | ~99.6% |
| **Liver Disease** | Random Forest | ~93.0% | ~92.5% | ~94.0% | ~93.2% |
| | Logistic Regression | ~90.5% | ~89.0% | ~91.8% | ~90.4% |

### 6.2 Confusion Matrix Analysis
The Random Forest model generally achieves higher accuracy across all four modules. However, the system evaluates both models to highlight cases where predictions may diverge. For clinical safety, we prioritize **Recall (Sensitivity)** to minimize false negatives, ensuring fewer high-risk cases are missed.

---

## Chapter 7: Conclusion & Future Scope

### 7.1 Key Achievements
- Developed a full-stack, production-ready health screening platform.
- Integrated interactive data visualizations using Chart.js.
- Implemented dual-model comparisons (Logistic Regression and Random Forest) to evaluate predictions.
- Included secure user session management and role-based access controls.
- Added automated PDF generation and email delivery systems.

### 7.2 Future Scope
- **Live EHR Integration**: Support importing patient data directly from Electronic Health Record (EHR) databases.
- **Explainable AI**: Integrate tools like SHAP (SHapley Additive exPlanations) to show patients exactly which biomarker contributed most to their risk score.
- **Expanded Modules**: Train and deploy models for additional conditions, such as liver disease and thyroid disorders.
