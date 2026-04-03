"""
Analysis Service - Core business logic for conversation analysis
Integrates trained ML models for emotion detection and pattern recognition
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime

# Import trained model inference
from .inference import (
    get_predictor,
    predict_sentiment,
    analyze_message_emotions,
    EMOTION_SEVERITY,
    EMOTION_LABELS
)


class PatternDetector:
    """Detect behavioral and linguistic patterns in conversations"""
    
    @staticmethod
    def detect_contradictions(messages: List[str]) -> List[Dict]:
        """Detect contradictory statements"""
        contradictions = []
        keywords_by_msg = []
        
        for i, msg in enumerate(messages):
            keywords = set(msg.lower().split())
            keywords_by_msg.append((i, keywords))
        
        # Simple contradiction detection - look for negation patterns
        for i in range(len(keywords_by_msg)):
            msg_text = messages[i].lower()
            
            # Check for contradiction patterns
            if any(neg in msg_text for neg in ["don't", "not", "never", "can't"]):
                for j in range(i + 1, len(keywords_by_msg)):
                    later_text = messages[j].lower()
                    
                    # Look for contradictory claims
                    if "was" in later_text and "wasn't" in msg_text:
                        contradictions.append({
                            'type': 'contradiction',
                            'msg_idx_1': i,
                            'msg_idx_2': j,
                            'severity': 'high'
                        })
        
        return contradictions
    
    @staticmethod
    def detect_vague_language(message: str) -> float:
        """Calculate vagueness score (0-1)"""
        vague_words = {
            'kind of', 'sort of', 'like', 'maybe', 'I think',
            'probably', 'possibly', 'somewhat', 'pretty much',
            'fairly', 'rather', 'quite', 'apparently', 'seem',
            'tends to', 'apparently', 'virtually', 'arguably'
        }
        
        msg_lower = message.lower()
        vague_count = sum(1 for word in vague_words if word in msg_lower)
        
        # Normalize by message length
        words = len(message.split())
        vagueness = vague_count / max(words, 5) if words > 0 else 0
        
        return min(vagueness, 1.0)
    
    @staticmethod
    def detect_deflection(message: str) -> bool:
        """Detect if message deflects from question"""
        deflection_patterns = [
            "what about you",
            "you're the one",
            "that's not the point",
            "anyway",
            "never mind",
            "forget it",
            "let's move on"
        ]
        
        msg_lower = message.lower()
        return any(pattern in msg_lower for pattern in deflection_patterns)
    
    @staticmethod
    def detect_over_explanation(messages: List[str]) -> float:
        """Detect over-explanation tendency"""
        if not messages:
            return 0.0
        
        # Messages with excessive length relative to others
        lengths = [len(msg.split()) for msg in messages]
        if not lengths:
            return 0.0
        
        avg_length = np.mean(lengths)
        over_explained = sum(1 for l in lengths if l > avg_length * 2)
        
        return over_explained / len(messages)


class DeceptionAnalyzer:
    """Analyze conversation for deceptive patterns"""
    
    @staticmethod
    def calculate_deception_score(messages: List[str]) -> Dict:
        """
        Calculate likelihood of deception based on multiple factors
        Returns score 0-100 and contributing factors
        """
        if not messages:
            return {'score': 50, 'factors': [], 'confidence': 0.0}
        
        factors = []
        scores = []
        
        detector = PatternDetector()
        
        # Factor 1: Message consistency (using trained emotions)
        emotions = analyze_message_emotions(messages)
        volatility = emotions['emotional_volatility']
        
        # High volatility might indicate inconsistency
        if volatility > 0.5:
            factors.append({
                'name': 'High emotional volatility',
                'weight': 3,
                'score': min(volatility * 100, 100)
            })
        
        # Factor 2: Vague language usage
        avg_vagueness = np.mean([detector.detect_vague_language(msg) for msg in messages])
        if avg_vagueness > 0.2:
            factors.append({
                'name': 'Excessive vague language',
                'weight': 3,
                'score': min(avg_vagueness * 100, 100)
            })
        
        # Factor 3: Deflection patterns
        deflections = sum(1 for msg in messages if detector.detect_deflection(msg))
        if deflections > 0:
            factors.append({
                'name': 'Message deflection',
                'weight': 2,
                'score': min((deflections / len(messages)) * 100, 100)
            })
        
        # Factor 4: Over-explanation
        over_explain = detector.detect_over_explanation(messages)
        if over_explain > 0.2:
            factors.append({
                'name': 'Over-explanation',
                'weight': 2,
                'score': min(over_explain * 100, 100)
            })
        
        # Factor 5: Response patterns (short/long imbalance)
        lengths = [len(msg.split()) for msg in messages]
        if len(set(lengths)) > 1:
            cv = np.std(lengths) / (np.mean(lengths) + 0.01)  # Coefficient of variation
            if cv > 1.5:
                factors.append({
                    'name': 'Inconsistent response length',
                    'weight': 2,
                    'score': min(cv * 100, 100)
                })
        
        # Calculate weighted average
        if factors:
            total_weight = sum(f['weight'] for f in factors)
            weighted_score = sum(f['weight'] * f['score'] for f in factors) / total_weight
        else:
            weighted_score = 50  # Neutral if no factors detected
        
        # Normalize to 0-100
        deception_score = int(min(max(weighted_score, 0), 100))
        
        # Calculate confidence
        confidence = min(len(messages) / 10, 1.0) * min(len(factors) / 5, 1.0)
        
        return {
            'score': deception_score,
            'factors': factors,
            'confidence': float(confidence),
            'recommendation': 'High suspicion' if deception_score > 70 else 'Moderate concern' if deception_score > 40 else 'Low suspicion'
        }


class GhostingAnalyzer:
    """Analyze conversation for ghosting signals"""
    
    @staticmethod
    def detect_ghosting_signals(messages: List[str]) -> Dict:
        """Detect patterns indicating ghosting behavior"""
        if not messages:
            return {
                'likelihood': 0,
                'signals': [],
                'trend': 'stable'
            }
        
        signals = []
        
        # Signal 1: Declining message length
        lengths = [len(msg.split()) for msg in messages]
        if len(lengths) > 2:
            avg_first_half = np.mean(lengths[:len(lengths)//2])
            avg_second_half = np.mean(lengths[len(lengths)//2:])
            decline = (avg_first_half - avg_second_half) / (avg_first_half + 0.01)
            
            if decline > 0.3:
                signals.append({
                    'name': 'Declining message length',
                    'weight': 3,
                    'score': min(decline * 100, 100)
                })
        
        # Signal 2: Short/minimal responses
        short_msgs = sum(1 for l in lengths if l < 3)
        if short_msgs / len(messages) > 0.3:
            signals.append({
                'name': 'Excessive short responses',
                'weight': 2,
                'score': (short_msgs / len(messages)) * 100
            })
        
        # Signal 3: Emotional withdrawal (neutral/sadness dominance)
        emotions = analyze_message_emotions(messages)
        if emotions['dominant_emotion'] in ['neutral', 'sadness']:
            emotion_score = emotions['emotion_distribution'].get(emotions['dominant_emotion'], 0) / len(messages)
            if emotion_score > 0.5:
                signals.append({
                    'name': 'Emotional withdrawal',
                    'weight': 2,
                    'score': emotion_score * 100
                })
        
        # Signal 4: Unavailability mentions
        avail_keywords = ['busy', 'tired', 'don\'t have time', 'later', 'tomorrow', 'soon']
        avail_mentions = sum(
            1 for msg in messages 
            if any(kw in msg.lower() for kw in avail_keywords)
        )
        if avail_mentions > 0:
            signals.append({
                'name': 'Unavailability mentions',
                'weight': 1,
                'score': min((avail_mentions / len(messages)) * 100, 100)
            })
        
        # Calculate likelihood
        if signals:
            total_weight = sum(s['weight'] for s in signals)
            likelihood = sum(s['weight'] * s['score'] for s in signals) / total_weight
        else:
            likelihood = 0
        
        # Determine trend
        if len(lengths) > 3:
            recent_decline = (lengths[-2] - lengths[-1]) / (lengths[-2] + 0.01)
            if recent_decline > 0.3:
                trend = 'worsening'
            elif recent_decline < -0.3:
                trend = 'improving'
            else:
                trend = 'stable'
        else:
            trend = 'unclear'
        
        return {
            'likelihood': int(likelihood),
            'signals': signals,
            'trend': trend
        }


class TrustScoreCalculator:
    """Calculate overall trust score based on multiple factors"""
    
    @staticmethod
    def calculate_trust_score(messages: List[str], analysis_type: str = 'general') -> Dict:
        """
        Calculate trust score (0-100, higher = more trustworthy)
        """
        if not messages:
            return {
                'score': 50,
                'components': {},
                'risk_level': 'unknown'
            }
        
        # Base score
        score = 70
        components = {}
        
        # Component 1: Deception analysis (negative impact)
        deception = DeceptionAnalyzer.calculate_deception_score(messages)
        deception_weight = 0.3
        components['deception_risk'] = {
            'value': deception['score'],
            'weight': deception_weight,
            'impact': -deception_weight * (deception['score'] - 50) / 50
        }
        
        # Component 2: Emotional consistency
        emotions_analysis = analyze_message_emotions(messages)
        consistency = (1 - emotions_analysis['emotional_volatility']) * 100
        consistency_weight = 0.2
        components['emotional_consistency'] = {
            'value': consistency,
            'weight': consistency_weight,
            'impact': consistency_weight * ((consistency - 50) / 50)
        }
        
        # Component 3: Engagement level
        avg_msg_length = np.mean([len(msg.split()) for msg in messages])
        if avg_msg_length > 5:
            engagement = min(avg_msg_length / 20 * 100, 100)
        else:
            engagement = 30
        
        engagement_weight = 0.2
        components['engagement'] = {
            'value': engagement,
            'weight': engagement_weight,
            'impact': engagement_weight * ((engagement - 50) / 50)
        }
        
        # Component 4: Response consistency
        if analysis_type == 'ghosting':
            ghosting = GhostingAnalyzer.detect_ghosting_signals(messages)
            response_consistency = 100 - ghosting['likelihood']
            consistency_description = 'ghosting_risk'
        else:
            response_consistency = 70
            consistency_description = 'response_pattern'
        
        consistency_weight = 0.15
        components[consistency_description] = {
            'value': response_consistency,
            'weight': consistency_weight,
            'impact': consistency_weight * ((response_consistency - 50) / 50)
        }
        
        # Component 5: Emotional indicators
        dominant_emotion = emotions_analysis['dominant_emotion']
        emotion_impact = {
            'joy': 15,
            'neutral': 5,
            'sadness': -5,
            'fear': -10,
            'anger': -20
        }
        emotion_effect = emotion_impact.get(dominant_emotion, 0)
        emotion_weight = 0.15
        components['emotional_tone'] = {
            'value': 50 + emotion_effect,
            'weight': emotion_weight,
            'impact': emotion_weight * (emotion_effect / 50) if emotion_effect != 0 else 0
        }
        
        # Calculate final score
        final_score = score
        for component in components.values():
            final_score += component['impact']
        
        # Clamp between 0-100
        final_score = int(max(0, min(100, final_score)))
        
        # Determine risk level
        if final_score >= 70:
            risk_level = 'low'
        elif final_score >= 40:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'score': final_score,
            'components': components,
            'risk_level': risk_level,
            'dominant_emotion': dominant_emotion,
            'message_count': len(messages),
            'timestamp': datetime.now().isoformat()
        }


def analyze_conversation(messages: List[str], analysis_type: str = 'general') -> Dict:
    """
    Complete conversation analysis using trained models
    
    Args:
        messages: List of message texts
        analysis_type: 'general', 'ghosting', 'deception'
    
    Returns:
        Comprehensive analysis dictionary
    """
    if not messages or not any(messages):
        return {'error': 'No valid messages provided', 'status': 'failed'}
    
    try:
        # Clean messages
        clean_messages = [msg for msg in messages if msg and isinstance(msg, str)]
        
        # Emotion analysis using trained model
        emotions = analyze_message_emotions(clean_messages)
        
        # Trust score calculation
        trust_analysis = TrustScoreCalculator.calculate_trust_score(
            clean_messages,
            analysis_type
        )
        
        # Deception analysis
        deception = DeceptionAnalyzer.calculate_deception_score(clean_messages)
        
        # Ghosting analysis
        ghosting = GhostingAnalyzer.detect_ghosting_signals(clean_messages)
        
        return {
            'status': 'success',
            'analysis_type': analysis_type,
            'message_count': len(clean_messages),
            'trust_score': trust_analysis,
            'emotions': emotions,
            'deception_analysis': deception,
            'ghosting_analysis': ghosting,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'status': 'error'
        }
