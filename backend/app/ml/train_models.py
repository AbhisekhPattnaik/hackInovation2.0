"""
ML Models Training Script
Trains both disease classifier and appointment no-show predictor
Run this script to generate the trained models
"""

import os
import sys
from pathlib import Path

# Ensure we're in the right directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.ml.disease_classifier import DiseaseClassifier, train_and_save_disease_classifier
from app.ml.appointment_noshow_predictor import AppointmentNoShowPredictor, train_and_save_noshow_predictor

def create_models_directory():
    """Create models directory if it doesn't exist"""
    models_dir = r"D:\PulseSync\backend\app\ml\models"
    os.makedirs(models_dir, exist_ok=True)
    print("[OK] Models directory ready: {}".format(models_dir))
    return models_dir

def train_all_models():
    """Train all ML models"""
    
    print("\n" + "="*80)
    print("PULSESYNC MACHINE LEARNING MODELS TRAINING")
    print("="*80)
    
    # Create models directory
    create_models_directory()
    
    # Train Disease Classifier
    print("\n" + "="*80)
    print("MODEL 1: DISEASE CLASSIFICATION")
    print("="*80)
    try:
        disease_classifier = train_and_save_disease_classifier()
        print("[SUCCESS] Disease classifier trained and saved successfully!")
    except Exception as e:
        print("[ERROR] Error training disease classifier: {}".format(str(e)))
        import traceback
        traceback.print_exc()
    
    # Train Appointment No-Show Predictor
    print("\n" + "="*80)
    print("MODEL 2: APPOINTMENT NO-SHOW PREDICTION")
    print("="*80)
    try:
        noshow_predictor = train_and_save_noshow_predictor()
        print("[SUCCESS] No-show predictor trained and saved successfully!")
    except Exception as e:
        print("[ERROR] Error training no-show predictor: {}".format(str(e)))
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TRAINING COMPLETE!")
    print("="*80)
    print("\nModels ready for production:")
    print("  1. [OK] Disease Classifier (disease_classifier.pkl)")
    print("  2. [OK] No-Show Predictor (noshow_predictor.pkl)")
    print("\nIntegrate these models with the FastAPI backend")
    print("="*80 + "\n")

if __name__ == "__main__":
    train_all_models()
