class KitchenMinderActions(object):
    def __init__(self, display, audio, switch):
        self.display = display
        self.audio = audio
        self.switch = switch
    def resetAudioCount(self):
        self.audio.reset()
    def turnSupplyOff(self):
        self.switch.switchOff()
    def turnSupplyOn(self):
        self.switch.switchOn()
    def msgPowerOff(self):
        self.audio.play('msgPowerOff', interval=60)
        self.display.setMessage('Cooker\nOFF', 'red')
    def msgPowerOn(self):
        self.audio.play('msgPowerOn', interval=60)
        self.display.setMessage('Cooker\nReady', 'green')
    def msgSmokePleaseWait(self):
        self.audio.play('msgSmokePleaseWait', interval=30)
        self.display.setMessage('Cooker\nOFF', 'red')
    def msgBlankScreen(self):
        self.display.setMessage('')
    def msgPleasePushButton(self):
        self.audio.play('msgPleasePushButton', interval=60)
        self.display.setMessage('Cooker\nOFF', 'red')
    def msgDeviceMissing(self):
        self.display.setMessage('Kitchen Minder\nis not working\n\nPlease wait...', 'white', showFooter=False)
    def msgSplashScreen(self):
        self.display.setMessage('msgSplashScreen', 'green')
