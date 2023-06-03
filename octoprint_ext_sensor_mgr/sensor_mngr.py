from octoprint_ext_sensor_mgr.logging import ContextLevel, Logging
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.util.config import parse_sensor_config, sensor_cls


class SensorManager:
    def __init__(self, is_mock_test=False, sensor_id_seed=1, logger: Logging = None):
        self._sensor_list = []
        self._is_mock_test = is_mock_test
        self.sensor_id_seed = sensor_id_seed
        self._logger = Logging() if logger is None else logger

    def handle_msg(self, msg) -> Sensor:
        self._logger.debug(
            context="SensorManager.handle_msg: msg", ref_object=msg)

        sensor_type = SensorType(int(msg['sensorType']))

        try:
            sensor_id = int(msg['sensorId'])
        except (TypeError, ValueError) as err:
            if msg['sensorId'] is not None:
                self._logger.debug(
                    context="SensorManager.handle_msg: invalid sensor id provided, must be None or int", context_level=ContextLevel.ERROR)
                return
        sensor_id = msg['sensorId']
        if sensor_type == SensorType.NOT_SET:
            self._logger.debug(
                context="SensorManager.handle_msg: ignore unset sensor", context_level=ContextLevel.DEBUG)
            return

        enabled = msg['enabled']
        config = parse_sensor_config(msg['config'])
        sensor = self.sensor(sensor_id)
        self._logger.debug(
            context="SensorManager.handle_msg: check existing sensor?", ref_object=sensor is not None)
        self._logger.debug(
            context="SensorManager.handle_msg: parsed config", ref_object=config)

        # new or existing unloaded sensor
        if sensor is None:
            constructor = sensor_cls(sensor_type, is_test=self._is_mock_test)
            if constructor is None:
                self._logger.debug(context="SensorManager.handle_msg: new sensor - (1) constructor is not defined",
                                   ref_object=constructor, context_level=ContextLevel.ERROR)
                self._logger.debug(context="SensorManager.handle_msg: new sensor - (2) sensor type",
                                   ref_object=sensor_type, context_level=ContextLevel.ERROR)
                self._logger.debug(context="SensorManager.handle_msg: new sensor - (3) is mock test",
                                   ref_object=self._is_mock_test, context_level=ContextLevel.ERROR)
                return
            sensor = constructor()
            sensor.id = sensor_id if sensor_id is not None else self._gen_sensor_id()
            self._logger.debug(
                context="SensorManager.handle_msg: constructed new sensor", ref_object=sensor)

        if 'input_values' in msg:
            input_config = sensor.input_config()
            if input_config is not None:
                for (input_id, conf) in input_config.items():
                    sensor.preload_input(
                        input_id, msg['input_values'][input_id] if msg['input_values'] is not None and input_id in msg['input_values'] else conf['value'])
                self._logger.debug(
                    context="SensorManager.handle_msg: processed initial inputs", ref_object=sensor.input_config())

        sensor.toggle(enabled)
        sensor.configure(config)
        self.add_sensor(sensor)
        self._logger.debug(
            context="SensorManager.handle_msg: sensor", ref_object=sensor)

        return sensor

    def _gen_sensor_id(self):
        gen_id = self.sensor_id_seed

        while self.is_id_exist(gen_id):
            gen_id = gen_id + 1
        return gen_id

    def is_id_exist(self, sensor_id: int):
        return any(s.id == sensor_id for s in self._sensor_list)

    def add_sensor(self, sensor: Sensor):
        if not self.is_id_exist(sensor.id):
            self._sensor_list.append(sensor)

    def remv_sensor(self, sensor: Sensor):
        if sensor in self._sensor_list:
            self._sensor_list.remove(sensor)

    def remv_sensor(self, sensor_id: int):
        if self.is_id_exist(sensor_id):
            sensor = self.sensor(sensor_id)
            self._sensor_list.remove(sensor)

    def is_pin_used(self, pin):
        return any(pin in s.pin_list() for s in self._sensor_list)

    def sensor(self, sensor_id: int) -> Sensor:
        return next(
            iter([sensor for sensor in self._sensor_list if sensor.id == sensor_id]),
            None
        )

    def sensor_list(self, sensor_type: SensorType = None):
        if sensor_type is None:
            return self._sensor_list
        return list(filter(lambda s: s.type == sensor_type, self._sensor_list))
