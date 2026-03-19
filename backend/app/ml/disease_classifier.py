"""
Advanced Disease Classification Model
Trained on symptom dataset to predict diseases with confidence scores
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import pickle
import os
import warnings

warnings.filterwarnings('ignore')

class DiseaseClassifier:
    """
    Multi-label disease classification system using ensemble learning
    Predicts multiple possible diseases based on patient symptoms
    """
    
    def __init__(self):
        self.model = None
        self.symptom_encoder = None
        self.disease_encoder = LabelEncoder()
        self.symptom_severity = {}
        self.disease_descriptions = {}
        self.feature_importance = {}
        self.model_performance = {}
        
    def load_datasets(self, dataset_path, symptom_severity_path, description_path):
        """Load and process all dataset files"""
        
        # Load disease-symptom mappings
        self.diseases_df = pd.read_csv(dataset_path)
        
        # Load symptom severity weights
        severity_df = pd.read_csv(symptom_severity_path)
        self.symptom_severity = dict(zip(severity_df['Symptom'], severity_df['weight']))
        
        # Load disease descriptions
        desc_df = pd.read_csv(description_path)
        self.disease_descriptions = dict(zip(desc_df['Disease'], desc_df['Description']))
        
        print(f"[OK] Loaded {len(self.diseases_df)} disease-symptom records")
        print(f"[OK] Loaded {len(self.symptom_severity)} symptoms with severity weights")
        print(f"[OK] Loaded {len(self.disease_descriptions)} disease descriptions")
        
        return self.diseases_df, self.symptom_severity, self.disease_descriptions
    
    def preprocess_data(self):
        """Convert raw symptom data into ML-ready format"""
        
        X_data = []
        y_data = []
        
        # Get all unique symptoms
        all_symptoms = set()
        for col in self.diseases_df.columns[1:]:
            for symptoms_str in self.diseases_df[col].dropna():
                if isinstance(symptoms_str, str):
                    symptoms = [s.strip().lower() for s in symptoms_str.split(',')]
                    all_symptoms.update(symptoms)
        
        all_symptoms = sorted(list(all_symptoms))
        self.symptom_list = all_symptoms
        
        print(f"[OK] Found {len(all_symptoms)} unique symptoms")
        
        # Create symptom encoder
        self.symptom_encoder = {symptom: idx for idx, symptom in enumerate(all_symptoms)}
        
        # Convert each row to feature vector
        for idx, row in self.diseases_df.iterrows():
            disease = row['Disease']
            
            # Create feature vector for this patient
            features = np.zeros(len(all_symptoms))
            
            # Collect all symptoms for this patient
            patient_symptoms = []
            for col in self.diseases_df.columns[1:]:
                symptoms_str = row[col]
                if isinstance(symptoms_str, str) and symptoms_str.strip():
                    symptoms = [s.strip().lower() for s in symptoms_str.split(',')]
                    patient_symptoms.extend(symptoms)
            
            # Encode symptoms with severity weighting
            for symptom in patient_symptoms:
                if symptom in self.symptom_encoder:
                    symptom_idx = self.symptom_encoder[symptom]
                    severity = self.symptom_severity.get(symptom, 1)
                    features[symptom_idx] = severity
            
            X_data.append(features)
            y_data.append(disease)
        
        X = np.array(X_data)
        y = np.array(y_data)
        
        print(f"[OK] Created feature matrix: {X.shape}")
        print(f"[OK] Target diseases: {len(np.unique(y))}")
        
        return X, y
    
    def train(self, dataset_path, symptom_severity_path, description_path, test_size=0.2):
        """Train the disease classification model"""
        
        print("\n" + "="*60)
        print("TRAINING DISEASE CLASSIFIER")
        print("="*60)
        
        # Load and preprocess data
        self.load_datasets(dataset_path, symptom_severity_path, description_path)
        X, y = self.preprocess_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"\n[OK] Train set: {X_train.shape[0]} samples")
        print(f"[OK] Test set: {X_test.shape[0]} samples")
        
        # Train ensemble model
        print("\n[STATUS] Training Gradient Boosting Classifier...")
        
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=8,
            min_samples_split=5,
            min_samples_leaf=2,
            subsample=0.8,
            random_state=42,
            verbose=0
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        train_f1 = f1_score(y_train, y_train_pred, average='weighted', zero_division=0)
        test_f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
        
        self.model_performance = {
            'train_accuracy': float(train_accuracy),
            'test_accuracy': float(test_accuracy),
            'train_f1': float(train_f1),
            'test_f1': float(test_f1),
            'num_diseases': len(np.unique(y)),
            'num_features': X.shape[1],
            'training_samples': X_train.shape[0],
            'test_samples': X_test.shape[0]
        }
        
        print("\n" + "="*60)
        print("MODEL PERFORMANCE METRICS")
        print("="*60)
        print(f"Training Accuracy:   {train_accuracy:.4f}")
        print(f"Test Accuracy:       {test_accuracy:.4f}")
        print(f"Training F1-Score:   {train_f1:.4f}")
        print(f"Test F1-Score:       {test_f1:.4f}")
        print(f"Disease Classes:     {len(np.unique(y))}")
        print("="*60)
        
        return self.model, self.model_performance
    
    def predict(self, symptoms: list, top_k=5):
        """
        Predict disease based on symptoms
        Returns top K predictions with confidence scores
        """
        if not self.model or not self.symptom_encoder:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create feature vector from symptoms
        features = np.zeros(len(self.symptom_encoder))
        
        input_symptoms = [s.strip().lower() for s in symptoms]
        
        for symptom in input_symptoms:
            if symptom in self.symptom_encoder:
                symptom_idx = self.symptom_encoder[symptom]
                severity = self.symptom_severity.get(symptom, 1)
                features[symptom_idx] = severity
        
        # Get predictions
        features = features.reshape(1, -1)
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        # Get class labels and sort by probability
        classes = self.model.classes_
        predictions_with_probs = list(zip(classes, probabilities))
        predictions_with_probs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top K
        results = []
        for disease, confidence in predictions_with_probs[:top_k]:
            results.append({
                'disease': disease,
                'confidence': float(confidence),
                'description': self.disease_descriptions.get(disease, 'No description available'),
                'recommended_action': self._get_recommendation(disease, confidence)
            })
        
        return {
            'primary_prediction': results[0] if results else None,
            'alternative_diagnoses': results[1:] if len(results) > 1 else [],
            'all_predictions': results,
            'input_symptoms': input_symptoms,
            'confidence_threshold': 0.15
        }
    
    def _get_recommendation(self, disease: str, confidence: float) -> str:
        """Generate recommendation based on disease and confidence"""
        if confidence < 0.3:
            return "Consider consulting a specialist for accurate diagnosis"
        elif confidence < 0.5:
            return "Strong possibility - Schedule consultation with relevant specialist"
        else:
            return "High confidence - Immediate specialist consultation recommended"
    
    def save(self, model_path):
        """Save trained model and metadata"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'symptom_encoder': self.symptom_encoder,
            'symptom_severity': self.symptom_severity,
            'disease_descriptions': self.disease_descriptions,
            'symptom_list': self.symptom_list,
            'model_performance': self.model_performance
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"[OK] Model saved to {model_path}")
    
    @classmethod
    def load(cls, model_path):
        """Load trained model from disk"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        classifier = cls()
        classifier.model = model_data['model']
        classifier.symptom_encoder = model_data['symptom_encoder']
        classifier.symptom_severity = model_data['symptom_severity']
        classifier.disease_descriptions = model_data['disease_descriptions']
        classifier.symptom_list = model_data['symptom_list']
        classifier.model_performance = model_data['model_performance']
        
        print(f"[OK] Model loaded from {model_path}")
        return classifier


def train_and_save_disease_classifier():
    """Train and save the disease classifier"""
    
    classifier = DiseaseClassifier()
    
    dataset_path = r"D:\PulseSync\classification dataset\dataset.csv"
    symptom_severity_path = r"D:\PulseSync\classification dataset\Symptom-severity.csv"
    description_path = r"D:\PulseSync\classification dataset\symptom_Description.csv"
    
    # Train model
    classifier.train(dataset_path, symptom_severity_path, description_path)
    
    # Save model
    model_save_path = r"D:\PulseSync\backend\app\ml\models\disease_classifier.pkl"
    classifier.save(model_save_path)
    
    # Test predictions
    print("\n" + "="*60)
    print("TESTING PREDICTIONS")
    print("="*60)
    
    test_symptoms = [
        ["itching", "skin_rash", "nodal_skin_eruptions"],
        ["continuous_sneezing", "shivering", "chills"],
        ["fatigue", "weight_gain", "anxiety"]
    ]
    
    for symptoms in test_symptoms:
        print(f"\nSymptoms: {symptoms}")
        result = classifier.predict(symptoms)
        print(f"Primary: {result['primary_prediction']['disease']} ({result['primary_prediction']['confidence']:.2%})")
        print(f"Recommendation: {result['primary_prediction']['recommended_action']}")
    
    return classifier


if __name__ == "__main__":
    train_and_save_disease_classifier()
