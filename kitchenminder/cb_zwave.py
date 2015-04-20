import logging, time

class ZWaveSwitch(object):
    def __init__(self, app):
        self.app = app

    def switchOn(self):
        self.cbLog("debug", "Switch on requested")
        self.app._sendData(self.app.switchId, 'on')
        self.cbLog("debug", "Switch on sent to app")

    def switchOff(self):
        self.cbLog("debug", "Switch off requested")
        self.app._sendData(self.app.switchId, 'off')
        self.cbLog("debug", "Switch off sent to app")
