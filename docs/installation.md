# Installation Guide: MediPredict AI

Follow these step-by-step instructions to set up, train, and run the MediPredict AI platform in a local development environment.

## Prerequisites

Ensure you have the following installed:
- **Python 3.8+**
- **Git**
- **pip** (Python package installer)
- **SQLite** (default/fallback) or **MySQL Server** (for production database structures)

---

## Step 1: Clone the Repository & Configure Directory
Navigate to your workspace directory:
```bash
# Verify you are in the application root directory
cd r:\madicalpradicted
```

---

## Step 2: Establish Virtual Environment (Recommended)
Creating an isolated environment prevents dependency conflicts:
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (CMD / Powershell)
.\venv\Scripts\activate
```

---

## Step 3: Install Required Dependencies
Install the required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## Step 4: Configure Environment Variables
Copy `.env.example` to create your active `.env` file:
```bash
copy .env.example .env
```
Open `.env` in a text editor. By default, the application uses **SQLite** (`medipredict.db` will be created in the root folder automatically). 

If you prefer to connect to **MySQL**, uncomment and update the database configuration variables in `.env`:
```ini
DB_USER=root
DB_PASSWORD=your_mysql_root_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medipredict
```
*Note: Make sure to create the database in MySQL (e.g., `CREATE DATABASE medipredict;`) before launching the application.*

---

## Step 5: Run Machine Learning Training
You must train and serialize the models before running predictions:
```bash
python train_models.py
```
This script will:
1. Generate synthetic clinical datasets for Diabetes, Heart Disease, and Chronic Kidney Disease.
2. Standardize features using Scikit-learn's `StandardScaler`.
3. Train both Random Forest and Logistic Regression models.
4. Save the trained models (`.pkl` format) and performance metrics to the `models/` directory.

---

## Step 6: Initialize & Launch the Application
Start the Flask development server:
```bash
python app.py
```
The server will initialize the database tables (SQLite or MySQL) and start running on:
**`http://127.0.0.1:5000`**

### Default Accounts:
- **Admin Portal**: 
  - Username: `admin`
  - Password: `admin123`
- **Patient Accounts**: Click **Register** on the navigation bar to create a patient profile.
