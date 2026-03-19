"""
Appointment No-Show Prediction Model
Predicts whether patients will miss their appointments
Helps optimize queue management and reduce idle time
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score
import pickle
import os
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

class AppointmentNoShowPredictor:
    """
    Predict appointment no-show probability using gradient boosting
    Features: demographics, medical history, scheduling patterns
    Helps optimize queue management and resource allocation
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_performance = {}
        self.feature_importance = {}
        
    def load_and_preprocess(self, dataset_path):
        """Load and prepare appointment dataset"""
        
        print("Loading appointment dataset...")
        df = pd.read_csv(dataset_path)
        
        print(f"[OK] Loaded {len(df)} appointment records")
        print(f"[OK] Features: {df.columns.tolist()}")
        print(f"[OK] No-show distribution:\n{df['No-show'].value_counts()}")
        
        return df
    
    def engineer_features(self, df):
        """Create advanced features from raw data"""
        
        df_processed = df.copy()
        
        # Handle missing values first
        df_processed['Age'] = df_processed['Age'].fillna(df_processed['Age'].median())
        
        # Convert dates to datetime
        df_processed['ScheduledDay'] = pd.to_datetime(df_processed['ScheduledDay'])
        df_processed['AppointmentDay'] = pd.to_datetime(df_processed['AppointmentDay'])
        
        # Time-based features
        df_processed['days_advance_booking'] = (
            df_processed['AppointmentDay'] - df_processed['ScheduledDay']
        ).dt.days
        
        df_processed['appointment_month'] = df_processed['AppointmentDay'].dt.month
        df_processed['appointment_weekday'] = df_processed['AppointmentDay'].dt.weekday
        df_processed['is_weekend_appt'] = (df_processed['appointment_weekday'] >= 5).astype(int)
        
        # Patient risk factors
        df_processed['has_hypertension'] = df_processed['Hipertension']
        df_processed['has_diabetes'] = df_processed['Diabetes']
        df_processed['has_alcoholism'] = df_processed['Alcoholism']
        df_processed['has_disability'] = df_processed['Handcap']
        df_processed['on_scholarship'] = df_processed['Scholarship']
        
        # Medical complexity score (number of conditions)
        df_processed['medical_complexity'] = (
            df_processed['has_hypertension'] + 
            df_processed['has_diabetes'] + 
            df_processed['has_alcoholism']
        )
        
        # Communication features
        df_processed['received_sms_reminder'] = df_processed['SMS_received']
        
        # Demographics
        df_processed['age'] = df_processed['Age']
        df_processed['is_female'] = (df_processed['Gender'] == 'F').astype(int)
        age_group = pd.cut(df_processed['Age'], bins=[0, 18, 35, 50, 65, 150], labels=[0, 1, 2, 3, 4])
        df_processed['age_group'] = age_group.fillna(2).astype(int)  # Fill NaN with middle group and convert
        
        # Neighborhood - one hot encode top neighborhoods
        top_neighborhoods = df_processed['Neighbourhood'].value_counts().head(10).index
        for neighborhood in top_neighborhoods:
            df_processed[f'neighborhood_{neighborhood}'] = (df_processed['Neighbourhood'] == neighborhood).astype(int)
        
        # Remove unnecessary columns
        df_processed = df_processed.drop([
            'PatientId', 'AppointmentID', 'ScheduledDay', 'AppointmentDay',
            'Gender', 'Neighbourhood', 'Hipertension', 'Diabetes', 'Alcoholism',
            'Handcap', 'SMS_received', 'Scholarship', 'Age'
        ], axis=1)
        
        print(f"[OK] Feature engineering complete")
        print(f"[OK] Features created: {df_processed.shape[1] - 1}")
        print(f"[OK] Dataset shape: {df_processed.shape}")
        
        return df_processed
    
    def train(self, dataset_path, test_size=0.2):
        """Train the no-show prediction model"""
        
        print("\n" + "="*60)
        print("TRAINING APPOINTMENT NO-SHOW PREDICTOR")
        print("="*60)
        
        # Load and preprocess
        df = self.load_and_preprocess(dataset_path)
        df = self.engineer_features(df)
        
        # Prepare features and target
        X = df.drop('No-show', axis=1)
        y = (df['No-show'] == 'Yes').astype(int)
        
        self.feature_names = X.columns.tolist()
        
        print(f"\nNo-show rate: {y.mean():.2%}")
        print(f"Imbalance ratio: 1:{(y==0).sum() / (y==1).sum():.1f}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"\n[OK] Train set: {X_train.shape[0]} samples")
        print(f"[OK] Test set: {X_test.shape[0]} samples")
        print(f"[OK] Features: {X_train.shape[1]}")
        
        # Train ensemble model
        print("\n→ Training ensemble classifier...")
        
        gb_model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.08,
            max_depth=7,
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,
            random_state=42
        )
        
        self.model = gb_model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        y_test_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        train_f1 = f1_score(y_train, y_train_pred)
        test_f1 = f1_score(y_test, y_test_pred)
        test_auc = roc_auc_score(y_test, y_test_proba)
        
        self.model_performance = {
            'train_f1': float(train_f1),
            'test_f1': float(test_f1),
            'test_auc': float(test_auc),
            'num_features': X_train.shape[1],
            'training_samples': X_train.shape[0],
            'test_samples': X_test.shape[0],
            'no_show_rate': float(y.mean())
        }
        
        # Feature importance
        gb_importance = self.model.feature_importances_
        
        feature_importance_dict = {}
        for name, importance in zip(self.feature_names, gb_importance):
            feature_importance_dict[name] = float(importance)
        
        # Sort by importance
        self.feature_importance = dict(sorted(
            feature_importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )[:15])
        
        print("\n" + "="*60)
        print("MODEL PERFORMANCE METRICS")
        print("="*60)
        print(f"Training F1-Score:   {train_f1:.4f}")
        print(f"Test F1-Score:       {test_f1:.4f}")
        print(f"Test AUC-ROC:        {test_auc:.4f}")
        print(f"Total Features:      {X_train.shape[1]}")
        print("="*60)
        
        print("\nTop 10 Most Important Features:")
        print("-" * 40)
        for i, (feature, importance) in enumerate(list(self.feature_importance.items())[:10], 1):
            print(f"{i:2d}. {feature:30s} {importance:.4f}")
        print("-" * 40)
        
        return self.model, self.model_performance
    
    def predict_no_show_probability(self, appointment_data):
        """
        Predict no-show probability for a specific appointment
        
        appointment_data should contain:
        - age, is_female, age_group
        - days_advance_booking
        - has_hypertension, has_diabetes, has_alcoholism
        - medical_complexity
        - received_sms_reminder
        - appointment_month, appointment_weekday, is_weekend_appt
        - neighborhood features
        """
        
        if not self.model:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create feature vector with all expected features
        features = pd.DataFrame(columns=self.feature_names)
        
        # Add the appointment data
        for key, value in appointment_data.items():
            if key in self.feature_names:
                features[key] = [value]
        
        # Fill any missing features with 0
        for col in self.feature_names:
            if col not in features.columns:
                features[col] = [0]
        
        # Ensure all columns are in the right order
        features = features[self.feature_names]
        
        # Handle any remaining NaN values
        features = features.fillna(0)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict probability
        no_show_prob = self.model.predict_proba(features_scaled)[0, 1]
        risk_level = self._get_risk_level(no_show_prob)
        recommendations = self._get_recommendations(no_show_prob, appointment_data)
        
        return {
            'no_show_probability': float(no_show_prob),
            'risk_level': risk_level,
            'recommendations': recommendations,
            'confidence': float(max(self.model.predict_proba(features_scaled)[0]))
        }
    
    def _get_risk_level(self, probability):
        """Categorize risk level"""
        if probability < 0.15:
            return "Low Risk"
        elif probability < 0.35:
            return "Medium Risk"
        elif probability < 0.55:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _get_recommendations(self, probability, data):
        """Generate recommendations based on risk"""
        recs = []
        
        if probability > 0.4:
            recs.append("Send reminder SMS/Email 24 hours before appointment")
            recs.append("Consider confirming appointment via call")
        
        if data.get('days_advance_booking', 0) > 14:
            recs.append("Early booking detected - send confirmation reminder")
        
        if not data.get('received_sms_reminder', False):
            recs.append("Enable SMS reminders to reduce no-show rate")
        
        if data.get('medical_complexity', 0) == 0:
            recs.append("High-risk patient - prioritize reminder follow-up")
        
        if data.get('is_weekend_appt', False):
            recs.append("Weekend appointment - higher no-show risk")
        
        return recs if recs else ["Standard reminder protocol recommended"]
    
    def save(self, model_path):
        """Save trained model and scaler"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_performance': self.model_performance,
            'feature_importance': self.feature_importance
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"[OK] Model saved to {model_path}")
    
    @classmethod
    def load(cls, model_path):
        """Load trained model from disk"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        predictor = cls()
        predictor.model = model_data['model']
        predictor.scaler = model_data['scaler']
        predictor.feature_names = model_data['feature_names']
        predictor.model_performance = model_data['model_performance']
        predictor.feature_importance = model_data['feature_importance']
        
        print(f"[OK] Model loaded from {model_path}")
        return predictor


def train_and_save_noshow_predictor():
    """Train and save the no-show prediction model"""
    
    predictor = AppointmentNoShowPredictor()
    
    dataset_path = r"D:\PulseSync\aapointment dataset\KaggleV2-May-2016.csv"
    
    # Train model
    predictor.train(dataset_path)
    
    # Save model
    model_save_path = r"D:\PulseSync\backend\app\ml\models\noshow_predictor.pkl"
    predictor.save(model_save_path)
    
    # Test predictions
    print("\n" + "="*60)
    print("TESTING PREDICTIONS")
    print("="*60)
    
    test_cases = [
        {  # Low risk patient
            'age': 30, 'is_female': 1, 'age_group': 1,
            'days_advance_booking': 7,
            'has_hypertension': 0, 'has_diabetes': 0, 'has_alcoholism': 0,
            'medical_complexity': 0,
            'received_sms_reminder': 1,
            'appointment_month': 4, 'appointment_weekday': 2, 'is_weekend_appt': 0
        },
        {  # High risk patient
            'age': 60, 'is_female': 0, 'age_group': 4,
            'days_advance_booking': 30,
            'has_hypertension': 1, 'has_diabetes': 1, 'has_alcoholism': 1,
            'medical_complexity': 3,
            'received_sms_reminder': 0,
            'appointment_month': 4, 'appointment_weekday': 5, 'is_weekend_appt': 1
        }
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        result = predictor.predict_no_show_probability(test_data)
        print(f"No-show Probability: {result['no_show_probability']:.2%}")
        print(f"Risk Level:          {result['risk_level']}")
        print(f"Recommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
    
    return predictor


if __name__ == "__main__":
    train_and_save_noshow_predictor()
