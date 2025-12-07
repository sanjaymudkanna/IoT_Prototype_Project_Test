"""
I2C sensor reader implementation
Supports reading sensor data via I2C protocol
"""

from typing import Optional, List
import struct
from smbus2 import SMBus
from src.sensor_interface import SensorInterface, SensorReading
from src.config import I2CConfig, I2CSensorConfig
from src.logger import get_logger


logger = get_logger(__name__)


class I2CSensor(SensorInterface):
    """I2C sensor implementation"""
    
    def __init__(self, config: I2CSensorConfig, bus: SMBus):
        super().__init__(config.name)
        self.config = config
        self.bus = bus
    
    def connect(self) -> bool:
        """Connection managed by I2CReader"""
        self._connected = self.bus is not None
        return self._connected
    
    def disconnect(self) -> None:
        """Disconnection managed by I2CReader"""
        self._connected = False
    
    def read(self) -> Optional[SensorReading]:
        """
        Read sensor data from I2C device
        
        Returns:
            SensorReading or None if read failed
        """
        if not self.bus:
            self.logger.error(f"I2C bus not available for sensor {self.name}")
            return None
        
        try:
            # Read data from I2C device
            data = self.bus.read_i2c_block_data(
                self.config.address,
                self.config.register,
                self.config.read_length
            )
            
            # Parse data based on sensor type
            value = self._parse_data(data)
            
            if value is None:
                return None
            
            self.logger.debug(f"Read {self.name}: value={value}")
            
            return SensorReading(
                sensor_name=self.name,
                value=value,
                unit=self.config.unit,
                metadata={
                    'address': hex(self.config.address),
                    'sensor_type': self.config.sensor_type,
                    'register': hex(self.config.register)
                }
            )
            
        except OSError as e:
            self.logger.error(f"I2C communication error reading {self.name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error reading {self.name}: {e}")
            return None
    
    def _parse_data(self, data: List[int]) -> Optional[float]:
        """
        Parse I2C data based on sensor type
        
        Args:
            data: Raw I2C data bytes
            
        Returns:
            Parsed float value or None
        """
        try:
            # BMP280/BME280 pressure sensor
            if self.config.sensor_type.upper() in ["BMP280", "BME280"]:
                if len(data) < 6:
                    self.logger.error("Insufficient data for BMP280")
                    return None
                
                # Combine pressure bytes (20-bit value)
                adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
                # Simplified conversion (actual requires calibration data)
                pressure_hpa = adc_p / 256.0
                return pressure_hpa
            
            # BH1750 light sensor
            elif self.config.sensor_type.upper() == "BH1750":
                if len(data) < 2:
                    self.logger.error("Insufficient data for BH1750")
                    return None
                
                # Combine 2 bytes (16-bit value)
                light_level = (data[0] << 8) | data[1]
                # Convert to lux (divide by 1.2 for high-res mode)
                lux = light_level / 1.2
                return lux
            
            # Generic 16-bit sensor
            elif len(data) >= 2:
                value = struct.unpack('>H', bytes(data[:2]))[0]
                return float(value)
            
            else:
                self.logger.error(f"Unsupported sensor type: {self.config.sensor_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error parsing I2C data: {e}")
            return None


class I2CReader:
    """Manages multiple I2C sensors on a single bus"""
    
    def __init__(self, config: I2CConfig):
        self.config = config
        self.bus: Optional[SMBus] = None
        self.sensors: List[I2CSensor] = []
        self.logger = get_logger(__name__)
    
    def connect(self) -> bool:
        """
        Connect to I2C bus
        
        Returns:
            True if connection successful
        """
        try:
            self.bus = SMBus(self.config.bus)
            self.logger.info(f"Connected to I2C bus {self.config.bus}")
            
            # Initialize sensors
            for sensor_config in self.config.sensors:
                sensor = I2CSensor(sensor_config, self.bus)
                self.sensors.append(sensor)
                self.logger.info(
                    f"Initialized I2C sensor: {sensor_config.name} "
                    f"at address {hex(sensor_config.address)}"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to I2C bus: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from I2C bus"""
        if self.bus:
            self.bus.close()
            self.logger.info("Disconnected from I2C bus")
        self.sensors.clear()
    
    def read_all(self) -> List[SensorReading]:
        """
        Read all configured sensors
        
        Returns:
            List of SensorReading objects
        """
        readings = []
        
        for sensor in self.sensors:
            reading = sensor.read()
            if reading:
                readings.append(reading)
        
        return readings
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
