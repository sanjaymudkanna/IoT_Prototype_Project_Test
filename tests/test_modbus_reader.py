"""
Unit tests for Modbus reader
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import struct
from src.modbus_reader import ModbusSensor, ModbusReader
from src.config import ModbusConfig, ModbusSensorConfig


@pytest.fixture
def modbus_sensor_config():
    """Create Modbus sensor config for testing"""
    return ModbusSensorConfig(
        name="temperature_sensor",
        slave_id=1,
        register_address=0,
        register_count=2,
        data_type="float32",
        scaling_factor=1.0,
        unit="celsius"
    )


@pytest.fixture
def modbus_config():
    """Create Modbus config for testing"""
    return ModbusConfig(
        enabled=True,
        port="/dev/ttyUSB0",
        baudrate=9600,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=3,
        sensors=[
            ModbusSensorConfig(
                name="temp_sensor",
                slave_id=1,
                register_address=0,
                register_count=2,
                data_type="float32",
                scaling_factor=1.0,
                unit="celsius"
            )
        ]
    )


def test_modbus_sensor_parse_int16():
    """Test parsing int16 data"""
    mock_client = MagicMock()
    config = ModbusSensorConfig(
        name="test",
        slave_id=1,
        register_address=0,
        register_count=1,
        data_type="int16",
        scaling_factor=1.0,
        unit="test"
    )
    
    sensor = ModbusSensor(config, mock_client)
    
    # Test positive value
    result = sensor._parse_registers([100])
    assert result == 100.0
    
    # Test negative value (two's complement)
    result = sensor._parse_registers([65436])  # -100 in two's complement
    assert result == -100.0


def test_modbus_sensor_parse_uint16():
    """Test parsing uint16 data"""
    mock_client = MagicMock()
    config = ModbusSensorConfig(
        name="test",
        slave_id=1,
        register_address=0,
        register_count=1,
        data_type="uint16",
        scaling_factor=1.0,
        unit="test"
    )
    
    sensor = ModbusSensor(config, mock_client)
    result = sensor._parse_registers([1234])
    
    assert result == 1234.0


def test_modbus_sensor_parse_float32():
    """Test parsing float32 data"""
    mock_client = MagicMock()
    config = ModbusSensorConfig(
        name="test",
        slave_id=1,
        register_address=0,
        register_count=2,
        data_type="float32",
        scaling_factor=1.0,
        unit="test"
    )
    
    sensor = ModbusSensor(config, mock_client)
    
    # Create float32 value
    value = 25.5
    packed = struct.pack('>f', value)
    reg1, reg2 = struct.unpack('>HH', packed)
    
    result = sensor._parse_registers([reg1, reg2])
    
    assert abs(result - value) < 0.01


def test_modbus_sensor_parse_insufficient_registers():
    """Test parsing with insufficient registers"""
    mock_client = MagicMock()
    config = ModbusSensorConfig(
        name="test",
        slave_id=1,
        register_address=0,
        register_count=2,
        data_type="float32",
        scaling_factor=1.0,
        unit="test"
    )
    
    sensor = ModbusSensor(config, mock_client)
    result = sensor._parse_registers([100])  # Only 1 register for float32
    
    assert result is None


@patch('src.modbus_reader.ModbusSerialClient')
def test_modbus_reader_connect(mock_client_class, modbus_config):
    """Test Modbus reader connection"""
    # Mock the serial client
    mock_client = MagicMock()
    mock_client.connect.return_value = True
    mock_client_class.return_value = mock_client
    
    reader = ModbusReader(modbus_config)
    result = reader.connect()
    
    assert result
    assert len(reader.sensors) == 1


@patch('src.modbus_reader.ModbusSerialClient')
def test_modbus_reader_connect_failure(mock_client_class, modbus_config):
    """Test Modbus reader connection failure"""
    # Mock the serial client
    mock_client = MagicMock()
    mock_client.connect.return_value = False
    mock_client_class.return_value = mock_client
    
    reader = ModbusReader(modbus_config)
    result = reader.connect()
    
    assert not result


@patch('src.modbus_reader.ModbusSerialClient')
def test_modbus_reader_disconnect(mock_client_class, modbus_config):
    """Test Modbus reader disconnection"""
    mock_client = MagicMock()
    mock_client.connect.return_value = True
    mock_client_class.return_value = mock_client
    
    reader = ModbusReader(modbus_config)
    reader.connect()
    reader.disconnect()
    
    mock_client.close.assert_called_once()
    assert len(reader.sensors) == 0
