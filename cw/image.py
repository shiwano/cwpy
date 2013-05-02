#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import wx
import pygame
from pygame.locals import *

import cw


class Image(object):
    def __init__(self, image):
        self.image = image

    def get_image(self):
        return self.image

    def get_negaimg(self):
        image = self.get_image()
        return cw.imageretouch.to_negative(image)

    def get_wxbmp(self):
        image = self.get_image()
        return conv2wxbmp(image)

    def get_wxnegabmp(self):
        image = self.get_negaimg()
        return conv2wxbmp(image)

class CardImage(Image):
    def __init__(self, path, bgtype, name="", premium=""):
        """
        カード画像と背景画像とカード名を合成・加工し、
        wxPythonとPygame両方で使える画像オブジェクトを生成する。
        """
        self.name = name
        self.path = path
        # FIXME: 画像ファイル読み込みにディスクキャッシュをきかすため。
        cw.util.load_image(path)
        self.premium = premium
        self.cardbg = cw.cwpy.rsrc.cardbgs[bgtype]
        self.rect = self.cardbg.get_rect()

    def get_image(self):
        image = self.cardbg.copy()

        # プレミア画像
        if self.premium == "Rare":
            subimg = cw.cwpy.rsrc.cardbgs["RARE"]
            image.blit(subimg, (64, 5))
            image.blit(subimg, (5, 64))
        elif self.premium == "Premium":
            subimg = cw.cwpy.rsrc.cardbgs["PREMIER"]
            image.blit(subimg, (64, 5))
            image.blit(subimg, (5, 41))

        path = cw.util.get_yadofilepath(self.path)

        if not path:
            path = self.path

        subimg = cw.util.load_image(path, True)
        image.blit(subimg, (3, 13))
        font = cw.cwpy.rsrc.fonts["mcard_name"]
        subimg = font.render(self.name, True, (0, 0, 0))
        w, h = subimg.get_size()

        if w + 3 > self.rect.w:
            size = (self.rect.w - 6, h)
            subimg = pygame.transform.scale(subimg, size)

        image.blit(subimg, (3, 4))
        return image

    def get_cardimg(self, header):
        if header.negaflag:
            image = self.get_negaimg()
        else:
            image = self.get_image()

        if header.type in ("ItemCard", "BeastCard"):
            uselimit, maxn = header.get_uselimit()

            # 使用回数(数字)
            if maxn or (header.type == "BeastCard" and not header.attachment):
                font = cw.cwpy.rsrc.fonts["card_uselimit"]
                s = str(uselimit)
                subimg = font.render(s, False, (0, 0, 0))
                pos = 5, 90
                image.blit(subimg, (pos[0]+1, pos[1]))
                image.blit(subimg, (pos[0]-1, pos[1]))
                image.blit(subimg, (pos[0], pos[1]+1))
                image.blit(subimg, (pos[0], pos[1]-1))

                if header.recycle:
                    colour = (255, 255, 0)
                else:
                    colour = (255, 255, 255)

                subimg = font.render(s, False, colour)
                image.blit(subimg, pos)

        if isinstance(header.get_owner(), cw.character.Character):
            # 適性値
            key = "HAND" + str(header.get_vocation_level())
            subimg = cw.cwpy.rsrc.stones[key]
            image.blit(subimg, (60, 90))

            # 使用回数(画像)
            if header.type == "SkillCard":
                key = "HAND" + str(header.get_uselimit_level() + 5)
                subimg = cw.cwpy.rsrc.stones[key]
                image.blit(subimg, (60, 75))

            # ホールド
            if header.hold:
                subimg = cw.cwpy.rsrc.cardbgs["HOLD"]
                image.blit(subimg, (0, 0))

            # ペナルティ
            if header.penalty:
                subimg = cw.cwpy.rsrc.cardbgs["PENALTY"]
                image.blit(subimg, (0, 0))

        return image

    def get_negaimg(self):
        # カード画像の外枠は色反転しない
        image = self.get_image()
        return cw.imageretouch.to_negative_for_card(image)

    def get_clickedimg(self, rect=None):
        if not rect:
            rect = self.rect

        size = (rect.w * 9 / 10, rect.h * 9 / 10)
        negaimg = self.get_negaimg()
        return pygame.transform.scale(negaimg, size)

    def get_wxclickedbmp(self):
        image = self.get_clickedimg()
        return conv2wxbmp(image)

    def get_cardwxbmp(self, header):
        image = self.get_cardimg(header)
        return conv2wxbmp(image)

    def update(self, card):
        pass

class LargeCardImage(CardImage):
    def __init__(self, path, bgtype, name="", premium=""):
        CardImage.__init__(self, path, "LARGE", name, premium)

    def get_image(self):
        image = self.cardbg.copy()

        # プレミア画像
        if self.premium == "Rare":
            subimg = cw.cwpy.rsrc.cardbgs["RARE"]
            image.blit(subimg, (64, 5))
            image.blit(subimg, (5, 64))
        elif self.premium == "Premium":
            subimg = cw.cwpy.rsrc.cardbgs["PREMIER"]
            image.blit(subimg, (64, 5))
            image.blit(subimg, (5, 41))

        subimg = cw.util.load_image(self.path, True)
        image.blit(subimg, (10, 23))
        font = cw.cwpy.rsrc.fonts["mcard_name"]
        subimg = font.render(self.name, True, (0, 0, 0))
        w, h = subimg.get_size()

        if w + 3 > self.rect.w:
            size = (self.rect.w - 12, h)
            subimg = pygame.transform.smoothscale(subimg, size)

        image.blit(subimg, (6, 6))
        return image

class CharacterCardImage(CardImage):
    def __init__(self, ccard, pos=(0, 0)):
        # カード画像
        self.cardimg = cw.util.load_image(ccard.imgpath, True)
        # フォント画像(カード名)
        self.set_nameimg(ccard.name)
        # フォント画像(レベル)
        self.set_levelimg(ccard.level)
        # ライフバー画像
        self.lifeimg = pygame.Surface((79, 13)).convert()
        self.lifeguage = cw.cwpy.rsrc.statuses["LIFEGUAGE"]
        self.lifebar = cw.cwpy.rsrc.statuses["LIFEBAR"]
        self.lifeimg.set_colorkey(self.lifeguage.get_at((0,0)), RLEACCEL)
        # rect
        self.rect = pygame.Rect(pos, (95, 130))

    def set_nameimg(self, name):
        font = cw.cwpy.rsrc.fonts["pcard_name"]
        self.nameimg = font.render(name, True, (0, 0, 0))
        w, h = self.nameimg.get_size()

        if w + 14 > 95:
            size = (95 - 14, h)
            self.nameimg = pygame.transform.smoothscale(self.nameimg, size)

    def set_levelimg(self, level):
        font = cw.cwpy.rsrc.fonts["pcard_level"]
        s = str(level)
        size = (15 * (len(s)-1) + 17, 31)
        self.levelimg = pygame.Surface(size, SRCALPHA).convert_alpha()

        for index, char in enumerate(s):
            subimg = font.render(char, True, (92, 92, 92))
            self.levelimg.blit(subimg, (15 * index, 0))

    def update(self, ccard):
        # 画像合成
        bgname = self.get_cardbgname(ccard)
        self.image = cw.cwpy.rsrc.cardbgs[bgname].copy()
        self.image.blit(self.levelimg, (91 - self.levelimg.get_width(), 0))
        self.image.blit(self.cardimg, (11, 17))
        self.image.blit(self.nameimg, (7, 4))

        if ccard.is_analyzable():
            lifeper = ccard.get_lifeper()
            self.lifeimg.blit(self.lifebar, (int(0.79 * (lifeper - 100)), 1))
            self.lifeimg.blit(self.lifeguage, (0, 0))
            self.image.blit(self.lifeimg, (9, 111))

        # ステータス画像追加
        self.update_statusimg(ccard)

    def update_statusimg(self, ccard):
        seq = []
        beastnum = ccard.has_beast()

        if beastnum: # 召喚獣所持(付帯召喚以外)
            image = cw.cwpy.rsrc.statuses["SUMMON"].copy()
            font = cw.cwpy.rsrc.fonts["statusimg"]
            pos = 8, 4
            s = str(beastnum)
            subimg = font.render(s, False, (0, 0, 0))
            image.blit(subimg, (pos[0]+1, pos[1]))
            image.blit(subimg, (pos[0]-1, pos[1]))
            image.blit(subimg, (pos[0], pos[1]+1))
            image.blit(subimg, (pos[0], pos[1]-1))
            subimg = font.render(s, False, (255, 255, 255))
            image.blit(subimg, pos)
            seq.append(image)
        if ccard.is_poison(): # 中毒
            seq.append(cw.cwpy.rsrc.statuses["BODY0"])
        if ccard.is_confuse(): # 混乱
            seq.append(cw.cwpy.rsrc.statuses["MIND2"])
        elif ccard.is_overheat(): # 激昂
            seq.append(cw.cwpy.rsrc.statuses["MIND3"])
        elif ccard.is_brave(): # 勇敢
            seq.append(cw.cwpy.rsrc.statuses["MIND4"])
        elif ccard.is_panic(): # 恐慌
            seq.append(cw.cwpy.rsrc.statuses["MIND5"])
        if ccard.is_silence(): # 沈黙
            seq.append(cw.cwpy.rsrc.statuses["MAGIC1"])
        if ccard.is_faceup(): # 暴露
            seq.append(cw.cwpy.rsrc.statuses["MAGIC2"])
        if ccard.is_antimagic(): # 魔法無効化
            seq.append(cw.cwpy.rsrc.statuses["MAGIC3"])
        if ccard.enhance_act > 0: # 行動力強化
            seq.append(cw.cwpy.rsrc.statuses["UP0"])
        elif ccard.enhance_act < 0: # 行動力弱化
            seq.append(cw.cwpy.rsrc.statuses["DOWN0"])
        if ccard.enhance_avo > 0: # 回避力強化
            seq.append(cw.cwpy.rsrc.statuses["UP1"])
        elif ccard.enhance_avo < 0: # 回避力弱化
            seq.append(cw.cwpy.rsrc.statuses["DOWN1"])
        if ccard.enhance_res > 0: # 抵抗力強化
            seq.append(cw.cwpy.rsrc.statuses["UP2"])
        elif ccard.enhance_res < 0: # 抵抗力弱化
            seq.append(cw.cwpy.rsrc.statuses["DOWN2"])
        if ccard.enhance_def > 0: # 防御力強化
            seq.append(cw.cwpy.rsrc.statuses["UP3"])
        elif ccard.enhance_def < 0: # 防御力弱化
            seq.append(cw.cwpy.rsrc.statuses["DOWN3"])

        x, y = 7, 92

        for index, subimg in enumerate(seq):
            pos = (x + index / 5 * 17, y - index * 17 + index / 5 * 85)
            self.image.blit(subimg, pos)

    def get_cardbgname(self, ccard):
        if ccard.is_unconscious():
            return "FAINT"  # 意識不明
        elif ccard.is_petrified():
            return "PETRIF" # 石化
        elif ccard.is_paralyze():
            return "PARALY" # 麻痺
        elif ccard.is_sleep():
            return "SLEEP"  # 睡眠
        elif ccard.is_bind():
            return "BIND"   # 呪縛
        elif ccard.is_heavyinjured():
            return "DANGER" # 重傷
        elif ccard.is_injured():
            return "INJURY" # 負傷
        else:
            return "LARGE"  # 正常

    def get_image(self):
        return self.image

    def get_cardwxbmp(self, header):
        return self.get_wxbmp()

    def get_cardimg(self, header):
        return self.get_image()

#-------------------------------------------------------------------------------
# 画像変換用関数
#-------------------------------------------------------------------------------

def conv2wxbmp(image):
    """pygame.Surfaceをwx.Bitmapに変換する。
    image: pygame.Surface
    """
    w, h = image.get_size()

    if image.get_flags() & SRCALPHA:
        buf = pygame.image.tostring(image, "RGBA")
        wxbmp = wx.BitmapFromBufferRGBA(w, h, buf)
    else:
        buf = pygame.image.tostring(image, "RGB")
        wxbmp = wx.BitmapFromBuffer(w, h, buf)

    if image.get_colorkey():
        r, g, b, a = image.get_at((0, 0))
        wxbmp.SetMaskColour(r, g, b)

    return wxbmp

def conv2surface(wxbmp):
    """wx.Bitmapをpygame.Surfaceに変換する。
    wxbmp: wx.Bitmap
    """
    w, h = wxbmp.GetSize()
    wximg = wxbmp.ConvertToImage()

    if wxbmp.HasAlpha():
        data = wximg.GetData()
        r_data = data[0::3]
        g_data = data[1::3]
        b_data = data[2::3]
        a_data = wximg.GetAlphaData()
        seq = []

        for cnt in xrange(w * h):
            seq.append((r_data[cnt] + g_data[cnt] + b_data[cnt] + a_data[cnt]))

        buf = "".join(seq)
        image = pygame.image.frombuffer(buf, (w, h), "RGBA").convert_alpha()
    else:
        wximg = wxbmp.ConvertToImage()
        buf = wximg.GetData()
        image = pygame.image.frombuffer(buf, (w, h), "RGB").convert()

    if wximg.HasMask():
        image.set_colorkey(wximg.GetOrFindMaskColour(), RLEACCEL)

    return image

def main():
    pass

if __name__ == "__main__":
    main()
