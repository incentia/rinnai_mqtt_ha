import json
import logging
from typing import Optional
from .mqtt_client import MQTTClientBase
from processors.message_processor import DeviceDataObserver
import time
import ssl


class LocalClient(MQTTClientBase, DeviceDataObserver):
    def __init__(self, config, rinnai_client):
        super().__init__("rinnai_ha_local")
        self.config = config
        self.rinnai_client = rinnai_client
        self.topics = config.get_local_topics()
        self.device_data = {}
        self.rinnai_client.message_processor.register_observer(self)

        if self.config.LOCAL_MQTT_TLS :
            self.client.tls_set(
                cert_reqs=ssl.CERT_NONE,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )

        if self.config.LOCAL_MQTT_USERNAME and self.config.LOCAL_MQTT_PASSWORD:
            self.client.username_pw_set(
                self.config.LOCAL_MQTT_USERNAME, self.config.LOCAL_MQTT_PASSWORD)

    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Local MQTT connect status: {rc}")
        if rc == 0:
            # Subscribe to all local topics
            for topic in self.topics.values():
                self.subscribe(topic)
        time.sleep(1)
        self.rinnai_client.set_default_status()

    def on_message(self, client, userdata, msg):
        try:
            action = msg.topic.split('/')[-2]
            if action == 'temp':
                temperature = int(msg.payload.decode())
                heat_type = msg.topic.split('/')[-1]
                self.rinnai_client.set_temperature(heat_type, temperature)
            elif action == 'mode':
                mode = msg.topic.split('/')[-1]
                self.rinnai_client.set_mode(mode)
        except Exception as e:
            logging.error(f"Local MQTT set failed: {e}")


    def update(self, device_data: dict) -> None:
        """Update device data from MessageProcessor."""
        # 检查是否有新的 device_data，且状态数据不为空
        if device_data:
            if device_data.get("state"):
                self.device_data["state"] = device_data["state"]
                self.publish_state(self.device_data["state"])

            if device_data.get("gas"):
                self.device_data["gas"] = device_data["gas"]
                self.publish_gas_consumption(self.device_data["gas"])

            if device_data.get("supplyTime"):
                self.device_data["supplyTime"] = device_data["supplyTime"]
                self.publish_supply_time(self.device_data["supplyTime"])
        else:
            logging.warning("Received empty device data; no updates made.")


    def publish_state(self, state_data: dict):
        """Publish device state to local MQTT broker."""
        self.publish(
            self.topics["state"],
            json.dumps(state_data, ensure_ascii=False)
        )
        logging.info(f"Published state to local MQTT: {state_data}")

    def publish_gas_consumption(self, gas_data: dict):
        """Publish gas consumption to local MQTT broker."""
        self.publish(
            self.topics["gas"],
            json.dumps(gas_data, ensure_ascii=False)
        )
        logging.info(f"Published gas consumption to local MQTT: {gas_data}")

    def publish_supply_time(self, supply_time_data: dict):
        """Publish supply time to local MQTT broker."""
        self.publish(
            self.topics["supplyTime"],
            json.dumps(supply_time_data, ensure_ascii=False)
        )
        logging.info(
            f"Published supply time to local MQTT: {supply_time_data}")
