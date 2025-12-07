"""
Unit tests for I2C reader
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.i2c_reader import I2CSensor, I2CReader
from src.config import I2CConfig, I2CSensorConfig


@pytest.fixture
def i2c_sensor_config():
    """Create I2C sensor config for testing"""
    return I2CSensorConfig(
        name="light_sensor",
        address=0x23,
        sensor_type="BH1750",
        register=0x10,
        read_length=2,
        unit="lux"
    )


@pytest.fixture
def i2c_config():
    """Create I2C config for testing"""
    return I2CConfig(
        enabled=True,
        bus=1,
        sensors=[
            I2CSensorConfig(
                name="light_sensor",
                address=0x23,
                sensor_type="BH1750",
                register=0x10,
                read_length=2,
                unit="lux"
            )
        ]
    )


def test_i2c_sensor_parse_bh1750():
    """Test parsing BH1750 light sensor data"""
    mock_bus = MagicMock()
    config = I2CSensorConfig(
        name="light",
        address=0x23,
        sensor_type="BH1750",
        register=0x10,
        read_length=2,
        unit="lux"
    )
    
    sensor = I2CSensor(config, mock_bus)
    
    # BH1750 returns 16-bit value, divide by 1.2 for lux
    # Example: 300 lux = 360 raw value
    data = [0x01, 0x68]  # 360 in big-endian
    result = sensor._parse_data(data)
    
    expected_lux = 360 / 1.2
    assert abs(result - expected_lux) < 0.1


def test_i2c_sensor_parse_bmp280():
    """Test parsing BMP280 pressure sensor data"""
    mock_bus = MagicMock()
    config = I2CSensorConfig(
        name="pressure",
        address=0x76,
        sensor_type="BMP280",
        register=0xF7,
        read_length=6,
        unit="hPa"
    )
    
    sensor = I2CSensor(config, mock_bus)
    
    # Sample pressure data (simplified, actual requires calibration)
    data = [0x50, 0x00, 0x00, 0x00, 0x00, 0x00]
    result = sensor._parse_data(data)
    
    assert result is not None
    assert result > 0


def test_i2c_sensor_parse_generic():
    """Test parsing generic 16-bit sensor"""
    mock_bus = MagicMock()
    config = I2CSensorConfig(
        name="generic",
        address=0x40,
        sensor_type="GENERIC",
        register=0x00,
        read_length=2,
        unit="raw"
    )
    
    sensor = I2CSensor(config, mock_bus)
    
    data = [0x12, 0x34]  # 0x1234 = 4660
    result = sensor._parse_data(data)
    
    assert result == 4660.0


def test_i2c_sensor_parse_insufficient_data():
    """Test parsing with insufficient data"""
    mock_bus = MagicMock()
    config = I2CSensorConfig(
        name="test",
        address=0x40,
        sensor_type="BH1750",
        register=0x00,
        read_length=2,
        unit="lux"
    )
    
    sensor = I2CSensor(config, mock_bus)
    
    # Insufficient data
    data = [0x12]
    result = sensor._parse_data(data)
    
    assert result is None


@patch('src.i2c_reader.SMBus')
def test_i2c_reader_connect(mock_smbus_class, i2c_config):
    """Test I2C reader connection"""
    mock_bus = MagicMock()
    mock_smbus_class.return_value = mock_bus
    
    reader = I2CReader(i2c_config)
    result = reader.connect()
    
    assert result
    assert len(reader.sensors) == 1
    mock_smbus_class.assert_called_once_with(1)


@patch('src.i2c_reader.SMBus')
def test_i2c_reader_disconnect(mock_smbus_class, i2c_config):
    """Test I2C reader disconnection"""
    mock_bus = MagicMock()
    mock_smbus_class.return_value = mock_bus
    
    reader = I2CReader(i2c_config)
    reader.connect()
    reader.disconnect()
    
    mock_bus.close.assert_called_once()
    assert len(reader.sensors) == 0


@patch('src.i2c_reader.SMBus')
def test_i2c_reader_read_all(mock_smbus_class, i2c_config):
    """Test reading all I2C sensors"""
    mock_bus = MagicMock()
    mock_bus.read_i2c_block_data.return_value = [0x01, 0x68]
    mock_smbus_class.return_value = mock_bus
    
    reader = I2CReader(i2c_config)
    reader.connect()
    
    readings = reader.read_all()
    
    assert len(readings) == 1
    assert readings[0].sensor_name == "light_sensor"
