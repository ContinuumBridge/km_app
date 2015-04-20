from statemachine import KitchenMinderStateMachine
from display import KitchenMinderDisplay
from actions import KitchenMinderActions
from audio import KitchenMinderAudio

class KitchenMinder(object):
    """
    Base class for kitchen minders which links together the state machine,
    display, audio and given z-wave switch components.
    """

    def __init__(self, switch, cbLog, useFramebuffer=True):
        """
        Construct a kitchen minder
        Arguments:
            switch          instance of a z-wave switch.

            useFramebuffer  whether or not to use the framebuffer for display
        """
        self.display = KitchenMinderDisplay(cbLog, useFramebuffer)
        cbLog("debug", "Initialised display")
        self.audio = KitchenMinderAudio(cbLog)
        cbLog("debug", "Initialised audio")

        actions = KitchenMinderActions(self.display, self.audio, switch)
        self.km = KitchenMinderStateMachine(actions, 'Start')
        self.km.Boot()

    def addEvent(self, event):
        """
        Expect this to be called whenever an event occurs. Having this allows
        us to either handle the event straight away by calling _handleEvent or
        do something like adding the event to a queue to be processed later.
        """
        raise NotImplemented('No addEvent implemented')

    def update(self):
        """
        Expect this to be called periodically to allow the kitchen minder to
        handle time-based updates.
        """
        pass

    def _handleEvent(self, event):
        """
        Trigger the given event in the state machine
        """
        assert self.km.islegalevent(event)
        if self.km.can(event):
            getattr(self.km, event)()
