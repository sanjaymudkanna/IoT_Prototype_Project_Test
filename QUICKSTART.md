# Quick Start Guide

## Overview

This IoT Edge Device project is a production-ready Python application for reading sensors and publishing data to MQTT.

## Installation (Quick)

```powershell
# 1. Navigate to project
cd E:\Coding\AI_Project

# 2. Run setup script
.\setup.ps1

# 3. Edit config.yaml with your settings

# 4. Run mock demo (no hardware needed)
python mock_demo.py
```

## Project Files Summary

### Core Application
- **src/main.py** - Main application entry point, orchestrates all components
- **src/config.py** - Configuration management with Pydantic validation
- **src/logger.py** - Structured JSON logging setup
- **src/sensor_interface.py** - Abstract base class for sensors
- **src/modbus_reader.py** - Modbus RTU/RS485 sensor implementation
- **src/i2c_reader.py** - I2C sensor implementation
- **src/telemetry.py** - Data validation and normalization
- **src/mqtt_publisher.py** - MQTT client with QoS 1 and auto-reconnect

### Configuration & Setup
- **config.yaml** - Main configuration file (MQTT, sensors, validation)
- **requirements.txt** - Python dependencies
- **setup.ps1** - Automated setup script for Windows
- **pytest.ini** - Test configuration
- **setup.cfg** - Linting and type checking config

### Testing
- **tests/test_*.py** - Comprehensive unit tests for all modules
- **tests/conftest.py** - Pytest configuration and fixtures
- **mock_demo.py** - Standalone demo with mock sensors

### Documentation
- **README.md** - Complete documentation
- **Dockerfile** - Optional Docker containerization
- **.gitignore** - Git ignore patterns

## Key Features Implemented

✅ **Modbus RTU/RS485 Support**
- Configurable baud rate, parity, stop bits
- Multiple data types (int16, uint16, int32, uint32, float32)
- Scaling factors for sensor calibration
- Multiple sensors on single serial port

✅ **I2C Sensor Support**
- Support for BMP280/BME280 pressure sensors
- Support for BH1750 light sensors
- Generic 16-bit sensor support
- Extensible parser architecture

✅ **Data Validation & Normalization**
- Configurable min/max validation ranges
- Validation status tracking
- Device ID and timestamp enrichment
- Batch and single-message modes

✅ **MQTT Publishing with QoS 1**
- Guaranteed message delivery
- Automatic reconnection with exponential backoff
- Configurable retry limits and delays
- TLS/SSL support
- Connection state callbacks

✅ **Production Features**
- Structured JSON logging
- Signal handlers for graceful shutdown
- Comprehensive error handling
- Configuration-driven design
- Full unit test coverage with mocking

## Testing Without Hardware

Run the mock demo to see the system in action:

```powershell
python mock_demo.py
```

This creates virtual sensors and demonstrates:
- Sensor reading
- Data validation
- Telemetry message creation
- JSON logging

## Running Tests

```powershell
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# View coverage report
.\htmlcov\index.html
```

## Configuration Examples

### MQTT Broker
```yaml
mqtt:
  broker: "mqtt.example.com"
  port: 1883
  client_id: "edge-device-001"
  qos: 1
```

### Modbus Sensor
```yaml
modbus:
  port: "COM1"
  sensors:
    - name: "temperature_sensor"
      slave_id: 1
      register_address: 0
      register_count: 2
      data_type: "float32"
      unit: "celsius"
```

### I2C Sensor
```yaml
i2c:
  bus: 1
  sensors:
    - name: "light_sensor"
      address: 0x23
      sensor_type: "BH1750"
      unit: "lux"
```

## Common Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run application
python src/main.py

# Run with custom config
python src/main.py custom_config.yaml

# Run tests
pytest

# Run mock demo
python mock_demo.py

# Check code quality
flake8 src/
mypy src/
```

## Next Steps

1. **Configure**: Edit `config.yaml` with your MQTT broker and sensor details
2. **Test**: Run `pytest` to ensure everything works
3. **Demo**: Run `python mock_demo.py` to see the system in action
4. **Deploy**: Run `python src/main.py` with real hardware

## Architecture Highlights

- **Modular Design**: Each component (sensors, validation, MQTT) is independent
- **Extensible**: Easy to add new sensor types by extending `SensorInterface`
- **Production-Ready**: Logging, error handling, graceful shutdown
- **Testable**: Full unit test coverage with hardware mocking
- **Configurable**: All settings in YAML, validated by Pydantic

## Performance Notes

- Default poll interval: 5 seconds
- MQTT QoS 1: At-least-once delivery
- Exponential backoff: 1s initial, 300s max, 2x multiplier
- Batching: Optional for high-frequency sensors

## Troubleshooting

**Import Errors**: Ensure virtual environment is activated
**Serial Access**: Check port permissions (Windows) or add user to dialout group (Linux)
**I2C Access**: Enable I2C in Raspberry Pi config
**MQTT Connection**: Verify broker address, port, and credentials

## Support

Refer to README.md for detailed documentation.

---
**Version**: 1.0.0
**Created**: December 7, 2025
