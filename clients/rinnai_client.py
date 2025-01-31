import ssl
import json
import logging
import utils.constants as const
import time
from .mqtt_client import MQTTClientBase
from processors.message_processor import MessageProcessor


class RinnaiClient(MQTTClientBase):
    def __init__(self, config, message_processor: MessageProcessor):
        super().__init__("rinnai_ha_bridge")
        self.config = config
        self.message_processor = message_processor
        self.topics = config.get_rinnai_topics()
        logging.info(f"Rinnai topics: {self.topics}")

        # Configure TLS
        self.client.tls_set(
            cert_reqs=ssl.CERT_NONE,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        self.client.tls_insecure_set(True)
        self.client.username_pw_set(
            self.config.RINNAI_USERNAME, self.config.RINNAI_PASSWORD)

    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Rinnai MQTT connect status: {rc}")
        if rc == 0:
            for topic in self.topics.values():
                self.subscribe(topic)
        
        # self.set_default_status()
        


    def on_message(self, client, userdata, msg):
        try:
            logging.info(
                f"Rinnai msg topic: {msg.topic}, payload: {json.loads(msg.payload.decode('utf-8'))}")
            self.message_processor.process_message(msg)
        except Exception as e:
            logging.error(f"Rinnai message error: {e}")


    def set_temperature_1(self, data = "00"):
        
        heat_type = "hotWaterTempOperate"
        request_payload = {
            "code": self.config.AUTH_CODE,
            "id": self.config.DEVICE_TYPE,
            "ptn": "J00",
            "enl": [
                {
                    "id": heat_type,
                    "data": data,
                }
            ],

            "sum": "1"
        }
        self.publish(self.topics["set"], json.dumps(request_payload), qos=1)
        logging.info(f"Set {heat_type} temperature with {data}°C")

    def set_temperature(self, heat_type, temperature):
        if not heat_type:
            raise ValueError("Error: heat type not specified")

        data_value = "00"
        
        if (temperature > const.CURRENT_HOTWATER_TEMP):
            data_value = "01"
            
        cnt = 0
        while (temperature != const.CURRENT_HOTWATER_TEMP):
            if (cnt > 0):
                break
            self.set_temperature_1(data_value);
            time.sleep(1)
            cnt = cnt + 1

        logging.info(f"Set {heat_type} temperature to {temperature}°C")


   
    def set_mode(self, mode, status="ON"):
        if not mode:
            raise ValueError("Error: mode not specified")

        data_value = "00"
        if "ON" in status:
            data_value = "01"
            
        request_payload = {
            "code": self.config.AUTH_CODE,
            "id": self.config.DEVICE_TYPE,
            "ptn": "J00", 
            "enl": [
                {
                    "data": data_value,
                    "id": mode
                }
            ],
                      
            "sum": "1"
        }
        self.publish(self.topics["set"], json.dumps(request_payload), qos=1)

    def set_default_status(self):
        default_status = {'enl': []}
        for key, value in self.config.INIT_STATUS.items():
            default_status['enl'].append({'id': key, 'data': value})
            if "hotWaterTempSetting" in key:
                const.CURRENT_HOTWATER_TEMP = int(value, 16)
        self.message_processor._process_device_info(default_status)
        self.message_processor.notify_observers()
