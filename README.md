# IoT Edge Device - Prototyping test prod-Ready Python Project

A complete, production-ready edge device application for reading sensor data via Modbus RTU/RS485 and I2C protocols, validating and normalizing telemetry, and publishing to MQTT with QoS 1.

## Features

✅ **Multiple Sensor Protocols**
- Modbus RTU over RS485 serial communication
- I2C bus sensor support
- Extensible sensor interface architecture

✅ **Data Processing**
- Real-time data validation with configurable ranges
- Data normalization and batching
- Metadata enrichment

✅ **MQTT Publishing**
- QoS 1 guaranteed message delivery
- Automatic reconnection with exponential backoff
- TLS/SSL support
- Connection state callbacks

✅ **Production Features**
- Structured JSON logging
- Comprehensive error handling
- Graceful shutdown on SIGINT/SIGTERM
- Configuration-driven design
- Full unit test coverage

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     IoT Edge Device                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Modbus     │    │     I2C      │    │   Future     │  │
│  │   Reader     │    │   Reader     │    │   Sensors    │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘  │
│         │                   │                                │
│         └───────────┬───────┘                                │
│                     ▼                                        │
│         ┌───────────────────────┐                            │
│         │  Telemetry Processor  │                            │
│         │  - Validation         │                            │
│         │  - Normalization      │                            │
│         └───────────┬───────────┘                            │
│                     ▼                                        │
│         ┌───────────────────────┐                            │
│         │   MQTT Publisher      │                            │
│         │  - QoS 1              │                            │
│         │  - Auto-reconnect     │                            │
│         │  - Exponential Backoff│                            │
│         └───────────┬───────────┘                            │
│                     │                                        │
└─────────────────────┼────────────────────────────────────────┘
                      ▼
              ┌───────────────┐
              │  MQTT Broker  │
              └───────────────┘
```

## Project Structure

```
AI_Project/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Main application entry point
│   ├── config.py             # Configuration management
│   ├── logger.py             # Logging setup
│   ├── sensor_interface.py   # Abstract sensor interface
│   ├── modbus_reader.py      # Modbus RTU/RS485 implementation
│   ├── i2c_reader.py         # I2C sensor implementation
│   ├── telemetry.py          # Validation & normalization
│   └── mqtt_publisher.py     # MQTT client with reconnection
├── tests/
│   ├── test_config.py
│   ├── test_sensor_interface.py
│   ├── test_modbus_reader.py
│   ├── test_i2c_reader.py
│   ├── test_telemetry.py
│   └── test_mqtt_publisher.py
├── config.yaml               # Application configuration
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Hardware access:
  - RS485/Serial port for Modbus (e.g., `/dev/ttyUSB0` on Linux, `COM1` on Windows)
  - I2C bus access (typically on Raspberry Pi or similar)
  - MQTT broker (local or remote)

### Setup

1. **Clone or download the project**

```powershell
cd E:\Coding\AI_Project
```

2. **Create virtual environment**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Configure the application**

Edit `config.yaml` to match your environment:

```yaml
mqtt:
  broker: "your-mqtt-broker.com"
  port: 1883
  client_id: "your-device-id"
  username: "your-username"
  password: "your-password"
  
modbus:
  port: "COM1"  # Windows: COM1, Linux: /dev/ttyUSB0
  
i2c:
  bus: 1  # I2C bus number
```

## Configuration

### MQTT Settings

```yaml
mqtt:
  broker: "mqtt.example.com"      # MQTT broker hostname/IP
  port: 1883                       # MQTT port (1883 standard, 8883 for TLS)
  client_id: "edge-device-001"    # Unique client identifier
  username: "device_user"          # MQTT username (optional)
  password: "device_password"      # MQTT password (optional)
  qos: 1                           # Quality of Service (0, 1, or 2)
  topic_prefix: "sensors/edge-001" # Topic prefix for all messages
  keepalive: 60                    # Keepalive interval in seconds
  
  reconnect:
    max_retries: 10                # Maximum reconnection attempts
    initial_delay: 1               # Initial delay in seconds
    max_delay: 300                 # Maximum delay in seconds
    backoff_multiplier: 2          # Exponential backoff multiplier
```

### Modbus Configuration

```yaml
modbus:
  enabled: true
  port: "/dev/ttyUSB0"     # Serial port
  baudrate: 9600           # Baud rate
  parity: "N"              # Parity: N (None), E (Even), O (Odd)
  stopbits: 1              # Stop bits
  bytesize: 8              # Data bits
  timeout: 3               # Read timeout in seconds
  
  sensors:
    - name: "temperature_sensor"
      slave_id: 1                    # Modbus slave ID
      register_address: 0            # Starting register address
      register_count: 2              # Number of registers to read
      data_type: "float32"           # Data type: int16, uint16, int32, uint32, float32
      scaling_factor: 0.1            # Multiply raw value by this
      unit: "celsius"                # Unit of measurement
```

### I2C Configuration

```yaml
i2c:
  enabled: true
  bus: 1                   # I2C bus number (1 on Raspberry Pi)
  
  sensors:
    - name: "light_sensor"
      address: 0x23              # I2C device address (hex)
      sensor_type: "BH1750"      # Sensor type for parsing
      register: 0x10             # Command/register to read
      read_length: 2             # Bytes to read
      unit: "lux"                # Unit of measurement
```

### Validation Rules

```yaml
validation:
  temperature:
    min: -40      # Minimum valid value
    max: 85       # Maximum valid value
  humidity:
    min: 0
    max: 100
  pressure:
    min: 300
    max: 1100
```

## Usage

### Running the Application

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run with default config
python src/main.py

# Run with custom config
python src/main.py path/to/custom_config.yaml
```

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_mqtt_publisher.py

# Run with verbose output
pytest -v
```

### Example Output

The application logs structured JSON to console and file:

```json
{
  "timestamp": "2025-12-07T10:30:45.123Z",
  "level": "INFO",
  "name": "iot-edge-device",
  "message": "Connected to MQTT broker mqtt.example.com"
}
{
  "timestamp": "2025-12-07T10:30:46.456Z",
  "level": "INFO",
  "name": "src.modbus_reader",
  "message": "Read 2 Modbus readings"
}
{
  "timestamp": "2025-12-07T10:30:46.789Z",
  "level": "INFO",
  "name": "iot-edge-device",
  "message": "Published telemetry with 2 readings"
}
```

## MQTT Message Format

Published messages follow this JSON schema:

```json
{
  "device_id": "edge-device-001",
  "timestamp": "2025-12-07T10:30:45.123Z",
  "message_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "readings": [
    {
      "sensor_name": "temperature_sensor",
      "value": 25.5,
      "unit": "celsius",
      "timestamp": "2025-12-07T10:30:45.100Z",
      "device_id": "edge-device-001",
      "validation_status": "valid",
      "metadata": {
        "slave_id": 1,
        "register_address": 0,
        "data_type": "float32"
      }
    },
    {
      "sensor_name": "humidity_sensor",
      "value": 60.2,
      "unit": "percent",
      "timestamp": "2025-12-07T10:30:45.120Z",
      "device_id": "edge-device-001",
      "validation_status": "valid",
      "metadata": {
        "slave_id": 1,
        "register_address": 2,
        "data_type": "float32"
      }
    }
  ]
}
```

## Error Handling

The application includes comprehensive error handling:

- **Connection Failures**: Automatic reconnection with exponential backoff
- **Sensor Read Errors**: Logged but don't stop the main loop
- **Validation Failures**: Readings marked as `out_of_range` but still published
- **MQTT Publish Failures**: Logged with retry on next poll cycle
- **Graceful Shutdown**: SIGINT/SIGTERM handlers ensure clean disconnection

## Extending the System

### Adding a New Sensor Protocol

1. Create a new sensor class extending `SensorInterface`
2. Implement `connect()`, `disconnect()`, and `read()` methods
3. Return `SensorReading` objects from `read()`

```python
from src.sensor_interface import SensorInterface, SensorReading

class MySensor(SensorInterface):
    def connect(self) -> bool:
        # Connection logic
        self._connected = True
        return True
    
    def disconnect(self) -> None:
        # Cleanup
        self._connected = False
    
    def read(self) -> Optional[SensorReading]:
        # Read and return data
        return SensorReading(
            sensor_name=self.name,
            value=42.0,
            unit="custom"
        )
```

### Adding Custom Validation

Extend the `ValidationRules` in `config.py` and update the validator logic in `telemetry.py`.

## Troubleshooting

### Common Issues

**Serial Port Access Denied**
```
Solution: Ensure user has permission to access serial port
Linux: sudo usermod -a -G dialout $USER
Windows: Run as administrator or check device permissions
```

**I2C Bus Not Found**
```
Solution: Enable I2C on Raspberry Pi
sudo raspi-config -> Interface Options -> I2C -> Enable
```

**MQTT Connection Timeout**
```
Solution: Check broker address, port, and network connectivity
Test with: mosquitto_pub -h mqtt.example.com -t test -m "hello"
```

**Module Import Errors**
```
Solution: Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1 (Windows)
source venv/bin/activate (Linux)
```

## Performance Considerations

- **Poll Interval**: Adjust `poll_interval` based on sensor update rates (default: 5 seconds)
- **Batching**: Enable `batch_enabled` for high-frequency sensors to reduce MQTT traffic
- **QoS Level**: QoS 1 provides good balance; use QoS 2 only if duplicate messages are critical
- **Logging**: Set log level to WARNING or ERROR in production to reduce I/O

## Security

- Store sensitive credentials in environment variables or secure vault
- Enable TLS/SSL for MQTT connections in production
- Use certificate-based authentication when possible
- Restrict file permissions on config files containing credentials
- Implement network segmentation for sensor networks

## License

This project is provided as-is for educational and commercial use.

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: December 7, 2025  
**Python Version**: 3.9+
