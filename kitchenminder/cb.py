from kitchenminder.main import KitchenMinder
from kitchenminder import cb_zwave

class CbKitchenMinder(KitchenMinder):
    def __init__(self, app):
        switch = cb_zwave.ZWaveSwitch(app)
        super(CbKitchenMinder, self).__init__(switch, app.cbLog)

    def addEvent(self, event):
        self._handleEvent(event)
