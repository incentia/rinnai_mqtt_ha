# MQTT Topics
TOPIC_TYPES = {
    "DEVICE_INFO": "inf",
    "ENERGY_DATA": "stg",
    "DEVICE_CONTROL": "set"
}

# Device States
OPERATION_MODES = {
    "0": "关机",
    "A0":  "普通模式",
    "90":  "淋浴模式",
    "88":  "水温按摩模式",
    "82":  "低温模式",
    "81":  "厨房模式",
    "84":  "浴缸模式",
    "E0":  "普通模式+循环",
    "D0":  "淋浴模式+循环",
    "C2":  "低温模式+循环",
    "C1":  "厨房模式+循环"
    
}

CYCLE_MODE = {
    "0": "标准循环",
    "1": "舒适循环",
    "2": "节能循环"
}

BURNING_STATES = {
    "0": "待机中",
    "1": "燃烧中",
    "2": "异常"
}

ONLINE_STATUS = {
    "0": "离线",
    "1": "在线",
}

SWITCH_STATUS = {
    "0": "关",
    "1": "开"
}

# Message Types
TIME_PARAMETERS = {
    'totalPowerSupplyTime',
    'actualUseTime',
    'totalHeatingBurningTime',
    'burningtotalHotWaterBurningTimeState',
    'heatingBurningTimes',
    'hotWaterBurningTimes'
}

STATE_PARAMETERS = {
    'operationMode',
    'roomTempControl',
    'heatingOutWaterTempControl',
    'burningState',
    'hotWaterTempSetting',
    'heatingTempSettingNM',
    'heatingTempSettingHES',
    'cycleReservationSetting',
    'temporaryCycleInsulationSetting',
    'childLock',
    'priority',
    'cycleModeSetting'
    }

CURRENT_HOTWATER_TEMP = 39

HOST = "https://iot.rinnai.com.cn/app"
LOGIN_URL = f"{HOST}/V1/login"
INFO_URL = f"{HOST}/V1/device/list"
PROCESS_PARAMETER_URL = f"{HOST}/V1/device/processParameter"
# 林内智家app内置accessKey
AK = "A39C66706B83CCF0C0EE3CB23A39454D" 
