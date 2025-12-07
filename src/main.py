"""
Main application orchestrator
Coordinates sensor reading, validation, and MQTT publishing
"""

import time
import signal
import sys
from typing import Optional
from pathlib import Path
from src.config import load_config, Config
from src.logger import setup_logging, get_logger
from src.modbus_reader import ModbusReader
from src.i2c_reader import I2CReader
from src.telemetry import TelemetryProcessor
from src.mqtt_publisher import MQTTPublisher


class IoTEdgeDevice:
    """Main IoT edge device application"""
    
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        self.config: Config = load_config(config_path)
        
        # Setup logging
        log_file = f"logs/{self.config.application.name}.log"
        self.logger = setup_logging(
            log_level=self.config.application.log_level,
            log_file=log_file,
            app_name=self.config.application.name
        )
        
        self.logger.info("Initializing IoT Edge Device")
        
        # Initialize components
        self.modbus_reader: Optional[ModbusReader] = None
        self.i2c_reader: Optional[I2CReader] = None
        self.telemetry_processor: Optional[TelemetryProcessor] = None
        self.mqtt_publisher: Optional[MQTTPublisher] = None
        
        self._running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating shutdown")
        self.stop()
    
    def initialize(self) -> bool:
        """
        Initialize all components
        
        Returns:
            True if initialization successful
        """
        try:
            # Initialize telemetry processor
            self.telemetry_processor = TelemetryProcessor(
                self.config.validation,
                self.config.telemetry
            )
            self.logger.info("Telemetry processor initialized")
            
            # Initialize MQTT publisher
            self.mqtt_publisher = MQTTPublisher(self.config.mqtt)
            if not self.mqtt_publisher.connect():
                self.logger.error("Failed to connect to MQTT broker")
                return False
            
            # Initialize Modbus reader if enabled
            if self.config.modbus.enabled:
                self.modbus_reader = ModbusReader(self.config.modbus)
                if not self.modbus_reader.connect():
                    self.logger.warning("Failed to connect to Modbus, continuing without it")
                    self.modbus_reader = None
            
            # Initialize I2C reader if enabled
            if self.config.i2c.enabled:
                self.i2c_reader = I2CReader(self.config.i2c)
                if not self.i2c_reader.connect():
                    self.logger.warning("Failed to connect to I2C, continuing without it")
                    self.i2c_reader = None
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", exc_info=True)
            return False
    
    def run(self) -> None:
        """Run the main application loop"""
        self.logger.info("Starting main application loop")
        self._running = True
        
        poll_interval = self.config.application.poll_interval
        
        while self._running:
            try:
                self._poll_sensors()
                time.sleep(poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(poll_interval)
    
    def _poll_sensors(self) -> None:
        """Poll all sensors and publish telemetry"""
        readings = []
        
        # Read Modbus sensors
        if self.modbus_reader:
            try:
                modbus_readings = self.modbus_reader.read_all()
                readings.extend(modbus_readings)
                self.logger.debug(f"Read {len(modbus_readings)} Modbus readings")
            except Exception as e:
                self.logger.error(f"Error reading Modbus sensors: {e}")
        
        # Read I2C sensors
        if self.i2c_reader:
            try:
                i2c_readings = self.i2c_reader.read_all()
                readings.extend(i2c_readings)
                self.logger.debug(f"Read {len(i2c_readings)} I2C readings")
            except Exception as e:
                self.logger.error(f"Error reading I2C sensors: {e}")
        
        # Process and publish readings
        if readings and self.telemetry_processor and self.mqtt_publisher:
            try:
                messages = self.telemetry_processor.process_readings(readings)
                
                for message in messages:
                    success = self.mqtt_publisher.publish(message)
                    if success:
                        self.logger.info(
                            f"Published telemetry with {len(message.readings)} readings"
                        )
                    else:
                        self.logger.error("Failed to publish telemetry")
                        
            except Exception as e:
                self.logger.error(f"Error processing/publishing telemetry: {e}")
        else:
            self.logger.debug("No readings to publish")
    
    def stop(self) -> None:
        """Stop the application and cleanup resources"""
        self.logger.info("Stopping IoT Edge Device")
        self._running = False
        
        # Disconnect from sensors
        if self.modbus_reader:
            self.modbus_reader.disconnect()
        
        if self.i2c_reader:
            self.i2c_reader.disconnect()
        
        # Disconnect from MQTT
        if self.mqtt_publisher:
            self.mqtt_publisher.disconnect()
        
        self.logger.info("Shutdown complete")
    
    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


def main():
    """Main entry point"""
    # Get config path from command line or use default
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    # Create and run application
    try:
        app = IoTEdgeDevice(config_path)
        
        if app.initialize():
            app.run()
        else:
            print("Failed to initialize application", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
