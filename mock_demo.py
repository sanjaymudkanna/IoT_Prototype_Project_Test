#!/usr/bin/env python3
"""
Quick start script for testing the IoT Edge Device
Creates a mock environment for testing without real hardware
"""

import time
import random
from datetime import datetime
from src.sensor_interface import SensorInterface, SensorReading
from src.telemetry import TelemetryProcessor
from src.config import ValidationRules, TelemetryConfig
from src.logger import setup_logging


class MockSensor(SensorInterface):
    """Mock sensor for testing without hardware"""
    
    def __init__(self, name: str, unit: str, min_val: float, max_val: float):
        super().__init__(name)
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
    
    def connect(self) -> bool:
        self._connected = True
        return True
    
    def disconnect(self) -> None:
        self._connected = False
    
    def read(self):
        if not self._connected:
            return None
        
        # Generate random value in range
        value = random.uniform(self.min_val, self.max_val)
        
        return SensorReading(
            sensor_name=self.name,
            value=value,
            unit=self.unit
        )


def main():
    """Run mock sensor demo"""
    print("=== IoT Edge Device Mock Demo ===\n")
    
    # Setup logging
    logger = setup_logging(log_level="INFO", app_name="mock-demo")
    
    # Create mock sensors
    sensors = [
        MockSensor("temperature_sensor", "celsius", 20.0, 30.0),
        MockSensor("humidity_sensor", "percent", 40.0, 70.0),
        MockSensor("pressure_sensor", "hPa", 1000.0, 1020.0),
    ]
    
    # Connect all sensors
    for sensor in sensors:
        sensor.connect()
        logger.info(f"Connected mock sensor: {sensor.name}")
    
    # Setup telemetry processor
    validation_rules = ValidationRules(
        temperature={'min': -40, 'max': 85},
        humidity={'min': 0, 'max': 100},
        pressure={'min': 300, 'max': 1100}
    )
    
    telemetry_config = TelemetryConfig(
        batch_enabled=False,
        batch_size=10,
        include_timestamp=True,
        include_device_id=True,
        device_id="mock-device-001"
    )
    
    processor = TelemetryProcessor(validation_rules, telemetry_config)
    
    print("\nReading sensors every 2 seconds. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            # Read all sensors
            readings = []
            for sensor in sensors:
                reading = sensor.read()
                if reading:
                    readings.append(reading)
            
            # Process readings
            messages = processor.process_readings(readings)
            
            # Display results
            for message in messages:
                print(f"\n[{message.timestamp.strftime('%H:%M:%S')}] Telemetry Message:")
                for reading in message.readings:
                    status_icon = "✓" if reading.validation_status == "valid" else "✗"
                    print(f"  {status_icon} {reading.sensor_name}: {reading.value:.2f} {reading.unit}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nShutting down mock demo...")
        for sensor in sensors:
            sensor.disconnect()
        print("Done!")


if __name__ == "__main__":
    main()
