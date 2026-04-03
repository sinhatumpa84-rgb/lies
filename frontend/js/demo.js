/* ===================================
   TRUTHLENS AI - Demo JavaScript
   Interactive Analysis Engine
   ==================================== */

// Sample conversations
const SAMPLES = {
    honest: `A: Hey! How have you been? Haven't heard from you in a while.
B: Good! Been pretty busy with work, but managing. How about you?
A: Same here. We should grab coffee soon!
B: I'd love that. Let me check my schedule and get back to you.
A: Sounds good! Looking forward to it.
B: Me too. Talk soon!`,

    deceptive: `A: Did you go to the party last night?
B: No, I was really tired from the gym.
A: Oh really? I thought I saw you there.
B: Maybe it was someone who looked like me? I was definitely home.
A: Are you sure? It looked a lot like you.
B: Yeah, I mean... maybe I went for like 10 minutes but didn't stay long.
A: So you weren't actually tired?
B: Well, I was tired when I got there, but they convinced me to stay for a bit.`,

    ghosting: `A: Hey! Hope you're doing well. Would love to catch up!
B: Hey! Yeah, been a minute.
A: Definitely! Free this weekend?
B: Maybe, not sure yet. Pretty packed.
A: No worries, just let me know!
B: ... [no response for 3 days]
A: Hey, still thinking about hanging out?
B: Oh yeah, been crazy busy. Will text you soon.
A: ... [no response after that]`,

    ai: `A: Can you help me understand quantum computing?
B: I'd be happy to help explain quantum computing. Certainly, I can provide a comprehensive overview. Quantum computing represents a revolutionary approach to computation that leverages quantum mechanical phenomena. Key points include: 1) Quantum bits can exist in superposition, 2) Entanglement enables correlations between qubits, 3) Quantum algorithms can potentially solve certain problems exponentially faster. As an AI, I should note that this is a complex field of study. Feel free to ask if you have any further questions or need clarification on specific concepts.
A: Thanks! What are some applications?
B: Excellent question. There are numerous important applications of quantum computing that deserve attention. In summary, the key applications include: drug discovery, cryptography, optimization problems, and financial modeling. I appreciate your interest in this topic. Please let me know if you would like more detailed information on any of these applications.
A: That's helpful!
B: You're welcome! I'm glad I could assist. As an AI language model, I'm designed to provide helpful, accurate information. If you have any other questions or topics you'd like to explore, don't hesitate to reach out. I'm here to help!`,

    casual_human: `A: yooo whatcha up to?? 
B: lol not much dude just chillin, watching some netflix haha
A: omg same!! wanna play some games later?
B: Haha fr fr? Yeah let's go bro, that would be sick! 🎮😂
A: yesss let me know when ur free k?
B: for sure! prob like 8pm? gonna grab food real quick lol
A: perfect bro 👍 ill hit u up later
B: cool cool see u then!! 🔥🔥`
};

// Initialize demo on page load
document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const clearBtn = document.getElementById('clearBtn');
    const chatInput = document.getElementById('chatInput');
    const voiceInput = document.getElementById('voiceInput');

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeConversation);
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', clearResults);
    }

    if (voiceInput) {
        voiceInput.addEventListener('change', handleVoiceUpload);
    }

    // Add navigation functionality
    initializeNavigation();
});

// Load sample conversations
function loadSample(type) {
    document.getElementById('chatInput').value = SAMPLES[type];
}

// Main analysis function
function analyzeConversation() {
    const chatInput = document.getElementById('chatInput').value.trim();
    const analysisType = document.getElementById('analysisType').value;
    const conversationType = document.getElementById('conversationType').value;

    if (!chatInput) {
        alert('Please enter a conversation to analyze.');
        return;
    }

    // Show loading state
    showLoading();

    // Simulate API processing delay
    setTimeout(() => {
        try {
            const analysis = performAnalysis(chatInput, analysisType, conversationType);
            displayResults(analysis);
        } catch (error) {
            console.error('Analysis error:', error);
            alert('Error analyzing conversation. Please try again.');
        }
    }, 1500);
}

// Core analysis engine
function performAnalysis(text, analysisType, conversationType) {
    const messages = parseMessages(text);
    
    return {
        trustScore: calculateTrustScore(messages, analysisType),
        emotionalTimeline: generateEmotionalTimeline(messages),
        deceptionPatterns: detectDeceptionPatterns(messages),
        emotionalShifts: analyzeEmotionalShifts(messages),
        ghostingSignals: detectGhostingSignals(messages),
        behaviorPatterns: analyzeBehaviorPatterns(messages),
        messageAnalysis: analyzeMessageMetrics(messages),
        riskIndicators: generateRiskIndicators(messages, analysisType),
        aiDetection: detectAIPatterns(messages, conversationType)
    };
}

// Parse messages from input
function parseMessages(text) {
    const lines = text.split('\n').filter(line => line.trim());
    const messages = [];

    lines.forEach(line => {
        // Try to extract sender and message
        const match = line.match(/^([A-Za-z0-9\s]*?):\s*(.+)$/);
        if (match) {
            messages.push({
                sender: match[1].trim() || 'Unknown',
                text: match[2].trim(),
                length: match[2].trim().length
            });
        } else if (line.trim()) {
            messages.push({
                sender: 'Unknown',
                text: line.trim(),
                length: line.trim().length
            });
        }
    });

    return messages;
}

// Calculate trustworthiness score (0-100)
function calculateTrustScore(messages, analysisType) {
    let score = 70; // Base score

    // Analyze patterns
    const patterns = {
        contradictions: countContradictions(messages),
        avoidance: countAvoidancePatterns(messages),
        consistencyShifts: countConsistencyShifts(messages),
        responseTime: analyzeResponsePatterns(messages),
        wordChoices: analyzeWordChoices(messages)
    };

    // Adjust score based on patterns
    score -= patterns.contradictions * 5;
    score -= patterns.avoidance * 4;
    score -= patterns.consistencyShifts * 3;
    score -= patterns.responseTime * 2;
    score -= patterns.wordChoices * 2;

    // Boost for positive patterns
    if (messages.length > 0) {
        const avgMessageLength = messages.reduce((sum, m) => sum + m.length, 0) / messages.length;
        if (avgMessageLength > 30) score += 5;
        if (avgMessageLength > 60) score += 5;
    }

    // Focus adjustments
    if (analysisType === 'deception') {
        score -= patterns.contradictions * 2;
    } else if (analysisType === 'emotional') {
        score -= patterns.consistencyShifts * 2;
    } else if (analysisType === 'behavioral') {
        score -= patterns.avoidance * 2;
    }

    return Math.max(0, Math.min(100, Math.round(score)));
}

// Detect deception patterns
function detectDeceptionPatterns(messages) {
    const patterns = [];

    // Check for contradictions
    const contradictions = countContradictions(messages);
    if (contradictions > 0) {
        patterns.push(`${contradictions} potential contradiction(s) detected`);
    }

    // Check for vague language
    const vagueMessages = messages.filter(m => 
        /maybe|guess|think|could be|might|possibly/i.test(m.text)
    ).length;
    if (vagueMessages > messages.length * 0.3) {
        patterns.push('Excessive use of uncertain language');
    }

    // Check for deflection
    const deflections = messages.filter(m => 
        /what about you|why do you ask|that's not important|anyway/i.test(m.text)
    ).length;
    if (deflections > 0) {
        patterns.push(`${deflections} potential deflection(s)`);
    }

    // Check for over-explaining
    const overtlyLongMessages = messages.filter(m => m.length > 150).length;
    if (overtlyLongMessages > messages.length * 0.4) {
        patterns.push('Tendency to over-explain (defensive indicator)');
    }

    return patterns.length > 0 ? patterns : ['No major deception patterns detected'];
}

// Detect ghosting signals
function detectGhostingSignals(messages) {
    const signals = [];
    let responseGaps = 0;
    let shortResponses = 0;

    // Analyze response patterns
    let lastSender = null;
    for (let i = 0; i < messages.length; i++) {
        if (lastSender && messages[i].sender !== lastSender) {
            responseGaps++;
            if (messages[i].length < 20) shortResponses++;
        }
        lastSender = messages[i].sender;
    }

    if (responseGaps > messages.length * 0.5) {
        signals.push('Frequent topic changes without engagement');
    }

    if (shortResponses > messages.length * 0.4) {
        signals.push('Pattern of minimal responses');
    }

    // Check for unavailability statements
    const unavailabilityIndicators = messages.filter(m => 
        /busy|tired|later|maybe|not sure|packed/i.test(m.text)
    ).length;
    if (unavailabilityIndicators > messages.length * 0.3) {
        signals.push('Frequent unavailability mentions');
    }

    return signals.length > 0 ? signals : ['No clear ghosting behavior detected'];
}

// Analyze emotional shifts
function analyzeEmotionalShifts(messages) {
    const shifts = [];
    
    // Simple sentiment tracking
    let previousSentiment = null;
    messages.forEach((msg, idx) => {
        const sentiment = detectSentiment(msg.text);
        
        if (previousSentiment && Math.abs(sentiment - previousSentiment) > 0.4) {
            shifts.push({
                position: idx,
                from: previousSentiment > 0 ? 'positive' : 'negative',
                to: sentiment > 0 ? 'positive' : 'negative'
            });
        }
        previousSentiment = sentiment;
    });

    return shifts.length > 0 ? 
        `${shifts.length} notable emotional shift(s) detected` :
        'Consistent emotional tone';
}

// Generate emotional timeline
function generateEmotionalTimeline(messages) {
    return messages.map(msg => ({
        sentiment: detectSentiment(msg.text),
        message: msg.text.substring(0, 30) + '...'
    }));
}

// Detect sentiment (-1 = negative, 0 = neutral, 1 = positive)
function detectSentiment(text) {
    const positiveWords = /love|happy|great|awesome|excellent|good|amazing|wonderful|fantastic|perfect/gi;
    const negativeWords = /hate|sad|bad|terrible|awful|horrible|disgusting|angry|upset|worried|scared/gi;
    const neutralWords = /okay|alright|fine|sure|yeah|no|maybe/gi;

    const positive = (text.match(positiveWords) || []).length;
    const negative = (text.match(negativeWords) || []).length;
    const neutral = (text.match(neutralWords) || []).length;

    if (positive > negative) return 0.6 + (positive * 0.05);
    if (negative > positive) return -0.6 - (negative * 0.05);
    return 0.1;
}

// Analyze behavior patterns
function analyzeBehaviorPatterns(messages) {
    const patterns = [];

    // Engagement level
    const engagementQuestions = messages.filter(m => /\?/.test(m.text)).length;
    if (engagementQuestions === 0) {
        patterns.push('Low engagement - minimal questions asked');
    } else if (engagementQuestions > messages.length * 0.5) {
        patterns.push('High engagement - frequent questions and interest');
    }

    // Response consistency
    let senders = new Set();
    messages.forEach(m => senders.add(m.sender));
    if (senders.size === 2) {
        let sender1Count = messages.filter(m => m.sender === [...senders][0]).length;
        let sender2Count = messages.filter(m => m.sender === [...senders][1]).length;
        
        if (Math.abs(sender1Count - sender2Count) > messages.length * 0.3) {
            patterns.push('Unbalanced participation');
        }
    }

    return patterns;
}

// Generate risk indicators
function generateRiskIndicators(messages, analysisType) {
    const indicators = [];

    const contradictions = countContradictions(messages);
    if (contradictions > 2) {
        indicators.push({ level: 'high', text: 'Multiple contradictions' });
    } else if (contradictions > 0) {
        indicators.push({ level: 'medium', text: 'Some contradictory statements' });
    }

    const avoidance = countAvoidancePatterns(messages);
    if (avoidance > 2) {
        indicators.push({ level: 'high', text: 'Significant avoidance behavior' });
    }

    const consistencyIssues = countConsistencyShifts(messages);
    if (consistencyIssues > messages.length * 0.3) {
        indicators.push({ level: 'medium', text: 'Moderate consistency shifts' });
    }

    return indicators.length > 0 ? indicators : [{ level: 'low', text: 'No major risk indicators' }];
}

// AI vs Human Detection
function detectAIPatterns(messages, conversationType) {
    const aiIndicators = [];
    const humanIndicators = [];
    let aiScore = 0; // 0-100, higher = more likely AI
    
    // Check for AI-like patterns
    const aiPhrases = /i'm an ai|i'm an artificial intelligence|as an ai|i cannot|i don't have|i don't experience|unable to|i'm designed|my programming|i was trained|language model|i don't have personal|i can't form|i don't feel|i provide information|i appreciate your question/gi;
    const aiPhrasesCount = (text => {
        let count = 0;
        messages.forEach(m => {
            count += (m.text.match(aiPhrases) || []).length;
        });
        return count;
    })();
    
    if (aiPhrasesCount > 0) {
        aiIndicators.push(`${aiPhrasesCount} explicit AI identifier(s) detected`);
        aiScore += 25;
    }
    
    // Check for overly formal language
    const formalWords = /furthermore|moreover|in conclusion|conversely|it is important to note|i would like to highlight|please note|kindly|hereby|thus|hence|accordingly/gi;
    const formalCount = messages.reduce((sum, m) => sum + (m.text.match(formalWords) || []).length, 0);
    if (formalCount > 2) {
        aiIndicators.push('Overly formal language pattern');
        aiScore += 15;
    }
    
    // Check for perfect emoji/punctuation consistency
    const emojiBadMessages = messages.filter(m => 
        /[😀😁😂🤣😃😄😅🙂🤗😊😇🤩😍😘😗😁😌😌🤔😐😑😶😏😒😞😔😟😕🙁😲😳😦😦😧😨😰😥😢😭😱😖😣😞😓😩😫🥺😤😠😡😤🤬😈👿💀☠️💩🤡👹👺👻👽👾🤖]/g.test(m.text)
    ).length;
    
    // Check for perfect email-like formatting in responses  
    const structuredResponses = messages.filter(m => {
        return /^(here|well|certainly|absolutely|of course|yes|no)[\s\.,;:]|^[-*•]\s|\d\.\s+[A-Z]/i.test(m.text);
    }).length;
    if (structuredResponses > messages.length * 0.4) {
        aiIndicators.push('Highly structured response format');
        aiScore += 12;
    }
    
    // Check for lack of personal anecdotes/experiences
    const personalReferences = messages.filter(m => 
        /i remember|i once|when i was|i've always|i used to|my friend|my family|my experience|that happened to me|i learned|i discovered/gi.test(m.text)
    ).length;
    if (personalReferences === 0 && messages.length > 5) {
        aiIndicators.push('No personal anecdotes or experiences shared');
        aiScore += 10;
    }
    
    // Check for perfect consistency (no contradictions)
    const contradictions = countContradictions(messages);
    if (contradictions === 0 && messages.length > 8) {
        aiIndicators.push('Perfect consistency - no contradictions');
        aiScore += 10;
    }
    
    // Check for emotional variety (AIs tend to be consistent)
    const emotionalVariety = analyzeEmotionVariety(messages);
    if (emotionalVariety < 0.3) {
        aiIndicators.push('Minimal emotional variation');
        aiScore += 8;
    }
    
    // Check for overly helpful/polite tone
    const helpfulPhrases = /happy to help|let me know|feel free to|don't hesitate|i'm here to|pleasure to assist|absolutely|certainly|of course|you're welcome/gi;
    const helpfulCount = messages.reduce((sum, m) => sum + (m.text.match(helpfulPhrases) || []).length, 0);
    if (helpfulCount > 3) {
        aiIndicators.push('Excessively helpful/polite tone');
        aiScore += 8;
    }
    
    // Check for informative summaries (often AI trait)
    const summaryPhrases = /in summary|to summarize|in conclusion|to recap|key points|main takeaways|in essence|essentially/gi;
    const summaryCount = messages.reduce((sum, m) => sum + (m.text.match(summaryPhrases) || []).length, 0);
    if (summaryCount > 1) {
        aiIndicators.push('Multiple summary/recap statements');
        aiScore += 7;
    }
    
    // Check message length consistency
    const avgLen = messages.reduce((sum, m) => sum + m.length, 0) / messages.length;
    const lengthDeviation = Math.sqrt(
        messages.reduce((sum, m) => sum + Math.pow(m.length - avgLen, 2), 0) / messages.length
    );
    if (lengthDeviation < avgLen * 0.3) {
        aiIndicators.push('Very consistent message lengths');
        aiScore += 6;
    }
    
    // Check for casual/human-like language
    const casualWords = /lol|haha|ya|gonna|wanna|gotta|kinda|sorta|like|omg|wtf|literally|actually|idk|tbh|ngl|fr|bruh|sarcasm|joking|kidding/gi;
    const casualCount = messages.reduce((sum, m) => sum + (m.text.match(casualWords) || []).length, 0);
    if (casualCount > 3) {
        humanIndicators.push('Casual/informal language detected');
        aiScore -= 15;
    }
    
    // Check for typos and errors (human trait)
    const typoPatterns = /\s{2,}|[a-z]{2,}\s+[a-z]{2,}/gi; // double spaces, common typo patterns
    const typoCount = messages.filter(m => /\s{2,}|ur |u r |im |ur |ur | thats | whats | hows | theyre | ive /i.test(m.text)).length;
    if (typoCount > 2) {
        humanIndicators.push('Typos and casual mistakes detected');
        aiScore -= 10;
    }
    
    // Check for emotional/personal expressions
    const emotionalExpressions = messages.filter(m => 
        /😊|😂|😍|😢|😡|😎|🤔|❤️|💔|🎉|😭|😪|😴|😩|😤|😠|😡|😱|😨|😰|😔|😕|😞|😟|😲|😳|😦|😧|😮|😲|😵|🙋|🤷|🤦|😂|🤣|😆|😄|😃|😊|😉|😌|🥰|😍|🤩|😘|😗|😚|😙|🥲|😋|😛|😜|🤪|😝|😑|😐|😶|🤐|🤫|🤬|🤨|😐|😏|😒|🙁|☹️|😕|😔|😟|😞|😖|😢|😭|😤|😠|😡|🤬|😳|😵|🥺|😦|😧|😨|😰|😢|😭|🤮|🤢|🤮|🤮|🤮|🤮|🤮/g.test(m.text)
    ).length;
    if (emotionalExpressions > messages.length * 0.3) {
        humanIndicators.push('Frequent emotional expressions through emojis');
        aiScore -= 12;
    }
    
    // Check for conversational patterns (asking back, engagement)
    const askingQuestions = messages.filter(m => /\?/.test(m.text)).length;
    if (askingQuestions > messages.length * 0.4) {
        // Could go either way, but excessive questions might indicate engagement
        humanIndicators.push('High engagement with back-and-forth questions');
        aiScore -= 5;
    }
    
    // Normalize the score
    aiScore = Math.max(0, Math.min(100, aiScore));
    
    // Determine result based on settings
    let detection = {
        aiScore: aiScore,
        prediction: '',
        confidence: 0,
        indicators: []
    };
    
    if (conversationType === 'auto') {
        if (aiScore >= 60) {
            detection.prediction = 'Likely AI Conversation';
            detection.confidence = Math.min(95, 50 + (aiScore - 60) / 2);
            detection.indicators = aiIndicators;
        } else if (aiScore >= 40) {
            detection.prediction = 'Mixed or Unclear';
            detection.confidence = Math.abs(50 - aiScore);
            detection.indicators = [...aiIndicators, ...humanIndicators];
        } else {
            detection.prediction = 'Likely Human Conversation';
            detection.confidence = Math.min(95, 50 + (50 - aiScore) / 2);
            detection.indicators = humanIndicators;
        }
    } else if (conversationType === 'ai') {
        detection.prediction = 'Analyzing as AI Conversation';
        detection.confidence = 100;
        detection.indicators = aiIndicators.length > 0 ? aiIndicators : ['No specific AI patterns detected'];
    } else {
        detection.prediction = 'Analyzing as Human Conversation';
        detection.confidence = 100;
        detection.indicators = humanIndicators.length > 0 ? humanIndicators : ['Normal human conversation patterns'];
    }
    
    return detection;
}

// Helper function to analyze emotional variety
function analyzeEmotionVariety(messages) {
    const sentiments = messages.map(m => detectSentiment(m.text));
    const uniqueSentiments = new Set(sentiments.map(s => Math.round(s * 10)));
    return uniqueSentiments.size / sentiments.length; // Variety ratio (0-1)
}

// Helper functions
function countContradictions(messages) {
    // Simple contradiction detection
    let count = 0;
    for (let i = 0; i < messages.length - 1; i++) {
        const text1 = messages[i].text.toLowerCase();
        const text2 = messages[i + 1].text.toLowerCase();
        
        if ((text1.includes('i was') && text2.includes("wasn't")) ||
            (text1.includes('yes') && text2.includes('no')) ||
            (text1.includes('definitely') && text2.includes('maybe'))) {
            count++;
        }
    }
    return count;
}

function countAvoidancePatterns(messages) {
    return messages.filter(m => 
        /anyway|moving on|let's talk about|but|changes subject/i.test(m.text)
    ).length;
}

function countConsistencyShifts(messages) {
    let shifts = 0;
    for (let i = 1; i < messages.length; i++) {
        const sentiment1 = detectSentiment(messages[i - 1].text);
        const sentiment2 = detectSentiment(messages[i].text);
        if (Math.abs(sentiment1 - sentiment2) > 0.5) shifts++;
    }
    return shifts;
}

function analyzeResponsePatterns(messages) {
    // Check for irregular response patterns
    let senders = {};
    messages.forEach(m => {
        senders[m.sender] = (senders[m.sender] || 0) + 1;
    });
    
    const values = Object.values(senders);
    const avgResponses = values.reduce((a, b) => a + b) / values.length;
    let irregularity = 0;
    
    values.forEach(v => {
        if (Math.abs(v - avgResponses) > avgResponses * 0.5) irregularity++;
    });
    
    return irregularity;
}

function analyzeWordChoices(messages) {
    const deceptiveWords = messages.filter(m => 
        /honestly|truthfully|frankly|believe me|to be honest/i.test(m.text)
    ).length;
    return deceptiveWords > 2 ? 2 : 0;
}

function analyzeMessageMetrics(messages) {
    return {
        totalMessages: messages.length,
        averageLength: Math.round(messages.reduce((sum, m) => sum + m.length, 0) / messages.length),
        shortMessages: messages.filter(m => m.length < 20).length,
        longMessages: messages.filter(m => m.length > 100).length
    };
}

// Display results
function displayResults(analysis) {
    const resultsPanel = document.getElementById('resultsPanel');
    resultsPanel.innerHTML = '';

    // Trust Score Card
    const trustScoreCard = createTrustScoreCard(analysis.trustScore);
    resultsPanel.appendChild(trustScoreCard);

    // AI Detection Card
    const aiDetectionCard = createAIDetectionCard(analysis.aiDetection);
    resultsPanel.appendChild(aiDetectionCard);

    // SNK Analysis Card (if Grok is enabled)
    if (document.getElementById('enableGrok')?.checked) {
        const chatInput = document.getElementById('chatInput').value;
        const snkData = performSNKAnalysis(chatInput);
        const snkCard = createSNKAnalysisCard(snkData);
        resultsPanel.appendChild(snkCard);
    }

    // Message Metrics
    const metricsCard = createMetricsCard(analysis.messageAnalysis);
    resultsPanel.appendChild(metricsCard);

    // Emotional Timeline
    const timelineCard = createTimelineCard(analysis.emotionalTimeline);
    resultsPanel.appendChild(timelineCard);

    // Deception Patterns
    const deceptionCard = createAnalysisCard(
        'Deception Indicators',
        analysis.deceptionPatterns,
        'fas fa-warning'
    );
    resultsPanel.appendChild(deceptionCard);

    // Ghosting Signals
    const ghostingCard = createAnalysisCard(
        'Ghosting Signals',
        analysis.ghostingSignals,
        'fas fa-heart-break'
    );
    resultsPanel.appendChild(ghostingCard);

    // Emotional Shifts
    const emotionalCard = document.createElement('div');
    emotionalCard.className = 'analysis-section';
    emotionalCard.innerHTML = `
        <h3><i class="fas fa-face-smile"></i> Emotional Consistency</h3>
        <div class="analysis-content">${analysis.emotionalShifts}</div>
    `;
    resultsPanel.appendChild(emotionalCard);

    // Risk Indicators
    const riskCard = createRiskCard(analysis.riskIndicators);
    resultsPanel.appendChild(riskCard);

    // Insights Section
    const insightsCard = createInsightsCard(analysis);
    resultsPanel.appendChild(insightsCard);
}

function createTrustScoreCard(score) {
    const card = document.createElement('div');
    card.className = 'trust-score-container';
    
    let interpretation = '';
    if (score >= 80) interpretation = 'High trustworthiness';
    else if (score >= 60) interpretation = 'Moderate trustworthiness';
    else if (score >= 40) interpretation = 'Mixed signals';
    else interpretation = 'Low trustworthiness indicators';

    const fillPercentage = score;
    
    card.innerHTML = `
        <div class="trust-score-label">TRUSTWORTHINESS SCORE</div>
        <div class="trust-score-value">${score}%</div>
        <div class="trust-score-bar">
            <div class="trust-score-fill" style="width: 0%; animation: slideIn 1s ease-out forwards;">
                <div style="width: 100%; height: 100%;"></div>
            </div>
        </div>
        <div class="trust-score-interpretation">${interpretation}</div>
    `;

    // Animate the bar fill
    setTimeout(() => {
        card.querySelector('.trust-score-fill').style.width = fillPercentage + '%';
    }, 100);

    return card;
}

function createAIDetectionCard(detection) {
    const card = document.createElement('div');
    card.className = 'analysis-section';
    
    let icon = 'fas fa-robot';
    let bgClass = 'ai-section';
    
    if (detection.prediction.includes('Human')) {
        icon = 'fas fa-user';
        bgClass = 'human-section';
    } else if (detection.prediction.includes('Mixed')) {
        icon = 'fas fa-question-circle';
        bgClass = 'mixed-section';
    }
    
    let content = `<h3 style="margin-bottom: 15px;"><i class="${icon}"></i> AI vs. Human Detection</h3>`;
    content += `<div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; margin-bottom: 15px;">`;
    content += `<div style="font-size: 24px; font-weight: bold; color: #00d4ff; margin-bottom: 8px;">${detection.prediction}</div>`;
    content += `<div style="font-size: 14px; color: rgba(255,255,255,0.8);">`;
    content += `<span style="background: rgba(0,212,255,0.2); padding: 4px 12px; border-radius: 20px;">Confidence: ${Math.round(detection.confidence)}%</span>`;
    content += `</div>`;
    
    // AI Score Bar
    content += `<div style="margin-top: 12px;">`;
    content += `<div style="font-size: 12px; margin-bottom: 5px; opacity: 0.8;">AI Score: ${detection.aiScore}/100</div>`;
    content += `<div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">`;
    content += `<div style="width: ${detection.aiScore}%; height: 100%; background: linear-gradient(90deg, #00d4ff, #0099ff); border-radius: 4px;"></div>`;
    content += `</div>`;
    content += `</div>`;
    content += `</div>`;
    
    // Indicators
    if (detection.indicators.length > 0) {
        content += '<div style="margin-top: 15px;"><strong>Key Indicators:</strong></div>';
        content += '<ul class="insight-list" style="margin-top: 10px;">';
        detection.indicators.forEach(indicator => {
            content += `<li><i class="fas fa-check-circle" style="color: #00d4ff; margin-right: 8px;"></i>${indicator}</li>`;
        });
        content += '</ul>';
    }
    
    card.innerHTML = content;
    return card;
}

function createMetricsCard(metrics) {
    const card = document.createElement('div');
    card.className = 'analysis-section';
    card.innerHTML = `
        <h3><i class="fas fa-chart-bar"></i> Message Metrics</h3>
        <div class="analysis-content">
            <ul class="insight-list">
                <li>Total messages: <strong>${metrics.totalMessages}</strong></li>
                <li>Average message length: <strong>${metrics.averageLength}</strong> characters</li>
                <li>Short messages: <strong>${metrics.shortMessages}</strong></li>
                <li>Long messages: <strong>${metrics.longMessages}</strong></li>
            </ul>
        </div>
    `;
    return card;
}

function createTimelineCard(timeline) {
    const card = document.createElement('div');
    card.className = 'analysis-section';
    
    let timelineHTML = '<h3><i class="fas fa-chart-line"></i> Emotional Timeline</h3>';
    timelineHTML += '<div class="emotion-timeline">';
    timelineHTML += '<div class="timeline-labels"><span>Negative</span><span>Neutral</span><span>Positive</span></div>';
    timelineHTML += '<div class="emotion-bar">';
    
    // Add markers for each sentiment
    timeline.forEach((item, idx) => {
        const position = ((item.sentiment + 1) / 2) * 100;
        timelineHTML += `<div class="emotion-marker" style="left: ${position}%; animation: appear 0.8s ease-out ${idx * 0.1}s both;"></div>`;
    });
    
    timelineHTML += '</div></div>';
    
    card.innerHTML = timelineHTML;
    return card;
}

function createAnalysisCard(title, items, icon) {
    const card = document.createElement('div');
    card.className = 'analysis-section';
    
    let content = `<h3><i class="${icon}"></i> ${title}</h3>`;
    content += '<div class="analysis-content"><ul class="insight-list">';
    
    if (Array.isArray(items)) {
        items.forEach(item => {
            content += `<li>${item}</li>`;
        });
    } else {
        content += `<li>${items}</li>`;
    }
    
    content += '</ul></div>';
    card.innerHTML = content;
    
    return card;
}

function createRiskCard(indicators) {
    const card = document.createElement('div');
    card.className = 'analysis-section';
    
    let content = '<h3><i class="fas fa-exclamation-triangle"></i> Risk Assessment</h3>';
    content += '<div class="risk-indicators">';
    
    indicators.forEach(indicator => {
        content += `
            <div class="risk-item ${indicator.level}">
                <span class="risk-badge">${indicator.level.toUpperCase()}</span>
                <span class="risk-text">${indicator.text}</span>
            </div>
        `;
    });
    
    content += '</div>';
    card.innerHTML = content;
    
    return card;
}

function createInsightsCard(analysis) {
    const card = document.createElement('div');
    card.className = 'analysis-section';
    
    const insights = generateAIInsights(analysis);
    
    let content = '<h3><i class="fas fa-lightbulb"></i> AI Insights & Recommendations</h3>';
    content += '<div class="analysis-content"><ul class="insight-list">';
    
    insights.forEach(insight => {
        content += `<li>${insight}</li>`;
    });
    
    content += '</ul></div>';
    card.innerHTML = content;
    
    return card;
}

function generateAIInsights(analysis) {
    const insights = [];
    
    if (analysis.trustScore < 50) {
        insights.push('Communication shows mixed trustworthiness signals - recommend clarification conversations.');
    }
    
    if (analysis.deceptionPatterns.length > 1) {
        insights.push('Multiple deception indicators detected - proceed with caution in future interactions.');
    }
    
    if (analysis.ghostingSignals.length > 0) {
        insights.push('Some avoidance behaviors detected - may indicate reduced engagement.');
    }
    
    if (analysis.messageAnalysis.averageLength < 30) {
        insights.push('Short message pattern suggests minimal effort in communication.');
    }
    
    if (analysis.messageAnalysis.longMessages > analysis.messageAnalysis.totalMessages * 0.3) {
        insights.push('Frequent detailed messages may indicate over-explaining or defensive positioning.');
    }
    
    if (insights.length === 0) {
        insights.push('Overall, conversation patterns appear relatively straightforward.');
    }
    
    return insights;
}

// Show loading state
function showLoading() {
    const resultsPanel = document.getElementById('resultsPanel');
    resultsPanel.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <span>Analyzing conversation...</span>
        </div>
    `;
}

// Clear results
function clearResults() {
    document.getElementById('chatInput').value = '';
    document.getElementById('voiceInput').value = '';
    document.getElementById('resultsPanel').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-inbox"></i>
            <p>Results will appear here after analyzing.</p>
        </div>
    `;
}

// Handle voice message upload
function handleVoiceUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    showLoading();
    
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('audio_file', file);

    // Simulate voice processing
    setTimeout(() => {
        const voiceAnalysis = {
            transcription: "Voice message transcribed: This is a sample transcription of the voice message.",
            duration: "00:15",
            audio_features: {
                pitch: "Medium (120Hz avg)",
                tempo: "Normal (100 BPM)",
                energy: "High",
                audio_quality: "Good"
            },
            voice_emotion: {
                detected_emotion: "Neutral/Friendly",
                confidence: 0.78,
                energy_level: "High"
            },
            snk_analysis: performSNKAnalysis("Voice message transcribed: This is a sample transcription of the voice message.")
        };

        const verbatimTranscription = voiceAnalysis.transcription;
        document.getElementById('chatInput').value = verbatimTranscription;
        
        displayVoiceAnalysis(voiceAnalysis);
    }, 2000);
}

// Perform SNK Analysis (Sentiment, NLP, Keywords)
function performSNKAnalysis(text) {
    // Sentiment Analysis
    const sentiment = analyzeSentimentAdvanced(text);
    
    // Keyword Extraction
    const keywords = extractKeywords(text);
    
    // NLP Pattern Analysis
    const nlpPatterns = analyzeNLPPatterns(text);
    
    // Emotional Content
    const emotions = detectEmotionalContent(text);
    
    return {
        sentiment: sentiment,
        keywords: keywords,
        nlp_patterns: nlpPatterns,
        emotions: emotions
    };
}

// Advanced sentiment analysis
function analyzeSentimentAdvanced(text) {
    const positiveWords = /amazing|excellent|wonderful|fantastic|love|great|good|happy|perfect|awesome/gi;
    const negativeWords = /horrible|terrible|bad|hate|awful|disgusting|angry|sad|depressed|worst/gi;
    const neutralWords = /okay|alright|fine|normal|average|moderate|middle/gi;

    const positive = (text.match(positiveWords) || []).length;
    const negative = (text.match(negativeWords) || []).length;
    const neutral = (text.match(neutralWords) || []).length;

    let score = 0;
    let label = 'Neutral';

    if (positive > negative) {
        score = Math.min(0.9, 0.5 + (positive * 0.15));
        label = positive > 3 ? 'Very Positive' : 'Positive';
    } else if (negative > positive) {
        score = Math.max(-0.9, -0.5 - (negative * 0.15));
        label = negative > 3 ? 'Very Negative' : 'Negative';
    } else {
        score = 0;
        label = 'Neutral';
    }

    return {
        score: score.toFixed(2),
        label: label,
        word_counts: {
            positive: positive,
            negative: negative,
            neutral: neutral
        }
    };
}

// Extract keywords from text
function extractKeywords(text) {
    const stopWords = ['the', 'a', 'an', 'is', 'are', 'was', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during'];
    
    // Extract words
    const words = text.toLowerCase().match(/\b\w+\b/g) || [];
    
    // Filter stopwords and count
    const keywordCount = {};
    words.forEach(word => {
        if (!stopWords.includes(word) && word.length > 2) {
            keywordCount[word] = (keywordCount[word] || 0) + 1;
        }
    });

    // Sort by frequency
    const sortedKeywords = Object.entries(keywordCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8)
        .map(([keyword, freq]) => ({ keyword, frequency: freq }));

    return sortedKeywords;
}

// Analyze NLP patterns
function analyzeNLPPatterns(text) {
    const sentences = text.split(/[.!?]+/).filter(s => s.trim());
    const words = text.split(/\s+/).filter(w => w.trim());
    
    const questions = (text.match(/\?/g) || []).length;
    const exclamations = (text.match(/!/g) || []).length;
    
    const avgWordsPerSentence = sentences.length > 0 ? (words.length / sentences.length).toFixed(1) : 0;
    const avgWordLength = words.length > 0 ? (text.length / words.length).toFixed(1) : 0;

    return {
        sentence_count: sentences.length,
        word_count: words.length,
        avg_words_per_sentence: avgWordsPerSentence,
        avg_word_length: avgWordLength,
        question_count: questions,
        exclamation_count: exclamations,
        lexical_diversity: ((new Set(words).size / words.length) * 100).toFixed(1) + '%'
    };
}

// Detect emotional content
function detectEmotionalContent(text) {
    const emotionalMarkers = {
        joy: ['happy', 'joy', 'excited', 'love', 'wonderful', 'great'],
        sadness: ['sad', 'depressed', 'unhappy', 'terrible', 'awful'],
        anger: ['angry', 'furious', 'hate', 'disgusted', 'furious'],
        fear: ['afraid', 'scared', 'worried', 'anxious', 'nervous'],
        trust: ['trust', 'believe', 'confident', 'sure', 'certain'],
        surprise: ['wow', 'amazing', 'surprising', 'unexpected', 'shocked']
    };

    const detectedEmotions = {};
    const textLower = text.toLowerCase();

    for (const [emotion, markers] of Object.entries(emotionalMarkers)) {
        const count = markers.filter(marker => textLower.includes(marker)).length;
        if (count > 0) {
            detectedEmotions[emotion] = count;
        }
    }

    return {
        detected_emotions: detectedEmotions,
        dominant_emotion: Object.keys(detectedEmotions).length > 0 
            ? Object.entries(detectedEmotions).sort((a, b) => b[1] - a[1])[0][0]
            : 'neutral',
        emotional_intensity: Object.values(detectedEmotions).length
    };
}

// Display voice analysis results
function displayVoiceAnalysis(analysis) {
    const resultsPanel = document.getElementById('resultsPanel');
    resultsPanel.innerHTML = '';

    // Voice Transcription Card
    const transcriptionCard = document.createElement('div');
    transcriptionCard.className = 'analysis-section';
    transcriptionCard.innerHTML = `
        <h3><i class="fas fa-microphone"></i> Voice Message Analysis</h3>
        <div class="analysis-content">
            <div style="background: rgba(0,212,255,0.1); padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                <strong>Transcription:</strong>
                <p style="margin-top: 8px; font-style: italic;">"${analysis.transcription.substring(0, 200)}..."</p>
            </div>
            <ul class="insight-list">
                <li>Duration: <strong>${analysis.duration}</strong></li>
                <li>Audio Quality: <strong>${analysis.audio_features.audio_quality}</strong></li>
                <li>Detected Emotion: <strong>${analysis.voice_emotion.detected_emotion}</strong></li>
                <li>Confidence: <strong>${(analysis.voice_emotion.confidence * 100).toFixed(0)}%</strong></li>
            </ul>
        </div>
    `;
    resultsPanel.appendChild(transcriptionCard);

    // SNK Analysis Card
    const snkCard = createSNKAnalysisCard(analysis.snk_analysis);
    resultsPanel.appendChild(snkCard);

    // Audio Features
    const featuresCard = document.createElement('div');
    featuresCard.className = 'analysis-section';
    featuresCard.innerHTML = `
        <h3><i class="fas fa-sliders-h"></i> Audio Features</h3>
        <div class="analysis-content">
            <ul class="insight-list">
                <li>Pitch Level: <strong>${analysis.audio_features.pitch}</strong></li>
                <li>Speech Tempo: <strong>${analysis.audio_features.tempo}</strong></li>
                <li>Energy Level: <strong>${analysis.audio_features.energy}</strong></li>
            </ul>
        </div>
    `;
    resultsPanel.appendChild(featuresCard);

    // Add regular analysis as well
    const combinedAnalysis = {
        trustScore: 72,
        emotionalTimeline: [],
        deceptionPatterns: [],
        emotionalShifts: 'Consistent',
        ghostingSignals: ['None detected'],
        behaviorPatterns: [],
        messageAnalysis: { totalMessages: 1, averageLength: 45, shortMessages: 0, longMessages: 0 },
        riskIndicators: [{ level: 'low', text: 'Voice message appears authentic' }],
        aiDetection: { aiScore: 15, prediction: 'Likely Human Voice', confidence: 85, indicators: ['Natural speech patterns', 'Authentic emotion'] }
    };

    const trustCard = createTrustScoreCard(combinedAnalysis.trustScore);
    resultsPanel.appendChild(trustCard);

    const aiCard = createAIDetectionCard(combinedAnalysis.aiDetection);
    resultsPanel.appendChild(aiCard);
}

// Create SNK Analysis Card
function createSNKAnalysisCard(snkData) {
    const card = document.createElement('div');
    card.className = 'analysis-section';

    let html = '<h3><i class="fas fa-chart-pie"></i> SNK Analysis (Sentiment/NLP/Keywords)</h3>';
    html += '<div class="analysis-content">';

    // Sentiment
    html += '<div style="margin-bottom: 20px;">';
    html += `<strong>Sentiment:</strong> <span style="color: ${snkData.sentiment.score > 0 ? '#00d4ff' : '#ff6b6b'}">${snkData.sentiment.label}</span> (${snkData.sentiment.score})`;
    html += '<div style="margin-top: 8px; font-size: 12px; opacity: 0.8;">';
    html += `<span>Positive: ${snkData.sentiment.word_counts.positive} | Negative: ${snkData.sentiment.word_counts.negative} | Neutral: ${snkData.sentiment.word_counts.neutral}</span>`;
    html += '</div></div>';

    // NLP Patterns
    html += '<div style="margin-bottom: 20px;">';
    html += '<strong>NLP Patterns:</strong>';
    html += '<ul class="insight-list" style="margin-top: 8px;">';
    html += `<li>Sentences: <strong>${snkData.nlp_patterns.sentence_count}</strong></li>`;
    html += `<li>Words: <strong>${snkData.nlp_patterns.word_count}</strong></li>`;
    html += `<li>Avg Words/Sentence: <strong>${snkData.nlp_patterns.avg_words_per_sentence}</strong></li>`;
    html += `<li>Lexical Diversity: <strong>${snkData.nlp_patterns.lexical_diversity}</strong></li>`;
    html += '</ul></div>';

    // Keywords
    html += '<div style="margin-bottom: 20px;">';
    html += '<strong>Top Keywords:</strong>';
    html += '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">';
    snkData.keywords.forEach(kw => {
        html += `<span style="background: rgba(0,212,255,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px;">
            ${kw.keyword} <span style="opacity: 0.7;">(${kw.frequency})</span>
        </span>`;
    });
    html += '</div></div>';

    // Emotions
    html += '<div>';
    html += '<strong>Emotional Tone:</strong>';
    if (Object.keys(snkData.emotions.detected_emotions).length > 0) {
        html += '<ul class="insight-list" style="margin-top: 8px;">';
        for (const [emotion, count] of Object.entries(snkData.emotions.detected_emotions)) {
            html += `<li>${emotion.charAt(0).toUpperCase() + emotion.slice(1)}: <strong>${count}</strong></li>`;
        }
        html += '</ul>';
    } else {
        html += '<p style="margin-top: 8px; opacity: 0.7;">No significant emotional markers detected</p>';
    }
    html += '</div>';

    html += '</div>';
    card.innerHTML = html;
    return card;
}

// Animation keyframe
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        0% { width: 0%; }
        100% { width: var(--target-width); }
    }
    @keyframes appear {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
`;
document.head.appendChild(style);
