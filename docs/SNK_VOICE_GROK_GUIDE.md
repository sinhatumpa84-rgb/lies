# SNK Analysis, Voice Message & Grok API Integration Guide

## Overview

TruthLens AI now includes three powerful new analysis features:
1. **SNK Analysis** (Sentiment/NLP/Keywords)
2. **Voice Message Analysis** (WhatsApp audio support)
3. **Grok API Integration** (Advanced LLM-based analysis)

---

## 1. SNK Analysis (Sentiment/NLP/Keywords)

### What is SNK?
SNK stands for **Sentiment, NLP (Natural Language Processing), Keywords** analysis. It provides deep linguistic insights into conversation text.

### Features

#### A. Sentiment Analysis
- **Compound Score**: Overall sentiment ranging from -1 (very negative) to +1 (very positive)
- **Multiple Scoring Methods**: Uses both VADER and TextBlob for accuracy
- **Intensity Levels**: Very Positive, Positive, Neutral, Negative, Very Negative

**Example:**
```
Text: "I absolutely love this! It's amazing and fantastic!"
Sentiment Score: 0.85
Label: Very Positive
```

#### B. NLP Pattern Analysis
- **Sentence Count**: Number of sentences in text
- **Word Count**: Total words used
- **Avg Words per Sentence**: Measures sentence complexity
- **Lexical Diversity**: Percentage of unique words
- **Flesch-Kincaid Grade**: Reading level difficulty
- **Question & Exclamation Count**: Engagement markers

**Example:**
```
NLP Metrics:
- Sentences: 5
- Words: 87
- Lexical Diversity: 78%
- Questions Asked: 3
- Exclamations: 2
```

#### C. Keyword Extraction
- Extracts top 8-10 most important keywords
- Removes common stopwords
- Calculates frequency and importance scores
- Classifies keywords by type (first-person, second-person, general)

**Example:**
```
Keywords:
1. "conversation" (frequency: 4, score: 0.046)
2. "analysis" (frequency: 3, score: 0.035)
3. "message" (frequency: 2, score: 0.023)
```

#### D. Emotional Content Detection
- Detects 6 primary emotions: Joy, Sadness, Anger, Fear, Trust, Surprise
- Identifies emotional markers and intensity
- Determines dominant emotion
- Provides emotional intensity score

**Example:**
```
Detected Emotions:
- Joy: 3 markers
- Trust: 2 markers
- Surprise: 1 marker
Dominant Emotion: Joy (score: 0.6)
```

### How to Use SNK Analysis

1. **Enable Grok AI** checkbox in the demo (optional, for enhanced analysis)
2. **Paste conversation** or **analyze voice message**
3. Results appear in **SNK Analysis** card with all metrics

### SNK Analysis in Backend

```python
from services.snk_analysis import SNKAnalyzer

analyzer = SNKAnalyzer()

# Comprehensive analysis
analysis = analyzer.comprehensive_analysis(text)

# Individual analyses
sentiment = analyzer.analyze_sentiment(text)
keywords = analyzer.extract_keywords(text)
nlp_patterns = analyzer.analyze_nlp_patterns(text)
emotions = analyzer.analyze_emotions(text)
```

---

## 2. Voice Message Analysis (WhatsApp Support)

### What is Voice Message Analysis?

Analyzes WhatsApp and other voice messages by:
1. **Transcription**: Converting audio to text
2. **Audio Features**: Extracting pitch, tempo, energy, quality
3. **Voice Emotion**: Inferring emotional state from voice characteristics
4. **SNK Analysis**: Analyzing the transcribed text

### Supported Audio Formats
- MP3
- WAV (8kHz, 16kHz, 44.1kHz, 48kHz)
- M4A (WhatsApp format)
- OGG
- FLAC

### Audio Features Extracted

| Feature | Description | Interpretation |
|---------|-------------|-----------------|
| **Pitch** | Average frequency (Hz) | High pitch = excitement; Low pitch = sadness |
| **Tempo** | Speech rate (BPM) | Fast = urgency/excitement; Slow = thoughtful/sad |
| **Energy** | Loudness/intensity (0-1) | High = confident/angry; Low = sad/quiet |
| **Spectral Centroid** | Frequency distribution | Higher = bright; Lower = dark tone |
| **MFCC** | Mel-frequency features | Voice quality and characteristics |
| **Zero Crossing Rate** | Voice activity indicator | Higher = non-voiced sounds |

### Emotion Detection from Voice

```
Pitch > 150 Hz + Tempo > 120 BPM + Energy > 0.5
→ Emotional State: EXCITED/HAPPY

Pitch < 80 Hz + Tempo < 100 BPM + Energy < 0.3
→ Emotional State: SAD/DEPRESSED

80Hz ≤ Pitch ≤ 150 Hz + Energy > 0.5 + Tempo > 120 BPM
→ Emotional State: CONFIDENT/URGENT
```

### Using Voice Message Analysis

1. Click **"Or Upload WhatsApp Voice Message"** button
2. Select MP3, WAV, M4A, or OGG file
3. Audio is automatically transcribed and analyzed
4. Results show:
   - Transcription text
   - Audio features (pitch, tempo, energy)
   - Detected emotion from voice
   - SNK analysis of transcription

### Voice Analysis in Backend

```python
from services.voice_analysis import VoiceAnalyzer, analyze_whatsapp_voice

analyzer = VoiceAnalyzer()

# Extract features
features = analyzer.extract_audio_features('voice_message.wav')

# Transcribe
transcription = analyzer.transcribe_voice_message('voice_message.wav')

# Analyze emotion
emotion = analyzer.analyze_voice_emotion('voice_message.wav')

# All-in-one
full_analysis = analyze_whatsapp_voice('voice_message.wav')
```

---

## 3. Grok API Integration

### What is Grok?

**Grok** is xAI's advanced LLM (Large Language Model) with:
- Real-time internet access
- Superior reasoning capabilities
- Advanced conversation understanding
- Current knowledge cutoff updates

### Grok Features in TruthLens

#### A. Conversation Analysis
- Comprehensive analysis with real-time reasoning
- Deception detection with advanced patterns
- Behavioral analysis
- Emotional authenticity assessment

#### B. Message Authenticity Detection
- Determines if message is from human or AI
- Analyzes linguistic patterns
- Provides confidence score
- Identifies specific indicators

#### C. Real-time Insights
- Natural language insights generation
- Context-aware analysis
- Current event awareness
- Advanced pattern recognition

### Setting Up Grok API

1. **Get API Key**: Obtained from xAI ([https://api.x.ai](https://api.x.ai))
   - Current key: `xai-pPPOPwicopg9N2i28aJvNY2HTah7w3MeEtsEQREDsVdYEFWcqn1ixkg6voE5SVoeLeRsGyC93llTvsDy`

2. **Setup in Backend**:
```python
from services.grok_analyzer import GrokAnalyzer

api_key = "xai-YOUR_API_KEY_HERE"
grok = GrokAnalyzer(api_key)

# Comprehensive analysis
result = grok.analyze_conversation_with_grok(messages, 'comprehensive')

# Deception detection
deception = grok.detect_deception_patterns_grok(conversation)

# AI vs Human detection
authenticity = grok.analyze_message_authenticity(message)
```

3. **Enable in Frontend**:
   - Check "Use Grok AI for Advanced Analysis" checkbox
   - Analysis will include Grok insights

### Grok Analysis Types

#### 1. Comprehensive Analysis
- Overall trustworthiness score
- Deception indicators
- Emotional consistency
- Risk assessment
- Actionable insights

#### 2. Deception Detection
- Contradiction analysis
- Vague language patterns
- Deflection techniques
- Over-explanation tactics
- Specific examples with confidence

#### 3. Behavioral Analysis
- Engagement evaluation
- Response consistency
- Avoidance patterns
- Ghosting indicators
- Participation balance

#### 4. Emotional Analysis
- Emotional tone consistency
- Sentiment shift analysis
- Emotional authenticity
- Empathy levels
- Manipulation detection

### Using Grok in Frontend

```javascript
// Enable Grok checkbox
document.getElementById('enableGrok').checked = true;

// Automatic Grok analysis on conversation submit
// Results will appear in analysis cards with model attribution

// Or make direct API calls
const grokResult = await queryGrokAPI(conversation, analysisType);
```

---

## Integration Architecture

### Data Flow

```
User Input (Text/Voice)
    ↓
Frontend Processing
    ↓
SNK Analysis (Local)
    ├─ Sentiment
    ├─ Keywords
    ├─ NLP Patterns
    └─ Emotions
    ↓
Voice Processing (if audio)
    ├─ Transcription
    ├─ Audio Features
    └─ Voice Emotion
    ↓
Grok API Processing (if enabled)
    ├─ Comprehensive Analysis
    ├─ Deception Detection
    └─ Advanced Insights
    ↓
Results Display
```

### Files Structure

```
backend/
├── app/services/
│   ├── snk_analysis.py           # Sentiment/NLP/Keywords
│   ├── voice_analysis.py         # Voice message processing
│   ├── grok_analyzer.py          # Grok API integration
│   └── analysis.py               # Main analysis service
└── requirements.txt              # Updated dependencies

frontend/
├── js/
│   ├── config.js                 # Configuration & API keys
│   ├── demo.js                   # Main demo logic
│   └── main.js                   # Navigation & animations
├── styles/
│   ├── demo.css                  # Updated with new styles
│   └── main.css                  # Global styles
└── demo.html                     # Updated form elements
```

---

## Configuration

### Environment Variables

```bash
# .env or config
GROK_API_KEY=xai-pPPOPwicopg9N2i28aJvNY2HTah7w3MeEtsEQREDsVdYEFWcqn1ixkg6voE5SVoeLeRsGyC93llTvsDy
GROK_MODEL=grok-beta
GROK_MAX_TOKENS=1000
GROK_TEMPERATURE=0.7

# Voice Processing
MAX_VOICE_FILE_SIZE=25MB
VOICE_FORMATS=mp3,wav,m4a,ogg,flac
```

### Frontend Configuration (config.js)

```javascript
const GROK_CONFIG = {
    API_KEY: "xai-pPPOPwicopg9N2i28aJvNY2HTah7w3MeEtsEQREDsVdYEFWcqn1ixkg6voE5SVoeLeRsGyC93llTvsDy",
    BASE_URL: "https://api.x.ai/v1",
    MODEL: "grok-beta",
    MAX_TOKENS: 1000,
    TEMPERATURE: 0.7
};

const SERVICE_CONFIG = {
    VOICE_ANALYSIS: {
        ENABLED: true,
        FORMATS: ['mp3', 'wav', 'm4a', 'ogg', 'flac'],
        MAX_FILE_SIZE: 25 * 1024 * 1024 // 25MB
    },
    SNK_ANALYSIS: {
        ENABLED: true,
        EXTRACT_KEYWORDS: true,
        ANALYZE_EMOTIONS: true,
        ANALYZE_NLP: true
    }
};
```

---

## API Endpoints (Backend)

### SNK Analysis
```
POST /api/snk/analyze
Body: { text: string }
Response: { sentiment, emotions, keywords, nlp_patterns }

POST /api/snk/sentiment
Body: { text: string }
Response: { score, label, intensity }

POST /api/snk/keywords
Body: { text: string, top_n: int }
Response: { keywords: [{ keyword, frequency, score }] }
```

### Voice Analysis
```
POST /api/voices/analyze
Body: { audio_file: File (multipart) }
Response: { transcription, audio_features, voice_emotion, snk_analysis }

POST /api/voices/transcribe
Body: { audio_file: File }
Response: { transcription, confidence }

POST /api/voices/emotions
Body: { audio_file: File }
Response: { detected_emotion, confidence, voice_characteristics }
```

### Grok Analysis
```
POST /api/grok/analyze
Body: { conversation: string, analysis_type: string, api_key: string }
Response: { analysis, model, timestamp }

POST /api/grok/authenticity
Body: { message: string, api_key: string }
Response: { classification, confidence, indicators }

POST /api/grok/deception
Body: { conversation: string, api_key: string }
Response: { deception_analysis, patterns }
```

---

## Error Handling

### Voice Processing Errors
- **Unsupported Format**: Direct user to supported formats
- **File Too Large**: Limit to 25MB max
- **Transcription Failed**: Fallback to manual text input
- **Audio Quality Issues**: Suggest re-recording

### Grok API Errors
- **API Key Invalid**: Validate before processing
- **Rate Limited**: Implement backoff strategy
- **Connection Timeout**: Cache results when possible
- **Response Format Error**: Parse fallback responses

### SNK Analysis Errors
- **Empty Text**: Validate minimum text length
- **Language Detection**: Default to English
- **Model Not Available**: Use fallback analysis

---

## Performance Considerations

### Caching
- Cache Grok API responses (24 hours)
- Store processed audio features
- Memoize SNK analysis results

### Optimization
- Lazy load voice processing libraries
- Use Web Workers for NLP processing
- Stream audio for large files
- Batch Grok API requests

### Load Times
- SNK Analysis: ~100-200ms
- Voice Processing: 2-5 seconds (depends on duration)
- Grok API: 3-10 seconds (network dependent)

---

## Testing

### Test Conversations

**Deceptive Conversation**
```
A: Where were you yesterday?
B: I was at home studying.
A: Really? I saw you at the mall.
B: No, you must have seen someone else. I was definitely home.
A: Are you sure? It looked just like you.
B: Yes, I'm sure. Well, maybe I went out for a bit but I was mostly home.
```

**AI Conversation**
```
A: Can you explain machine learning?
B: I'd be delighted to provide a comprehensive explanation. Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience. Key components include supervised learning, unsupervised learning, and reinforcement learning. Each approach has distinct applications and methodologies.
```

**Authentic Voice**
- Record yourself speaking naturally
- Include emotional expressions
- Vary pace and energy

---

## Troubleshooting

### Grok API Issues
1. Verify API key format: starts with `xai-`
2. Check rate limits (if exceeded, wait)
3. Ensure internet connection
4. Try with shorter input first

### Voice Analysis Issues
1. Check audio file format support
2. Verify file isn't corrupted
3. Test with sample audio first
4. Check microphone permissions

### SNK Analysis Issues
1. Ensure text encoding is UTF-8
2. Check for language support
3. Verify spaCy model is installed
4. Try with different text samples

---

## Future Enhancements

- Multi-language support for SNK analysis
- Real-time audio streaming analysis
- Volume-based emotion detection
- Advanced Grok features (vision, real-time events)
- Integration with messaging APIs
- Custom model training per user
- Historical analysis tracking

---

## Resources

- **Grok API Documentation**: https://api.x.ai/docs
- **spaCy NLP**: https://spacy.io
- **Librosa Audio**: https://librosa.org
- **NLTK**: https://www.nltk.org

---

**Last Updated**: April 4, 2026
**Version**: 2.0 (SNK + Voice + Grok)
