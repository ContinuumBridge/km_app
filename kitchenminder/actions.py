class KitchenMinderActions(object):
    def __init__(self, display, audio, switch):
        self.display = display
        self.audio = audio
        self.switch = switch
        self.interval = 30
        self.timeout = 600
    def resetAudioCount(self):
        self.audio.reset()
    def turnSupplyOff(self):
        self.switch.switchOff()
    def turnSupplyOn(self):
        self.switch.switchOn()
    def msgPowerOff(self):
        self.audio.play('msgPowerOff', interval=self.interval)
        self.display.setMessage('Cooker\nOFF', 'red', timeout=self.timeout)
    def msgPowerOn(self):
        self.audio.play('msgPowerOn', interval=self.interval)
        self.display.setMessage('Cooker\nReady', 'green', timeout=self.timeout)
    def msgSmokePleaseWait(self):
        self.audio.play('msgSmokePleaseWait', interval=self.interval)
        self.display.setMessage('Cooker\nOFF', 'red', timeout=self.timeout)
    def msgBlankScreen(self):
        self.display.setMessage('')
    def msgPleasePushButton(self):
        self.audio.play('msgPleasePushButton', interval=self.interval)
        self.display.setMessage('Cooker\nOFF', 'red', timeout=self.timeout)
    def msgDeviceMissing(self):
        self.audio.play('msgDeviceMissing', interval=self.interval)
        self.display.setMessage('Kitchen Minder\nis not working\n\nPlease wait...', 'white', showFooter=False)
    def msgSplashScreen(self):
        self.display.setMessage('msgSplashScreen', 'green')
