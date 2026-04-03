/**
 * TruthLens AI Configuration
 * Stores API keys and settings for advanced services
 */

// Grok API Configuration
const GROK_CONFIG = {
    API_KEY: "xai-pPPOPwicopg9N2i28aJvNY2HTah7w3MeEtsEQREDsVdYEFWcqn1ixkg6voE5SVoeLeRsGyC93llTvsDy",
    BASE_URL: "https://api.x.ai/v1",
    MODEL: "grok-beta",
    MAX_TOKENS: 1000,
    TEMPERATURE: 0.7
};

// Service Configuration
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
    },
    GROK_INTEGRATION: {
        ENABLED: true,
        DECEPTION_DETECTION: true,
        BEHAVIORAL_ANALYSIS: true,
        EMOTIONAL_ANALYSIS: true,
        AI_DETECTION: true
    }
};

// Feature Flags
const FEATURES = {
    VOICE_UPLOAD: true,
    SNK_ANALYSIS: true,
    GROK_API: true,
    AUTO_TRANSCRIBE: true,
    REAL_TIME_ANALYSIS: true
};

// Initialize configuration
function initializeConfig() {
    console.log('TruthLens AI Configuration Initialized');
    console.log('Services:', SERVICE_CONFIG);
    console.log('Features Enabled:', FEATURES);
}

// Get Grok API Key (for backend calls)
function getGrokApiKey() {
    return GROK_CONFIG.API_KEY;
}

// Validate API Key
function validateGrokApiKey(apiKey = null) {
    const key = apiKey || GROK_CONFIG.API_KEY;
    return key && key.startsWith('xai-') && key.length > 20;
}

// Update configuration
function updateConfig(section, updates) {
    if (SERVICE_CONFIG[section]) {
        Object.assign(SERVICE_CONFIG[section], updates);
        console.log(`Updated ${section}:`, updates);
    }
}

// Export configuration
const config = {
    GROK: GROK_CONFIG,
    SERVICES: SERVICE_CONFIG,
    FEATURES: FEATURES,
    validateApiKey: validateGrokApiKey,
    getApiKey: getGrokApiKey,
    updateConfig: updateConfig
};

// Initialize on load
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', initializeConfig);
}
