import pygame, os, time, logging

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
            logging.debug("Audio:Loaded audio:" + file)
        self.reset()

    def reset(self):
        """
        Clears the audio state
        """
        self.count = 0
        for f in self.audiofiles.values():
            f['lastplayed'] = 0

    def play(self, audio, interval, maxcount=3):
        if not self.audiofiles.has_key(audio):
            logging.debug("Audio:No audio file:" + audio)
            return

        if self.count >= maxcount:
            logging.debug("Audio:Reached max count for this state")
            return

        now = time.time()
        if self.audiofiles[audio]['lastplayed'] + interval > now:
            logging.debug("Audio:Playing within the interval so not repeated")
            return

        self.channel.stop()
        logging.debug("Audio:Playing:" + audio)
        self.channel.play(self.audiofiles[audio]['audio'])
        self.audiofiles[audio]['lastplayed'] = now
        self.count += 1
