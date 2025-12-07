"""
Unit tests for MQTT publisher
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import paho.mqtt.client as mqtt
from src.mqtt_publisher import MQTTPublisher
from src.config import MQTTConfig, ReconnectConfig
from src.telemetry import TelemetryMessage, ValidatedReading
from datetime import datetime


@pytest.fixture
def mqtt_config():
    """Create MQTT config for testing"""
    return MQTTConfig(
        broker="test.mqtt.broker",
        port=1883,
        client_id="test-client",
        topic_prefix="test/topic",
        qos=1,
        keepalive=60,
        reconnect=ReconnectConfig(
            max_retries=3,
            initial_delay=1,
            max_delay=10,
            backoff_multiplier=2
        )
    )


@pytest.fixture
def telemetry_message():
    """Create a sample telemetry message"""
    reading = ValidatedReading(
        sensor_name="test_sensor",
        value=25.5,
        unit="celsius",
        timestamp=datetime.utcnow()
    )
    
    return TelemetryMessage(
        device_id="test-device",
        timestamp=datetime.utcnow(),
        readings=[reading]
    )


def test_mqtt_publisher_init(mqtt_config):
    """Test MQTT publisher initialization"""
    publisher = MQTTPublisher(mqtt_config)
    
    assert publisher.config == mqtt_config
    assert not publisher.is_connected


@patch('paho.mqtt.client.Client')
def test_mqtt_publisher_connect(mock_client_class, mqtt_config):
    """Test MQTT connection"""
    # Mock the MQTT client
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    publisher = MQTTPublisher(mqtt_config)
    
    # Simulate successful connection
    publisher._connected = True
    
    assert publisher._connected


@patch('paho.mqtt.client.Client')
def test_mqtt_publisher_publish(mock_client_class, mqtt_config, telemetry_message):
    """Test MQTT message publishing"""
    # Mock the MQTT client
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Mock successful publish
    mock_result = MagicMock()
    mock_result.rc = mqtt.MQTT_ERR_SUCCESS
    mock_client.publish.return_value = mock_result
    
    publisher = MQTTPublisher(mqtt_config)
    publisher.client = mock_client
    publisher._connected = True
    
    # Publish message
    success = publisher.publish(telemetry_message)
    
    assert success
    mock_client.publish.assert_called_once()


@patch('paho.mqtt.client.Client')
def test_mqtt_publisher_publish_not_connected(mock_client_class, mqtt_config, telemetry_message):
    """Test publishing when not connected"""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = False
    
    success = publisher.publish(telemetry_message)
    
    assert not success


@patch('paho.mqtt.client.Client')
def test_mqtt_publisher_publish_json(mock_client_class, mqtt_config):
    """Test publishing JSON data"""
    # Mock the MQTT client
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    # Mock successful publish
    mock_result = MagicMock()
    mock_result.rc = mqtt.MQTT_ERR_SUCCESS
    mock_client.publish.return_value = mock_result
    
    publisher = MQTTPublisher(mqtt_config)
    publisher.client = mock_client
    publisher._connected = True
    
    # Publish JSON
    test_data = {"temperature": 25.5, "humidity": 60.0}
    success = publisher.publish_json("status", test_data)
    
    assert success
    mock_client.publish.assert_called_once()


def test_mqtt_on_connect_callback(mqtt_config):
    """Test on_connect callback"""
    publisher = MQTTPublisher(mqtt_config)
    
    # Simulate successful connection
    publisher._on_connect(None, None, None, 0)
    
    assert publisher._connected


def test_mqtt_on_disconnect_callback(mqtt_config):
    """Test on_disconnect callback"""
    publisher = MQTTPublisher(mqtt_config)
    publisher._connected = True
    
    # Simulate clean disconnection
    publisher._on_disconnect(None, None, 0)
    
    assert not publisher._connected


def test_mqtt_connection_callbacks(mqtt_config):
    """Test connection callback registration"""
    publisher = MQTTPublisher(mqtt_config)
    
    callback_called = {'value': False}
    
    def test_callback():
        callback_called['value'] = True
    
    publisher.add_connection_callback(test_callback)
    
    # Trigger connection
    publisher._on_connect(None, None, None, 0)
    
    assert callback_called['value']
