"""
Unit tests for telemetry validation and normalization
"""

import pytest
from datetime import datetime
from src.telemetry import (
    DataValidator,
    TelemetryNormalizer,
    TelemetryProcessor,
    ValidatedReading
)
from src.sensor_interface import SensorReading
from src.config import ValidationRules, TelemetryConfig


@pytest.fixture
def validation_rules():
    """Create validation rules for testing"""
    return ValidationRules(
        temperature={'min': -40, 'max': 85},
        humidity={'min': 0, 'max': 100},
        pressure={'min': 300, 'max': 1100}
    )


@pytest.fixture
def telemetry_config():
    """Create telemetry config for testing"""
    return TelemetryConfig(
        batch_enabled=False,
        batch_size=10,
        include_timestamp=True,
        include_device_id=True,
        device_id="test-device-001"
    )


def test_validator_valid_reading(validation_rules):
    """Test validation of a valid reading"""
    validator = DataValidator(validation_rules)
    
    reading = SensorReading(
        sensor_name="temperature_sensor",
        value=25.5,
        unit="celsius"
    )
    
    validated = validator.validate(reading)
    
    assert validated.validation_status == "valid"
    assert validated.value == 25.5


def test_validator_out_of_range_high(validation_rules):
    """Test validation of reading above maximum"""
    validator = DataValidator(validation_rules)
    
    reading = SensorReading(
        sensor_name="temperature_sensor",
        value=100.0,  # Above max of 85
        unit="celsius"
    )
    
    validated = validator.validate(reading)
    
    assert validated.validation_status == "out_of_range"


def test_validator_out_of_range_low(validation_rules):
    """Test validation of reading below minimum"""
    validator = DataValidator(validation_rules)
    
    reading = SensorReading(
        sensor_name="humidity_sensor",
        value=-5.0,  # Below min of 0
        unit="percent"
    )
    
    validated = validator.validate(reading)
    
    assert validated.validation_status == "out_of_range"


def test_normalizer_single_reading(telemetry_config):
    """Test normalizing a single reading"""
    normalizer = TelemetryNormalizer(telemetry_config)
    
    reading = ValidatedReading(
        sensor_name="temperature_sensor",
        value=25.5,
        unit="celsius",
        timestamp=datetime.utcnow()
    )
    
    message = normalizer.add_reading(reading)
    
    assert message is not None
    assert message.device_id == "test-device-001"
    assert len(message.readings) == 1
    assert message.readings[0].device_id == "test-device-001"


def test_normalizer_batch_mode():
    """Test normalizing with batching enabled"""
    config = TelemetryConfig(
        batch_enabled=True,
        batch_size=3,
        include_timestamp=True,
        include_device_id=True,
        device_id="test-device-001"
    )
    
    normalizer = TelemetryNormalizer(config)
    
    # Add readings one by one
    reading1 = ValidatedReading(
        sensor_name="temp1",
        value=25.5,
        unit="celsius",
        timestamp=datetime.utcnow()
    )
    
    reading2 = ValidatedReading(
        sensor_name="temp2",
        value=26.5,
        unit="celsius",
        timestamp=datetime.utcnow()
    )
    
    # First two should not trigger message
    assert normalizer.add_reading(reading1) is None
    assert normalizer.add_reading(reading2) is None
    
    # Third should trigger batch
    reading3 = ValidatedReading(
        sensor_name="temp3",
        value=27.5,
        unit="celsius",
        timestamp=datetime.utcnow()
    )
    
    message = normalizer.add_reading(reading3)
    
    assert message is not None
    assert len(message.readings) == 3


def test_telemetry_processor(validation_rules, telemetry_config):
    """Test complete telemetry processing"""
    processor = TelemetryProcessor(validation_rules, telemetry_config)
    
    reading = SensorReading(
        sensor_name="temperature_sensor",
        value=25.5,
        unit="celsius"
    )
    
    message = processor.process_reading(reading)
    
    assert message is not None
    assert len(message.readings) == 1
    assert message.readings[0].validation_status == "valid"


def test_telemetry_processor_multiple_readings(validation_rules, telemetry_config):
    """Test processing multiple readings"""
    processor = TelemetryProcessor(validation_rules, telemetry_config)
    
    readings = [
        SensorReading("temperature_sensor", 25.5, "celsius"),
        SensorReading("humidity_sensor", 60.0, "percent"),
        SensorReading("pressure_sensor", 1013.0, "hPa")
    ]
    
    messages = processor.process_readings(readings)
    
    # In non-batch mode, should get 3 messages plus possibly a flush
    assert len(messages) >= 3
