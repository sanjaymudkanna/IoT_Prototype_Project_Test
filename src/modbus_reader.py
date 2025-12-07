"""
Modbus RTU/RS485 sensor reader implementation
Supports reading sensor data via Modbus RTU protocol
"""

from typing import Optional, List
import struct
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from src.sensor_interface import SensorInterface, SensorReading
from src.config import ModbusConfig, ModbusSensorConfig
from src.logger import get_logger


logger = get_logger(__name__)


class ModbusSensor(SensorInterface):
    """Modbus RTU sensor implementation"""
    
    def __init__(self, config: ModbusSensorConfig, client: ModbusSerialClient):
        super().__init__(config.name)
        self.config = config
        self.client = client
    
    def connect(self) -> bool:
        """Connection managed by ModbusReader"""
        self._connected = self.client.connected if self.client else False
        return self._connected
    
    def disconnect(self) -> None:
        """Disconnection managed by ModbusReader"""
        self._connected = False
    
    def read(self) -> Optional[SensorReading]:
        """
        Read sensor data from Modbus registers
        
        Returns:
            SensorReading or None if read failed
        """
        if not self.client or not self.client.connected:
            self.logger.error(f"Modbus client not connected for sensor {self.name}")
            return None
        
        try:
            # Read holding registers
            result = self.client.read_holding_registers(
                address=self.config.register_address,
                count=self.config.register_count,
                slave=self.config.slave_id
            )
            
            if result.isError():
                self.logger.error(f"Error reading Modbus registers for {self.name}: {result}")
                return None
            
            # Parse data based on type
            raw_value = self._parse_registers(result.registers)
            
            if raw_value is None:
                return None
            
            # Apply scaling factor
            scaled_value = raw_value * self.config.scaling_factor
            
            self.logger.debug(
                f"Read {self.name}: raw={raw_value}, scaled={scaled_value}"
            )
            
            return SensorReading(
                sensor_name=self.name,
                value=scaled_value,
                unit=self.config.unit,
                metadata={
                    'slave_id': self.config.slave_id,
                    'register_address': self.config.register_address,
                    'data_type': self.config.data_type
                }
            )
            
        except ModbusException as e:
            self.logger.error(f"Modbus exception reading {self.name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error reading {self.name}: {e}")
            return None
    
    def _parse_registers(self, registers: List[int]) -> Optional[float]:
        """
        Parse register values based on data type
        
        Args:
            registers: List of register values
            
        Returns:
            Parsed float value or None
        """
        try:
            if self.config.data_type == "int16":
                return float(struct.unpack('>h', struct.pack('>H', registers[0]))[0])
            
            elif self.config.data_type == "uint16":
                return float(registers[0])
            
            elif self.config.data_type == "int32":
                if len(registers) < 2:
                    self.logger.error("Insufficient registers for int32")
                    return None
                data = struct.pack('>HH', registers[0], registers[1])
                return float(struct.unpack('>i', data)[0])
            
            elif self.config.data_type == "uint32":
                if len(registers) < 2:
                    self.logger.error("Insufficient registers for uint32")
                    return None
                data = struct.pack('>HH', registers[0], registers[1])
                return float(struct.unpack('>I', data)[0])
            
            elif self.config.data_type == "float32":
                if len(registers) < 2:
                    self.logger.error("Insufficient registers for float32")
                    return None
                data = struct.pack('>HH', registers[0], registers[1])
                return struct.unpack('>f', data)[0]
            
            else:
                self.logger.error(f"Unsupported data type: {self.config.data_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error parsing registers: {e}")
            return None


class ModbusReader:
    """Manages multiple Modbus sensors on a single serial port"""
    
    def __init__(self, config: ModbusConfig):
        self.config = config
        self.client: Optional[ModbusSerialClient] = None
        self.sensors: List[ModbusSensor] = []
        self.logger = get_logger(__name__)
    
    def connect(self) -> bool:
        """
        Connect to Modbus serial port
        
        Returns:
            True if connection successful
        """
        try:
            self.client = ModbusSerialClient(
                port=self.config.port,
                baudrate=self.config.baudrate,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                bytesize=self.config.bytesize,
                timeout=self.config.timeout
            )
            
            if self.client.connect():
                self.logger.info(f"Connected to Modbus port {self.config.port}")
                
                # Initialize sensors
                for sensor_config in self.config.sensors:
                    sensor = ModbusSensor(sensor_config, self.client)
                    self.sensors.append(sensor)
                    self.logger.info(f"Initialized Modbus sensor: {sensor_config.name}")
                
                return True
            else:
                self.logger.error(f"Failed to connect to Modbus port {self.config.port}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to Modbus: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Modbus serial port"""
        if self.client:
            self.client.close()
            self.logger.info("Disconnected from Modbus")
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
