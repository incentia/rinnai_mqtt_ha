import json
import logging
from typing import Dict, Any, List
import utils.constants as const


class DeviceDataObserver:
    def update(self, device_data: Dict[str, Any]) -> None:
        pass


class MessageProcessor:
    def __init__(self):
        self.device_data = {
            "state": {},
            "gas": {},
            "supplyTime": {}
        }
        self.observers: List[DeviceDataObserver] = []

    def register_observer(self, observer: DeviceDataObserver) -> None:
        self.observers.append(observer)

    def notify_observers(self) -> None:
        for observer in self.observers:
            observer.update(self.device_data)

    def _process_hex_value(self, value: str, param_name: str) -> str:
        """Convert hex value to decimal string."""
        try:
            if "hotWaterTempSetting" in param_name:
              const.CURRENT_HOTWATER_TEMP = int(value, 16)
            return str(int(value, 16))
        except ValueError as e:
            logging.warning(f"Invalid hex value for {param_name}: {value}")
            raise ValueError(
                f"Invalid hex value for {param_name}: {value}") from e

    def _get_operation_mode(self, mode_code: str) -> str:
        mode_mapping = const.OPERATION_MODES
        return mode_mapping.get(mode_code, f"invalid ({mode_code})")

    def _get_burning_state(self, state_code: str) -> str:
        state_mapping = const.BURNING_STATES
        return state_mapping.get(state_code, f"invalid ({state_code})")

    def _get_online_status(self, status: str) -> str:
        online_status_mapping = const.ONLINE_STATUS
        return online_status_mapping.get(status, f"invalid ({status})")

    def _get_temporaryCycleInsulationSetting(self, status: str) -> str:
        temporaryCycleInsulationSetting_mapping = const.SWITCH_STATUS
        return temporaryCycleInsulationSetting_mapping.get(status, f"invalid ({status})")

    def _get_childLock(self, status: str) -> str:
        childLock_mapping = const.SWITCH_STATUS
        return childLock_mapping.get(status, f"invalid ({status})")

    def _get_priority(self, status: str) -> str:
        priority_mapping = const.SWITCH_STATUS
        return priority_mapping.get(status, f"invalid ({status})")

    def _get_cycleModeSetting(self, status: str) -> str:
        cycleModeSetting_mapping = const.CYCLE_MODE
        return cycleModeSetting_mapping.get(status, f"invalid ({status})")

    def _get_cycleReservationSetting(self, status: str) -> str:
        cycleReservationSetting_mapping = const.SWITCH_STATUS
        return cycleReservationSetting_mapping.get(status, f"invalid ({status})")

    def _get_cycleReservationTimeSetting(self, status: str) -> str:
        result = status.split();
        status_inv = ""
        for tmp in result:
            status_inv = tmp + status_inv
            
        #logging.info(f"MG {status} vs {status_inv}")

        #bin_str = format(int(status_inv, 16), '016b')
            
        #logging.info(f"MG {status} vs {bin_str}")

        return (status_inv)

    def _get_waterInjectionCompleteConfirm(self, status: str) -> str:
        waterInjectionCompleteConfirm_mapping = const.COMPLETE_CONFIRM
        return waterInjectionCompleteConfirm_mapping.get(status, f"invalid ({status})")

    def _get_hotWaterUseableSign(self, status: str) -> str:
        hotWaterUseableSign_mapping = const.USEABLE
        return hotWaterUseableSign_mapping.get(status, f"invalid ({status})")

    def _get_faucetNotCloseSign(self, status: str) -> str:
        faucetNotCloseSign_mapping = const.SWITCH_STATUS
        return faucetNotCloseSign_mapping.get(status, f"invalid ({status})")

    def _get_errorCode(self, status: str) -> str:
        #faucetNotCloseSign_mapping = const.SWITCH_STATUS
        #return faucetNotCloseSign_mapping.get(status, f"invalid ({status})")
        return (status)

    def _process_device_info(self, parsed_data: Dict[str, Any]) -> None:
        """Process device information from parsed message."""
        state_mapping = {
            'operationMode': self._get_operation_mode,
            'roomTempControl': lambda x: self._process_hex_value(x, 'roomTempControl'),
            'heatingOutWaterTempControl': lambda x: self._process_hex_value(x, 'heatingOutWaterTempControl'),
            'burningState': self._get_burning_state,
            'hotWaterTempSetting': lambda x: self._process_hex_value(x, 'hotWaterTempSetting'),
            'heatingTempSettingNM': lambda x: self._process_hex_value(x, 'heatingTempSettingNM'),
            'heatingTempSettingHES': lambda x: self._process_hex_value(x, 'heatingTempSettingHES'),
            'temporaryCycleInsulationSetting': self._get_temporaryCycleInsulationSetting,
            'childLock': self._get_childLock,
            'priority' : self._get_priority,
            'cycleModeSetting': self._get_cycleModeSetting,
            'cycleReservationSetting': self._get_cycleReservationSetting,
            'cycleReservationTimeSetting': self._get_cycleReservationTimeSetting,
            'bathWaterInjectionSetting': lambda x: self._process_hex_value(x, 'bathWaterInjectionSetting'),
            'waterInjectionStatus': lambda x: self._process_hex_value(x, 'waterInjectionStatus'),
            'remainingWater': lambda x: self._process_hex_value(x, 'remainingWater'),
            'waterInjectionCompleteConfirm': self._get_waterInjectionCompleteConfirm,
            'hotWaterUseableSign': self._get_hotWaterUseableSign,
            'faucetNotCloseSign': self._get_faucetNotCloseSign,
            'errorCode': self._get_errorCode
        }

        for param in parsed_data.get('enl', []):
            try:
                param_id = param.get('id')
                param_data = param.get('data')

                if not param_id or not param_data:
                    continue

                if param_id in state_mapping:
                    self.device_data["state"][param_id] = state_mapping[param_id](
                        param_data)

            except Exception as e:
                logging.error(f"Error processing parameter {param_id}: {e}")


    def _process_energy_data(self, parsed_data: Dict[str, Any]) -> None:
        """Process energy consumption data."""
        time_parameters = const.TIME_PARAMETERS

        for param in parsed_data.get('egy', []):
            if not isinstance(param, dict):
                logging.warning(f"Skipping invalid parameter entry: {param}")
                continue

            # Process gas consumption
            if gas_value := param.get('gasConsumption'):
                try:
                    self.device_data["gas"]["gasConsumption"] = self._process_hex_value(
                        gas_value, 'gasConsumption')
                except ValueError:
                    continue

            # Process time-related parameters
            for key in param.keys() & time_parameters:
                try:
                    self.device_data["supplyTime"][key] = self._process_hex_value(
                        param[key], key)
                except ValueError:
                    logging.warning(f"Failed to process {key}")
                    continue

    def process_message(self, msg):
        """Process incoming Rinnai device messages."""
        try:
            parsed_data = json.loads(msg.payload.decode('utf-8'))
            parsed_topic = msg.topic.split('/')[-2]

            if not parsed_data or not parsed_topic:
                logging.warning("Received invalid or empty message")
                return

            if (parsed_topic == 'sys' and
                    parsed_data.get('ptn') == "JA3"):
                self.device_data["state"]['online'] = self._get_online_status(parsed_data.get('online'))
                self.notify_observers()  # Notify observers after processing device info

            if (parsed_topic == 'res' and
                parsed_data.get('enl') and
                    parsed_data.get('code') == "FFFF"):
                self._process_device_info(parsed_data)
                self.notify_observers()  # Notify observers after processing device info

            elif (parsed_topic == 'inf' and
                    parsed_data.get('egy') and
                    parsed_data.get('ptn') == "J05"):
                self._process_energy_data(parsed_data)
                self.notify_observers()  # Notify observers after processing energy data

        except json.JSONDecodeError:
            logging.error("Failed to parse JSON message")
        except Exception as e:
            logging.error(f"Unexpected error in message processing: {e}")
