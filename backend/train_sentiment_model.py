"""
Sentiment/Emotion Classification Model Training
Trains on dailydialog.csv dataset using multiple ML approaches
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, List

import warnings
warnings.filterwarnings('ignore')

# NLP & ML Libraries
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import spacy
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_recall_fscore_support, roc_auc_score
)
import lightgbm as lgb
import joblib

# Download required NLTK data
print("Downloading NLTK resources...")
for resource in ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']:
    try:
        nltk.download(resource, quiet=True)
    except:
        pass

# Configuration
DATA_PATH = Path(__file__).parent.parent / "assets" / "dailydialog.csv"
MODEL_DIR = Path(__file__).parent / "app" / "models" / "trained"
VECTORIZER_DIR = Path(__file__).parent / "app" / "vectorizers"

# Create directories
MODEL_DIR.mkdir(parents=True, exist_ok=True)
VECTORIZER_DIR.mkdir(parents=True, exist_ok=True)

# Emotion mapping
EMOTION_LABELS = {
    'sadness': 0,
    'fear': 1,
    'anger': 2,
    'joy': 3,
    'neutral': 4
}

EMOTION_REVERSE = {v: k for k, v in EMOTION_LABELS.items()}


class DataPreprocessor:
    """Preprocess text data for model training"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Convert to lowercase
        text = text.lower()
        # Remove quotes and special markers
        text = text.replace('"', '').replace("'", '').replace("`", '')
        text = text.replace("`` ", "").replace(" ''", "")
        
        return text.strip()
    
    def tokenize_and_lemmatize(self, text: str) -> List[str]:
        """Tokenize and lemmatize text"""
        tokens = word_tokenize(text)
        # Remove stopwords and lemmatize
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token.isalpha() and token not in self.stop_words and len(token) > 2
        ]
        return tokens
    
    def extract_features(self, text: str) -> Dict:
        """Extract linguistic features from text"""
        features = {}
        
        # Basic features
        features['text_length'] = len(text)
        features['word_count'] = len(text.split())
        features['avg_word_length'] = np.mean([len(w) for w in text.split()]) if text.split() else 0
        
        # Punctuation features
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['comma_count'] = text.count(',')
        
        # Case features
        features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        return features
    
    def preprocess(self, texts: List[str]) -> Tuple[List[str], List[Dict]]:
        """Preprocess multiple texts"""
        cleaned_texts = []
        features_list = []
        
        for text in texts:
            cleaned = self.clean_text(text)
            if cleaned:
                cleaned_texts.append(cleaned)
                features_list.append(self.extract_features(cleaned))
        
        return cleaned_texts, features_list


def load_and_prepare_data(data_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Load CSV and prepare data for training"""
    print(f"\nLoading data from {data_path}...")
    
    # Load data
    df = pd.read_csv(data_path)
    
    # Remove any null values
    df = df.dropna(subset=['text', 'sentiment'])
    
    print(f"Dataset size: {len(df)} samples")
    print(f"Emotion distribution:\n{df['sentiment'].value_counts()}\n")
    
    # Prepare features and labels
    X = df['text'].values
    y = df['sentiment'].map(EMOTION_LABELS).values
    
    return X, y


def train_tfidf_random_forest() -> Tuple[Pipeline, float]:
    """Train TF-IDF + Random Forest model"""
    print("\n" + "="*60)
    print("Training TF-IDF + Random Forest Model")
    print("="*60)
    
    X, y = load_and_prepare_data(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=2000,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2),
            sublinear_tf=True
        )),
        ('classifier', RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    # Train
    print(f"Training on {len(X_train)} samples...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=EMOTION_LABELS.keys()))
    
    # Save model
    model_path = MODEL_DIR / "tfidf_random_forest.pkl"
    joblib.dump(pipeline, model_path)
    print(f"\n✓ Model saved to {model_path}")
    
    return pipeline, accuracy


def train_tfidf_lightgbm() -> Tuple[object, float]:
    """Train TF-IDF + LightGBM model (often better for text)"""
    print("\n" + "="*60)
    print("Training TF-IDF + LightGBM Model")
    print("="*60)
    
    X, y = load_and_prepare_data(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Vectorize
    vectorizer = TfidfVectorizer(
        max_features=2000,
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 2),
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train LightGBM
    print(f"Training on {len(X_train)} samples...")
    model = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    model.fit(X_train_vec.toarray(), y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_vec.toarray())
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=EMOTION_LABELS.keys()))
    
    # Save model and vectorizer
    model_path = MODEL_DIR / "tfidf_lightgbm.pkl"
    vectorizer_path = VECTORIZER_DIR / "tfidf_vectorizer.pkl"
    
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    print(f"\n✓ Model saved to {model_path}")
    print(f"✓ Vectorizer saved to {vectorizer_path}")
    
    return (model, vectorizer), accuracy


def train_ensemble_model() -> Tuple[Dict, float]:
    """Train ensemble of multiple models"""
    print("\n" + "="*60)
    print("Training Ensemble Model")
    print("="*60)
    
    X, y = load_and_prepare_data(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Vectorize
    vectorizer = TfidfVectorizer(
        max_features=2000,
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 2),
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    X_train_dense = X_train_vec.toarray()
    X_test_dense = X_test_vec.toarray()
    
    # Train multiple models
    print("Training sub-models...")
    models = {
        'random_forest': RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
        'lightgbm': lgb.LGBMClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1, verbose=0),
        'naive_bayes': MultinomialNB(),
        'gradient_boosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    }
    
    trained_models = {}
    predictions = []
    
    for name, model in models.items():
        print(f"  - Training {name}...", end=" ")
        model.fit(X_train_dense, y_train)
        trained_models[name] = model
        pred = model.predict(X_test_dense)
        predictions.append(pred)
        acc = accuracy_score(y_test, pred)
        print(f"✓ (Accuracy: {acc:.4f})")
    
    # Ensemble voting
    print("\nEnsemble voting...")
    predictions = np.array(predictions)
    ensemble_pred = np.apply_along_axis(
        lambda x: np.bincount(x.astype(int)).argmax(),
        axis=0,
        arr=predictions
    )
    
    ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
    print(f"Ensemble Accuracy: {ensemble_accuracy:.4f}")
    
    print("\nEnsemble Classification Report:")
    print(classification_report(y_test, ensemble_pred, target_names=EMOTION_LABELS.keys()))
    
    # Save ensemble
    ensemble = {
        'vectorizer': vectorizer,
        'models': trained_models,
        'accuracy': ensemble_accuracy
    }
    
    ensemble_path = MODEL_DIR / "ensemble_model.pkl"
    joblib.dump(ensemble, ensemble_path)
    
    print(f"\n✓ Ensemble saved to {ensemble_path}")
    
    return ensemble, ensemble_accuracy


def create_inference_wrapper():
    """Create inference wrapper for use in the API"""
    print("\n" + "="*60)
    print("Creating Inference Wrapper")
    print("="*60)
    
    wrapper_code = '''"""
Sentiment/Emotion Inference Module
"""
import joblib
from pathlib import Path
from typing import Dict, Tuple

MODEL_DIR = Path(__file__).parent / "trained"
VECTORIZER_DIR = Path(__file__).parent.parent / "vectorizers"

EMOTION_LABELS = {
    'sadness': 0,
    'fear': 1,
    'anger': 2,
    'joy': 3,
    'neutral': 4
}

EMOTION_REVERSE = {v: k for k, v in EMOTION_LABELS.items()}

class SentimentPredictor:
    """Load and use trained sentiment models"""
    
    def __init__(self, model_type: str = 'ensemble'):
        """
        Initialize predictor with trained model
        
        Args:
            model_type: 'ensemble', 'lightgbm', or 'random_forest'
        """
        self.model_type = model_type
        
        if model_type == 'ensemble':
            self.model = joblib.load(MODEL_DIR / "ensemble_model.pkl")
            self.vectorizer = self.model['vectorizer']
            self.models = self.model['models']
        elif model_type == 'lightgbm':
            self.model = joblib.load(MODEL_DIR / "tfidf_lightgbm.pkl")
            self.vectorizer = joblib.load(VECTORIZER_DIR / "tfidf_vectorizer.pkl")
        elif model_type == 'random_forest':
            self.model = joblib.load(MODEL_DIR / "tfidf_random_forest.pkl")
            self.vectorizer = None  # Vectorizer is in pipeline
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def predict_emotion(self, text: str) -> Tuple[str, float]:
        """
        Predict emotion for text
        
        Returns:
            Tuple of (emotion_label, confidence)
        """
        if not text or not isinstance(text, str):
            return 'neutral', 0.0
        
        try:
            if self.model_type == 'ensemble':
                X_vec = self.vectorizer.transform([text]).toarray()
                predictions = []
                for name, model in self.models.items():
                    pred = model.predict(X_vec)[0]
                    predictions.append(pred)
                
                # Vote
                prediction = max(set(predictions), key=predictions.count)
                
                # Get probabilities
                probs = np.mean([
                    model.predict_proba(X_vec)[0] 
                    for model in self.models.values()
                ], axis=0)
                confidence = probs[prediction]
                
            elif self.model_type == 'lightgbm':
                X_vec = self.vectorizer.transform([text]).toarray()
                prediction = self.model.predict(X_vec)[0]
                confidence = np.max(self.model.predict_proba(X_vec)[0])
                
            else:  # random_forest
                prediction = self.model.predict([text])[0]
                confidence = np.max(self.model.named_steps['classifier'].predict_proba([text])[0])
            
            emotion = EMOTION_REVERSE.get(prediction, 'neutral')
            return emotion, float(confidence)
        
        except Exception as e:
            print(f"Prediction error: {e}")
            return 'neutral', 0.0
    
    def predict_batch(self, texts: list) -> list:
        """Predict emotions for multiple texts"""
        results = []
        for text in texts:
            emotion, confidence = self.predict_emotion(text)
            results.append({
                'text': text[:100],
                'emotion': emotion,
                'confidence': confidence
            })
        return results

# Default predictor instance
_predictor = None

def get_predictor(model_type: str = 'ensemble') -> SentimentPredictor:
    """Get or create sentiment predictor"""
    global _predictor
    if _predictor is None:
        _predictor = SentimentPredictor(model_type)
    return _predictor

def predict_sentiment(text: str) -> Dict:
    """Quick sentiment prediction"""
    predictor = get_predictor()
    emotion, confidence = predictor.predict_emotion(text)
    return {
        'emotion': emotion,
        'confidence': confidence,
        'encoded': EMOTION_LABELS.get(emotion, 4)
    }
'''
    
    inference_path = Path(__file__).parent / "app" / "models" / "inference.py"
    inference_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add numpy import
    inference_code = "import numpy as np\n" + wrapper_code
    
    with open(inference_path, 'w') as f:
        f.write(inference_code)
    
    print(f"✓ Inference wrapper created at {inference_path}")


def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("TRUTHLENS AI - SENTIMENT MODEL TRAINING PIPELINE")
    print("="*60)
    
    # Check data exists
    if not DATA_PATH.exists():
        print(f"\n❌ Data file not found: {DATA_PATH}")
        print("Please ensure dailydialog.csv exists in assets/ folder")
        return
    
    print(f"\n📊 Data source: {DATA_PATH}")
    print(f"📁 Models will be saved to: {MODEL_DIR}")
    
    # Train models
    accuracies = {}
    
    # Model 1: Random Forest
    try:
        _, acc = train_tfidf_random_forest()
        accuracies['Random Forest'] = acc
    except Exception as e:
        print(f"Error training Random Forest: {e}")
    
    # Model 2: LightGBM
    try:
        _, acc = train_tfidf_lightgbm()
        accuracies['LightGBM'] = acc
    except Exception as e:
        print(f"Error training LightGBM: {e}")
    
    # Model 3: Ensemble
    try:
        _, acc = train_ensemble_model()
        accuracies['Ensemble'] = acc
    except Exception as e:
        print(f"Error training Ensemble: {e}")
    
    # Create inference wrapper
    try:
        create_inference_wrapper()
    except Exception as e:
        print(f"Error creating inference wrapper: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TRAINING COMPLETE - SUMMARY")
    print("="*60)
    
    for model_name, accuracy in sorted(accuracies.items(), key=lambda x: x[1], reverse=True):
        print(f"{model_name:20} Accuracy: {accuracy:.4f}")
    
    print("\n✓ All models trained and saved!")
    print("\nTo use in inference:")
    print("  from app.models.inference import get_predictor")
    print("  predictor = get_predictor('ensemble')")
    print("  emotion, confidence = predictor.predict_emotion('I am very happy!')")


if __name__ == "__main__":
    main()
