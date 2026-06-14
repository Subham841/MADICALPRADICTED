import os
import json
import io
import pickle
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, PredictionHistory, ModelPerformance

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ML Model Loading Utility ---
MODELS = {}
SCALERS = {}

def load_ml_resources():
    diseases = ['diabetes', 'heart_disease', 'kidney_disease', 'liver_disease', 'brain_disease']
    for disease in diseases:
        scaler_path = f'models/{disease}_scaler.pkl'
        rf_path = f'models/{disease}_rf.pkl'
        lr_path = f'models/{disease}_lr.pkl'
        
        # Load scaler
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                SCALERS[disease] = pickle.load(f)
        
        # Load RF model
        if os.path.exists(rf_path):
            with open(rf_path, 'rb') as f:
                MODELS[f'{disease}_rf'] = pickle.load(f)
                
        # Load LR model
        if os.path.exists(lr_path):
            with open(lr_path, 'rb') as f:
                MODELS[f'{disease}_lr'] = pickle.load(f)

# Helper to check if ML resources are trained
def is_ml_trained():
    required_files = [
        'models/diabetes_scaler.pkl', 'models/diabetes_rf.pkl',
        'models/heart_disease_scaler.pkl', 'models/heart_disease_rf.pkl',
        'models/kidney_disease_scaler.pkl', 'models/kidney_disease_rf.pkl',
        'models/liver_disease_scaler.pkl', 'models/liver_disease_rf.pkl',
        'models/brain_disease_scaler.pkl', 'models/brain_disease_rf.pkl',
        'models/brain_disease_lr.pkl'
    ]
    return all(os.path.exists(f) for f in required_files)

# Dynamic DB seeding for Model Performance
def seed_model_performance():
    try:
        if ModelPerformance.query.first() is None:
            metrics_path = 'models/metrics.json'
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)
                
                for disease, models_dict in metrics.items():
                    for model_name, score_dict in models_dict.items():
                        perf = ModelPerformance(
                            disease_type=disease,
                            model_name=model_name,
                            accuracy=score_dict['accuracy'],
                            precision_score=score_dict['precision'],
                            recall=score_dict['recall'],
                            f1_score=score_dict['f1_score'],
                            confusion_matrix=json.dumps(score_dict['confusion_matrix'])
                        )
                        db.session.add(perf)
                db.session.commit()
                print("Model performance seeded successfully.")
    except Exception as e:
        print(f"Error seeding model performance: {e}")

# Database initialization
with app.app_context():
    db.create_all()
    # Check if admin user exists, if not, create one
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', email='admin@medipredict.ai', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created (username: admin, password: admin123).")
    
    # Load ML models
    load_ml_resources()
    # Seed performance data if available
    seed_model_performance()

# --- Recommendation Helpers ---
def get_recommendations(disease, result, data):
    recommendations = []
    if disease == 'Diabetes':
        glucose = float(data.get('Glucose', 0))
        bmi = float(data.get('BMI', 0))
        if result == 'High Risk':
            recommendations.append("Schedule a comprehensive evaluation with an Endocrinologist.")
            if glucose > 140:
                recommendations.append(f"Your glucose reading ({glucose} mg/dL) is high. Track your levels daily before and after meals.")
            if bmi > 25:
                recommendations.append(f"Your BMI of {bmi:.1f} indicates overweight/obesity. Aim for a gradual weight reduction of 5-10% through diet changes.")
            recommendations.append("Limit intake of refined sugars, soda, and high-glycemic carbohydrates.")
            recommendations.append("Incorporate at least 150 minutes of moderate-intensity aerobic physical activity weekly.")
        else:
            recommendations.append("Continue periodic blood sugar screenings (e.g., HbA1c test annually).")
            recommendations.append("Maintain a balanced diet rich in fiber, whole grains, and lean proteins.")
            recommendations.append("Keep active with daily exercises (30 minutes of brisk walking).")
            
    elif disease == 'Heart Disease':
        chol = float(data.get('Cholesterol', 0))
        bp = float(data.get('Resting Blood Pressure', 0) or data.get('RestingBP', 0))
        if result == 'High Risk':
            recommendations.append("Seek immediate consultation with a Cardiologist.")
            if chol > 240:
                recommendations.append(f"Your cholesterol is high ({chol} mg/dL). Consider adopting a Low-Cholesterol or Mediterranean diet.")
            if bp > 130:
                recommendations.append(f"Your resting blood pressure is elevated ({bp} mmHg). Restrict sodium intake to under 1,500 mg daily.")
            recommendations.append("Monitor blood pressure and resting heart rate daily.")
            recommendations.append("Avoid high-intensity triggers, tobacco usage, and limit alcohol consumption.")
        else:
            recommendations.append("Maintain a heart-healthy diet consisting of healthy fats (olive oil, avocados, nuts).")
            recommendations.append("Engage in regular cardiovascular exercise (running, swimming, cycling).")
            recommendations.append("Keep stress levels managed through mindfulness or yoga.")
            
    elif disease == 'Kidney Disease':
        creatinine = float(data.get('Serum Creatinine', 0) or data.get('SerumCreatinine', 0))
        hb = float(data.get('Hemoglobin', 0))
        if result == 'High Risk':
            recommendations.append("Consult a Nephrologist for detailed renal function evaluation.")
            if creatinine > 1.2:
                recommendations.append(f"Elevated Serum Creatinine ({creatinine} mg/dL) signals reduced filtering capacity. Track kidney metrics regularly.")
            if hb < 12.0:
                recommendations.append(f"Low Hemoglobin ({hb} g/dL) can be a secondary effect of CKD. Discuss iron/erythropoietin therapy with a physician.")
            recommendations.append("Limit dietary intake of sodium, potassium, and high phosphorus foods.")
            recommendations.append("Consult your doctor before taking NSAIDs (like ibuprofen, naproxen) which damage kidneys.")
        else:
            recommendations.append("Stay adequately hydrated (aim for 2-3 liters of water daily unless advised otherwise).")
            recommendations.append("Ensure control of blood pressure and blood glucose, as they are primary causes of kidney damage.")
            recommendations.append("Schedule annual urinalysis and kidney function panels.")
            
    elif disease == 'Liver Disease':
        bilirubin = float(data.get('Bilirubin', 0))
        albumin = float(data.get('Albumin', 0))
        if result == 'High Risk':
            recommendations.append("Consult a Gastroenterologist or Hepatologist immediately for standard liver evaluation.")
            if bilirubin > 1.2:
                recommendations.append(f"Elevated Serum Bilirubin ({bilirubin} mg/dL) indicates possible hepatocyte injury or biliary obstruction.")
            if albumin < 3.5:
                recommendations.append(f"Low Albumin ({albumin} g/dL) suggests reduced liver protein synthesis function.")
            recommendations.append("Strictly avoid alcohol consumption and hepatotoxic medications (e.g. high dose paracetamol).")
            recommendations.append("Track liver enzyme panel levels (AST/SGOT, ALT/SGPT, ALP) frequently.")
        else:
            recommendations.append("Maintain a balanced, nutrient-dense diet rich in green vegetables and antioxidants.")
            recommendations.append("Maintain a healthy weight to prevent Non-Alcoholic Fatty Liver Disease (NAFLD).")
            recommendations.append("Avoid excessive chemical exposure and unnecessary self-medication.")
            
    elif disease == 'Brain Disease':
        headache = float(data.get('Headache Intensity', 0))
        cog = float(data.get('Cognitive Symptoms', 0) if isinstance(data.get('Cognitive Symptoms'), (int, float)) else (1.0 if data.get('Cognitive Symptoms') == 'Yes' else 0.0))
        sens = float(data.get('Sensorimotor Symptoms', 0) if isinstance(data.get('Sensorimotor Symptoms'), (int, float)) else (1.0 if data.get('Sensorimotor Symptoms') == 'Yes' else 0.0))
        seiz = float(data.get('History of Seizures', 0) if isinstance(data.get('History of Seizures'), (int, float)) else (1.0 if data.get('History of Seizures') == 'Yes' else 0.0))
        
        if result == 'High Risk':
            recommendations.append("Schedule an urgent consultation with a Neurologist for a comprehensive neurological examination.")
            if headache > 6:
                recommendations.append(f"Your reported headache intensity ({headache}/10) is severe. Avoid self-medication and obtain a clinical review.")
            if cog == 1.0 or data.get('Cognitive Symptoms') == 'Yes':
                recommendations.append("Cognitive changes (memory/speech) warrant brain imaging tests (such as MRI or CT scan) to rule out structural anomalies.")
            if sens == 1.0 or data.get('Sensorimotor Symptoms') == 'Yes':
                recommendations.append("Sensorimotor changes (numbness, weakness, vision changes) require prompt clinical assessment of reflexes and motor pathways.")
            if seiz == 1.0 or data.get('History of Seizures') == 'Yes':
                recommendations.append("Seizure history requires electroencephalogram (EEG) screening and specialized seizure control protocols.")
            recommendations.append("Strictly monitor and control systemic vitals, especially blood pressure and glucose levels, which affect neurological health.")
        else:
            recommendations.append("Maintain routine physical and cognitive exercises (like puzzles, reading, active learning).")
            recommendations.append("Adopt a diet rich in omega-3 fatty acids, antioxidants, and vitamins (e.g., MIND diet).")
            recommendations.append("Ensure 7-8 hours of high-quality sleep daily to promote neurological recovery and glymphatic clearance.")
            recommendations.append("Perform routine health checks including blood pressure and lipid panels.")
            
    return recommendations

# --- Basic Web Pages ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash("Thank you for your message! Our medical support team will reach out to you shortly.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

# --- Secure Authentication ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash("Email address already registered.", "danger")
            return redirect(url_for('register'))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username_or_email = request.form.get('username').strip()
        password = request.form.get('password')
        
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully.", "success")
    return redirect(url_for('home'))

# --- Patient Dashboard & User Features ---
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin'))
        
    search_query = request.args.get('search', '').strip()
    disease_filter = request.args.get('disease', '').strip()
    
    query = PredictionHistory.query.filter_by(user_id=current_user.id)
    
    if disease_filter:
        query = query.filter(PredictionHistory.disease_type == disease_filter)
        
    if search_query:
        query = query.filter(PredictionHistory.prediction_result.like(f"%{search_query}%") | 
                             PredictionHistory.disease_type.like(f"%{search_query}%") |
                             PredictionHistory.model_used.like(f"%{search_query}%"))
                             
    history = query.order_by(PredictionHistory.created_at.desc()).all()
    
    # Calculate statistics
    total_preds = len(history)
    high_risk_count = sum(1 for p in history if p.prediction_result == 'High Risk')
    low_risk_count = total_preds - high_risk_count
    
    ml_status = is_ml_trained()
    
    return render_template('dashboard.html', 
                           history=history, 
                           total_preds=total_preds,
                           high_risk_count=high_risk_count,
                           low_risk_count=low_risk_count,
                           ml_status=ml_status)

# --- Prediction Modules ---
@app.route('/predict/diabetes', methods=['GET', 'POST'])
@login_required
def predict_diabetes():
    if not is_ml_trained():
        flash("Machine Learning models are not trained yet.", "warning")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            glucose = float(request.form.get('Glucose'))
            bp = float(request.form.get('BloodPressure'))
            bmi = float(request.form.get('BMI'))
            insulin = float(request.form.get('Insulin'))
            age = float(request.form.get('Age'))
            model_type = request.form.get('model_used', 'Random Forest')
            
            input_dict = {
                'Glucose': glucose,
                'Blood Pressure': bp,
                'BMI': bmi,
                'Insulin': insulin,
                'Age': age
            }
            
            scaler = SCALERS.get('diabetes')
            features = [[glucose, bp, bmi, insulin, age]]
            scaled_features = scaler.transform(features)
            
            model_key = 'diabetes_rf' if model_type == 'Random Forest' else 'diabetes_lr'
            model = MODELS.get(model_key)
            
            prediction = model.predict(scaled_features)[0]
            probability = model.predict_proba(scaled_features)[0][1] * 100
            
            result = 'High Risk' if prediction == 1 else 'Low Risk'
            
            history = PredictionHistory(
                user_id=current_user.id,
                disease_type='Diabetes',
                input_data=json.dumps(input_dict),
                prediction_result=result,
                probability=round(probability, 2),
                model_used=model_type
            )
            db.session.add(history)
            db.session.commit()
            
            return redirect(url_for('result', prediction_id=history.id))
            
        except Exception as e:
            flash(f"Error processing prediction: {e}", "danger")
            return redirect(url_for('predict_diabetes'))
            
    return render_template('predict_diabetes.html')

@app.route('/predict/heart', methods=['GET', 'POST'])
@login_required
def predict_heart():
    if not is_ml_trained():
        flash("Machine Learning models are not trained yet.", "warning")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            age = float(request.form.get('Age'))
            gender = float(request.form.get('Gender'))
            chol = float(request.form.get('Cholesterol'))
            bp = float(request.form.get('RestingBP'))
            max_hr = float(request.form.get('MaxHR'))
            model_type = request.form.get('model_used', 'Random Forest')
            
            gender_label = 'Male' if gender == 1.0 else 'Female'
            input_dict = {
                'Age': age,
                'Gender': gender_label,
                'Cholesterol': chol,
                'Resting Blood Pressure': bp,
                'Maximum Heart Rate': max_hr
            }
            
            scaler = SCALERS.get('heart_disease')
            features = [[age, gender, chol, bp, max_hr]]
            scaled_features = scaler.transform(features)
            
            model_key = 'heart_disease_rf' if model_type == 'Random Forest' else 'heart_disease_lr'
            model = MODELS.get(model_key)
            
            prediction = model.predict(scaled_features)[0]
            probability = model.predict_proba(scaled_features)[0][1] * 100
            
            result = 'High Risk' if prediction == 1 else 'Low Risk'
            
            history = PredictionHistory(
                user_id=current_user.id,
                disease_type='Heart Disease',
                input_data=json.dumps(input_dict),
                prediction_result=result,
                probability=round(probability, 2),
                model_used=model_type
            )
            db.session.add(history)
            db.session.commit()
            
            return redirect(url_for('result', prediction_id=history.id))
            
        except Exception as e:
            flash(f"Error processing prediction: {e}", "danger")
            return redirect(url_for('predict_heart'))
            
    return render_template('predict_heart.html')

@app.route('/predict/kidney', methods=['GET', 'POST'])
@login_required
def predict_kidney():
    if not is_ml_trained():
        flash("Machine Learning models are not trained yet.", "warning")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            bu = float(request.form.get('BloodUrea'))
            sc = float(request.form.get('SerumCreatinine'))
            hb = float(request.form.get('Hemoglobin'))
            bp = float(request.form.get('BloodPressure'))
            model_type = request.form.get('model_used', 'Random Forest')
            
            input_dict = {
                'Blood Urea': bu,
                'Serum Creatinine': sc,
                'Hemoglobin': hb,
                'Blood Pressure': bp
            }
            
            scaler = SCALERS.get('kidney_disease')
            features = [[bu, sc, hb, bp]]
            scaled_features = scaler.transform(features)
            
            model_key = 'kidney_disease_rf' if model_type == 'Random Forest' else 'kidney_disease_lr'
            model = MODELS.get(model_key)
            
            prediction = model.predict(scaled_features)[0]
            probability = model.predict_proba(scaled_features)[0][1] * 100
            
            result = 'High Risk' if prediction == 1 else 'Low Risk'
            
            history = PredictionHistory(
                user_id=current_user.id,
                disease_type='Kidney Disease',
                input_data=json.dumps(input_dict),
                prediction_result=result,
                probability=round(probability, 2),
                model_used=model_type
            )
            db.session.add(history)
            db.session.commit()
            
            return redirect(url_for('result', prediction_id=history.id))
            
        except Exception as e:
            flash(f"Error processing prediction: {e}", "danger")
            return redirect(url_for('predict_kidney'))
            
    return render_template('predict_kidney.html')

@app.route('/predict/liver', methods=['GET', 'POST'])
@login_required
def predict_liver():
    if not is_ml_trained():
        flash("Machine Learning models are not trained yet.", "warning")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            bilirubin = float(request.form.get('Bilirubin'))
            albumin = float(request.form.get('Albumin'))
            alp = float(request.form.get('AlkalinePhos'))
            sgot = float(request.form.get('SGOT'))
            age = float(request.form.get('Age'))
            model_type = request.form.get('model_used', 'Random Forest')
            
            input_dict = {
                'Bilirubin': bilirubin,
                'Albumin': albumin,
                'Alkaline Phosphatase': alp,
                'SGOT/AST': sgot,
                'Age': age
            }
            
            scaler = SCALERS.get('liver_disease')
            features = [[bilirubin, albumin, alp, sgot, age]]
            scaled_features = scaler.transform(features)
            
            model_key = 'liver_disease_rf' if model_type == 'Random Forest' else 'liver_disease_lr'
            model = MODELS.get(model_key)
            
            prediction = model.predict(scaled_features)[0]
            probability = model.predict_proba(scaled_features)[0][1] * 100
            
            result = 'High Risk' if prediction == 1 else 'Low Risk'
            
            history = PredictionHistory(
                user_id=current_user.id,
                disease_type='Liver Disease',
                input_data=json.dumps(input_dict),
                prediction_result=result,
                probability=round(probability, 2),
                model_used=model_type
            )
            db.session.add(history)
            db.session.commit()
            
            return redirect(url_for('result', prediction_id=history.id))
            
        except Exception as e:
            flash(f"Error processing prediction: {e}", "danger")
            return redirect(url_for('predict_liver'))
            
    return render_template('predict_liver.html')

@app.route('/predict/brain', methods=['GET', 'POST'])
@login_required
def predict_brain():
    if not is_ml_trained():
        flash("Machine Learning models are not trained yet.", "warning")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        try:
            headache = float(request.form.get('HeadacheIntensity', 0))
            cognitive = float(request.form.get('CognitiveSymptoms', 0))
            sensorimotor = float(request.form.get('SensorimotorSymptoms', 0))
            seizures = float(request.form.get('HistoryOfSeizures', 0))
            age = float(request.form.get('Age', 0))
            model_type = request.form.get('model_used', 'Random Forest')
            
            cog_label = 'Yes' if cognitive == 1.0 else 'No'
            sens_label = 'Yes' if sensorimotor == 1.0 else 'No'
            seiz_label = 'Yes' if seizures == 1.0 else 'No'
            
            input_dict = {
                'Headache Intensity': headache,
                'Cognitive Symptoms': cog_label,
                'Sensorimotor Symptoms': sens_label,
                'History of Seizures': seiz_label,
                'Age': age
            }
            
            scaler = SCALERS.get('brain_disease')
            features = [[headache, cognitive, sensorimotor, seizures, age]]
            scaled_features = scaler.transform(features)
            
            model_key = 'brain_disease_rf' if model_type == 'Random Forest' else 'brain_disease_lr'
            model = MODELS.get(model_key)
            
            prediction = model.predict(scaled_features)[0]
            probability = model.predict_proba(scaled_features)[0][1] * 100
            
            result = 'High Risk' if prediction == 1 else 'Low Risk'
            
            history = PredictionHistory(
                user_id=current_user.id,
                disease_type='Brain Disease',
                input_data=json.dumps(input_dict),
                prediction_result=result,
                probability=round(probability, 2),
                model_used=model_type
            )
            db.session.add(history)
            db.session.commit()
            
            return redirect(url_for('result', prediction_id=history.id))
            
        except Exception as e:
            flash(f"Error processing prediction: {e}", "danger")
            return redirect(url_for('predict_brain'))
            
    return render_template('predict_brain.html')

@app.route('/result/<int:prediction_id>')
@login_required
def result(prediction_id):
    pred = PredictionHistory.query.get_or_404(prediction_id)
    
    if current_user.role != 'admin' and pred.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard'))
        
    inputs = pred.parsed_input
    recs = get_recommendations(pred.disease_type, pred.prediction_result, inputs)
    
    alt_model_type = 'Logistic Regression' if pred.model_used == 'Random Forest' else 'Random Forest'
    alt_prob = 0.0
    alt_result = 'Low Risk'
    
    try:
        disease_key = pred.disease_type.lower().replace(" ", "_")
        scaler = SCALERS.get(disease_key)
        
        if pred.disease_type == 'Diabetes':
            feat_list = [inputs.get('Glucose', 0), inputs.get('Blood Pressure', 0), inputs.get('BMI', 0), inputs.get('Insulin', 0), inputs.get('Age', 0)]
        elif pred.disease_type == 'Heart Disease':
            gender_val = 1.0 if inputs.get('Gender') == 'Male' else 0.0
            feat_list = [inputs.get('Age', 0), gender_val, inputs.get('Cholesterol', 0), inputs.get('Resting Blood Pressure', 0) or inputs.get('RestingBP', 0), inputs.get('Maximum Heart Rate', 0)]
        elif pred.disease_type == 'Kidney Disease':
            feat_list = [inputs.get('Blood Urea', 0), inputs.get('Serum Creatinine', 0), inputs.get('Hemoglobin', 0), inputs.get('Blood Pressure', 0)]
        elif pred.disease_type == 'Liver Disease':
            feat_list = [inputs.get('Bilirubin', 0), inputs.get('Albumin', 0), inputs.get('Alkaline Phosphatase', 0), inputs.get('SGOT/AST', 0), inputs.get('Age', 0)]
        elif pred.disease_type == 'Brain Disease':
            def map_binary(val):
                if isinstance(val, str):
                    return 1.0 if val.strip().lower() in ['yes', '1', 'true'] else 0.0
                return float(val or 0.0)
            feat_list = [
                float(inputs.get('Headache Intensity', 0)),
                map_binary(inputs.get('Cognitive Symptoms')),
                map_binary(inputs.get('Sensorimotor Symptoms')),
                map_binary(inputs.get('History of Seizures')),
                float(inputs.get('Age', 0))
            ]
            
        scaled_feat = scaler.transform([feat_list])
        model_key = f"{disease_key}_{'lr' if alt_model_type == 'Logistic Regression' else 'rf'}"
        alt_model = MODELS.get(model_key)
        
        alt_prediction = alt_model.predict(scaled_feat)[0]
        alt_prob = round(alt_model.predict_proba(scaled_feat)[0][1] * 100, 2)
        alt_result = 'High Risk' if alt_prediction == 1 else 'Low Risk'
    except Exception as e:
        print(f"Error computing model comparison: {e}")
        
    return render_template('result.html', 
                           pred=pred, 
                           inputs=inputs, 
                           recs=recs, 
                           alt_model_type=alt_model_type, 
                           alt_prob=alt_prob, 
                           alt_result=alt_result)

# --- PDF Report Generation ---
@app.route('/download_report/<int:prediction_id>')
@login_required
def download_report(prediction_id):
    pred = PredictionHistory.query.get_or_404(prediction_id)
    
    if current_user.role != 'admin' and pred.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard'))
        
    buffer = io.BytesIO()
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#198754'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    bold_style = ParagraphStyle(
        'BoldText',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("MediPredict AI - Risk Assessment Report", title_style))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Paragraph(f"Patient Name: {pred.user.username.capitalize()} | Email: {pred.user.email}", normal_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Assessment Summary", heading_style))
    risk_color = '#dc3545' if pred.prediction_result == 'High Risk' else '#198754'
    
    summary_data = [
        [Paragraph("Disease Assessed:", bold_style), Paragraph(pred.disease_type, normal_style)],
        [Paragraph("Prediction Outcome:", bold_style), Paragraph(f"<font color='{risk_color}'><b>{pred.prediction_result}</b></font>", normal_style)],
        [Paragraph("Risk Score / Probability:", bold_style), Paragraph(f"<b>{pred.probability}%</b>", normal_style)],
        [Paragraph("Machine Learning Model:", bold_style), Paragraph(pred.model_used, normal_style)]
    ]
    
    t_summary = Table(summary_data, colWidths=[150, 350])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#dee2e6'))
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Clinical Inputs Received", heading_style))
    inputs = pred.parsed_input
    
    inputs_data = [[Paragraph("Feature Description", bold_style), Paragraph("Submitted Value", bold_style)]]
    for key, value in inputs.items():
        inputs_data.append([Paragraph(key, normal_style), Paragraph(str(value), normal_style)])
        
    t_inputs = Table(inputs_data, colWidths=[250, 250])
    t_inputs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#e9ecef')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t_inputs)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Medical Advisory & Recommendations", heading_style))
    recs = get_recommendations(pred.disease_type, pred.prediction_result, inputs)
    
    recs_story = ""
    for r in recs:
        recs_story += f"• {r}<br/>"
        
    story.append(Paragraph(recs_story, normal_style))
    story.append(Spacer(1, 20))
    
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=normal_style,
        fontSize=8,
        textColor=colors.HexColor('#6c757d'),
        alignment=1
    )
    story.append(Paragraph("<b>Disclaimer:</b> MediPredict AI predictions are based on machine learning probability estimates trained on demographic research cohorts. This is an assessment platform, not a replacement for professional clinical diagnosis. Please consult a registered medical practitioner for full diagnostic evaluations.", disclaimer_style))
    
    doc.build(story)
    buffer.seek(0)
    
    filename = f"medipredict_{pred.disease_type.lower().replace(' ', '_')}_{pred.id}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

# --- Email Report ---
@app.route('/email_report/<int:prediction_id>', methods=['POST'])
@login_required
def email_report(prediction_id):
    pred = PredictionHistory.query.get_or_404(prediction_id)
    
    if current_user.role != 'admin' and pred.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
        
    recipient_email = request.form.get('email', '').strip()
    if not recipient_email:
        return jsonify({'success': False, 'message': 'Invalid Email Address'}), 400
        
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = recipient_email
        msg['Subject'] = f"MediPredict AI Risk Assessment Report - {pred.disease_type}"
        
        body = f"""
Dear Patient,

Thank you for utilizing MediPredict AI. Your medical risk assessment for {pred.disease_type} is complete.

--- Assessment Results ---
Disease: {pred.disease_type}
Risk Level: {pred.prediction_result}
Probability Score: {pred.probability}%
Model Used: {pred.model_used}
Timestamp: {pred.created_at.strftime('%Y-%m-%d %H:%M:%S')}

You can download your PDF report from your dashboard.

Disclaimer: MediPredict AI predictions are for screening and advisory purposes and do not replace professional medical diagnosis.

Warm regards,
MediPredict AI Support Team
        """
        msg.attach(MIMEText(body, 'plain'))
        
        username = app.config['MAIL_USERNAME']
        password = app.config['MAIL_PASSWORD']
        
        if username and password:
            server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            if app.config['MAIL_USE_TLS']:
                server.starttls()
            server.login(username, password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.quit()
            
            return jsonify({'success': True, 'message': f'Report emailed successfully to {recipient_email}!'})
        else:
            print(f"[Simulated Email] To: {recipient_email}\nBody: {body}")
            return jsonify({'success': True, 'simulated': True, 'message': f'Simulated transmission! Report details logged for {recipient_email}. (To configure active emails, set SMTP keys in .env)'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'SMTP Error: {str(e)}'}), 500

# --- Admin Dashboard ---
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash("Access restricted to Administrators.", "danger")
        return redirect(url_for('dashboard'))
        
    total_users = User.query.filter_by(role='patient').count()
    total_predictions = PredictionHistory.query.count()
    high_risk_preds = PredictionHistory.query.filter_by(prediction_result='High Risk').count()
    
    seed_model_performance()
    
    performances = ModelPerformance.query.all()
    recent_predictions = PredictionHistory.query.order_by(PredictionHistory.created_at.desc()).limit(50).all()
    patients = User.query.filter_by(role='patient').order_by(User.created_at.desc()).all()
    
    return render_template('admin.html',
                           total_users=total_users,
                           total_predictions=total_predictions,
                           high_risk_preds=high_risk_preds,
                           performances=performances,
                           recent_predictions=recent_predictions,
                           patients=patients)

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
