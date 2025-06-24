# app/core/model_manager.py
"""
Model Manager for ASL Recognition
Loads and manages the trained ASL recognition model
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List
import threading

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Install with: pip install tensorflow")

try:
    from ..utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class ModelManager:
    """Manages the ASL recognition model"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the model manager
        
        Args:
            model_path: Path to the model file. If None, will search for models.
        """
        self.model = None
        self.model_path = model_path
        self.is_loaded = False
        self.model_type = None  # 'keras' or 'tflite'
        self.input_shape = (224, 224, 3)  # Default input shape
        self.class_names = self._get_asl_classes()
        self.load_lock = threading.Lock()
        
        # Model loading
        if TENSORFLOW_AVAILABLE:
            self._find_and_load_model()
        else:
            logger.error("TensorFlow not available - cannot load model")
    
    def _get_asl_classes(self) -> List[str]:
        """Get the ASL class names"""
        # Standard ASL alphabet + special commands
        return [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'space', 'del', 'nothing'
        ]
    
    def _find_and_load_model(self):
        """Find and load the best available model"""
        if self.model_path:
            model_paths = [Path(self.model_path)]
        else:
            # Search for models in common locations
            possible_paths = [
                Path("assets/models/best_model.h5"),
                Path("assets/models/best_model.tflite"),
                Path("models/best_model.h5"),
                Path("models/best_model.tflite"),
                Path("best_model.h5"),
                Path("best_model.tflite")
            ]
            model_paths = [p for p in possible_paths if p.exists()]
        
        if not model_paths:
            logger.error("No model files found!")
            return
        
        # Prefer .h5 files for better accuracy, .tflite for speed
        keras_models = [p for p in model_paths if p.suffix == '.h5']
        tflite_models = [p for p in model_paths if p.suffix == '.tflite']
        
        if keras_models:
            self._load_keras_model(keras_models[0])
        elif tflite_models:
            self._load_tflite_model(tflite_models[0])
    
    def _load_keras_model(self, model_path: Path):
        """Load a Keras model"""
        try:
            logger.info(f"Loading Keras model from {model_path}")
            with self.load_lock:
                self.model = keras.models.load_model(str(model_path))
                self.model_type = 'keras'
                self.is_loaded = True
                
                # Get input shape from model
                if hasattr(self.model, 'input_shape'):
                    shape = self.model.input_shape
                    if len(shape) >= 4:
                        self.input_shape = shape[1:4]  # Remove batch dimension
                
                logger.info(f"✅ Keras model loaded successfully!")
                logger.info(f"   Input shape: {self.input_shape}")
                logger.info(f"   Classes: {len(self.class_names)}")
                
        except Exception as e:
            logger.error(f"Error loading Keras model: {e}")
            self.is_loaded = False
    
    def _load_tflite_model(self, model_path: Path):
        """Load a TensorFlow Lite model"""
        try:
            logger.info(f"Loading TFLite model from {model_path}")
            with self.load_lock:
                self.interpreter = tf.lite.Interpreter(model_path=str(model_path))
                self.interpreter.allocate_tensors()
                
                # Get input and output details
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                
                # Get input shape
                input_shape = self.input_details[0]['shape']
                if len(input_shape) >= 4:
                    self.input_shape = tuple(input_shape[1:4])  # Remove batch dimension
                
                self.model_type = 'tflite'
                self.is_loaded = True
                
                logger.info(f"✅ TFLite model loaded successfully!")
                logger.info(f"   Input shape: {self.input_shape}")
                logger.info(f"   Classes: {len(self.class_names)}")
                
        except Exception as e:
            logger.error(f"Error loading TFLite model: {e}")
            self.is_loaded = False
    
    def predict(self, image: np.ndarray) -> Tuple[Optional[int], float]:
        """Make a prediction on an image
        
        Args:
            image: Preprocessed image array of shape (1, height, width, 3)
            
        Returns:
            Tuple of (class_index, confidence) or (None, 0.0) if error
        """
        if not self.is_loaded or image is None:
            return None, 0.0
        
        try:
            with self.load_lock:
                if self.model_type == 'keras':
                    predictions = self.model.predict(image, verbose=0)
                elif self.model_type == 'tflite':
                    # Set input tensor
                    self.interpreter.set_tensor(self.input_details[0]['index'], image.astype(np.float32))
                    
                    # Run inference
                    self.interpreter.invoke()
                    
                    # Get output
                    predictions = self.interpreter.get_tensor(self.output_details[0]['index'])
                else:
                    return None, 0.0
                
                # Get the predicted class and confidence
                if len(predictions.shape) > 1:
                    predictions = predictions[0]  # Remove batch dimension
                
                class_idx = np.argmax(predictions)
                confidence = float(predictions[class_idx])
                
                # Ensure class index is within bounds
                if 0 <= class_idx < len(self.class_names):
                    return int(class_idx), confidence
                else:
                    logger.warning(f"Predicted class index {class_idx} out of bounds")
                    return None, 0.0
                    
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return None, 0.0
    
    def get_class_name(self, class_idx: int) -> str:
        """Get class name from index"""
        if 0 <= class_idx < len(self.class_names):
            return self.class_names[class_idx]
        return "unknown"
    
    def predict_with_name(self, image: np.ndarray) -> Tuple[Optional[str], float]:
        """Make a prediction and return class name
        
        Args:
            image: Preprocessed image array
            
        Returns:
            Tuple of (class_name, confidence) or (None, 0.0) if error
        """
        class_idx, confidence = self.predict(image)
        if class_idx is not None:
            class_name = self.get_class_name(class_idx)
            return class_name, confidence
        return None, 0.0
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.is_loaded
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            'loaded': self.is_loaded,
            'type': self.model_type,
            'input_shape': self.input_shape,
            'num_classes': len(self.class_names),
            'classes': self.class_names,
            'tensorflow_available': TENSORFLOW_AVAILABLE
        }
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for model input
        
        Args:
            image: Raw image array (H, W, 3)
            
        Returns:
            Preprocessed image array (1, H, W, 3)
        """
        try:
            # Ensure image is the right shape
            if len(image.shape) == 4:
                image = image[0]  # Remove batch dimension if present
            
            # Resize to model input shape
            target_height, target_width = self.input_shape[:2]
            
            if TENSORFLOW_AVAILABLE:
                # Use TensorFlow for resizing
                image_resized = tf.image.resize(image, [target_height, target_width])
                image_resized = tf.cast(image_resized, tf.float32)
                
                # Normalize to [0, 1]
                image_normalized = image_resized / 255.0
                
                # Add batch dimension
                image_batch = tf.expand_dims(image_normalized, 0)
                
                return image_batch.numpy()
            else:
                # Fallback to basic processing
                import cv2
                image_resized = cv2.resize(image, (target_width, target_height))
                image_normalized = image_resized.astype(np.float32) / 255.0
                image_batch = np.expand_dims(image_normalized, axis=0)
                return image_batch
                
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            # Return a zero array with correct shape
            return np.zeros((1, *self.input_shape), dtype=np.float32)

# Image processor for compatibility
class ImageProcessor:
    """Image processor for ASL recognition"""
    
    def __init__(self):
        self.target_size = 224
    
    @staticmethod
    def preprocess_image(image: np.ndarray, target_size: int = 224) -> np.ndarray:
        """Preprocess image for model input"""
        try:
            if TENSORFLOW_AVAILABLE:
                # Ensure image is the right type
                if image.dtype != np.float32:
                    image = image.astype(np.float32)
                
                # Resize image
                image_resized = tf.image.resize(image, [target_size, target_size])
                
                # Normalize to [0, 1]
                image_normalized = image_resized / 255.0
                
                # Add batch dimension
                image_batch = tf.expand_dims(image_normalized, 0)
                
                return image_batch.numpy()
            else:
                # Fallback processing
                import cv2
                if len(image.shape) == 4:
                    image = image[0]
                image_resized = cv2.resize(image, (target_size, target_size))
                image_normalized = image_resized.astype(np.float32) / 255.0
                return np.expand_dims(image_normalized, axis=0)
                
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return np.zeros((1, target_size, target_size, 3), dtype=np.float32)