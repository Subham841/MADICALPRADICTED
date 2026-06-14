# MediPredict AI - Basic Verification Script

import os
import sys

def verify():
    print("Starting verification checks...")
    
    # Check key files exist
    required_files = [
        'app.py', 'config.py', 'models.py', 'train_models.py', 
        'requirements.txt', 'schema.sql'
    ]
    
    missing_files = []
    for f in required_files:
        if not os.path.exists(f):
            missing_files.append(f)
            
    if missing_files:
        print(f"ERROR: Missing crucial files: {missing_files}")
        return False
        
    print("✓ All crucial source files are present in the directory.")
    
    # Try importing modules
    try:
        from app import app
        from models import User, PredictionHistory, ModelPerformance
        print("✓ Successfully imported app.py, models.py, and database entities.")
    except Exception as e:
        print(f"ERROR: Importing modules failed: {e}")
        return False
        
    print("\n==============================================")
    print("MediPredict AI Verification: SUCCESS!")
    print("==============================================")
    print("Please follow the setup instructions:")
    print("1. Set up a virtual environment: python -m venv venv")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run training: python train_models.py")
    print("4. Start backend: python app.py")
    print("==============================================")
    return True

if __name__ == '__main__':
    success = verify()
    sys.exit(0 if success else 1)
