import Queue
import threading
from kitchenminder import gpio, zwave
from kitchenminder.main import KitchenMinder

class StandaloneKitchenMinder(KitchenMinder):
    def __init__(self):
        self.events = Queue.Queue()

        switch = zwave.ZWaveSwitch(device=4, instance=0)
        t = threading.Thread(target=switch.pollStatus, args=[self.setPowerSwitchFailed])
        t.daemon = True
        t.start()

        super(StandaloneKitchenMinder, self).__init__(switch)

        smokeDetector = zwave.ZWaveSmokeDetector(device=5, instance=0)
        t = threading.Thread(target=smokeDetector.pollEvents, args=[self.setSmokeDetected])
        t.daemon = True
        t.start()

        self.inputs = gpio.KitchenMinderInputs(self)
        self.inputs.setupSwitch()
        self.inputs.setupPIR()
        print "Setup GPIOs"

    def setPowerSwitchFailed(self, failed):
        if failed:
            self.addEvent('NotConnected')
        else:
            self.addEvent('Connected')

    def setSmokeDetected(self, detected):
        if detected:
            self.addEvent('Smoke')
        else:
            self.addEvent('NoSmoke')

    def addEvent(self, event):
        self.events.put(event)

    def run(self):
        self.events.queue.clear()
        while True:
            try:
                event = self.events.get(True, 1)
                self._handleEvent(event)
            except Queue.Empty:
                pass
            finally:
                self.update()

    def cleanup(self):
        self.inputs.cleanup()
