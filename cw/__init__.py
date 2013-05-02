#!/usr/bin/env python
# -*- coding: utf-8 -*-

import util
import battle
import data
import dice
import effectmotion
import event
import eventhandler
import eventrelay
import scenariodb
import setting
import animation
import thread
import header
import image
import imageretouch
import frame
import deck
import character
import effectbooster
import content
import xmlcreater

import dialog
import debug
import sprite


# CWPyThread
cwpy = thread.CWPy()

# アプリケーション情報
APP_VERSION = (0, 1, 2)
APP_NAME = "CardWirthPy"

# サイズ
SIZE_SCR = (640, 480)
SIZE_GAME = (632, 453)
SIZE_AREA = (632, 420)

# 特殊エリアのID
AREAS_SP = (0, -1, -2, -3, -4, -5)
AREAS_TRADE = (-1, -2, -5)       # カード移動操作エリア
AREA_SELECT = 0                  # ターゲット選択エリア
AREA_TRADE1 = -1                 # カード移動操作エリア(宿・パーティなし時)
AREA_TRADE2 = -2                 # カード移動操作エリア(宿・パーティロード中時)
AREA_TRADE3 = -5                 # カード移動操作エリア(キャンプエリア)
AREA_BREAKUP = -3                # パーティ解散エリア
AREA_CAMP = -4                   # キャンプエリア

# カードポケットのインデックス
POCKET_SKILL = 0
POCKET_ITEM = 1
POCKET_BEAST = 2

# イベント用子コンテンツ特殊インデックス
IDX_TREEEND = -1

# 対応拡張子
EXTS_IMG = (".bmp", ".jpg", ".jpeg", ".png", ".gif", "pcx", ".tif", ".xpm")
EXTS_MSC = (".mid", ".midi", ".mp3", ".ogg")
EXTS_SND = (".wav", ".wave", ".ogg")

def main():
    pass

if __name__ == "__main__":
    main()

