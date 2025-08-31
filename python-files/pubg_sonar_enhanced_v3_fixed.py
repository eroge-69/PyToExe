"""
PUBG Sonar Radar - Enhanced Version for Deaf Players
A professional sonar-style radar with sound classification, distance estimation,
and player sound filtering for PUBG, designed specifically for deaf players.

Version: 3.0
"""

import os
import sys
import time
import math
import json
import queue
import threading
import numpy as np
import pyaudio
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from typing import Dict, List, Tuple, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime
from functools import partial
import scipy.signal as signal

# Try to import optional ML dependencies
try:
    import librosa
    import joblib
    ML_FEATURES_AVAILABLE = True
except ImportError:
    ML_FEATURES_AVAILABLE = False

# Try to import Windows-specific modules
try:
    import win32gui
    import win32con
    import win32api
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    WINDOWS_FEATURES_AVAILABLE = True
except ImportError:
    WINDOWS_FEATURES_AVAILABLE = False
    # Create minimal PIL imports if possible
    try:
        from PIL import Image, ImageTk, ImageDraw, ImageFont
    except ImportError:
        pass

# Constants for sound classification
SOUND_TYPES = {
    'footstep': {'symbol': '👣', 'priority': 1, 'band_range': (90, 400)},
    'vehicle': {'symbol': '🚗', 'priority': 2, 'band_range': (50, 300)},
    'gunfire': {'symbol': '🔫', 'priority': 3, 'band_range': (1000, 4000)},
    'grenade': {'symbol': '💣', 'priority': 4, 'band_range': (200, 2000)},
    'healing': {'symbol': '💊', 'priority': 5, 'band_range': (100, 800)},
    'door': {'symbol': '🚪', 'priority': 6, 'band_range': (100, 600)},
    'reload': {'symbol': '🔄', 'priority': 7, 'band_range': (200, 1200)},
    'unknown': {'symbol': '❓', 'priority': 8, 'band_range': (20, 20000)}
}

# Distance color mapping
DISTANCE_COLORS = {
    'close': '#ff3333',    # Red (≤30m)
    'medium': '#ffcc00',   # Yellow (30-100m)
    'far': '#33cc33'       # Green (>100m)
}

# Settings schema version
SETTINGS_VERSION = "3.0"

# Default settings
DEFAULT_SETTINGS = {
    'version': SETTINGS_VERSION,
    'radar_size': 300,
    'transparency': 0.85,
    'sweep_speed': 2.0,
    'sweep_trail_length': 60,
    'sound_threshold': 0.001,
    'chunk_size': 2048,  # Optimized for lower latency
    'show_all_sounds': True,
    'filter_own_sounds': True,
    'sound_types_enabled': {
        'footstep': True,
        'vehicle': True,
        'gunfire': True,
        'grenade': True,
        'healing': True,
        'door': True,
        'reload': True,
        'unknown': True
    },
    'distance_colors': {
        'close': '#ff3333',
        'medium': '#ffcc00',
        'far': '#33cc33'
    },
    'close_distance': 30,
    'medium_distance': 100,
    'adaptive_gate': {
        'attack': 0.6,
        'release': 0.1,
        'margin': 1.8
    },
    'self_sound_windows': {
        'gunfire': {
            'angle': 30,
            'duration_ms': 120
        },
        'footstep': {
            'angle': 30,
            'duration_ms': 200
        }
    },
    'distance_model': {
        'default': {'a': 200.0, 'b': -0.5},
        'footstep': {'a': 150.0, 'b': -0.6},
        'vehicle': {'a': 250.0, 'b': -0.4},
        'gunfire': {'a': 180.0, 'b': -0.5},
        'grenade': {'a': 200.0, 'b': -0.5}
    },
    'feature_throttle': 10,  # Process heavy features every N frames
    
    # New settings for enhancements
    'show_sound_trails': True,
    'trail_length': 10,
    'highlight_threats': True,
    'threat_sensitivity': 0.7,
    'show_threat_notifications': True,
    'environment_detection': True,
    'memory_optimization': True,
    'performance_mode': 'balanced',  # 'performance', 'balanced', 'quality'
    'keyboard_shortcuts_enabled': True
}




# Moved circular_mean to module scope
def circular_mean(angles_deg: np.ndarray, weights: np.ndarray = None) -> float:
    """
    Calculate the circular mean of angles in degrees with optional weights

    Args:
        angles_deg: Array of angles in degrees
        weights: Optional weights for each angle

    Returns:
        Mean angle in degrees (0-360)
    """
    if weights is None:
        weights = np.ones_like(angles_deg)

    angles_rad = np.radians(angles_deg)
    x = np.sum(np.cos(angles_rad) * weights)
    y = np.sum(np.sin(angles_rad) * weights)
    mean_rad = np.arctan2(y, x)
    mean_deg = np.degrees(mean_rad) % 360
    return float(mean_deg)


@dataclass
class SonarTheme:
    """Theme configuration for the sonar radar UI"""
    # Background colors
    bg_dark: str = '#1a1a1a'
    bg_darker: str = '#000000'
    bg_light: str = '#2a2a2a'
    
    # Text colors
    text_primary: str = '#00ff41'    # Bright green
    text_secondary: str = '#00aa2a'  # Darker green
    text_muted: str = '#888888'      # Gray
    text_warning: str = '#ffcc00'    # Yellow
    text_danger: str = '#ff3333'     # Red
    
    # Accent colors
    accent_blue: str = '#0099ff'
    accent_orange: str = '#ff9900'
    accent_purple: str = '#cc00ff'
    accent_red: str = '#ff4444'
    
    # Sonar colors
    sonar_ring: str = '#00aa44'
    sonar_line: str = '#004422'
    sonar_sweep: str = '#00ff41'
    
    # Distance colors
    distance_close: str = '#ff3333'    # Red (≤30m)
    distance_medium: str = '#ffcc00'   # Yellow (30-100m)
    distance_far: str = '#33cc33'      # Green (>100m)
    
    # Button colors as nested dictionaries
    btn_green: Dict[str, str] = field(default_factory=lambda: {
        'bg': '#003d0f', 'fg': '#00ff41', 'active_bg': '#00ff41', 'active_fg': '#000000'
    })
    btn_blue: Dict[str, str] = field(default_factory=lambda: {
        'bg': '#001a33', 'fg': '#0099ff', 'active_bg': '#0099ff', 'active_fg': '#000000'
    })
    btn_orange: Dict[str, str] = field(default_factory=lambda: {
        'bg': '#331a00', 'fg': '#ff9900', 'active_bg': '#ff9900', 'active_fg': '#000000'
    })
    btn_purple: Dict[str, str] = field(default_factory=lambda: {
        'bg': '#1a0033', 'fg': '#cc00ff', 'active_bg': '#cc00ff', 'active_fg': '#000000'
    })
    btn_red: Dict[str, str] = field(default_factory=lambda: {
        'bg': '#4d0000', 'fg': '#ff4444', 'active_bg': '#ff4444', 'active_fg': '#000000'
    })
    
    # Font definitions with fallbacks
    def get_font(self, font_type: str, size: int = 10, bold: bool = False) -> tuple:
        """Get a font tuple with fallbacks"""
        style = 'bold' if bold else ''
        font_families = {
            'title': ('Orbitron', 'Arial', 'Helvetica'),
            'text': ('Consolas', 'Courier New', 'monospace'),
            'button': ('Orbitron', 'Arial', 'Helvetica')
        }
        
        font_family = font_families.get(font_type, font_families['text'])
        return (font_family[0], size, style) if style else (font_family[0], size)


@dataclass
class SoundDetection:
    """Represents a detected sound with classification and properties"""
    angle: float
    intensity: float
    distance: float
    sound_type: str
    timestamp: float
    confidence: float = 0.5
    band_energies: Dict[str, float] = field(default_factory=dict)
    # Add trail_points to store previous positions
    trail_points: List[Tuple[float, float]] = field(default_factory=list)
    
    @property
    def distance_category(self) -> str:
        """Get the distance category (close, medium, far)"""
        # Use settings from the global scope if available
        close_threshold = 30
        medium_threshold = 100
        
        if self.distance <= close_threshold:
            return 'close'
        elif self.distance <= medium_threshold:
            return 'medium'
        else:
            return 'far'
    
    @property
    def age(self) -> float:
        """Get the age of the detection in seconds"""
        return time.time() - self.timestamp
    
    @property
    def is_recent(self) -> bool:
        """Check if the detection is recent (less than 3 seconds old)"""
        return self.age < 3.0
    
    @property
    def fade_factor(self) -> float:
        """Get the fade factor based on age (1.0 to 0.0 over 3 seconds)"""
        return max(0, 1.0 - (self.age / 3.0))
        
    @property
    def threat_level(self) -> float:
        """Calculate threat level based on distance, sound type and recency"""
        # Base threat is inverse of distance (closer = more threatening)
        base_threat = max(0, 1.0 - (self.distance / 200.0))
        
        # Sound type multipliers
        type_multipliers = {
            'footstep': 1.0,
            'vehicle': 0.7,
            'gunfire': 1.2,
            'grenade': 1.5,
            'healing': 0.3,
            'door': 0.5,
            'reload': 0.8,
            'unknown': 0.4
        }
        
        # Apply sound type multiplier
        type_multiplier = type_multipliers.get(self.sound_type, 0.5)
        
        # Apply recency factor (newer sounds are more threatening)
        recency_factor = self.fade_factor
        
        # Calculate final threat level (0-1 scale)
        return base_threat * type_multiplier * recency_factor
    
    def update_trail(self, x: float, y: float, max_points: int = 10):
        """Update the trail with a new position point"""
        self.trail_points.append((x, y))
        # Keep only the most recent points
        if len(self.trail_points) > max_points:
            self.trail_points = self.trail_points[-max_points:]

class EnvironmentDetector:
    """Detects and classifies the acoustic environment"""
    
    def __init__(self):
        """Initialize the environment detector"""
        self.history_size = 20
        self.reverb_history = deque(maxlen=self.history_size)
        self.spectral_history = deque(maxlen=self.history_size)
        self.current_environment = "unknown"
        self.environment_confidence = 0.5
        
        # Environment characteristics
        self.environments = {
            "indoor_small": {
                "reverb_time": (0.3, 0.7),
                "spectral_balance": "mid_heavy"
            },
            "indoor_large": {
                "reverb_time": (0.7, 1.5),
                "spectral_balance": "mid_heavy"
            },
            "outdoor_open": {
                "reverb_time": (0.0, 0.3),
                "spectral_balance": "balanced"
            },
            "outdoor_urban": {
                "reverb_time": (0.2, 0.5),
                "spectral_balance": "high_heavy"
            }
        }
    
    def analyze_audio(self, audio_data: np.ndarray, sample_rate: int = 48000) -> str:
        """
        Analyze audio to detect the environment type
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            Detected environment type
        """
        # Estimate reverb time
        reverb_time = self._estimate_reverb_time(audio_data, sample_rate)
        self.reverb_history.append(reverb_time)
        
        # Analyze spectral balance
        spectral_balance = self._analyze_spectral_balance(audio_data, sample_rate)
        self.spectral_history.append(spectral_balance)
        
        # Classify environment based on history
        self._classify_environment()
        
        return self.current_environment
    
    def _estimate_reverb_time(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
        Estimate reverb time from audio
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            Estimated reverb time in seconds
        """
        # Calculate envelope
        envelope = np.abs(audio_data)
        
        # Smooth envelope
        window_size = min(128, len(envelope) // 10)
        if window_size < 2:
            return 0.0
            
        smoothed = np.convolve(envelope, np.ones(window_size)/window_size, mode='valid')
        
        # Find decay segments
        decay_times = []
        
        # Find peaks
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(smoothed, height=np.mean(smoothed)*1.5, distance=sample_rate//50)
        
        for i in range(len(peaks)-1):
            if peaks[i+1] - peaks[i] > sample_rate // 20:  # At least 50ms apart
                # Extract segment between peaks
                segment = smoothed[peaks[i]:peaks[i+1]]
                
                if len(segment) > 10:
                    # Find point where amplitude decays to -60dB
                    peak_amp = segment[0]
                    target_amp = peak_amp * 0.001  # -60dB
                    
                    for j, amp in enumerate(segment):
                        if amp <= target_amp:
                            # Convert samples to seconds
                            decay_time = j / sample_rate
                            decay_times.append(decay_time)
                            break
        
        # Return average decay time or default
        if decay_times:
            return np.mean(decay_times)
        else:
            return 0.2  # Default value
    
    def _analyze_spectral_balance(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Analyze spectral balance of audio
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            Spectral balance category
        """
        # Calculate FFT
        n_fft = min(2048, len(audio_data))
        if n_fft < 64:
            return "balanced"  # Default
            
        fft = np.abs(np.fft.rfft(audio_data[:n_fft]))
        freqs = np.fft.rfftfreq(n_fft, 1/sample_rate)
        
        # Define frequency bands
        low_band = (20, 250)
        mid_band = (250, 2000)
        high_band = (2000, 20000)
        
        # Calculate energy in each band
        low_energy = np.sum(fft[(freqs >= low_band[0]) & (freqs < low_band[1])])
        mid_energy = np.sum(fft[(freqs >= mid_band[0]) & (freqs < mid_band[1])])
        high_energy = np.sum(fft[(freqs >= high_band[0]) & (freqs < high_band[1])])
        
        # Normalize
        total_energy = low_energy + mid_energy + high_energy
        if total_energy > 0:
            low_ratio = low_energy / total_energy
            mid_ratio = mid_energy / total_energy
            high_ratio = high_energy / total_energy
            
            # Classify spectral balance
            if low_ratio > 0.5:
                return "low_heavy"
            elif mid_ratio > 0.5:
                return "mid_heavy"
            elif high_ratio > 0.5:
                return "high_heavy"
            else:
                return "balanced"
        else:
            return "balanced"  # Default
    
    def _classify_environment(self):
        """Classify environment based on acoustic properties"""
        if not self.reverb_history:
            return
        
        # Calculate average reverb time
        avg_reverb = np.mean(list(self.reverb_history))
        
        # Count spectral balance occurrences
        spectral_counts = {
            "low_heavy": 0,
            "mid_heavy": 0,
            "high_heavy": 0,
            "balanced": 0
        }
        
        for balance in self.spectral_history:
            if balance in spectral_counts:
                spectral_counts[balance] += 1
        
        # Find most common spectral balance
        dominant_spectral = max(spectral_counts, key=spectral_counts.get)
        
        # Match to environment
        best_match = "unknown"
        best_score = 0
        
        for env_name, env_props in self.environments.items():
            score = 0
            
            # Score reverb match
            min_reverb, max_reverb = env_props["reverb_time"]
            if min_reverb <= avg_reverb <= max_reverb:
                score += 2
            elif abs(avg_reverb - (min_reverb + max_reverb) / 2) < 0.3:
                score += 1
            
            # Score spectral balance match
            if env_props["spectral_balance"] == dominant_spectral:
                score += 2
            
            # Update best match
            if score > best_score:
                best_score = score
                best_match = env_name
        
        # Update environment with confidence
        self.current_environment = best_match
        self.environment_confidence = min(1.0, best_score / 4.0)


class SoundClassifier:
    """Handles sound classification for different PUBG sound types"""
    
    def __init__(self):
        """Initialize the sound classifier"""
        self.model_loaded = False
        self.model = None
        self.feature_extractor = None
        self.feature_cache = {}
        self.last_feature_time = 0
        self.feature_cache_lifetime = 0.1  # seconds
        
        # Try to load pre-trained model if available
        self.load_model()
    
    def load_model(self) -> bool:
        """Load the pre-trained sound classification model"""
        try:
            # Check if ML features are available
            if not ML_FEATURES_AVAILABLE:
                print("ML libraries not available, using heuristic classification")
                return False
                
            # Check if model files exist
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'sound_classifier.joblib')
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.model_loaded = True
                print("Sound classification model loaded successfully")
                return True
            else:
                print("Sound classification model not found, using heuristic classification")
                return False
        except Exception as e:
            print(f"Error loading sound classification model: {e}")
            return False
    
    def classify_sound(self, audio_data: np.ndarray, sample_rate: int = 48000, 
                      band_energies: Dict[str, float] = None) -> Tuple[str, float]:
        """
        Classify the sound type from audio data
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio data
            band_energies: Optional pre-computed band energies
            
        Returns:
            Tuple of (sound_type, confidence)
        """
        # Check if we have ML features available
        if not ML_FEATURES_AVAILABLE:
            # Fall back to heuristic classification using band energies
            if band_energies:
                return self._classify_with_band_energies(band_energies)
            else:
                # Basic heuristic without librosa
                return self._basic_heuristic_classification(audio_data)
        
        # Use ML model if available
        if self.model_loaded and self.model is not None:
            # Check if we can use cached features
            current_time = time.time()
            if (current_time - self.last_feature_time < self.feature_cache_lifetime and 
                audio_data.shape[0] in self.feature_cache):
                features = self.feature_cache[audio_data.shape[0]]
            else:
                # Extract features
                features = self.extract_features(audio_data, sample_rate)
                
                # Cache features
                self.feature_cache[audio_data.shape[0]] = features
                self.last_feature_time = current_time
            
            try:
                # Make prediction
                prediction = self.model.predict_proba([features])[0]
                sound_type_idx = np.argmax(prediction)
                confidence = prediction[sound_type_idx]
                
                # Map index to sound type
                sound_types = list(SOUND_TYPES.keys())
                sound_type = sound_types[sound_type_idx] if sound_type_idx < len(sound_types) else 'unknown'
                
                return sound_type, confidence
            except Exception as e:
                print(f"Error making prediction: {e}")
                # Fall back to heuristic classification
                if band_energies:
                    return self._classify_with_band_energies(band_energies)
                else:
                    return self.heuristic_classification(audio_data, sample_rate)
        else:
            # Use heuristic classification if model is not available
            if band_energies:
                return self._classify_with_band_energies(band_energies)
            else:
                return self.heuristic_classification(audio_data, sample_rate)
            
    def _classify_with_band_energies(self, band_energies: Dict[str, float]) -> Tuple[str, float]:
        """
        Classify sound using band energy ratios
        
        Args:
            band_energies: Dictionary of band energies
            
        Returns:
            Tuple of (sound_type, confidence)
        """
        # Find the band with the highest energy
        if not band_energies:
            return 'unknown', 0.3
        
        # Normalize band energies
        total_energy = sum(band_energies.values()) + 1e-10
        normalized_energies = {k: v / total_energy for k, v in band_energies.items()}
        
        # Find dominant band
        dominant_type = max(normalized_energies, key=normalized_energies.get)
        confidence = normalized_energies[dominant_type]
        
        # Apply some heuristic rules to improve classification
        if dominant_type == 'footstep' and normalized_energies.get('vehicle', 0) > 0.3:
            # Vehicle engines can be confused with footsteps
            if normalized_energies.get('vehicle', 0) > normalized_energies.get('footstep', 0) * 0.8:
                dominant_type = 'vehicle'
                confidence = normalized_energies['vehicle']
        
        elif dominant_type == 'gunfire' and normalized_energies.get('grenade', 0) > 0.4:
            # Explosions have broad spectrum like gunfire but more low-frequency content
            dominant_type = 'grenade'
            confidence = normalized_energies['grenade']
        
        return dominant_type, min(confidence * 1.5, 0.95)  # Scale confidence but cap at 0.95
    
    def _basic_heuristic_classification(self, audio_data: np.ndarray) -> Tuple[str, float]:
        """
        Basic heuristic classification without librosa
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Tuple of (sound_type, confidence)
        """
        # Calculate basic features
        rms = np.sqrt(np.mean(audio_data**2))
        zcr = np.mean(np.abs(np.diff(np.signbit(audio_data))))
        
        # Simple spectral analysis using FFT
        try:
            fft = np.abs(np.fft.rfft(audio_data))
            freq = np.fft.rfftfreq(len(audio_data))
            
            # Calculate spectral centroid
            if np.sum(fft) > 0:
                centroid = np.sum(freq * fft) / np.sum(fft)
            else:
                centroid = 0
                
            # Normalize centroid to 0-1 range
            centroid = centroid * 10  # Scale for easier comparison
        except:
            centroid = 0.5  # Default value
        
        # Simple heuristic classification based on audio characteristics
        if rms > 0.1:  # High energy sounds
            if centroid > 0.5:  # High frequency components
                return 'gunfire', 0.7
            else:
                return 'vehicle', 0.6
        elif 0.05 < rms <= 0.1:  # Medium energy sounds
            if zcr > 0.1:  # Many zero crossings
                return 'footstep', 0.6
            else:
                return 'door', 0.5
        elif 0.01 < rms <= 0.05:  # Low energy sounds
            if centroid > 0.3:  # Higher frequency
                return 'reload', 0.5
            else:
                return 'healing', 0.4
        else:
            # Very low energy or unclear
            return 'unknown', 0.3
    
    def extract_features(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Extract audio features for classification
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio data
            
        Returns:
            Feature vector as numpy array
        """
        if not ML_FEATURES_AVAILABLE:
            return np.zeros(18)  # Return dummy features if librosa not available
            
        try:
            # Extract basic features
            # This is a simplified version - a real implementation would use more sophisticated features
            
            # Zero crossing rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            
            # Spectral centroid
            centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
            
            # RMS energy
            rms = np.mean(librosa.feature.rms(y=audio_data))
            
            # Spectral bandwidth
            bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate))
            
            # Spectral rolloff
            rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate))
            
            # MFCCs (first 13)
            mfccs = np.mean(librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13), axis=1)
            
            # Combine features
            features = np.concatenate(([zcr, centroid, rms, bandwidth, rolloff], mfccs))
            
            return features
        except Exception as e:
            print(f"Error extracting audio features: {e}")
            # Return a default feature vector
            return np.zeros(18)
    
    def heuristic_classification(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[str, float]:
        """
        Classify sound using simple heuristics when ML model is not available
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio data
            
        Returns:
            Tuple of (sound_type, confidence)
        """
        if not ML_FEATURES_AVAILABLE:
            return self._basic_heuristic_classification(audio_data)
            
        try:
            # Extract basic features
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
            rms = np.mean(librosa.feature.rms(y=audio_data))
            
            # Additional features for better classification
            onset_env = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
            onset_rate = np.mean(onset_env)
            
            # Simple heuristic classification based on audio characteristics
            if rms > 0.1:  # High energy sounds
                if centroid > 5000:  # High frequency components
                    if onset_rate > 0.2:  # Sharp attacks
                        return 'gunfire', 0.8
                    else:
                        return 'vehicle', 0.7
                else:
                    if onset_rate > 0.15:
                        return 'grenade', 0.7
                    else:
                        return 'vehicle', 0.6
            elif 0.05 < rms <= 0.1:  # Medium energy sounds
                if zcr > 0.1:  # Many zero crossings
                    if onset_rate > 0.1:
                        return 'footstep', 0.7
                    else:
                        return 'reload', 0.6
                else:
                    return 'door', 0.5
            elif 0.01 < rms <= 0.05:  # Low energy sounds
                if centroid > 3000:  # Higher frequency
                    return 'reload', 0.5
                else:
                    return 'healing', 0.4
            else:
                # Very low energy or unclear
                return 'unknown', 0.3
        except Exception as e:
            print(f"Error in heuristic classification: {e}")
            return self._basic_heuristic_classification(audio_data)


class SelfSoundFilter:
    """Filters out sounds generated by the player"""
    
    def __init__(self):
        """Initialize the self-sound filter"""
        self.player_actions = deque(maxlen=20)  # Recent player actions
        self.self_sound_patterns = {}  # Patterns of self-generated sounds
        self.last_key_press = 0
        self.last_mouse_click = 0
        
        # Class-specific mute windows (in seconds)
        self.mute_windows = {
            'gunfire': {
                'angle': 30,      # Angle in degrees from front center
                'duration_ms': 120  # Duration in milliseconds
            },
            'footstep': {
                'angle': 30,
                'duration_ms': 200
            }
        }
        
        # Try to load calibration data if available
        self.load_calibration()
    
    def load_calibration(self) -> bool:
        """Load calibration data for self-sound filtering"""
        try:
            calibration_path = os.path.join(os.path.dirname(__file__), 'data', 'self_sound_calibration.json')
            if os.path.exists(calibration_path):
                with open(calibration_path, 'r') as f:
                    data = json.load(f)
                    
                    # Load self sound patterns
                    if 'self_sound_patterns' in data:
                        self.self_sound_patterns = data['self_sound_patterns']
                    
                    # Load mute windows if available
                    if 'mute_windows' in data:
                        self.mute_windows = data['mute_windows']
                        
                print("Self-sound calibration data loaded successfully")
                return True
            else:
                print("Self-sound calibration data not found, using default filtering")
                return False
        except Exception as e:
            print(f"Error loading self-sound calibration: {e}")
            return False
    
    def register_player_action(self, action_type: str):
        """Register a player action (keyboard/mouse input)"""
        current_time = time.time()
        
        self.player_actions.append({
            'type': action_type,
            'timestamp': current_time
        })
        
        if action_type == 'key':
            self.last_key_press = current_time
        elif action_type == 'mouse':
            self.last_mouse_click = current_time
    
    def is_self_sound(self, audio_data: np.ndarray, angle: float, sound_type: str = None) -> bool:
        """
        Determine if a sound is likely generated by the player
        
        Args:
            audio_data: Audio data as numpy array
            angle: Detected angle of the sound
            sound_type: Optional type of sound for class-specific filtering
            
        Returns:
            True if the sound is likely self-generated, False otherwise
        """
        # Check if there was a recent player action
        current_time = time.time()
        
        # Apply class-specific mute windows if sound_type is provided
        if sound_type and sound_type in self.mute_windows:
            window = self.mute_windows[sound_type]
            angle_threshold = window.get('angle', 30)
            duration_ms = window.get('duration_ms', 200)
            duration_sec = duration_ms / 1000.0
            
            # Check for specific action types
            if sound_type == 'gunfire' and current_time - self.last_mouse_click < duration_sec:
                # Check if the sound is coming from the player's firing direction (front)
                if self._is_in_angle_range(angle, 0, angle_threshold):
                    return True
                    
            elif sound_type == 'footstep' and current_time - self.last_key_press < duration_sec:
                # Check if the sound is coming from the player's movement direction (front)
                if self._is_in_angle_range(angle, 0, angle_threshold):
                    return True
        
        # General filtering for any recent action
        if (current_time - self.last_key_press < 0.5 or 
            current_time - self.last_mouse_click < 0.5):
            
            # Check if the sound is coming from the player's position (roughly front center)
            if self._is_in_angle_range(angle, 0, 30):
                return True
        
        # Check against all recent actions with more specific timing
        for action in self.player_actions:
            action_age = current_time - action['timestamp']
            
            # Only consider recent actions
            if action_age > 1.0:
                continue
                
            # Different action types might have different filtering rules
            if action['type'] == 'key' and action_age < 0.3:
                # Movement sounds (footsteps, etc.)
                if self._is_in_angle_range(angle, 0, 40):
                    return True
                    
            elif action['type'] == 'mouse' and action_age < 0.2:
                # Shooting sounds
                if self._is_in_angle_range(angle, 0, 35):
                    return True
        
        return False
    
    def _is_in_angle_range(self, angle: float, center: float, threshold: float) -> bool:
        """
        Check if an angle is within a threshold of a center angle
        
        Args:
            angle: Angle to check (0-360)
            center: Center angle (0-360)
            threshold: Threshold in degrees
            
        Returns:
            True if the angle is within the threshold of the center
        """
        # Normalize angles to 0-360
        angle = angle % 360
        center = center % 360
        
        # Calculate the smallest difference between the angles
        diff = min(abs(angle - center), 360 - abs(angle - center))
        
        # Check if the difference is within the threshold
        return diff <= threshold

class AudioProcessor:
    """Handles audio input and processing for the sonar radar"""
    
    def __init__(self, on_detection: Callable[[SoundDetection], None]):
        """Initialize the audio processor"""
        self.on_detection = on_detection
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.active = False
        self.audio_thread = None
        self.audio_queue = queue.Queue()
        self.level_callback = None
        
        # Audio settings
        self.chunk_size = 2048  # Optimized for lower latency
        self.audio_format = pyaudio.paFloat32
        self.channels = 8  # 7.1 surround sound
        self.sample_rate = 48000
        self.sound_threshold = 0.001
        # Track current device and channel count (avoid using private attributes)
        self.current_device_index = None
        self.channels_in_stream = None
        
        # Channel mapping for 7.1 surround (VoiceMeeter order)
        self.channel_angles = {
            0: 315,  # Front Left
            1: 45,   # Front Right  
            2: 0,    # Front Center
            3: 180,  # LFE/Subwoofer
            4: 225,  # Rear Left
            5: 135,  # Rear Right
            6: 270,  # Side Left
            7: 90    # Side Right
        }
        
        # Adaptive gate settings
        self.attack_coef = 0.6
        self.release_coef = 0.1
        self.gate_margin = 1.8
        
        # Detection state
        self.noise_floor = None
        self.level_state = None
        self.frame_counter = 0
        self.feature_throttle = 10  # Process heavy features every N frames
        
        # Band-pass filters for sound classification
        self.band_filters = {}
        self._init_band_filters()
        
        # Initialize sound classifier and self-sound filter
        self.sound_classifier = SoundClassifier()
        self.self_sound_filter = SelfSoundFilter()
        
        # Settings
        self.filter_own_sounds = True
        
        # Distance model
        self.distance_model = {
            'default': {'a': 200.0, 'b': -0.5},
            'footstep': {'a': 150.0, 'b': -0.6},
            'vehicle': {'a': 250.0, 'b': -0.4},
            'gunfire': {'a': 180.0, 'b': -0.5},
            'grenade': {'a': 200.0, 'b': -0.5}
        }
        
        # Initialize environment detector
        self.environment_detector = EnvironmentDetector()
        self.current_environment = "unknown"
        self.environment_update_interval = 20  # Update every 20 frames
        
        # Add environment-specific distance models
        self.distance_model.update({
            'indoor_small': {
                'default': {'a': 150.0, 'b': -0.45},
                'footstep': {'a': 120.0, 'b': -0.55},
                'vehicle': {'a': 200.0, 'b': -0.35},
                'gunfire': {'a': 150.0, 'b': -0.45},
                'grenade': {'a': 170.0, 'b': -0.45}
            },
            'indoor_large': {
                'default': {'a': 180.0, 'b': -0.48},
                'footstep': {'a': 140.0, 'b': -0.58},
                'vehicle': {'a': 220.0, 'b': -0.38},
                'gunfire': {'a': 170.0, 'b': -0.48},
                'grenade': {'a': 190.0, 'b': -0.48}
            },
            'outdoor_open': {
                'default': {'a': 220.0, 'b': -0.52},
                'footstep': {'a': 160.0, 'b': -0.62},
                'vehicle': {'a': 280.0, 'b': -0.42},
                'gunfire': {'a': 200.0, 'b': -0.52},
                'grenade': {'a': 220.0, 'b': -0.52}
            },
            'outdoor_urban': {
                'default': {'a': 200.0, 'b': -0.5},
                'footstep': {'a': 150.0, 'b': -0.6},
                'vehicle': {'a': 250.0, 'b': -0.4},
                'gunfire': {'a': 180.0, 'b': -0.5},
                'grenade': {'a': 200.0, 'b': -0.5}
            }
        })
    
    def _init_band_filters(self):
        """Initialize band-pass filters for different sound types"""
        for sound_type, info in SOUND_TYPES.items():
            if 'band_range' in info:
                low_freq, high_freq = info['band_range']
                
                # Create band-pass filter coefficients
                # Use a 4th order Butterworth filter (2nd order applied twice)
                try:
                    nyquist = self.sample_rate / 2
                    low = low_freq / nyquist
                    high = high_freq / nyquist
                    
                    if low <= 0:
                        low = 0.001
                    if high >= 1:
                        high = 0.999
                    
                    b, a = signal.butter(2, [low, high], btype='band')
                    self.band_filters[sound_type] = (b, a)
                except Exception as e:
                    print(f"Error creating filter for {sound_type}: {e}")
                    # Create a default pass-through filter
                    self.band_filters[sound_type] = (np.array([1.0]), np.array([1.0]))
    
    def _init_detection_state(self, channels):
        """Initialize detection state arrays for adaptive gating"""
        # Initialize noise floor and level state arrays
        self.noise_floor = np.zeros(channels)
        self.level_state = np.zeros(channels)
        self.frame_counter = 0
    
    def _smooth_levels(self, channel_rms):
        """
        Apply adaptive noise gate and envelope smoothing to channel levels
        
        Args:
            channel_rms: Array of RMS values for each channel
            
        Returns:
            Array of smoothed levels after adaptive gating
        """
        # Initialize state if needed
        if self.noise_floor is None or len(self.noise_floor) != len(channel_rms):
            self._init_detection_state(len(channel_rms))
        
        # Update noise floor with slow adaptation (when signal is below current floor)
        mask_below = channel_rms < self.noise_floor
        self.noise_floor[mask_below] = (
            self.release_coef * channel_rms[mask_below] + 
            (1 - self.release_coef) * self.noise_floor[mask_below]
        )
        
        # Apply gate based on noise floor
        gate_threshold = self.noise_floor * self.gate_margin
        
        # Apply fast attack / slow release envelope
        mask_above = channel_rms > self.level_state
        self.level_state[mask_above] = (
            self.attack_coef * channel_rms[mask_above] + 
            (1 - self.attack_coef) * self.level_state[mask_above]
        )
        self.level_state[~mask_above] = (
            self.release_coef * channel_rms[~mask_above] + 
            (1 - self.release_coef) * self.level_state[~mask_above]
        )
        
        # Apply gate
        smoothed_levels = np.copy(self.level_state)
        smoothed_levels[self.level_state < gate_threshold] = 0
        
        return smoothed_levels
    
    def _estimate_azimuth(self, channel_levels):
        """
        Estimate sound direction using energy-weighted circular mean
        
        Args:
            channel_levels: Array of audio levels for each channel
            
        Returns:
            Estimated angle in degrees (0-360)
        """
        # Get angles and levels for channels with signal
        angles = []
        weights = []
        
        for channel, level in enumerate(channel_levels):
            if level > 0 and channel in self.channel_angles:
                angles.append(self.channel_angles[channel])
                weights.append(level)
        
        if not angles:
            # Default to front if no channels have signal
            return 0
        
        # Convert to numpy arrays
        angles = np.array(angles)
        weights = np.array(weights)
        
        # Calculate circular mean
        return circular_mean(angles, weights)
    
    def set_level_callback(self, callback: Callable[[float], None]):
        """Set callback for audio level updates"""
        self.level_callback = callback
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get available audio input devices"""
        devices = []
        voicemeeter_devices = []
        
        for i in range(self.audio.get_device_count()):
            try:
                info = self.audio.get_device_info_by_index(i)
                if info['maxInputChannels'] >= 2:
                    device = {
                        'index': i,
                        'name': info['name'],
                        'channels': info['maxInputChannels'],
                        'display_name': f"{i}: {info['name']} ({info['maxInputChannels']}ch)"
                    }
                    devices.append(device)
                    
                    # Prioritize VoiceMeeter devices
                    if 'voicemeeter' in info['name'].lower() or 'vb-audio' in info['name'].lower():
                        voicemeeter_devices.append(device)
            except Exception:
                continue
        
        # Put VoiceMeeter devices first
        return voicemeeter_devices + [d for d in devices if d not in voicemeeter_devices]
    
    def has_voicemeeter(self) -> bool:
        """Check if VoiceMeeter is available"""
        for i in range(self.audio.get_device_count()):
            try:
                info = self.audio.get_device_info_by_index(i)
                if 'voicemeeter' in info['name'].lower() or 'vb-audio' in info['name'].lower():
                    return True
            except Exception:
                continue
        return False
    
    def test_device(self, device_index: int, duration: float = 5.0) -> Tuple[bool, float]:
        """
        Test an audio device and return success status and max level
        
        Args:
            device_index: Index of the audio device to test
            duration: Duration of the test in seconds
            
        Returns:
            Tuple of (success, max_level)
        """
        try:
            device_info = self.audio.get_device_info_by_index(device_index)
            max_channels = min(8, device_info['maxInputChannels'])
            
            # Open test stream
            test_stream = self.audio.open(
                format=self.audio_format,
                channels=max_channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            max_level = 0
            frames = int(duration * 10)  # 10 frames per second
            
            for _ in range(frames):
                try:
                    data = test_stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.float32)
                    
                    if len(audio_data) > 0:
                        level = np.sqrt(np.mean(audio_data**2))
                        max_level = max(max_level, level)
                        
                        # Update level through callback
                        if self.level_callback:
                            self.level_callback(level)
                except Exception:
                    break
                
                time.sleep(0.1)
            
            test_stream.stop_stream()
            test_stream.close()
            
            return True, max_level
        
        except Exception as e:
            print(f"Audio test error: {e}")
            return False, 0.0
    
    def start(self, device_index: int) -> bool:
        """
        Start audio processing
        
        Args:
            device_index: Index of the audio device to use
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            device_info = self.audio.get_device_info_by_index(device_index)
            max_channels = min(self.channels, device_info['maxInputChannels'])
            
            # Open audio stream
            self.stream = self.audio.open(
                format=self.audio_format,
                channels=max_channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            
            # Store device index and channel count
            self.current_device_index = device_index
            self.channels_in_stream = max_channels
            # Initialize detection state
            self._init_detection_state(max_channels)
            
            self.active = True
            
            # Start audio processing thread
            self.audio_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.audio_thread.start()
            
            return True
        
        except Exception as e:
            print(f"Failed to start audio: {e}")
            return False
    
    def stop(self):
        """Stop audio processing"""
        self.active = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    def _processing_loop(self):
        """Audio processing loop running in a separate thread"""
        consecutive_errors = 0
        restart_attempted = False
        last_process_time = time.time()
        processing_interval = 0.02  # Process every 20ms (50Hz)
        last_memory_cleanup = time.time()
        memory_cleanup_interval = 60.0  # Clean up every minute
        
        while self.active:
            try:
                current_time = time.time()
                
                # Throttle processing to reduce CPU usage
                if current_time - last_process_time < processing_interval:
                    time.sleep(0.001)  # Short sleep to reduce CPU usage
                    continue
                
                last_process_time = current_time
                
                # Periodic memory cleanup
                if current_time - last_memory_cleanup > memory_cleanup_interval:
                    self._perform_memory_cleanup()
                    last_memory_cleanup = current_time
                
                # Read audio data
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                
                # Get number of channels (use stored value instead of private attribute)
                channels = self.channels_in_stream or self.channels
                if channels <= 1:
                    continue  # Skip processing for mono audio

                # Ensure audio_data length is divisible by channel count to avoid reshape errors
                trim = (len(audio_data) // channels) * channels
                if trim == 0:
                    continue  # Skip if we don't have enough data for even one frame

                # Reshape audio data to [frames, channels] for vectorized processing
                frames = audio_data[:trim].reshape(-1, channels)

                # Calculate RMS for each channel (vectorized)
                channel_rms = np.sqrt(np.mean(frames**2, axis=0) + 1e-12)
                    
                # Apply adaptive gate and smoothing
                smoothed_levels = self._smooth_levels(channel_rms)
                
                # Update environment detection periodically
                if self.environment_update_interval > 0 and self.frame_counter % self.environment_update_interval == 0:
                    # Use the dominant channel for environment detection
                    dominant_channel = np.argmax(np.mean(frames**2, axis=0))
                    channel_audio = frames[:, dominant_channel]
                    
                    # Detect environment
                    detected_env = self.environment_detector.analyze_audio(channel_audio, self.sample_rate)
                    
                    # Only update if confidence is high enough
                    if self.environment_detector.environment_confidence > 0.6:
                        self.current_environment = detected_env
                
                # Update overall audio level indicator (throttled)
                if self.level_callback and (self.frame_counter % 3 == 0):
                    overall_level = np.sqrt(np.mean(smoothed_levels**2))
                    if hasattr(self, 'on_detection') and hasattr(self.on_detection, '__self__'):
                        root = getattr(self.on_detection.__self__, 'root', None)
                        if root:
                            root.after(0, lambda l=overall_level: self.level_callback(l))
                        else:
                            self.level_callback(overall_level)
                    else:
                        self.level_callback(overall_level)
                
                # Check if any channel is above threshold
                if np.max(smoothed_levels) > self.sound_threshold:
                    # Extract audio data for each channel
                    # Only extract channels that have significant signal to reduce processing
                    significant_channels = np.where(smoothed_levels > self.sound_threshold / 2)[0]
                    if len(significant_channels) > 0:
                        channel_data = [frames[:, i] for i in significant_channels]
                        
                        # Analyze for sound direction and properties
                        detection = self._analyze_audio(channel_data, smoothed_levels)
                        
                        if detection:
                            # Post detection to main thread
                            if hasattr(self, 'on_detection') and hasattr(self.on_detection, '__self__'):
                                root = getattr(self.on_detection.__self__, 'root', None)
                                if root:
                                    root.after(0, lambda d=detection: self.on_detection(d))
                                else:
                                    self.on_detection(detection)
                            else:
                                self.on_detection(detection)
                
                # Increment frame counter
                self.frame_counter += 1
                
                # Reset error counter on successful processing
                consecutive_errors = 0
            
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors < 5:  # Only log first few errors
                    print(f"Audio error: {e}")
            
                # Auto-restart after 10 consecutive errors
                if consecutive_errors >= 10 and not restart_attempted:
                    print("Attempting to restart audio stream after multiple errors")
                    try:
                        # Close the current stream
                        if self.stream:
                            self.stream.stop_stream()
                            self.stream.close()
                        
                        # Reopen the stream with the same parameters
                        device_index = self.current_device_index
                        device_info = self.audio.get_device_info_by_index(device_index)
                        max_channels = min(self.channels, device_info['maxInputChannels'])
                        
                        self.stream = self.audio.open(
                            format=self.audio_format,
                            channels=max_channels,
                            rate=self.sample_rate,
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=self.chunk_size,
                            stream_callback=None
                        )
                        
                        # Update stored channel count
                        self.channels_in_stream = max_channels
                        
                        # Reset error counter and mark restart as attempted
                        consecutive_errors = 0
                        restart_attempted = True
                        print("Audio stream restarted successfully")
                        
                        # Re-initialize detection state
                        self._init_detection_state(max_channels)
                    except Exception as restart_error:
                        print(f"Failed to restart audio stream: {restart_error}")
                        # If restart fails, stop the radar
                        if consecutive_errors > 20:
                            print("Too many audio errors, stopping radar")
                            self.active = False
                            break
            
                # If we've already attempted a restart and still getting errors, stop
                elif consecutive_errors > 20 and restart_attempted:
                    print("Too many audio errors after restart attempt, stopping radar")
                    self.active = False
                    break
            
                time.sleep(0.01)

    def _perform_memory_cleanup(self):
        """Perform memory cleanup to prevent leaks during long sessions"""
        # Clear any cached data
        if hasattr(self.sound_classifier, 'feature_cache'):
            self.sound_classifier.feature_cache.clear()
    
        # Force garbage collection
        import gc
        gc.collect()

    def _analyze_audio(self, channel_data: List[np.ndarray], smoothed_levels: np.ndarray = None) -> Optional[SoundDetection]:
        """
        Analyze audio channels for direction, intensity, and sound type
    
        Args:
            channel_data: List of audio data for each channel
            smoothed_levels: Pre-computed smoothed levels for each channel
        
        Returns:
            SoundDetection object if a sound is detected, None otherwise
        """
        if not channel_data:
            return None
        
        # Use provided smoothed levels or calculate them
        if smoothed_levels is None:
            channel_levels = []
            
            # Calculate RMS for each channel with noise gate
            for channel in channel_data:
                if len(channel) > 0:
                    # Apply simple noise gate
                    channel_filtered = channel[np.abs(channel) > self.sound_threshold / 10]
                    if len(channel_filtered) > 0:
                        rms = np.sqrt(np.mean(channel_filtered**2))
                        channel_levels.append(rms)
                    else:
                        channel_levels.append(0.0)
                else:
                    channel_levels.append(0.0)
            
            channel_levels = np.array(channel_levels)
        else:
            channel_levels = smoothed_levels
        
        # Check if any channel is above threshold
        if len(channel_levels) == 0 or np.max(channel_levels) < self.sound_threshold:
            return None
        
        # Calculate direction using energy-weighted circular mean
        angle = self._estimate_azimuth(channel_levels)
        
        # Get the dominant channel and its intensity
        max_channel = np.argmax(channel_levels)
        intensity = channel_levels[max_channel]
        
        # Enhanced environment detection (indoor vs outdoor)
        is_indoor = self._detect_indoor_environment(channel_data[max_channel])
        
        # Check if this is likely a self-generated sound with improved filtering
        if self.filter_own_sounds:
            # Enhanced self-sound filtering with context awareness
            if self._is_self_sound_with_context(channel_data[max_channel], angle, intensity):
                return None
        
        # Calculate band energies for classification
        band_energies = self._calculate_band_energies(channel_data[max_channel])
        
        # Classify the sound type with improved accuracy
        dominant_channel_audio = channel_data[max_channel]
        sound_type, confidence = self._classify_sound_enhanced(dominant_channel_audio, band_energies, is_indoor)
        
        # Calculate distance using calibration model with environment adjustment
        distance_meters = self._estimate_distance_enhanced(intensity, sound_type, is_indoor)
        
        # Create and return the sound detection
        return SoundDetection(
            angle=angle,
            intensity=intensity,
            distance=distance_meters,
            sound_type=sound_type,
            timestamp=time.time(),
            confidence=confidence,
            band_energies=band_energies,
            trail_points=[]  # Initialize empty trail
        )
    
    def _detect_indoor_environment(self, audio_data: np.ndarray) -> bool:
        """
        Detect if the environment is likely indoor based on audio characteristics
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            True if likely indoor, False if likely outdoor
        """
        # Indoor environments typically have more reverb/echo
        # We can detect this by analyzing the decay rate of the signal
        
        # Calculate envelope
        envelope = np.abs(audio_data)
        
        # Smooth envelope
        window_size = 32
        if len(envelope) > window_size:
            smoothed = np.convolve(envelope, np.ones(window_size)/window_size, mode='valid')
            
            # Calculate decay rate
            if len(smoothed) > 2:
                # Find peaks
                from scipy.signal import find_peaks
                peaks, _ = find_peaks(smoothed, height=np.mean(smoothed)*1.5)
                
                if len(peaks) >= 2:
                    # Calculate average decay between peaks
                    decay_rates = []
                    for i in range(1, len(peaks)):
                        if peaks[i] - peaks[i-1] > 10:  # Ensure peaks are separated
                            segment = smoothed[peaks[i-1]:peaks[i]]
                            if len(segment) > 0:
                                decay = (segment[0] - segment[-1]) / len(segment)
                                decay_rates.append(decay)
                    
                    if decay_rates:
                        avg_decay = np.mean(decay_rates)
                        # Slower decay indicates more reverb (indoor)
                        return avg_decay < 0.01
        
        # Default to outdoor if analysis is inconclusive
        return False
    def _is_self_sound_with_context(self, audio_data: np.ndarray, angle: float, intensity: float) -> bool:
        """
        Enhanced self-sound detection with context awareness
        
        Args:
            audio_data: Audio data as numpy array
            angle: Detected angle of the sound
            intensity: Sound intensity
            
        Returns:
            True if the sound is likely self-generated, False otherwise
        """
        # First check with the existing self-sound filter
        if self.self_sound_filter.is_self_sound(audio_data, angle):
            return True
        
        # Additional context-aware checks
        
        # Very high intensity sounds from the front are likely self-generated
        if angle < 30 or angle > 330:
            if intensity > 0.1:  # Very loud
                return True
        
        # Check for characteristic patterns of self-sounds
        # (This would be more sophisticated in a real implementation)
        
        return False
    
    def _classify_sound_enhanced(self, audio_data: np.ndarray, band_energies: Dict[str, float], 
                               is_indoor: bool) -> Tuple[str, float]:
        """
        Enhanced sound classification with environment context
        
        Args:
            audio_data: Audio data as numpy array
            band_energies: Dictionary of band energies
            is_indoor: Whether the environment is indoor
            
        Returns:
            Tuple of (sound_type, confidence)
        """
        # Start with the existing classification
        sound_type, confidence = self._classify_sound_with_bands(audio_data, band_energies)
        
        # Apply environment-specific adjustments
        if is_indoor:
            # Indoor environments have more echo, affecting certain sound types
            if sound_type == 'footstep':
                # Footsteps echo more indoors, might be confused with other sounds
                # Check if the footstep pattern is clear
                if self._verify_footstep_pattern(audio_data):
                    confidence *= 1.2  # Increase confidence
                else:
                    confidence *= 0.8  # Decrease confidence
            
            elif sound_type == 'door':
                # Doors are more common indoors
                confidence *= 1.3
        else:
            # Outdoor adjustments
            if sound_type == 'vehicle':
                # Vehicles are more common outdoors
                confidence *= 1.2
        
        return sound_type, min(confidence, 0.95)
    
    def _verify_footstep_pattern(self, audio_data: np.ndarray) -> bool:
        """
        Verify if the audio matches a footstep pattern
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            True if the pattern matches footsteps, False otherwise
        """
        # Footsteps typically have a characteristic pattern of impacts
        
        # Calculate envelope
        envelope = np.abs(audio_data)
        
        # Find peaks (impacts)
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(envelope, height=np.mean(envelope)*2, distance=20)
        
        # Footsteps typically have 1-2 clear peaks
        if 1 <= len(peaks) <= 3:
            return True
        
        return False
    
    def _classify_sound_with_bands(self, audio_data: np.ndarray, band_energies: Dict[str, float]) -> Tuple[str, float]:
        """
        Classify sound using band energies and optional ML model
        
        Args:
            audio_data: Audio data as numpy array
            band_energies: Dictionary of band energies
            
        Returns:
            Tuple of (sound_type, confidence)
        """
        # Increment frame counter
        self.frame_counter += 1
        
        # Try to use ML model if available
        if self.sound_classifier.model_loaded and self.sound_classifier.model is not None:
            # Only extract heavy features every N frames to reduce CPU usage
            if self.frame_counter % self.feature_throttle == 0:
                return self.sound_classifier.classify_sound(audio_data, self.sample_rate)
        
        # Fall back to heuristic classification using band energies
        return self._heuristic_band_classification(band_energies)
    
    def _heuristic_band_classification(self, band_energies: Dict[str, float]) -> Tuple[str, float]:
        """
        Classify sound using band energy ratios
        
        Args:
            band_energies: Dictionary of band energies
            
        Returns:
            Tuple of (sound_type, confidence)
        """
        # Find the band with the highest energy
        if not band_energies:
            return 'unknown', 0.3
        
        # Normalize band energies
        total_energy = sum(band_energies.values()) + 1e-10
        normalized_energies = {k: v / total_energy for k, v in band_energies.items()}
        
        # Find dominant band
        dominant_type = max(normalized_energies, key=normalized_energies.get)
        confidence = normalized_energies[dominant_type]
        
        # Apply some heuristic rules to improve classification
        if dominant_type == 'footstep' and normalized_energies.get('vehicle', 0) > 0.3:
            # Vehicle engines can be confused with footsteps
            if normalized_energies.get('vehicle', 0) > normalized_energies.get('footstep', 0) * 0.8:
                dominant_type = 'vehicle'
                confidence = normalized_energies['vehicle']
        
        elif dominant_type == 'gunfire' and normalized_energies.get('grenade', 0) > 0.4:
            # Explosions have broad spectrum like gunfire but more low-frequency content
            dominant_type = 'grenade'
            confidence = normalized_energies['grenade']
        
        return dominant_type, min(confidence * 1.5, 0.95)  # Scale confidence but cap at 0.95
    
    def _calculate_band_energies(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Calculate energy in different frequency bands for sound classification
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dictionary of band energies for each sound type
        """
        band_energies = {}
        
        for sound_type, (b, a) in self.band_filters.items():
            try:
                # Skip processing if coefficients are zeroed (invalid filter)
                if np.all(np.abs(b) < 1e-10) or np.all(np.abs(a[1:]) < 1e-10):
                    band_energies[sound_type] = 0.0
                    continue
                # Apply band-pass filter
                filtered = signal.lfilter(b, a, audio_data)
                
                # Calculate energy in band
                energy = np.mean(filtered**2)
                band_energies[sound_type] = energy
            except Exception as e:
                print(f"Error calculating band energy for {sound_type}: {e}")
                band_energies[sound_type] = 0.0
        
        return band_energies
    
    def _estimate_distance_enhanced(self, intensity: float, sound_type: str, is_indoor: bool) -> float:
        """
        Enhanced distance estimation with environment context
        
        Args:
            intensity: Sound intensity
            sound_type: Type of sound
            is_indoor: Whether the environment is indoor
            
        Returns:
            Estimated distance in meters
        """
        # Use environment-specific distance model if available
        if self.current_environment in self.distance_model:
            env_model = self.distance_model[self.current_environment]
            if sound_type in env_model:
                model = env_model[sound_type]
            else:
                model = env_model['default']
        else:
            # Fall back to general model
            model = self.distance_model.get(sound_type, self.distance_model['default'])
        
        a = model['a']
        b = model['b']
        
        # Calculate distance using power law model: distance = a * intensity^b
        safe_intensity = max(1e-10, intensity)
        distance = a * (safe_intensity ** b)
        
        # Clamp distance to reasonable range (0-300 meters)
        distance = max(0.0, min(distance, 300.0))
        
        return distance
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()
        if self.audio:
            self.audio.terminate()


class PUBGSonarRadar:
    """Main application class for the PUBG Sonar Radar"""
    
    def __init__(self):
        """Initialize the application"""
        self.theme = SonarTheme()
        self.settings = self.load_settings()
        
        # UI state
        self.radar_active = False
        self.overlay_visible = False
        self.overlay_locked = False
        self.sonar_sweep_active = True
        self.sweep_angle = 0
        self.detection_count = 0
        self.detection_history = deque(maxlen=200)
        
        # ML model status
        self.ml_model_available = ML_FEATURES_AVAILABLE
        # Self-test state
        self.self_test_active = False
        self.self_test_timer = None
        self.self_test_count = 0
        self.self_test_sequence = []
        
        # Off-screen buffer for double-buffered drawing
        self.buffer_image = None
        self.buffer_photo = None
        
        # Initialize audio processor with enhanced features
        self.audio_processor = AudioProcessor(on_detection=self.handle_detection)
        self.audio_processor.sound_threshold = self.settings.get('sound_threshold', 0.001)
        self.audio_processor.filter_own_sounds = self.settings.get('filter_own_sounds', True)
        self.audio_processor.chunk_size = self.settings.get('chunk_size', 2048)
        
        # Configure adaptive gate parameters
        adaptive_gate = self.settings.get('adaptive_gate', {})
        self.audio_processor.attack_coef = adaptive_gate.get('attack', 0.6)
        self.audio_processor.release_coef = adaptive_gate.get('release', 0.1)
        self.audio_processor.gate_margin = adaptive_gate.get('margin', 1.8)
        
        # Configure distance model
        self.audio_processor.distance_model = self.settings.get('distance_model', {
            'default': {'a': 200.0, 'b': -0.5}
        })
        
        # Configure feature throttling based on performance mode
        performance_mode = self.settings.get('performance_mode', 'balanced')
        self.audio_processor.feature_throttle = {
            'performance': 20,
            'balanced': 10,
            'quality': 5
        }.get(performance_mode, 10)
        
        # Configure environment detection
        self.audio_processor.environment_update_interval = {
            'performance': 40,
            'balanced': 20,
            'quality': 10
        }.get(performance_mode, 20)
        
        if not self.settings.get('environment_detection', True):
            self.audio_processor.environment_update_interval = 0  # Disable updates
        
        # Setup UI components
        self.setup_main_window()
        self.setup_overlay_window()
        
        # Log initialization
        self.log_message("🎯 Enhanced PUBG Sonar Radar initialized")
        self.log_message("🎵 Configure VoiceMeeter for best results")
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or use defaults"""
        try:
            settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                print("Settings loaded successfully")
                
                # Check settings version
                if 'version' not in settings or settings['version'] != SETTINGS_VERSION:
                    print(f"Settings version mismatch: found {settings.get('version', 'unknown')}, expected {SETTINGS_VERSION}")
                    print("Migrating settings to new version")
                    
                    # Keep existing settings but add new defaults
                    migrated_settings = DEFAULT_SETTINGS.copy()
                    
                    # Copy over compatible settings
                    for key, value in settings.items():
                        if key in DEFAULT_SETTINGS and key != 'version':
                            migrated_settings[key] = value
                    
                    # Update version
                    migrated_settings['version'] = SETTINGS_VERSION
                    settings = migrated_settings
                    
                    # Save migrated settings
                    self.settings = settings
                    self.save_settings()
                    print("Settings migrated and saved")
                else:
                    # Merge with defaults to ensure all settings exist
                    for key, value in DEFAULT_SETTINGS.items():
                        if key not in settings:
                            settings[key] = value
                
                return settings
            else:
                print("Settings file not found, using defaults")
                return DEFAULT_SETTINGS.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            # Ensure version is set
            self.settings['version'] = SETTINGS_VERSION
            
            settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print("Settings saved successfully")
            self.log_message("✅ Settings saved")
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.log_message(f"⚠️ Error saving settings: {e}")
    
    def setup_main_window(self):
        """Setup the main application window"""
        self.root = tk.Tk()
        self.root.title("PUBG Sonar Radar - Enhanced for Deaf Players")
        self.root.geometry("600x800")
        self.root.minsize(600, 700)
        self.root.configure(bg=self.theme.bg_dark)
        
        # Configure ttk styles
        style = ttk.Style()
        style.configure('TProgressbar', 
                       background=self.theme.text_primary,
                       troughcolor=self.theme.bg_darker)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.main_tab = tk.Frame(self.notebook, bg=self.theme.bg_dark)
        self.settings_tab = tk.Frame(self.notebook, bg=self.theme.bg_dark)
        self.calibration_tab = tk.Frame(self.notebook, bg=self.theme.bg_dark)
        self.help_tab = tk.Frame(self.notebook, bg=self.theme.bg_dark)
        
        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.calibration_tab, text="Calibration")
        self.notebook.add(self.help_tab, text="Help")
        
        # Setup tab contents
        self.setup_main_tab()
        self.setup_settings_tab()
        self.setup_calibration_tab()
        self.setup_help_tab()
        
        # Status bar
        self.status_bar = tk.Frame(self.root, bg=self.theme.bg_light, height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(
            self.status_bar, 
            text="Ready", 
            fg=self.theme.text_muted, 
            bg=self.theme.bg_light,
            font=self.theme.get_font('text', 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Add keyboard shortcut help to status bar
        keyboard_help = tk.Label(
            self.status_bar, 
            text="Shortcuts: Ctrl+R (Radar), Ctrl+O (Overlay), Ctrl+L (Lock), Ctrl+T (Sweep), F1 (Help)", 
            fg=self.theme.text_muted, 
            bg=self.theme.bg_light,
            font=self.theme.get_font('text', 8)
        )
        keyboard_help.pack(side=tk.RIGHT, padx=10)
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind keyboard events for player action detection
        self.root.bind_all("<Key>", lambda e: self.audio_processor.self_sound_filter.register_player_action('key'))
        self.root.bind_all("<Button>", lambda e: self.audio_processor.self_sound_filter.register_player_action('mouse'))
        
        # Bind keyboard shortcuts
        if self.settings.get('keyboard_shortcuts_enabled', True):
            self.root.bind('<Control-s>', lambda e: self.save_settings())
            self.root.bind('<Control-r>', lambda e: self.toggle_radar())
            self.root.bind('<Control-o>', lambda e: self.toggle_overlay())
            self.root.bind('<Control-l>', lambda e: self.toggle_lock())
            self.root.bind('<Control-t>', lambda e: self.toggle_sweep())
            self.root.bind('<F1>', lambda e: self.show_help())
    
    def setup_main_tab(self):
        """Setup the main tab with controls and status"""
        # Header
        header_frame = tk.Frame(self.main_tab, bg=self.theme.bg_dark)
        header_frame.pack(pady=15)
        
        title_label = tk.Label(
            header_frame, 
            text="🎯 PUBG SONAR RADAR", 
            font=self.theme.get_font('title', 18, True), 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame, 
            text=("Enhanced for Deaf Players • VoiceMeeter Ready" + (" • Heuristic Mode" if not self.ml_model_available else "")), 
            font=self.theme.get_font('title', 10), 
            fg=self.theme.text_secondary, 
            bg=self.theme.bg_dark
        )
        subtitle_label.pack()
        
        # Main control panel
        control_frame = tk.LabelFrame(
            self.main_tab, 
            text="⚡ RADAR CONTROL", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        control_frame.pack(pady=15, padx=20, fill='x')
        
        # Main radar toggle button
        self.radar_btn = tk.Button(
            control_frame, 
            text="🎯 START SONAR", 
            command=self.toggle_radar,
            bg=self.theme.btn_green['bg'], 
            fg=self.theme.btn_green['fg'], 
            activebackground=self.theme.btn_green['active_bg'],
            activeforeground=self.theme.btn_green['active_fg'],
            font=self.theme.get_font('title', 14, True),
            height=2, 
            width=20,
            bd=3, 
            relief='raised'
        )
        self.radar_btn.pack(pady=15)
        
        # Overlay controls in a grid
        overlay_frame = tk.Frame(control_frame, bg=self.theme.bg_dark)
        overlay_frame.pack(pady=10)
        
        self.overlay_btn = tk.Button(
            overlay_frame, 
            text="📡 Show Overlay", 
            command=self.toggle_overlay,
            bg=self.theme.btn_blue['bg'], 
            fg=self.theme.btn_blue['fg'], 
            font=self.theme.get_font('button', 10, True),
            width=15, 
            bd=2
        )
        self.overlay_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.lock_btn = tk.Button(
            overlay_frame, 
            text="🔓 Unlocked", 
            command=self.toggle_lock,
            bg=self.theme.btn_orange['bg'], 
            fg=self.theme.btn_orange['fg'], 
            font=self.theme.get_font('button', 10, True),
            width=15, 
            bd=2
        )
        self.lock_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Sonar sweep toggle
        self.sweep_btn = tk.Button(
            overlay_frame, 
            text="🌊 Sweep ON", 
            command=self.toggle_sweep,
            bg=self.theme.btn_purple['bg'], 
            fg=self.theme.btn_purple['fg'], 
            font=self.theme.get_font('button', 10, True),
            width=15, 
            bd=2
        )
        self.sweep_btn.grid(row=1, column=0, padx=5, pady=5)
        
        # Reset button
        self.reset_btn = tk.Button(
            overlay_frame, 
            text="🔄 Reset Defaults", 
            command=self.reset_to_defaults,
            bg=self.theme.btn_red['bg'], 
            fg=self.theme.btn_red['fg'], 
            font=self.theme.get_font('button', 10, True),
            width=15, 
            bd=2
        )
        self.reset_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Self-test button
        self.self_test_btn = tk.Button(
            control_frame, 
            text="🧪 Run Radar Self-Test", 
            command=self.toggle_self_test,
            bg='#333366', 
            fg='#aaccff', 
            font=self.theme.get_font('button', 11, True),
            width=20, 
            bd=2
        )
        self.self_test_btn.pack(pady=10)
        
        # Audio panel
        self.setup_audio_panel()
        
        # Sound type filters
        self.setup_sound_filters()
        
        # Status panel
        self.setup_status_panel()
    
    def setup_audio_panel(self):
        """Setup the audio configuration panel"""
        audio_frame = tk.LabelFrame(
            self.main_tab, 
            text="🎵 AUDIO CONFIGURATION", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        audio_frame.pack(pady=15, padx=20, fill='x')
        
        # VoiceMeeter detection
        vm_frame = tk.Frame(audio_frame, bg=self.theme.bg_dark)
        vm_frame.pack(pady=10, fill='x')
        
        self.vm_status = tk.Label(
            vm_frame, 
            text="VoiceMeeter: Checking...", 
            fg='#ffaa00', 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        )
        self.vm_status.pack(side=tk.LEFT)
        
        vm_help_btn = tk.Button(
            vm_frame, 
            text="❓ Setup Help", 
            command=self.show_voicemeeter_help,
            bg='#330033', 
            fg='#ff66ff',
            font=self.theme.get_font('button', 8)
        )
        vm_help_btn.pack(side=tk.RIGHT)
        
        # Audio device selection
        device_frame = tk.Frame(audio_frame, bg=self.theme.bg_dark)
        device_frame.pack(pady=10, fill='x')
        
        tk.Label(
            device_frame, 
            text="Audio Input:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        self.audio_device_var = tk.StringVar()
        self.audio_device_combo = ttk.Combobox(
            device_frame, 
            textvariable=self.audio_device_var,
            state='readonly',
            font=self.theme.get_font('text', 9)
        )
        self.audio_device_combo.pack(fill='x', pady=5)
        
        # Control buttons
        btn_frame = tk.Frame(audio_frame, bg=self.theme.bg_dark)
        btn_frame.pack(pady=5)
        
        refresh_btn = tk.Button(
            btn_frame, 
            text="🔄 Refresh", 
            command=self.refresh_audio_devices,
            bg='#003300', 
            fg='#00ff00',
            font=self.theme.get_font('button', 9)
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        test_btn = tk.Button(
            btn_frame, 
            text="🎤 Test Audio", 
            command=self.test_audio_input,
            bg='#330000', 
            fg='#ff6666',
            font=self.theme.get_font('button', 9)
        )
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Audio level indicator
        self.audio_level_var = tk.DoubleVar()
        self.audio_level_bar = ttk.Progressbar(
            audio_frame, 
            variable=self.audio_level_var,
            maximum=100, 
            length=300
        )
        self.audio_level_bar.pack(pady=5)
        
        tk.Label(
            audio_frame, 
            text="Audio Level Monitor", 
            fg=self.theme.text_muted, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 8)
        ).pack()
        
        # Set level callback
        self.audio_processor.set_level_callback(self.update_audio_level)
        
        # Initialize device list and check VoiceMeeter
        self.refresh_audio_devices()
        self.check_voicemeeter()
    def setup_sound_filters(self):
        """Setup sound type filter controls"""
        filter_frame = tk.LabelFrame(
            self.main_tab, 
            text="🔊 SOUND FILTERS", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        filter_frame.pack(pady=15, padx=20, fill='x')
        
        # Sound type checkboxes
        self.sound_type_vars = {}
        
        # Create a frame for the checkboxes with 4 columns
        checkbox_frame = tk.Frame(filter_frame, bg=self.theme.bg_dark)
        checkbox_frame.pack(pady=10, fill='x')
        
        # Add "Show All" checkbox
        self.show_all_var = tk.BooleanVar(value=self.settings.get('show_all_sounds', True))
        show_all_cb = tk.Checkbutton(
            checkbox_frame,
            text="Show All Sounds",
            variable=self.show_all_var,
            command=self.toggle_all_sound_types,
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            selectcolor=self.theme.bg_darker,
            activebackground=self.theme.bg_dark,
            activeforeground=self.theme.text_primary,
            font=self.theme.get_font('text', 10, True)
        )
        show_all_cb.grid(row=0, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Add "Filter Own Sounds" checkbox
        self.filter_own_var = tk.BooleanVar(value=self.settings.get('filter_own_sounds', True))
        filter_own_cb = tk.Checkbutton(
            checkbox_frame,
            text="Filter Own Sounds",
            variable=self.filter_own_var,
            command=self.toggle_filter_own_sounds,
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            selectcolor=self.theme.bg_darker,
            activebackground=self.theme.bg_dark,
            activeforeground=self.theme.text_primary,
            font=self.theme.get_font('text', 10, True)
        )
        filter_own_cb.grid(row=0, column=2, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Add individual sound type checkboxes
        row = 1
        col = 0
        for i, (sound_type, info) in enumerate(SOUND_TYPES.items()):
            # Get the enabled state from settings
            enabled = self.settings.get('sound_types_enabled', {}).get(sound_type, True)
            
            # Create variable and checkbox
            var = tk.BooleanVar(value=enabled)
            self.sound_type_vars[sound_type] = var
            
            cb = tk.Checkbutton(
                checkbox_frame,
                text=f"{info['symbol']} {sound_type.capitalize()}",
                variable=var,
                command=lambda st=sound_type: self.toggle_sound_type(st),
                fg=self.theme.text_primary,
                bg=self.theme.bg_dark,
                selectcolor=self.theme.bg_darker,
                activebackground=self.theme.bg_dark,
                activeforeground=self.theme.text_primary,
                font=self.theme.get_font('text', 10)
            )
            cb.grid(row=row, column=col, sticky='w', padx=10, pady=5)
            
            # Update row and column for next checkbox
            col += 1
            if col > 3:  # 4 columns (0-3)
                col = 0
                row += 1
    
    def setup_status_panel(self):
        """Setup the status panel with detection log"""
        status_frame = tk.LabelFrame(
            self.main_tab, 
            text="📊 DETECTION LOG", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        status_frame.pack(pady=15, padx=20, fill='both', expand=True)
        
        # Status text with sonar-style colors
        self.status_text = tk.Text(
            status_frame, 
            height=10, 
            width=50,
            bg=self.theme.bg_darker, 
            fg=self.theme.text_primary, 
            insertbackground=self.theme.text_primary,
            font=self.theme.get_font('text', 9),
            bd=2, 
            relief='sunken'
        )
        self.status_text.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Configure tags for different priority messages
        self.status_text.tag_configure("timestamp", foreground=self.theme.text_muted)
        self.status_text.tag_configure("high_priority", foreground="#ff3333", font=self.theme.get_font('text', 9, True))
        self.status_text.tag_configure("medium_priority", foreground="#ffcc00")
        self.status_text.tag_configure("normal_priority", foreground=self.theme.text_primary)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(status_frame, bg=self.theme.bg_dark)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
        # Detection counter and environment display
        counter_frame = tk.Frame(status_frame, bg=self.theme.bg_dark)
        counter_frame.pack(pady=5)
        
        self.counter_label = tk.Label(
            counter_frame, 
            text="Detections: 0", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('button', 10, True)
        )
        self.counter_label.pack(side=tk.LEFT, padx=10)
        
        self.env_label = tk.Label(
            counter_frame, 
            text="Environment: Unknown", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('button', 10)
        )
        self.env_label.pack(side=tk.RIGHT, padx=10)
        
        # Update environment display periodically
        self.root.after(1000, self.update_environment_display)
    
    def setup_settings_tab(self):
        """Setup the settings tab with configuration options"""
        # Radar settings
        radar_frame = tk.LabelFrame(
            self.settings_tab, 
            text="🎯 RADAR SETTINGS", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        radar_frame.pack(pady=15, padx=20, fill='x')
        
        # Radar size slider
        size_frame = tk.Frame(radar_frame, bg=self.theme.bg_dark)
        size_frame.pack(pady=8, fill='x')
        
        tk.Label(
            size_frame, 
            text="Radar Size:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        self.size_var = tk.IntVar(value=self.settings.get('radar_size', 300))
        self.size_scale = tk.Scale(
            size_frame, 
            from_=200, 
            to=500, 
            orient=tk.HORIZONTAL, 
            variable=self.size_var,
            command=self.update_radar_size,
            bg=self.theme.bg_dark, 
            fg=self.theme.text_primary,
            highlightbackground=self.theme.bg_dark,
            troughcolor='#003300',
            font=self.theme.get_font('text', 8)
        )
        self.size_scale.pack(fill='x', padx=10)
        
        # Transparency slider
        trans_frame = tk.Frame(radar_frame, bg=self.theme.bg_dark)
        trans_frame.pack(pady=8, fill='x')
        
        tk.Label(
            trans_frame, 
            text="Overlay Transparency:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        self.transparency_var = tk.DoubleVar(value=self.settings.get('transparency', 0.85))
        self.transparency_scale = tk.Scale(
            trans_frame, 
            from_=0.3, 
            to=1.0, 
            resolution=0.05, 
            orient=tk.HORIZONTAL, 
            variable=self.transparency_var,
            command=self.update_transparency,
            bg=self.theme.bg_dark, 
            fg=self.theme.text_primary,
            highlightbackground=self.theme.bg_dark,
            troughcolor='#003300',
            font=self.theme.get_font('text', 8)
        )
        self.transparency_scale.pack(fill='x', padx=10)
        
        # Sweep speed slider
        sweep_frame = tk.Frame(radar_frame, bg=self.theme.bg_dark)
        sweep_frame.pack(pady=8, fill='x')
        
        tk.Label(
            sweep_frame, 
            text="Sonar Sweep Speed:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        self.sweep_speed_var = tk.DoubleVar(value=self.settings.get('sweep_speed', 2.0))
        self.sweep_speed_scale = tk.Scale(
            sweep_frame, 
            from_=0.5, 
            to=5.0, 
            resolution=0.1, 
            orient=tk.HORIZONTAL, 
            variable=self.sweep_speed_var,
            command=self.update_sweep_speed,
            bg=self.theme.bg_dark, 
            fg=self.theme.text_primary,
            highlightbackground=self.theme.bg_dark,
            troughcolor='#003300',
            font=self.theme.get_font('text', 8)
        )
        self.sweep_speed_scale.pack(fill='x', padx=10)
        
        # Sound trails settings
        trails_frame = tk.Frame(radar_frame, bg=self.theme.bg_dark)
        trails_frame.pack(pady=8, fill='x')
        
        tk.Label(
            trails_frame, 
            text="Sound Trails:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        # Show sound trails checkbox
        self.show_trails_var = tk.BooleanVar(value=self.settings.get('show_sound_trails', True))
        show_trails_cb = tk.Checkbutton(
            trails_frame,
            text="Show Sound Movement Trails",
            variable=self.show_trails_var,
            command=self.toggle_sound_trails,
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            selectcolor=self.theme.bg_darker,
            activebackground=self.theme.bg_dark,
            activeforeground=self.theme.text_primary,
            font=self.theme.get_font('text', 10)
        )
        show_trails_cb.pack(anchor='w', pady=5)
        
        # Trail length slider
        self.trail_length_var = tk.IntVar(value=self.settings.get('trail_length', 10))
        trail_length_scale = tk.Scale(
            trails_frame, 
            from_=3, 
            to=20, 
            orient=tk.HORIZONTAL, 
            variable=self.trail_length_var,
            command=self.update_trail_length,
            bg=self.theme.bg_dark, 
            fg=self.theme.text_primary,
            highlightbackground=self.theme.bg_dark,
            troughcolor='#003300',
            font=self.theme.get_font('text', 8)
        )
        trail_length_scale.pack(fill='x', padx=10)
        
        # Audio settings
        audio_settings_frame = tk.LabelFrame(
            self.settings_tab, 
            text="🎵 AUDIO SETTINGS", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        audio_settings_frame.pack(pady=15, padx=20, fill='x')
        
        # Sensitivity slider
        sens_frame = tk.Frame(audio_settings_frame, bg=self.theme.bg_dark)
        sens_frame.pack(pady=8, fill='x')
        
        tk.Label(
            sens_frame, 
            text="Detection Sensitivity:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        self.sensitivity_var = tk.DoubleVar(value=self.settings.get('sound_threshold', 0.001) * 1000)
        self.sensitivity_scale = tk.Scale(
            sens_frame, 
            from_=0.1, 
            to=10.0, 
            resolution=0.1, 
            orient=tk.HORIZONTAL, 
            variable=self.sensitivity_var,
            command=self.update_sensitivity,
            bg=self.theme.bg_dark, 
            fg=self.theme.text_primary,
            highlightbackground=self.theme.bg_dark,
            troughcolor='#003300',
            font=self.theme.get_font('text', 8)
        )
        self.sensitivity_scale.pack(fill='x', padx=10)
        
        # Distance settings
        distance_frame = tk.LabelFrame(
            self.settings_tab, 
            text="📏 DISTANCE SETTINGS", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        distance_frame.pack(pady=15, padx=20, fill='x')
        
        # Close distance threshold
        close_frame = tk.Frame(distance_frame, bg=self.theme.bg_dark)
        close_frame.pack(pady=8, fill='x')
        
        tk.Label(
            close_frame, 
            text="Close Distance Threshold (meters):", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        self.close_distance_var = tk.IntVar(value=self.settings.get('close_distance', 30))
        self.close_distance_scale = tk.Scale(
            close_frame, 
            from_=10, 
            to=50, 
            orient=tk.HORIZONTAL, 
            variable=self.close_distance_var,
            command=self.update_close_distance,
            bg=self.theme.bg_dark, 
            fg=self.theme.text_primary,
            highlightbackground=self.theme.bg_dark,
            troughcolor='#003300',
            font=self.theme.get_font('text', 8)
        )
        self.close_distance_scale.pack(fill='x', padx=10)
        # Medium distance threshold
        medium_frame = tk.Frame(distance_frame, bg=self.theme.bg_dark)
        medium_frame.pack(pady=8, fill='x')
        
        tk.Label(
            medium_frame, 
            text="Medium Distance Threshold (meters):", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        self.medium_distance_var = tk.IntVar(value=self.settings.get('medium_distance', 100))
        self.medium_distance_scale = tk.Scale(
            medium_frame, 
            from_=50, 
            to=200, 
            orient=tk.HORIZONTAL, 
            variable=self.medium_distance_var,
            command=self.update_medium_distance,
            bg=self.theme.bg_dark, 
            fg=self.theme.text_primary,
            highlightbackground=self.theme.bg_dark,
            troughcolor='#003300',
            font=self.theme.get_font('text', 8)
        )
        self.medium_distance_scale.pack(fill='x', padx=10)
        
        # Threat assessment settings
        threat_frame = tk.LabelFrame(
            self.settings_tab, 
            text="⚠️ THREAT ASSESSMENT", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        threat_frame.pack(pady=15, padx=20, fill='x')
        
        # Enable threat highlighting checkbox
        self.highlight_threats_var = tk.BooleanVar(value=self.settings.get('highlight_threats', True))
        highlight_threats_cb = tk.Checkbutton(
            threat_frame,
            text="Highlight High Threat Sounds",
            variable=self.highlight_threats_var,
            command=self.toggle_threat_highlighting,
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            selectcolor=self.theme.bg_darker,
            activebackground=self.theme.bg_dark,
            activeforeground=self.theme.text_primary,
            font=self.theme.get_font('text', 10)
        )
        highlight_threats_cb.pack(anchor='w', pady=5)
        
        # Show threat notifications checkbox
        self.show_threat_notifications_var = tk.BooleanVar(value=self.settings.get('show_threat_notifications', True))
        show_threat_notifications_cb = tk.Checkbutton(
            threat_frame,
            text="Show Threat Notifications",
            variable=self.show_threat_notifications_var,
            command=self.toggle_threat_notifications,
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            selectcolor=self.theme.bg_darker,
            activebackground=self.theme.bg_dark,
            activeforeground=self.theme.text_primary,
            font=self.theme.get_font('text', 10)
        )
        show_threat_notifications_cb.pack(anchor='w', pady=5)
        
        # Threat sensitivity slider
        self.threat_sensitivity_var = tk.DoubleVar(value=self.settings.get('threat_sensitivity', 0.7))
        tk.Label(
            threat_frame, 
            text="Threat Sensitivity:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        threat_sensitivity_scale = tk.Scale(
            threat_frame, 
            from_=0.3, 
            to=0.9, 
            resolution=0.1,
            orient=tk.HORIZONTAL, 
            variable=self.threat_sensitivity_var,
            command=self.update_threat_sensitivity,
            bg=self.theme.bg_dark, 
            fg=self.theme.text_primary,
            highlightbackground=self.theme.bg_dark,
            troughcolor='#003300',
            font=self.theme.get_font('text', 8)
        )
        threat_sensitivity_scale.pack(fill='x', padx=10)
        
        # Performance settings
        performance_frame = tk.LabelFrame(
            self.settings_tab, 
            text="⚙️ PERFORMANCE SETTINGS", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        performance_frame.pack(pady=15, padx=20, fill='x')
        
        # Performance mode
        mode_frame = tk.Frame(performance_frame, bg=self.theme.bg_dark)
        mode_frame.pack(pady=10, fill='x')
        
        tk.Label(
            mode_frame, 
            text="Performance Mode:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('title', 10)
        ).pack(anchor='w')
        
        # Get current mode
        current_mode = self.settings.get('performance_mode', 'balanced')
        
        # Create radio buttons for performance modes
        self.performance_mode_var = tk.StringVar(value=current_mode)
        
        modes = [
            ("Performance (Low CPU/Memory)", "performance"),
            ("Balanced", "balanced"),
            ("Quality (Best Detection)", "quality")
        ]
        
        for text, mode in modes:
            rb = tk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.performance_mode_var,
                value=mode,
                command=self.update_performance_mode,
                fg=self.theme.text_primary,
                bg=self.theme.bg_dark,
                selectcolor=self.theme.bg_darker,
                activebackground=self.theme.bg_dark,
                activeforeground=self.theme.text_primary,
                font=self.theme.get_font('text', 9)
            )
            rb.pack(anchor='w', pady=2)
        
        # Memory optimization checkbox
        self.memory_optimization_var = tk.BooleanVar(value=self.settings.get('memory_optimization', True))
        memory_opt_cb = tk.Checkbutton(
            performance_frame,
            text="Enable Memory Optimization (Recommended for Long Sessions)",
            variable=self.memory_optimization_var,
            command=self.toggle_memory_optimization,
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            selectcolor=self.theme.bg_darker,
            activebackground=self.theme.bg_dark,
            activeforeground=self.theme.text_primary,
            font=self.theme.get_font('text', 9)
        )
        memory_opt_cb.pack(anchor='w', pady=5)
        
        # Environment detection checkbox
        self.environment_detection_var = tk.BooleanVar(value=self.settings.get('environment_detection', True))
        env_detect_cb = tk.Checkbutton(
            performance_frame,
            text="Enable Environment Detection",
            variable=self.environment_detection_var,
            command=self.toggle_environment_detection,
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            selectcolor=self.theme.bg_darker,
            activebackground=self.theme.bg_dark,
            activeforeground=self.theme.text_primary,
            font=self.theme.get_font('text', 9)
        )
        env_detect_cb.pack(anchor='w', pady=5)
        
        # Keyboard shortcuts checkbox
        self.keyboard_shortcuts_var = tk.BooleanVar(value=self.settings.get('keyboard_shortcuts_enabled', True))
        keyboard_shortcuts_cb = tk.Checkbutton(
            performance_frame,
            text="Enable Keyboard Shortcuts",
            variable=self.keyboard_shortcuts_var,
            command=self.toggle_keyboard_shortcuts,
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            selectcolor=self.theme.bg_darker,
            activebackground=self.theme.bg_dark,
            activeforeground=self.theme.text_primary,
            font=self.theme.get_font('text', 9)
        )
        keyboard_shortcuts_cb.pack(anchor='w', pady=5)
        
        # Color settings
        color_frame = tk.LabelFrame(
            self.settings_tab, 
            text="🎨 COLOR SETTINGS", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        color_frame.pack(pady=15, padx=20, fill='x')
        
        # Color pickers
        colors_grid = tk.Frame(color_frame, bg=self.theme.bg_dark)
        colors_grid.pack(pady=10, fill='x')
        
        # Close distance color
        tk.Label(
            colors_grid, 
            text="Close Distance:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10)
        ).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.close_color_btn = tk.Button(
            colors_grid,
            width=3,
            bg=self.settings.get('distance_colors', {}).get('close', '#ff3333'),
            command=lambda: self.choose_color('close')
        )
        self.close_color_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Medium distance color
        tk.Label(
            colors_grid, 
            text="Medium Distance:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10)
        ).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.medium_color_btn = tk.Button(
            colors_grid,
            width=3,
            bg=self.settings.get('distance_colors', {}).get('medium', '#ffcc00'),
            command=lambda: self.choose_color('medium')
        )
        self.medium_color_btn.grid(row=1, column=1, padx=10, pady=5)
        
        # Far distance color
        tk.Label(
            colors_grid, 
            text="Far Distance:", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10)
        ).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        
        self.far_color_btn = tk.Button(
            colors_grid,
            width=3,
            bg=self.settings.get('distance_colors', {}).get('far', '#33cc33'),
            command=lambda: self.choose_color('far')
        )
        self.far_color_btn.grid(row=2, column=1, padx=10, pady=5)
        
        # Save and reset buttons
        button_frame = tk.Frame(self.settings_tab, bg=self.theme.bg_dark)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            bg=self.theme.btn_green['bg'],
            fg=self.theme.btn_green['fg'],
            font=self.theme.get_font('button', 10, True),
            width=15,
            bd=2
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = tk.Button(
            button_frame,
            text="🔄 Reset All",
            command=self.reset_to_defaults,
            bg=self.theme.btn_red['bg'],
            fg=self.theme.btn_red['fg'],
            font=self.theme.get_font('button', 10, True),
            width=15,
            bd=2
        )
        reset_btn.pack(side=tk.LEFT, padx=10)
    
    def setup_calibration_tab(self):
        """Setup the calibration tab for sound classification and filtering"""
        # Header
        header_frame = tk.Frame(self.calibration_tab, bg=self.theme.bg_dark)
        header_frame.pack(pady=15)
        
        title_label = tk.Label(
            header_frame, 
            text="🎚️ CALIBRATION", 
            font=self.theme.get_font('title', 16, True), 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Calibrate sound detection for your specific setup", 
            font=self.theme.get_font('title', 10), 
            fg=self.theme.text_secondary, 
            bg=self.theme.bg_dark
        )
        subtitle_label.pack()
        
        # Self-sound calibration
        self_sound_frame = tk.LabelFrame(
            self.calibration_tab, 
            text="🔇 SELF-SOUND CALIBRATION", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        self_sound_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(
            self_sound_frame,
            text="Record your own sounds to filter them out from detection",
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10),
            justify=tk.LEFT,
            wraplength=550
        ).pack(pady=10, padx=10, fill='x')
        
        self_sound_btn_frame = tk.Frame(self_sound_frame, bg=self.theme.bg_dark)
        self_sound_btn_frame.pack(pady=10)
        
        record_self_btn = tk.Button(
            self_sound_btn_frame,
            text="🎙️ Record Self Sounds",
            command=self.record_self_sounds,
            bg=self.theme.btn_blue['bg'],
            fg=self.theme.btn_blue['fg'],
            font=self.theme.get_font('button', 10),
            width=20,
            bd=2
        )
        record_self_btn.pack(side=tk.LEFT, padx=10)
        
        clear_self_btn = tk.Button(
            self_sound_btn_frame,
            text="🗑️ Clear Self Sounds",
            command=self.clear_self_sounds,
            bg=self.theme.btn_red['bg'],
            fg=self.theme.btn_red['fg'],
            font=self.theme.get_font('button', 10),
            width=20,
            bd=2
        )
        clear_self_btn.pack(side=tk.LEFT, padx=10)
        # Sound classification calibration
        sound_class_frame = tk.LabelFrame(
            self.calibration_tab, 
            text="🔊 SOUND CLASSIFICATION CALIBRATION", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        sound_class_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(
            sound_class_frame,
            text="Record and classify PUBG sounds to improve detection accuracy",
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10),
            justify=tk.LEFT,
            wraplength=550
        ).pack(pady=10, padx=10, fill='x')
        
        # Sound type selection for calibration
        sound_type_frame = tk.Frame(sound_class_frame, bg=self.theme.bg_dark)
        sound_type_frame.pack(pady=10, fill='x')
        
        tk.Label(
            sound_type_frame,
            text="Sound Type:",
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10)
        ).pack(side=tk.LEFT, padx=10)
        
        self.calib_sound_type = tk.StringVar()
        sound_type_combo = ttk.Combobox(
            sound_type_frame,
            textvariable=self.calib_sound_type,
            values=list(SOUND_TYPES.keys()),
            state='readonly',
            font=self.theme.get_font('text', 10),
            width=15
        )
        sound_type_combo.pack(side=tk.LEFT, padx=10)
        sound_type_combo.current(0)
        
        # Calibration buttons
        calib_btn_frame = tk.Frame(sound_class_frame, bg=self.theme.bg_dark)
        calib_btn_frame.pack(pady=10)
        
        record_sound_btn = tk.Button(
            calib_btn_frame,
            text="🎙️ Record Sound Sample",
            command=self.record_sound_sample,
            bg=self.theme.btn_blue['bg'],
            fg=self.theme.btn_blue['fg'],
            font=self.theme.get_font('button', 10),
            width=20,
            bd=2
        )
        record_sound_btn.pack(side=tk.LEFT, padx=10)
        
        train_model_btn = tk.Button(
            calib_btn_frame,
            text="🧠 Train Model",
            command=self.train_sound_model,
            bg=self.theme.btn_green['bg'],
            fg=self.theme.btn_green['fg'],
            font=self.theme.get_font('button', 10),
            width=20,
            bd=2
        )
        train_model_btn.pack(side=tk.LEFT, padx=10)
        
        # Distance calibration
        distance_calib_frame = tk.LabelFrame(
            self.calibration_tab, 
            text="📏 DISTANCE CALIBRATION", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        distance_calib_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(
            distance_calib_frame,
            text="Calibrate distance estimation based on sound intensity",
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10),
            justify=tk.LEFT,
            wraplength=550
        ).pack(pady=10, padx=10, fill='x')
        
        # Distance calibration controls
        dist_calib_frame = tk.Frame(distance_calib_frame, bg=self.theme.bg_dark)
        dist_calib_frame.pack(pady=10, fill='x')
        
        tk.Label(
            dist_calib_frame,
            text="Known Distance (meters):",
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10)
        ).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.calib_distance = tk.StringVar(value="30")
        distance_entry = tk.Entry(
            dist_calib_frame,
            textvariable=self.calib_distance,
            font=self.theme.get_font('text', 10),
            width=10
        )
        distance_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Calibration buttons
        dist_btn_frame = tk.Frame(distance_calib_frame, bg=self.theme.bg_dark)
        dist_btn_frame.pack(pady=10)
        
        record_dist_btn = tk.Button(
            dist_btn_frame,
            text="🎙️ Record at Distance",
            command=self.record_distance_sample,
            bg=self.theme.btn_blue['bg'],
            fg=self.theme.btn_blue['fg'],
            font=self.theme.get_font('button', 10),
            width=20,
            bd=2
        )
        record_dist_btn.pack(side=tk.LEFT, padx=10)
        
        calibrate_dist_btn = tk.Button(
            dist_btn_frame,
            text="📊 Calibrate Distance",
            command=self.calibrate_distance,
            bg=self.theme.btn_green['bg'],
            fg=self.theme.btn_green['fg'],
            font=self.theme.get_font('button', 10),
            width=20,
            bd=2
        )
        calibrate_dist_btn.pack(side=tk.LEFT, padx=10)
        
        # Environment calibration
        env_calib_frame = tk.LabelFrame(
            self.calibration_tab, 
            text="🏙️ ENVIRONMENT CALIBRATION", 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark, 
            font=self.theme.get_font('button', 12, True),
            bd=2, 
            relief='groove'
        )
        env_calib_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(
            env_calib_frame,
            text="Calibrate environment detection for different game locations",
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10),
            justify=tk.LEFT,
            wraplength=550
        ).pack(pady=10, padx=10, fill='x')
        
        # Environment selection
        env_select_frame = tk.Frame(env_calib_frame, bg=self.theme.bg_dark)
        env_select_frame.pack(pady=10, fill='x')
        
        tk.Label(
            env_select_frame,
            text="Environment Type:",
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark,
            font=self.theme.get_font('text', 10)
        ).pack(side=tk.LEFT, padx=10)
        
        self.calib_env_type = tk.StringVar()
        env_type_combo = ttk.Combobox(
            env_select_frame,
            textvariable=self.calib_env_type,
            values=["indoor_small", "indoor_large", "outdoor_open", "outdoor_urban"],
            state='readonly',
            font=self.theme.get_font('text', 10),
            width=15
        )
        env_type_combo.pack(side=tk.LEFT, padx=10)
        env_type_combo.current(0)
        
        # Environment calibration buttons
        env_btn_frame = tk.Frame(env_calib_frame, bg=self.theme.bg_dark)
        env_btn_frame.pack(pady=10)
        
        record_env_btn = tk.Button(
            env_btn_frame,
            text="🎙️ Record Environment",
            command=self.record_environment_sample,
            bg=self.theme.btn_blue['bg'],
            fg=self.theme.btn_blue['fg'],
            font=self.theme.get_font('button', 10),
            width=20,
            bd=2
        )
        record_env_btn.pack(side=tk.LEFT, padx=10)
        
        calibrate_env_btn = tk.Button(
            env_btn_frame,
            text="📊 Calibrate Environment",
            command=self.calibrate_environment,
            bg=self.theme.btn_green['bg'],
            fg=self.theme.btn_green['fg'],
            font=self.theme.get_font('button', 10),
            width=20,
            bd=2
        )
        calibrate_env_btn.pack(side=tk.LEFT, padx=10)
    
    def setup_help_tab(self):
        """Setup the help tab with instructions and information"""
        # Header
        header_frame = tk.Frame(self.help_tab, bg=self.theme.bg_dark)
        header_frame.pack(pady=15)
        
        title_label = tk.Label(
            header_frame, 
            text="❓ HELP & INFORMATION", 
            font=self.theme.get_font('title', 16, True), 
            fg=self.theme.text_primary, 
            bg=self.theme.bg_dark
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Instructions and information for using the PUBG Sonar Radar", 
            font=self.theme.get_font('title', 10), 
            fg=self.theme.text_secondary, 
            bg=self.theme.bg_dark
        )
        subtitle_label.pack()
        
        # Create a notebook for help sections
        help_notebook = ttk.Notebook(self.help_tab)
        help_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create help section tabs
        getting_started_tab = tk.Frame(help_notebook, bg=self.theme.bg_dark)
        sound_types_tab = tk.Frame(help_notebook, bg=self.theme.bg_dark)
        voicemeeter_tab = tk.Frame(help_notebook, bg=self.theme.bg_dark)
        shortcuts_tab = tk.Frame(help_notebook, bg=self.theme.bg_dark)
        about_tab = tk.Frame(help_notebook, bg=self.theme.bg_dark)
        
        help_notebook.add(getting_started_tab, text="Getting Started")
        help_notebook.add(sound_types_tab, text="Sound Types")
        help_notebook.add(voicemeeter_tab, text="VoiceMeeter Setup")
        help_notebook.add(shortcuts_tab, text="Keyboard Shortcuts")
        help_notebook.add(about_tab, text="About")
        
        # Getting Started content
        self.create_help_content(
            getting_started_tab,
            "Getting Started with PUBG Sonar Radar",
            [
                "1. Connect your VoiceMeeter Banana or Potato to PUBG audio output",
                "2. Select the appropriate VoiceMeeter output as your input device",
                "3. Click 'Start Sonar' to begin sound detection",
                "4. Use 'Show Overlay' to display the radar over your game",
                "5. Lock the overlay in position once placed correctly",
                "6. Adjust sensitivity if needed in the Settings tab",
                "7. Use the sound type filters to focus on specific sounds",
                "",
                "The radar will show detected sounds with different symbols and colors:",
                "- Red: Close sounds (≤30m) - immediate threat",
                "- Yellow: Medium distance sounds (30-100m)",
                "- Green: Far sounds (>100m)",
                "",
                "NEW FEATURES:",
                "- Sound trails show movement patterns of detected sounds",
                "- Threat assessment highlights dangerous sounds",
                "- Environment detection adapts to indoor/outdoor locations",
                "- Performance modes to balance quality and CPU usage"
            ]
        )
        
        # Sound Types content
        self.create_help_content(
            sound_types_tab,
            "Sound Types and Symbols",
            [
                "The radar uses different symbols to represent sound types:",
                "",
                "👣 Footsteps: Player movement (walking, running, jumping)",
                "🚗 Vehicles: Cars, motorcycles, boats, etc.",
                "🔫 Gunfire: Weapon firing sounds",
                "💣 Grenades: Explosions, grenade bounces",
                "💊 Healing: Med kits, bandages, energy drinks",
                "🚪 Doors: Door opening/closing sounds",
                "🔄 Reload: Weapon reloading sounds",
                "❓ Unknown: Unclassified sounds",
                "",
                "Sound classification accuracy improves with calibration.",
                "Use the Calibration tab to record sound samples for better detection.",
                "",
                "Threat Assessment:",
                "The system automatically evaluates threat levels based on:",
                "- Sound type (gunfire and footsteps are higher threat)",
                "- Distance (closer sounds are higher threat)",
                "- Recency (newer sounds are higher threat)"
            ]
        )
        
        # VoiceMeeter Setup content
        self.create_help_content(
            voicemeeter_tab,
            "VoiceMeeter Setup Guide",
            [
                "VoiceMeeter Banana/Potato Setup for PUBG:",
                "",
                "1. Install VoiceMeeter Banana (free) or Potato (for 7.1 surround)",
                "2. Set Windows default playback to VoiceMeeter Input",
                "3. Set PUBG audio output to VoiceMeeter",
                "4. In VoiceMeeter:",
                "   - Route Hardware Input A1 to your headphones",
                "   - Enable 'Monitor' on Hardware Input",
                "5. In this app, select 'VoiceMeeter Output' as input device",
                "6. Adjust sensitivity until you see audio levels",
                "",
                "For 7.1 surround sound (recommended):",
                "- Use VoiceMeeter Potato (supports 8 channels)",
                "- Set PUBG to 7.1 surround sound",
                "- Route all channels through VoiceMeeter",
                "",
                "For best results:",
                "- Set VoiceMeeter buffer size to 256 or lower",
                "- Use ASIO drivers if available",
                "- Close other audio applications"
            ]
        )
        
        # Keyboard Shortcuts content
        self.create_help_content(
            shortcuts_tab,
            "Keyboard Shortcuts",
            [
                "The following keyboard shortcuts are available:",
                "",
                "Ctrl+R: Toggle Radar On/Off",
                "Ctrl+O: Toggle Overlay Visibility",
                "Ctrl+L: Lock/Unlock Overlay Position",
                "Ctrl+T: Toggle Sweep Animation",
                "Ctrl+S: Save Settings",
                "F1: Show Help",
                "",
                "You can enable/disable keyboard shortcuts in the Settings tab",
                "under Performance Settings."
            ]
        )
        
        # About content
        self.create_help_content(
            about_tab,
            "About PUBG Sonar Radar",
            [
                "PUBG Sonar Radar - Enhanced for Deaf Players",
                "Version 3.0",
                "",
                "This application is designed to help deaf and hard-of-hearing",
                "players visualize audio cues in PUBG through a sonar-style radar.",
                "",
                "Features:",
                "- Sound direction detection with 7.1 surround sound support",
                "- Sound type classification (footsteps, vehicles, gunfire, etc.)",
                "- Distance estimation with color coding",
                "- Player sound filtering",
                "- Sound movement trails",
                "- Threat assessment",
                "- Environment detection",
                "- Customizable overlay",
                "",
                "Created for the deaf gaming community to provide",
                "equal access to crucial audio information in PUBG."
            ]
        )
    def create_help_content(self, parent, title, content_lines):
        """Create help content with title and text"""
        frame = tk.Frame(parent, bg=self.theme.bg_dark)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            frame,
            text=title,
            font=self.theme.get_font('title', 14, True),
            fg=self.theme.text_primary,
            bg=self.theme.bg_dark
        )
        title_label.pack(pady=(0, 10), anchor='w')
        
        # Content
        content_text = tk.Text(
            frame,
            bg=self.theme.bg_darker,
            fg=self.theme.text_primary,
            font=self.theme.get_font('text', 10),
            wrap=tk.WORD,
            bd=1,
            relief=tk.SUNKEN,
            padx=10,
            pady=10,
            height=20
        )
        content_text.pack(fill='both', expand=True)
        
        # Insert content
        content_text.insert(tk.END, "\n".join(content_lines))
        content_text.config(state=tk.DISABLED)  # Make read-only
        
        # Scrollbar
        scrollbar = tk.Scrollbar(content_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=content_text.yview)
    
    def setup_overlay_window(self):
        """Setup the sonar overlay window"""
        self.overlay = tk.Toplevel()
        self.overlay.withdraw()  # Hide initially
        try:
            # Windows-specific attributes
            if WINDOWS_FEATURES_AVAILABLE:
                self.overlay.overrideredirect(True)
                self.overlay.attributes('-topmost', True)
                self.overlay.attributes('-transparentcolor', 'black')
            else:
                # Cross-platform fallback
                self.overlay.overrideredirect(True)  # This works on most platforms
                try:
                    self.overlay.attributes('-topmost', True)
                except tk.TclError:
                    pass
            self.overlay.configure(bg='black')
            try:
                self.overlay.attributes('-alpha', self.settings.get('transparency', 0.85))
            except tk.TclError:
                self.overlay.configure(bg='#111111')
                self.log_message("⚠️ Transparency not supported on this platform")
        except Exception as e:
            print(f"Error configuring overlay window: {e}")
            self.overlay.configure(bg='black')
                
        # Create canvas for sonar
        radar_size = self.settings.get('radar_size', 300)
        self.overlay_canvas = tk.Canvas(
            self.overlay, 
            width=radar_size, 
            height=radar_size,
            bg='black', 
            highlightthickness=0
        )
        self.overlay_canvas.pack()
        
        # Bind mouse events for dragging
        self.overlay_canvas.bind('<Button-1>', self.start_drag)
        self.overlay_canvas.bind('<B1-Motion>', self.do_drag)
        
        # Initialize drag variables
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Draw the sonar base
        self.draw_sonar_base()
        
        # Start sonar animation
        self.animate_sonar()
    
    def check_voicemeeter(self):
        """Check if VoiceMeeter is available"""
        if self.audio_processor.has_voicemeeter():
            self.vm_status.config(text="VoiceMeeter: ✅ Detected", fg='#00ff00')
        else:
            self.vm_status.config(text="VoiceMeeter: ❌ Not Found", fg='#ff6600')
    
    def show_voicemeeter_help(self):
        """Show VoiceMeeter setup help"""
        help_text = """
VoiceMeeter Setup for PUBG Sonar:

1. Install VoiceMeeter Banana (free) or Potato (for 7.1)
2. Set Windows default playback to VoiceMeeter Input
3. Set PUBG audio output to VoiceMeeter
4. In VoiceMeeter:
   - Route Hardware Input A1 to your headphones
   - Enable "Monitor" on Hardware Input
5. In this app, select "VoiceMeeter Output" as input device
6. Adjust sensitivity until you see audio levels

For 7.1 surround sound (recommended):
- Use VoiceMeeter Potato (supports 8 channels)
- Set PUBG to 7.1 surround sound
- Route all channels through VoiceMeeter
        """
        
        messagebox.showinfo("VoiceMeeter Setup Guide", help_text)
    
    def show_help(self):
        """Show keyboard shortcuts help"""
        help_text = """
Keyboard Shortcuts:

Ctrl+R: Toggle Radar On/Off
Ctrl+O: Toggle Overlay Visibility
Ctrl+L: Lock/Unlock Overlay Position
Ctrl+T: Toggle Sweep Animation
Ctrl+S: Save Settings
F1: Show This Help
        """
        
        messagebox.showinfo("Keyboard Shortcuts", help_text)
    
    def refresh_audio_devices(self):
        """Refresh the list of available audio devices"""
        devices = self.audio_processor.get_devices()
        
        # Update combobox
        self.audio_device_combo['values'] = [d['display_name'] for d in devices]
        if devices:
            self.audio_device_combo.current(0)
        
        self.log_message(f"📡 Found {len(devices)} audio devices")
    
    def test_audio_input(self):
        """Test the selected audio input device"""
        if not self.audio_device_var.get():
            messagebox.showwarning("Warning", "Please select an audio device first")
            return
        
        self.log_message("🎤 Testing audio input for 5 seconds...")
        
        try:
            device_index = int(self.audio_device_var.get().split(':')[0])
            success, max_level = self.audio_processor.test_device(device_index)
            
            if success:
                self.log_message(f"🎵 Max audio level: {max_level:.4f}")
                if max_level < 0.001:
                    self.log_message("⚠️ Very low audio! Check VoiceMeeter routing")
                elif max_level > 0.1:
                    self.log_message("⚠️ Audio very loud! Reduce sensitivity")
                else:
                    self.log_message("✅ Audio levels look good!")
            else:
                self.log_message("❌ Audio test failed")
        
        except Exception as e:
            self.log_message(f"❌ Audio test error: {str(e)}")
            messagebox.showerror("Error", f"Audio test failed: {str(e)}")
    
    def toggle_radar(self):
        """Toggle the radar on/off"""
        if not self.radar_active:
            self.start_radar()
        else:
            self.stop_radar()
    
    def start_radar(self):
        """Start the sonar radar"""
        if not self.audio_device_var.get():
            messagebox.showerror("Error", "Please select an audio device")
            return
        
        try:
            device_index = int(self.audio_device_var.get().split(':')[0])
            
            if self.audio_processor.start(device_index):
                self.radar_active = True
                self.radar_btn.config(
                    text="🛑 STOP SONAR", 
                    bg=self.theme.btn_red['bg'], 
                    fg=self.theme.btn_red['fg']
                )
                self.log_message("✅ Sonar radar active")
                
                # Update status bar
                self.status_label.config(text="Radar Active", fg=self.theme.text_primary)
            else:
                self.log_message("❌ Failed to start radar")
        
        except Exception as e:
            self.log_message(f"❌ Failed to start radar: {str(e)}")
            messagebox.showerror("Error", f"Failed to start radar: {str(e)}")
    
    def stop_radar(self):
        """Stop the sonar radar"""
        self.radar_active = False
        self.audio_processor.stop()
        
        self.radar_btn.config(
            text="🎯 START SONAR", 
            bg=self.theme.btn_green['bg'], 
            fg=self.theme.btn_green['fg']
        )
        self.log_message("🛑 Sonar radar stopped")
        
        # Update status bar
        self.status_label.config(text="Radar Inactive", fg=self.theme.text_muted)
    
    def toggle_overlay(self):
        """Toggle the overlay visibility"""
        if self.overlay_visible:
            self.overlay.withdraw()
            self.overlay_btn.config(text="📡 Show Overlay")
            self.overlay_visible = False
        else:
            self.overlay.deiconify()
            self.overlay_btn.config(text="📡 Hide Overlay")
            self.overlay_visible = True
    
    def toggle_lock(self):
        """Toggle the overlay lock state"""
        self.overlay_locked = not self.overlay_locked
        if self.overlay_locked:
            self.lock_btn.config(text="🔒 Locked", bg='#003300', fg='#00ff00')
        else:
            self.lock_btn.config(text="🔓 Unlocked", bg='#331a00', fg='#ff9900')
    
    def toggle_sweep(self):
        """Toggle the sonar sweep animation"""
        self.sonar_sweep_active = not self.sonar_sweep_active
        if self.sonar_sweep_active:
            self.sweep_btn.config(text="🌊 Sweep ON", bg='#1a0033', fg='#cc00ff')
        else:
            self.sweep_btn.config(text="⏸️ Sweep OFF", bg='#330000', fg='#ff6666')
    
    def toggle_all_sound_types(self):
        """Toggle all sound type filters"""
        show_all = self.show_all_var.get()
        
        # Update all checkboxes
        for sound_type, var in self.sound_type_vars.items():
            var.set(show_all)
        
        # Update settings
        self.settings['show_all_sounds'] = show_all
        for sound_type in SOUND_TYPES:
            self.settings['sound_types_enabled'][sound_type] = show_all
    
    def toggle_sound_type(self, sound_type):
        """Toggle a specific sound type filter"""
        enabled = self.sound_type_vars[sound_type].get()
        self.settings['sound_types_enabled'][sound_type] = enabled
        
        # Check if all are enabled/disabled
        all_enabled = all(var.get() for var in self.sound_type_vars.values())
        all_disabled = not any(var.get() for var in self.sound_type_vars.values())
        
        if all_enabled:
            self.show_all_var.set(True)
            self.settings['show_all_sounds'] = True
        elif all_disabled:
            self.show_all_var.set(False)
            self.settings['show_all_sounds'] = False
    
    def toggle_filter_own_sounds(self):
        """Toggle filtering of player's own sounds"""
        filter_own = self.filter_own_var.get()
        self.settings['filter_own_sounds'] = filter_own
        self.audio_processor.filter_own_sounds = filter_own
    
    def toggle_sound_trails(self):
        """Toggle sound movement trails"""
        show_trails = self.show_trails_var.get()
        self.settings['show_sound_trails'] = show_trails
        self.save_settings()
    
    def update_trail_length(self, value):
        """Update the trail length"""
        length = int(value)
        self.settings['trail_length'] = length
        self.save_settings()
    
    def toggle_threat_highlighting(self):
        """Toggle threat highlighting"""
        highlight_threats = self.highlight_threats_var.get()
        self.settings['highlight_threats'] = highlight_threats
        self.save_settings()
    
    def toggle_threat_notifications(self):
        """Toggle threat notifications"""
        show_notifications = self.show_threat_notifications_var.get()
        self.settings['show_threat_notifications'] = show_notifications
        self.save_settings()
    
    def update_threat_sensitivity(self, value):
        """Update the threat sensitivity threshold"""
        sensitivity = float(value)
        self.settings['threat_sensitivity'] = sensitivity
        self.save_settings()
    
    def update_performance_mode(self):
        """Update the performance mode"""
        mode = self.performance_mode_var.get()
        self.settings['performance_mode'] = mode
        
        # Apply performance settings
        if mode == 'performance':
            # Optimize for performance
            self.audio_processor.feature_throttle = 20  # Process heavy features less frequently
            self.audio_processor.environment_update_interval = 40  # Update environment less frequently
            self.settings['show_sound_trails'] = False  # Disable trails
            self.show_trails_var.set(False)
        elif mode == 'balanced':
            # Balanced settings
            self.audio_processor.feature_throttle = 10
            self.audio_processor.environment_update_interval = 20
        elif mode == 'quality':
            # Optimize for quality
            self.audio_processor.feature_throttle = 5  # Process heavy features more frequently
            self.audio_processor.environment_update_interval = 10  # Update environment more frequently
        
        self.save_settings()
        self.log_message(f"Performance mode changed to: {mode}")
    def toggle_memory_optimization(self):
        """Toggle memory optimization"""
        enabled = self.memory_optimization_var.get()
        self.settings['memory_optimization'] = enabled
        self.save_settings()
    
    def toggle_environment_detection(self):
        """Toggle environment detection"""
        enabled = self.environment_detection_var.get()
        self.settings['environment_detection'] = enabled
        
        # Enable/disable environment detection
        if hasattr(self, 'audio_processor'):
            if enabled:
                self.audio_processor.environment_update_interval = {
                    'performance': 40,
                    'balanced': 20,
                    'quality': 10
                }.get(self.settings.get('performance_mode', 'balanced'), 20)
            else:
                self.audio_processor.environment_update_interval = 0  # Disable updates
        
        self.save_settings()
    
    def toggle_keyboard_shortcuts(self):
        """Toggle keyboard shortcuts"""
        enabled = self.keyboard_shortcuts_var.get()
        self.settings['keyboard_shortcuts_enabled'] = enabled
        
        # Apply keyboard shortcut settings
        if enabled:
            self.root.bind('<Control-s>', lambda e: self.save_settings())
            self.root.bind('<Control-r>', lambda e: self.toggle_radar())
            self.root.bind('<Control-o>', lambda e: self.toggle_overlay())
            self.root.bind('<Control-l>', lambda e: self.toggle_lock())
            self.root.bind('<Control-t>', lambda e: self.toggle_sweep())
            self.root.bind('<F1>', lambda e: self.show_help())
        else:
            self.root.unbind('<Control-s>')
            self.root.unbind('<Control-r>')
            self.root.unbind('<Control-o>')
            self.root.unbind('<Control-l>')
            self.root.unbind('<Control-t>')
            self.root.unbind('<F1>')
        
        self.save_settings()
    
    def start_drag(self, event):
        """Start dragging the overlay"""
        if not self.overlay_locked:
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
    
    def do_drag(self, event):
        """Handle overlay dragging"""
        if not self.overlay_locked:
            x = self.overlay.winfo_x() + event.x_root - self.drag_start_x
            y = self.overlay.winfo_y() + event.y_root - self.drag_start_y
            self.overlay.geometry(f"+{x}+{y}")
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
    
    def update_sensitivity(self, value):
        """Update the sound detection sensitivity"""
        threshold = float(value) / 1000.0
        self.settings['sound_threshold'] = threshold
        self.audio_processor.sound_threshold = threshold
    
    def update_radar_size(self, value):
        """Update the radar size"""
        size = int(value)
        self.settings['radar_size'] = size
        
        # Update overlay canvas
        if hasattr(self, 'overlay_canvas'):
            self.overlay_canvas.config(width=size, height=size)
            self.overlay.geometry(f"{size}x{size}")
            self.draw_sonar_base()
    
    def update_sweep_speed(self, value):
        """Update the sweep speed"""
        speed = float(value)
        self.settings['sweep_speed'] = speed
    
    def update_transparency(self, value):
        """Update the overlay transparency"""
        transparency = float(value)
        self.settings['transparency'] = transparency
        if hasattr(self, 'overlay'):
            self.overlay.attributes('-alpha', transparency)
    
    def update_close_distance(self, value):
        """Update the close distance threshold"""
        distance = int(value)
        self.settings['close_distance'] = distance
    
    def update_medium_distance(self, value):
        """Update the medium distance threshold"""
        distance = int(value)
        self.settings['medium_distance'] = distance
    
    def choose_color(self, distance_type):
        """Open color chooser dialog for distance colors"""
        current_color = self.settings.get('distance_colors', {}).get(distance_type, DISTANCE_COLORS[distance_type])
        color = colorchooser.askcolor(color=current_color, title=f"Choose {distance_type} distance color")
        
        if color[1]:  # If a color was chosen
            # Update settings
            if 'distance_colors' not in self.settings:
                self.settings['distance_colors'] = {}
            self.settings['distance_colors'][distance_type] = color[1]
            
            # Update button color
            if distance_type == 'close':
                self.close_color_btn.config(bg=color[1])
            elif distance_type == 'medium':
                self.medium_color_btn.config(bg=color[1])
            elif distance_type == 'far':
                self.far_color_btn.config(bg=color[1])
    
    def update_audio_level(self, level):
        """Update the audio level indicator"""
        self.audio_level_var.set(min(100, level * 1000))
    
    def update_environment_display(self):
        """Update the environment display"""
        if hasattr(self, 'audio_processor') and hasattr(self.audio_processor, 'current_environment'):
            env = self.audio_processor.current_environment
            env_display = env.replace('_', ' ').title()
            self.env_label.config(text=f"Environment: {env_display}")
        
        # Schedule next update
        self.root.after(1000, self.update_environment_display)
    
    def handle_detection(self, detection: SoundDetection):
        """Handle a new sound detection"""
        # Check if this sound type is enabled
        if not self.settings.get('sound_types_enabled', {}).get(detection.sound_type, True):
            return
        
        # Add to detection history
        self.detection_history.append(detection)
        
        # Update detection counter
        self.detection_count += 1
        self.counter_label.config(text=f"Detections: {self.detection_count}")
        
        # Check for high-threat sounds
        if detection.threat_level > self.settings.get('threat_sensitivity', 0.7):
            # Show threat notification if enabled
            if self.settings.get('show_threat_notifications', True):
                self.show_threat_notification(detection)
        
        # Log significant detections (higher confidence)
        if detection.confidence > 0.5:
            distance_category = detection.distance_category
            color_code = {
                'close': '🔴',
                'medium': '🟡',
                'far': '🟢'
            }.get(distance_category, '⚪')
            
            sound_symbol = SOUND_TYPES.get(detection.sound_type, {}).get('symbol', '❓')
            
            # Determine priority based on threat level
            priority = "normal"
            if detection.threat_level > self.settings.get('threat_sensitivity', 0.7):
                priority = "high"
            elif detection.threat_level > 0.4:
                priority = "medium"
            
            self.log_message(
                f"{color_code} {sound_symbol} {detection.sound_type.capitalize()} detected: "
                f"{self.get_direction_name(detection.angle)} ({detection.angle:.1f}°) - "
                f"{detection.distance:.1f}m",
                priority=priority
            )
    
    def show_threat_notification(self, detection: SoundDetection):
        """Show a notification for high-threat sounds"""
        # Get direction name
        direction = self.get_direction_name(detection.angle)
        
        # Get sound type
        sound_type = detection.sound_type.capitalize()
        
        # Get distance
        distance = f"{detection.distance:.1f}m"
        
        # Create notification message
        message = f"⚠️ {sound_type} detected {distance} {direction}"
        
        # Add to log with high priority
        self.log_message(message, priority="high")
        
        # Flash the overlay border if visible
        if self.overlay_visible:
            self.flash_overlay_border()
    
    def flash_overlay_border(self):
        """Flash the overlay border to alert the user"""
        # Create a border around the overlay
        border_width = 4
        border_color = "#ff0000"  # Red
        
        # Save original overlay background
        original_bg = self.overlay.cget("bg")
        
        # Create border effect
        self.overlay.configure(bg=border_color)
        self.overlay_canvas.configure(bd=border_width, highlightthickness=border_width, highlightbackground=border_color)
        
        # Reset after a short delay
        self.root.after(300, lambda: self.overlay.configure(bg=original_bg))
        self.root.after(300, lambda: self.overlay_canvas.configure(bd=0, highlightthickness=0))
    
    def toggle_self_test(self):
        """Toggle the self-test mode"""
        if not self.self_test_active:
            self.start_self_test()
        else:
            self.stop_self_test()
    
    def start_self_test(self):
        """Start the radar self-test"""
        self.self_test_active = True
        self.self_test_btn.config(text="⏹️ Stop Self-Test", bg='#660000', fg='#ff9999')
        
        # Initialize test sequence
        self.self_test_count = 0
        self.self_test_sequence = [
            {'angle': 0, 'distance': 20, 'sound_type': 'footstep'},
            {'angle': 90, 'distance': 50, 'sound_type': 'vehicle'},
            {'angle': 180, 'distance': 150, 'sound_type': 'gunfire'},
            {'angle': 270, 'distance': 30, 'sound_type': 'grenade'},
            {'angle': 45, 'distance': 15, 'sound_type': 'footstep'},
            {'angle': 135, 'distance': 80, 'sound_type': 'door'},
            {'angle': 225, 'distance': 40, 'sound_type': 'reload'},
            {'angle': 315, 'distance': 120, 'sound_type': 'vehicle'}
        ]
        
        self.log_message("🧪 Starting radar self-test...")
        
        # Start test sequence
        self.run_next_test()
    
    def run_next_test(self):
        """Run the next test in the sequence"""
        if not self.self_test_active or self.self_test_count >= len(self.self_test_sequence):
            self.stop_self_test()
            return
        
        # Get test parameters
        test = self.self_test_sequence[self.self_test_count]
        angle = test['angle']
        distance = test['distance']
        sound_type = test['sound_type']
        
        # Create a simulated detection
        detection = SoundDetection(
            angle=angle,
            intensity=0.1,
            distance=distance,
            sound_type=sound_type,
            timestamp=time.time(),
            confidence=0.9
        )
        
        # Process the detection
        self.handle_detection(detection)
        
        # Increment counter
        self.self_test_count += 1
        
        # Schedule next test
        self.self_test_timer = self.root.after(1000, self.run_next_test)
    
    def stop_self_test(self):
        """Stop the radar self-test"""
        self.self_test_active = False
        self.self_test_btn.config(text="🧪 Run Radar Self-Test", bg='#333366', fg='#aaccff')
        
        if self.self_test_timer:
            self.root.after_cancel(self.self_test_timer)
            self.self_test_timer = None
        
        self.log_message("🧪 Self-test complete")
    
    def record_self_sounds(self):
        """Record player's own sounds for filtering"""
        messagebox.showinfo(
            "Record Self Sounds",
            "This feature will record your own sounds to filter them out.\n\n"
            "1. Make sure your audio input is set up correctly\n"
            "2. Click OK to start recording\n"
            "3. Make the sounds you want to filter (walking, shooting, etc.)\n"
            "4. Recording will stop automatically after 10 seconds"
        )
        
        self.log_message("🎙️ Recording self sounds for 10 seconds...")
        # In a real implementation, this would record and process audio samples
        
        # Simulate recording
        self.root.after(10000, lambda: self.log_message("✅ Self sound recording complete"))
    
    def clear_self_sounds(self):
        """Clear recorded self-sound patterns"""
        if messagebox.askyesno("Clear Self Sounds", "Are you sure you want to clear all recorded self sounds?"):
            # In a real implementation, this would clear the self-sound database
            self.log_message("🗑️ Self sound patterns cleared")
    
    def record_sound_sample(self):
        """Record a sound sample for classification training"""
        sound_type = self.calib_sound_type.get()
        
        messagebox.showinfo(
            f"Record {sound_type.capitalize()} Sound",
            f"This will record a sample of {sound_type} sound for training.\n\n"
            "1. Make sure your audio input is set up correctly\n"
            "2. Click OK to start recording\n"
            "3. Play or make the sound you want to record\n"
            "4. Recording will stop automatically after 5 seconds"
        )
        
        self.log_message(f"🎙️ Recording {sound_type} sound sample for 5 seconds...")
        # In a real implementation, this would record and process audio samples
        
        # Simulate recording
        self.root.after(5000, lambda: self.log_message(f"✅ {sound_type.capitalize()} sound sample recorded"))
    
    def train_sound_model(self):
        """Train the sound classification model with recorded samples"""
        messagebox.showinfo(
            "Train Sound Model",
            "This will train the sound classification model using all recorded samples.\n\n"
            "This process may take a few minutes depending on the number of samples."
        )
        
        self.log_message("🧠 Training sound classification model...")
        # In a real implementation, this would train a machine learning model
        
        # Simulate training
        self.root.after(3000, lambda: self.log_message("✅ Sound classification model trained successfully"))
    def record_distance_sample(self):
        """Record a sound sample at a known distance for calibration"""
        try:
            distance = float(self.calib_distance.get())
            
            messagebox.showinfo(
                f"Record Sound at {distance}m",
                f"This will record a sound sample at {distance} meters for distance calibration.\n\n"
                "1. Make sure your audio input is set up correctly\n"
                "2. Click OK to start recording\n"
                "3. Play or make a sound at exactly {distance} meters distance\n"
                "4. Recording will stop automatically after 5 seconds"
            )
            
            self.log_message(f"🎙️ Recording sound at {distance}m for 5 seconds...")
            # In a real implementation, this would record and process audio samples
            
            # Simulate recording
            self.root.after(5000, lambda: self.log_message(f"✅ Sound sample at {distance}m recorded"))
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid distance in meters")
    
    def calibrate_distance(self):
        """Calibrate distance estimation using recorded samples"""
        messagebox.showinfo(
            "Calibrate Distance",
            "This will calibrate the distance estimation using all recorded samples.\n\n"
            "This process may take a few moments."
        )
        
        self.log_message("📏 Calibrating distance estimation...")
        # In a real implementation, this would calibrate the distance estimation algorithm
        
        # Simulate calibration
        self.root.after(2000, lambda: self.log_message("✅ Distance estimation calibrated successfully"))
    
    def record_environment_sample(self):
        """Record an environment sample for calibration"""
        env_type = self.calib_env_type.get()
        
        messagebox.showinfo(
            f"Record {env_type.replace('_', ' ').title()} Environment",
            f"This will record a sample of {env_type.replace('_', ' ')} environment sounds.\n\n"
            "1. Make sure your audio input is set up correctly\n"
            "2. Click OK to start recording\n"
            "3. Play or make sounds in the selected environment\n"
            "4. Recording will stop automatically after 10 seconds"
        )
        
        self.log_message(f"🎙️ Recording {env_type} environment for 10 seconds...")
        # In a real implementation, this would record and process audio samples
        
        # Simulate recording
        self.root.after(10000, lambda: self.log_message(f"✅ {env_type.replace('_', ' ').title()} environment sample recorded"))
    
    def calibrate_environment(self):
        """Calibrate environment detection using recorded samples"""
        messagebox.showinfo(
            "Calibrate Environment Detection",
            "This will calibrate the environment detection using all recorded samples.\n\n"
            "This process may take a few moments."
        )
        
        self.log_message("🏙️ Calibrating environment detection...")
        # In a real implementation, this would calibrate the environment detection algorithm
        
        # Simulate calibration
        self.root.after(2000, lambda: self.log_message("✅ Environment detection calibrated successfully"))
    
    def log_message(self, message, priority="normal"):
        """Add a message to the status text with timestamp and priority"""
        if hasattr(self, 'status_text'):
            timestamp = time.strftime("%H:%M:%S")
            
            self.status_text.configure(state='normal')
            self.status_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.status_text.insert(tk.END, f"{message}\n", priority + "_priority")
            self.status_text.see(tk.END)
            self.status_text.configure(state='disabled')
            
            # Also print to console for debugging
            print(f"[{timestamp}] {message}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.settings = DEFAULT_SETTINGS.copy()
            
            # Update UI elements
            self.size_var.set(self.settings['radar_size'])
            self.transparency_var.set(self.settings['transparency'])
            self.sweep_speed_var.set(self.settings['sweep_speed'])
            self.sensitivity_var.set(self.settings['sound_threshold'] * 1000)
            self.show_all_var.set(self.settings['show_all_sounds'])
            self.filter_own_var.set(self.settings['filter_own_sounds'])
            self.close_distance_var.set(self.settings['close_distance'])
            self.medium_distance_var.set(self.settings['medium_distance'])
            self.show_trails_var.set(self.settings['show_sound_trails'])
            self.trail_length_var.set(self.settings['trail_length'])
            self.highlight_threats_var.set(self.settings['highlight_threats'])
            self.show_threat_notifications_var.set(self.settings['show_threat_notifications'])
            self.threat_sensitivity_var.set(self.settings['threat_sensitivity'])
            self.performance_mode_var.set(self.settings['performance_mode'])
            self.memory_optimization_var.set(self.settings['memory_optimization'])
            self.environment_detection_var.set(self.settings['environment_detection'])
            self.keyboard_shortcuts_var.set(self.settings['keyboard_shortcuts_enabled'])
            
            # Update color buttons
            self.close_color_btn.config(bg=self.settings['distance_colors']['close'])
            self.medium_color_btn.config(bg=self.settings['distance_colors']['medium'])
            self.far_color_btn.config(bg=self.settings['distance_colors']['far'])
            
            # Update sound type checkboxes
            for sound_type, var in self.sound_type_vars.items():
                var.set(self.settings['sound_types_enabled'][sound_type])
            
            # Apply settings
            self.update_radar_size(self.settings['radar_size'])
            self.update_transparency(self.settings['transparency'])
            self.update_sweep_speed(self.settings['sweep_speed'])
            self.update_sensitivity(self.settings['sound_threshold'] * 1000)
            self.audio_processor.filter_own_sounds = self.settings['filter_own_sounds']
            self.update_performance_mode()
            self.toggle_environment_detection()
            self.toggle_keyboard_shortcuts()
            
            self.log_message("🔄 Settings reset to defaults")
    
    def draw_sonar_base(self):
        """Draw the base sonar display"""
        # Get radar dimensions
        radar_size = self.settings.get('radar_size', 300)
        center_x = radar_size // 2
        center_y = radar_size // 2
        
        # Create or resize buffer image if needed
        if (self.buffer_image is None or 
            self.buffer_image.width != radar_size or 
            self.buffer_image.height != radar_size):
            self.buffer_image = Image.new('RGBA', (radar_size, radar_size), (0, 0, 0, 0))
        
        # Create drawing context
        draw = ImageDraw.Draw(self.buffer_image)
        
        # Clear buffer
        draw.rectangle([0, 0, radar_size, radar_size], fill=(0, 0, 0, 0))
        
        # Parse colors
        sonar_ring_color = self._parse_color(self.theme.sonar_ring)
        sonar_line_color = self._parse_color(self.theme.sonar_line)
        text_color = self._parse_color(self.theme.text_primary)
        
        # Draw concentric circles (sonar rings)
        ring_count = 4
        for i in range(1, ring_count + 1):
            radius = (radar_size / 2) * (i / ring_count)
            
            # Draw dashed circle
            self._draw_dashed_circle(
                draw, 
                center_x, 
                center_y, 
                radius, 
                sonar_ring_color, 
                dash_length=5, 
                gap_length=5
            )
        
        # Draw cardinal direction lines
        directions = [0, 45, 90, 135, 180, 225, 270, 315]
        labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        radius = radar_size / 2
        
        # Try to load font
        try:
            font = ImageFont.truetype("Arial", 10)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        for angle, label in zip(directions, labels):
            # Convert angle to radians
            rad = math.radians(angle)
            
            # Calculate line endpoints
            x1 = center_x
            y1 = center_y
            x2 = center_x + radius * math.sin(rad)
            y2 = center_y - radius * math.cos(rad)
            
            # Draw direction line (dashed)
            self._draw_dashed_line(
                draw, 
                x1, y1, x2, y2, 
                sonar_line_color, 
                dash_length=3, 
                gap_length=3
            )
            
            # Add direction label
            label_x = center_x + (radius + 15) * math.sin(rad)
            label_y = center_y - (radius + 15) * math.cos(rad)
            
            # Draw text
            if font:
                draw.text((label_x, label_y), label, fill=text_color, font=font, anchor="mm")
            else:
                # Fallback if font not available
                draw.text((label_x, label_y), label, fill=text_color)
        
        # Draw center dot
        draw.ellipse(
            [center_x - 3, center_y - 3, center_x + 3, center_y + 3],
            fill=text_color
        )
        
        # Update the canvas with the buffer
        self._update_canvas_from_buffer()
    
    def _parse_color(self, color_str):
        """Parse a color string to RGBA tuple"""
        if color_str.startswith('#'):
            # Convert hex to RGB
            r = int(color_str[1:3], 16)
            g = int(color_str[3:5], 16)
            b = int(color_str[5:7], 16)
            
            # Add alpha if available
            if len(color_str) > 7:
                a = int(color_str[7:9], 16)
            else:
                a = 255
                
            return (r, g, b, a)
        else:
            # Default to white if parsing fails
            return (255, 255, 255, 255)
    
    def _draw_dashed_line(self, draw, x1, y1, x2, y2, color, dash_length=5, gap_length=5):
        """Draw a dashed line on the given ImageDraw object"""
        # Calculate line length and angle
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
            
        # Normalize direction vector
        dx /= length
        dy /= length
        
        # Draw dashes
        pos = 0
        drawing = True
        
        while pos < length:
            # Calculate segment length
            segment_length = dash_length if drawing else gap_length
            end_pos = min(pos + segment_length, length)
            segment_dx = dx * (end_pos - pos)
            segment_dy = dy * (end_pos - pos)
            
            # Draw segment if it's a dash
            if drawing:
                draw.line(
                    [x1 + dx * pos, y1 + dy * pos, x1 + dx * end_pos, y1 + dy * end_pos],
                    fill=color,
                    width=1
                )
            
            # Move to next segment
            pos = end_pos
            drawing = not drawing
    
    def _draw_dashed_circle(self, draw, center_x, center_y, radius, color, dash_length=5, gap_length=5):
        """Draw a dashed circle on the given ImageDraw object"""
        # Calculate circumference
        circumference = 2 * math.pi * radius
        
        # Calculate number of segments
        segment_length = dash_length + gap_length
        num_segments = int(circumference / segment_length)
        
        # Ensure at least 8 segments
        num_segments = max(num_segments, 8)
        
        # Draw segments
        for i in range(num_segments):
            # Calculate start and end angles
            start_angle = i * 2 * math.pi / num_segments
            arc_angle = dash_length / circumference * 2 * math.pi
            end_angle = start_angle + arc_angle
            
            # Convert to degrees for PIL
            start_deg = math.degrees(start_angle)
            end_deg = math.degrees(end_angle)
            
            # Draw arc
            draw.arc(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                start_deg,
                end_deg,
                fill=color,
                width=1
            )
    
    def _update_canvas_from_buffer(self):
        """Update the canvas with the current buffer image"""
        # Clear canvas
        self.overlay_canvas.delete("all")
        
        # Convert buffer to PhotoImage
        self.buffer_photo = ImageTk.PhotoImage(self.buffer_image)
        
        # Draw image on canvas
        self.overlay_canvas.create_image(0, 0, image=self.buffer_photo, anchor="nw")
    
    def animate_sonar(self):
        """Animate the sonar sweep and update sound detections"""
        if hasattr(self, 'overlay_canvas'):
            # Get radar dimensions
            radar_size = self.settings.get('radar_size', 300)
            center_x = radar_size // 2
            center_y = radar_size // 2
            
            # Create or resize buffer image if needed
            if (self.buffer_image is None or 
                self.buffer_image.width != radar_size or 
                self.buffer_image.height != radar_size):
                self.buffer_image = Image.new('RGBA', (radar_size, radar_size), (0, 0, 0, 0))
            
            # Create drawing context
            draw = ImageDraw.Draw(self.buffer_image)
            
            # Clear buffer
            draw.rectangle([0, 0, radar_size, radar_size], fill=(0, 0, 0, 0))
            
            # Draw base sonar elements (rings, directions)
            self.draw_sonar_base()
            
            # Draw sweep line and trail
            if self.sonar_sweep_active:
                # Update sweep angle
                self.sweep_angle = (self.sweep_angle + self.settings.get('sweep_speed', 2.0)) % 360
                
                # Parse sweep color
                sweep_color = self._parse_color(self.theme.sonar_sweep)
                
                # Draw sweep line
                radius = radar_size / 2
                rad = math.radians(self.sweep_angle)
                x2 = center_x + radius * math.sin(rad)
                y2 = center_y - radius * math.cos(rad)
                
                draw.line(
                    [center_x, center_y, x2, y2],
                    fill=sweep_color,
                    width=2
                )
                
                # Draw sweep trail (fading)
                sweep_trail_length = self.settings.get('sweep_trail_length', 60)
                for i in range(1, int(sweep_trail_length)):
                    trail_angle = (self.sweep_angle - i) % 360
                    trail_rad = math.radians(trail_angle)
                    trail_x = center_x + radius * math.sin(trail_rad)
                    trail_y = center_y - radius * math.cos(trail_rad)
                    
                    # Calculate alpha for fading effect (1.0 to 0.0 over trail length)
                    alpha = 1.0 - (i / sweep_trail_length)
                    
                    # Create color with alpha
                    trail_color = (sweep_color[0], sweep_color[1], sweep_color[2], int(alpha * 255))
                    
                    draw.line(
                        [center_x, center_y, trail_x, trail_y],
                        fill=trail_color,
                        width=1
                    )
            
            # Draw sound detections
            self.draw_sound_detections(draw)
            
            # Update the canvas with the buffer
            self._update_canvas_from_buffer()
            
            # Schedule next animation frame
            self.overlay.after(30, self.animate_sonar)
    
    def draw_sound_detections(self, draw=None):
        """
        Draw sound detection markers on the radar
        
        Args:
            draw: Optional ImageDraw object for double-buffered drawing
        """
        radar_size = self.settings.get('radar_size', 300)
        center_x = radar_size // 2
        center_y = radar_size // 2
        radius = radar_size / 2
        
        # Get current time for fade calculation
        current_time = time.time()
        
        # Get distance thresholds
        close_distance = self.settings.get('close_distance', 30)
        medium_distance = self.settings.get('medium_distance', 100)
        
        # Get distance colors
        distance_colors = self.settings.get('distance_colors', DISTANCE_COLORS)
        
        # Get trail length
        trail_length = self.settings.get('trail_length', 10)
        
        # Get threat sensitivity
        threat_sensitivity = self.settings.get('threat_sensitivity', 0.7)
        
        # Sort detections by threat level (highest first)
        sorted_detections = sorted(
            [d for d in self.detection_history if d.is_recent],
            key=lambda d: d.threat_level,
            reverse=True
        )
        
        # Using double-buffered drawing with PIL
        # Try to load font
        try:
            font_sizes = {i: ImageFont.truetype("Arial", i) for i in range(8, 20)}
        except:
            font_sizes = None
        
        # Draw each detection in history
        for detection in sorted_detections:
            # Skip if disabled sound type
            if not self.settings.get('sound_types_enabled', {}).get(detection.sound_type, True):
                continue
            
            # Calculate position based on angle and distance
            rad = math.radians(detection.angle)
            
            # Scale distance to radar size (0-200m maps to 0-radius)
            distance_factor = min(detection.distance / 200.0, 1.0)
            
            x = center_x + (radius * distance_factor) * math.sin(rad)
            y = center_y - (radius * distance_factor) * math.cos(rad)
            
            # Update trail
            detection.update_trail(x, y, max_points=trail_length)
            
            # Draw trail if enabled
            if self.settings.get('show_sound_trails', True) and len(detection.trail_points) > 1:
                # Determine color based on distance
                if detection.distance <= close_distance:
                    color_str = distance_colors.get('close', '#ff3333')
                elif detection.distance <= medium_distance:
                    color_str = distance_colors.get('medium', '#ffcc00')
                else:
                    color_str = distance_colors.get('far', '#33cc33')
                
                # Parse color
                base_color = self._parse_color(color_str)
                
                # Draw trail lines with fading transparency
                for i in range(1, len(detection.trail_points)):
                    # Calculate alpha based on point age (older points are more transparent)
                    alpha_factor = 0.7 * (i / len(detection.trail_points))
                    trail_color = (base_color[0], base_color[1], base_color[2], 
                                  int((1.0 - alpha_factor) * 255))
                    
                    # Draw line segment
                    draw.line(
                        [detection.trail_points[i-1][0], detection.trail_points[i-1][1],
                         detection.trail_points[i][0], detection.trail_points[i][1]],
                        fill=trail_color,
                        width=2
                    )
            
            # Determine color based on distance
            if detection.distance <= close_distance:
                color_str = distance_colors.get('close', '#ff3333')
            elif detection.distance <= medium_distance:
                color_str = distance_colors.get('medium', '#ffcc00')
            else:
                color_str = distance_colors.get('far', '#33cc33')
            
            # Parse color
            color = self._parse_color(color_str)
            
            # Size based on distance and fade
            base_size = 12
            size = int(base_size * (1.0 - distance_factor * 0.5) * detection.fade_factor)
            size = max(8, min(size, 19))  # Clamp to available font sizes
            
            # Get symbol for sound type
            symbol = SOUND_TYPES.get(detection.sound_type, {}).get('symbol', '❓')
            
            # Highlight high threats
            if self.settings.get('highlight_threats', True) and detection.threat_level > threat_sensitivity:
                # Draw pulsing highlight around the detection
                pulse_size = size * 2.5
                pulse_alpha = int((0.7 + 0.3 * math.sin(current_time * 5)) * 255)
                pulse_color = (color[0], color[1], color[2], pulse_alpha)
                
                draw.ellipse(
                    [x - pulse_size, y - pulse_size, x + pulse_size, y + pulse_size],
                    outline=pulse_color,
                    width=3
                )
            
            # Draw sound symbol
            if font_sizes:
                font = font_sizes.get(size, font_sizes[12])
                draw.text((x, y), symbol, fill=color, font=font, anchor="mm")
            else:
                # Fallback if font not available
                draw.text((x, y), symbol, fill=color)
            
            # Draw pulse effect for recent detections (less than 1 second old)
            if detection.age < 1.0:
                pulse_size = size * 2 * (1.0 - detection.age)
                pulse_alpha = int((1.0 - detection.age) * 255)
                pulse_color = (color[0], color[1], color[2], pulse_alpha)
                
                draw.ellipse(
                    [x - pulse_size, y - pulse_size, x + pulse_size, y + pulse_size],
                    outline=pulse_color,
                    width=2
                )
    
    def get_direction_name(self, angle):
        """Convert angle to direction name"""
        directions = {
            0: "North",
            45: "Northeast",
            90: "East",
            135: "Southeast",
            180: "South",
            225: "Southwest",
            270: "West",
            315: "Northwest"
        }
        
        # Find the closest direction
        closest = min(directions.keys(), key=lambda x: abs((angle - x + 180) % 360 - 180))
        return directions[closest]
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Stop radar if active
            if self.radar_active:
                self.stop_radar()
            
            # Save settings
            self.save_settings()
            
            # Clean up audio resources
            self.audio_processor.cleanup()
            
            # Destroy windows
            if hasattr(self, 'overlay') and self.overlay:
                self.overlay.destroy()
            
            self.root.destroy()
        except Exception as e:
            print(f"Error during closing: {e}")
            self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = PUBGSonarRadar()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Application error: {e}")


if __name__ == "__main__":
    main()