from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.util.dev import serial_dev_list
from pms7003 import Pms7003Sensor
import copy


class Pms7003(Sensor):
    _is_config_params_init = False

    def __init__(self):
        super().__init__()
        self.serial_dev = None
        self.sensor_intf: Pms7003Sensor = None
        self.type = SensorType.PMS7003
        self.output_type = SensorOutputType.PM1_0 | SensorOutputType.PM2_5 | SensorOutputType.PM10
        self.output_type_unit = None

    def __del__(self):
        if self.sensor_intf is not None:
            self.sensor_intf.close()

    def reset(self):
        super().reset()

    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(
                super(Pms7003, cls).config_params())

            cls._config_params['max_readings'].default_value = 60
            cls._config_params['serial_dev'] = ConfigProperty(data_type=str, value_list=serial_dev_list(
            ), default_value=None, label='Serial Device (/dev/ttySx)', group_seq=('Sensor Configuration',))

            cls._is_config_params_init = True
        return cls._config_params

    def output_config(self) -> dict():
        if self.output_type_unit is not None:
            return self.output_type_unit

        config = dict()
        if SensorOutputType.PM2_5 in self.output_type:
            config['pm2_5'] = dict(
                type=SensorOutputType.PM2_5.name, unit='ug/m3')
        if SensorOutputType.PM1_0 in self.output_type:
            config['pm1_0'] = dict(
                type=SensorOutputType.PM1_0.name, unit='ug/m3')
        if SensorOutputType.PM10 in self.output_type:
            config['pm10'] = dict(
                type=SensorOutputType.PM10.name, unit='ug/m3')
        self.output_type_unit = config

        return config

    def _configure(self, config: dict):
        self.serial_dev = Pms7003.convert_value_type(config, 'serial_dev')
        self.init_history_reading(
            Pms7003.convert_value_type(config, 'max_readings'))
        self.sensor_intf = Pms7003Sensor(self.serial_dev)

        is_configured = self.sensor_intf is not None
        return is_configured

    def _postprc_read(self, reading):
        return dict(pm1_0=reading['pm1_0'], pm2_5=reading['pm2_5'], pm10=reading['pm10'])

    def _read(self):
        return self.sensor_intf.read()

    def _write(self):
        pass
