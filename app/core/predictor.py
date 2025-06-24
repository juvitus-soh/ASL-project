"""
ASL prediction engine for trained models
Author: [Your Name] - MSc Thesis
"""

import os
import numpy as np
import tensorflow as tf
import cv2
from typing import Optional, Tuple, List, Dict, Any

from src.config import Config
from src.utils.logger import get_logger


class ASLPredictor:
    """ASL sign prediction using trained models"""

    def __init__(self, config: Config):
        """
        Initialize ASL predictor

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.model = None
        self.model_loaded = False

        # Performance tracking
        self.prediction_count = 0
        self.total_inference_time = 0.0

        self.logger.info("🔮 ASL predictor initialized")

    def load_model(self, model_path: str) -> bool:
        """
        Load trained ASL model

        Args:
            model_path: Path to saved model file

        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(model_path):
                self.logger.error(f"❌ Model file not found: {model_path}")
                return False

            self.logger.info(f"📥 Loading model from: {model_path}")

            # Load model
            self.model = tf.keras.models.load_model(model_path)
            self.model_loaded = True

            # Print model info
            self._print_model_info()

            self.logger.info("✅ Model loaded successfully!")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to load model: {e}")
            self.model_loaded = False
            return False

    def load_tflite_model(self, tflite_path: str) -> bool:
        """
        Load TensorFlow Lite model for edge deployment

        Args:
            tflite_path: Path to TFLite model file

        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(tflite_path):
                self.logger.error(f"❌ TFLite model file not found: {tflite_path}")
                return False

            self.logger.info(f"📱 Loading TFLite model from: {tflite_path}")

            # Initialize TFLite interpreter
            self.interpreter = tf.lite.Interpreter(model_path=tflite_path)
            self.interpreter.allocate_tensors()

            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            self.model_loaded = True
            self.is_tflite = True

            self.logger.info("✅ TFLite model loaded successfully!")
            self.logger.info(f"📊 Input shape: {self.input_details[0]['shape']}")
            self.logger.info(f"📊 Output shape: {self.output_details[0]['shape']}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to load TFLite model: {e}")
            self.model_loaded = False
            return False

    def predict(self, input_data: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Make prediction on input data

        Args:
            input_data: Preprocessed input data

        Returns:
            Tuple of (predicted_class, confidence)
        """
        try:
            if not self.model_loaded:
                self.logger.warning("⚠️ No model loaded")
                return None, 0.0

            import time
            start_time = time.time()

            # Make prediction based on model type
            if hasattr(self, 'is_tflite') and self.is_tflite:
                predictions = self._predict_tflite(input_data)
            else:
                predictions = self._predict_keras(input_data)

            # Calculate inference time
            inference_time = time.time() - start_time
            self.total_inference_time += inference_time
            self.prediction_count += 1

            if predictions is not None:
                # Get predicted class and confidence
                predicted_class_idx = np.argmax(predictions)
                confidence = np.max(predictions)

                # Map to class label
                if predicted_class_idx < len(self.config.class_labels):
                    predicted_class = self.config.class_labels[predicted_class_idx]
                    return predicted_class, float(confidence)

            return None, 0.0

        except Exception as e:
            self.logger.error(f"❌ Prediction failed: {e}")
            return None, 0.0

    def _predict_keras(self, input_data: np.ndarray) -> Optional[np.ndarray]:
        """
        Make prediction using Keras model

        Args:
            input_data: Input data array

        Returns:
            Prediction probabilities or None if failed
        """
        try:
            predictions = self.model.predict(input_data, verbose=0)
            return predictions[0]  # Remove batch dimension

        except Exception as e:
            self.logger.error(f"❌ Keras prediction failed: {e}")
            return None

    def _predict_tflite(self, input_data: np.ndarray) -> Optional[np.ndarray]:
        """
        Make prediction using TensorFlow Lite model

        Args:
            input_data: Input data array

        Returns:
            Prediction probabilities or None if failed
        """
        try:
            # Set input tensor
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

            # Run inference
            self.interpreter.invoke()

            # Get output
            predictions = self.interpreter.get_tensor(self.output_details[0]['index'])
            return predictions[0]  # Remove batch dimension

        except Exception as e:
            self.logger.error(f"❌ TFLite prediction failed: {e}")
            return None

    def predict_from_image(self, image_path: str) -> Tuple[Optional[str], float]:
        """
        Make prediction from image file

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (predicted_class, confidence)
        """
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"❌ Image file not found: {image_path}")
                return None, 0.0

            # Load and preprocess image
            preprocessed = self._preprocess_image(image_path)

            if preprocessed is not None:
                # Make prediction
                prediction, confidence = self.predict(preprocessed)

                if prediction:
                    self.logger.info(f"🎯 Prediction: {prediction} (confidence: {confidence:.4f})")

                    # Get top predictions for additional info
                    top_predictions = self.get_top_predictions(preprocessed, k=3)
                    if top_predictions:
                        self.logger.info("📊 Top 3 predictions:")
                        for i, (pred, conf) in enumerate(top_predictions):
                            self.logger.info(f"   {i + 1}. {pred}: {conf:.4f}")

                return prediction, confidence

            return None, 0.0

        except Exception as e:
            self.logger.error(f"❌ Image prediction failed: {e}")
            return None, 0.0

    def _preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Preprocess image for model input

        Args:
            image_path: Path to image file

        Returns:
            Preprocessed image array or None if failed
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"❌ Failed to load image: {image_path}")
                return None

            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Resize to model input size
            image = cv2.resize(image, (self.config.model.input_size, self.config.model.input_size))

            # Normalize pixel values
            image = image.astype(np.float32) / 255.0

            # Add batch dimension
            image = np.expand_dims(image, axis=0)

            return image

        except Exception as e:
            self.logger.error(f"❌ Image preprocessing failed: {e}")
            return None

    def get_top_predictions(self, input_data: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Get top k predictions with confidence scores

        Args:
            input_data: Preprocessed input data
            k: Number of top predictions to return

        Returns:
            List of (class_name, confidence) tuples
        """
        try:
            if not self.model_loaded:
                return []

            # Get predictions
            if hasattr(self, 'is_tflite') and self.is_tflite:
                predictions = self._predict_tflite(input_data)
            else:
                predictions = self._predict_keras(input_data)

            if predictions is None:
                return []

            # Get top k indices
            top_k_indices = np.argsort(predictions)[-k:][::-1]

            # Create results
            results = []
            for idx in top_k_indices:
                if idx < len(self.config.class_labels):
                    class_name = self.config.class_labels[idx]
                    confidence = float(predictions[idx])
                    results.append((class_name, confidence))

            return results

        except Exception as e:
            self.logger.error(f"❌ Top predictions failed: {e}")
            return []

    def predict_batch(self, batch_data: np.ndarray) -> List[Tuple[Optional[str], float]]:
        """
        Make predictions on batch of data

        Args:
            batch_data: Batch of preprocessed input data

        Returns:
            List of (predicted_class, confidence) tuples
        """
        try:
            if not self.model_loaded:
                return []

            results = []

            # Process each item in batch
            for i in range(batch_data.shape[0]):
                single_input = np.expand_dims(batch_data[i], axis=0)
                prediction, confidence = self.predict(single_input)
                results.append((prediction, confidence))

            return results

        except Exception as e:
            self.logger.error(f"❌ Batch prediction failed: {e}")
            return []

    def _print_model_info(self):
        """Print information about loaded model"""
        if self.model is None:
            return

        try:
            self.logger.info("📊 Model Information:")
            self.logger.info(f"   Input shape: {self.model.input_shape}")
            self.logger.info(f"   Output shape: {self.model.output_shape}")
            self.logger.info(f"   Parameters: {self.model.count_params():,}")
            self.logger.info(f"   Layers: {len(self.model.layers)}")

            # Model size estimation
            param_size = self.model.count_params() * 4 / (1024 * 1024)  # 4 bytes per parameter
            self.logger.info(f"   Estimated size: ~{param_size:.1f} MB")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to print model info: {e}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get prediction performance statistics

        Returns:
            Dictionary with performance metrics
        """
        stats = {
            'prediction_count': self.prediction_count,
            'total_inference_time': self.total_inference_time,
            'average_inference_time': 0.0,
            'predictions_per_second': 0.0
        }

        if self.prediction_count > 0:
            stats['average_inference_time'] = self.total_inference_time / self.prediction_count
            stats['predictions_per_second'] = self.prediction_count / self.total_inference_time

        return stats

    def reset_stats(self):
        """Reset performance statistics"""
        self.prediction_count = 0
        self.total_inference_time = 0.0
        self.logger.info("📊 Performance statistics reset")

    def is_model_loaded(self) -> bool:
        """
        Check if model is loaded

        Returns:
            True if model is loaded, False otherwise
        """
        return self.model_loaded

    def get_class_probabilities(self, input_data: np.ndarray) -> Optional[Dict[str, float]]:
        """
        Get prediction probabilities for all classes

        Args:
            input_data: Preprocessed input data

        Returns:
            Dictionary mapping class names to probabilities
        """
        try:
            if not self.model_loaded:
                return None

            # Get predictions
            if hasattr(self, 'is_tflite') and self.is_tflite:
                predictions = self._predict_tflite(input_data)
            else:
                predictions = self._predict_keras(input_data)

            if predictions is None:
                return None

            # Create probability dictionary
            probabilities = {}
            for i, prob in enumerate(predictions):
                if i < len(self.config.class_labels):
                    class_name = self.config.class_labels[i]
                    probabilities[class_name] = float(prob)

            return probabilities

        except Exception as e:
            self.logger.error(f"❌ Failed to get class probabilities: {e}")
            return None

    def predict_with_uncertainty(self, input_data: np.ndarray, num_samples: int = 10) -> Tuple[
        Optional[str], float, float]:
        """
        Make prediction with uncertainty estimation using Monte Carlo dropout

        Args:
            input_data: Preprocessed input data
            num_samples: Number of forward passes for uncertainty estimation

        Returns:
            Tuple of (predicted_class, mean_confidence, uncertainty)
        """
        try:
            if not self.model_loaded or hasattr(self, 'is_tflite'):
                # Fall back to regular prediction for TFLite
                pred, conf = self.predict(input_data)
                return pred, conf, 0.0

            # Collect predictions from multiple forward passes
            predictions = []
            for _ in range(num_samples):
                pred_probs = self.model(input_data, training=True)  # Enable dropout
                predictions.append(pred_probs.numpy()[0])

            predictions = np.array(predictions)

            # Calculate mean and uncertainty
            mean_predictions = np.mean(predictions, axis=0)
            uncertainty = np.std(predictions, axis=0)

            # Get predicted class
            predicted_class_idx = np.argmax(mean_predictions)
            predicted_class = self.config.class_labels[predicted_class_idx]
            mean_confidence = float(mean_predictions[predicted_class_idx])
            prediction_uncertainty = float(uncertainty[predicted_class_idx])

            return predicted_class, mean_confidence, prediction_uncertainty

        except Exception as e:
            self.logger.error(f"❌ Uncertainty prediction failed: {e}")
            return None, 0.0, 0.0


if __name__ == "__main__":
    # Test predictor functionality
    from src.config import get_config

    config = get_config()
    predictor = ASLPredictor(config)

    print("ASL predictor initialized successfully!")

    # Test model loading
    model_path = config.get_model_path()
    if os.path.exists(model_path):
        if predictor.load_model(model_path):
            print("✅ Model loaded successfully")

            # Test performance stats
            stats = predictor.get_performance_stats()
            print(f"Performance stats: {stats}")
        else:
            print("❌ Failed to load model")
    else:
        print(f"Model not found at: {model_path}")