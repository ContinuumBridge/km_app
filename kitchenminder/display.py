import pygame
import os

from text_lines import TextLines

FOOTER_HEIGHT = 50

class KitchenMinderDisplay(object):
    def __init__(self, useFramebuffer=True):
        if useFramebuffer:
            os.putenv('SDL_VIDEODRIVER', 'fbcon')
            os.putenv("SDL_FBDEV",  "/dev/fb1")
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.set_mode((320, 240))
        self.setMessage("KitchenMinder")

    def _renderFooter(self, colour):
        bar = pygame.Surface((self.screen.get_rect().width, FOOTER_HEIGHT))
        bar.fill(pygame.Color(colour))
        barpos = bar.get_rect()
        barpos.bottom = self.screen.get_rect().bottom
        self.screen.blit(bar, barpos)

    def setMessage(self, msg, colour='white', showFooter=True):
        self.screen.fill(pygame.Color('black'))

        rect = self.screen.get_rect()
        if showFooter:
            rect.height = rect.height - FOOTER_HEIGHT
            self._renderFooter(colour)

        surface = TextLines().getTextSurface(rect,
                                             msg.split("\n"),
                                             colour=pygame.Color(colour))
        surfacepos = surface.get_rect()
        surfacepos.center = rect.center
        self.screen.blit(surface, surfacepos)

        pygame.display.update()
