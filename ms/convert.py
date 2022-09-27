import json
import datetime
import math
import urllib.parse

class AttributeDict(object):
    def __init__(self, obj):
        self.obj = obj

    def __getstate__(self):
        return self.obj.items()

    def __setstate__(self, items):
        if not hasattr(self, 'obj'):
            self.obj = {}
        for key, val in items:
            self.obj[key] = val

    def __getattr__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    def fields(self):
        return self.obj

    def keys(self):
        return self.obj.keys()
    
    def get(self, key):
        return self.obj.get(str(key))

# variables you might actually want to change
NAMEPREF   = 1;     # 2 for english, 1 for sane amount of weeb, 0 for japanese
VERBOSELOG = False; # dump mjs records to output - will make the file too large for tenhou.net/5 viewer
SHOWFU     = False; # always show fu/han for scoring - even for limit hands

# words that can end up in log, some are mandatory kanji in places
JPNAME = 0
RONAME = 1
ENNAME = 2
RUNES  = {
    # hand limits
    "mangan"         : ["満貫",         "Mangan ",         "Mangan "               ],
    "haneman"        : ["跳満",         "Haneman ",        "Haneman "              ],
    "baiman"         : ["倍満",         "Baiman ",         "Baiman "               ],
    "sanbaiman"      : ["三倍満",       "Sanbaiman ",      "Sanbaiman "            ],
    "yakuman"        : ["役満",         "Yakuman ",        "Yakuman "              ],
    "kazoeyakuman"   : ["数え役満",     "Kazoe Yakuman ",  "Counted Yakuman "      ],
    "kiriagemangan"  : ["切り上げ満貫", "Kiriage Mangan ", "Rounded Mangan "       ],
    # round enders
    "agari"          : ["和了",         "Agari",           "Agari"                 ],
    "ryuukyoku"      : ["流局",         "Ryuukyoku",       "Exhaustive Draw"       ],
    "nagashimangan"  : ["流し満貫",     "Nagashi Mangan",  "Mangan at Draw"        ],
    "suukaikan"      : ["四開槓",       "Suukaikan",       "Four Kan Abortion"     ],
    "sanchahou"      : ["三家和",       "Sanchahou",       "Three Ron Abortion"    ],
    "kyuushukyuuhai" : ["九種九牌",     "Kyuushu Kyuuhai", "Nine Terminal Abortion"],
    "suufonrenda"    : ["四風連打",     "Suufon Renda",    "Four Wind Abortion"    ],
    "suuchariichi"   : ["四家立直",     "Suucha Riichi",   "Four Riichi Abortion"  ],
    # scoring
    "fu"             : ["符",           "符",              "Fu"                    ],
    "han"            : ["飜",           "飜",              "Han"                   ],
    "points"         : ["点",           "点",              "Points"                ],
    "all"            : ["∀",           "∀",              "∀"                    ],
    "pao"            : ["包",           "pao",             "Responsibility"        ],
    # rooms
    "tonpuu"         : ["東喰",         " East",           " East"                 ],
    "hanchan"        : ["南喰",         " South",          " South"                ],
    "friendly"       : ["友人戦",       "Friendly",        "Friendly"              ],
    "tournament"     : ["大会戦",       "Tounament",       "Tournament"            ],
    "sanma"          : ["三",           "3-Player ",       "3-Player "             ],
    "red"            : ["赤",           " Red",            " Red Fives"            ],
    "nored"          : ["",             " Aka Nashi",      " No Red Fives"         ]
}
RUNES  = AttributeDict(RUNES)

# senkinin barai yaku - please don't change, yostar..
DAISANGEN = 37  # daisangen cfg.fan.fan.map_ index
DAISUUSHI = 50
TSUMOGIRI = 60 # tenhou tsumogiri symbol

# global variables - don't touch
ALLOW_KIRIAGE = False # potentially allow this to be true
TSUMOLOSSOFF  = False # sanma tsumo loss, is set true for sanma when tsumo loss off

json_open = open('ms/data.json', 'r', encoding="utf-8_sig")
cfg = json.load(json_open, object_hook=AttributeDict)

# round information, to be reset every RecordNewRound
class Kyoku():
    # init kyoku
    def init(self, leaf):
        self.nplayers    = len(leaf.scores)
        self.round       = [4 * leaf.chang + leaf.ju, leaf.ben, leaf.liqibang]
        self.initscores  = Kyoku.pad_right(leaf.scores, 4, 0)
        self.doras       = [Kyoku.tm2t(leaf.dora)] if leaf.dora else [Kyoku.tm2t(e) for e in leaf.doras]
        self.draws       = [[],[],[],[]]
        self.discards    = [[],[],[],[]]
        self.haipais     = [[Kyoku.tm2t(f) for f in leaf.get("tiles{}".format(i))] for i,_ in enumerate(self.draws)]

        # treat the last tile in the dealer's hand as a drawn tile
        self.poppedtile  = self.haipais[leaf.ju].pop()
        self.draws[leaf.ju].append(self.poppedtile)
        # information we need, but can't expect in every record
        self.dealerseat  = leaf.ju
        self.ldseat      = -1 # who dealt the last tile
        self.nriichi     = 0 # number of current riichis - needed for scores, abort workaround
        self.priichi     = False
        self.nkan        = 0 # number of current kans - only for abort workaround
        # pao rule
        self.nowinds     = [0]*4 # counter for each players open wind pons/kans
        self.nodrags     = [0]*4
        self.paowind     = -1 # seat of who dealt the final wind, -1 if no one is responsible
        self.paodrag     = -1

    # senkinin barai incrementer - to be called every pon, daiminkan, ankan
    def countpao(self, tile, owner, feeder):
        # owner and feeder are seats, tile should be tenhou
        if tile in WINDS:
            
            self.nowinds[owner] += 1
            if 4 == self.nowinds[owner]:
                self.paowind = feeder
    
        elif tile in DRAGS:
    
            self.nodrags[owner] += 1
            if 3 == self.nodrags[owner]:
                self.paodrag = feeder

    # dump round informaion
    def dump(self, uras):
        # NOTE: doras,uras are the indicators
        entry = []
        entry.append(self.round)
        entry.append(self.initscores)
        entry.append(self.doras)
        entry.append(uras)
        for i,f in enumerate(self.haipais):
            entry.append(f)
            entry.append(self.draws[i])
            entry.append(self.discards[i])
        return entry

    # parse mjs hule into tenhou agari list
    def parsehule(self, h):
        # tenhou log viewer requires 点, 飜) or 役満) to end strings, rest of scoring string is entirely optional
        # who won, points from (self if tsumo), who won or if pao: who's responsible
        res    = [h.seat, h.seat if h.zimo else self.ldseat, h.seat]
        delta  = [] # we need to compute the delta ourselves to handle double/triple ron
        points = 0
        rp     = 1000 * (self.nriichi + self.round[2]) if (-1 != self.nriichi) else 0 # riichi stick points, -1 means already taken
        hb     = 100 * self.round[1] # base honba payment

        # sekinin barai logic
        pao         = False
        liableseat  = -1
        liablefor   = 0

        if h.yiman:
            # only worth checking yakuman hands
            for e in h.fans:
                if DAISUUSHI == e.id and (-1 != self.paowind):
                    # daisuushi pao
                    pao        = True
                    liableseat = self.paowind
                    liablefor += e.val # realistically can only be liable once
                
                elif DAISANGEN == e.id and (-1 != self.paodrag):
                    pao        = True
                    liableseat = self.paodrag
                    liablefor += e.val

        if h.zimo:
            # ko-oya payment for non-dealer tsumo
            delta =  [-hb - h.point_zimo_xian - Kyoku.tlround((1/2) * (h.point_zimo_xian))] * self.nplayers
            if h.seat == self.dealerseat: # oya tsumo
                delta[h.seat] = rp + (self.nplayers - 1) * (hb + h.point_zimo_xian) + 2 * Kyoku.tlround((1/2) * (h.point_zimo_xian))
                points = str(h.point_zimo_xian + Kyoku.tlround((1/2) * (h.point_zimo_xian)))
            
            else:  # ko tsumo    
                delta[h.seat]       = rp + hb + h.point_zimo_qin + (self.nplayers - 2) * (hb + h.point_zimo_xian) + 2 * Kyoku.tlround((1/2) * (h.point_zimo_xian))
                delta[self.dealerseat] = -hb - h.point_zimo_qin - Kyoku.tlround((1/2) * (h.point_zimo_xian))
                points = str(h.point_zimo_xian) + "-" + str(h.point_zimo_qin)
            
        else:
            # ron
            delta = [0]*self.nplayers
            delta[h.seat]      = rp + (self.nplayers - 1) * hb + h.point_rong
            delta[self.ldseat] = -(self.nplayers - 1) * hb - h.point_rong
            points = str(h.point_rong)
            self.nriichi = -1; # mark the sticks as taken, in case of double ron
        
        # sekinin barai payments
        # treat pao as the liable player paying back the other players - safe for multiple yakuman
        OYA    = 0
        KO     = 1
        RON    = 2
        YSCORE = [ #yakuman scoring table
            # oya,    ko,   ron  pays
            [0,    16000, 48000], # oya wins
            [16000, 8000, 32000]  # ko  wins
        ]

        if pao:
            res[2] = liableseat # this is how tenhou does it - doesn't really seem to matter to akochan or tenhou.net/5

            if h.zimo: # liable player needs to payback n yakuman tsumo payments
                
                if h.qinjia: # dealer tsumo
                    # should treat tsumo loss as ron, luckily all yakuman values round safely for north bisection
                    delta[liableseat] -= 2 * hb + liablefor * 2 * YSCORE[OYA][KO] + Kyoku.tlround((1/2) * liablefor *  YSCORE[OYA][KO]) # 1? only paying back other ko
                    for i,e in enumerate(delta):
                        if liableseat != i and h.seat != i and self.nplayers >= i:
                            delta[i] += hb + liablefor * YSCORE[OYA][KO] + Kyoku.tlround((1/2) * liablefor * (YSCORE[OYA][KO]))
                    
                    if 3 == self.nplayers: # dealer should get north's payment from liable
                        delta[h.seat] += 0 if TSUMOLOSSOFF else liablefor * YSCORE[OYA][KO]
                
                else:  # non-dealer tsumo
                
                    delta[liableseat] -= (self.nplayers - 2) * hb + liablefor * (YSCORE[KO][OYA] + YSCORE[KO][KO]) + Kyoku.tlround((1/2) * liablefor *  YSCORE[KO][KO]) #^^same 1st, but ko
                    for i,e in enumerate(delta):
                    
                        if liableseat != i and h.seat != i and  self.nplayers >= i:
                        
                            if self.dealerseat == i:
                                delta[i] += hb + liablefor * YSCORE[KO][OYA] + Kyoku.tlround((1/2) * liablefor *  YSCORE[KO][KO]) # ^^same 1st ...
                            else:
                                delta[i] += hb + liablefor * YSCORE[KO][KO] + Kyoku.tlround((1/2) * liablefor *  YSCORE[KO][KO]) # ^^same 1st ...

            else:      # ron
                # liable seat pays the deal-in seat 1/2 yakuman + full honba
                delta[liableseat]  -= (self.nplayers - 1) * hb + (1/2) * liablefor * YSCORE[OYA if h.qinjia else KO][RON]
                delta[self.ldseat] += (self.nplayers - 1) * hb + (1/2) * liablefor * YSCORE[OYA if h.qinjia else KO][RON]
        
        # append point symbol
        points = str(points) + RUNES.points[JPNAME] + (RUNES.all[NAMEPREF] if h.zimo and h.qinjia else "")

        # score string
        fuhan = str(h.fu) + RUNES.fu[NAMEPREF] + str(h.count) + RUNES.han[NAMEPREF]
        if h.yiman:                                                                                # yakuman
            res.append((fuhan if SHOWFU else "") + RUNES.yakuman[NAMEPREF] + points)
        elif (13 <= h.count):                                                                      # kazoe
            res.append((fuhan if SHOWFU else "") + RUNES.kazoeyakuman[NAMEPREF] + points)
        elif (11 <= h.count):                                                                      # sanbaiman
            res.append((fuhan if SHOWFU else "") + RUNES.sanbaiman[NAMEPREF] + points)
        elif (8 <= h.count):                                                                       # baiman
            res.append((fuhan if SHOWFU else "") + RUNES.baiman[NAMEPREF] + points)
        elif (6 <= h.count):                                                                       # haneman
            res.append((fuhan if SHOWFU else "") + RUNES.haneman[NAMEPREF] + points)
        elif (5 <= h.count or (4 <= h.count and 40 <= h.fu) or (3 <= h.count and 70 <= h.fu)):     # mangan
            res.append((fuhan if SHOWFU else "") + RUNES.mangan[NAMEPREF] + points)
        elif (ALLOW_KIRIAGE and ((4 == h.count and 30 == h.fu) or (3 == h.count and 60 == h.fu))): # kiriage
            res.append((fuhan if SHOWFU else "") + RUNES.kiriagemangan[NAMEPREF] + points)
        else:                                                                                      # ordinary hand
            res.append(fuhan + points)

        for e in h.fans:
            res.append( 
                (cfg.fan.fan.map_.get(e.id).name_jp if JPNAME == NAMEPREF else cfg.fan.fan.map_.get(e.id).name_en) 
                + "(" + ((RUNES.yakuman[JPNAME]) if h.yiman else (str(e.val) + RUNES.han[JPNAME]) )+ ")"
            )


        return [Kyoku.pad_right(delta, 4, 0), res]

    # pad a to length l with f, needed to pad log for >sanma
    @classmethod
    def pad_right(cls, a, l, f):
        return a + [f] * (l - len(a))

    # take '2m' and return 2 + 10 etc.
    @classmethod
    def tm2t(cls, str):
        # tenhou's tile encoding:
        #   11-19    - 1-9 man
        #   21-29    - 1-9 pin
        #   31-39    - 1-9 sou
        #   41-47    - ESWN WGR
        #   51,52,53 - aka 5 man, pin, sou
        num = int(str[0])
        tcon = { 'm' : 1, 'p' : 2, 's' : 3, 'z' : 4 }

        return 10 * tcon[str[1]] + num if num else 50 + tcon[str[1]]
    
    # seat1 is seat0's x
    @classmethod
    def relativeseating(cls, seat0, seat1):
        # return 0: kamicha, 1: toimen, 2: if shimocha
        return (seat0 - seat1 + 4 - 1) % 4

    # return normal tile from aka, tenhou rep(ex 51 to 15)
    @classmethod
    def deaka(cls, til):
        # alternativly - use strings
        if 5 == math.floor(til/10):
            return 10*(til%10) + math.floor(til/10)
        return til

    # return aka version of tile(ex 15 to 51)
    @classmethod
    def makeaka(cls, til):
        if 5 == (til%10): # is a five (or haku)
            return 10*(til%10) + math.floor(til/10)
        return til # can't be/already is aka

    # round up to nearest hundred iff TSUMOLOSSOFF == true otherwise return 0
    @classmethod
    def tlround(cls, x):
        return 100*math.ceil(x/100) if TSUMOLOSSOFF else 0

# sekinin barai tiles
WINDS = [Kyoku.tm2t(e) for e in ["1z", "2z", "3z", "4z"]]
DRAGS = [Kyoku.tm2t(e) for e in ["5z", "6z", "7z", "0z"]] # 0z would be aka haku


def generatelog(mjslog):
    log = []
    kyoku = Kyoku()

    for e in mjslog:
        data = e.data
        match e.name:
            
            case ".lq.RecordNewRound":
                # new round
                kyoku.init(data)
            
            case ".lq.RecordDiscardTile":
                # discard - marking tsumogiri and riichi
                symbol = TSUMOGIRI if data.moqie else Kyoku.tm2t(data.tile)

                # we pretend that the dealer's initial 14th tile is drawn - so we need to manually check the first discard
                if data.seat == kyoku.dealerseat and not len(kyoku.discards[data.seat]) and symbol == kyoku.poppedtile:
                    symbol = TSUMOGIRI

                if data.is_liqi: # riichi delcaration
                    kyoku.priichi = True
                    symbol = "r" + str(symbol)
                
                kyoku.discards[data.seat].append(symbol)
                kyoku.ldseat = data.seat # for ron, pon etc.

                # sometimes we get dora passed here
                if data.doras and len(data.doras) > len(kyoku.doras):
                    kyoku.doras = [Kyoku.tm2t(f) for f in data.doras]
            
            case ".lq.RecordDealTile":
               # draw - after kan this gets passed the new dora
                if kyoku.priichi:
                    kyoku.priichi = False
                    kyoku.nriichi += 1

                if data.doras and len(data.doras) > len(kyoku.doras):
                    kyoku.doras = [Kyoku.tm2t(f) for f in data.doras]

                kyoku.draws[data.seat].append(Kyoku.tm2t(data.tile))

            case ".lq.RecordChiPengGang":
                # call - chi, pon, daiminkan
                if kyoku.priichi:
                    kyoku.priichi = False
                    kyoku.nriichi += 1
                
                match data.type:

                    case 0:
                        # chii
                        kyoku.draws[data.seat].append(
                            "c{}{}{}".format(
                                Kyoku.tm2t(data.tiles[2]),
                                Kyoku.tm2t(data.tiles[0]),
                                Kyoku.tm2t(data.tiles[1])
                            )
                        )

                    case 1:
                        # pon
                        worktiles = [Kyoku.tm2t(f) for f in data.tiles]
                        idx = Kyoku.relativeseating(data.seat, kyoku.ldseat)
                        kyoku.countpao(worktiles[0], data.seat, kyoku.ldseat)
                        # pop the called tile a preprend 'p'
                        worktiles[idx] = f"p{worktiles[idx]}"
                        kyoku.draws[data.seat].append("".join(map(str,worktiles)))

                    case 2:
                        """
                        ///////////////////////////////////////////////////
                        // kan naki:
                        //   daiminkan:
                        //     kamicha   "m39393939" (0)
                        //     toimen    "39m393939" (1)
                        //     shimocha  "222222m22" (3)
                        //     (writes to draws; 0 to discards)
                        //   shouminkan: (same order as pon; immediate tile after k is the added tile)
                        //     kamicha   "k37373737" (0)
                        //     toimen    "31k313131" (1)
                        //     shimocha  "3737k3737" (2)
                        //     (writes to discards)
                        //   ankan:
                        //     "121212a12" (3)
                        //     (writes to discards)
                        ///////////////////////////////////////////////////
                        """
                        # daiminkan
                        calltiles = [Kyoku.tm2t(f) for f in data.tiles]
                        # < kamicha 0 | toimen 1 | shimocha 3 >
                        idx = Kyoku.relativeseating(data.seat, kyoku.ldseat)
                        idxm = 3 if 2 == idx else idx

                        kyoku.countpao(calltiles[0], data.seat, kyoku.ldseat)
                        calltiles[idxm] = f"m{calltiles[idxm]}"
                        kyoku.draws[data.seat].append("".join(map(str, calltiles)))
                        # tenhou drops a 0 in discards for this
                        kyoku.discards[data.seat].append(0)
                        # register kan
                        kyoku.nkan += 1

                    case _:
                        print(
                            "didn't know what to do with " +
                            e.name + "(" + data.type + ")"
                        )

            case ".lq.RecordAnGangAddGang":
                # kan - shouminkan 'k', ankan 'a'
                # NOTE: e.tiles here is a single tile; naki is placed in discards
                til =  Kyoku.tm2t(data.tiles)
                kyoku.ldseat = data.seat # for chankan, no conflict as last discard has passed
                match data.type:

                    case 3:
                        # //ankan
                        # ////////////////////
                        # // mjs chun ankan example record:
                        # //{"seat":0,"type":3,"tiles":"7z"}
                        # ////////////////////
                        
                        kyoku.countpao(til, data.seat, -1) # count the group as visible, but don't set pao
                        # get the tiles from haipai and draws that
                        # are involved in ankan, dumb
                        # because n aka might be involved
                        ankantiles = \
                            list(filter(lambda t: Kyoku.deaka(t)==Kyoku.deaka(til), kyoku.haipais[data.seat])) + \
                            list(filter(lambda t: Kyoku.deaka(t)==Kyoku.deaka(til), kyoku.draws[data.seat]))

                        til = ankantiles.pop()  #doesn't really matter which tile we mark ankan with - chosing last drawn
                        kyoku.discards[data.seat].append("".join(map(str, ankantiles)) + "a" + str(til))  # push naki
                        kyoku.nkan += 1

                    case 2:
                        # shouminkan
                        # get pon naki from .draws and swap in new symbol
                        
                        def has_kantile(w):
                            if type(w) == str: # naki
                                return "p"+str(Kyoku.deaka(til)) in w or "p"+str(Kyoku.makeaka(til)) in w  # pon involves same tile type
                            return False

                        nakis = list(filter(has_kantile, kyoku.draws[data.seat]))

                        kyoku.discards[data.seat].append(nakis[0].replace("p", "k"+str(til))) # push naki
                        kyoku.nkan += 1

                    case _:
                        print("didn't know what to do with "
                            + e.name + " type: " + data.type)

            case ".lq.RecordBaBei":
                # kita - this record (only) gives {seat, moqie}
                # NOTE: tenhou doesn't mark its kita based on when they were drawn, so we won't
                # if (e.moqie)
                #     kyoku.discards[e.seat].push("f" + TSUMOGIRI);
                # else
                kyoku.discards[data.seat].append("f44")
                
            # /////////////////////////////////////////////////////
            # // round enders:
            # // "RecordNoTile" - ryuukyoku
            # // "RecordHule"   - agari - ron/tsumo
            # // "RecordLiuJu"  - abortion
            # //////////////////////////////////////////////////////
            case ".lq.RecordLiuJu":
                # abortion
                if kyoku.priichi: 
                    kyoku.priichi = False
                    kyoku.nriichi += 1
                

                entry = kyoku.dump([])

                if 1 == data.type:
                    entry.append([RUNES.kyuushukyuuhai[NAMEPREF]]) # kyuushukyuhai
                elif 2 == data.type:
                    entry.append([RUNES.suufonrenda[NAMEPREF]])    # suufon renda
                elif 4 == kyoku.nriichi:                           # TODO: actually get the type code
                    entry.append([RUNES.suuchariichi[NAMEPREF]])   # 4 riichi
                elif 4 <= kyoku.nkan:                              # TODO: actually get type code
                    entry.append([RUNES.suukaikan[NAMEPREF]])      # 4 kan, potentially false positive on 3 ron with 4 kans
                else:
                    entry.append([RUNES.sanchahou[NAMEPREF]])      # 3 ron - can't actually get this in mjs

                log.append(entry)
            
            case ".lq.RecordNoTile":
                # ryuukyoku
                entry = kyoku.dump([])
                delta = [0]*4

                # NOTE: mjs wll not give delta_scores if everyone is (no)ten - TODO: minimize the autism
                if data.scores and data.scores[0] and data.scores[0].delta_scores and len(data.scores[0].delta_scores):
                    # for the rare case of multiple nagashi, we sum the arrays
                    for f in data.scores:
                        for i,g in enumerate(f.delta_scores):
                            delta[i] += g

                if data.liujumanguan: # nagashi mangan
                    entry.append([RUNES.nagashimangan[NAMEPREF], delta])
                else:              # normal ryuukyoku
                    entry.append([RUNES.ryuukyoku[NAMEPREF], delta])
                log.append(entry)

            case ".lq.RecordHule":
                # agari
                agari = []
                ura = []
                for f in data.hules:
                    if len(ura) < (len(f.li_doras) if f.li_doras else 0):
                        ura = [Kyoku.tm2t(g) for g in f.li_doras]
                    agari.append(kyoku.parsehule(f))
  
                entry = kyoku.dump(ura)

                entry.append( [RUNES.agari[JPNAME]] + sum(agari,[]) ) # needs the japanese agari
                log.append(entry)

            case _:
                print("didn't know what to do with " + e.name)
    return log


def parse(record):
    res = {}
    ruledisp   = ""
    lobby      = ""
    nplayers   = len(record.head.result.players)
    nakas      = nplayers - 1
    mjslog = \
        [action.result for action in record.data.data.actions if action.type==1] \
        if record.data.data.version == 210715 else \
        record.data.data.records
        

    res["ver"]     = "2.3"
    res["ref"]     = record.head.uuid
    res["log"]     = generatelog(mjslog)
    res["ratingc"] = "PF{}".format(nplayers)

    # rule display
    if 3 == nplayers and JPNAME == NAMEPREF:
        ruledisp += RUNES.sanma[JPNAME]

    if record.head.config.meta.mode_id: # ranked or casual
        ruledisp += \
            cfg.desktop.matchmode.map_.get(record.head.config.meta.mode_id).room_name_jp \
            if (JPNAME == NAMEPREF) else \
            cfg.desktop.matchmode.map_.get(record.head.config.meta.mode_id).room_name_en
    elif record.head.config.meta.room_id: # friendly
        lobby    = ": " + str(record.head.config.meta.room_id) # can set room number as lobby number
        ruledisp += RUNES.friendly[NAMEPREF]  # "Friendly"
        nakas    = record.head.config.mode.detail_rule.dora_count
        TSUMOLOSSOFF = not record.head.config.mode.detail_rule.have_zimosun if (3 == nplayers) else False
    elif record.head.config.meta.contest_uid: # tourney
        lobby    = ": " + str(record.head.config.meta.contest_uid)
        ruledisp += RUNES.tournament[NAMEPREF] # "Tournament"
        nakas    = record.head.config.mode.detail_rule.dora_count
        TSUMOLOSSOFF = not record.head.config.mode.detail_rule.have_zimosun if (3 == nplayers) else False

    if 1 == record.head.config.mode.mode:
        ruledisp += RUNES.tonpuu[NAMEPREF] # " East"
    elif 2 == record.head.config.mode.mode:
        ruledisp += RUNES.hanchan[NAMEPREF] # " South"
    
    if not record.head.config.meta.mode_id and not record.head.config.mode.detail_rule.dora_count:
        if JPNAME != NAMEPREF:
            ruledisp += RUNES.nored[NAMEPREF]
        res["rule"] = {"disp" : ruledisp, "aka53" : 0, "aka52" : 0, "aka51": 0}
    else:
        if JPNAME == NAMEPREF:
            ruledisp += RUNES.red[JPNAME]
        res["rule"] = {"disp" : ruledisp, "aka53" : 1, "aka52" : 2 if 4 == nakas else 1, "aka51": 1 if 4 == nplayers else 0}
    
    res["lobby"] = 0 # tenhou custom lobby - could be tourney id or friendly room for mjs. appending to title instead to avoid 3->C etc. in tenhou.net/5

    # rank, rate, name, sex
    res["dan"] = [""]*4
    res["rate"] = [""]*4
    res["sx"]   = ['C']*4
    res["name"] = ['AI']*4
    for e in record.head.accounts:
        res["dan"][e.seat] = \
            cfg.level_definition.level_definition.map_.get(e.level.id).full_name_jp \
            if JPNAME == NAMEPREF \
            else cfg.level_definition.level_definition.map_.get(e.level.id).full_name_en

        # sex = cfg.item_definition.character.map_.get(e.character.charid).sex
        # res["sx"][e.seat]   = "F" if 1 == sex else "M" if 2 == sex else "C"
        res["rate"][e.seat] = e.level.score
        res["name"][e.seat] = e.nickname

    # clean up for sanma AI
    if 3 == nplayers:
        res["name"][3] = ""
        res["sx"][3]   = ""

    # scores
    res["sc"] = [""]*8
    scores = [[e.seat, e.part_point_1, e.total_point/1000] for e in record.head.result.players]
    for score in scores:
        res["sc"][2*score[0]]   = score[1]
        res["sc"][2*score[0]+1] = score[2]

    # optional title - why not give the room and put the timestamp here; 1000 for unix to .js timestamp convention
    dt = datetime.datetime.fromtimestamp(record.head.end_time).strftime('%Y/%m/%d %H:%M:%S')
    res["title"] = [ruledisp+lobby, dt]

    # optionally dump mjs records NOTE: this will likely make the file too large for tenhou.net/5 viewer
    if VERBOSELOG:
        res["mjshead"]        = record.head
        res["mjslog"]         = mjslog
        #res["mjsrecordtypes"] = [e.name for e in mjslog]


    return res


def convert(paifu):
    paifu = json.loads(json.dumps(paifu), object_hook=AttributeDict)
    paifu = parse(paifu)
    return paifu
