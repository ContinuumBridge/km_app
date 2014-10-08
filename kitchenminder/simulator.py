import Queue
import threading
from kitchenminder.main import KitchenMinder

class DummySwitch(object):
    def switchOn(self):
        print "Switch On"
    def switchOff(self):
        print "Switch Off"

class KitchenMinderSimulator(KitchenMinder):
    def __init__(self):
        self.events = Queue.Queue()
        switch = DummySwitch()
        super(KitchenMinderSimulator, self).__init__(switch, useFramebuffer=False)

        t = threading.Thread(target=self.inputs)
        t.daemon = True
        t.start()

    def inputs(self):
        while True:
            buttonPress = raw_input('(b/m/s/c) > ')
            if buttonPress == 'b':
                self.addEvent('SwitchPressed')
            elif buttonPress == 'm':
                self.addEvent('Movement')
            elif buttonPress == 's':
                self.addEvent('Smoke')
            elif buttonPress == 'c':
                self.addEvent('NoSmoke')
            elif buttonPress == 'd':
                self.addEvent('NotConnected')
            elif buttonPress == 'r':
                self.addEvent('Connected')

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
