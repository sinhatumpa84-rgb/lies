"""
Voice Message Analysis Service
Handles WhatsApp voice message transcription and analysis
"""

from typing import Dict, Optional, Tuple
import os
import io
from pathlib import Path
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import requests


class VoiceAnalyzer:
    """Analyze WhatsApp and other voice messages"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize voice analyzer
        
        Args:
            api_key: Optional Google Cloud Speech API key or similar
        """
        self.api_key = api_key
        self.supported_formats = ['.wav', '.mp3', '.ogg', '.m4a', '.flac']
    
    def convert_audio_format(self, audio_path: str, target_format: str = 'wav') -> str:
        """
        Convert audio to target format (default WAV)
        
        Args:
            audio_path: Path to audio file
            target_format: Target format (wav, mp3, etc.)
        
        Returns:
            Path to converted audio file
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            
            # Export to target format
            output_path = audio_path.rsplit('.', 1)[0] + f'_converted.{target_format}'
            audio.export(output_path, format=target_format)
            
            return output_path
        except Exception as e:
            raise ValueError(f"Audio conversion failed: {str(e)}")
    
    def extract_audio_features(self, audio_path: str) -> Dict:
        """
        Extract audio features (pitch, intensity, speed, etc.)
        
        Returns features useful for emotional content analysis
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path)
            
            # Duration
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_centroid_mean = np.mean(spectral_centroids)
            
            # MFCC (Mel-frequency cepstral coefficients)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1)
            
            # Pitch estimation (simplified)
            harmonic, percussive = librosa.effects.hpss(y)
            pitch = np.mean(librosa.feature.chroma_stft(y=harmonic, sr=sr))
            
            # Energy/Loudness
            energy = np.mean(librosa.feature.rms(y=y)[0])
            
            # Tempo estimation
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
            
            # Zero crossing rate (voice activity)
            zcr = np.mean(librosa.feature.zero_crossing_rate(y)[0])
            
            return {
                'duration_seconds': round(duration, 2),
                'sampling_rate': sr,
                'spectral_centroid': round(float(spectral_centroid_mean), 2),
                'mfcc_coefficients': [round(float(x), 3) for x in mfcc_mean],
                'average_pitch': round(float(pitch), 2),
                'energy_loudness': round(float(energy), 3),
                'estimated_tempo': round(float(tempo), 2),
                'zero_crossing_rate': round(float(zcr), 3),
                'audio_quality': self._assess_audio_quality(y, sr)
            }
        except Exception as e:
            raise ValueError(f"Audio feature extraction failed: {str(e)}")
    
    def transcribe_voice_message(self, audio_path: str, use_grok: bool = False) -> Dict:
        """
        Transcribe voice message using Google Cloud Speech or Grok API
        
        For WhatsApp voices, this converts audio to text
        """
        try:
            # Ensure audio is in WAV format
            if not audio_path.endswith('.wav'):
                audio_path = self.convert_audio_format(audio_path, 'wav')
            
            # Extract features while we're at it
            features = self.extract_audio_features(audio_path)
            
            # Transcription method depends on availability
            if use_grok:
                transcription = self._transcribe_with_grok(audio_path)
            else:
                transcription = self._transcribe_with_google(audio_path)
            
            return {
                'transcription': transcription,
                'audio_features': features,
                'confidence': 0.85  # Mock confidence
            }
        except Exception as e:
            raise ValueError(f"Transcription failed: {str(e)}")
    
    def _transcribe_with_google(self, audio_path: str) -> str:
        """Transcribe using Google Cloud Speech API"""
        try:
            from google.cloud import speech
            
            client = speech.SpeechClient()
            
            with open(audio_path, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            
            response = client.recognize(config=config, audio=audio)
            
            transcription = ""
            for result in response.results:
                transcription += result.alternatives[0].transcript
            
            return transcription if transcription else "[Inaudible]"
        except ImportError:
            return "[Google Cloud Speech not available]"
    
    def _transcribe_with_grok(self, audio_path: str) -> str:
        """Transcribe using Grok API"""
        # Grok doesn't directly support audio, so we'd use it for enhanced processing
        # This is a placeholder for potential integration
        return "[Grok transcription not directly available]"
    
    def analyze_voice_emotion(self, audio_path: str) -> Dict:
        """
        Analyze emotional content from voice characteristics
        
        Uses pitch, tempo, energy, and other features to infer emotion
        """
        try:
            features = self.extract_audio_features(audio_path)
            
            # Emotion inference from audio features
            pitch = features['average_pitch']
            tempo = features['estimated_tempo']
            energy = features['energy_loudness']
            
            emotion = self._infer_emotion_from_features(pitch, tempo, energy)
            
            return {
                'detected_emotion': emotion['emotion'],
                'confidence': emotion['confidence'],
                'energy_level': self._energy_to_level(energy),
                'speech_rate': self._tempo_to_rate(tempo),
                'voice_characteristics': {
                    'pitch': features['average_pitch'],
                    'tempo': features['estimated_tempo'],
                    'energy': features['energy_loudness']
                }
            }
        except Exception as e:
            return {
                'detected_emotion': 'Unknown',
                'confidence': 0.0,
                'error': str(e)
            }
    
    @staticmethod
    def _assess_audio_quality(y: np.ndarray, sr: int) -> str:
        """Assess audio quality"""
        # SNR estimation
        rms = np.sqrt(np.mean(y**2))
        if rms > 0.2:
            return "High Quality"
        elif rms > 0.05:
            return "Good Quality"
        elif rms > 0.01:
            return "Acceptable Quality"
        else:
            return "Low Quality"
    
    @staticmethod
    def _infer_emotion_from_features(pitch: float, tempo: float, energy: float) -> Dict:
        """Infer emotion from audio features"""
        emotions = []
        
        # High pitch + high tempo + high energy = excited/happy
        if pitch > 150 and tempo > 120 and energy > 0.5:
            emotions.append(('Excited/Happy', 0.8))
        
        # Low pitch + low tempo + low energy = sad/depressed
        elif pitch < 80 and tempo < 100 and energy < 0.3:
            emotions.append(('Sad/Depressed', 0.7))
        
        # Normal pitch + high energy + fast tempo = confident/angry
        elif 80 <= pitch <= 150 and energy > 0.5 and tempo > 120:
            emotions.append(('Confident/Urgent', 0.6))
        
        # Low pitch + normal energy = neutral/thoughtful
        elif pitch < 100 and 0.2 <= energy <= 0.45:
            emotions.append(('Thoughtful/Neutral', 0.5))
        
        else:
            emotions.append(('Neutral', 0.4))
        
        return {'emotion': emotions[0][0], 'confidence': emotions[0][1]}
    
    @staticmethod
    def _energy_to_level(energy: float) -> str:
        """Convert energy to descriptive level"""
        if energy > 0.5:
            return "Very High"
        elif energy > 0.3:
            return "High"
        elif energy > 0.15:
            return "Normal"
        else:
            return "Low"
    
    @staticmethod
    def _tempo_to_rate(tempo: float) -> str:
        """Convert tempo to speech rate description"""
        if tempo > 150:
            return "Very Fast"
        elif tempo > 120:
            return "Fast"
        elif tempo > 80:
            return "Normal"
        else:
            return "Slow"


def analyze_whatsapp_voice(audio_path: str, api_key: Optional[str] = None) -> Dict:
    """
    Convenience function to analyze WhatsApp voice message
    
    Args:
        audio_path: Path to voice message file
        api_key: Optional API key for advanced services
    
    Returns:
        Comprehensive analysis dictionary
    """
    analyzer = VoiceAnalyzer(api_key=api_key)
    
    try:
        # Get transcription
        transcription_result = analyzer.transcribe_voice_message(audio_path)
        
        # Get voice emotion
        emotion_result = analyzer.analyze_voice_emotion(audio_path)
        
        return {
            'status': 'success',
            'transcription': transcription_result['transcription'],
            'audio_features': transcription_result['audio_features'],
            'voice_emotion': emotion_result,
            'transcription_confidence': transcription_result['confidence']
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
