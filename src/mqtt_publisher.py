"""
MQTT publisher with reconnection logic and exponential backoff
Publishes telemetry data to MQTT broker with QoS 1
"""

import json
import time
import ssl
from typing import Optional, Callable
from datetime import datetime
import paho.mqtt.client as mqtt
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)
from src.config import MQTTConfig
from src.telemetry import TelemetryMessage
from src.logger import get_logger


logger = get_logger(__name__)


class MQTTPublisher:
    """MQTT publisher with automatic reconnection and exponential backoff"""
    
    def __init__(self, config: MQTTConfig):
        self.config = config
        self.client: Optional[mqtt.Client] = None
        self.logger = get_logger(__name__)
        self._connected = False
        self._connection_callbacks: list[Callable] = []
        self._disconnection_callbacks: list[Callable] = []
    
    def connect(self) -> bool:
        """
        Connect to MQTT broker with exponential backoff
        
        Returns:
            True if connection successful
        """
        try:
            self._attempt_connection()
            return True
        except RetryError as e:
            self.logger.error(f"Failed to connect to MQTT broker after retries: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to MQTT: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(
            multiplier=1,
            min=1,
            max=300
        ),
        retry=retry_if_exception_type(ConnectionError)
    )
    def _attempt_connection(self) -> None:
        """Attempt MQTT connection with retry logic"""
        try:
            # Create MQTT client
            self.client = mqtt.Client(
                client_id=self.config.client_id,
                clean_session=True,
                protocol=mqtt.MQTTv311
            )
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish
            
            # Set authentication if provided
            if self.config.username and self.config.password:
                self.client.username_pw_set(
                    self.config.username,
                    self.config.password
                )
            
            # Configure TLS if enabled
            if self.config.tls.enabled:
                self._configure_tls()
            
            # Connect to broker
            self.logger.info(
                f"Attempting to connect to MQTT broker {self.config.broker}:{self.config.port}"
            )
            
            self.client.connect(
                self.config.broker,
                self.config.port,
                self.config.keepalive
            )
            
            # Start network loop
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self._connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self._connected:
                raise ConnectionError("MQTT connection timeout")
                
        except Exception as e:
            self.logger.error(f"MQTT connection attempt failed: {e}")
            raise ConnectionError(f"MQTT connection failed: {e}")
    
    def _configure_tls(self) -> None:
        """Configure TLS/SSL for MQTT connection"""
        if not self.client:
            return
        
        tls_config = self.config.tls
        
        self.client.tls_set(
            ca_certs=tls_config.ca_certs,
            certfile=tls_config.certfile,
            keyfile=tls_config.keyfile,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        
        self.logger.info("TLS/SSL configured for MQTT connection")
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self._connected = False
            self.logger.info("Disconnected from MQTT broker")
    
    def publish(self, message: TelemetryMessage) -> bool:
        """
        Publish telemetry message to MQTT broker
        
        Args:
            message: TelemetryMessage to publish
            
        Returns:
            True if publish successful
        """
        if not self._connected or not self.client:
            self.logger.error("Cannot publish: not connected to MQTT broker")
            return False
        
        try:
            # Convert message to JSON
            payload = message.json()
            
            # Construct topic
            topic = f"{self.config.topic_prefix}/telemetry"
            
            # Publish with QoS
            result = self.client.publish(
                topic,
                payload,
                qos=self.config.qos,
                retain=False
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published message to {topic}")
                return True
            else:
                self.logger.error(f"Failed to publish message: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error publishing message: {e}")
            return False
    
    def publish_json(self, topic_suffix: str, data: dict, qos: Optional[int] = None) -> bool:
        """
        Publish arbitrary JSON data to a topic
        
        Args:
            topic_suffix: Topic suffix to append to prefix
            data: Dictionary to publish as JSON
            qos: Quality of Service (uses config default if not specified)
            
        Returns:
            True if publish successful
        """
        if not self._connected or not self.client:
            self.logger.error("Cannot publish: not connected to MQTT broker")
            return False
        
        try:
            payload = json.dumps(data)
            topic = f"{self.config.topic_prefix}/{topic_suffix}"
            qos_level = qos if qos is not None else self.config.qos
            
            result = self.client.publish(topic, payload, qos=qos_level, retain=False)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published JSON to {topic}")
                return True
            else:
                self.logger.error(f"Failed to publish JSON: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error publishing JSON: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for successful MQTT connection"""
        if rc == 0:
            self._connected = True
            self.logger.info(f"Connected to MQTT broker {self.config.broker}")
            
            # Trigger connection callbacks
            for callback in self._connection_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Error in connection callback: {e}")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
            self._connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        self._connected = False
        
        if rc == 0:
            self.logger.info("Cleanly disconnected from MQTT broker")
        else:
            self.logger.warning(f"Unexpectedly disconnected from MQTT broker (code {rc})")
            
            # Trigger disconnection callbacks
            for callback in self._disconnection_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Error in disconnection callback: {e}")
            
            # Attempt reconnection with exponential backoff
            self._reconnect_with_backoff()
    
    def _on_publish(self, client, userdata, mid):
        """Callback for successful publish"""
        self.logger.debug(f"Message {mid} published successfully")
    
    def _reconnect_with_backoff(self) -> None:
        """Reconnect to MQTT broker with exponential backoff"""
        delay = self.config.reconnect.initial_delay
        max_delay = self.config.reconnect.max_delay
        multiplier = self.config.reconnect.backoff_multiplier
        max_retries = self.config.reconnect.max_retries
        
        for attempt in range(max_retries):
            self.logger.info(
                f"Reconnection attempt {attempt + 1}/{max_retries} "
                f"after {delay}s delay"
            )
            
            time.sleep(delay)
            
            try:
                if self.client:
                    self.client.reconnect()
                    self.logger.info("Reconnection successful")
                    return
            except Exception as e:
                self.logger.warning(f"Reconnection attempt failed: {e}")
            
            # Increase delay with exponential backoff
            delay = min(delay * multiplier, max_delay)
        
        self.logger.error(f"Failed to reconnect after {max_retries} attempts")
    
    def add_connection_callback(self, callback: Callable) -> None:
        """Add callback to be called on successful connection"""
        self._connection_callbacks.append(callback)
    
    def add_disconnection_callback(self, callback: Callable) -> None:
        """Add callback to be called on disconnection"""
        self._disconnection_callbacks.append(callback)
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to MQTT broker"""
        return self._connected
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
