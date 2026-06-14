-- MediPredict AI Database Schema (MySQL)

CREATE DATABASE IF NOT EXISTS medipredict;
USE medipredict;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(50) DEFAULT 'patient',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Prediction History Table
CREATE TABLE IF NOT EXISTS prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    disease_type VARCHAR(50) NOT NULL,
    input_data TEXT NOT NULL,
    prediction_result VARCHAR(50) NOT NULL,
    probability FLOAT NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Performance Table
CREATE TABLE IF NOT EXISTS model_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    disease_type VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    accuracy FLOAT NOT NULL,
    precision_score FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    confusion_matrix TEXT NOT NULL,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert Admin User Default Seed (Password: admin123)
-- Hash generated using pbkdf2:sha256:260000$ in Werkzeug
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@medipredict.ai', 'pbkdf2:sha256:260000$jU0B9r4378t1d1f0$cc688a202a0a2df3324dcd93d395781a9adbf0885c192d3b25a3adbf042b45cf', 'admin')
ON DUPLICATE KEY UPDATE id=id;
