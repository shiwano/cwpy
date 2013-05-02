#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base
import bgimage
import dialog
import effectmotion
import xmltemplate


class ContentBase(base.CWBinaryBase):
    def __init__(self, parent, f, tag, type):
        base.CWBinaryBase.__init__(self, parent, f)
        self.xmltype = "Content"
        self.tag = tag
        self.type = type
        self.name = f.string()
        children_num = f.dword() % 10000
        self.children = [Content(self, f) for cnt in xrange(children_num)]

        # 宿データの埋め込みカードのコンテントは
        # 子コンテントデータの後ろに"dword()"(5)が埋め込まれている。
        if self.is_yadodata():
            f.dword()

        self.properties = {}

    def get_xmldict(self, indent):
        d = {"indent": self.get_indent(indent),
             "tag": self.tag,
             "type": ' type="%s"' % (self.type) if self.type else "",
             "name": ' name="%s"' % (self.name) if self.name else "",
             "properties": self.get_propertiestext(self.properties),
             "children": "",
             "contents": self.get_childrentext(self.children, indent + 2),
             }
        return d

class StartContent(ContentBase):
    pass

class LinkStartContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["link"] = f.string()

class StartBattleContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()

class EndContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["complete"] = f.bool()

class EndBadEndContent(ContentBase):
    pass

class ChangeAreaContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()

class TalkMessageContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["path"] = self.get_materialpath(f.string())
        self.text = f.string(True)

    def get_xmldict(self, indent):
        d = ContentBase.get_xmldict(self, indent)
        s1 = self.get_indent(indent + 1)
        d["children"] = "\n%s<Text>%s</Text>" % (s1, self.text)
        return d

class PlayBgmContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["path"] = self.get_materialpath(f.string())

class ChangeBgImageContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        bgimgs_num = f.dword()
        self.bgimgs = [bgimage.BgImage(self, f) for cnt in xrange(bgimgs_num)]

    def get_xmldict(self, indent):
        d = ContentBase.get_xmldict(self, indent)
        s1 = self.get_indent(indent + 1)
        s2 = self.get_childrentext(self.bgimgs, indent + 2)
        d["children"] = "\n%s<BgImages>%s\n%s</BgImages>" % (s1, s2, s1)
        return d

class PlaySoundContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["path"] = self.get_materialpath(f.string())

class WaitContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["value"] = f.dword()

class EffectContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["level"] = f.dword()
        targetm = f.byte()

        # 効果コンテントの適用メンバには"選択中以外のメンバ"は存在しない。
        # 代わりに"パーティ全体"となる。
        if targetm == 2:
            targetm = 6

        self.properties["targetm"] = self.conv_target_member(targetm)
        self.properties["effecttype"] = self.conv_card_effecttype(f.byte())
        self.properties["resisttype"] = self.conv_card_resisttype(f.byte())
        self.properties["successrate"] = f.dword()
        self.properties["sound"] = self.get_materialpath(f.string())
        self.properties["visual"] = self.conv_card_visualeffect(f.byte())
        motions_num = f.dword()
        self.motions = [effectmotion.EffectMotion(self, f)
                                        for cnt in xrange(motions_num)]

    def get_xmldict(self, indent):
        d = ContentBase.get_xmldict(self, indent)
        s1 = self.get_indent(indent + 1)
        s2 = self.get_childrentext(self.motions, indent + 2)
        d["children"] = "\n%s<Motions>%s\n%s</Motions>" % (s1, s2, s1)
        return d

class BranchSelectContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["targetall"] = f.bool()
        self.properties["random"] = f.bool()

class BranchAbilityContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["value"] = f.dword()
        self.properties["targetm"] = self.conv_target_member(f.byte())
        self.properties["physical"] = self.conv_card_physicalability(f.dword())
        self.properties["mental"] = self.conv_card_mentalability(f.dword())

class BranchRandomContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["value"] = f.dword()

class BranchFlagContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["flag"] = f.string()

class SetFlagContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["flag"] = f.string()
        self.properties["value"] = f.bool()

class BranchMultiStepContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["step"] = f.string()

class SetStepContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["step"] = f.string()
        self.properties["value"] = f.dword()

class BranchCastContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()

class BranchItemContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class BranchSkillContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class BranchInfoContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()

class BranchBeastContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class BranchMoneyContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["value"] = f.dword()

class BranchCouponContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["coupon"] = f.string()
        f.dword() # 不明
        self.properties["targets"] = self.conv_target_scope(f.byte())

class GetCastContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()

class GetItemContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class GetSkillContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class GetInfoContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()

class GetBeastContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class GetMoneyContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["value"] = f.dword()

class GetCouponContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["coupon"] = f.string()
        self.properties["value"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class LoseCastContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()

class LoseItemContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class LoseSkillContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class LoseInfoContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()

class LoseBeastContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["id"] = f.dword()
        self.properties["number"] = f.dword()
        self.properties["targets"] = self.conv_target_scope(f.byte())

class LoseMoneyContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["value"] = f.dword()

class LoseCouponContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["coupon"] = f.string()
        f.dword() # 不明
        self.properties["targets"] = self.conv_target_scope(f.byte())

class TalkDialogContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["targetm"] = self.conv_target_member(f.byte())
        dialogs_num = f.dword()
        self.dialogs = [dialog.Dialog(self, f) for cnt in xrange(dialogs_num)]

    def get_xmldict(self, indent):
        d = ContentBase.get_xmldict(self, indent)
        s1 = self.get_indent(indent + 1)
        s2 = self.get_childrentext(self.dialogs, indent + 2)
        d["children"] = "\n%s<Dialogs>%s\n%s</Dialogs>" % (s1, s2, s1)
        return d

class SetStepUpContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["step"] = f.string()

class SetStepDownContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["step"] = f.string()

class ReverseFlagContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["flag"] = f.string()

class BranchStepContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["step"] = f.string()
        self.properties["value"] = f.dword()

class ElapseTimeContent(ContentBase):
    pass

class BranchLevelContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["average"] = f.bool()
        self.properties["value"] = f.dword()

class BranchStatusContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["status"] = self.conv_statustype(f.byte())
        self.properties["targetm"] = self.conv_target_member(f.byte())

class BranchPartyNumberContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["value"] = f.dword()

class ShowPartyContent(ContentBase):
    pass

class HidePartyContent(ContentBase):
    pass

class EffectBreakContent(ContentBase):
    pass

class CallStartContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["call"] = f.string()

class LinkPackageContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["link"] = f.dword()

class CallPackageContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["call"] = f.dword()

class BranchAreaContent(ContentBase):
    pass

class BranchBattleContent(ContentBase):
    pass

class BranchCompleteStampContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["scenario"] = f.string()

class GetCompleteStampContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["scenario"] = f.string()

class LoseCompleteStampContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["scenario"] = f.string()

class BranchGossipContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["gossip"] = f.string()

class GetGossipContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["gossip"] = f.string()

class LoseGossipContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["gossip"] = f.string()

class BranchIsBattleContent(ContentBase):
    pass

class RedisplayContent(ContentBase):
    pass

class CheckFlagContent(ContentBase):
    def __init__(self, parent, f, tag, type):
        ContentBase.__init__(self, parent, f, tag, type)
        self.properties["flag"] = f.string()

def Content(parent, f):
    """Contentファクトリ。
    parent: CWBinaryBase
    f: CWFile
    """
    type = f.byte()
    tag, type = parent.conv_contenttype(type)
    return globals()[tag + type + "Content"](parent, f, tag, type)

def main():
    pass

if __name__ == "__main__":
    main()
