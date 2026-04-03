"""
Grok API Integration Service
Advanced LLM-based analysis using xAI's Grok model
"""

from typing import Dict, Optional, List
import requests
import json
from datetime import datetime


class GrokAnalyzer:
    """
    Integrate with Grok API for advanced LLM-based analysis
    
    Grok (xAI) provides real-time internet access and advanced reasoning
    """
    
    # Grok API endpoint
    BASE_URL = "https://api.x.ai/v1"
    MODEL = "grok-beta"
    
    def __init__(self, api_key: str):
        """
        Initialize Grok API client
        
        Args:
            api_key: xAI Grok API key (xai-XXXXXXXXXX)
        """
        self.api_key = api_key
        self.client = self._init_client()
    
    def _init_client(self):
        """Initialize API client"""
        return {
            'headers': {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        }
    
    def analyze_conversation_with_grok(self, messages: List[str], 
                                       analysis_type: str = 'comprehensive') -> Dict:
        """
        Use Grok to perform advanced conversational analysis
        
        Args:
            messages: List of conversation messages
            analysis_type: Type of analysis (comprehensive, deception, behavioral)
        
        Returns:
            Dictionary with Grok's analysis
        """
        try:
            # Format conversation for Grok
            conversation_text = "\n".join(messages)
            
            # Create analysis prompt based on type
            if analysis_type == 'deception':
                prompt = self._create_deception_prompt(conversation_text)
            elif analysis_type == 'behavioral':
                prompt = self._create_behavioral_prompt(conversation_text)
            elif analysis_type == 'emotional':
                prompt = self._create_emotional_prompt(conversation_text)
            else:
                prompt = self._create_comprehensive_prompt(conversation_text)
            
            # Query Grok
            response = self._query_grok(prompt)
            
            return {
                'status': 'success',
                'analysis': response,
                'model': self.MODEL,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'model': self.MODEL
            }
    
    def analyze_message_authenticity(self, message: str) -> Dict:
        """
        Analyze if a message appears to be from a human or AI
        Uses Grok's advanced reasoning
        """
        try:
            prompt = f"""Analyze this message and determine if it appears to be written by a human or an AI system.

Message: "{message}"

Provide analysis in JSON format with:
1. classification: "human" or "ai"
2. confidence: 0-100 confidence score
3. indicators: list of language patterns indicating human/AI
4. reasoning: brief explanation of conclusion

Be thorough and explain specific linguistic patterns."""
            
            response = self._query_grok(prompt)
            
            # Try to parse JSON response
            try:
                result = json.loads(response)
            except:
                result = {'raw_analysis': response}
            
            return {
                'status': 'success',
                'authenticity_analysis': result,
                'model': self.MODEL
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def detect_deception_patterns_grok(self, conversation: str) -> Dict:
        """
        Use Grok to detect deception patterns in conversation
        Leverages real-time understanding and reasoning
        """
        try:
            prompt = self._create_deception_prompt(conversation)
            response = self._query_grok(prompt)
            
            return {
                'status': 'success',
                'deception_analysis': response,
                'model': self.MODEL,
                'real_time_analysis': True
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def analyze_emotional_authenticity(self, conversation: str) -> Dict:
        """
        Analyze emotional consistency and authenticity
        """
        try:
            prompt = self._create_emotional_prompt(conversation)
            response = self._query_grok(prompt)
            
            return {
                'status': 'success',
                'emotional_analysis': response,
                'model': self.MODEL
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_insights(self, analysis_data: Dict) -> str:
        """
        Generate human-readable insights from analysis data
        Uses Grok for natural language generation
        """
        try:
            prompt = f"""Based on this conversation analysis data, generate clear, 
actionable insights for the user:

Analysis Data:
{json.dumps(analysis_data, indent=2)}

Provide:
1. Key findings
2. Risk indicators
3. Recommendations
4. Confidence levels

Keep response concise but thorough."""
            
            response = self._query_grok(prompt)
            
            return {
                'status': 'success',
                'insights': response,
                'model': self.MODEL
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _query_grok(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Send query to Grok API
        
        Args:
            prompt: Analysis prompt/question
            max_tokens: Maximum response tokens
        
        Returns:
            Grok's response text
        """
        try:
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert AI analyst specializing in conversation analysis, deception detection, and behavioral patterns."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": self.MODEL,
                "stream": False,
                "temperature": 0.7,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.client['headers'],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
                else:
                    return "No response from Grok"
            else:
                return f"API Error: {response.status_code} - {response.text}"
        
        except requests.exceptions.Timeout:
            return "Request timeout - Grok API took too long to respond"
        except requests.exceptions.ConnectionError:
            return "Connection error - Unable to reach Grok API"
        except Exception as e:
            return f"Error querying Grok: {str(e)}"
    
    # Prompt templates
    @staticmethod
    def _create_comprehensive_prompt(conversation: str) -> str:
        return f"""You are an expert conversation analyst. Analyze this conversation for:
1. Overall trustworthiness (0-100 score)
2. Deception indicators
3. Emotional consistency
4. Ghosting signals
5. Risk level assessment

Conversation:
{conversation}

Provide detailed analysis with confidence scores and actionable insights."""
    
    @staticmethod
    def _create_deception_prompt(conversation: str) -> str:
        return f"""Analyze this conversation specifically for deception indicators.

Look for:
1. Contradictions or inconsistencies
2. Vague language patterns
3. Deflection techniques
4. Over-explanation (common deception tactic)
5. Linguistic red flags

Conversation:
{conversation}

Provide specific examples and confidence scores."""
    
    @staticmethod
    def _create_behavioral_prompt(conversation: str) -> str:
        return f"""Analyze behavioral patterns in this conversation.

Evaluate:
1. Engagement level
2. Response consistency
3. Avoidance patterns
4. Ghosting indicators
5. Participation balance

Conversation:
{conversation}

Provide behavioral assessment with patterns identified."""
    
    @staticmethod
    def _create_emotional_prompt(conversation: str) -> str:
        return f"""Analyze emotional consistency and authenticity in this conversation.

Assess:
1. Emotional tone consistency
2. Sentiment shifts and causes
3. Emotional authenticity indicators
4. Empathy levels
5. Emotional manipulation signs

Conversation:
{conversation}

Provide emotional analysis with authenticity score."""


def analyze_with_grok(api_key: str, conversation: str, 
                     analysis_type: str = 'comprehensive') -> Dict:
    """
    Convenience function to analyze conversation with Grok
    
    Args:
        api_key: Grok API key
        conversation: Conversation text or list of messages
        analysis_type: Type of analysis to perform
    
    Returns:
        Analysis results from Grok
    """
    try:
        analyzer = GrokAnalyzer(api_key)
        
        # Handle both string and list inputs
        messages = conversation.split('\n') if isinstance(conversation, str) else conversation
        
        result = analyzer.analyze_conversation_with_grok(messages, analysis_type)
        
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


# Example usage and testing
if __name__ == "__main__":
    # Test API key (replace with real key)
    TEST_API_KEY = "xai-pPPOPwicopg9N2i28aJvNY2HTah7w3MeEtsEQREDsVdYEFWcqn1ixkg6voE5SVoeLeRsGyC93llTvsDy"
    
    test_conversation = """
A: Hey! How have you been?
B: Good, been busy with work lately.
A: That's great! Want to hang out soon?
B: Maybe, I'm not sure about my schedule.
A: No worries, just let me know!
B: I will definitely text you.
"""
    
    # Initialize analyzer
    analyzer = GrokAnalyzer(TEST_API_KEY)
    
    # Test comprehensive analysis
    print("Testing comprehensive analysis...")
    result = analyzer.analyze_conversation_with_grok(test_conversation.split('\n'))
    print(json.dumps(result, indent=2))
