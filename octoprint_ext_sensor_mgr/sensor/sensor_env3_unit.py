from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.sensor_sht30 import Sht30
from octoprint_ext_sensor_mgr.sensor.sensor_qmp6988 import Qmp6988
import copy

class Env3Unit(Sensor):
    _is_config_params_init = False
    
    def __init__(self):
        super().__init__()
        self.serial_dev = None
        self.type = SensorType.ENV3_UNIT
        self.output_type =  SensorOutputType.TEMPERATURE | SensorOutputType.HUMIDITY | SensorOutputType.PRESSURE
        self.output_type_unit = None
        self.qmp6988: Qmp6988 = Qmp6988()
        self.sht30: Sht30 = Sht30()
    
    def __del__(self):
        pass
    
    def reset(self):
        super().reset()
    
    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(super(Env3Unit, cls).config_params())
            sht30_config = Sht30.config_params()
            qmp6988_config = Qmp6988.config_params()
            # prefix config to prevent conflicts
            for k, v in sht30_config.items():
                cls._config_params['sht30_' + k] = v
            for k, v in qmp6988_config.items():
                cls._config_params['qmp6988_' + k] = v
            
            max_readings_cfg = cls._config_params['max_readings']
            prop = ConfigProperty(
                data_type=max_readings_cfg.data_type, value_list=max_readings_cfg.value_list, default_value=60, label=max_readings_cfg.label)
            cls._config_params['max_readings'] = prop
            cls._config_params['sht30_max_readings'] = prop
            cls._config_params['qmp6988_max_readings'] = prop
            
            cls._is_config_params_init = True
        return cls._config_params
    
    def output_config(self) -> dict():
        if self.output_type_unit is not None:
            return self.output_type_unit
        
        config = dict()
        if SensorOutputType.TEMPERATURE in self.output_type:
            config['sht30_temp'] = dict(type=SensorOutputType.TEMPERATURE.name, unit='C')
            config['qmp6988_temp'] = dict(type=SensorOutputType.TEMPERATURE.name, unit='C')
        if SensorOutputType.HUMIDITY in self.output_type:
            config['hum'] = dict(type=SensorOutputType.HUMIDITY.name, unit='%')
        if SensorOutputType.PRESSURE in self.output_type:
            config['psr'] = dict(type=SensorOutputType.PRESSURE.name, unit='Pa')
        self.output_type_unit = config
        
        return config
    
    def _configure(self, config: dict):
        sht30_config = { k[6:]: v for k, v in config.items() if k.startswith('sht30_') }
        qmp6988_config = { k[8:]: v for k, v in config.items() if k.startswith('qmp6988_') }
        self.sht30.configure(sht30_config)
        self.qmp6988.configure(qmp6988_config)
        
        self.init_history_reading(Env3Unit.convert_value_type(config, 'max_readings'))
        
        is_configured = self.sht30.is_configured and self.qmp6988.is_configured
        return is_configured
    
    def _after_toggle(self):
        if self.sht30 is not None:
            self.sht30.toggle(self.enabled)
        if self.qmp6988 is not None:
            self.qmp6988.toggle(self.enabled)
        
    def _postprc_read(self, reading):
        if reading is None:
            return None
        return dict(temp=dict(sht30=reading['sht30_temp'], qmp6988=reading['qmp6988_temp']), hum=reading['hum'], psr=reading['psr'])
    
    def _read(self):
        out = dict()
        sht30_out = self.sht30.read()
        out['sht30_temp'] = sht30_out['temp']
        out['hum'] = sht30_out['hum']
        qmp6988_out = self.qmp6988.read()
        out['qmp6988_temp'] = qmp6988_out['temperature']
        out['psr'] = qmp6988_out['humidity']
        
        return out
    
    def _write(self):
        pass