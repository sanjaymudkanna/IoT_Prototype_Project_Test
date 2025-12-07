"""
Unit tests for configuration management
"""

import pytest
from pathlib import Path
from pydantic import ValidationError
from src.config import (
    Config,
    MQTTConfig,
    ModbusConfig,
    I2CConfig,
    load_config
)


def test_mqtt_config_valid():
    """Test valid MQTT configuration"""
    config = MQTTConfig(
        broker="mqtt.example.com",
        port=1883,
        client_id="test-client",
        topic_prefix="test/topic"
    )
    
    assert config.broker == "mqtt.example.com"
    assert config.port == 1883
    assert config.qos == 1  # default


def test_mqtt_config_invalid_port():
    """Test invalid MQTT port"""
    with pytest.raises(ValidationError):
        MQTTConfig(
            broker="mqtt.example.com",
            port=99999,  # Invalid port
            client_id="test-client",
            topic_prefix="test/topic"
        )


def test_mqtt_config_invalid_qos():
    """Test invalid MQTT QoS"""
    with pytest.raises(ValidationError):
        MQTTConfig(
            broker="mqtt.example.com",
            port=1883,
            client_id="test-client",
            topic_prefix="test/topic",
            qos=3  # Invalid QoS
        )


def test_modbus_sensor_config_valid():
    """Test valid Modbus sensor configuration"""
    from src.config import ModbusSensorConfig
    
    config = ModbusSensorConfig(
        name="temp_sensor",
        slave_id=1,
        register_address=0,
        register_count=2,
        data_type="float32",
        unit="celsius"
    )
    
    assert config.name == "temp_sensor"
    assert config.slave_id == 1


def test_modbus_sensor_config_invalid_slave():
    """Test invalid Modbus slave ID"""
    from src.config import ModbusSensorConfig
    
    with pytest.raises(ValidationError):
        ModbusSensorConfig(
            name="temp_sensor",
            slave_id=300,  # Invalid slave ID
            register_address=0,
            register_count=2,
            data_type="float32",
            unit="celsius"
        )


def test_load_config_file_not_found():
    """Test loading non-existent config file"""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")
