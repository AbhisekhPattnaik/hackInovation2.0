#!/usr/bin/env python
"""Simple ML Model Training Script - No Unicode Characters"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import pickle
import os

def train_disease_model():
    """Train disease classifier"""
    print("="*70)
    print("TRAINING DISEASE CLASSIFIER")
    print("="*70)
    
    try:
        dataset_path = r"D:\PulseSync\classification dataset\dataset.csv"
        severity_path = r"D:\PulseSync\classification dataset\Symptom-severity.csv"
        desc_path = r"D:\PulseSync\classification dataset\symptom_Description.csv"
        
        print("Loading datasets...")
        diseases_df = pd.read_csv(dataset_path)
        severity_df = pd.read_csv(severity_path)
        desc_df = pd.read_csv(desc_path)
        
        print("[OK] Loaded {} disease records".format(len(diseases_df)))
        print("[OK] Loaded {} symptoms".format(len(severity_df)))
        print("[OK] Loaded {} descriptions".format(len(desc_df)))
        
        # Parse symptoms
        print("[PROCESSING] Building feature matrix...")
        symptom_severity = dict(zip(severity_df['Symptom'], severity_df['weight']))
        all_symptoms = set()
        
        for col in diseases_df.columns[1:]:
            for symptoms_str in diseases_df[col].dropna():
                if isinstance(symptoms_str, str):
                    symptoms = [s.strip().lower() for s in symptoms_str.split(',')]
                    all_symptoms.update(symptoms)
        
        all_symptoms = sorted(list(all_symptoms))
        print("[OK] Found {} unique symptoms".format(len(all_symptoms)))
        
        # Create features
        X_data = []
        y_data = []
        
        for _, row in diseases_df.iterrows():
            disease = row['Disease']
            features = np.zeros(len(all_symptoms))
            symptom_encoder = {s: i for i, s in enumerate(all_symptoms)}
            
            for col in diseases_df.columns[1:]:
                symptoms_str = row[col]
                if isinstance(symptoms_str, str) and symptoms_str.strip():
                    symptoms = [s.strip().lower() for s in symptoms_str.split(',')]
                    for symptom in symptoms:
                        if symptom in symptom_encoder:
                            idx = symptom_encoder[symptom]
                            sev = symptom_severity.get(symptom, 1)
                            features[idx] = sev
            
            X_data.append(features)
            y_data.append(disease)
        
        X = np.array(X_data)
        y = np.array(y_data)
        
        print("[OK] Feature matrix shape: {}".format(X.shape))
        print("[OK] Classes: {}".format(len(np.unique(y))))
        
        # Train
        print("[STATUS] Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print("[OK] Train: {} samples".format(len(X_train)))
        print("[OK] Test: {} samples".format(len(X_test)))
        
        print("[STATUS] Training model...")
        model = GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.05, max_depth=8,
            random_state=42, verbose=0
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))
        train_f1 = f1_score(y_train, model.predict(X_train), average='weighted', zero_division=0)
        test_f1 = f1_score(y_test, model.predict(X_test), average='weighted', zero_division=0)
        
        print("\n" + "="*70)
        print("DISEASE CLASSIFIER - RESULTS")
        print("="*70)
        print("Train Accuracy: {:.4f}".format(train_acc))
        print("Test Accuracy : {:.4f}".format(test_acc))
        print("Train F1      : {:.4f}".format(train_f1))
        print("Test F1       : {:.4f}".format(test_f1))
        print("="*70)
        
        # Save
        os.makedirs(r"D:\PulseSync\backend\app\ml\models", exist_ok=True)
        model_data = {
            'model': model,
            'symptom_encoder': {s: i for i, s in enumerate(all_symptoms)},
            'symptom_severity': symptom_severity,
            'symptom_list': all_symptoms,
            'model_performance': {
                'train_accuracy': float(train_acc),
                'test_accuracy': float(test_acc)
            }
        }
        
        model_path = r"D:\PulseSync\backend\app\ml\models\disease_classifier.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print("[OK] Model saved to {}".format(model_path))
        return True
        
    except Exception as e:
        print("[ERROR] {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

def train_noshow_model():
    """Train no-show predictor"""
    print("\n" + "="*70)
    print("TRAINING NO-SHOW PREDICTOR")
    print("="*70)
    
    try:
        dataset_path = r"D:\PulseSync\appointment dataset.csv"
        
        print("Loading appointment data...")
        df = pd.read_csv(dataset_path)
        print("[OK] Loaded {} records".format(len(df)))
        
        # Preprocess
        print("[PROCESSING] Engineering features...")
        df['Age'] = df['Age'].fillna(df['Age'].median())
        df['days_advance_booking'] = pd.to_datetime(df['AppointmentDay']) - pd.to_datetime(df['ScheduledDay'])
        df['days_advance_booking'] = df['days_advance_booking'].dt.days
        
        features_list = [
            'Age', 'days_advance_booking', 'Diabetes', 'Hypertension',
            'Alcoholism', 'SMS_received'
        ]
        
        X = df[features_list].fillna(0).values
        y = (df['No-show'] == 'Yes').astype(int).values
        
        print("[OK] Features: {}".format(X.shape))
        print("[OK] Target distribution: {} positive, {} negative".format(
            np.sum(y), len(y) - np.sum(y)
        ))
        
        # Train
        print("[STATUS] Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        print("[OK] Train: {} samples".format(len(X_train)))
        print("[OK] Test: {} samples".format(len(X_test)))
        
        print("[STATUS] Training model...")
        model = GradientBoostingClassifier(n_estimators=100, random_state=42, verbose=0)
        model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))
        
        print("\n" + "="*70)
        print("NO-SHOW PREDICTOR - RESULTS")
        print("="*70)
        print("Train Accuracy: {:.4f}".format(train_acc))
        print("Test Accuracy : {:.4f}".format(test_acc))
        print("="*70)
        
        # Save
        os.makedirs(r"D:\PulseSync\backend\app\ml\models", exist_ok=True)
        model_data = {
            'model': model,
            'features': features_list,
            'model_performance': {
                'train_accuracy': float(train_acc),
                'test_accuracy': float(test_acc)
            }
        }
        
        model_path = r"D:\PulseSync\backend\app\ml\models\noshow_predictor.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print("[OK] Model saved to {}".format(model_path))
        return True
        
    except Exception as e:
        print("[ERROR] {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PULSESYNC ML TRAINING")
    print("="*70 + "\n")
    
    disease_ok = train_disease_model()
    noshow_ok = train_noshow_model()
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print("Disease Classifier: {}".format("SUCCESS" if disease_ok else "FAILED"))
    print("No-Show Predictor : {}".format("SUCCESS" if noshow_ok else "FAILED"))
    print("="*70 + "\n")
