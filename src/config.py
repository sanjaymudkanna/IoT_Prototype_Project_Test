"""
Configuration management module
Handles loading and validation of application configuration
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator


class ReconnectConfig(BaseModel):
    """MQTT reconnection configuration"""
    max_retries: int = Field(default=10, ge=1)
    initial_delay: int = Field(default=1, ge=1)
    max_delay: int = Field(default=300, ge=1)
    backoff_multiplier: float = Field(default=2.0, ge=1.0)


class TLSConfig(BaseModel):
    """TLS/SSL configuration"""
    enabled: bool = False
    ca_certs: Optional[str] = None
    certfile: Optional[str] = None
    keyfile: Optional[str] = None


class MQTTConfig(BaseModel):
    """MQTT broker configuration"""
    broker: str
    port: int = Field(default=1883, ge=1, le=65535)
    client_id: str
    username: Optional[str] = None
    password: Optional[str] = None
    qos: int = Field(default=1, ge=0, le=2)
    topic_prefix: str
    keepalive: int = Field(default=60, ge=10)
    reconnect: ReconnectConfig = Field(default_factory=ReconnectConfig)
    tls: TLSConfig = Field(default_factory=TLSConfig)


class ModbusSensorConfig(BaseModel):
    """Individual Modbus sensor configuration"""
    name: str
    slave_id: int = Field(ge=1, le=247)
    register_address: int = Field(ge=0)
    register_count: int = Field(ge=1)
    data_type: str = Field(default="float32")
    scaling_factor: float = Field(default=1.0)
    unit: str


class ModbusConfig(BaseModel):
    """Modbus RTU configuration"""
    enabled: bool = True
    port: str
    baudrate: int = Field(default=9600)
    parity: str = Field(default="N")
    stopbits: int = Field(default=1, ge=1, le=2)
    bytesize: int = Field(default=8, ge=5, le=8)
    timeout: int = Field(default=3, ge=1)
    sensors: list[ModbusSensorConfig] = Field(default_factory=list)


class I2CSensorConfig(BaseModel):
    """Individual I2C sensor configuration"""
    name: str
    address: int = Field(ge=0x00, le=0x7F)
    sensor_type: str
    register: int = Field(ge=0)
    read_length: int = Field(ge=1)
    unit: str


class I2CConfig(BaseModel):
    """I2C bus configuration"""
    enabled: bool = True
    bus: int = Field(default=1, ge=0)
    sensors: list[I2CSensorConfig] = Field(default_factory=list)


class ValidationRules(BaseModel):
    """Sensor data validation rules"""
    temperature: Optional[Dict[str, float]] = None
    humidity: Optional[Dict[str, float]] = None
    pressure: Optional[Dict[str, float]] = None
    light: Optional[Dict[str, float]] = None


class TelemetryConfig(BaseModel):
    """Telemetry settings"""
    batch_enabled: bool = False
    batch_size: int = Field(default=10, ge=1)
    include_timestamp: bool = True
    include_device_id: bool = True
    device_id: str


class ApplicationConfig(BaseModel):
    """Application-level configuration"""
    name: str = "iot-edge-device"
    log_level: str = "INFO"
    poll_interval: int = Field(default=5, ge=1)


class Config(BaseModel):
    """Main configuration model"""
    application: ApplicationConfig
    mqtt: MQTTConfig
    modbus: ModbusConfig
    i2c: I2CConfig
    validation: ValidationRules
    telemetry: TelemetryConfig
    
    @validator('application')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.log_level.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load and validate configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Validated Config object
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with path.open('r') as f:
        config_dict = yaml.safe_load(f)
    
    return Config(**config_dict)
