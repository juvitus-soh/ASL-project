# # app/core/asl_engine.py
# """
# Updated ASL Recognition Engine with Real Model Integration
# Coordinates all ASL recognition components with actual model
# """
#
# import threading
# import time
# from typing import Optional, Tuple, List
# import numpy as np
# from collections import Counter
#
# try:
#     from .model_manager import ModelManager, ImageProcessor
#     from .speech_engine import SpeechEngine
#     from ..utils.constants import CONFIDENCE_THRESHOLD
#     from ..utils.logger import logger
# except ImportError as e:
#     print(f"Import warning: {e}")
#     # Fallback imports
#     logger = None
#     CONFIDENCE_THRESHOLD = 0.75
#
#     # Import the classes from the files we created
#     import sys
#     import os
#
#     sys.path.append(os.path.join(os.path.dirname(__file__)))
#
#     try:
#         from model_manager import ModelManager, ImageProcessor
#         from speech_engine import SpeechEngine
#     except ImportError:
#         # Create minimal fallbacks
#         class ModelManager:
#             def __init__(self):
#                 self.is_loaded = False
#
#             def predict(self, image):
#                 return None, 0.0
#
#             def is_model_loaded(self):
#                 return False
#
#             def get_model_info(self):
#                 return {'loaded': False}
#
#             def get_class_name(self, class_idx):
#                 return f"class_{class_idx}"
#
#             def preprocess_image(self, image):
#                 return np.zeros((1, 224, 224, 3))
#
#
#         class ImageProcessor:
#             @staticmethod
#             def preprocess_image(image, target_size=224):
#                 return np.zeros((1, 224, 224, 3))
#
#
#         class SpeechEngine:
#             def __init__(self):
#                 pass
#
#             def speak(self, text):
#                 print(f"TTS: {text}")
#
#             def set_enabled(self, enabled):
#                 pass
#
#             def update_settings(self, settings):
#                 pass
#
#
# class ASLEngine:
#     """Main ASL Recognition Engine with Real Model Integration"""
#
#     def __init__(self):
#         """Initialize the ASL recognition engine"""
#         print("🚀 Initializing ASL Engine...")
#
#         # Initialize components
#         self.model_manager = ModelManager()
#         self.image_processor = ImageProcessor()
#         self.speech_engine = SpeechEngine()
#
#         # Recognition state
#         self.is_running = False
#         self.current_prediction = None
#         self.current_confidence = 0.0
#         self.prediction_history = []
#
#         # Word building
#         self.current_word = ""
#         self.completed_sentence = ""
#         self.last_prediction_time = 0
#         self.prediction_cooldown = 1.0  # seconds between same predictions
#
#         # Settings
#         self.confidence_threshold = CONFIDENCE_THRESHOLD
#         self.prediction_smoothing = True
#         self.auto_word_completion = True
#         self.letter_hold_time = 1.5  # seconds to hold a letter before adding
#
#         # Statistics tracking
#         self._total_predictions = 0
#         self._successful_predictions = 0
#         self._avg_confidence = 0.0
#         self._accuracy_rate = 0.0
#         self._last_prediction_time = None
#
#         # Threading
#         self.lock = threading.Lock()
#
#         # Check model status
#         model_info = self.model_manager.get_model_info()
#         if model_info['loaded']:
#             print(f"✅ ASL Engine initialized with {model_info['type']} model")
#             print(f"   Classes: {model_info['num_classes']}")
#             print(f"   Input shape: {model_info['input_shape']}")
#         else:
#             print("⚠️ ASL Engine initialized but no model loaded")
#             print("   Place your trained model in assets/models/")
#
#         if logger:
#             logger.info("ASL Engine initialized")
#
#     def start_recognition(self):
#         """Start ASL recognition"""
#         if not self.is_running:
#             self.is_running = True
#             print("🎯 ASL recognition started")
#             if logger:
#                 logger.info("ASL recognition started")
#
#     def stop_recognition(self):
#         """Stop ASL recognition"""
#         if self.is_running:
#             self.is_running = False
#             print("⏹️ ASL recognition stopped")
#             if logger:
#                 logger.info("ASL recognition stopped")
#
#     def process_frame(self, frame) -> Tuple[Optional[str], float]:
#         """Process a single frame for ASL recognition"""
#         if not self.is_running or frame is None:
#             return None, 0.0
#
#         if not self.model_manager.is_model_loaded():
#             return None, 0.0
#
#         try:
#             # Preprocess the image using the model manager
#             processed_image = self.model_manager.preprocess_image(frame)
#
#             # Make prediction
#             class_idx, confidence = self.model_manager.predict(processed_image)
#
#             # Update statistics
#             was_successful = class_idx is not None and confidence > self.confidence_threshold
#             self._update_stats(confidence, was_successful)
#
#             if class_idx is not None and confidence > self.confidence_threshold:
#                 predicted_letter = self.model_manager.get_class_name(class_idx)
#
#                 # Update prediction history for smoothing
#                 if self.prediction_smoothing:
#                     self.prediction_history.append(predicted_letter)
#                     if len(self.prediction_history) > 15:
#                         self.prediction_history.pop(0)
#
#                     # Use most common prediction from recent history
#                     if len(self.prediction_history) >= 5:
#                         most_common = Counter(self.prediction_history).most_common(1)
#                         if most_common:
#                             predicted_letter = most_common[0][0]
#
#                 # Update current prediction
#                 with self.lock:
#                     self.current_prediction = predicted_letter
#                     self.current_confidence = confidence
#
#                 # Auto-add letters based on time held
#                 current_time = time.time()
#                 if (predicted_letter != 'nothing' and
#                         current_time - self.last_prediction_time > self.letter_hold_time):
#                     self.add_letter_to_word(predicted_letter)
#                     self.last_prediction_time = current_time
#
#                 return predicted_letter, confidence
#             else:
#                 # Clear prediction if confidence too low
#                 with self.lock:
#                     if confidence <= self.confidence_threshold:
#                         self.current_prediction = None
#                         self.current_confidence = 0.0
#
#         except Exception as e:
#             print(f"❌ Error processing frame: {e}")
#             if logger:
#                 logger.error(f"Error processing frame: {e}")
#
#         return None, 0.0
#
#     def add_letter_to_word(self, letter: str):
#         """Add a letter to the current word"""
#         if not letter or letter == 'nothing':
#             return
#
#         with self.lock:
#             if letter == 'space':
#                 self.complete_word()
#             elif letter == 'del':
#                 self.backspace()
#             else:
#                 # Only add if it's different from the last letter
#                 if not self.current_word or self.current_word[-1] != letter.upper():
#                     self.current_word += letter.upper()
#                     print(f"📝 Added letter: {letter}, current word: {self.current_word}")
#                     if logger:
#                         logger.debug(f"Added letter: {letter}, current word: {self.current_word}")
#
#     def complete_word(self):
#         """Complete the current word and add to sentence"""
#         with self.lock:
#             if self.current_word:
#                 if self.completed_sentence:
#                     self.completed_sentence += " " + self.current_word
#                 else:
#                     self.completed_sentence = self.current_word
#
#                 print(f"✅ Word completed: {self.current_word}")
#                 print(f"📄 Sentence: {self.completed_sentence}")
#
#                 if logger:
#                     logger.info(f"Word completed: {self.current_word}")
#
#                 self.current_word = ""
#
#     def backspace(self):
#         """Remove the last letter from current word or last word from sentence"""
#         with self.lock:
#             if self.current_word:
#                 self.current_word = self.current_word[:-1]
#                 print(f"⬅️ Backspace, current word: {self.current_word}")
#                 if logger:
#                     logger.debug(f"Backspace, current word: {self.current_word}")
#             elif self.completed_sentence:
#                 # Remove last word from sentence
#                 words = self.completed_sentence.split()
#                 if words:
#                     self.current_word = words[-1]
#                     self.completed_sentence = " ".join(words[:-1])
#                     print(f"⬅️ Moved last word back to editing: {self.current_word}")
#
#     def speak_current_sentence(self):
#         """Speak the current sentence"""
#         with self.lock:
#             text_to_speak = self.completed_sentence
#             if self.current_word:
#                 if text_to_speak:
#                     text_to_speak += " " + self.current_word
#                 else:
#                     text_to_speak = self.current_word
#
#         if text_to_speak:
#             print(f"🔊 Speaking: {text_to_speak}")
#             self.speech_engine.speak(text_to_speak)
#             if logger:
#                 logger.info(f"Speaking: {text_to_speak}")
#         else:
#             print("🔇 Nothing to speak")
#
#     def clear_all(self):
#         """Clear current word and sentence"""
#         with self.lock:
#             self.current_word = ""
#             self.completed_sentence = ""
#             self.prediction_history.clear()
#             print("🗑️ Cleared all text")
#             if logger:
#                 logger.info("Cleared all text")
#
#     def get_current_word(self) -> str:
#         """Get the current word being built"""
#         with self.lock:
#             return self.current_word
#
#     def get_completed_sentence(self) -> str:
#         """Get the completed sentence"""
#         with self.lock:
#             return self.completed_sentence
#
#     def get_full_text(self) -> str:
#         """Get the full text (sentence + current word)"""
#         with self.lock:
#             if self.completed_sentence and self.current_word:
#                 return f"{self.completed_sentence} {self.current_word}"
#             elif self.completed_sentence:
#                 return self.completed_sentence
#             elif self.current_word:
#                 return self.current_word
#             else:
#                 return ""
#
#     def get_current_prediction(self) -> Tuple[Optional[str], float]:
#         """Get the current prediction and confidence"""
#         with self.lock:
#             return self.current_prediction, self.current_confidence
#
#     def update_settings(self, settings: dict):
#         """Update engine settings"""
#         self.confidence_threshold = settings.get('confidence_threshold', self.confidence_threshold)
#         self.prediction_smoothing = settings.get('prediction_smoothing', self.prediction_smoothing)
#         self.auto_word_completion = settings.get('auto_word_completion', self.auto_word_completion)
#         self.letter_hold_time = settings.get('letter_hold_time', self.letter_hold_time)
#
#         # Update speech engine settings
#         speech_settings = {
#             'enabled': settings.get('speech_enabled', True),
#             'rate': settings.get('speech_rate', 150),
#             'volume': settings.get('speech_volume', 0.8)
#         }
#         self.speech_engine.update_settings(speech_settings)
#
#         print("⚙️ Engine settings updated")
#         if logger:
#             logger.info("Engine settings updated")
#
#     def get_model_status(self) -> bool:
#         """Check if the model is loaded and ready"""
#         return self.model_manager.is_model_loaded()
#
#     def get_model_info(self) -> dict:
#         """Get detailed model information"""
#         return self.model_manager.get_model_info()
#
#     def get_statistics(self) -> dict:
#         """Get recognition statistics"""
#         with self.lock:
#             model_info = self.get_model_info()
#             return {
#                 'current_word': self.current_word,
#                 'completed_sentence': self.completed_sentence,
#                 'full_text': self.get_full_text(),
#                 'last_prediction': self.current_prediction,
#                 'last_confidence': self.current_confidence,
#                 'is_running': self.is_running,
#                 'model_loaded': model_info['loaded'],
#                 'model_type': model_info.get('type', 'none'),
#                 'total_letters': len(self.current_word) + len(self.completed_sentence.replace(' ', '')),
#                 'confidence_threshold': self.confidence_threshold,
#                 'prediction_smoothing': self.prediction_smoothing
#             }
#
#     def manual_add_letter(self, letter: str):
#         """Manually add a letter (for testing or manual input)"""
#         self.add_letter_to_word(letter)
#
#     def set_confidence_threshold(self, threshold: float):
#         """Set the confidence threshold"""
#         self.confidence_threshold = max(0.1, min(1.0, threshold))
#         print(f"🎯 Confidence threshold set to {self.confidence_threshold}")
#
#     def get_prediction_stats(self):
#         """Get prediction statistics for settings/debugging"""
#         if not self.model_manager.is_model_loaded():
#             return {
#                 'total_predictions': 0,
#                 'average_confidence': 0.0,
#                 'successful_predictions': 0,
#                 'accuracy_rate': 0.0,
#                 'last_prediction_time': None
#             }
#
#         model_info = self.get_model_info()
#         return {
#             'total_predictions': self._total_predictions,
#             'average_confidence': self._avg_confidence,
#             'successful_predictions': self._successful_predictions,
#             'accuracy_rate': self._accuracy_rate,
#             'last_prediction_time': self._last_prediction_time,
#             'model_type': model_info.get('type', 'keras'),
#             'model_classes': model_info.get('num_classes', 0),
#             'input_shape': model_info.get('input_shape', '(224, 224, 3)')
#         }
#
#     def reset_stats(self):
#         """Reset prediction statistics"""
#         self._total_predictions = 0
#         self._successful_predictions = 0
#         self._avg_confidence = 0.0
#         self._accuracy_rate = 0.0
#         self._last_prediction_time = None
#         print("📊 Prediction statistics reset")
#         if logger:
#             logger.info("Prediction statistics reset")
#
#     def _update_stats(self, confidence, was_successful=True):
#         """Update prediction statistics (call this after each prediction)"""
#         self._total_predictions += 1
#         if was_successful:
#             self._successful_predictions += 1
#
#         # Update running average of confidence
#         self._avg_confidence = ((self._avg_confidence * (
#                     self._total_predictions - 1)) + confidence) / self._total_predictions
#
#         # Update accuracy rate
#         self._accuracy_rate = (
#                                           self._successful_predictions / self._total_predictions) * 100 if self._total_predictions > 0 else 0.0
#
#         # Update last prediction time
#         self._last_prediction_time = time.time()
#
#
# # Helper function for testing
# def test_asl_engine():
#     """Test the ASL engine"""
#     print("🧪 Testing ASL Engine...")
#
#     engine = ASLEngine()
#     stats = engine.get_statistics()
#
#     print(f"Model loaded: {stats['model_loaded']}")
#     print(f"Model type: {stats['model_type']}")
#
#     if stats['model_loaded']:
#         print("✅ ASL Engine test passed - model loaded!")
#     else:
#         print("⚠️ ASL Engine working but no model loaded")
#         print("   Copy your trained model to assets/models/best_model.h5")
#
#     # Test prediction statistics
#     pred_stats = engine.get_prediction_stats()
#     print(f"📊 Prediction stats: {pred_stats}")
#
#
# if __name__ == "__main__":
#     test_asl_engine()

# !/usr/bin/env python3
"""
ASL Engine - Sign language recognition engine
"""

import os
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import TensorFlow (with fallbacks for different environments)
TENSORFLOW_AVAILABLE = False
MODEL_TYPE = None

try:
    # Try TensorFlow Lite first (mobile-optimized)
    import tensorflow.lite as tflite

    TENSORFLOW_AVAILABLE = True
    MODEL_TYPE = 'tflite'
    print("✅ TensorFlow Lite available")
except ImportError:
    try:
        # Fallback to full TensorFlow
        import tensorflow as tf

        TENSORFLOW_AVAILABLE = True
        MODEL_TYPE = 'tensorflow'
        print("✅ TensorFlow available")
    except ImportError:
        print("⚠️ TensorFlow not available - using demo mode")

# Try to import OpenCV for image processing
try:
    import cv2

    OPENCV_AVAILABLE = True
    print("✅ OpenCV available")
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV not available - using PIL fallback")

# Fallback to PIL for basic image processing
try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("❌ Neither OpenCV nor PIL available")


class ASLEngine:
    """ASL Sign Language Recognition Engine"""

    def __init__(self):
        """Initialize the ASL recognition engine"""

        # Model state
        self.model = None
        self.model_loaded = False
        self.model_path = None
        self.model_type = None

        # Model info
        self.input_shape = (224, 224, 3)  # Default input shape
        self.num_classes = 29  # A-Z + space + delete + nothing
        self.class_names = self.get_default_class_names()

        # Prediction state
        self.last_prediction = None
        self.last_confidence = 0.0
        self.prediction_history = []

        # Demo mode
        self.demo_mode = not TENSORFLOW_AVAILABLE
        self.demo_index = 0

        print("🚀 ASL Engine initialized")
        if self.demo_mode:
            print("🎭 Running in demo mode (no TensorFlow)")

    def get_default_class_names(self) -> List[str]:
        """Get default class names for ASL alphabet"""
        # Standard ASL alphabet + special characters
        alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        special = ['SPACE', 'DELETE', 'NOTHING']
        return alphabet + special

    def load_model(self, model_path: str) -> bool:
        """
        Load ASL recognition model

        Args:
            model_path: Path to the model file

        Returns:
            bool: True if loaded successfully
        """
        if self.demo_mode:
            print("🎭 Demo mode: Simulating model load")
            self.model_loaded = True
            self.model_path = model_path
            self.model_type = 'demo'
            return True

        try:
            model_file = Path(model_path)

            if not model_file.exists():
                print(f"❌ Model file not found: {model_path}")
                return False

            print(f"📥 Loading model from {model_path}")

            # Determine model type and load accordingly
            if model_path.endswith('.tflite') and MODEL_TYPE == 'tflite':
                success = self._load_tflite_model(model_path)
            elif model_path.endswith('.h5') and MODEL_TYPE == 'tensorflow':
                success = self._load_keras_model(model_path)
            else:
                print(f"⚠️ Unsupported model format or TensorFlow not available")
                return False

            if success:
                self.model_loaded = True
                self.model_path = model_path
                print(f"✅ Model loaded successfully!")
                print(f"   Input shape: {self.input_shape}")
                print(f"   Classes: {self.num_classes}")
                return True
            else:
                print("❌ Model loading failed")
                return False

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            logger.error(f"Model loading error: {e}")
            return False

    def _load_tflite_model(self, model_path: str) -> bool:
        """Load TensorFlow Lite model"""
        try:
            self.model = tflite.Interpreter(model_path=model_path)
            self.model.allocate_tensors()

            # Get input and output details
            input_details = self.model.get_input_details()
            output_details = self.model.get_output_details()

            # Update input shape from model
            self.input_shape = input_details[0]['shape'][1:4]  # Remove batch dimension
            self.num_classes = output_details[0]['shape'][1]
            self.model_type = 'tflite'

            print(f"✅ TensorFlow Lite model loaded")
            return True

        except Exception as e:
            print(f"❌ TensorFlow Lite loading failed: {e}")
            return False

    def _load_keras_model(self, model_path: str) -> bool:
        """Load Keras/TensorFlow model"""
        try:
            import tensorflow as tf

            self.model = tf.keras.models.load_model(model_path)

            # Get model info
            input_shape = self.model.input_shape
            self.input_shape = input_shape[1:4]  # Remove batch dimension
            self.num_classes = self.model.output_shape[1]
            self.model_type = 'keras'

            print(f"✅ Keras model loaded")
            return True

        except Exception as e:
            print(f"❌ Keras loading failed: {e}")
            return False

    def preprocess_image(self, image_data) -> Optional[np.ndarray]:
        """
        Preprocess image for model input

        Args:
            image_data: Input image (numpy array, PIL Image, or file path)

        Returns:
            Preprocessed image array or None if failed
        """
        try:
            # Handle different input types
            if isinstance(image_data, str):
                # File path
                if OPENCV_AVAILABLE:
                    image = cv2.imread(image_data)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                elif PIL_AVAILABLE:
                    image = np.array(Image.open(image_data))
                else:
                    print("❌ No image processing library available")
                    return None
            elif isinstance(image_data, np.ndarray):
                # Numpy array
                image = image_data
            elif PIL_AVAILABLE and hasattr(image_data, 'save'):
                # PIL Image
                image = np.array(image_data)
            else:
                print("❌ Unsupported image format")
                return None

            # Resize to model input size
            target_size = self.input_shape[:2]  # (height, width)

            if OPENCV_AVAILABLE:
                image = cv2.resize(image, target_size)
            elif PIL_AVAILABLE:
                pil_image = Image.fromarray(image)
                pil_image = pil_image.resize(target_size)
                image = np.array(pil_image)
            else:
                # Basic resize (not ideal but functional)
                print("⚠️ Using basic image resize")

            # Normalize pixel values
            image = image.astype(np.float32) / 255.0

            # Add batch dimension
            image = np.expand_dims(image, axis=0)

            return image

        except Exception as e:
            print(f"❌ Image preprocessing failed: {e}")
            return None

    def predict(self, image_data) -> Optional[Tuple[str, float]]:
        """
        Predict ASL sign from image

        Args:
            image_data: Input image

        Returns:
            Tuple of (predicted_class, confidence) or None if failed
        """
        if self.demo_mode:
            return self._demo_predict()

        if not self.model_loaded:
            print("❌ Model not loaded")
            return None

        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            if processed_image is None:
                return None

            # Make prediction
            if self.model_type == 'tflite':
                prediction = self._predict_tflite(processed_image)
            elif self.model_type == 'keras':
                prediction = self._predict_keras(processed_image)
            else:
                print("❌ Unknown model type")
                return None

            if prediction is None:
                return None

            # Get class and confidence
            class_index = np.argmax(prediction)
            confidence = float(prediction[class_index])

            # Get class name
            if class_index < len(self.class_names):
                class_name = self.class_names[class_index]
            else:
                class_name = f"CLASS_{class_index}"

            # Store prediction
            self.last_prediction = class_name
            self.last_confidence = confidence

            # Add to history
            self.prediction_history.append({
                'class': class_name,
                'confidence': confidence,
                'timestamp': np.datetime64('now')
            })

            # Keep history limited
            if len(self.prediction_history) > 100:
                self.prediction_history = self.prediction_history[-50:]

            return class_name, confidence

        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            logger.error(f"Prediction error: {e}")
            return None

    def _predict_tflite(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Make prediction using TensorFlow Lite model"""
        try:
            input_details = self.model.get_input_details()
            output_details = self.model.get_output_details()

            # Set input tensor
            self.model.set_tensor(input_details[0]['index'], image)

            # Run inference
            self.model.invoke()

            # Get output
            output_data = self.model.get_tensor(output_details[0]['index'])
            return output_data[0]  # Remove batch dimension

        except Exception as e:
            print(f"❌ TensorFlow Lite prediction failed: {e}")
            return None

    def _predict_keras(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Make prediction using Keras model"""
        try:
            prediction = self.model.predict(image, verbose=0)
            return prediction[0]  # Remove batch dimension

        except Exception as e:
            print(f"❌ Keras prediction failed: {e}")
            return None

    def _demo_predict(self) -> Tuple[str, float]:
        """Generate demo predictions for testing"""
        # Cycle through letters for demo
        demo_letters = ['C', 'N', 'J', 'G', 'O', 'W', 'M', 'F', 'B', 'A', 'E', 'I', 'L', 'R', 'S', 'T']

        letter = demo_letters[self.demo_index % len(demo_letters)]
        confidence = 0.85 + (np.random.random() * 0.14)  # Random confidence 0.85-0.99

        self.demo_index += 1

        return letter, confidence

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model

        Returns:
            Dict containing model information
        """
        return {
            'loaded': self.model_loaded,
            'path': self.model_path,
            'type': self.model_type,
            'input_shape': self.input_shape,
            'classes': self.num_classes,
            'class_names': self.class_names[:10],  # First 10 for brevity
            'demo_mode': self.demo_mode,
            'last_prediction': self.last_prediction,
            'last_confidence': self.last_confidence,
            'prediction_count': len(self.prediction_history)
        }

    def get_prediction_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent prediction history

        Args:
            limit: Maximum number of predictions to return

        Returns:
            List of recent predictions
        """
        return self.prediction_history[-limit:] if self.prediction_history else []

    def clear_history(self):
        """Clear prediction history"""
        self.prediction_history.clear()
        print("🗑️ Prediction history cleared")

    def get_class_distribution(self) -> Dict[str, int]:
        """Get distribution of predicted classes from history"""
        if not self.prediction_history:
            return {}

        distribution = {}
        for pred in self.prediction_history:
            class_name = pred['class']
            distribution[class_name] = distribution.get(class_name, 0) + 1

        return distribution

    def cleanup(self):
        """Clean up the ASL engine"""
        try:
            if self.model and hasattr(self.model, 'close'):
                self.model.close()

            self.model = None
            self.model_loaded = False
            print("🔧 ASL Engine cleaned up")

        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")