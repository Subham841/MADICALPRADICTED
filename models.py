from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='patient')  # 'patient' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    predictions = db.relationship('PredictionHistory', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    disease_type = db.Column(db.String(50), nullable=False)  # 'Diabetes', 'Heart Disease', 'Kidney Disease'
    input_data = db.Column(db.Text, nullable=False)  # JSON string of input values
    prediction_result = db.Column(db.String(50), nullable=False)  # 'High Risk' or 'Low Risk'
    probability = db.Column(db.Float, nullable=False)  # Probability percentage (0 to 100)
    model_used = db.Column(db.String(100), nullable=False)  # 'Random Forest' or 'Logistic Regression'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def parsed_input(self):
        try:
            return json.loads(self.input_data)
        except Exception:
            return {}

class ModelPerformance(db.Model):
    __tablename__ = 'model_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    disease_type = db.Column(db.String(50), nullable=False)  # 'Diabetes', 'Heart Disease', 'Kidney Disease'
    model_name = db.Column(db.String(100), nullable=False)  # 'Random Forest', 'Logistic Regression'
    accuracy = db.Column(db.Float, nullable=False)
    precision_score = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    confusion_matrix = db.Column(db.Text, nullable=False)  # JSON string of [[TN, FP], [FN, TP]]
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def parsed_matrix(self):
        try:
            return json.loads(self.confusion_matrix)
        except Exception:
            return [[0,0],[0,0]]
