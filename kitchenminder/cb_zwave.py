import logging, time

class ZWaveSwitch(object):
    def __init__(self, app):
        self.app = app

    def switchOn(self):
        logging.debug("Switch on requested")
        self.app._sendData(self.app.switchId, 'on')
        logging.debug("Switch on sent to app")

    def switchOff(self):
        logging.debug("Switch off requested")
        self.app._sendData(self.app.switchId, 'off')
        logging.debug("Switch off sent to app")
