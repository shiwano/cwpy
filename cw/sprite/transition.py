#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *

import cw
import base


class Transition(base.CWPySprite):
    def __init__(self, bgscr, speed):
        """背景変更時のトランジション用スプライト。
        image: 変更前の背景。
        speed: トランジション効果時のウェイト。
        """
        base.CWPySprite.__init__(self)
        self.image = bgscr
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.status = "hidden"
        self.frame = 0
        self.speed = speed

    def clear(self):
        self.image = pygame.Surface((0, 0)).convert()
        self.rect = self.image.get_rect(center=self.rect.center)
        self.status = "hidden"

    def update(self, scr):
        method = getattr(self, "update_" + self.status, None)

        if method:
            method(scr)

    def update_transition(self, scr):
        self.clear()

class Fade(Transition):
    def __init__(self, bgscr, speed):
        Transition.__init__(self, bgscr, speed)
        self.variation = - (11 - self.speed) * 2
        self.image.set_alpha(255)

    def update_transition(self, scr):
        self.frame += 1
        alpha = self.image.get_alpha()
        self.image.set_alpha(alpha + self.variation)

        if alpha == 0:
            self.frame = 0
            self.status = "hidden"

class PixelDissolve(Transition):
    def __init__(self, bgscr, speed):
        Transition.__init__(self, bgscr, speed)
        self.variation = (11 - self.speed) * 15
        self.sec_w = 10
        self.sec_h = 10
        self.rect_sec = pygame.Rect(0, 0, self.sec_w, self.sec_h)
        self.poslist = []

        for x in xrange(cw.SIZE_GAME[0] / self.sec_w + 1):
            for y in xrange(cw.SIZE_GAME[1] / self.sec_h + 1):
                self.poslist.append((x * self.sec_w, y * self.sec_h))

        self.poslist = cw.cwpy.dice.shuffle(self.poslist)
        self.image.set_colorkey((255, 255, 255))
        self.changecolor = (255, 255, 255)

    def update_transition(self, scr):
        self.frame += 1

        for cnt in xrange(self.variation):
            if self.poslist:
                x, y = self.poslist.pop()
                self.rect_sec.topleft = (x, y)
                self.image.fill(self.changecolor, self.rect_sec)
                self.image.set_at((x, y), self.changecolor)
            else:
                break

        if not self.poslist:
            self.frame = 0
            self.status = "hidden"

class Blinds(Transition):
    def __init__(self, bgscr, speed):
        Transition.__init__(self, bgscr, speed)
        self.variation = (11 - self.speed)
        self.num_split = 30
        self.poslist = []
        self.w_blinds = cw.SIZE_GAME[0] / self.num_split
        self.rect_blinds = pygame.Rect(0, 0, self.w_blinds, cw.SIZE_GAME[1])

        for n in xrange(self.num_split + 2):
            self.poslist.append((n * self.w_blinds, 0))

        self.image.set_colorkey((255, 255, 255))
        self.changecolor = (255, 255, 255)

    def update_transition(self, scr):
        self.frame += 1
        w = (self.frame * self.variation) / 5

        if not self.rect_blinds.w == w:
            self.rect_blinds.size = (w, cw.SIZE_GAME[1])

            for x, y in self.poslist:
                self.rect_blinds.topleft = (x - w, y)
                self.image.fill(self.changecolor, self.rect_blinds)

            if w >= self.w_blinds:
                self.frame = 0
                self.status = "hidden"

def get_transition((name, speed)):
    """現在表示中の背景を元にしたトランジションスプライトを返す。
    transitiontype: トランジション効果の種類名と速度のタプル。
    """
    if name == "Default":
        name = cw.cwpy.setting.transition

    if not isinstance(speed, int):
        speed = cw.cwpy.setting.transitionspeed

    if not speed == 0 and not name == "None":
        cls = globals().get(name, None)

        if cls:
            return cls(cw.cwpy.background.image.copy(), speed)

    return None

def main():
    pass

if __name__ == "__main__":
    main()
