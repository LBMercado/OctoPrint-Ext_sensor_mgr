from collections import deque
from enum import Enum
from typing import Dict, Union
from datetime import datetime
from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_in_type import SensorInputType
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType


class Sensor:
    _config_params: Dict[str, ConfigProperty] = dict()
    _is_config_params_init = False
    output_type: SensorOutputType

    def __init__(self) -> None:
        super().__init__()
        self.enabled = False
        self.is_configured = False
        self.output_type: SensorOutputType = None
        self.input_type: SensorInputType = None
        self._input_config: dict = None
        self._output_config: dict = None
        self.output_unit_seq = ()
        self.id = None
        self.type = None
        self.init_history_reading()

    def __str__(self) -> str:
        return str(dict(type=self.type, id=str(self.id)))

    """
        configuration parameters possible for giving sensor, returns dict('param':data_type)        
        for list data type, provide possible values
    """
    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:

            group_seq = ('Common',)
            cls._config_params['max_readings'] = ConfigProperty(
                data_type=int, value_list=[], default_value=1, label='Maximum number of readings', group_seq=group_seq)
            cls._config_params['name'] = ConfigProperty(
                data_type=str, value_list=[], default_value='New Sensor', label='Sensor Name', group_seq=group_seq)
            cls._is_config_params_init = True
        return cls._config_params

    @classmethod
    def convert_value_type(cls, config: dict, param: str):
        default = cls.config_params()[param].default_value
        type = cls.config_params()[param].data_type
        value = config[param] if param in config else default

        try:
            if type == int:
                return int(value)
            elif type == str:
                return str(value)
            elif issubclass(type, Enum):
                return type(value)
            else:
                return value
        except TypeError:
            return value

    def output_config(self) -> dict():
        return self._output_config

    def input_config(self) -> dict():
        return self._input_config

    def init_history_reading(self, max_readings=1):
        self.max_readings = max_readings
        self.past_readings = deque(maxlen=self.max_readings)

    def history_reading_list(self):
        return list(self.past_readings)

    def allow_history(self):
        return self.max_readings > 1

    def _add_reading(self, reading: Union[dict, any]):
        if isinstance(reading, type(dict)):
            if 'value' not in reading:
                return
        else:
            reading = dict(value=reading)

        reading['timestamp'] = datetime.timestamp(datetime.now())
        self.past_readings.append(reading)

    def reset(self):
        if self.past_readings is not None:
            self.past_readings.clear()

    def _after_toggle(self):
        pass

    def toggle(self, enable):
        self.enabled = enable
        self._after_toggle()

    def _configure(self, config: dict):
        raise NotImplementedError()

    def configure(self, config: dict):
        self.is_configured = self._configure(config)

    def pin_list(self) -> list:
        raise NotImplementedError()

    def _read(self):
        raise NotImplementedError()

    def _postprc_read(self, reading: dict):
        if reading is not None and self.input_type is not None:
            inputs = dict(
                filter(lambda kv: kv[0] in self._input_config, reading.items()))
            inputs = {k: config['value'] for (k, config) in inputs.items()}
            reading.update(inputs)

        return reading

    def read(self):
        if self.is_configured and self.enabled:
            reading = self._postprc_read(self._read())
            self._add_reading(reading)
            return reading

    def preload_input(self, input_id, value):
        """
        @input_id: specific input in sensor to refer to
        @value: initial value
        """
        config = self.input_config()

        if config is not None and input_id in config:
            config[input_id]['value'] = config[input_id]['datatype'](value)

    def read_inputs(self):
        reading = self.read()
        if reading is not None:
            inputs = dict(
                filter(lambda kv: kv[0] in self._input_config, reading.items()))
            return inputs

    def _write(self, input_id, value):
        raise NotImplementedError()

    def write(self, input_id, value):
        """
        @input_id: specific input in sensor to refer to
        @value: value to write
        """
        config = self.input_config()

        if self.is_configured and self.enabled and config is not None and input_id in config:
            return self._write(input_id, config[input_id]['datatype'](value))
