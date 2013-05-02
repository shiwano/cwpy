#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *

import cw


class EventHandler(object):
    def run(self):
        cw.cwpy.has_inputevent = False

        # 左方向キー押しっぱなし
        if cw.cwpy.keyin[K_LEFT] > cw.cwpy.keyevent.threshold:
            self.dirkey_event(x=-1)
        # 右方向キー押しっぱなし
        elif cw.cwpy.keyin[K_RIGHT] > cw.cwpy.keyevent.threshold:
            self.dirkey_event(x=1)

        for event in cw.cwpy.events:
            if event.type == KEYDOWN:
                # ESCAPEキー
                if event.key == K_ESCAPE:
                    self.escapekey_event()
                # F1キー
                elif event.key == K_F1:
                    self.f1key_event()
                # F2キー
                elif event.key == K_F2:
                    self.f2key_event()
                # F3キー
                elif event.key == K_F3:
                    self.f3key_event()
                # F4キー
                elif event.key == K_F4:
                    self.f4key_event()
                # F9キー
                elif event.key == K_F9:
                    self.f9key_event()
                # リターンキー
                elif event.key == K_RETURN:
                    self.returnkey_event()
                # 上方向キー
                elif event.key == K_UP:
                    self.dirkey_event(y=-1)
                # 下方向キー
                elif event.key == K_DOWN:
                    self.dirkey_event(y=1)
                # 左方向キー
                elif event.key == K_LEFT:
                    self.dirkey_event(x=-1)
                # 右方向キー
                elif event.key == K_RIGHT:
                    self.dirkey_event(x=1)

            elif event.type == MOUSEBUTTONUP:
                # 左クリックイベント
                if event.button == 1:
                    self.lclick_event()

                # 右クリックイベント
                elif event.button == 3:
                    self.rclick_event()

            # ユーザイベント
            elif event.type == USEREVENT and hasattr(event, "func"):
                self.executing_event(event)

    def calc_index(self, value):
        length = len(cw.cwpy.list)
        index = cw.cwpy.index
        index += value

        if length == 0:
            index = -1
        elif index >= length:
            index = 0
        elif index < 0:
            index = length - 1

        return index

    def dirkey_event(self, x=0, y=0, pushing=False):
        """
        方向キーイベント。カードのフォーカスを変更する。
        """
        cw.cwpy.has_inputevent = True

        if x:
            cw.cwpy.index = self.calc_index(x)

            if not cw.cwpy.index < 0:
                sprite = cw.cwpy.list[cw.cwpy.index]
                cw.cwpy.change_selection(sprite)

        elif y:
            if y > 0:
                seq = cw.cwpy.get_pcards("unreversed")
            else:
                seq = cw.cwpy.get_mcards("visible")

            if seq:
                cw.cwpy.list = seq

            cw.cwpy.index = -1
            self.dirkey_event(x=1)

    def lclick_event(self):
        """
        左クリックイベント。
        """
        if cw.cwpy.selection:
            if cw.cwpy.selection.rect.collidepoint(cw.cwpy.mousepos):
                cw.cwpy.has_inputevent = True
                cw.cwpy.selection.lclick_event()

    def rclick_event(self):
        """
        右クリックイベント。
        """
        if cw.cwpy.selection:
            if cw.cwpy.selection.rect.collidepoint(cw.cwpy.mousepos):
                cw.cwpy.has_inputevent = True
                cw.cwpy.selection.rclick_event()
        elif cw.cwpy.background.rect.collidepoint(cw.cwpy.mousepos):
            # シナリオプレイ時、キャンプモード切替
            if cw.cwpy.status == "Scenario" and not cw.cwpy.is_dealing():
                cw.cwpy.has_inputevent = True
                cw.cwpy.sounds[u"システム・クリック"].play()

                if cw.cwpy.areaid == -4:
                    cw.cwpy.clear_specialarea()
                else:
                    cw.cwpy.change_specialarea(-4)

            # シナリオ戦闘時、戦闘行動選択ダイアログ表示
            elif cw.cwpy.battle and cw.cwpy.battle.is_ready():
                cw.cwpy.sounds[u"システム・クリック"].play()
                cw.cwpy.call_dlg("BATTLECOMMAND")

    def escapekey_event(self):
        """
        ESCAPEキーイベント。終了ダイアログ。
        """
        cw.cwpy.has_inputevent = True
        cw.cwpy.sounds[u"システム・クリック"].play()
        cw.cwpy.call_dlg("CLOSE")

    def f1key_event(self):
        """
        F1キーイベント。フルスクリーン化・解除
        """
        cw.cwpy.has_inputevent = True

        if cw.cwpy.is_showingdebugger() and not cw.cwpy.is_fullscreen():
            cw.cwpy.sounds[u"システム・シグナル"].play()
            s = u"デバッガ表示中はフルスクリーン化できません。"
            cw.cwpy.call_dlg("MESSAGE", text=s)
        else:
            cw.cwpy.set_fullscreen(not cw.cwpy.is_fullscreen())

    def f2key_event(self):
        """
        F2キーイベント。設定ダイアログを開く。
        """
        cw.cwpy.has_inputevent = True
        cw.cwpy.sounds[u"システム・クリック"].play()
        cw.cwpy.call_dlg("SETTINGS")

    def f3key_event(self):
        """
        F3キーイベント。デバッガを開閉する。
        """
        cw.cwpy.set_fullscreen(False)
        cw.cwpy.sounds[u"システム・改ページ"].play()

        if cw.cwpy.frame.debugger:
            cw.cwpy.frame.exec_func(cw.cwpy.frame.close_debugger)
        else:
            cw.cwpy.frame.exec_func(cw.cwpy.frame.show_debugger)

    def f4key_event(self):
        """
        F4キーイベント。
        """
        pass
##        for ecard in cw.cwpy.get_ecards():
##            for h in ecard.deck.talon:
##                print h.name, ecard.name
##
##        print "*"*20
##        import timeit
##        s = ("import cw;" +
##             "image = cw.util.load_image('ACTION0.png');" +
##             "cw.imageretouch.to_negative_for_card(image)")
##        timer = timeit.Timer(s)
##        print timer.timeit(5000)
##        # 回収された循環参照や回収不能オブジェクトが表示される
##        import gc
##        gc.set_debug(gc.DEBUG_LEAK)
##        gc.disable()
##        gc.collect()

    def f9key_event(self):
        """
        F9キーイベント。緊急非難。
        """
        if cw.cwpy.is_playingscenario():
            cw.cwpy.has_inputevent = True
            cw.cwpy.sounds[u"システム・シグナル"].play()
            cw.cwpy.call_dlg("F9")

    def returnkey_event(self):
        """
        リターンキーイベント。
        """
        if cw.cwpy.selection:
            cw.cwpy.has_inputevent = True
            cw.cwpy.selection.lclick_event()

    def executing_event(self, event):
        """
        cwpy.exec_func()でポストされたユーザイベント。
        CWPyスレッドで指定のメソッドを実行する。
        """
        cw.cwpy.has_inputevent = True
        func = event.func
        func(*event.args, **event.kwargs)

class EventHandlerForMessageWindow(EventHandler):
    def __init__(self, mwin):
        """メッセージウィンドウ表示中のイベントハンドラ。
        mwin: MessageWindowインスタンス。
        """
        self.mwin = mwin

    def run(self):
        cw.cwpy.has_inputevent = False

        # リターンキー押しっぱなし
        if cw.cwpy.keyin[K_RETURN] > cw.cwpy.keyevent.threshold:
            self.returnkey_event(True)
        # 上方向キー押しっぱなし
        elif cw.cwpy.keyin[K_UP] > cw.cwpy.keyevent.threshold:
            self.dirkey_event(y=-1)
        # 下方向キー押しっぱなし
        elif cw.cwpy.keyin[K_DOWN] > cw.cwpy.keyevent.threshold:
            self.dirkey_event(y=1)

        for event in cw.cwpy.events:
            if event.type == KEYDOWN:
                # ESCAPEキー
                if event.key == K_ESCAPE:
                    self.escapekey_event()
                # F1キー
                elif event.key == K_F1:
                    self.f1key_event()
                # F2キー
                elif event.key == K_F2:
                    self.f2key_event()
                # F3キー
                elif event.key == K_F3:
                    self.f3key_event()
                # F9キー
                elif event.key == K_F9:
                    self.f9key_event()
                # リターンキー
                elif event.key == K_RETURN:
                    self.returnkey_event()
                # 上方向キー
                elif event.key == K_UP:
                    self.dirkey_event(y=-1)
                # 下方向キー
                elif event.key == K_DOWN:
                    self.dirkey_event(y=1)

            elif event.type == MOUSEBUTTONUP:
                # マウスボタン押下(文字描画中のみ)
                if self.mwin.is_drawing and\
                        cw.cwpy.background.rect.collidepoint(cw.cwpy.mousepos):
                    self.mouse_event()
                # 左クリック
                elif event.button == 1:
                    self.lclick_event()
                # ミドルクリック
                elif event.button == 2:
                    self.mclick_event()
                # 右クリック
                elif event.button == 3:
                    self.rclick_event()
                # マウスホイール上移動
                elif event.button == 4:
                    self.wheel_event(y=-1)
                # マウスホイール下移動
                elif event.button == 5:
                    self.wheel_event(y=1)

            # ユーザイベント
            elif event.type == USEREVENT and hasattr(event, "func"):
                self.executing_event(event)

    def mouse_event(self):
        """
        全てのマウスボタン押下イベント。
        文字全て描画。
        """
        if self.mwin.is_drawing:
            cw.cwpy.has_inputevent = True
            self.mwin.draw_all()

    def lclick_event(self):
        """
        左クリックイベント。
        """
        if cw.cwpy.selection:
            if cw.cwpy.selection.rect.collidepoint(cw.cwpy.mousepos):
                cw.cwpy.has_inputevent = True
                cw.cwpy.selection.lclick_event()

        elif cw.cwpy.list and (len(cw.cwpy.list) == 1 or cw.cwpy.index >= 0):
            if cw.cwpy.background.rect.collidepoint(cw.cwpy.mousepos):
                cw.cwpy.has_inputevent = True
                sbar = cw.cwpy.list[cw.cwpy.index]
                sbar.lclick_event(skip=True)

    def mclick_event(self):
        """
        ミドルクリックイベント。
        """
        if cw.cwpy.selection and len(cw.cwpy.list) > 1:
            cw.cwpy.has_inputevent = True
            cw.cwpy.selection.lclick_event(skip=True)

    def rclick_event(self):
        """
        右クリックイベント。
        """
        if cw.cwpy.selection:
            if cw.cwpy.selection.rect.collidepoint(cw.cwpy.mousepos):
                cw.cwpy.has_inputevent = True
                cw.cwpy.selection.rclick_event()

    def returnkey_event(self, pushing=False):
        """
        リターンキーイベント。
        """
        # 文字描画中の時は文字全て描画
        if self.mwin.is_drawing:
            cw.cwpy.has_inputevent = True
            self.mwin.draw_all()

        # テキスト送り
        elif len(cw.cwpy.list) == 1:
            cw.cwpy.has_inputevent = True
            sbar = cw.cwpy.list[cw.cwpy.index]
            sbar.lclick_event(skip=True)
        elif not pushing and cw.cwpy.index >= 0:
            cw.cwpy.has_inputevent = True
            sbar = cw.cwpy.list[cw.cwpy.index]
            sbar.lclick_event(skip=True)

    def dirkey_event(self, x=0, y=0, pushing=False):
        """
        方向キーイベント。選択肢バーをフォーカスする。
        """
        if not self.mwin.is_drawing:
            cw.cwpy.has_inputevent = True
            cw.cwpy.index = self.calc_index(y)
            sbar = cw.cwpy.list[cw.cwpy.index]
            cw.cwpy.change_selection(sbar)

    def wheel_event(self, y=0):
        """
        ホイールイベント。
        """
        if cw.cwpy.has_inputevent:
            return

        if len(cw.cwpy.list) == 1 and y > 0:
            cw.cwpy.has_inputevent = True
            sbar = cw.cwpy.list[cw.cwpy.index]
            sbar.lclick_event(skip=True)

        elif cw.cwpy.list:
            cw.cwpy.has_inputevent = True
            self.dirkey_event(y=y)

def main():
    pass

if __name__ == "__main__":
    main()

