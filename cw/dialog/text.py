#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import wx

import cw


#-------------------------------------------------------------------------------
#　テキストダイアログ　スーパークラス
#-------------------------------------------------------------------------------

class Text(wx.Dialog):
    def __init__(self, parent, name):
        # ダイアログボックス
        wx.Dialog.__init__(self, parent, -1, name, size=(500, 290),
                            style=wx.CAPTION|wx.DIALOG_MODAL|wx.SYSTEM_MENU|wx.CLOSE_BOX)
        self.csize = self.GetClientSize()
        # panel
        self.toppanel = wx.Panel(self, -1, size=(500, 245))
        self.toppanel.SetBackgroundColour(wx.Colour(0, 0, 128))
        self.panel = wx.Panel(self, -1, style=wx.RAISED_BORDER)

        # text ctrl
        if self.list2:
            value = self.list2[self.index2]
        else:
            value = ""

        self.textctrl = wx.TextCtrl(self.toppanel, -1, value, size=(500, 220), style=wx.TE_MULTILINE)
        self.textctrl.SetBackgroundColour(wx.Colour(0, 0, 128))
        self.textctrl.SetForegroundColour(wx.WHITE)
        self.textctrl.SetFont(cw.cwpy.rsrc.get_wxfont("gothic", 10, weight=wx.NORMAL))
        self.textctrl.SetEditable(False)
        # close
        self.closebtn = cw.cwpy.rsrc.create_wxbutton(self.panel, wx.ID_CANCEL, (85, 24), u"閉じる")
        # left
        bmp = cw.cwpy.rsrc.buttons["LMOVE"]
        self.leftbtn = cw.cwpy.rsrc.create_wxbutton(self.panel, wx.ID_UP, (30, 30), bmp=bmp)
        # right
        bmp = cw.cwpy.rsrc.buttons["RMOVE"]
        self.rightbtn = cw.cwpy.rsrc.create_wxbutton(self.panel, wx.ID_DOWN, (30, 30), bmp=bmp)
        # choice
        self.combo = wx.ComboBox(self.toppanel, size=(140, 20), choices=self.list, style=wx.CB_READONLY)

        if self.list:
            self.combo.SetSelection(self.index)

        # button enable
        self._enable_btn()
        # layout
        self.__do_layout()
        # bind
        self.Bind(wx.EVT_BUTTON, self.OnClickLeftBtn, self.leftbtn)
        self.Bind(wx.EVT_BUTTON, self.OnClickRightBtn, self.rightbtn)
        self.Bind(wx.EVT_COMBOBOX, self.OnCombobox)
        self.toppanel.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnCombobox(self, event):
        self.index = self.combo.GetSelection()
        self.index2 = self.index
        value = self.list2[self.index2]

        # ZIPアーカイブのファイルエンコーディングと
        # 読み込むテキストファイルのエンコーディングが異なる場合、
        # エラーが出るので
        try:
            self.textctrl.SetValue(value)
        except:
            self.textctrl.SetValue(cw.util.decode_zipname(value))

    def OnClickLeftBtn(self, event):
        self.Parent.OnClickLeftBtn(event)
        self._enable_btn()
        self.list, self.list2 = self.Parent.get_texts()
        self.index = 0
        self.index2 = 0

        if self.list2:
            value = self.list2[self.index2]
        else:
            value = ""

        self.textctrl.SetValue(value)
        self.combo.SetItems(self.list)

        if self.list:
            self.combo.SetSelection(self.index)

        # notextfile
        self.draw_notextfile()

    def OnClickRightBtn(self, event):
        self.Parent.OnClickRightBtn(event)
        self._enable_btn()
        self.list, self.list2 = self.Parent.get_texts()
        self.index = 0
        self.index2 = 0

        if self.list2:
            value = self.list2[self.index2]
        else:
            value = ""

        self.textctrl.SetValue(value)
        self.combo.SetItems(self.list)

        if self.list:
            self.combo.SetSelection(self.index)

        # notextfile
        self.draw_notextfile()

    def OnPaint(self, event):
        self.draw()

    def draw(self, update=False):
        if update:
            cw.cwpy.sounds[u"システム・改ページ"].play()
            dc = wx.ClientDC(self.toppanel)
        else:
            dc = wx.PaintDC(self.toppanel)

        self.toppanel.PrepareDC(dc)
        dc.SetTextForeground(wx.LIGHT_GREY)
        dc.SetFont(cw.cwpy.rsrc.get_wxfont("uigothic", size=11))
        s = u"添付テキスト"
        dc.DrawText(s, 10, 2)
        s = u"参照ファイル"
        w = dc.GetTextExtent(s)[0]
        w = w + 5 + self.combo.GetSize()[0]
        dc.DrawText(s, self.csize[0] - w, 2)
        # no text file
        self.draw_notextfile()

    def draw_notextfile(self):
        if not self.list2:
            dc = wx.ClientDC(self.textctrl)
            dc.SetTextForeground(wx.LIGHT_GREY)
            dc.SetFont(cw.cwpy.rsrc.get_wxfont("uigothic", size=14))
            # 文字
            s = "No Text File"
            size = dc.GetTextExtent(s)
            size2 = self.textctrl.GetSize()
            pos = (size2[0]-size[0])/2, (size2[1]-size[1])/2
            dc.DrawText(s, pos[0], pos[1])
            # ボックス
            size = size[0] + 60, size[1] + 20
            pos = pos[0] - 30, pos[1] - 10
            cw.util.draw_box(dc, pos, size)

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_panel = wx.BoxSizer(wx.HORIZONTAL)
        sizer_toppanel = wx.BoxSizer(wx.VERTICAL)
        sizer_topbar = wx.BoxSizer(wx.HORIZONTAL)

        # トップバー
        size = self.combo.GetSize()
        sizer_topbar.Add((500-size[0], 0), 0, 0, 0)
        sizer_topbar.Add(self.combo, 0, 0, 0)
        sizer_toppanel.Add(sizer_topbar, 0, 0, 0)
        sizer_toppanel.Add(self.textctrl, 0, 0, 0)
        self.toppanel.SetSizer(sizer_toppanel)

        margin = (self.csize[0] - 145) / 2
        margin2 = margin + (self.csize[0] - 145) % 2
        sizer_panel.Add(self.leftbtn, 0, 0, 0)
        sizer_panel.Add((margin, 0), 0, 0, 0)
        sizer_panel.Add(self.closebtn, 0, wx.TOP|wx.BOTTOM, 3)
        sizer_panel.Add((margin2, 0), 0, 0, 0)
        sizer_panel.Add(self.rightbtn, 0, 0, 0)
        self.panel.SetSizer(sizer_panel)

        sizer_1.Add(self.toppanel, 1, 0, 0)
        sizer_1.Add(self.panel, 0, 0, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def _enable_btn(self):
        # リストが空だったらボタンを無効化
        if self.Parent.list:
            if len(self.Parent.list) == 1:
                self.rightbtn.Disable()
                self.leftbtn.Disable()
            else:
                self.rightbtn.Enable()
                self.leftbtn.Enable()
                self.closebtn.Enable()
        else:
            self.rightbtn.Disable()
            self.leftbtn.Disable()
            self.closebtn.Disable()
#-------------------------------------------------------------------------------
#　リードミーダイアログ
#-------------------------------------------------------------------------------

class Readme(Text):
    def __init__(self, parent, name, lists):
        self.list = lists[0]
        self.index = 0
        self.list2 = lists[1]
        self.index2 = 0
        Text.__init__(self, parent, name)

def main():
    pass

if __name__ == "__main__":
    main()
