/*
 * View model for OctoPrint-Ext_sensor_mgr_settings
 *
 * Author: Luis Mercado
 * License: AGPLv3
 */
$(function () {
    function ExtSensorMgrSettingsViewModel(parameters) {
        var self = this;

        // injected view models
        self.settingsVM = parameters[0];

        // ko variables
        self.sensorList = ko.observableArray();
        self.supportedSensorList = ko.observableArray();
        self.selectedSensor = ko.observable(null);
        self.selectedSupportedConfig = ko.observable();
        self.selectedSupportedConfigList = ko.computed(function () {
            config = self.selectedSupportedConfig();
            if (config != null) {
                return Object.keys(config).map((val) => {
                    self._log(
                        (info =
                            "selectedSupportedConfigList ko computed: given config for key = " +
                            val),
                        (obj = config)
                    );
                    const groupSeq = ko.isObservable(config[val].group_seq)
                        ? config[val].group_seq()
                        : config[val].group_seq;
                    return {
                        param: val,
                        type:
                            config[val].value_list.length > 0
                                ? self.CONFIG_DATA_TYPE.Options
                                : self.CONFIG_DATA_TYPE.Text,
                        label: config[val].label,
                        group: groupSeq.map((val, idx) => {
                            return { name: val, level: idx + 1 };
                        }),
                    };
                });
            } else {
                return [];
            }
        }, self);
        self.selectedSuppConfigGroupList = ko.observableArray([]);

        // others
        self._null_sensor_type = null;
        self.do_subst_mock_sensor = false;
        self._do_log = true;
        self.CONFIG_DATA_TYPE = {
            Text: 1,
            Options: 2,
        };
        self.LOG_TYPE = {
            INFO: 1,
            ERROR: 2,
            WARNING: 3,
        };
        self.apiCache = {};

        // functions / methods
        self.toggleSensorButtonCss = function (data) {
            self._log(
                (info = "toggleSensorButtonCss: enabled = " + data.enabled())
            );
            return {
                fa: true,
                "fa-toggle-on": data.enabled(),
                "fa-toggle-off": !data.enabled(),
            };
        };

        self.toggleSensor = function (data) {
            data.enabled(!data.enabled());
            self._log((info = "toggleSensor: new enabled =" + data.enabled()));
        };

        self.addSensor = function () {
            var sensor = {
                sensorType: ko.observable(self._null_sensor_type),
                enabled: ko.observable(false),
                sensorId: ko.observable(),
                config: { name: { value: ko.observable("New Sensor") } },
            };
            self.sensorList.push(sensor);
            self._log((info = "addSensor: (1) new sensor = " + sensor));
            self._log(
                (info =
                    "addSensor: (2) sensor count = " + self.sensorList().length)
            );
        };

        self.removeSensor = function (data) {
            self._log((info = "remove sensor"), (obj = data));
            self.sensorList.remove(data);
            if (self.selectedSensor() == data) {
                self.selectedSensor(null);
            }
            self._log(
                (info =
                    "removeSensor: sensor count = " + self.sensorList().length)
            );
        };

        self.isSelectedSensorCb = function (data) {
            return ko.pureComputed(function () {
                return data == self.selectedSensor();
            }, self);
        };

        self.matchingParamConfigCb = function (supp_config, sensorConfig) {
            return ko.computed(function () {
                self._log(
                    (info = "matchingParamConfigCb: (1) supp_config = "),
                    (obj = supp_config)
                );
                self._log(
                    (info = "matchingParamConfigCb: (2) sensorConfig = "),
                    (obj = sensorConfig)
                );
                if (
                    sensorConfig != null &&
                    supp_config != null &&
                    sensorConfig[supp_config.param] != null &&
                    sensorConfig[supp_config.param].hasOwnProperty("type") &&
                    supp_config.type == sensorConfig[supp_config.param].type()
                ) {
                    return sensorConfig[supp_config.param];
                }
                return null;
            }, self);
        };

        self.init_config_param = function (config_param, value = null) {
            // check if default value is enum
            if (
                config_param.default_value != null &&
                typeof config_param.default_value === "object"
            ) {
                config_param.value = value ?? config_param.default_value.key;
            } else {
                config_param.value = value ?? config_param.default_value;
            }
            config_param.type =
                config_param.value_list.length > 0
                    ? self.CONFIG_DATA_TYPE.Options
                    : self.CONFIG_DATA_TYPE.Text;

            for (const param in config_param) {
                config_param[param] = ko.observable(config_param[param]);
            }
        };

        self.prop_sensor_config = function (sensor, supportedConfig) {
            if (!supportedConfig) {
                return;
            }
            config = null;

            self._log(
                (info = "prop_sensor_config: supported config list"),
                (obj = supportedConfig)
            );
            self._log(
                (info = "prop_sensor_config: prop to sensor"),
                (obj = sensor)
            );

            if (!sensor.hasOwnProperty("config") || sensor.config == null) {
                sensor.config = { ...supportedConfig };
                config = sensor.config;
                self._log(
                    (info = "prop_sensor_config: new config list"),
                    (obj = config)
                );
                for (const k in config) {
                    self.init_config_param(config[k]);
                }
            } else {
                config = sensor.config;
                for (const k in supportedConfig) {
                    item = { ...supportedConfig[k] };
                    self.init_config_param(
                        item,
                        config.hasOwnProperty(k) ? config[k].value() : null
                    );
                    config[k] = item;
                }
            }
            self.selectedSupportedConfig(supportedConfig);
            self._log(
                (info = "prop_sensor_config: config list ko computed"),
                (obj = self.selectedSupportedConfigList())
            );
            self._log(
                (info = "prop_sensor_config: processed config list"),
                (obj = config)
            );
            self.selectedSuppConfigGroupList(self.getConfigGroupList());
            self._log(
                (info = "prop_sensor_config: processed group list"),
                (obj = self.selectedSuppConfigGroupList())
            );
        };

        self.mdfSensor = function () {
            var sensor = self.selectedSensor();
            self._log((info = "configure sensor"), (obj = sensor));
            if (sensor) {
                self.getCommandParamList(sensor.sensorType()).then((res) => {
                    self._log(
                        (info =
                            "API command config param list for sensor result"),
                        (obj = res)
                    );
                    self.prop_sensor_config(sensor, res);
                    self._log((info = "Modify sensor post:  "), (obj = sensor));
                    $("#SensorManagerConfigure").modal("show");
                });
            }
        };

        self.getCommandParamList = function (sensorTypeKey) {
            const onSuccess = function (res) {
                if (!self.apiCache.hasOwnProperty(sensorTypeKey)) {
                    self.apiCache[sensorTypeKey] = res;
                }
                return res;
            };

            if (self.apiCache.hasOwnProperty(sensorTypeKey)) {
                self._log(
                    (info = "getCommandParamList: cache hit"),
                    (obj = sensorTypeKey)
                );
                return Promise.resolve(self.apiCache[sensorTypeKey]);
            }

            return OctoPrint.simpleApiCommand(
                "ext_sensor_mgr",
                "config_param_list",
                { sensor_type_id: sensorTypeKey }
            ).done(onSuccess);
        };

        self.onSensorTypeChange = function (sensor) {
            if (sensor != null) {
                self.wipeSupportedSensorConfig(sensor);
                // wipe existing config
                sensor.config = { name: sensor.config.name };
                self._log(
                    "onSensorTypeChange: wiped config = ",
                    (obj = sensor.config)
                );
                self.getCommandParamList(sensor.sensorType()).then((res) => {
                    self.prop_sensor_config(sensor, res);
                });
            }
        };

        self.wipeSupportedSensorConfig = function (sensor) {
            if (sensor != null && ko.isObservable(sensor)) {
                self.selectedSupportedConfig(null);
                self.selectedSuppConfigGroupList([]);
            }
        };

        self.enableSensorCb = function (sensor) {
            return ko.pureComputed(() => {
                return (
                    sensor() &&
                    sensor().sensorType() != self._null_sensor_type.value()
                );
            });
        };

        self.disableSensorConfigCb = function (sensor) {
            return ko.pureComputed(() => {
                if (
                    !ko.isObservable(sensor) ||
                    sensor() == null ||
                    self.selectedSupportedConfig() == null
                ) {
                    return true;
                }

                return sensor().sensorType() == self._null_sensor_type.value();
            });
        };

        self.modalSensorCb = function (sensor) {
            return ko.pureComputed(() => {
                if (
                    !ko.isObservable(sensor) ||
                    sensor() == null ||
                    self.selectedSupportedConfig() == null ||
                    sensor().sensorType() == self._null_sensor_type.value()
                ) {
                    return null;
                }

                return sensor;
            });
        };

        self.onSelectSensor = function (data) {
            self.selectedSensor(data);
            self._log((info = "onSelectSensor: selected sensor"), (obj = data));
        };

        self.getConfigGroupList = function (doReset = true) {
            if (doReset) self.selectedSuppConfigGroupList([]);
            config = self.selectedSupportedConfig();
            self._log((info = "getConfigGroupList: config"), (obj = config));
            if (config != null) {
                return Object.values(config).reduce(
                    (groupList, configEntry) => {
                        var prevGroup = null,
                            currGroup = null,
                            level;
                        const groupSeq = ko.isObservable(configEntry.group_seq)
                            ? configEntry.group_seq()
                            : configEntry.group_seq;
                        groupSeq.forEach((group, idx) => {
                            level = idx + 1;

                            // main grouping
                            if (prevGroup == null) {
                                currGroup = groupList.find(
                                    (g) =>
                                        g.name == group &&
                                        g.level == level &&
                                        g.parentGroup == null
                                );
                                if (currGroup == null) {
                                    groupList.push({
                                        name: group,
                                        level: level,
                                        parentGroup: null,
                                    });
                                }
                            } else {
                                // subgroupings
                                currGroup = groupList.find(
                                    (g) =>
                                        g.name == group &&
                                        g.level == level &&
                                        g.parentGroup == prevGroup
                                );
                                if (currGroup == null) {
                                    groupList.push({
                                        name: group,
                                        level: level,
                                        parentGroup: prevGroup,
                                    });
                                }
                            }
                            prevGroup = currGroup;
                        });
                        return groupList;
                    },
                    self.selectedSuppConfigGroupList()
                );
            } else {
                return [];
            }
        };

        self.onBeforeBinding = function () {
            self._do_log =
                self.settingsVM.settings.plugins.ext_sensor_mgr.enable_logging();
            self.do_subst_mock_sensor =
                self.settingsVM.settings.plugins.ext_sensor_mgr.is_mock_test();

            var sensorList =
                self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list();
            self.sensorList(sensorList);
            self._log(
                (info = "onBeforeBinding: active sensors: "),
                (obj = self.sensorList())
            );
            sensorList =
                self.settingsVM.settings.plugins.ext_sensor_mgr.supported_sensor_list();
            self.supportedSensorList(sensorList);
            self._null_sensor_type = self
                .supportedSensorList()
                .filter((val) => {
                    return val.value() == -1;
                })[0];
            self._log(
                (info = "onBeforeBinding: null sensor defined as: "),
                (obj = self._null_sensor_type)
            );
            self._log(
                (info = "onBeforeBinding: supported sensors: "),
                (obj = self.supportedSensorList())
            );
        };

        self.onSettingsBeforeSave = function () {
            self._log(
                (info = "onSettingsBeforeSave: old active sensors: "),
                (obj =
                    self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list())
            );
            self._log(
                (info = "onSettingsBeforeSave: new active sensors: "),
                (obj = self.sensorList())
            );
            self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list(
                self.sensorList()
            );
        };

        self._log = function (
            info,
            obj = undefined,
            logType = self.LOG_TYPE.INFO
        ) {
            if (
                self._do_log ||
                logType == self.LOG_TYPE.ERROR ||
                logType == self.LOG_TYPE.WARNING
            ) {
                const dbg = "ExtSensorMgrSettingsViewModel: " + info;

                if (obj !== undefined) {
                    switch (logType) {
                        case self.LOG_TYPE.ERROR:
                            console.error(dbg + " %o", obj);
                            break;
                        case self.LOG_TYPE.WARNING:
                            console.warn(dbg + " %o", obj);
                            break;
                        default:
                            console.log(dbg + " %o", obj);
                    }
                } else {
                    switch (logType) {
                        case self.LOG_TYPE.ERROR:
                            console.error(dbg);
                            break;
                        case self.LOG_TYPE.WARNING:
                            console.warn(dbg);
                            break;
                        default:
                            console.log(dbg);
                    }
                }
            }
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ExtSensorMgrSettingsViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_ext_sensor_mgr"],
    });
});
