# Copyright (c) 2014 Afterthought Software Ltd. All rights reserved.
# This is Unpublished Proprietary Source Code of Afterthought Software Ltd.

import pygame

cachedSurfaces = {}

class TextLines:

    DEFAULT_FONT_SIZE = 100

    def __init__(self):
        self.baseFont = pygame.font.match_font('freesans')

    def renderTextLines(self, screen, linesArray, cacheKey=None):
        surface = self.getTextSurface(screen.get_rect(), linesArray, cacheKey)
        self.renderSurface(screen, surface)

    def getTextSurface(self, rect, linesArray, colour=(255, 255, 255), cacheKey=None):
        """
        Render lines of text from linesArray, fitting them within targetSurface.

        linesArray elements may be strings or tuples. Strings will be rendered
        at default font size. Tuples should be of the form (text, scaling)
        where scaling is a float and specifies the proportion of the default
        font size to use to render text.
        """

        if cacheKey in cachedSurfaces:
            (lines, surface) = cachedSurfaces[cacheKey]
            if lines == linesArray:
                return surface

        padding = 0.85
        requiredWidth = 0
        requiredHeight = 0

        for text in linesArray:
            fontSize = self.DEFAULT_FONT_SIZE
            if isinstance(text, tuple):
                (text, scaling) = text
                fontSize = int(fontSize * scaling)
            font = pygame.font.Font(self.baseFont, fontSize)
            (width, height) = font.size(text)
            requiredWidth = max([width, requiredWidth])
            requiredHeight += height

        widthScaleFactor = (rect.width * padding) / requiredWidth
        heightScaleFactor = (rect.height * padding) / requiredHeight
        scaleFactor = min([widthScaleFactor, heightScaleFactor])

        # Render the lines with the correct font size
        fontSize = int(self.DEFAULT_FONT_SIZE * scaleFactor)
        lines = [self._renderText(l, fontSize, colour) for l in linesArray]

        # We work out the actual height so we end up with vertically centred
        # text
        actualHeight = sum([l.get_rect().height for l in lines])
        surface = pygame.Surface((rect.width * padding, actualHeight))

        topOffset = 0
        for line in lines:
            linepos = line.get_rect()
            linepos.centerx = surface.get_rect().centerx
            linepos.top = topOffset
            surface.blit(line, linepos)
            topOffset = linepos.bottom

        if cacheKey is not None:
            cachedSurfaces[cacheKey] = (linesArray, surface.copy())

        return surface

    def renderSurface(self, screen, surface):
        surfacepos = surface.get_rect()
        surfacepos.center = screen.get_rect().center
        screen.fill((0, 0, 0))
        screen.blit(surface, surfacepos)

    def _renderText(self, text, fontSize=DEFAULT_FONT_SIZE, colour=(255, 255, 255)):
        if isinstance(text, tuple):
            (text, scaling) = text
            fontSize = int(fontSize * scaling)

        font = pygame.font.Font(self.baseFont, fontSize)
        return font.render(text, True, colour, (0, 0, 0))
