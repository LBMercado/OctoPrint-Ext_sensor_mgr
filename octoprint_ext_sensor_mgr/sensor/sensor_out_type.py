from enum import Flag, auto


class SensorOutputType(Flag):
    TEMPERATURE = auto()
    HUMIDITY = auto()
    PRESSURE = auto()
    PM1_0 = auto()
    PM2_5 = auto()
    PM10 = auto()
    TOGGLE = auto()
