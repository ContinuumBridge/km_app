import requests
import time

# ZWave command classes
COMMAND_CLASSES = {
    "SWITCH_BINARY": 37,
    "METER": 50
}

API_URL = "http://127.0.0.1:8083/ZWaveAPI%(path)s"
DEVICE_PATH = "/Run/devices[%(device)i]"
INSTANCE_COMMAND_PATH = "instances[%(instance)i].commandClasses[%(class)s].%(cmd)s"

class ZWaveDeviceInstance(object):
    def __init__(self, device, instance):
        self.device = device
        self.instance = instance
        self.device_path = DEVICE_PATH % { "device": device }
        self.apiCall("/Run/RequestNodeInformation("+str(device)+")")

    def sendCommand(self, cmd_class, cmd):
        command_path = INSTANCE_COMMAND_PATH % {
                "instance": self.instance,
                "class": cmd_class,
                "cmd": cmd
            }
        return self.sendDeviceCommand(command_path)

    def sendDeviceCommand(self, cmd):
        return self.apiCall(self.device_path + "." + str(cmd))

    def apiCall(self, path):
        url = API_URL % {"path": path}
        resp = requests.post(url)
        if resp.status_code == 200:
            return resp.json()
        else:
            return ""

class ZWaveSwitch(ZWaveDeviceInstance):
    def __init__(self, device, instance):
        super(ZWaveSwitch, self).__init__(device, instance)

    def isOn(self):
        time.sleep(0.5) ; # Seems to take some time to actually update.
        return self.sendCommand(COMMAND_CLASSES["SWITCH_BINARY"], "data.level.value")

    def getMeterData(self):
        # TODO: Probably don't want to expose the raw data
        return self.sendCommand(COMMAND_CLASSES["METER"], "data")

    def switchOn(self):
        return self.sendCommand(COMMAND_CLASSES["SWITCH_BINARY"], "Set(1)")

    def switchOff(self):
        return self.sendCommand(COMMAND_CLASSES["SWITCH_BINARY"], "Set(0)")

    def pollStatus(self, callback):
        while True:
            self.sendDeviceCommand("SendNoOperation()")
            time.sleep(20)
            value = self.sendDeviceCommand("data.isFailed.value")
            callback(value)

class ZWaveSmokeDetector(ZWaveDeviceInstance):
    def __init__(self, device, instance):
        super(ZWaveSmokeDetector, self).__init__(device, instance)

    def getState(self):
        return self.sendCommand(156, "data[1].sensorState.value")

    def pollEvents(self, callback):
        while True:
            time.sleep(0.1)
            callback(int(self.getState()))
