"""
Sensor interface base classes
Defines abstract interfaces for sensor readers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from src.logger import get_logger


logger = get_logger(__name__)


class SensorReading:
    """Represents a single sensor reading"""
    
    def __init__(
        self,
        sensor_name: str,
        value: float,
        unit: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.sensor_name = sensor_name
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reading to dictionary"""
        return {
            'sensor_name': self.sensor_name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        return f"SensorReading({self.sensor_name}={self.value}{self.unit})"


class SensorInterface(ABC):
    """Abstract base class for sensor interfaces"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"{__name__}.{name}")
        self._connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to sensor
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to sensor"""
        pass
    
    @abstractmethod
    def read(self) -> Optional[SensorReading]:
        """
        Read data from sensor
        
        Returns:
            SensorReading object or None if read failed
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if sensor is connected"""
        return self._connected
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
