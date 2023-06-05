/*
 * View model for OctoPrint-Ext_sensor_mgr
 *
 * Author: Luis Mercado
 * License: AGPLv3
 */
$(function () {
    function ExtSensorMgrViewModel(parameters) {
        var self = this;

        // injected view models
        self.settingsVM = parameters[0];

        // ko variables
        self.sensorList = ko.observableArray();
        self.graphSensorList = ko.observableArray();
        self.selectedSensorId = ko.observable();
        self.sensorTypeList = ko.observableArray();
        self.chartCfgList = ko.observableArray([]);

        // others
        self._do_log = false;
        self.read_frequency_ms = 5000;
        self.selectedSensorChart = null;
        self.is_visible = false;
        self.BASE_CHART_OPTIONS = {
            scales: {
                x: {
                    type: "time",
                    time: {
                        unit: "second",
                    },
                },
                y: {
                    suggestedMin: 0,
                },
            },
            elements: {
                point: {
                    radius: 0,
                },
            },
            animation: {
                duration: 0,
            },
            interaction: {
                intersect: false,
                mode: "index",
            },
            plugins: {
                verticalLiner: {},
            },
        };
        self.lineDrawPlugin = {
            id: "verticalLiner",
            afterInit: (chart, args, opts) => {
                chart.verticalLiner = {};
            },
            afterEvent: (chart, args, options) => {
                const { inChartArea } = args;
                chart.verticalLiner = { draw: inChartArea };
            },
            beforeTooltipDraw: (chart, args, options) => {
                const { draw } = chart.verticalLiner;
                if (!draw) return;

                const { ctx } = chart;
                const { top, bottom } = chart.chartArea;
                const { tooltip } = args;
                const x = tooltip?.caretX;
                if (!x) return;

                ctx.save();

                ctx.beginPath();
                ctx.moveTo(x, top);
                ctx.lineTo(x, bottom);
                ctx.stroke();

                ctx.restore();
            },
        };
        self.BASE_CHART_PLUGIN = [self.lineDrawPlugin];
        self.LOG_TYPE = {
            INFO: 1,
            ERROR: 2,
            WARNING: 3,
        };

        // functions / methods
        self._log = function (
            info,
            obj = undefined,
            logType = self.LOG_TYPE.INFO
        ) {
            if (self._do_log) {
                const dbg = "ExtSensorMgrViewModel: " + info;

                if (
                    obj !== undefined ||
                    logType == self.LOG_TYPE.ERROR ||
                    logType == self.LOG_TYPE.WARNING
                ) {
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

        self._capitalizeStr = function (str) {
            var outputStr = str.toLowerCase();
            outputStr = outputStr[0].toUpperCase() + outputStr.substring(1);
            return outputStr;
        };

        self.getSensorOutputConfig = function (sensorId) {
            if (!sensorId) {
                return;
            }
            return OctoPrint.simpleApiCommand(
                "ext_sensor_mgr",
                "sensor_output_config",
                { sensor_id: sensorId }
            );
        };

        self.getSensorInputConfig = function (sensorId) {
            if (!sensorId) {
                return;
            }
            return OctoPrint.simpleApiCommand(
                "ext_sensor_mgr",
                "sensor_input_config",
                { sensor_id: sensorId }
            );
        };

        self.sendSensorInputRequest = function (sensor, input) {
            if (input.datatype == "bool")
                input.value = input.value == null ? false : !input.value;

            OctoPrint.simpleApiCommand("ext_sensor_mgr", "write_sensor", {
                sensor_id: sensor.sensorId(),
                input_id: input.key,
                value: input.value,
            })
                .then(() => {
                    return self.readSensor(sensor.sensorId());
                })
                .then((reading) => {
                    input.value = reading[input.key];
                    self.intervalSensorReadCb(sensor);
                });
        };

        self.readSensor = function (sensorId) {
            return OctoPrint.simpleApiCommand("ext_sensor_mgr", "read_sensor", {
                sensor_id: sensorId,
            });
        };

        self.getSensorReadHistoryList = function (sensorId) {
            if (!sensorId) {
                return;
            }
            return OctoPrint.simpleApiCommand(
                "ext_sensor_mgr",
                "hist_reading_list",
                { sensor_id: sensorId }
            );
        };

        self.sensorTypeFromId = function (sensorTypeId) {
            const sensorType = self.sensorTypeList().filter((type) => {
                return type.value() == sensorTypeId;
            });

            return sensorType.length > 0 ? sensorType[0] : null;
        };

        self._propChartConfig = function (config, datasets, options) {
            if (config != null) {
                config.data.datasets.forEach((ds, idx) => {
                    if (datasets[idx]) {
                        ds.label = datasets[idx].label;
                        ds.data = datasets[idx].data;
                    }
                });
                options.scales = {
                    ...config.options.scales,
                    ...options.scales,
                };
                Object.keys(options).forEach((cfgKey) => {
                    config.options[cfgKey] = {
                        ...config.options[cfgKey],
                        ...options[cfgKey],
                    };
                });
            } else {
                config = {};
                config.data = { datasets: datasets };
                config.options = options;
                config.plugins = self.BASE_CHART_PLUGIN;
            }

            return config;
        };

        self.ParseSensorToChartConfig = function (sensor, sensorData) {
            var config, initDatasets, options;
            var configList = self.chartCfgList();
            // from python timestamp to js timestamp (js uses millis)
            var chartData = sensorData.map((row) => ({
                ...row,
                timestamp: row.timestamp * 1000,
            }));
            initDatasets = [
                {
                    label: sensor.config.name(),
                    data: chartData,
                },
            ];
            self._log(
                (info = "ParseSensorToChartConfig: (1) sensor: "),
                (obj = sensor)
            );
            self._log(
                (info = "ParseSensorToChartConfig: (2) sensor data: "),
                (obj = sensorData)
            );
            Object.entries(sensor.outputStd).forEach(
                ([key, outputCfg], idx) => {
                    var datasetList = [];
                    if (outputCfg.hasOwnProperty("sub_output_list")) {
                        for (const subOutput of Object.values(
                            outputCfg.sub_output_list
                        )) {
                            subOutDs = {
                                label: sensor.config
                                    .name()
                                    .concat(" (", subOutput, ")"),
                                data: chartData,
                                parsing: {
                                    xAxisKey: "timestamp",
                                    yAxisKey: `value.${key}.${subOutput.toLowerCase()}`,
                                },
                            };
                            datasetList.push(subOutDs);
                        }
                    } else {
                        datasetList = [...initDatasets];
                    }

                    options = {
                        ...options,
                        ...self.BASE_CHART_OPTIONS,
                        parsing: {
                            xAxisKey: "timestamp",
                            yAxisKey: `value.${key}`,
                        },
                        scales: {
                            ...self.BASE_CHART_OPTIONS.scales,
                            y: {
                                ...self.BASE_CHART_OPTIONS.scales.y,
                                title: {
                                    display: true,
                                    text:
                                        self._capitalizeStr(outputCfg.type) +
                                        " (" +
                                        outputCfg.unit +
                                        ")", //TODO: special formating for naming?
                                },
                            },
                        },
                    };
                    config = self._propChartConfig(
                        configList[idx],
                        datasetList,
                        options
                    );
                    if (configList.indexOf(config) == -1) {
                        configList.push(config);
                    }
                }
            );
            self._log(
                (info = "ParseSensorToChartConfig: (3) config list: "),
                (obj = configList)
            );

            return configList;
        };

        self.mapSensorOutputStd = function (sensor, config) {
            const outputStd = { ...config };

            // add degree symbol (°) to temperature unit
            Object.keys(outputStd).filter((o) => o.type == "temp");
            for (const [key, val] of Object.entries(outputStd)) {
                if (key == "temp") {
                    val.unit = "°" + val.unit;
                }
            }

            sensor.outputStd = outputStd;
            self._log(
                (info = "mapSensorOutputStd: out sensor: "),
                (obj = sensor)
            );
        };

        self.mapSensorInputStd = function (sensor, config) {
            sensor.inputStd = { ...config };
            self._log(
                (info = "mapSensorOutputStd: out sensor: "),
                (obj = sensor)
            );
        };

        self.genSensorOutputObs = function (sensor) {
            var output_list = [];
            const outputStd = sensor.outputStd;

            Object.entries(outputStd).forEach((stdEntry) => {
                const [k, std] = stdEntry;
                var suboutputList = [];

                if (std.hasOwnProperty("sub_output_list")) {
                    suboutputList = std.sub_output_list.map((suboutput) => {
                        return {
                            name: suboutput,
                            val: null,
                        };
                    });
                } else {
                    suboutputList.push({
                        name: null,
                        val: null,
                    });
                }

                var output = {
                    key: k,
                    label: self._capitalizeStr(std.type),
                    unit: ko.observable(std.unit),
                    suboutput: ko.observableArray(suboutputList),
                };
                output_list.push(output);
            });

            sensor.output(output_list);
            self._log(
                (info = "genSensorOutputObs: out sensor: "),
                (obj = sensor)
            );
        };

        self.genSensorInputObs = function (sensor) {
            const inputList = [];
            const inputStd = sensor.inputStd;

            Object.entries(inputStd).forEach((stdEntry) => {
                const [k, std] = stdEntry;
                const input = {
                    key: k,
                    label: self._capitalizeStr(std.name),
                    datatype: std.datatype,
                    value: sensor.input_values[k],
                };
                inputList.push(input);
            });
            sensor.input(inputList);
            self._log(
                (info = "genSensorInputObs: in sensor: "),
                (obj = sensor)
            );
        };

        self.prcSubOutput = function (outputObsArr, subOutput) {
            if (!ko.isObservableArray(outputObsArr)) {
                self._log(
                    (info = "prcSubOutput: output is not observable arr: "),
                    (obj = outputObs),
                    (logType = self.LOG_TYPE.WARNING)
                );
                return;
            }
            // multiple output
            if (subOutput !== null && typeof subOutput === "object") {
                for (const [outputName, outputVal] of Object.entries(
                    subOutput
                )) {
                    const subOutputEntry = outputObsArr.remove(
                        (o) => o.name.toLowerCase() == outputName.toLowerCase()
                    );
                    if (subOutputEntry != null) {
                        subOutputEntry[0].val = outputVal;
                        outputObsArr.push(subOutputEntry[0]);
                    }
                }
            } else {
                const subOutputEntry = outputObsArr.remove(
                    (o) => o.name == null
                );
                if (subOutputEntry != null) {
                    subOutputEntry[0].val = subOutput;
                    outputObsArr.push(subOutputEntry[0]);
                }
            }
            self._log(
                (info = "prcSubOutput: processed output: "),
                (obj = outputObsArr())
            );
        };

        self.prcSensorReading = function (sensor, reading) {
            if (!reading) {
                self._log(
                    (info = "prcSensorReading: no reading returned for sensor"),
                    (obj = sensor),
                    (logType = self.LOG_TYPE.WARNING)
                );
                return;
            }

            for (const readingKey in reading.value) {
                const displOutput = sensor
                    .output()
                    .find((o) => o.key == readingKey);
                self._log(
                    (info = "prcSensorReading: (1) displ_reading: "),
                    (obj = displOutput)
                );
                if (displOutput != null) {
                    const readVal = reading.value[readingKey];
                    self.prcSubOutput(displOutput.suboutput, readVal);
                }
            }
            self._log(
                (info = "prcSensorReading: (2) reading: "),
                (obj = reading)
            );
            self._log(
                (info = "prcSensorReading: (3) output: "),
                (obj = sensor.output())
            );
        };

        // bindings / callbacks
        self.fmtSensorReadingCb = function (unit, value, name = undefined) {
            return ko.pureComputed(function () {
                displDesc = name != null ? name.toUpperCase() + ": " : "";
                displVal = ko.isObservable(value) ? value() : value;
                displ = "".concat(
                    displDesc,
                    !isNaN(parseFloat(displVal))
                        ? displVal.toFixed(2)
                        : displVal,
                    " ",
                    (ko.isObservable(unit) ? unit() : unit) ?? ""
                );
                return displ;
            });
        };

        self.intervalSensorReadCb = function (sensor) {
            if (!sensor.enabled()) {
                self._log(
                    (info =
                        "intervalSensorReadCb: not proceeding, sensor is disabled"),
                    (obj = sensor)
                );
                return;
            }

            self.getSensorReadHistoryList(sensor.sensorId()).done(
                (read_history_list) => {
                    if (!read_history_list) {
                        return;
                    }
                    // dashboard value
                    self.prcSensorReading(sensor, read_history_list.at(-1));

                    // selected sensor graph
                    if (self.selectedSensorId() != sensor.sensorId()) {
                        return;
                    }
                    const cfg = self.ParseSensorToChartConfig(
                        sensor,
                        read_history_list
                    );
                    self.chartCfgList(cfg);
                    self._log(
                        (info =
                            "intervalSensorReadCb (getSensorReadHistoryList): graph config list: "),
                        (obj = cfg)
                    );

                    self.build_graph(sensor.sensorId(), cfg);
                }
            );
        };

        self.initSensorReadingCb = function (target) {
            self._log(
                (info = "initSensorReadingCb: (1) init sensor: "),
                (obj = target)
            );
            if (!target.output) target.output = ko.observable();
            else target.output();
            if (!target.input) target.input = ko.observable();
            else target.input();

            const output_config_prom = self.getSensorOutputConfig(
                target.sensorId()
            );
            const input_config_prom = self.getSensorInputConfig(
                target.sensorId()
            );
            if (output_config_prom) {
                output_config_prom.then((config) => {
                    self.mapSensorOutputStd(target, config);
                    self.genSensorOutputObs(target);
                    self.intervalSensorReadCb(target);
                    self._log(
                        (info =
                            "initSensorReadingCb: (2) finish init output sensor: "),
                        (obj = target)
                    );
                });
            }
            if (input_config_prom) {
                input_config_prom.then((config) => {
                    self.mapSensorInputStd(target, config);
                    self.genSensorInputObs(target);
                    self._log(
                        (info =
                            "initSensorReadingCb: (3) finish init input sensor: "),
                        (obj = target)
                    );
                });
            }
        };

        self.build_graph = function (sensorId, configList) {
            sensorId = ko.isObservable(sensorId) ? sensorId() : sensorId;
            if (sensorId === null) {
                return;
            }

            configList.forEach((config, idx) => {
                const data = config.data;
                const options = config.options;
                const chart = config.chart;
                const plugins = config.plugins;

                if (
                    chart &&
                    chart.data &&
                    self.selectedSensorId() == sensorId
                ) {
                    var chartDatasetList = chart.data.datasets;
                    var chartOpt = chart.options;

                    // just update
                    Object.keys(options).forEach((optionKey) => {
                        chartOpt[optionKey] = options[optionKey];
                    });

                    if (chartDatasetList && chartDatasetList.length == 0) {
                        chart.data = { ...data };
                    } else {
                        Object.keys(data.datasets).forEach((datasetKey) => {
                            const newData = data.datasets[datasetKey].data;

                            chartDatasetList[datasetKey].data = newData;
                        });
                    }

                    self._log(
                        (info = "build_graph: update graph data: "),
                        (obj = data)
                    );

                    chart.update();
                    return;
                }
                self._log(
                    (info = "build_graph: new graph data: "),
                    (obj = data)
                );
                const canvas_elem = $("#ext_sensor_mgr_sensor_graph" + idx)[0];

                const cfg = {
                    type: "line",
                    options: {
                        ...self.BASE_CHART_OPTIONS,
                        ...options,
                    },
                    data: { ...data },
                    plugins: [...plugins],
                };

                if (chart != undefined) {
                    chart.destroy();
                }
                config.chart = new Chart(canvas_elem, cfg);
            });
        };

        self.resetChart = function () {
            self.chartCfgList([]);
        };

        self.onBeforeBinding = function () {
            self._do_log =
                self.settingsVM.settings.plugins.ext_sensor_mgr.enable_logging();
            self.sensorTypeList(
                self.settingsVM.settings.plugins.ext_sensor_mgr.supported_sensor_list()
            );
            self.read_frequency_ms =
                self.settingsVM.settings.plugins.ext_sensor_mgr.web_update_freq_s() *
                1000;
            // deep copy to prevent modification of settings
            var sensorList =
                self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list();
            sensorList = ko.mapping.fromJS(ko.mapping.toJS(sensorList))();
            sensorList = sensorList.map((s) => ({
                ...s,
                sensorType: self.sensorTypeFromId(s.sensorType()),
            }));
            self.sensorList(sensorList);
            self.sensorList().forEach((sensor) => {
                self.initSensorReadingCb(sensor);
            });
            self.graphSensorList(self.sensorList().filter((s) => s.enabled()));

            self._log(
                (info = "onBeforeBinding: (1) supported sensor types: "),
                (obj = self.sensorTypeList())
            );
            self._log(
                (info = "onBeforeBinding: (2) active sensors: "),
                (obj = self.sensorList())
            );
        };

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin != "ext_sensor_mgr") {
                return;
            }
            if (data.hasOwnProperty("upd_sensor_list")) {
                const sensorList = data.upd_sensor_list;
                self._log(
                    (info =
                        "onDataUpdaterPluginMessage: updated sensors from server: "),
                    sensorList
                );
                // update/push new sensors
                sensorList.forEach((s) => {
                    var viewSensor = self
                        .sensorList()
                        .find((v) => v.sensorId() == s.sensorId);
                    if (viewSensor) {
                        self._log(
                            (info =
                                "onDataUpdaterPluginMessage: existing sensor matched for update: "),
                            viewSensor
                        );
                        viewSensor.enabled(s.enabled);
                        viewSensor.sensorType = self.sensorTypeFromId(
                            s.sensorType
                        );
                        Object.keys(s.config).forEach((configKey) => {
                            for (const [paramKey, paramVal] of Object.entries(
                                s.config[configKey]
                            )) {
                                if (
                                    ko.isObservable(
                                        viewSensor.config[configKey][paramKey]
                                    )
                                )
                                    viewSensor.config[configKey][paramKey](
                                        paramVal
                                    );
                                else
                                    viewSensor.config[configKey][paramKey] =
                                        paramVal;
                            }
                        });

                        // reinitialize
                        self.initSensorReadingCb(viewSensor);

                        // reset periodic reader callback
                        if (viewSensor.read_cb) {
                            clearInterval(viewSensor.read_cb);
                            viewSensor.read_cb = setInterval(
                                self.intervalSensorReadCb,
                                self.read_frequency_ms,
                                viewSensor
                            );
                        }
                    } else {
                        viewSensor = ko.mapping.fromJS({ ...s });
                        viewSensor.sensorType = self.sensorTypeFromId(
                            s.sensorType
                        );

                        // reinitialize
                        self.initSensorReadingCb(viewSensor);

                        // reset periodic reader callback
                        if (self.is_visible) {
                            viewSensor.read_cb = setInterval(
                                self.intervalSensorReadCb,
                                self.read_frequency_ms,
                                viewSensor
                            );
                        }
                        self.sensorList.push(viewSensor);
                    }
                });

                // delete removed sensors
                const existSensorIdList = sensorList.map((s) => s.sensorId);
                self.sensorList().forEach((s) => {
                    if (!existSensorIdList.includes(s.sensorId())) {
                        clearInterval(s.read_cb);
                        s.read_cb = null;
                    }
                });

                const removedList = self.sensorList.remove(
                    (s) => !existSensorIdList.includes(s.sensorId())
                );

                // synchronize with selectable graph sensors
                self.graphSensorList(
                    self.sensorList().filter((s) => s.enabled())
                );
                const graphSensor = self
                    .graphSensorList()
                    .find((s) => self.selectedSensorId() == s.sensorId());
                self.selectedSensorId(
                    graphSensor != null ? graphSensor.sensorId() : null
                );
                self.resetChart();

                self._log(
                    (info =
                        "onDataUpdaterPluginMessage: removed sensors in view: "),
                    removedList
                );
                self._log(
                    (info =
                        "onDataUpdaterPluginMessage: updated sensors in view: "),
                    self.sensorList()
                );
            }
        };

        self.onTabChange = function (next, current) {
            if (next == "#tab_plugin_ext_sensor_mgr") {
                // reset the interval callbacks
                for (const idx in self.sensorList()) {
                    var sensor = self.sensorList()[idx];
                    if (!sensor.read_cb)
                        sensor.read_cb = setInterval(
                            self.intervalSensorReadCb,
                            self.read_frequency_ms,
                            sensor
                        );
                    self._log((info = "onTabChange: reset sensor: "), sensor);
                }
                self.is_visible = true;
                self._log(
                    (info = "onTabChange: resetting intervals: "),
                    self.sensorList()
                );
            } else if (current == "#tab_plugin_ext_sensor_mgr") {
                // stop the interval callbacks
                for (const idx in self.sensorList()) {
                    const sensor = self.sensorList()[idx];
                    clearInterval(sensor.read_cb);
                    sensor.read_cb = null;
                }
                self.is_visible = false;
                self._log(
                    (info = "onTabChange: stopping intervals: "),
                    (obj = self.sensorList())
                );
            }
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ExtSensorMgrViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#tab_plugin_ext_sensor_mgr"],
    });
});
