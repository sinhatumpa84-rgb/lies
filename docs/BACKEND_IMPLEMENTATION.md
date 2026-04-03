# FastAPI Backend Implementation Guide

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration & env vars
│   ├── middleware/
│   │   ├── auth.py            # JWT authentication
│   │   ├── rate_limit.py      # Rate limiting
│   │   └── error_handler.py   # Global error handling
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api_v1.py          # v1 API endpoints
│   │   └── health.py          # Health checks
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py         # Pydantic models
│   │   ├── database.py        # SQLAlchemy models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis.py        # Core analysis logic
│   │   ├── nlp_processor.py   # NLP operations
│   │   ├── llm_service.py     # LLM integration
│   │   └── cache_service.py   # Redis caching
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py          # Logging setup
│   │   ├── validators.py      # Input validation
│   │   └── security.py        # Security utilities
│   └── database/
│       ├── __init__.py
│       ├── connection.py      # DB connections
│       └── migrations/        # Alembic migrations
├── tests/
│   ├── __init__.py
│   ├── test_api.py           # API tests
│   ├── test_analysis.py      # Analysis tests
│   └── fixtures.py           # Test fixtures
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Installation & Setup

### Requirements

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.0.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.0
redis==5.0.0
pytest==7.4.0

# NLP & ML
spacy==3.7.0
nltk==3.8.0
scikit-learn==1.3.0
lightgbm==4.0.0
xgboost==2.0.0
transformers==4.35.0
torch==2.0.0

# LLM Integration
openai==1.3.0
google-generativeai==0.3.0

# Utilities
python-dotenv==1.0.0
python-jose==3.3.0
pydantic-settings==2.0.0
aioredis==2.0.1
httpx==0.25.0
```

### Setup Commands

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt vader_lexicon wordnet

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🚀 Core Application Files

### main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.middleware import auth, error_handler, rate_limit
from app.routes import api_v1, health
from app.database import connection

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up...")
    await connection.connect_db()
    yield
    # Shutdown
    logger.info("Application shutting down...")
    await connection.close_db()

app = FastAPI(
    title="TruthLens AI API",
    description="Advanced chat analysis powered by AI and NLP",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(error_handler.ErrorHandlerMiddleware)

# Routes
app.include_router(health.router)
app.include_router(api_v1.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "name": "TruthLens AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### config.py

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "TruthLens AI"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/truthlens"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LLM
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://truthlens.ai"
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### models/schemas.py

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class AnalysisType(str, Enum):
    BALANCED = "balanced"
    DECEPTION = "deception"
    EMOTIONAL = "emotional"
    BEHAVIORAL = "behavioral"

class ConversationRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000)
    source: Optional[str] = Field(default="manual", pattern="^(manual|whatsapp|instagram)$")
    language: Optional[str] = Field(default="en", pattern="^[a-z]{2}$")
    analysis_type: Optional[AnalysisType] = AnalysisType.BALANCED
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v

class RiskIndicator(BaseModel):
    level: str  # high, medium, low
    text: str

class AnalysisResponse(BaseModel):
    trust_score: int = Field(..., ge=0, le=100)
    emotional_timeline: List[dict]
    deception_patterns: List[str]
    ghosting_signals: List[str]
    risk_indicators: List[RiskIndicator]
    insights: List[str]
    message_metrics: dict
    confidence_level: float = Field(..., ge=0, le=1)

class HealthResponse(BaseModel):
    status: str
    version: str
```

### services/analysis.py

```python
import asyncio
from typing import Dict, List
from app.services import nlp_processor, llm_service, cache_service
import logging

logger = logging.getLogger(__name__)

class ConversationAnalyzer:
    def __init__(self):
        self.nlp = nlp_processor.NLPProcessor()
        self.llm = llm_service.LLMService()
        self.cache = cache_service.CacheService()
    
    async def analyze(self, text: str, analysis_type: str) -> Dict:
        """Main analysis pipeline"""
        
        # Check cache
        cache_key = self._generate_cache_key(text, analysis_type)
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for {cache_key}")
            return cached_result
        
        # Preprocessing
        preprocessed = self.nlp.preprocess(text)
        
        # Feature extraction (parallel tasks)
        features, patterns, metrics = await asyncio.gather(
            self._extract_features(preprocessed),
            self._detect_patterns(preprocessed),
            self._analyze_metrics(preprocessed)
        )
        
        # Calculate scores
        trust_score = self._calculate_trust_score(features, patterns, analysis_type)
        
        # Generate insights
        insights = await self.llm.generate_insights(
            text, trust_score, patterns, analysis_type
        )
        
        # Compile result
        result = {
            'trust_score': trust_score,
            'emotional_timeline': features['emotional_timeline'],
            'deception_patterns': patterns['deception'],
            'ghosting_signals': patterns['ghosting'],
            'risk_indicators': self._generate_risk_indicators(patterns),
            'insights': insights,
            'message_metrics': metrics,
            'confidence_level': self._calculate_confidence(patterns)
        }
        
        # Cache result
        await self.cache.set(cache_key, result, ttl=3600)
        
        return result
    
    async def _extract_features(self, text: str) -> Dict:
        """Extract linguistic features"""
        return await asyncio.to_thread(self.nlp.extract_features, text)
    
    async def _detect_patterns(self, text: str) -> Dict:
        """Detect behavioral patterns"""
        return await asyncio.to_thread(self.nlp.detect_patterns, text)
    
    async def _analyze_metrics(self, text: str) -> Dict:
        """Analyze message metrics"""
        return await asyncio.to_thread(self.nlp.analyze_metrics, text)
    
    def _calculate_trust_score(self, features: Dict, patterns: Dict, analysis_type: str) -> int:
        """Calculate trustworthiness score"""
        base_score = 70
        
        # Deduction factors
        base_score -= len(patterns['deception']) * 5
        base_score -= len(patterns['ghosting']) * 4
        base_score -= len(patterns['emotional_shifts']) * 3
        
        # Analysis type weighting
        if analysis_type == 'deception':
            base_score -= len(patterns['deception']) * 2
        elif analysis_type == 'emotional':
            base_score -= len(patterns['emotional_shifts']) * 2
        elif analysis_type == 'behavioral':
            base_score -= len(patterns['behavioral']) * 2
        
        return max(0, min(100, base_score))
    
    def _generate_risk_indicators(self, patterns: Dict) -> List:
        """Generate prioritized risk indicators"""
        indicators = []
        
        if len(patterns['deception']) > 2:
            indicators.append({'level': 'high', 'text': 'Multiple contradictions'})
        elif len(patterns['deception']) > 0:
            indicators.append({'level': 'medium', 'text': 'Some contradictory statements'})
        
        if len(patterns['ghosting']) > 0:
            indicators.append({'level': 'medium', 'text': 'Avoidance behavior detected'})
        
        return indicators if indicators else [{'level': 'low', 'text': 'No risk indicators'}]
    
    def _calculate_confidence(self, patterns: Dict) -> float:
        """Calculate analysis confidence level"""
        # Higher confidence with more signals
        signal_count = (
            len(patterns.get('deception', [])) +
            len(patterns.get('ghosting', [])) +
            len(patterns.get('emotional_shifts', []))
        )
        
        # Cap confidence at 0.95 to be conservative
        return min(0.95, 0.4 + (signal_count * 0.1))
    
    def _generate_cache_key(self, text: str, analysis_type: str) -> str:
        """Generate cache key from input"""
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"analysis:{text_hash}:{analysis_type}"

# Global analyzer instance
analyzer = ConversationAnalyzer()
```

### routes/api_v1.py

```python
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ConversationRequest, AnalysisResponse
from app.services.analysis import analyzer
from app.middleware.auth import verify_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_conversation(
    request: ConversationRequest,
    user_id: str = Depends(verify_token)
):
    """
    Analyze a conversation for deception, emotional shifts, and ghosting patterns.
    
    Required authentication: JWT token in Authorization header
    """
    try:
        # Log request (without sensitive data)
        logger.info(f"Analysis request from user {user_id}, type: {request.analysis_type}")
        
        # Perform analysis
        result = await analyzer.analyze(request.text, request.analysis_type)
        
        logger.info(f"Analysis completed successfully for user {user_id}")
        
        return AnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
```

## 🧪 Testing

### tests/test_api.py

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def valid_token():
    # Mock token for testing
    return "Bearer eyJhbGc..."

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_valid_input(valid_token):
    payload = {
        "text": "Person A: Hey! How are you? Person B: Good, thanks! How about you?",
        "analysis_type": "balanced"
    }
    
    response = client.post(
        "/api/v1/analyze",
        json=payload,
        headers={"Authorization": valid_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'trust_score' in data
    assert 'insights' in data

def test_analyze_short_input(valid_token):
    payload = {
        "text": "Hi",
        "analysis_type": "balanced"
    }
    
    response = client.post(
        "/api/v1/analyze",
        json=payload,
        headers={"Authorization": valid_token}
    )
    
    assert response.status_code == 422  # Validation error

def test_analyze_without_auth():
    payload = {
        "text": "Person A: Hey! How are you? Person B: Good, thanks!",
        "analysis_type": "balanced"
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 403  # Forbidden
```

## 🐳 Docker Setup

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLP models
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader punkt vader_lexicon wordnet

# Copy application
COPY app/ ./app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://truthlens:password@postgres:5432/truthlens
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./app:/app/app

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: truthlens
      POSTGRES_PASSWORD: password
      POSTGRES_DB: truthlens
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 🚀 Running the Application

```bash
# Development
uvicorn app.main:app --reload

# Production
gunicorn app.main:app -w 4 -b 0.0.0.0:8000

# Docker
docker-compose up -d

# Run tests
pytest tests/
```

---

**Version**: 1.0.0
**Last Updated**: March 2024
