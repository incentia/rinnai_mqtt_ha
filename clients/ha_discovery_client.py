import ssl
import json
import logging
from .mqtt_client import MQTTClientBase


class RinnaiHomeAssistantDiscovery(MQTTClientBase):
    def __init__(self,config):
        super().__init__("rinnai_ha_discovery")
        self.config = config
        self.mqtt_host = self.config.LOCAL_MQTT_HOST
        self.mqtt_port = self.config.LOCAL_MQTT_PORT
        self.unique_id = "rinnai_heater"
        self.discovery_prefix = "homeassistant"
        
        if self.config.LOCAL_MQTT_TLS:
            self.client.tls_set(
                cert_reqs=ssl.CERT_NONE,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            self.client.tls_insecure_set(True)
            logging.info("Local MQTT TLS enabled")

        if self.config.LOCAL_MQTT_USERNAME and self.config.LOCAL_MQTT_PASSWORD:
            self.client.username_pw_set(
                self.config.LOCAL_MQTT_USERNAME, self.config.LOCAL_MQTT_PASSWORD)
            logging.info("Local MQTT authentication enabled")
        
    
    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"HomeAssistant MQTT connect status: {rc}")

    def on_message(self, client, userdata, msg):
        pass
    def generate_config(self, component_type, object_id, name, topic, config_type='sensor', unit=None):
        """
        生成通用配置
        """
        base_topic = f"{self.discovery_prefix}/{component_type}/rinnai_{object_id}"

        config = {
            "name": name,
            "unique_id": f"{self.unique_id}_{object_id}",
            "state_topic": self.config.get_local_topics().get("state"),
            "value_template": f"{{{{ value_json.{object_id} }}}}",
            "device": {
                "identifiers": [self.unique_id],
                "name": "Rinnai Heater",
                "manufacturer": "Rinnai",
                "model": "RUS-R**E86"
            }
        }
        # 添加单位
        if unit:
            config["unit_of_measurement"] = unit

        if config_type == 'sensor' and object_id == 'gasConsumption':
            config.update({
                "state_topic": self.config.get_local_topics().get("gas"),
                "value_template": f"{{{{ (value_json.{object_id} | float) / 10000 }}}}",
                "unit_of_measurement": "m³",
                "device_class": "gas"
            })
        elif config_type == 'sensor' and 'supplyTime' in object_id:

            config.update({
                "state_topic": self.config.get_local_topics().get("supplyTime"),
                "value_template": f"{{{{ value_json.{object_id.split('/')[-1]} }}}}",
            })


        if config_type == 'number' and object_id == 'hotWaterTempSetting':
            config.update({
                "command_topic": topic,
                "min": 35,
                "max": 60,
                "step": 1,
                "unit_of_measurement": "°C"
            })
        elif config_type == 'number' and (object_id == 'heatingTempSettingNM' or object_id == 'heatingTempSettingHES'):
            config.update({
                "command_topic": topic,
                "min": 45,
                "max": 70,
                "step": 1,
                "unit_of_measurement": "°C"
            })
        elif config_type == 'switch':
            config.update({
                "state_topic": self.config.get_local_topics().get("state"),
                "command_topic": topic,
                "payload_on": "ON",
                "payload_off": "OFF",
                "value_template": self.get_switch_value_template(object_id)
            })

        return f"{base_topic}/config", json.dumps(config)


    def get_switch_value_template(self, object_id):
        if object_id == "power":
            return "{% if value_json.operationMode in ['关机'] %}OFF{% else %}ON{% endif %}"
        else:
            return "{% if value_json.temporaryCycleInsulationSetting in ['关'] %}OFF{% else %}ON{% endif %}"




    def publish_discovery_configs(self):
        """
        发布Home Assistant自动发现配置
        """
        self.connect(self.mqtt_host, self.mqtt_port, 60)

        # 传感器配置
        sensors = [
            ("热水模式", "operationMode", None),
            ("燃烧器状态", "burningState", None),
            ("当前水温设定", "hotWaterTempSetting", "°C"),
            ("耗气量", "gasConsumption", "m³"),
            ("一键循环","temporaryCycleInsulationSetting", None),
            ("优先键","priority", None),
            ("儿童锁","childLock", None),
            ("循环模式","cycleModeSetting", None),
            ("网络状态","online", None),
            ("预约循环","cycleReservationSetting", None),
            ("预约循环时间","cycleReservationTimeSetting", None),
            ("浴缸注水量设定", "bathWaterInjectionSetting", "L"),
            ("浴缸注水", "waterInjectionStatus", "L"),
            ("浴缸剩余注水量", "remainingWater", "L"),
            ("浴缸注水完成", "waterInjectionCompleteConfirm", None),
            ("热水可用", "hotWaterUseableSign", None),
            ("龙头未关", "faucetNotCloseSign", None),
            ("错误代码", "errorCode", None)
        ]
        for label, object_id, unit in sensors:
            topic, config = self.generate_config(
                'sensor',
                object_id,
                f"{label}",
                None,
                'sensor',
                unit
            )
            self.publish(topic, config, retain=True)

        #温度控制
        temp_controls = [
            ("热水温度", "hotWaterTempSetting",self.config.get_local_topics().get("hotWaterTempSetting"))
        ]


        for label, object_id, topic in temp_controls:
            number_topic, number_config = self.generate_config(
                'number',
                object_id,
                f"{label}",
                topic,
                'number'
            )
            self.publish(number_topic, number_config, retain=True)

        # 模式控制
        mode_controls = [
            ("热水器开关", "power", self.config.get_local_topics().get("power")),
            ("一键循环", "temporaryCycleInsulationSetting", self.config.get_local_topics().get("temporaryCycleInsulationSetting"))
        ]

        for label, object_id, topic in mode_controls:
            switch_topic, switch_config = self.generate_config(
                'switch',
                object_id,
                f"{label}",
                topic,
                'switch'
            )
            self.publish(switch_topic, switch_config, retain=True)

        self.disconnect()
