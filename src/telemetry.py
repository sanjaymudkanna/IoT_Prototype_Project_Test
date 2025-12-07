"""
Data validation and normalization module
Validates sensor readings against configured rules and normalizes data
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from src.sensor_interface import SensorReading
from src.config import ValidationRules, TelemetryConfig
from src.logger import get_logger


logger = get_logger(__name__)


class ValidatedReading(BaseModel):
    """Validated and normalized sensor reading"""
    sensor_name: str
    value: float
    unit: str
    timestamp: datetime
    device_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_status: str = "valid"  # valid, out_of_range, invalid
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TelemetryMessage(BaseModel):
    """Normalized telemetry message for MQTT publishing"""
    device_id: str
    timestamp: datetime
    readings: List[ValidatedReading]
    message_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DataValidator:
    """Validates sensor readings against configured rules"""
    
    def __init__(self, validation_rules: ValidationRules):
        self.rules = validation_rules
        self.logger = get_logger(__name__)
    
    def validate(self, reading: SensorReading) -> ValidatedReading:
        """
        Validate a sensor reading
        
        Args:
            reading: SensorReading to validate
            
        Returns:
            ValidatedReading with validation status
        """
        # Extract sensor type from name (e.g., "temperature_sensor" -> "temperature")
        sensor_type = self._extract_sensor_type(reading.sensor_name)
        
        # Get validation rules for this sensor type
        rules = self._get_rules(sensor_type)
        
        validation_status = "valid"
        
        if rules:
            min_val = rules.get('min')
            max_val = rules.get('max')
            
            if min_val is not None and reading.value < min_val:
                validation_status = "out_of_range"
                self.logger.warning(
                    f"{reading.sensor_name} value {reading.value} below minimum {min_val}"
                )
            elif max_val is not None and reading.value > max_val:
                validation_status = "out_of_range"
                self.logger.warning(
                    f"{reading.sensor_name} value {reading.value} above maximum {max_val}"
                )
        
        return ValidatedReading(
            sensor_name=reading.sensor_name,
            value=reading.value,
            unit=reading.unit,
            timestamp=reading.timestamp,
            metadata=reading.metadata,
            validation_status=validation_status
        )
    
    def _extract_sensor_type(self, sensor_name: str) -> str:
        """Extract sensor type from sensor name"""
        # Try to match common sensor types
        name_lower = sensor_name.lower()
        
        if 'temp' in name_lower:
            return 'temperature'
        elif 'humid' in name_lower:
            return 'humidity'
        elif 'pressure' in name_lower or 'press' in name_lower:
            return 'pressure'
        elif 'light' in name_lower:
            return 'light'
        
        return sensor_name
    
    def _get_rules(self, sensor_type: str) -> Optional[Dict[str, float]]:
        """Get validation rules for a sensor type"""
        rules_dict = self.rules.dict()
        return rules_dict.get(sensor_type)


class TelemetryNormalizer:
    """Normalizes validated readings into telemetry messages"""
    
    def __init__(self, telemetry_config: TelemetryConfig):
        self.config = telemetry_config
        self.logger = get_logger(__name__)
        self._batch: List[ValidatedReading] = []
    
    def add_reading(self, reading: ValidatedReading) -> Optional[TelemetryMessage]:
        """
        Add a validated reading and optionally return a message
        
        Args:
            reading: ValidatedReading to add
            
        Returns:
            TelemetryMessage if ready to send, None otherwise
        """
        # Add device ID if configured
        if self.config.include_device_id:
            reading.device_id = self.config.device_id
        
        if self.config.batch_enabled:
            self._batch.append(reading)
            
            if len(self._batch) >= self.config.batch_size:
                return self._create_message()
            return None
        else:
            # Single reading mode
            return self._create_message([reading])
    
    def flush(self) -> Optional[TelemetryMessage]:
        """
        Flush any pending readings
        
        Returns:
            TelemetryMessage with remaining readings, or None if empty
        """
        if self._batch:
            return self._create_message()
        return None
    
    def _create_message(self, readings: Optional[List[ValidatedReading]] = None) -> TelemetryMessage:
        """
        Create a telemetry message
        
        Args:
            readings: Optional list of readings (uses batch if not provided)
            
        Returns:
            TelemetryMessage
        """
        if readings is None:
            readings = self._batch.copy()
            self._batch.clear()
        
        timestamp = datetime.utcnow() if self.config.include_timestamp else readings[0].timestamp
        
        message = TelemetryMessage(
            device_id=self.config.device_id,
            timestamp=timestamp,
            readings=readings,
            message_id=self._generate_message_id()
        )
        
        self.logger.debug(f"Created telemetry message with {len(readings)} readings")
        
        return message
    
    def _generate_message_id(self) -> str:
        """Generate a unique message ID"""
        import uuid
        return str(uuid.uuid4())


class TelemetryProcessor:
    """Combines validation and normalization"""
    
    def __init__(self, validation_rules: ValidationRules, telemetry_config: TelemetryConfig):
        self.validator = DataValidator(validation_rules)
        self.normalizer = TelemetryNormalizer(telemetry_config)
        self.logger = get_logger(__name__)
    
    def process_reading(self, reading: SensorReading) -> Optional[TelemetryMessage]:
        """
        Process a sensor reading through validation and normalization
        
        Args:
            reading: SensorReading to process
            
        Returns:
            TelemetryMessage if ready to send, None otherwise
        """
        # Validate
        validated = self.validator.validate(reading)
        
        # Normalize
        message = self.normalizer.add_reading(validated)
        
        return message
    
    def process_readings(self, readings: List[SensorReading]) -> List[TelemetryMessage]:
        """
        Process multiple sensor readings
        
        Args:
            readings: List of SensorReading objects
            
        Returns:
            List of TelemetryMessage objects ready to send
        """
        messages = []
        
        for reading in readings:
            message = self.process_reading(reading)
            if message:
                messages.append(message)
        
        # Flush any remaining readings
        final_message = self.normalizer.flush()
        if final_message:
            messages.append(final_message)
        
        return messages
