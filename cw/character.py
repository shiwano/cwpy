#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import pygame

import cw


class Character(object):
    def __init__(self, data=None):
        if data:
            self.data = data

        # 名前
        self.name = self.data.gettext("/Property/Name", "")
        # レベル
        self.level = self.data.getint("/Property/Level")
        # 各種所持カードのリスト
        self.cardpocket = self.get_cardpocket()
        # 現在ライフ・最大ライフ
        self.life = self.data.getint("/Property/Life")
        self.maxlife = self.data.getint("/Property/Life", "max")
        # 精神状態
        self.mentality = self.data.gettext("/Property/Status/Mentality")
        self.mentality_dur = self.data.getint("/Property/Status/Mentality",
                                                                    "duration")
        # 麻痺値
        self.paralyze = self.data.getint("/Property/Status/Paralyze")
        # 中毒値
        self.poison = self.data.getint("/Property/Status/Poison")
        # 束縛時間値
        self.bind = self.data.getint("/Property/Status/Bind", "duration")
        # 沈黙時間値
        self.silence = self.data.getint("/Property/Status/Silence", "duration")
        # 暴露時間値
        self.faceup = self.data.getint("/Property/Status/FaceUp", "duration")
        # 魔法無効時間値
        self.antimagic = self.data.getint("/Property/Status/AntiMagic",
                                                                    "duration")
        # 行動力強化値
        self.enhance_act = self.data.getint("/Property/Enhance/Action")
        self.enhance_act_dur = self.data.getint("/Property/Enhance/Action",
                                                                    "duration")
        # 回避力強化値
        self.enhance_avo = self.data.getint("/Property/Enhance/Avoid")
        self.enhance_avo_dur = self.data.getint("/Property/Enhance/Avoid",
                                                                    "duration")
        # 抵抗力強化値
        self.enhance_res = self.data.getint("/Property/Enhance/Resist")
        self.enhance_res_dur = self.data.getint("/Property/Enhance/Resist",
                                                                    "duration")
        # 防御力強化値
        self.enhance_def = self.data.getint("/Property/Enhance/Defense")
        self.enhance_def_dur = self.data.getint("/Property/Enhance/Defense",
                                                                    "duration")
        # 各種能力値
        e = self.data.getfind("/Property/Ability/Physical")
        self.physical = copy.copy(e.attrib)
        e = self.data.getfind("/Property/Ability/Mental")
        self.mental = copy.copy(e.attrib)
        e = self.data.getfind("/Property/Ability/Enhance")
        self.enhance = copy.copy(e.attrib)

        for d in (self.physical, self.mental, self.enhance):
            for key, value in d.iteritems():
                d[key] = int(value)

        # 特性
        e = self.data.getfind("/Property/Feature/Type")
        self.feature = copy.copy(e.attrib)
        e = self.data.getfind("/Property/Feature/NoEffect")
        self.noeffect = copy.copy(e.attrib)
        e = self.data.getfind("/Property/Feature/Resist")
        self.resist = copy.copy(e.attrib)
        e = self.data.getfind("/Property/Feature/Weakness")
        self.weakness = copy.copy(e.attrib)

        for d in (self.feature, self.noeffect, self.resist, self.weakness):
            for key, value in d.iteritems():
                d[key] = cw.util.str2bool(value)

        # デッキ
        self.deck = cw.deck.Deck(self)
        # 戦闘行動(Target, CardHeader)
        self.actiondata = None
        # 行動順位を決定する数値
        self.actionorder = 0
        # 時限クーポンのデータのリスト(name, flag_countable)
        self.timedcoupons = self.get_timedcoupons()
        # 対象消去されたか否か
        self._vanished = False

    def get_cardpocket(self):
        flag = bool(self.data.getroot().tag == "CastCard")
        maxnums = self.get_cardpocketspace()
        paths = ("/SkillCards", "/ItemCards", "/BeastCards")
        cardpocket = []

        for maxn, path in zip(maxnums, paths):
            headers = []

            for e in self.data.getfind(path):
                header = cw.header.CardHeader(owner=self, carddata=e,
                                                            from_scenario=flag)
                headers.append(header)

            # 最大所持数を越えたカードは消去
            for header in headers[maxn:]:
                self.data.remove(path, header.carddata)

            cardpocket.append(headers[:maxn])

        return tuple(cardpocket)

    def lost(self):
        """
        対象消去やゲームオーバー時に呼ばれる。
        Playerクラスでオーバーライト。
        """
        pass

    #---------------------------------------------------------------------------
    #　状態チェック用
    #---------------------------------------------------------------------------

    def is_normal(self):
        """
        通常の精神状態かどうかをbool値で返す。
        """
        return bool(self.mentality == "Normal")

    def is_panic(self):
        """
        恐慌状態かどうかをbool値で返す
        """
        return bool(self.mentality == "Panic")

    def is_brave(self):
        """
        勇敢状態かどうかをbool値で返す
        """
        return bool(self.mentality == "Brave")

    def is_overheat(self):
        """
        激昂状態かどうかをbool値で返す
        """
        return bool(self.mentality == "Overheat")

    def is_confuse(self):
        """
        混乱状態かどうかをbool値で返す
        """
        return bool(self.mentality == "Confuse")

    def is_sleep(self):
        """
        睡眠状態かどうかをbool値で返す
        """
        return bool(self.mentality == "Sleep")

    def is_paralyze(self):
        """
        麻痺または石化状態かどうかをbool値で返す
        """
        return bool(self.paralyze > 0)

    def is_poison(self):
        """
        中毒状態かどうかをbool値で返す
        """
        return bool(self.poison > 0)

    def is_bind(self):
        """
        呪縛状態かどうかをbool値で返す
        """
        return bool(self.bind > 0)

    def is_silence(self):
        """
        沈黙状態かどうかをbool値で返す。
        """
        return bool(self.silence > 0)

    def is_faceup(self):
        """
        暴露状態かどうかをbool値で返す。
        """
        return bool(self.faceup > 0)

    def is_antimagic(self):
        """
        魔法無効状態かどうかをbool値で返す。
        """
        return bool(self.antimagic > 0)

    def is_petrified(self):
        """
        石化状態かどうかをbool値で返す
        """
        return bool(self.paralyze > 20)

    def is_unconscious(self):
        """
        意識不明状態かどうかをbool値で返す
        """
        return bool(self.get_lifeper() == 0)

    def is_heavyinjured(self):
        """
        重傷状態かどうかをbool値で返す
        """
        return bool(self.get_lifeper() < 20)

    def is_injured(self):
        """
        負傷状態かどうかをbool値で返す
        """
        return bool(self.get_lifeper() < 100)

    def is_inactive(self):
        """
        行動不可状態かどうかをbool値で返す
        """
        b = self.is_sleep()
        b |= self.is_paralyze()
        b |= self.is_bind()
        b |= self.is_unconscious()
        b |= self.is_reversed()
        return b

    def is_active(self):
        """
        行動可能状態かどうかをbool値で返す
        """
        return not self.is_inactive()

    def is_dead(self):
        """
        非生存状態かどうかをbool値で返す
        """
        b = self.is_paralyze()
        b |= self.is_unconscious()
        b |= self.is_reversed()
        return b

    def is_alive(self):
        """
        生存状態かどうかをbool値で返す
        """
        return not self.is_dead()

    def is_fine(self):
        """
        健康状態かどうかをbool値で返す
        """
        return not self.is_injured()

    def is_analyzable(self):
        """
        各種データが暴露可能かどうかbool値で返す。
        EnemyCardのための処理。
        デバッグフラグがTrueだったら問答無用で暴露する。
        """
        if isinstance(self, Enemy):
            return cw.cwpy.debug or self.is_faceup()
        else:
            return True

    def is_avoidable(self):
        """
        回避判定可能かどうかbool値で返す。
        """
        return self.is_active()

    def is_resistable(self):
        """
        抵抗判定可能かどうかbool値で返す。
        呪縛状態でも抵抗できる。
        """
        b = self.is_sleep()
        b |= self.is_paralyze()
        b |= self.is_unconscious()
        return not b

    def is_reversed(self):
        """
        隠蔽状態かどうかbool値で返す。
        """
        return self.reversed

    def is_vanished(self):
        return self._vanished

    def has_beast(self):
        """
        付帯召喚じゃない召喚獣カードの所持数を返す。
        """
        return len([h for h in self.cardpocket[2] if not h.attachment])

    #---------------------------------------------------------------------------
    #　カード操作
    #---------------------------------------------------------------------------

    def use_card(self, targets, header):
        """targetsにカードを使用する。"""
        if not isinstance(targets, list):
            targets = [targets]

        data = header.carddata
        # TargetArrow削除
        cw.cwpy.clear_targetarrow()
        # 効果音鳴らす
        path = data.gettext("Property/SoundPath", "")
        cw.cwpy.play_sound(path)

        # 使用アニメーション
        if header.type == "BeastCard":
            cw.cwpy.set_inusecardimg(self, header, "hidden", center=True)
            inusecardimg = cw.cwpy.get_inusecardimg()
            cw.animation.animate_sprite(inusecardimg, "deal")
            cw.animation.animate_sprite(inusecardimg, "zoomin")
            pygame.time.wait(cw.cwpy.setting.frametime * 15)
            cw.animation.animate_sprite(inusecardimg, "zoomout")
            cw.animation.animate_sprite(inusecardimg, "hide")
        elif isinstance(self, cw.character.Friend):
            self.set_pos(center=(316, 142))
            self.status == "hidden"
            cw.cwpy.pcardgrp.add(self)
            cw.animation.animate_sprite(self, "deal")
            cw.animation.animate_sprite(self, "zoomin")
            cw.cwpy.set_inusecardimg(self, header, center=True)
            cw.cwpy.draw()
            pygame.time.wait(cw.cwpy.setting.frametime * 15)
            cw.cwpy.clear_inusecardimg()
            cw.animation.animate_sprite(self, "zoomout")
            cw.animation.animate_sprite(self, "hide")
            cw.cwpy.pcardgrp.remove(self)
        else:
            cw.cwpy.set_inusecardimg(self, header)
            cw.animation.animate_sprite(self, "zoomin")

        # カードイベント開始
        e = data.find("Events/Event")
        cw.event.CardEvent(e, header, self, targets).start()

    def throwaway_card(self, header, from_event=True):
        """
        引数のheaderのカードを破棄処理する。
        """
        cw.cwpy.trade("TRASHBOX", header=header, from_event=from_event)

    #---------------------------------------------------------------------------
    #　戦闘行動関係
    #---------------------------------------------------------------------------

    def action(self):
        """設定している戦闘行動を行う。
        BattleEngineからのみ呼ばれる。
        """
        if self.actiondata:
            targets, header, beasts = self.actiondata
            self.clear_action()

            # 召喚獣カードの使用
            for targets_b, header_b in beasts:
                self.use_card(targets_b, header_b)

                # 戦闘勝利チェック
                if cw.cwpy.battle.check_win():
                    raise cw.battle.BattleWinError()

            # 手札カードの使用
            if self.is_active():
                if header in self.deck.hand and not header.type == "ItemCard":
                    self.deck.hand.remove(header)

                self.use_card(targets, header)

    def set_action(self, target, header, beasts=[], auto=False):
        """
        戦闘行動を設定。
        auto: 自動手札選択から設定されたかどうか。
        """
        if auto:
            self.actiondata = (target, header, beasts)
        else:
            if self.actiondata:
                beasts = self.actiondata[2]

            self.actiondata = (target, header, beasts)
            cw.cwpy.sounds[u"システム・改ページ"].play()
            cw.cwpy.pre_dialogs.pop()

    def clear_action(self):
        self.actiondata = None

    #---------------------------------------------------------------------------
    #　判定用
    #---------------------------------------------------------------------------

    def decide_outcome(self, level, vocation, thresholdbonus=4, subbonus=0):
        """
        行為判定を行う。成功ならTrue。失敗ならFalseを返す。
        level: 判定レベル。
        vocation: 適性データ。(身体適性名, 精神適性名)のタプル。
        thresholdbonus: アクション元の適正値+行動力強化値。効果コンテントだと4。
        subbonus: 各種判定のサブボーナス(回避判定なら回避力強化値をあてる等)。
        """
        dice = cw.cwpy.dice.roll(2)

        if dice == 12:
            return True
        elif dice == 2:
            return False

        bonus = self.get_bonus(vocation) + subbonus
        bonus = bonus / 2 + bonus % 2
        n = dice + self.level + bonus
        thresholdbonus = thresholdbonus / 2 + thresholdbonus % 2
        threshold = cw.cwpy.dice.roll(2) + level + thresholdbonus

        if n > threshold:
            return True
        else:
            return False

    def decide_misfire(self, level):
        """
        カードの不発判定を行う。成功ならTrue。失敗ならFalseを返す。
        level: 判定レベル(カードの技能レベル)。
        """
        dice = cw.cwpy.dice.roll(2)
        threshold = level - self.level - 1

        if dice == 12:
            flag = True
        elif dice >= threshold:
            flag = True
        else:
            flag = False

        return flag

    #---------------------------------------------------------------------------
    #　戦闘行動設定関連
    #---------------------------------------------------------------------------

    def decide_actionorder(self):
        """
        行動順位を判定する数値をself.actionorderに設定。
        敏捷度と大胆性で判定。レベル・行動力は関係なし。
        """
        vocation_val = self.get_vocation_val(("agl", "uncautious")) + 4
        n = vocation_val / 2
        n2 = vocation_val % 2 * 5
        value = cw.cwpy.dice.roll(n, 10)

        if n2:
            value += cw.cwpy.dice.roll(1, n2)

        self.actionorder = value
        return value

    def decide_action(self):
        """
        自動手札選択。
        """
        if self.is_inactive() or not cw.cwpy.status == "ScenarioBattle":
            self.clear_action()
            return

        # 召喚獣カード
        beasts = []

        for header in self.cardpocket[2]:
            if header.is_autoselectable():
                targets, effectivetargets = header.get_targets()

                if effectivetargets:
                    if not header.allrange and len(targets) > 1:
                        targets = [cw.cwpy.dice.choice(effectivetargets)]

                    beasts.append((targets, header))

        # 使用するカード
        headers = []

        for header in self.deck.hand:
            if header.is_autoselectable():
                targets, effectivetargets = header.get_targets()

                if effectivetargets or header.target == "None":
                    if not header.allrange:
                        targets = effectivetargets

                    headers.append((targets, header))

        targets, header = self.decide_usecard(headers)

        if not header.allrange and len(targets) > 1:
            targets = [cw.cwpy.dice.choice(targets)]

        # 行動設定
        self.set_action(targets, header, beasts, True)

    def decide_usecard(self, headers):
        seq = []

        for index, t in enumerate(headers):
            targets, header = t

            # カード交換のソートキーは4固定
            if header.type == "ActionCard" and header.id == 0:
                sortkey = 4
            else:
                sortkey = header.get_vocation_val()

            seq.append((sortkey, len(targets), index, (targets, header)))

        seq.sort(reverse=True)
        seq2 = []

        for index, i in enumerate(seq):
            for cnt in xrange(len(seq) - index):
                seq2.append(i)

        return cw.cwpy.dice.choice(seq2)[3]

    #---------------------------------------------------------------------------
    #　状態取得用
    #---------------------------------------------------------------------------

    def get_cardpocketspace(self):
        """
        最大所持カード枚数を
        (スキルカード, アイテムカード, 召喚獣カード)のタプルで返す
        """
        maxskillnum = self.level / 2 + self.level % 2 + 2
        maxskillnum = cw.util.numwrap(maxskillnum, 1, 10)
        maxbeastnum = (self.level + 2) / 4

        if (self.level + 2) % 4:
            maxbeastnum += 1

        maxbeastnum = cw.util.numwrap(maxbeastnum, 1, 10)
        return (maxskillnum, maxskillnum, maxbeastnum)

    def get_lifeper(self):
        """
        ライフのパーセンテージを返す。
        """
        return 100 * self.life / self.maxlife

    def get_bonus(self, vocation):
        """
        適性値と行動力強化値を合計した、行為判定用のボーナス値を返す。
        vocation: 適性データ。(身体適性名, 精神適性名)のタプル。
        """
        return self.get_vocation_val(vocation) + self.get_enhance_act()

    def get_vocation_val(self, vocation):
        """
        適正値(身体適性値 + 精神適性値)を返す。
        引数のvocationは(身体適性名, 精神適性名)のタプル。
        """
        vocation = (vocation[0].lower(), vocation[1].lower())
        physical = vocation[0]
        mental = vocation[1].replace("un", "", 1)
        physical = self.physical.get(physical)
        mental = self.mental.get(mental)

        if vocation[1].find("un") > -1:
            mental = -mental

        return physical + mental

    def get_enhance_act(self):
        """
        行動力強化値を返す。行動力は効果コンテントによる強化値だけ。
        """
        return cw.util.numwrap(self.enhance_act, -10, 10)

    def get_enhance_def(self):
        """
        現在かけられている全ての防御力強化値の合計を返す。
        デフォルト強化値 + 効果コンテント強化値 + アイテム所持強化値。
        単体で+10の修正がない場合は、合計値が+10を越えていても+9を返す。
        """
        val1 = self.enhance.get("defense")
        val1 = cw.util.numwrap(val1, -10, 10)
        val2 = self.enhance_def
        val2 = cw.util.numwrap(val2, -10, 10)
        val3 = 0
        b = False

        for header in self.cardpocket[cw.POCKET_ITEM]:
            avoid, resist, defense = header.get_enhance_val()

            if defense >= 10:
                b = True

            val3 += defense

        if b:
            val3 = cw.util.numwrap(val3, -10, 10)
        else:
            val3 = cw.util.numwrap(val3, -10, 9)

        value = 0
        b = False

        for n in (val1, val2, val3):
            if n == 10:
                b = True

            value += n

        if b:
            value = cw.util.numwrap(value, -10, 10)
        else:
            value = cw.util.numwrap(value, -10, 9)

        return value

    def get_enhance_res(self):
        """
        現在かけられている全ての抵抗力強化値の合計を返す。
        デフォルト強化値 + 効果コンテント強化値 + アイテム所持強化値。
        """
        val1 = self.enhance.get("resist")
        val1 = cw.util.numwrap(val1, -10, 10)
        val2 = self.enhance_res
        val2 = cw.util.numwrap(val2, -10, 10)
        val3 = 0

        for header in self.cardpocket[cw.POCKET_ITEM]:
            avoid, resist, defense = header.get_enhance_val()
            val3 += resist

        val3 = cw.util.numwrap(val3, -10, 10)
        value = val1 + val2 + val3
        value = cw.util.numwrap(value, -10, 10)
        return value

    def get_enhance_avo(self):
        """
        現在かけられている全ての回避力強化値の合計を返す。
        デフォルト強化値 + 効果コンテント強化値 + アイテム所持強化値。
        """
        val1 = self.enhance.get("avoid")
        val1 = cw.util.numwrap(val1, -10, 10)
        val2 = self.enhance_avo
        val2 = cw.util.numwrap(val2, -10, 10)
        val3 = 0

        for header in self.cardpocket[cw.POCKET_ITEM]:
            avoid, resist, defense = header.get_enhance_val()
            val3 += avoid

        val3 = cw.util.numwrap(val3, -10, 10)
        value = val1 + val2 + val3
        value = cw.util.numwrap(value, -10, 10)
        return value

    #---------------------------------------------------------------------------
    #　クーポン関連
    #---------------------------------------------------------------------------

    def get_coupons(self):
        """
        所有クーポンをセット型で返す。
        """
        return set([e.text for e in self.data.getfind("/Property/Coupons")])

    def has_coupon(self, coupon):
        """
        引数のクーポンを所持しているかbool値で返す。
        """
        for e in self.data.getfind("/Property/Coupons"):
            if e.text == coupon:
                return True

        return False

    def get_couponsvalue(self):
        """
        全ての所持クーポンの点数を合計した値を返す。
        """
        cnt = 0

        for e in self.data.getfind("/Property/Coupons"):
            if e.text and not e.text.startswith(u"＠"):
                n = e.getint("", "value", 0)
                cnt += n

        return cnt

    def get_specialcoupons(self):
        """
        "＠"で始まる特殊クーポンの
        辞書(key=クーポン名, value=クーポン得点)を返す。
        """
        d = {}

        for e in self.data.getfind("/Property/Coupons"):
            if e.text and e.text.startswith(u"＠"):
                d[e.text] = e.getint("", "value", 0)

        return d

    def get_sex(self):
        sets = set([u"＿♂", u"＿♀"])

        for e in self.data.getfind("/Property/Coupons"):
            if e.text in sets:
                return e.text

        return None

    def get_age(self):
        sets = set([u"＿子供", u"＿若者", u"大人", u"老人"])

        for e in self.data.getfind("/Property/Coupons"):
            if e.text in sets:
                return e.text

        return None

    def get_talent(self):
        sets = set([u"＿標準型", u"＿万能型", u"＿勇将型", u"＿豪傑型",
                    u"＿知将型", u"＿策士型", u"＿英明型", u"＿無双型",
                    u"＿天才型", u"＿凡庸型"])

        for e in self.data.getfind("/Property/Coupons"):
            if e.text in sets:
                return e.text

        return None

    def count_timedcoupon(self, value=-1):
        """
        時限クーポンの点数を減らす。
        value: 減らす数。
        """
        if self.timedcoupons:
            self.data.is_edited = True
            names = set([name for name, flag in self.timedcoupons if flag])
            elements = [e for e in self.data.getfind("/Property/Coupons")
                                                            if e.text in names]

            for e in elements:
                if "value" in e.attrib:
                    n = int(e.get("value", 0)) + value
                    n = cw.util.numwrap(n, 0, 999)

                    if n > 0:
                        e.set("value", str(n))
                    else:
                        self.remove_coupon(e.text)

    def set_coupon(self, name, value):
        """
        クーポンを付与する。同名のクーポンがあったら上書き。
        時限クーポン("："or"；"で始まるクーポン)はtimedcouponsに登録する。
        name: クーポン名。
        value: クーポン点数。
        """
        value = cw.util.numwrap(int(value), 0, 999)
        self.remove_coupon(name)
        e = self.data.make_element("Coupon", name, {"value" : str(value)})
        self.data.append("/Property/Coupons", e)

        # 時限クーポン
        if name.startswith(u"：") or name.startswith(u"；"):
            timedcoupon = (name, bool(int(value)))
            self.timedcoupons.append(timedcoupon)

            # 隠蔽クーポン
            if name == u"：Ｒ" and not self.is_reversed():
                if not self.status == "hidden":
                    cw.animation.animate_sprite(self, "reverse")

                self.reversed = True

    def get_timedcoupons(self):
        """
        時限クーポンのデータをまとめたリストを返す。
        """
        seq = []

        for e in self.data.getfind("/Property/Coupons"):
            if e.text.startswith(u"：") or e.text.startswith(u"；"):
                 seq.append((e.text, not bool(e.get("value") == "0")))

        return seq

    def remove_coupon(self, name):
        """
        同じ名前のクーポンを全て剥奪する。
        name: クーポン名。
        """
        elements = [e for e in self.data.getfind("/Property/Coupons")
                                                        if e.text == name]

        for e in elements:
            self.data.remove("/Property/Coupons", e)

        # 時限クーポン
        if name.startswith(u"：") or name.startswith(u"；"):
            timedcoupons = [i for i in self.timedcoupons if i[0] == name]

            for timedcoupon in timedcoupons:
                self.timedcoupons.remove(timedcoupon)

            # 隠蔽クーポン
            if name == u"：Ｒ" and self.is_reversed():
                if not self.status == "hidden":
                    cw.animation.animate_sprite(self, "reverse")

                self.reversed = False

    def remove_timedcoupons(self, battleonly=False):
        """
        時限クーポンを削除する。
        battleonly: Trueの場合は"；"の時限クーポンのみ削除。
        """
        names = [name for name, value in self.timedcoupons]

        for name in names:
            if not battleonly or name.startswith(u"；"):
                self.remove_coupon(name)

    def remove_numbercoupon(self):
        """
        "＿１"等の番号クーポンを削除。
        """
        names = [u"＿１", u"＿２", u"＿３", u"＿４", u"＿５", u"＿６"]

        for name in names:
            self.remove_coupon(name)
    #---------------------------------------------------------------------------
    #　レベル変更用
    #---------------------------------------------------------------------------

    def check_levelup(self):
        coupons = self.get_specialcoupons()
        level = coupons[u"＠レベル原点"]

        if u"＠レベル上限" in coupons:
            limit = coupons[u"＠レベル上限"]
        elif u"＠本来の上限" in coupons:
            limit = coupons[u"＠本来の上限"]
            self.set_coupon(u"＠レベル上限", limit)
        else:
            limit = 10
            self.set_coupon(u"＠レベル上限", 10)

        cnt = self.get_couponsvalue()
        n = level * (level + 1)
        return bool(cnt >= n and limit > level)

    def set_level(self, value):
        # レベル
        self.level = value
        self.data.edit("/Property/Level", str(self.level))
        # 最大HPとHP
        vit = self.physical.get("vit")

        if vit < 1:
            vit = 1

        min = self.physical.get("min")

        if min < 1:
            min = 1

        maxlife = (vit / 2 + 4) * (self.level + 1) + min / 2
        self.maxlife += maxlife - self.maxlife
        self.data.edit("/Property/Life", str(self.maxlife), "max")
        self.set_life(self.maxlife)

        # レベル原点・EPクーポン操作
        for e in self.data.find("/Property/Coupons"):
            if not e.text:
                continue

            if e.text == u"＠レベル原点":
                e.attrib["value"] = str(self.level)
            elif e.text == u"＠ＥＰ":
                e.attrib["value"] = str(e.getint("", "value", 0) + 10)

    #---------------------------------------------------------------------------
    #　状態変更用
    #---------------------------------------------------------------------------

    def set_normalstatus(self):
        """
        すべての状態回復。状態異常回復。
        強化値もすべて0、付帯召喚以外の召喚獣カードも消去。
        """
        self.set_paralyze(-40)
        self.set_poison(-40)
        self.set_mentality("Normal", 0)
        self.set_bind(0)
        self.set_silence(0)
        self.set_faceup(0)
        self.set_antimagic(0)
        self.set_enhance_act(0, 0)
        self.set_enhance_avo(0, 0)
        self.set_enhance_res(0, 0)
        self.set_enhance_def(0, 0)
        self.set_beast(vanish=True)

    def set_fullrecovery(self):
        """
        完全回復処理。HP＆精神力＆状態異常回復。
        強化値もすべて0、付帯召喚以外の召喚獣カードも消去。
        """
        self.set_life(self.maxlife)
        self.set_paralyze(-40)
        self.set_poison(-40)
        self.set_mentality("Normal", 0)
        self.set_bind(0)
        self.set_silence(0)
        self.set_faceup(0)
        self.set_antimagic(0)
        self.set_enhance_act(0, 0)
        self.set_enhance_avo(0, 0)
        self.set_enhance_res(0, 0)
        self.set_enhance_def(0, 0)
        self.set_skillpower(True)
        self.set_beast(vanish=True)

    def set_life(self, value):
        """
        現在ライフに引数nの値を足す(nが負だと引き算でダメージ)。
        """
        self.life += value
        self.life = cw.util.numwrap(self.life, 0, self.maxlife)
        self.data.edit("/Property/Life", str(self.life))

    def set_paralyze(self, value):
        """
        麻痺値を操作する。
        麻痺値は0～40の範囲を越えない。
        """
        self.paralyze += value
        self.paralyze = cw.util.numwrap(self.paralyze, 0, 40)
        self.data.edit("/Property/Status/Paralyze", str(self.paralyze))

    def set_poison(self, value):
        """
        中毒値を操作する。
        中毒値は0～40の範囲を越えない。
        """
        self.poison += value
        self.poison = cw.util.numwrap(self.poison, 0, 40)
        self.data.edit("/Property/Status/Poison", str(self.poison))

    def set_mentality(self, name, value):
        """
        精神状態とその継続ラウンド数を操作する。
        継続ラウンド数の範囲は0～999を越えない。
        """
        self.mentality = name
        self.mentality_dur = value
        self.mentality_dur = cw.util.numwrap(self.mentality_dur, 0, 999)
        path = "/Property/Status/Mentality"
        self.data.edit(path, self.mentality)
        self.data.edit(path, str(self.mentality_dur), "duration")

    def set_bind(self, value):
        """
        束縛状態の継続ラウンド数を操作する。
        継続ラウンド数の範囲は0～999を越えない。
        """
        self.bind = value
        self.bind = cw.util.numwrap(self.bind, 0, 999)
        self.data.edit("/Property/Status/Bind", str(self.bind), "duration")

    def set_silence(self, value):
        """
        沈黙状態の継続ラウンド数を操作する。
        継続ラウンド数の範囲は0～999を越えない。
        """
        self.silence = value
        self.silence = cw.util.numwrap(self.silence, 0, 999)
        self.data.edit("/Property/Status/Silence", str(self.silence), "duration")

    def set_faceup(self, value):
        """
        暴露状態の継続ラウンド数を操作する。
        継続ラウンド数の範囲は0～999を越えない。
        """
        self.faceup = value
        self.faceup = cw.util.numwrap(self.faceup, 0, 999)
        self.data.edit("/Property/Status/FaceUp", str(self.faceup), "duration")

    def set_antimagic(self, value):
        """
        魔法無効状態の継続ラウンド数を操作する。
        継続ラウンド数の範囲は0～999を越えない。
        """
        self.antimagic = value
        self.antimagic = cw.util.numwrap(self.antimagic, 0, 999)
        self.data.edit("/Property/Status/AntiMagic", str(self.antimagic), "duration")

    def set_vanish(self):
        """
        対象消去を行う。
        """
        if not self.is_vanished():
            self._vanished = True
            cw.animation.animate_sprite(self, "delete")
            self.lost()

    def set_enhance_act(self, value, duration):
        """
        行動力強化値とその継続ラウンド数を操作する。
        強化値の範囲は-10～10、継続ラウンド数の範囲は0～999を越えない。
        """
        self.enhance_act = value
        self.enhance_act = cw.util.numwrap(self.enhance_act, -10, 10)
        self.enhance_act_dur = duration
        self.enhance_act_dur = cw.util.numwrap(self.enhance_act_dur, 0, 999)
        path = "/Property/Enhance/Action"
        self.data.edit(path, str(self.enhance_act))
        self.data.edit(path, str(self.enhance_act_dur), "duration")

    def set_enhance_avo(self, value, duration):
        """
        回避力強化値とその継続ラウンド数を操作する。
        強化値の範囲は-10～10、継続ラウンド数の範囲は0～999を越えない。
        """
        self.enhance_avo = value
        self.enhance_avo = cw.util.numwrap(self.enhance_avo, -10, 10)
        self.enhance_avo_dur = duration
        self.enhance_avo_dur = cw.util.numwrap(self.enhance_avo_dur, 0, 999)
        path = "/Property/Enhance/Avoid"
        self.data.edit(path, str(self.enhance_avo))
        self.data.edit(path, str(self.enhance_avo_dur), "duration")

    def set_enhance_res(self, value, duration):
        """
        抵抗力強化値とその継続ラウンド数を操作する。
        強化値の範囲は-10～10、継続ラウンド数の範囲は0～999を越えない。
        """
        self.enhance_res = value
        self.enhance_res = cw.util.numwrap(self.enhance_res, -10, 10)
        self.enhance_res_dur = duration
        self.enhance_res_dur = cw.util.numwrap(self.enhance_res_dur, 0, 999)
        path = "/Property/Enhance/Resist"
        self.data.edit(path, str(self.enhance_res))
        self.data.edit(path, str(self.enhance_res_dur), "duration")

    def set_enhance_def(self, value, duration):
        """
        抵抗力強化値とその継続ラウンド数を操作する。
        強化値の範囲は-10～10、継続ラウンド数の範囲は0～999を越えない。
        """
        self.enhance_def = value
        self.enhance_def = cw.util.numwrap(self.enhance_def, -10, 10)
        self.enhance_def_dur = duration
        self.enhance_def_dur = cw.util.numwrap(self.enhance_def_dur, 0, 999)
        path = "/Property/Enhance/Defense"
        self.data.edit(path, str(self.enhance_def))
        self.data.edit(path, str(self.enhance_def_dur), "duration")

    def set_skillpower(self, recovery=True):
        """
        精神力(スキルの使用回数)を操作する。
        recoveryがTrueだったら、最大値まで回復。
        Falseだったら、0にする。
        """
        for header in self.cardpocket[0]:
            if recovery:
                header.set_uselimit(999)
            else:
                header.set_uselimit(0)

    def set_beast(self, element=None, vanish=False):
        """召喚獣を召喚する。付帯召喚設定は強制的にクリアされる。
        vanish: 召喚獣を消去するかどうか。
        """
        idx = cw.POCKET_BEAST

        if vanish:
            for header in self.cardpocket[idx][::-1]:
                if not header.attachment:
                    self.throwaway_card(header)

        elif len(self.cardpocket[idx]) < self.get_cardpocketspace()[idx]:
            etree = cw.data.xml2etree(element=element)
            content = cw.content.GetContent(None)
            content.get_card(etree, self, True)

    def set_timeelapse(self, time=1):
        """時間経過。"""
        # 時限クーポン処理
        self.count_timedcoupon()
        flag = False

        # 中毒
        if self.is_poison():
            self.set_poison(-time)

            if not self.is_poison():
                flag = True
            else:
                cw.cwpy.sounds[u"システム・破棄"].play()
                value = 1 * self.poison
                n = value / 5
                n2 = value % 5 * 2
                value = cw.cwpy.dice.roll(n, 10)

                if n2:
                    value += cw.cwpy.dice.roll(1, n2)

                self.set_life(-value)

                if self.is_unconscious():
                    self.set_paralyze(-40)
                    self.set_poison(-40)
                    self.set_mentality("Normal", 0)
                    self.set_bind(0)
                    self.set_silence(0)
                    self.set_faceup(0)
                    self.set_antimagic(0)
                    self.set_enhance_act(0, 0)
                    self.set_enhance_avo(0, 0)
                    self.set_enhance_res(0, 0)
                    self.set_enhance_def(0, 0)
                    self.set_beast(vanish=True)

                cw.animation.animate_sprite(self, "lateralvibe")
                self.update_image()

        # 麻痺
        if self.is_paralyze() and not self.is_petrified():
            self.set_paralyze(-time)
            flag |= not self.is_paralyze()

        # 束縛
        if self.is_bind():
            value = self.bind - time
            self.set_bind(value)
            flag |= not self.is_bind()

        # 沈黙
        if self.is_silence():
            value = self.silence - time
            self.set_silence(value)
            flag |= not self.is_silence()

        # 暴露
        if self.is_faceup():
            value = self.faceup - time
            self.set_faceup(value)
            flag |= not self.is_faceup()

        # 魔法無効化
        if self.is_antimagic():
            value = self.antimagic - time
            self.set_antimagic(value)
            flag |= not self.is_antimagic()

        # 精神状態
        if self.mentality_dur > 0:
            value = self.mentality_dur - time

            if value > 0:
                self.set_mentality(self.mentality, value)
            else:
                self.set_mentality("Normal", 0)
                flag = True

        # 行動力
        if self.enhance_act_dur > 0:
            value = self.enhance_act_dur - time

            if value > 0:
                self.set_enhance_act(self.enhance_act, value)
            else:
                self.set_enhance_act(0, 0)
                flag = True

        # 回避力
        if self.enhance_avo_dur > 0:
            value = self.enhance_avo_dur - time

            if value > 0:
                self.set_enhance_avo(self.enhance_avo, value)
            else:
                self.set_enhance_avo(0, 0)
                flag = True

        # 抵抗力
        if self.enhance_res_dur > 0:
            value = self.enhance_res_dur - time

            if value > 0:
                self.set_enhance_res(self.enhance_res, value)
            else:
                self.set_enhance_res(0, 0)
                flag = True

        # 防御力
        if self.enhance_def_dur > 0:
            value = self.enhance_def_dur - time

            if value > 0:
                self.set_enhance_def(self.enhance_def, value)
            else:
                self.set_enhance_def(0, 0)
                flag = True

        # 中毒効果で死亡していたら、ステータスを元に戻す
        if self.is_dead():
            self.set_normalstatus()

        # 敵が中毒効果で死亡していたら、死亡イベント開始
        if isinstance(self, Enemy) and self.is_dead():
            self.events.start(1)

        # 画像更新
        if flag:
            cw.animation.animate_sprite(self, "hide")
            self.update_image()
            cw.animation.animate_sprite(self, "deal")

class Player(Character):
    def lost(self):
        if cw.cwpy.is_playingscenario():
            self.data.edit("Property", "True", "lost")
            self.data.write_xml()
            cw.cwpy.sdata.lostadventurers.add(self.data.fpath)

class Enemy(Character):
    pass

class Friend(Character):
    pass

class AlbumPage(object):
    def __init__(self, data):
        self.data = data
        self.name = self.data.gettext("/Property/Name", "")
        self.level = self.data.getint("/Property/Level")

def main():
    pass

if __name__ == "__main__":
    main()

