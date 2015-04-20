import logging, time

class ZWaveSwitch(object):
    def __init__(self, app):
        self.app = app

    def switchOn(self):
        self.app.cbLog("debug", "Switch on requested")
        self.app._sendData(self.app.switchId, 'on')
        self.app.cbLog("debug", "Switch on sent to app")

    def switchOff(self):
        self.app.cbLog("debug", "Switch off requested")
        self.app._sendData(self.app.switchId, 'off')
        self.app.cbLog("debug", "Switch off sent to app")
