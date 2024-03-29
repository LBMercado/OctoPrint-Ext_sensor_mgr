import copy
import random
from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_pms7003 import Pms7003 as Pms7003Actual
from octoprint_ext_sensor_mgr.sensor.util.dev import serial_dev_list

PM2_5_RANGE = (200, 300)
PM1_0_RANGE = (100, 200)
PM10_RANGE = (300, 400)


class Pms7003(Pms7003Actual):
    _is_config_params_init = False

    def __init__(self):
        super().__init__()

    def __del__(self):
        pass

    def _after_toggle(self):
        pass

    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(
                super(Pms7003, cls).config_params())

            cls._config_params['max_readings'].default_value = 60
            cls._config_params['serial_dev'] = ConfigProperty(data_type=str, value_list=[
                                                              '/dev/ttyS0', '/dev/ttyS1'], default_value=None, label='Serial Device (/dev/ttySx)', group_seq=('Sensor Configuration',))

            cls._is_config_params_init = True
        return cls._config_params

    def _configure(self, config: dict):
        self.serial_dev = Pms7003.convert_value_type(config, 'serial_dev')
        self.init_history_reading(
            Pms7003.convert_value_type(config, 'max_readings'))

        is_configured = True
        return is_configured

    def _read(self):
        pm1_0 = random.randint(PM1_0_RANGE[0], PM1_0_RANGE[1])
        pm2_5 = random.randint(PM2_5_RANGE[0], PM2_5_RANGE[1])
        pm10 = random.randint(PM10_RANGE[0], PM10_RANGE[1])
        ret = dict(pm1_0=pm1_0, pm2_5=pm2_5, pm10=pm10)

        return ret
