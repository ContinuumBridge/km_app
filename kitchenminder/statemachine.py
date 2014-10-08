from atswfysom import Fysom

class KitchenMinderStateMachine(Fysom):
    def notImplemented(self, e):
        raise NotImplemented()

    def onchangestate(self, e):
        self.actions.resetAudioCount()

    def onchangestateSupplyOff(self, e):
        self.actions.turnSupplyOff()
        self.actions.msgPowerOff()

    def onchangestateSupplyOn(self, e):
        self.actions.turnSupplyOn()
        self.actions.msgPowerOn()

    def onchangestateSmokeDetected(self, e):
        self.actions.turnSupplyOff()

    def onenterSmokeDetected(self, e):
        self.actions.msgSmokePleaseWait()

    def onenterSmokeClear(self, e):
        self.actions.msgPleasePushButton()

    def onchangestateDeviceMissing(self, e):
        self.actions.turnSupplyOff()

    def onenterDeviceMissing(self, e):
        self.actions.msgDeviceMissing()

    def onenterStart(self, e):
        self.actions.msgSplashScreen()

    def __init__(self, actions, initial):
        self.actions = actions

        #  event                  src state              dst state
        self.events  = [
          ('Boot',             'Start',               'SupplyOff'),

          ('Smoke',            ['SupplyOff',
                                'SupplyOn',
                                'SmokeClear'],        'SmokeDetected'),

          ('NoSmoke',          ['SmokeDetected'],     'SmokeClear'),


          ('SwitchPressed',    'SupplyOff',           'SupplyOn'),
          ('SwitchPressed',    'SmokeClear',          'SupplyOn'),
          ('SwitchPressed',    'SmokeDetected',       'SmokeDetected'),
          ('SwitchPressed',    'DeviceMissing',       'DeviceMissing'),

          ('NotConnected',     ['SupplyOff',
                                'SupplyOn',
                                'SmokeDetected',
                                'SmokeClear'],        'DeviceMissing'),

          ('Connected',        'DeviceMissing',       'SupplyOff'),

          ('Movement',         'SmokeClear',          'SmokeClear'),
          ('Movement',         'SmokeDetected',       'SmokeDetected'),
          ('Movement',         'SupplyOff',           'SupplyOff'),
          ('Movement',         'SupplyOn',            'SupplyOn'),
          ('Movement',         'DeviceMissing',       'DeviceMissing'),
        ]

        Fysom.__init__(self,
                       initial=initial,
                       events=self.events)
