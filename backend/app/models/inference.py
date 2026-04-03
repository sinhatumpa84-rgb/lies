"""
Sentiment/Emotion Inference Module
Uses trained models for real-time emotion prediction
"""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

# Model paths
MODEL_DIR = Path(__file__).parent / "trained"
VECTORIZER_DIR = Path(__file__).parent.parent / "vectorizers"

# Emotion labels mapping
EMOTION_LABELS = {
    'sadness': 0,
    'fear': 1,
    'anger': 2,
    'joy': 3,
    'neutral': 4
}

EMOTION_REVERSE = {v: k for k, v in EMOTION_LABELS.items()}

# Emotion to severity mapping for risk assessment
EMOTION_SEVERITY = {
    'fear': 'high',
    'anger': 'high',
    'sadness': 'medium',
    'joy': 'low',
    'neutral': 'low'
}


class SentimentPredictor:
    """Load and use trained sentiment models"""
    
    def __init__(self, model_type: str = 'ensemble'):
        """
        Initialize predictor with trained model
        
        Args:
            model_type: 'ensemble', 'lightgbm', or 'random_forest'
        """
        self.model_type = model_type
        self.models_loaded = False
        
        try:
            if model_type == 'ensemble':
                ensemble_data = joblib.load(MODEL_DIR / "ensemble_model.pkl")
                self.vectorizer = ensemble_data['vectorizer']
                self.models = ensemble_data['models']
                self.model = None
            elif model_type == 'lightgbm':
                self.model = joblib.load(MODEL_DIR / "tfidf_lightgbm.pkl")
                self.vectorizer = joblib.load(VECTORIZER_DIR / "tfidf_vectorizer.pkl")
                self.models = None
            elif model_type == 'random_forest':
                self.model = joblib.load(MODEL_DIR / "tfidf_random_forest.pkl")
                self.vectorizer = None  # Vectorizer is in pipeline
                self.models = None
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            self.models_loaded = True
        except Exception as e:
            print(f"Warning: Could not load {model_type} model: {e}")
            self.model = None
            self.models = None
            self.vectorizer = None
            self.models_loaded = False
    
    def predict_emotion(self, text: str) -> Tuple[str, float]:
        """
        Predict emotion for text
        
        Returns:
            Tuple of (emotion_label, confidence)
        """
        if not text or not isinstance(text, str) or not self.models_loaded:
            return 'neutral', 0.0
        
        try:
            if self.model_type == 'ensemble':
                X_vec = self.vectorizer.transform([text]).toarray()
                predictions = []
                
                for name, model in self.models.items():
                    pred = model.predict(X_vec)[0]
                    predictions.append(pred)
                
                # Vote
                unique, counts = np.unique(predictions, return_counts=True)
                prediction = unique[np.argmax(counts)]
                
                # Get average probability
                probs = np.mean([
                    np.eye(len(EMOTION_LABELS))[p] * (1.0 / len(self.models))
                    for p in predictions
                ], axis=0)
                
                confidence = float(np.max(probs))
                
            elif self.model_type == 'lightgbm':
                X_vec = self.vectorizer.transform([text]).toarray()
                prediction = self.model.predict(X_vec)[0]
                probs = self.model.predict_proba(X_vec)[0]
                confidence = float(np.max(probs))
                
            else:  # random_forest
                prediction = self.model.predict([text])[0]
                probs = self.model.named_steps['classifier'].predict_proba(
                    self.model.named_steps['tfidf'].transform([text])
                )[0]
                confidence = float(np.max(probs))
            
            emotion = EMOTION_REVERSE.get(int(prediction), 'neutral')
            return emotion, confidence
        
        except Exception as e:
            print(f"Prediction error: {e}")
            return 'neutral', 0.0
    
    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """Predict emotions for multiple texts"""
        results = []
        for text in texts:
            emotion, confidence = self.predict_emotion(text)
            results.append({
                'text': text[:100] if len(text) > 100 else text,
                'emotion': emotion,
                'confidence': confidence,
                'severity': EMOTION_SEVERITY.get(emotion, 'low')
            })
        return results
    
    def get_emotion_probabilities(self, text: str) -> Dict[str, float]:
        """Get probability distribution across all emotions"""
        if not text or not isinstance(text, str) or not self.models_loaded:
            return {emotion: 0.0 for emotion in EMOTION_LABELS.keys()}
        
        try:
            if self.model_type == 'ensemble':
                X_vec = self.vectorizer.transform([text]).toarray()
                probs_list = []
                
                for name, model in self.models.items():
                    try:
                        probs = model.predict_proba(X_vec)[0]
                    except:
                        # For naive bayes that might not have predict_proba
                        pred = model.predict(X_vec)[0]
                        probs = np.eye(len(EMOTION_LABELS))[int(pred)]
                    probs_list.append(probs)
                
                avg_probs = np.mean(probs_list, axis=0)
                
            elif self.model_type == 'lightgbm':
                X_vec = self.vectorizer.transform([text]).toarray()
                avg_probs = self.model.predict_proba(X_vec)[0]
                
            else:  # random_forest
                X_vec = self.model.named_steps['tfidf'].transform([text])
                avg_probs = self.model.named_steps['classifier'].predict_proba(X_vec)[0]
            
            return {emotion: float(avg_probs[idx]) for emotion, idx in EMOTION_LABELS.items()}
        
        except Exception as e:
            print(f"Error getting probabilities: {e}")
            return {emotion: 0.0 for emotion in EMOTION_LABELS.keys()}


# Global predictor instance
_predictors = {}


def get_predictor(model_type: str = 'ensemble') -> SentimentPredictor:
    """Get or create sentiment predictor (cached)"""
    global _predictors
    
    if model_type not in _predictors:
        _predictors[model_type] = SentimentPredictor(model_type)
    
    return _predictors[model_type]


def predict_sentiment(text: str, model_type: str = 'ensemble') -> Dict:
    """
    Quick sentiment prediction
    
    Args:
        text: Text to analyze
        model_type: Which trained model to use
    
    Returns:
        Dictionary with emotion, confidence, and metadata
    """
    predictor = get_predictor(model_type)
    emotion, confidence = predictor.predict_emotion(text)
    probs = predictor.get_emotion_probabilities(text)
    
    return {
        'emotion': emotion,
        'confidence': confidence,
        'encoded': EMOTION_LABELS.get(emotion, 4),
        'severity': EMOTION_SEVERITY.get(emotion, 'low'),
        'probabilities': probs
    }


def analyze_message_emotions(messages: List[str]) -> Dict:
    """
    Analyze emotional progression across multiple messages
    
    Args:
        messages: List of message texts
    
    Returns:
        Analysis with emotion timeline and statistics
    """
    predictor = get_predictor()
    emotions = []
    confidences = []
    
    for msg in messages:
        emotion, conf = predictor.predict_emotion(msg)
        emotions.append(emotion)
        confidences.append(conf)
    
    # Calculate emotional metrics
    emotion_counts = {}
    for emotion in emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Detect mood swings (changes between different emotions)
    mood_swings = 0
    for i in range(1, len(emotions)):
        if emotions[i] != emotions[i-1]:
            mood_swings += 1
    
    # Average confidence
    avg_confidence = float(np.mean(confidences)) if confidences else 0.0
    
    return {
        'emotions': emotions,
        'emotion_distribution': emotion_counts,
        'mood_swings': mood_swings,
        'average_confidence': avg_confidence,
        'dominant_emotion': max(emotion_counts, key=emotion_counts.get),
        'emotional_volatility': mood_swings / max(len(emotions) - 1, 1)
    }
