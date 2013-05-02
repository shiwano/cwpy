#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx

import cw


#-------------------------------------------------------------------------------
#　メッセージダイアログ
#-------------------------------------------------------------------------------

class Message(wx.Dialog):
    """
    メッセージダイアログ。
    mode=1だと「はい」「いいえ」。mode=2だと「閉じる」。
    """
    def __init__(self, parent, name, text, mode=2):
        wx.Dialog.__init__(self, parent, -1, name, size=(355, 120),
                            style=wx.CAPTION|wx.DIALOG_MODAL|wx.SYSTEM_MENU|wx.CLOSE_BOX)
        self.SetClientSize((349, 96))
        self.text = text
        self.mode = mode

        if self.mode == 1:
            # yes and no
            self.yesbtn = cw.cwpy.rsrc.create_wxbutton(self, wx.ID_OK, (120, 30), u"はい")
            self.nobtn = cw.cwpy.rsrc.create_wxbutton(self, wx.ID_CANCEL, (120, 30), u"いいえ")
        elif self.mode == 2:
            # close
            self.closebtn = cw.cwpy.rsrc.create_wxbutton(self, wx.ID_CANCEL, (120, 30), u"閉じる")

        # layout
        self.__do_layout()
        # bind
        self.Bind(wx.EVT_RIGHT_UP, self.OnCancel)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnCancel(self, event):
        cw.cwpy.sounds[u"システム・クリック"].play()
        btnevent = wx.PyCommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_CANCEL)
        self.ProcessEvent(btnevent)

    def OnPaint (self, evt):
        dc = wx.PaintDC(self)
        # background
        bmp = cw.cwpy.rsrc.dialogs["CAUTION"]
        csize = self.GetClientSize()
        cw.util.fill_bitmap(dc, bmp, csize)
        # massage
        dc.SetTextForeground(wx.BLACK)
        dc.SetFont(cw.cwpy.rsrc.get_wxfont("uigothic"))
        dc.DrawLabel(self.text, (0, 0, csize[0], 50), wx.ALIGN_CENTER)

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add((0, 55), 0, 0, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        csize = self.GetClientSize()

        if self.mode == 1:
            margin = (csize[0] - self.yesbtn.GetSize()[0] * 2) / 3
            sizer_2.Add(self.yesbtn, 0, wx.LEFT, margin)
            sizer_2.Add(self.nobtn, 0, wx.LEFT|wx.RIGHT, margin)
        elif self.mode == 2:
            margin = (csize[0] - self.closebtn.GetSize()[0]) / 2
            sizer_2.Add(self.closebtn, 0, wx.LEFT, margin)

        self.SetSizer(sizer_1)
        self.Layout()

class YesNoMessage(Message):
    def __init__(self, parent, name, text):
        Message.__init__(self, parent, name, text, 1)

class ErrorMessage(Message):
    def __init__(self, parent, text):
        cw.cwpy.sounds[u"システム・エラー"].play()
        Message.__init__(self, parent, u"エラーメッセージ", text, 2)

def main():
    pass

if __name__ == "__main__":
    main()
