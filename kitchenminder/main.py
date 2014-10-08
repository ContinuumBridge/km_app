from statemachine import KitchenMinderStateMachine
from display import KitchenMinderDisplay
from actions import KitchenMinderActions
from audio import KitchenMinderAudio
import logging

class KitchenMinder(object):
    def __init__(self, switch, useFramebuffer=True):
        self.display = KitchenMinderDisplay(useFramebuffer)
        print "Initialised display"
        self.audio = KitchenMinderAudio()
        print "Initialised audio"

        actions = KitchenMinderActions(self.display, self.audio, switch)
        self.km = KitchenMinderStateMachine(actions, 'Start')
        self.km.Boot()

    def addEvent(self, event):
        raise NotImplemented('No addEvent implemented')

    def update(self):
        self.display.update()

    def _handleEvent(self, event):
        assert self.km.islegalevent(event)
        if self.km.can(event):
            getattr(self.km, event)()
