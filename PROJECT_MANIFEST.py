"""
PROJECT OVERVIEW AND FILE MANIFEST
IoT Edge Device - Production-Ready Python Project
Version: 1.0.0
Created: December 7, 2025
"""

# ==============================================================================
# PROJECT STRUCTURE
# ==============================================================================

AI_Project/
├── src/                                 # Main application source code
│   ├── __init__.py                      # Package initialization
│   ├── main.py                          # Application entry point & orchestrator
│   ├── config.py                        # Configuration management with Pydantic
│   ├── logger.py                        # Structured JSON logging setup
│   ├── sensor_interface.py              # Abstract base class for sensors
│   ├── modbus_reader.py                 # Modbus RTU/RS485 implementation
│   ├── i2c_reader.py                    # I2C sensor implementation
│   ├── telemetry.py                     # Data validation & normalization
│   └── mqtt_publisher.py                # MQTT client with QoS 1 & reconnection
│
├── tests/                               # Unit tests with mocking
│   ├── __init__.py                      # Test package initialization
│   ├── conftest.py                      # Pytest configuration & fixtures
│   ├── test_config.py                   # Config management tests
│   ├── test_sensor_interface.py         # Base sensor interface tests
│   ├── test_modbus_reader.py            # Modbus reader tests
│   ├── test_i2c_reader.py               # I2C reader tests
│   ├── test_telemetry.py                # Validation & normalization tests
│   └── test_mqtt_publisher.py           # MQTT publisher tests
│
├── logs/                                # Application logs (created at runtime)
│
├── config.yaml                          # Main configuration file
├── requirements.txt                     # Python dependencies
├── README.md                            # Comprehensive documentation
├── QUICKSTART.md                        # Quick start guide
├── .gitignore                           # Git ignore patterns
├── Dockerfile                           # Docker containerization (optional)
├── setup.ps1                            # Windows setup script
├── pytest.ini                           # Pytest configuration
├── setup.cfg                            # Flake8 & MyPy configuration
└── mock_demo.py                         # Standalone demo with mock sensors


# ==============================================================================
# MODULE DESCRIPTIONS
# ==============================================================================

## Core Application Modules

### src/main.py (175 lines)
- IoTEdgeDevice class: Main application orchestrator
- Signal handlers for graceful shutdown (SIGINT, SIGTERM)
- Component initialization (MQTT, Modbus, I2C)
- Main polling loop with error handling
- Entry point with command-line config path support

### src/config.py (180 lines)
- Pydantic models for type-safe configuration
- MQTTConfig: Broker, QoS, reconnection settings
- ModbusConfig: Serial port, sensors, data types
- I2CConfig: Bus, sensors, addresses
- ValidationRules: Min/max ranges for sensors
- TelemetryConfig: Batching, device ID, timestamps
- load_config(): YAML parsing with validation

### src/logger.py (65 lines)
- CustomJsonFormatter: JSON log formatting
- setup_logging(): Console and file handlers
- get_logger(): Retrieve logger instances
- Structured logging with timestamp, level, module

### src/sensor_interface.py (70 lines)
- SensorReading: Data class for sensor values
- SensorInterface: Abstract base class
- connect(), disconnect(), read() abstract methods
- Context manager support (__enter__, __exit__)
- is_connected property

### src/modbus_reader.py (200 lines)
- ModbusSensor: Individual Modbus sensor handler
- Data type parsing: int16, uint16, int32, uint32, float32
- Register reading with scaling factors
- ModbusReader: Manages multiple sensors on one port
- PyModbus integration
- Error handling for communication failures

### src/i2c_reader.py (170 lines)
- I2CSensor: Individual I2C sensor handler
- Sensor-specific parsers (BMP280, BH1750, generic)
- I2CReader: Manages multiple sensors on one bus
- SMBus integration
- OSError handling for I2C communication

### src/telemetry.py (220 lines)
- ValidatedReading: Validated sensor data model
- TelemetryMessage: MQTT message format
- DataValidator: Range validation against rules
- TelemetryNormalizer: Batching and enrichment
- TelemetryProcessor: Combined validation + normalization
- UUID-based message IDs

### src/mqtt_publisher.py (270 lines)
- MQTTPublisher: MQTT client with advanced features
- QoS 1 guaranteed delivery
- Exponential backoff reconnection
- Tenacity-based retry logic
- TLS/SSL support
- Connection/disconnection callbacks
- publish() and publish_json() methods


# ==============================================================================
# TEST COVERAGE
# ==============================================================================

## Unit Tests (6 files, ~600 lines total)

### tests/test_config.py
- Valid/invalid MQTT configuration
- Port and QoS validation
- Modbus sensor config validation
- Slave ID range checking
- File not found handling

### tests/test_sensor_interface.py
- SensorReading creation and serialization
- MockSensor implementation
- Connection/disconnection lifecycle
- Context manager usage
- Read from connected/disconnected sensors

### tests/test_modbus_reader.py
- Data type parsing (int16, uint16, float32, etc.)
- Register byte order handling
- Insufficient register detection
- Connection success/failure scenarios
- Multiple sensor management

### tests/test_i2c_reader.py
- BH1750 light sensor parsing
- BMP280 pressure sensor parsing
- Generic 16-bit sensor parsing
- Insufficient data handling
- Bus connection and disconnection

### tests/test_telemetry.py
- Valid reading validation
- Out-of-range detection (high/low)
- Single reading normalization
- Batch mode operation
- Complete telemetry processing pipeline

### tests/test_mqtt_publisher.py
- Publisher initialization
- Connection mocking
- Message publishing with QoS 1
- JSON data publishing
- Connection/disconnection callbacks
- Not-connected error handling


# ==============================================================================
# DEPENDENCIES (requirements.txt)
# ==============================================================================

Production Dependencies:
- paho-mqtt==1.6.1              # MQTT client
- pymodbus==3.5.4               # Modbus RTU/RS485
- pyserial==3.5                 # Serial communication
- smbus2==0.4.3                 # I2C communication
- pyyaml==6.0.1                 # YAML configuration
- pydantic==2.5.3               # Data validation
- python-json-logger==2.0.7     # JSON logging
- tenacity==8.2.3               # Retry/backoff logic

Testing Dependencies:
- pytest==7.4.3                 # Test framework
- pytest-cov==4.1.0             # Coverage reporting
- pytest-mock==3.12.0           # Mocking utilities
- pytest-asyncio==0.21.1        # Async test support

Development Dependencies:
- black==23.12.1                # Code formatting
- flake8==6.1.0                 # Linting
- mypy==1.7.1                   # Type checking


# ==============================================================================
# CONFIGURATION SCHEMA
# ==============================================================================

config.yaml structure:
├── application
│   ├── name: str
│   ├── log_level: str (DEBUG|INFO|WARNING|ERROR|CRITICAL)
│   └── poll_interval: int (seconds)
│
├── mqtt
│   ├── broker: str
│   ├── port: int (1-65535)
│   ├── client_id: str
│   ├── username: str (optional)
│   ├── password: str (optional)
│   ├── qos: int (0|1|2)
│   ├── topic_prefix: str
│   ├── keepalive: int
│   ├── reconnect
│   │   ├── max_retries: int
│   │   ├── initial_delay: int
│   │   ├── max_delay: int
│   │   └── backoff_multiplier: float
│   └── tls
│       ├── enabled: bool
│       ├── ca_certs: str
│       ├── certfile: str
│       └── keyfile: str
│
├── modbus
│   ├── enabled: bool
│   ├── port: str
│   ├── baudrate: int
│   ├── parity: str (N|E|O)
│   ├── stopbits: int (1|2)
│   ├── bytesize: int (5-8)
│   ├── timeout: int
│   └── sensors: list
│       ├── name: str
│       ├── slave_id: int (1-247)
│       ├── register_address: int
│       ├── register_count: int
│       ├── data_type: str
│       ├── scaling_factor: float
│       └── unit: str
│
├── i2c
│   ├── enabled: bool
│   ├── bus: int
│   └── sensors: list
│       ├── name: str
│       ├── address: int (0x00-0x7F)
│       ├── sensor_type: str
│       ├── register: int
│       ├── read_length: int
│       └── unit: str
│
├── validation
│   ├── temperature: {min: float, max: float}
│   ├── humidity: {min: float, max: float}
│   ├── pressure: {min: float, max: float}
│   └── light: {min: float, max: float}
│
└── telemetry
    ├── batch_enabled: bool
    ├── batch_size: int
    ├── include_timestamp: bool
    ├── include_device_id: bool
    └── device_id: str


# ==============================================================================
# DATA FLOW
# ==============================================================================

1. Application Start
   └─> Load config.yaml
   └─> Setup logging
   └─> Initialize MQTT client
   └─> Connect to MQTT broker
   └─> Initialize Modbus reader (if enabled)
   └─> Connect to serial port
   └─> Initialize I2C reader (if enabled)
   └─> Connect to I2C bus

2. Main Loop (every poll_interval seconds)
   └─> Read all Modbus sensors
       └─> For each sensor:
           └─> Read registers
           └─> Parse data type
           └─> Apply scaling factor
           └─> Create SensorReading
   └─> Read all I2C sensors
       └─> For each sensor:
           └─> Read I2C bytes
           └─> Parse sensor type
           └─> Create SensorReading
   └─> Process readings
       └─> Validate against rules
       └─> Create ValidatedReading
       └─> Normalize to TelemetryMessage
       └─> Add device ID and timestamp
   └─> Publish to MQTT
       └─> Serialize to JSON
       └─> Publish with QoS 1
       └─> Log result

3. MQTT Disconnection
   └─> Trigger on_disconnect callback
   └─> Calculate backoff delay
   └─> Attempt reconnection
   └─> Repeat with exponential backoff
   └─> Max retries: 10

4. Graceful Shutdown
   └─> Receive SIGINT/SIGTERM
   └─> Stop main loop
   └─> Disconnect Modbus
   └─> Disconnect I2C
   └─> Disconnect MQTT
   └─> Exit


# ==============================================================================
# MQTT MESSAGE FORMAT
# ==============================================================================

Topic: {topic_prefix}/telemetry
QoS: 1 (at-least-once delivery)

Message Structure:
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
    }
  ]
}


# ==============================================================================
# KEY FEATURES
# ==============================================================================

✅ Multi-Protocol Sensor Support
   - Modbus RTU/RS485 over serial
   - I2C bus communication
   - Extensible sensor interface

✅ Production-Ready MQTT
   - QoS 1 guaranteed delivery
   - Automatic reconnection
   - Exponential backoff (1s -> 300s, 2x multiplier)
   - TLS/SSL support
   - Connection state tracking

✅ Data Quality
   - Configurable min/max validation
   - Out-of-range detection
   - Validation status tracking
   - Data normalization

✅ Reliability
   - Comprehensive error handling
   - Graceful shutdown (SIGINT/SIGTERM)
   - Retry logic with tenacity
   - Connection health monitoring

✅ Observability
   - Structured JSON logging
   - Console and file output
   - Configurable log levels
   - Module-level loggers

✅ Testability
   - Full unit test coverage
   - Hardware mocking
   - Pytest fixtures
   - Coverage reporting

✅ Developer Experience
   - Type hints throughout
   - Pydantic validation
   - Configuration-driven
   - Clear documentation
   - Mock demo for testing


# ==============================================================================
# PERFORMANCE CHARACTERISTICS
# ==============================================================================

- Poll Interval: 5 seconds (configurable)
- MQTT Keepalive: 60 seconds
- Modbus Timeout: 3 seconds
- Reconnection Max Delay: 300 seconds
- Batch Size: 10 readings (if enabled)
- QoS Level: 1 (at-least-once)


# ==============================================================================
# EXTENSIBILITY
# ==============================================================================

Adding New Sensor Types:
1. Create class extending SensorInterface
2. Implement connect(), disconnect(), read()
3. Return SensorReading objects
4. Add to main.py initialization

Adding New Validation Rules:
1. Add to ValidationRules in config.py
2. Add to config.yaml validation section
3. Update DataValidator._extract_sensor_type()

Adding New MQTT Topics:
1. Use mqtt_publisher.publish_json()
2. Specify topic suffix
3. Provide data dictionary


# ==============================================================================
# DEPLOYMENT OPTIONS
# ==============================================================================

1. Standalone Python
   - Virtual environment
   - Systemd service (Linux)
   - Windows Service (Windows)

2. Docker Container
   - Use provided Dockerfile
   - Mount config.yaml
   - Device access for serial/I2C

3. Edge Computing Platforms
   - AWS IoT Greengrass
   - Azure IoT Edge
   - Google Cloud IoT Core


# ==============================================================================
# SECURITY CONSIDERATIONS
# ==============================================================================

- Store credentials in environment variables
- Enable TLS/SSL for MQTT
- Use certificate-based authentication
- Restrict config file permissions
- Network segmentation for sensors
- Regular security updates
- Input validation (Pydantic)
- No hardcoded secrets


# ==============================================================================
# MAINTENANCE
# ==============================================================================

Regular Tasks:
- Review logs for errors
- Monitor MQTT connection stability
- Update dependencies
- Run unit tests
- Check sensor calibration
- Verify data quality

Monitoring Metrics:
- Sensor read success rate
- MQTT publish success rate
- Reconnection frequency
- Validation failure rate
- Message latency


# ==============================================================================
# VERSION HISTORY
# ==============================================================================

Version 1.0.0 (December 7, 2025)
- Initial production release
- Modbus RTU/RS485 support
- I2C sensor support
- MQTT QoS 1 publishing
- Exponential backoff reconnection
- Data validation and normalization
- Comprehensive unit tests
- Full documentation

"""
