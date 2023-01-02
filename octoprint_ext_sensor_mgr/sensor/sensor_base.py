from collections import deque
from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty


class Sensor:
    _config_params = dict()
    _is_config_params_init = False

    def __init__(self) -> None:
        super().__init__()
        self.enabled = False
        self.is_configured = False
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
    def config_params(cls=None):
        cls = cls if cls is not None else Sensor
        if not cls._is_config_params_init:
            cls._config_params['max_readings'] = ConfigProperty(
                data_type=type(int), value_list=[], default_value=1)
            cls._is_config_params_init = True
        return cls._config_params

    @classmethod
    def convert_value_type(cls, config: dict, param: str):
        default = cls.config_params()[param].default_value
        type = cls.config_params()[param].data_type
        value = config[param] if param in config else default
        
        try:
            if type is type(int):
                return int(value)
            elif type is type(str):
                return str(value)
            else:
                return value
        except TypeError:
            return value

    def init_history_reading(self, max_readings=1):
        self.max_readings = max_readings
        self.past_readings = deque(maxlen=self.max_readings)

    def history_reading_list(self):
        return list(self.past_readings)

    def allow_history(self):
        return self.max_readings > 1

    def _add_reading(self, reading):
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

    def read(self):
        if self.is_configured and self.enabled:
            return self._read(self)

    def _write(self):
        raise NotImplementedError()

    def write(self):
        if self.is_configured and self.enabled:
            return self._write(self)
