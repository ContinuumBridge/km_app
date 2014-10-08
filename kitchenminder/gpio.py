import RPi.GPIO as GPIO

SWITCH_GPIO = 18
PIR_GPIO = 17

class KitchenMinderInputs(object):
    def __init__(self, km):
        self.km = km
        # Refer to pins as Broadcom SOC channel
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def setupSwitch(self):
        GPIO.setup(SWITCH_GPIO, GPIO.IN)
        GPIO.add_event_detect(SWITCH_GPIO, GPIO.FALLING, callback=self.button_callback, bouncetime=300)

    def setupPIR(self):
        GPIO.setup(PIR_GPIO, GPIO.IN)
        GPIO.add_event_detect(PIR_GPIO, GPIO.FALLING, callback=self.pir_callback, bouncetime=300)

    def button_callback(self, channel):
        self.km.addEvent('SwitchPressed')

    def pir_callback(self, channel):
        self.km.addEvent('Movement')

    def cleanup(self):
        GPIO.cleanup()
