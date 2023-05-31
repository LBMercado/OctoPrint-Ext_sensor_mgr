from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_in_type import SensorInputType
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.util.dev import gpio_dev_list
import gpiod
import copy


class OnOff(Sensor):
    _is_config_params_init = False

    def __init__(self):
        super().__init__()
        self.type = SensorType.ONOFF
        self.output_type = SensorOutputType.TOGGLE
        self.output_type_unit = None
        self.input_type = SensorInputType.TOGGLE
        self.is_on = None

    def __del__(self):
        pass

    def reset(self):
        super().reset()

    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(
                super(OnOff, cls).config_params())
            cls._config_params['max_readings'].default_value = 1

            group_seq = ('Sensor Configuration',)

            cls._config_params['gpio_device'] = ConfigProperty(data_type=str, value_list=gpio_dev_list(
            ), default_value=None, label='GPIO Device', group_seq=group_seq)
            cls._config_params['pin'] = ConfigProperty(data_type=int, value_list=[
            ], default_value=None, label='Pin (WiringPi pin)', group_seq=group_seq)
            cls._config_params['is_active_low'] = ConfigProperty(data_type=bool, value_list=[
                True, False], default_value=False, label='Is active low?', group_seq=group_seq)

            cls._is_config_params_init = True
        return cls._config_params

    def output_config(self) -> dict():
        if self.output_type_unit is not None:
            return self.output_type_unit

        config = dict()
        if SensorOutputType.TOGGLE in self.output_type:
            config['toggle'] = dict(
                type=SensorOutputType.TOGGLE.name, unit=None)
        self.output_type_unit = config

        return config

    def input_config(self) -> dict():
        config = super().input_config()
        if config is not None:
            return config

        config = dict()
        if SensorInputType.TOGGLE in self.input_type:
            config['toggle'] = dict(
                name='Toggle', datatype=bool)
        self._input_config = config

        return config

    def _configure(self, config: dict):
        self.board_pin = OnOff.convert_value_type(config, 'pin')
        self.gpio_device = OnOff.convert_value_type(config, 'gpio_device')
        self.is_active_low = OnOff.convert_value_type(config, 'is_active_low')
        self.init_history_reading(
            OnOff.convert_value_type(config, 'max_readings'))

        is_configured = self.board_pin is not None and self.gpio_device is not None
        if is_configured:
            chip = gpiod.chip(self.gpio_device)
            self.gpiod_line = chip.get_line(self.board_pin)
            self.gpiod_req = gpiod.line_request()
            self.gpiod_req.consumer = 'sensor_onoff' + str(self.id)
            self.gpiod_req.request_type = gpiod.line_request.DIRECTION_OUTPUT

        return is_configured

    def _after_toggle(self):
        if not self.enabled:
            self.gpiod_line.release()

    def _postprc_read(self, reading):
        return reading

    def _read(self):
        return dict(toggle=self.is_on)

    def _write(self, input_id, value):
        level = int(not value) if self.is_active_low else int(value)

        if not self.gpiod_line.is_requested():
            self.gpiod_line.request(
                self.gpiod_req, default_val=self.is_active_low)

        self.gpiod_line.set_value(level)
        self.is_on = value
