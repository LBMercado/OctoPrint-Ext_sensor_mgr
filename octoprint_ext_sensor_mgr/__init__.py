# coding=utf-8
from __future__ import absolute_import
from typing import List

# (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
from octoprint_ext_sensor_mgr.logging import OctoprintLogging
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.util import determine_sensor_config, transform_sensor_config
from octoprint_ext_sensor_mgr.sensor_mngr import SensorManager
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType, SUPPORTED_SENSOR_LIST


class Ext_sensor_mgrPlugin(octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.AssetPlugin,
                           octoprint.plugin.TemplatePlugin,
                           octoprint.plugin.StartupPlugin,
                           octoprint.plugin.SimpleApiPlugin
                           ):

    def init_sensors(self, sensor_list: List[Sensor]):
        self._log("init_sensors: stored sensors = ",
            sensor_list)
        
        for sensor in sensor_list:
            self._log("init_sensors: processing sensor = ",
            sensor)
            ret_sensor = self.sensor_mgr.handle_msg(sensor)
            self._log("init_sensors: done processing sensor = ",
            ret_sensor)
            
        self._log("init_sensors: interface-enabled sensors = ",
            self.sensor_mgr.sensor_list())
    
    # ~~ StartupPlugin mixin
    def on_after_startup(self):
        self._log("Plugin on startup called")
        sensor_seed_id = self._settings.get(["sensor_id_seed"])
        enable_logging = self._settings.get(["enable_logging"])
        enable_mock_test = self._settings.get(["is_mock_test"])
        self.sensor_mgr = SensorManager(enable_mock_test, sensor_seed_id, OctoprintLogging(self._logger, enable_logging))
        self.init_sensors(self._settings.get(["active_sensor_list"]))

    # ~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(
            active_sensor_list=[],
            sensor_id_seed=1,
            is_mock_test=False,
            enable_logging=False,
            supported_sensor_list=[dict(value=s.value, name=s.name)
                                   for s in SUPPORTED_SENSOR_LIST],
        )

    # ~~ SettingsPlugin mixin
    def on_settings_save(self, data):
        self._log("on_settings_save: data = ",
                  data)
        
        if "active_sensor_list" in data:
            del_sensor_list = []
            for sensor in data["active_sensor_list"]:
                ret_sensor = self.sensor_mgr.handle_msg(sensor)
                
                if ret_sensor is None:
                    del_sensor_list.append(sensor)
                else:
                    sensor["sensorId"] = ret_sensor.id
            
            self._log("on_settings_save: Remove invalid stored sensors = ",
                  del_sensor_list)
            for sensor in del_sensor_list:
                data["active_sensor_list"].remove(sensor)
                    
        diff = octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        new_sensor_list = self._settings.get(["active_sensor_list"])
        self._log("on_settings_save: New stored sensors = ",
                  new_sensor_list)
        self.init_sensors(new_sensor_list)
        
        return diff

    # ~~ AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/ext_sensor_mgr.js", "js/ext_sensor_mgr_settings.js"],
            "css": ["css/ext_sensor_mgr.css"],
            "less": ["less/ext_sensor_mgr.less"]
        }

    # ~~ TemplatePlugin mixin
    def get_template_configs(self):
        return [
            # TODO: dict(type="tab", template="ext_sensor_mgr_tab.jinja2"),
            dict(type="settings", template="ext_sensor_mgr_settings.jinja2")
        ]

    # ~~ SimpleApiPlugin mixin
    def on_api_command(self, command, data):
        self._log("POST Command received: " + command + ", with data: ", data)
        if command == "config_param_list":
            sensorType = data.get('sensor_type_id')
            try:
                sensorType = SensorType(int(sensorType))
            except ValueError:
                return None
            return transform_sensor_config(determine_sensor_config(sensorType=sensorType, is_test=self._settings.get(["is_mock_test"])))

    # ~~ SimpleApiPlugin hook
    def get_api_commands(self):
        return dict(
            config_param_list=["sensor_type_id"]
        )

    # ~~ Softwareupdate hook
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "ext_sensor_mgr": {
                "displayName": "Ext_sensor_mgr Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "LBMercado",
                "repo": "OctoPrint-Ext_sensor_mgr",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/LBMercado/OctoPrint-Ext_sensor_mgr/archive/{target_version}.zip",
            }
        }

    def _log(self, data, obj=None):
        enable_log = self._settings.get(["enable_logging"])
        if enable_log:
            if obj is not None:
                self._logger.debug(data + str(obj))
            else:
                self._logger.debug(data)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "External Sensor Manager"
__plugin_description__ = "Monitor and configure your sensors' with this simple interface"
__plugin_version__ = "0.1.0"

# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Ext_sensor_mgrPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
