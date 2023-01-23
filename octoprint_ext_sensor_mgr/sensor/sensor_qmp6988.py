from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from piqmp6988.smbus_intf import Smbus
import piqmp6988 as PiQMP6988
import copy

class Qmp6988(Sensor):
    _is_config_params_init = False
    
    def __init__(self):
        super().__init__()
        self.type = SensorType.QMP6988
        self.output_type =  SensorOutputType.TEMPERATURE | SensorOutputType.PRESSURE
        self.output_type_unit = None
        self.sensor_intf: PiQMP6988.PiQmp6988 = None
    
    def __del__(self):
        pass
    
    def reset(self):
        super().reset()
    
    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(super(Qmp6988, cls).config_params())
            
            max_readings_cfg = cls._config_params['max_readings']
            cls._config_params['max_readings'] = ConfigProperty(
                data_type=max_readings_cfg.data_type, value_list=max_readings_cfg.value_list, default_value=60, label=max_readings_cfg.label)
            
            cls._config_params['bus_num'] = ConfigProperty(
                data_type=int, value_list=[], default_value=1, label='I2C bus number')
            cls._config_params['i2c_addr'] = ConfigProperty(data_type=PiQMP6988.Address, value_list=[a for a in PiQMP6988.Address],
                                                            default_value=PiQMP6988.Address.LOW, label='I2C address (in decimal)')
            cls._config_params['temp_sampling'] = ConfigProperty(data_type=PiQMP6988.Oversampling, value_list=[o for o in PiQMP6988.Oversampling],
                                                                 default_value=PiQMP6988.Oversampling.X4, label='Temperature sampling')
            cls._config_params['psr_sampling'] = ConfigProperty(data_type=PiQMP6988.Oversampling, value_list=[o for o in PiQMP6988.Oversampling],
                                                                default_value=PiQMP6988.Oversampling.X32, label='Pressure sampling')
            cls._config_params['filter'] = ConfigProperty(data_type=PiQMP6988.Filter, value_list=[f for f in PiQMP6988.Filter],
                                                          default_value=PiQMP6988.Filter.COEFFECT_32, label='Filter')
            cls._config_params['pow_mode'] = ConfigProperty(data_type=PiQMP6988.Powermode, value_list=[f for f in PiQMP6988.Powermode],
                                                            default_value=PiQMP6988.Powermode.NORMAL, label='Power Mode')
            
            cls._is_config_params_init = True
        return cls._config_params
    
    def output_config(self) -> dict():
        if self.output_type_unit is not None:
            return self.output_type_unit
        
        config = dict()
        if SensorOutputType.TEMPERATURE in self.output_type:
            config['temp'] = dict(type=SensorOutputType.TEMPERATURE.name, unit='C')
        if SensorOutputType.PRESSURE in self.output_type:
            config['psr'] = dict(type=SensorOutputType.PRESSURE.name, unit='Pa')
        self.output_type_unit = config
        
        return config
    
    def _configure(self, config: dict):
        self.bus_num = Qmp6988.convert_value_type(config, 'bus_num')
        self.i2c_addr = Qmp6988.convert_value_type(config, 'i2c_addr')
        self.temp_sampling = Qmp6988.convert_value_type(config, 'temp_sampling')
        self.psr_sampling = Qmp6988.convert_value_type(config, 'psr_sampling')
        self.filter = Qmp6988.convert_value_type(config, 'filter')
        self.pow_mode = Qmp6988.convert_value_type(config, 'pow_mode')
        
        qmp_config = dict(temperature=self.temp_sampling.value,
                      pressure=self.psr_sampling.value, filter=self.filter.value, mode=self.pow_mode.value)
        
        self.init_history_reading(Qmp6988.convert_value_type(config, 'max_readings'))
        
        if self.i2c_addr is not None:
            self.sensor_intf = PiQMP6988.PiQmp6988(Smbus(), qmp_config)
        
        is_configured = self.sensor_intf is not None
        return is_configured
    
    def _after_toggle(self):
        if self.sensor_intf is None:
            return
        
    def _postprc_read(self, reading):
        if reading is None:
            return None
        return dict(temp=reading['temperature'], psr=reading['pressure'])
    
    def _read(self):
        if self.sensor_intf is None:
            return
        return self.sensor_intf.read()
    
    def _write(self):
        pass