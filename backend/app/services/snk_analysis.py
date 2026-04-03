"""
SNK Analysis Service - Sentiment, NLP, and Keyword Analysis
Advanced text analysis using NLP techniques
"""

from typing import List, Dict, Optional, Tuple
import re
from collections import Counter
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from textblob import TextBlob
import spacy

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
    
try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')


class SNKAnalyzer:
    """Analyze text for Sentiment, NLP patterns, and Keywords"""
    
    def __init__(self):
        """Initialize NLP tools"""
        self.sia = SentimentIntensityAnalyzer()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not loaded. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        self.stop_words = set(stopwords.words('english'))
        
        # Emotional words
        self.emotional_words = {
            'positive': [
                'love', 'happy', 'great', 'awesome', 'excellent', 'amazing',
                'wonderful', 'fantastic', 'beautiful', 'good', 'nice', 'perfect',
                'brilliant', 'superb', 'outstanding', 'incredible', 'delighted'
            ],
            'negative': [
                'hate', 'sad', 'bad', 'terrible', 'awful', 'horrible', 'disgusting',
                'angry', 'upset', 'worried', 'scared', 'depressed', 'miserable',
                'pathetic', 'disgusting', 'dreadful', 'appalling'
            ],
            'neutral': [
                'okay', 'alright', 'fine', 'sure', 'yeah', 'no', 'maybe',
                'interesting', 'noted', 'understood', 'definitely'
            ]
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Comprehensive sentiment analysis using multiple methods
        
        Returns:
            Dict with compound score, positive/neutral/negative scores, labels
        """
        # VADER Sentiment
        vader_scores = self.sia.polarity_scores(text)
        
        # TextBlob polarity
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Compound sentiment (average of both)
        compound_score = (vader_scores['compound'] + textblob_polarity) / 2
        
        # Determine label
        if compound_score >= 0.05:
            sentiment_label = "Positive"
        elif compound_score <= -0.05:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
        
        return {
            'compound_score': round(compound_score, 3),
            'vader_score': round(vader_scores['compound'], 3),
            'textblob_score': round(textblob_polarity, 3),
            'positive': round(vader_scores['pos'], 3),
            'neutral': round(vader_scores['neu'], 3),
            'negative': round(vader_scores['neg'], 3),
            'label': sentiment_label,
            'intensity': self._score_to_intensity(compound_score)
        }
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Dict]:
        """
        Extract important keywords using NLP
        
        Returns:
            List of dicts with keyword, frequency, and importance score
        """
        # Tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and special characters
        keywords = [
            token for token in tokens
            if token.isalpha() and token not in self.stop_words and len(token) > 2
        ]
        
        # Count frequencies
        freq_dist = Counter(keywords)
        
        # Get top N keywords
        top_keywords = freq_dist.most_common(top_n)
        
        # Calculate TF-IDF-like scores
        total_words = len(keywords)
        results = []
        
        for keyword, freq in top_keywords:
            tf_score = freq / total_words if total_words > 0 else 0
            results.append({
                'keyword': keyword,
                'frequency': freq,
                'score': round(tf_score, 3),
                'type': self._classify_keyword(keyword)
            })
        
        return results
    
    def analyze_nlp_patterns(self, text: str) -> Dict:
        """
        Analyze NLP patterns including:
        - Sentence structure
        - Word complexity
        - Grammatical patterns
        - Named entities (if spaCy available)
        """
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        
        # Filter out punctuation
        word_tokens = [w for w in words if w.isalpha()]
        
        # Basic metrics
        avg_words_per_sentence = len(word_tokens) / len(sentences) if sentences else 0
        avg_word_length = sum(len(w) for w in word_tokens) / len(word_tokens) if word_tokens else 0
        
        # Readability metrics
        flesch_kincaid_grade = self._calculate_flesch_kincaid(text)
        
        # Named entities (if spaCy available)
        entities = []
        if self.nlp:
            doc = self.nlp(text)
            entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
        
        # Question and exclamation count
        question_count = text.count('?')
        exclamation_count = text.count('!')
        
        return {
            'sentence_count': len(sentences),
            'word_count': len(word_tokens),
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'avg_word_length': round(avg_word_length, 2),
            'lexical_diversity': round(len(set(word_tokens)) / len(word_tokens), 3) if word_tokens else 0,
            'flesch_kincaid_grade': round(flesch_kincaid_grade, 1),
            'question_count': question_count,
            'exclamation_count': exclamation_count,
            'entities': entities[:10]  # Top 10
        }
    
    def analyze_emotions(self, text: str) -> Dict:
        """
        Detect emotional content using emotional word lists
        """
        text_lower = text.lower()
        emotions = {}
        
        for emotion_type, words in self.emotional_words.items():
            count = sum(1 for word in words if word in text_lower)
            emotions[emotion_type] = {
                'count': count,
                'score': min(count * 0.1, 1.0)  # Normalize to 0-1
            }
        
        # Determine dominant emotion
        dominant = max(emotions.items(), key=lambda x: x[1]['score'])
        
        return {
            'emotions': emotions,
            'dominant_emotion': dominant[0],
            'emotional_intensity': round(dominant[1]['score'], 3)
        }
    
    def calculate_reliability_score(self, messages: List[str]) -> Dict:
        """
        Calculate message reliability based on:
        - Consistency
        - Coherence
        - Linguistic patterns
        """
        sentiments = [self.analyze_sentiment(msg)['compound_score'] for msg in messages]
        
        # Sentiment consistency
        if len(sentiments) > 1:
            inconsistency = sum(abs(sentiments[i] - sentiments[i+1]) for i in range(len(sentiments)-1)) / (len(sentiments)-1)
            consistency_score = max(0, 100 - (inconsistency * 50))
        else:
            consistency_score = 100
        
        # Average sentiment coherence
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        coherence = abs(avg_sentiment)  # How far from neutral
        
        reliability = {
            'consistency_score': round(consistency_score, 1),
            'average_sentiment': round(avg_sentiment, 3),
            'sentiment_coherence': round(coherence, 3),
            'reliability_rating': self._score_to_reliability(consistency_score)
        }
        
        return reliability
    
    def comprehensive_analysis(self, text: str) -> Dict:
        """
        Perform comprehensive SNK analysis on text
        """
        return {
            'sentiment': self.analyze_sentiment(text),
            'emotions': self.analyze_emotions(text),
            'keywords': self.extract_keywords(text),
            'nlp_patterns': self.analyze_nlp_patterns(text),
            'text_preview': text[:200] + ('...' if len(text) > 200 else '')
        }
    
    # Helper methods
    @staticmethod
    def _score_to_intensity(score: float) -> str:
        """Convert sentiment score to intensity description"""
        if score > 0.5:
            return "Very Positive"
        elif score > 0.15:
            return "Positive"
        elif score > -0.15:
            return "Neutral"
        elif score > -0.5:
            return "Negative"
        else:
            return "Very Negative"
    
    @staticmethod
    def _score_to_reliability(score: float) -> str:
        """Convert consistency score to reliability rating"""
        if score >= 85:
            return "Very Reliable"
        elif score >= 70:
            return "Reliable"
        elif score >= 50:
            return "Moderate"
        elif score >= 30:
            return "Questionable"
        else:
            return "Unreliable"
    
    @staticmethod
    def _classify_keyword(keyword: str) -> str:
        """Classify keyword type"""
        if keyword in ['i', 'me', 'my', 'we', 'our', 'me']:
            return 'first_person'
        elif keyword in ['you', 'your', 'yours']:
            return 'second_person'
        elif keyword in ['he', 'she', 'they', 'it', 'his', 'her', 'their']:
            return 'third_person'
        else:
            return 'general'
    
    @staticmethod
    def _calculate_flesch_kincaid(text: str) -> float:
        """Calculate Flesch-Kincaid Grade Level"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        syllables = sum(1 for word in words if word.isalpha())  # Simplified
        
        if len(words) == 0 or len(sentences) == 0:
            return 0
        
        # Simplified FLK formula
        grade = (11.8 * (syllables / len(words))) + (0.39 * (len(words) / len(sentences))) - 15.59
        return max(0, grade)
