"""
Unit tests for sensor interfaces
"""

import pytest
from datetime import datetime
from src.sensor_interface import SensorReading, SensorInterface


def test_sensor_reading_creation():
    """Test creating a sensor reading"""
    reading = SensorReading(
        sensor_name="test_sensor",
        value=25.5,
        unit="celsius"
    )
    
    assert reading.sensor_name == "test_sensor"
    assert reading.value == 25.5
    assert reading.unit == "celsius"
    assert isinstance(reading.timestamp, datetime)


def test_sensor_reading_to_dict():
    """Test converting sensor reading to dictionary"""
    timestamp = datetime.utcnow()
    reading = SensorReading(
        sensor_name="test_sensor",
        value=25.5,
        unit="celsius",
        timestamp=timestamp,
        metadata={"source": "test"}
    )
    
    reading_dict = reading.to_dict()
    
    assert reading_dict['sensor_name'] == "test_sensor"
    assert reading_dict['value'] == 25.5
    assert reading_dict['unit'] == "celsius"
    assert reading_dict['timestamp'] == timestamp.isoformat()
    assert reading_dict['metadata']['source'] == "test"


def test_sensor_reading_repr():
    """Test sensor reading string representation"""
    reading = SensorReading(
        sensor_name="test_sensor",
        value=25.5,
        unit="celsius"
    )
    
    repr_str = repr(reading)
    
    assert "test_sensor" in repr_str
    assert "25.5" in repr_str
    assert "celsius" in repr_str


class MockSensor(SensorInterface):
    """Mock sensor for testing"""
    
    def __init__(self, name: str, should_connect: bool = True):
        super().__init__(name)
        self.should_connect = should_connect
        self.connect_called = False
        self.disconnect_called = False
        self.read_called = False
    
    def connect(self) -> bool:
        self.connect_called = True
        self._connected = self.should_connect
        return self.should_connect
    
    def disconnect(self) -> None:
        self.disconnect_called = True
        self._connected = False
    
    def read(self):
        self.read_called = True
        if self._connected:
            return SensorReading(self.name, 25.5, "celsius")
        return None


def test_sensor_interface_connect():
    """Test sensor interface connection"""
    sensor = MockSensor("test_sensor", should_connect=True)
    
    result = sensor.connect()
    
    assert result
    assert sensor.is_connected
    assert sensor.connect_called


def test_sensor_interface_connect_failure():
    """Test sensor interface connection failure"""
    sensor = MockSensor("test_sensor", should_connect=False)
    
    result = sensor.connect()
    
    assert not result
    assert not sensor.is_connected


def test_sensor_interface_disconnect():
    """Test sensor interface disconnection"""
    sensor = MockSensor("test_sensor")
    sensor.connect()
    
    sensor.disconnect()
    
    assert not sensor.is_connected
    assert sensor.disconnect_called


def test_sensor_interface_read_connected():
    """Test reading from connected sensor"""
    sensor = MockSensor("test_sensor")
    sensor.connect()
    
    reading = sensor.read()
    
    assert reading is not None
    assert reading.sensor_name == "test_sensor"
    assert sensor.read_called


def test_sensor_interface_read_disconnected():
    """Test reading from disconnected sensor"""
    sensor = MockSensor("test_sensor")
    
    reading = sensor.read()
    
    assert reading is None


def test_sensor_interface_context_manager():
    """Test sensor interface as context manager"""
    sensor = MockSensor("test_sensor")
    
    with sensor:
        assert sensor.is_connected
        assert sensor.connect_called
    
    assert not sensor.is_connected
    assert sensor.disconnect_called
