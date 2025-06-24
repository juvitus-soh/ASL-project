"""
Configuration management for ASL Translation System
Author: Sadeu Armel - MSc Thesis
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Model configuration parameters"""
    name: str
    input_size: int
    alpha: float
    include_top: bool
    weights: str
    batch_size: int
    epochs: int
    learning_rate: float
    fine_tune_learning_rate: float
    dense_units: List[int]
    dropout_rates: List[float]


@dataclass
class DataConfig:
    """Data configuration parameters"""
    dataset_path: str
    processed_path: str
    image_size: int
    validation_split: float
    augmentation: Dict[str, Any]


@dataclass
class InferenceConfig:
    """Real-time inference configuration"""
    confidence_threshold: float
    prediction_buffer_size: int
    smoothing_required_count: int
    camera_width: int
    camera_height: int


class Config:
    """Main configuration class for ASL Translation System"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration from YAML file

        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        self._config = self._load_config()

        # Create configuration objects
        self.model = ModelConfig(**self._config['model'])
        self.data = DataConfig(**self._config['data'])
        self.inference = InferenceConfig(**self._config['inference'])

        # Direct access to other configs
        self.classes = self._config['classes']
        self.mediapipe = self._config['mediapipe']
        self.tts = self._config['tts']
        self.paths = self._config['paths']
        self.logging = self._config['logging']
        self.tflite = self._config['tflite']
        self.callbacks = self._config['callbacks']

        # Ensure directories exist
        self._create_directories()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.data.dataset_path,
            self.data.processed_path,
            self.paths['models'],
            self.paths['checkpoints'],
            self.paths['tflite'],
            self.paths['logs'],
            self.paths['plots'],
            self.paths['reports']
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def get_model_path(self, model_name: str = None) -> str:
        """Get full path for saving/loading model"""
        if model_name is None:
            model_name = f"{self.model.name}.h5"
        return os.path.join(self.paths['models'], model_name)

    def get_checkpoint_path(self, checkpoint_name: str = None) -> str:
        """Get full path for model checkpoints"""
        if checkpoint_name is None:
            checkpoint_name = f"{self.model.name}_checkpoint.h5"
        return os.path.join(self.paths['checkpoints'], checkpoint_name)

    def get_tflite_path(self, tflite_name: str = None) -> str:
        """Get full path for TensorFlow Lite model"""
        if tflite_name is None:
            tflite_name = f"{self.model.name}.tflite"
        return os.path.join(self.paths['tflite'], tflite_name)

    def get_log_path(self, log_name: str = "asl_system.log") -> str:
        """Get full path for log files"""
        return os.path.join(self.paths['logs'], log_name)

    def get_plot_path(self, plot_name: str) -> str:
        """Get full path for saving plots"""
        return os.path.join(self.paths['plots'], plot_name)

    def get_report_path(self, report_name: str) -> str:
        """Get full path for saving reports"""
        return os.path.join(self.paths['reports'], report_name)

    @property
    def num_classes(self) -> int:
        """Get number of ASL classes"""
        return len(self.classes['labels'])

    @property
    def class_labels(self) -> List[str]:
        """Get ASL class labels"""
        return self.classes['labels']

    def update_config(self, key: str, value: Any):
        """Update configuration value"""
        keys = key.split('.')
        current = self._config

        for k in keys[:-1]:
            current = current[k]
        current[keys[-1]] = value

    def save_config(self, output_path: str = None):
        """Save current configuration to file"""
        if output_path is None:
            output_path = self.config_path

        with open(output_path, 'w') as file:
            yaml.dump(self._config, file, default_flow_style=False)

    def __str__(self) -> str:
        """String representation of configuration"""
        return f"ASL Config: {self.model.name}, Classes: {self.num_classes}, Input: {self.model.input_size}x{self.model.input_size}"


# Global configuration instance
_config_instance = None


def get_config(config_path: str = "config.yaml") -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance


def reload_config(config_path: str = "config.yaml") -> Config:
    """Reload configuration (useful for testing)"""
    global _config_instance
    _config_instance = Config(config_path)
    return _config_instance


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    print("Configuration loaded successfully!")
    print(config)
    print(f"Model: {config.model.name}")
    print(f"Classes: {config.class_labels}")
    print(f"Model path: {config.get_model_path()}")