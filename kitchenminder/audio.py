import pygame, os, time

class KitchenMinderAudio(object):
    def __init__(self):
        pygame.mixer.init()
        self.channel = pygame.mixer.Channel(0)
        self.audiofiles = {}
        basedir = os.path.dirname(os.path.realpath(__file__)) + "/audio/"
        try:
            files = os.listdir(basedir)
        except:
            files = []
        for f in files:
            file = basedir + f
            self.audiofiles[f.split('.')[0]] = {'audio': pygame.mixer.Sound(file), 'lastplayed': 0}
            self.cbLog("debug", "Audio:Loaded audio: " + str(file))
        self.reset()

    def reset(self):
        """
        Clears the audio state
        """
        self.count = 0
        for f in self.audiofiles.values():
            f['lastplayed'] = 0

    def play(self, audio, interval):
        if not self.audiofiles.has_key(audio):
            self.cbLog("debug", "Audio: No audio file: " + str(audio))
            return

        now = time.time()
        if self.audiofiles[audio]['lastplayed'] + interval > now:
            self.cbLog("debug", "Audio: Playing within the interval so not repeated")
            return

        self.channel.stop()
        self.cbLog("debug", "Audio:Playing: " + str(audio))
        self.channel.play(self.audiofiles[audio]['audio'])
        self.audiofiles[audio]['lastplayed'] = now
        self.count += 1
