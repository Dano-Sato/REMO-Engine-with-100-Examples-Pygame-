import typing,pygame


#colorSheet
class Cs():
    '''
    Colors의 약자. 색상을 나타내는 클래스\n
    각종 색상의 RGB값 혹은 hexColor를 rgb 튜플로 만들어준다.\n
    '''
    white=(255, 255, 255)
    grey=(128,128,128)
    grey75=(192,192,192)
    grey25=(64,64,64)
    black=(0,0,0)
    red=(255,0,0)
    green=(0,255,0)
    blue=(0,0,255)
    yellow=(255,255,0)
    cyan = (0,255,255)
    orange=(255,165,0)
    purple=(160,32,240)
    pink=(255,192,203)
    beige = (245,245,220)
    brown_old = (150, 75, 0)
    aquamarine = (127,255,212)
    salmon = (250,128,114)
    ebony = (85,93,80)
    cognac = (154, 70, 61)
    mint = (62, 180, 137)
    lint = (186, 204, 129)
    tiffanyBlue = (10, 186, 181)
    dustyRose = (220, 174, 150)
    burgundy = (128, 0, 32)

    # CSS 140개 색상 표준 추가
    aliceblue = (240, 248, 255)
    antiquewhite = (250, 235, 215)
    aqua = (0, 255, 255)
    aquamarine = (127, 255, 212)
    azure = (240, 255, 255)
    beige = (245, 245, 220)
    bisque = (255, 228, 196)
    black = (0, 0, 0)
    blanchedalmond = (255, 235, 205)
    blue = (0, 0, 255)
    blueviolet = (138, 43, 226)
    brown = (165, 42, 42)
    burlywood = (222, 184, 135)
    cadetblue = (95, 158, 160)
    chartreuse = (127, 255, 0)
    chocolate = (210, 105, 30)
    coral = (255, 127, 80)
    cornflowerblue = (100, 149, 237)
    cornsilk = (255, 248, 220)
    crimson = (220, 20, 60)
    cyan = (0, 255, 255)
    darkblue = (0, 0, 139)
    darkcyan = (0, 139, 139)
    darkgoldenrod = (184, 134, 11)
    darkgray = (169, 169, 169)
    darkgreen = (0, 100, 0)
    darkkhaki = (189, 183, 107)
    darkmagenta = (139, 0, 139)
    darkolivegreen = (85, 107, 47)
    darkorange = (255, 140, 0)
    darkorchid = (153, 50, 204)
    darkred = (139, 0, 0)
    darksalmon = (233, 150, 122)
    darkseagreen = (143, 188, 143)
    darkslateblue = (72, 61, 139)
    darkslategray = (47, 79, 79)
    darkturquoise = (0, 206, 209)
    darkviolet = (148, 0, 211)
    deeppink = (255, 20, 147)
    deepskyblue = (0, 191, 255)
    dimgray = (105, 105, 105)
    dodgerblue = (30, 144, 255)
    firebrick = (178, 34, 34)
    floralwhite = (255, 250, 240)
    forestgreen = (34, 139, 34)
    fuchsia = (255, 0, 255)
    gainsboro = (220, 220, 220)
    ghostwhite = (248, 248, 255)
    gold = (255, 215, 0)
    goldenrod = (218, 165, 32)
    gray = (128, 128, 128)
    green = (0, 128, 0)
    greenyellow = (173, 255, 47)
    honeydew = (240, 255, 240)
    hotpink = (255, 105, 180)
    indianred = (205, 92, 92)
    indigo = (75, 0, 130)
    ivory = (255, 255, 240)
    khaki = (240, 230, 140)
    lavender = (230, 230, 250)
    lavenderblush = (255, 240, 245)
    lawngreen = (124, 252, 0)
    lemonchiffon = (255, 250, 205)
    lightblue = (173, 216, 230)
    lightcoral = (240, 128, 128)
    lightcyan = (224, 255, 255)
    lightgoldenrodyellow = (250, 250, 210)
    lightgreen = (144, 238, 144)
    lightgrey = (211, 211, 211)
    lightpink = (255, 182, 193)
    lightsalmon = (255, 160, 122)
    lightseagreen = (32, 178, 170)
    lightskyblue = (135, 206, 250)
    lightslategray = (119, 136, 153)
    lightsteelblue = (176, 196, 222)
    lightyellow = (255, 255, 224)
    lime = (0, 255, 0)
    limegreen = (50, 205, 50)
    linen = (250, 240, 230)
    magenta = (255, 0, 255)
    maroon = (128, 0, 0)
    mediumaquamarine = (102, 205, 170)
    mediumblue = (0, 0, 205)
    mediumorchid = (186, 85, 211)
    mediumpurple = (147, 112, 219)
    mediumseagreen = (60, 179, 113)
    mediumslateblue = (123, 104, 238)
    mediumspringgreen = (0, 250, 154)
    mediumturquoise = (72, 209, 204)
    mediumvioletred = (199, 21, 133)
    midnightblue = (25, 25, 112)
    mintcream = (245, 255, 250)
    mistyrose = (255, 228, 225)
    moccasin = (255, 228, 181)
    navajowhite = (255, 222, 173)
    navy = (0, 0, 128)
    oldlace = (253, 245, 230)
    olive = (128, 128, 0)
    olivedrab = (107, 142, 35)
    orange = (255, 165, 0)
    orangered = (255, 69, 0)
    orchid = (218, 112, 214)
    palegoldenrod = (238, 232, 170)
    palegreen = (152, 251, 152)
    paleturquoise = (175, 238, 238)
    palevioletred = (219, 112, 147)
    papayawhip = (255, 239, 213)
    peachpuff = (255, 218, 185)
    peru = (205, 133, 63)
    pink = (255, 192, 203)
    plum = (221, 160, 221)
    powderblue = (176, 224, 230)
    purple = (128, 0, 128)
    rebeccapurple = (102, 51, 153)
    red = (255, 0, 0)
    rosybrown = (188, 143, 143)
    royalblue = (65, 105, 225)
    saddlebrown = (139, 69, 19)
    salmon = (250, 128, 114)
    sandybrown = (244, 164, 96)
    seagreen = (46, 139, 87)
    seashell = (255, 245, 238)
    sienna = (160, 82, 45)
    silver = (192, 192, 192)
    skyblue = (135, 206, 235)
    slateblue = (106, 90, 205)
    slategray = (112, 128, 144)
    snow = (255, 250, 250)
    springgreen = (0, 255, 127)
    steelblue = (70, 130, 180)
    tan = (210, 180, 140)
    teal = (0, 128, 128)
    thistle = (216, 191, 216)
    tomato = (255, 99, 71)
    turquoise = (64, 224, 208)
    violet = (238, 130, 238)
    wheat = (245, 222, 179)
    white = (255, 255, 255)
    whitesmoke = (245, 245, 245)
    yellow = (255, 255, 0)
    yellowgreen = (154, 205, 50)

    __hexCodePipeline = {}

    @classmethod
    def apply(cls,color,r) -> typing.Tuple[int,int,int]:
        f = lambda x: min(255,x*r)
        return tuple([f(x) for x in color])
    @classmethod
    def dark(cls,color) -> typing.Tuple[int,int,int]:
        return Cs.apply(color,0.4)
    @classmethod
    def dim(cls,color)-> typing.Tuple[int,int,int]:
        return Cs.apply(color,0.8)
    @classmethod
    def light(cls,color)-> typing.Tuple[int,int,int]:
        return Cs.apply(color,1.2)
    @classmethod
    def bright(cls,color)-> typing.Tuple[int,int,int]:
        return Cs.apply(color,1.6)
    
    @classmethod
    def hexColor(cls,hex:str)-> typing.Tuple[int,int,int]:
        hex = hex.upper()
        if hex in list(Cs.__hexCodePipeline):
            return Cs.__hexCodePipeline[hex]
        else:
            rgb = tuple(int(hex[i:i+2], 16)  for i in (0, 2, 4))
            Cs.__hexCodePipeline[hex]=rgb
            return rgb

    @classmethod
    def __getattr__(cls, name: str) -> pygame.Color:
        """존재하지 않는 속성에 접근할 때 pygame.Color 객체를 반환"""
        try:
            # Pygame의 Color 객체를 그대로 반환
            return pygame.Color(name.lower())
        except ValueError:
            raise AttributeError(f"'{cls.__name__}' 클래스에 '{name}' 속성이 없습니다.")        

class Icons:
    '''
    아이콘들의 실제 경로를 모아놓은 클래스입니다.
    base\REMO_ICONS 폴더에 있는 아이콘들을 사용합니다.
    '''
    ARROWDOWN = 'REMO_DEFAULT_ICONS_arrowDown.png'
    ARROWLEFT = 'REMO_DEFAULT_ICONS_arrowLeft.png'
    ARROWRIGHT = 'REMO_DEFAULT_ICONS_arrowRight.png'
    ARROWUP = 'REMO_DEFAULT_ICONS_arrowUp.png'
    ARROW_CLOCKWISE = 'REMO_DEFAULT_ICONS_arrow_clockwise.png'
    ARROW_COUNTERCLOCKWISE = 'REMO_DEFAULT_ICONS_arrow_counterclockwise.png'
    ARROW_CROSS = 'REMO_DEFAULT_ICONS_arrow_cross.png'
    ARROW_CROSS_DIVIDED = 'REMO_DEFAULT_ICONS_arrow_cross_divided.png'
    ARROW_DIAGONAL = 'REMO_DEFAULT_ICONS_arrow_diagonal.png'
    ARROW_DIAGONAL_CROSS = 'REMO_DEFAULT_ICONS_arrow_diagonal_cross.png'
    ARROW_DIAGONAL_CROSS_DIVIDED = 'REMO_DEFAULT_ICONS_arrow_diagonal_cross_divided.png'
    ARROW_HORIZONTAL = 'REMO_DEFAULT_ICONS_arrow_horizontal.png'
    ARROW_RESERVE = 'REMO_DEFAULT_ICONS_arrow_reserve.png'
    ARROW_RIGHT = 'REMO_DEFAULT_ICONS_arrow_right.png'
    ARROW_RIGHT_CURVE = 'REMO_DEFAULT_ICONS_arrow_right_curve.png'
    ARROW_ROTATE = 'REMO_DEFAULT_ICONS_arrow_rotate.png'
    AUDIOOFF = 'REMO_DEFAULT_ICONS_audioOff.png'
    AUDIOON = 'REMO_DEFAULT_ICONS_audioOn.png'
    AWARD = 'REMO_DEFAULT_ICONS_award.png'
    BARSHORIZONTAL = 'REMO_DEFAULT_ICONS_barsHorizontal.png'
    BARSVERTICAL = 'REMO_DEFAULT_ICONS_barsVertical.png'
    BOOK_CLOSED = 'REMO_DEFAULT_ICONS_book_closed.png'
    BOOK_OPEN = 'REMO_DEFAULT_ICONS_book_open.png'
    BOW = 'REMO_DEFAULT_ICONS_bow.png'
    BUTTON1 = 'REMO_DEFAULT_ICONS_button1.png'
    BUTTON2 = 'REMO_DEFAULT_ICONS_button2.png'
    BUTTON3 = 'REMO_DEFAULT_ICONS_button3.png'
    BUTTONA = 'REMO_DEFAULT_ICONS_buttonA.png'
    BUTTONB = 'REMO_DEFAULT_ICONS_buttonB.png'
    BUTTONL = 'REMO_DEFAULT_ICONS_buttonL.png'
    BUTTONL1 = 'REMO_DEFAULT_ICONS_buttonL1.png'
    BUTTONL2 = 'REMO_DEFAULT_ICONS_buttonL2.png'
    BUTTONR = 'REMO_DEFAULT_ICONS_buttonR.png'
    BUTTONR1 = 'REMO_DEFAULT_ICONS_buttonR1.png'
    BUTTONR2 = 'REMO_DEFAULT_ICONS_buttonR2.png'
    BUTTONSELECT = 'REMO_DEFAULT_ICONS_buttonSelect.png'
    BUTTONSTART = 'REMO_DEFAULT_ICONS_buttonStart.png'
    BUTTONX = 'REMO_DEFAULT_ICONS_buttonX.png'
    BUTTONY = 'REMO_DEFAULT_ICONS_buttonY.png'
    CAMPFIRE = 'REMO_DEFAULT_ICONS_campfire.png'
    CAR = 'REMO_DEFAULT_ICONS_car.png'
    CARD = 'REMO_DEFAULT_ICONS_card.png'
    CARDS_COLLECTION = 'REMO_DEFAULT_ICONS_cards_collection.png'
    CARDS_COLLECTION_OUTLINE = 'REMO_DEFAULT_ICONS_cards_collection_outline.png'
    CARDS_DIAGONAL = 'REMO_DEFAULT_ICONS_cards_diagonal.png'
    CARDS_FAN = 'REMO_DEFAULT_ICONS_cards_fan.png'
    CARDS_FAN_OUTLINE = 'REMO_DEFAULT_ICONS_cards_fan_outline.png'
    CARDS_FLIP = 'REMO_DEFAULT_ICONS_cards_flip.png'
    CARDS_ORDER = 'REMO_DEFAULT_ICONS_cards_order.png'
    CARDS_RETURN = 'REMO_DEFAULT_ICONS_cards_return.png'
    CARDS_SEEK = 'REMO_DEFAULT_ICONS_cards_seek.png'
    CARDS_SEEK_TOP = 'REMO_DEFAULT_ICONS_cards_seek_top.png'
    CARDS_SHIFT = 'REMO_DEFAULT_ICONS_cards_shift.png'
    CARDS_SHUFFLE = 'REMO_DEFAULT_ICONS_cards_shuffle.png'
    CARDS_SKULL = 'REMO_DEFAULT_ICONS_cards_skull.png'
    CARDS_STACK = 'REMO_DEFAULT_ICONS_cards_stack.png'
    CARDS_STACK_CROSS = 'REMO_DEFAULT_ICONS_cards_stack_cross.png'
    CARDS_STACK_HIGH = 'REMO_DEFAULT_ICONS_cards_stack_high.png'
    CARDS_TAKE = 'REMO_DEFAULT_ICONS_cards_take.png'
    CARDS_UNDER = 'REMO_DEFAULT_ICONS_cards_under.png'
    CARD_ADD = 'REMO_DEFAULT_ICONS_card_add.png'
    CARD_DIAGONAL = 'REMO_DEFAULT_ICONS_card_diagonal.png'
    CARD_DOWN = 'REMO_DEFAULT_ICONS_card_down.png'
    CARD_DOWN_OUTLINE = 'REMO_DEFAULT_ICONS_card_down_outline.png'
    CARD_FLIP = 'REMO_DEFAULT_ICONS_card_flip.png'
    CARD_FLIPDOUBLE = 'REMO_DEFAULT_ICONS_card_flipdouble.png'
    CARD_LIFT = 'REMO_DEFAULT_ICONS_card_lift.png'
    CARD_OUTLINE = 'REMO_DEFAULT_ICONS_card_outline.png'
    CARD_OUTLINE_LIFT = 'REMO_DEFAULT_ICONS_card_outline_lift.png'
    CARD_OUTLINE_PLACE = 'REMO_DEFAULT_ICONS_card_outline_place.png'
    CARD_OUTLINE_REMOVE = 'REMO_DEFAULT_ICONS_card_outline_remove.png'
    CARD_PLACE = 'REMO_DEFAULT_ICONS_card_place.png'
    CARD_REMOVE = 'REMO_DEFAULT_ICONS_card_remove.png'
    CARD_ROTATE = 'REMO_DEFAULT_ICONS_card_rotate.png'
    CARD_SUBTRACT = 'REMO_DEFAULT_ICONS_card_subtract.png'
    CARD_TAP = 'REMO_DEFAULT_ICONS_card_tap.png'
    CARD_TAP_DOWN = 'REMO_DEFAULT_ICONS_card_tap_down.png'
    CARD_TAP_OUTLINE = 'REMO_DEFAULT_ICONS_card_tap_outline.png'
    CARD_TAP_OUTLINE_DOWN = 'REMO_DEFAULT_ICONS_card_tap_outline_down.png'
    CARD_TAP_OUTLINE_UP = 'REMO_DEFAULT_ICONS_card_tap_outline_up.png'
    CARD_TAP_UP = 'REMO_DEFAULT_ICONS_card_tap_up.png'
    CARD_TARGET = 'REMO_DEFAULT_ICONS_card_target.png'
    CHARACTER = 'REMO_DEFAULT_ICONS_character.png'
    CHARACTER_LIFT = 'REMO_DEFAULT_ICONS_character_lift.png'
    CHARACTER_PLACE = 'REMO_DEFAULT_ICONS_character_place.png'
    CHARACTER_REMOVE = 'REMO_DEFAULT_ICONS_character_remove.png'
    CHECKMARK = 'REMO_DEFAULT_ICONS_checkmark.png'
    CHESS_BISHOP = 'REMO_DEFAULT_ICONS_chess_bishop.png'
    CHESS_KING = 'REMO_DEFAULT_ICONS_chess_king.png'
    CHESS_KNIGHT = 'REMO_DEFAULT_ICONS_chess_knight.png'
    CHESS_PAWN = 'REMO_DEFAULT_ICONS_chess_pawn.png'
    CHESS_QUEEN = 'REMO_DEFAULT_ICONS_chess_queen.png'
    CHESS_ROOK = 'REMO_DEFAULT_ICONS_chess_rook.png'
    CLOUD = 'REMO_DEFAULT_ICONS_cloud.png'
    CLOUDUPLOAD = 'REMO_DEFAULT_ICONS_cloudUpload.png'
    COIN = 'REMO_DEFAULT_ICONS_coin.png'
    CONTRAST = 'REMO_DEFAULT_ICONS_contrast.png'
    CONTROLLERTILT = 'REMO_DEFAULT_ICONS_controllerTilt.png'
    CONTROLLERTILT_LEFT = 'REMO_DEFAULT_ICONS_controllerTilt_left.png'
    CONTROLLERTILT_RIGHT = 'REMO_DEFAULT_ICONS_controllerTilt_right.png'
    CPU = 'REMO_DEFAULT_ICONS_cpu.png'
    CROSS = 'REMO_DEFAULT_ICONS_cross.png'
    CROWN_A = 'REMO_DEFAULT_ICONS_crown_a.png'
    CROWN_B = 'REMO_DEFAULT_ICONS_crown_b.png'
    CURSOR = 'REMO_DEFAULT_ICONS_cursor.png'
    D10 = 'REMO_DEFAULT_ICONS_d10.png'
    D10_NUMBER = 'REMO_DEFAULT_ICONS_d10_number.png'
    D10_OUTLINE = 'REMO_DEFAULT_ICONS_d10_outline.png'
    D10_OUTLINE_NUMBER = 'REMO_DEFAULT_ICONS_d10_outline_number.png'
    D12 = 'REMO_DEFAULT_ICONS_d12.png'
    D12_NUMBER = 'REMO_DEFAULT_ICONS_d12_number.png'
    D12_OUTLINE = 'REMO_DEFAULT_ICONS_d12_outline.png'
    D12_OUTLINE_NUMBER = 'REMO_DEFAULT_ICONS_d12_outline_number.png'
    D2 = 'REMO_DEFAULT_ICONS_d2.png'
    D20 = 'REMO_DEFAULT_ICONS_d20.png'
    D20_NUMBER = 'REMO_DEFAULT_ICONS_d20_number.png'
    D20_OUTLINE = 'REMO_DEFAULT_ICONS_d20_outline.png'
    D20_OUTLINE_NUMBER = 'REMO_DEFAULT_ICONS_d20_outline_number.png'
    D2_NUMBER = 'REMO_DEFAULT_ICONS_d2_number.png'
    D2_OUTLINE = 'REMO_DEFAULT_ICONS_d2_outline.png'
    D2_OUTLINE_NUMBER = 'REMO_DEFAULT_ICONS_d2_outline_number.png'
    D3 = 'REMO_DEFAULT_ICONS_d3.png'
    D3_NUMBER = 'REMO_DEFAULT_ICONS_d3_number.png'
    D3_OUTLINE = 'REMO_DEFAULT_ICONS_d3_outline.png'
    D3_OUTLINE_NUMBER = 'REMO_DEFAULT_ICONS_d3_outline_number.png'
    D4 = 'REMO_DEFAULT_ICONS_d4.png'
    D4_NUMBER = 'REMO_DEFAULT_ICONS_d4_number.png'
    D4_OUTLINE = 'REMO_DEFAULT_ICONS_d4_outline.png'
    D4_OUTLINE_NUMBER = 'REMO_DEFAULT_ICONS_d4_outline_number.png'
    D6 = 'REMO_DEFAULT_ICONS_d6.png'
    D6_NUMBER = 'REMO_DEFAULT_ICONS_d6_number.png'
    D6_OUTLINE = 'REMO_DEFAULT_ICONS_d6_outline.png'
    D6_OUTLINE_NUMBER = 'REMO_DEFAULT_ICONS_d6_outline_number.png'
    D8 = 'REMO_DEFAULT_ICONS_d8.png'
    D8_NUMBER = 'REMO_DEFAULT_ICONS_d8_number.png'
    D8_OUTLINE = 'REMO_DEFAULT_ICONS_d8_outline.png'
    D8_OUTLINE_NUMBER = 'REMO_DEFAULT_ICONS_d8_outline_number.png'
    DEVICETILT = 'REMO_DEFAULT_ICONS_deviceTilt.png'
    DEVICETILT_LEFT = 'REMO_DEFAULT_ICONS_deviceTilt_left.png'
    DEVICETILT_RIGHT = 'REMO_DEFAULT_ICONS_deviceTilt_right.png'
    DIAMOND = 'REMO_DEFAULT_ICONS_diamond.png'
    DICE = 'REMO_DEFAULT_ICONS_dice.png'
    DICE_1 = 'REMO_DEFAULT_ICONS_dice_1.png'
    DICE_2 = 'REMO_DEFAULT_ICONS_dice_2.png'
    DICE_3 = 'REMO_DEFAULT_ICONS_dice_3.png'
    DICE_3D = 'REMO_DEFAULT_ICONS_dice_3D.png'
    DICE_3D_DETAILED = 'REMO_DEFAULT_ICONS_dice_3D_detailed.png'
    DICE_4 = 'REMO_DEFAULT_ICONS_dice_4.png'
    DICE_5 = 'REMO_DEFAULT_ICONS_dice_5.png'
    DICE_6 = 'REMO_DEFAULT_ICONS_dice_6.png'
    DICE_CLOSE = 'REMO_DEFAULT_ICONS_dice_close.png'
    DICE_DETAILED = 'REMO_DEFAULT_ICONS_dice_detailed.png'
    DICE_EMPTY = 'REMO_DEFAULT_ICONS_dice_empty.png'
    DICE_OUT = 'REMO_DEFAULT_ICONS_dice_out.png'
    DICE_QUESTION = 'REMO_DEFAULT_ICONS_dice_question.png'
    DICE_SHIELD = 'REMO_DEFAULT_ICONS_dice_shield.png'
    DICE_SKULL = 'REMO_DEFAULT_ICONS_dice_skull.png'
    DICE_SWORD = 'REMO_DEFAULT_ICONS_dice_sword.png'
    DIRECTION_E = 'REMO_DEFAULT_ICONS_direction_e.png'
    DIRECTION_N = 'REMO_DEFAULT_ICONS_direction_n.png'
    DIRECTION_S = 'REMO_DEFAULT_ICONS_direction_s.png'
    DIRECTION_W = 'REMO_DEFAULT_ICONS_direction_w.png'
    DOLLAR = 'REMO_DEFAULT_ICONS_dollar.png'
    DOWN = 'REMO_DEFAULT_ICONS_down.png'
    DOWNLEFT = 'REMO_DEFAULT_ICONS_downLeft.png'
    DOWNLOAD = 'REMO_DEFAULT_ICONS_download.png'
    DOWNRIGHT = 'REMO_DEFAULT_ICONS_downRight.png'
    DPAD = 'REMO_DEFAULT_ICONS_DPAD.png'
    DPAD_ALL = 'REMO_DEFAULT_ICONS_DPAD_all.png'
    DPAD_DOWN = 'REMO_DEFAULT_ICONS_DPAD_down.png'
    DPAD_LEFT = 'REMO_DEFAULT_ICONS_DPAD_left.png'
    DPAD_RIGHT = 'REMO_DEFAULT_ICONS_DPAD_right.png'
    DPAD_UP = 'REMO_DEFAULT_ICONS_DPAD_up.png'
    EXCLAMATION = 'REMO_DEFAULT_ICONS_exclamation.png'
    EXIT = 'REMO_DEFAULT_ICONS_exit.png'
    EXITLEFT = 'REMO_DEFAULT_ICONS_exitLeft.png'
    EXITRIGHT = 'REMO_DEFAULT_ICONS_exitRight.png'
    EXPLODING = 'REMO_DEFAULT_ICONS_exploding.png'
    EXPLODING_6 = 'REMO_DEFAULT_ICONS_exploding_6.png'
    EXPORT = 'REMO_DEFAULT_ICONS_export.png'
    FASTFORWARD = 'REMO_DEFAULT_ICONS_fastForward.png'
    FIGHTFIST = 'REMO_DEFAULT_ICONS_fightFist.png'
    FIGHTFIST_CIRCLE = 'REMO_DEFAULT_ICONS_fightFist_circle.png'
    FIGHTJ = 'REMO_DEFAULT_ICONS_fightJ.png'
    FIGHTJOY_00 = 'REMO_DEFAULT_ICONS_fightJoy_00.png'
    FIGHTJOY_01 = 'REMO_DEFAULT_ICONS_fightJoy_01.png'
    FIGHTJOY_02 = 'REMO_DEFAULT_ICONS_fightJoy_02.png'
    FIGHTJOY_03 = 'REMO_DEFAULT_ICONS_fightJoy_03.png'
    FIGHTJOY_04 = 'REMO_DEFAULT_ICONS_fightJoy_04.png'
    FIGHTJOY_05 = 'REMO_DEFAULT_ICONS_fightJoy_05.png'
    FIGHTJOY_06 = 'REMO_DEFAULT_ICONS_fightJoy_06.png'
    FIGHTJOY_07 = 'REMO_DEFAULT_ICONS_fightJoy_07.png'
    FIGHTJOY_08 = 'REMO_DEFAULT_ICONS_fightJoy_08.png'
    FIGHTJOY_09 = 'REMO_DEFAULT_ICONS_fightJoy_09.png'
    FIGHTJOY_10 = 'REMO_DEFAULT_ICONS_fightJoy_10.png'
    FIGHTJOY_11 = 'REMO_DEFAULT_ICONS_fightJoy_11.png'
    FIGHTJOY_12 = 'REMO_DEFAULT_ICONS_fightJoy_12.png'
    FIGHTJOY_13 = 'REMO_DEFAULT_ICONS_fightJoy_13.png'
    FIGHTJOY_14 = 'REMO_DEFAULT_ICONS_fightJoy_14.png'
    FIGHTJOY_15 = 'REMO_DEFAULT_ICONS_fightJoy_15.png'
    FIGHTJOY_16 = 'REMO_DEFAULT_ICONS_fightJoy_16.png'
    FIGHTJOY_17 = 'REMO_DEFAULT_ICONS_fightJoy_17.png'
    FIGHTJOY_18 = 'REMO_DEFAULT_ICONS_fightJoy_18.png'
    FIGHTJOY_19 = 'REMO_DEFAULT_ICONS_fightJoy_19.png'
    FIGHTJOY_20 = 'REMO_DEFAULT_ICONS_fightJoy_20.png'
    FIGHTJOY_21 = 'REMO_DEFAULT_ICONS_fightJoy_21.png'
    FIGHTJOY_22 = 'REMO_DEFAULT_ICONS_fightJoy_22.png'
    FIGHTJOY_23 = 'REMO_DEFAULT_ICONS_fightJoy_23.png'
    FIGHTJOY_24 = 'REMO_DEFAULT_ICONS_fightJoy_24.png'
    FIGHTJOY_25 = 'REMO_DEFAULT_ICONS_fightJoy_25.png'
    FIGHTJOY_26 = 'REMO_DEFAULT_ICONS_fightJoy_26.png'
    FIGHTJOY_27 = 'REMO_DEFAULT_ICONS_fightJoy_27.png'
    FIGHTJOY_28 = 'REMO_DEFAULT_ICONS_fightJoy_28.png'
    FIGHTJOY_29 = 'REMO_DEFAULT_ICONS_fightJoy_29.png'
    FIGHTJOY_30 = 'REMO_DEFAULT_ICONS_fightJoy_30.png'
    FIGHTJOY_31 = 'REMO_DEFAULT_ICONS_fightJoy_31.png'
    FIGHTPLUS = 'REMO_DEFAULT_ICONS_fightPlus.png'
    FIGURINE = 'REMO_DEFAULT_ICONS_figurine.png'
    FIRE = 'REMO_DEFAULT_ICONS_fire.png'
    FLAG = 'REMO_DEFAULT_ICONS_flag.png'
    FLAG_SQUARE = 'REMO_DEFAULT_ICONS_flag_square.png'
    FLAG_TRIANGLE = 'REMO_DEFAULT_ICONS_flag_triangle.png'
    FLASK_EMPTY = 'REMO_DEFAULT_ICONS_flask_empty.png'
    FLASK_FULL = 'REMO_DEFAULT_ICONS_flask_full.png'
    FLASK_HALF = 'REMO_DEFAULT_ICONS_flask_half.png'
    FLIP_EMPTY = 'REMO_DEFAULT_ICONS_flip_empty.png'
    FLIP_FULL = 'REMO_DEFAULT_ICONS_flip_full.png'
    FLIP_HALF = 'REMO_DEFAULT_ICONS_flip_half.png'
    FLIP_HEAD = 'REMO_DEFAULT_ICONS_flip_head.png'
    FLIP_TAILS = 'REMO_DEFAULT_ICONS_flip_tails.png'
    GAMEPAD = 'REMO_DEFAULT_ICONS_gamepad.png'
    GAMEPAD1 = 'REMO_DEFAULT_ICONS_gamepad1.png'
    GAMEPAD2 = 'REMO_DEFAULT_ICONS_gamepad2.png'
    GAMEPAD3 = 'REMO_DEFAULT_ICONS_gamepad3.png'
    GAMEPAD4 = 'REMO_DEFAULT_ICONS_gamepad4.png'
    GEAR = 'REMO_DEFAULT_ICONS_gear.png'
    HAND = 'REMO_DEFAULT_ICONS_hand.png'
    HAND_CARD = 'REMO_DEFAULT_ICONS_hand_card.png'
    HAND_CROSS = 'REMO_DEFAULT_ICONS_hand_cross.png'
    HAND_CUBE = 'REMO_DEFAULT_ICONS_hand_cube.png'
    HAND_HEXAGON = 'REMO_DEFAULT_ICONS_hand_hexagon.png'
    HAND_TOKEN = 'REMO_DEFAULT_ICONS_hand_token.png'
    HAND_TOKEN_OPEN = 'REMO_DEFAULT_ICONS_hand_token_open.png'
    HEXAGON = 'REMO_DEFAULT_ICONS_hexagon.png'
    HEXAGON_IN = 'REMO_DEFAULT_ICONS_hexagon_in.png'
    HEXAGON_OUT = 'REMO_DEFAULT_ICONS_hexagon_out.png'
    HEXAGON_OUTLINE = 'REMO_DEFAULT_ICONS_hexagon_outline.png'
    HEXAGON_QUESTION = 'REMO_DEFAULT_ICONS_hexagon_question.png'
    HEXAGON_SWITCH = 'REMO_DEFAULT_ICONS_hexagon_switch.png'
    HEXAGON_TILE = 'REMO_DEFAULT_ICONS_hexagon_tile.png'
    HOME = 'REMO_DEFAULT_ICONS_home.png'
    HOURGLASS = 'REMO_DEFAULT_ICONS_hourglass.png'
    HOURGLASS_BOTTOM = 'REMO_DEFAULT_ICONS_hourglass_bottom.png'
    HOURGLASS_TOP = 'REMO_DEFAULT_ICONS_hourglass_top.png'
    IMPORT = 'REMO_DEFAULT_ICONS_import.png'
    INFORMATION = 'REMO_DEFAULT_ICONS_information.png'
    JOYSTICK = 'REMO_DEFAULT_ICONS_joystick.png'
    JOYSTICKLEFT = 'REMO_DEFAULT_ICONS_joystickLeft.png'
    JOYSTICKL_SIDE = 'REMO_DEFAULT_ICONS_joystickL_side.png'
    JOYSTICKL_TOP = 'REMO_DEFAULT_ICONS_joystickL_top.png'
    JOYSTICKRIGHT = 'REMO_DEFAULT_ICONS_joystickRight.png'
    JOYSTICKR_SIDE = 'REMO_DEFAULT_ICONS_joystickR_side.png'
    JOYSTICKR_TOP = 'REMO_DEFAULT_ICONS_joystickR_top.png'
    JOYSTICKUP = 'REMO_DEFAULT_ICONS_joystickUp.png'
    KEY = 'REMO_DEFAULT_ICONS_key.png'
    KEYLARGE = 'REMO_DEFAULT_ICONS_keyLarge.png'
    KEYLARGE_3D = 'REMO_DEFAULT_ICONS_keyLarge_3d.png'
    KEYSMALL = 'REMO_DEFAULT_ICONS_keySmall.png'
    KEYSMALL_3D = 'REMO_DEFAULT_ICONS_keySmall_3d.png'
    LARGER = 'REMO_DEFAULT_ICONS_larger.png'
    LEADERBOARDSCOMPLEX = 'REMO_DEFAULT_ICONS_leaderboardsComplex.png'
    LEADERBOARDSSIMPLE = 'REMO_DEFAULT_ICONS_leaderboardsSimple.png'
    LEFT = 'REMO_DEFAULT_ICONS_left.png'
    LOCKED = 'REMO_DEFAULT_ICONS_locked.png'
    LOCK_CLOSED = 'REMO_DEFAULT_ICONS_lock_closed.png'
    LOCK_OPEN = 'REMO_DEFAULT_ICONS_lock_open.png'
    MASSIVEMULTIPLAYER = 'REMO_DEFAULT_ICONS_massiveMultiplayer.png'
    MEDAL1 = 'REMO_DEFAULT_ICONS_medal1.png'
    MEDAL2 = 'REMO_DEFAULT_ICONS_medal2.png'
    MENUGRID = 'REMO_DEFAULT_ICONS_menuGrid.png'
    MENULIST = 'REMO_DEFAULT_ICONS_menuList.png'
    MINUS = 'REMO_DEFAULT_ICONS_minus.png'
    MOUSE = 'REMO_DEFAULT_ICONS_mouse.png'
    MOUSELEFT = 'REMO_DEFAULT_ICONS_mouseLeft.png'
    MOUSEMIDDLE = 'REMO_DEFAULT_ICONS_mouseMiddle.png'
    MOUSERIGHT = 'REMO_DEFAULT_ICONS_mouseRight.png'
    MOVIE = 'REMO_DEFAULT_ICONS_movie.png'
    MULTIPLAYER = 'REMO_DEFAULT_ICONS_multiplayer.png'
    MUSICOFF = 'REMO_DEFAULT_ICONS_musicOff.png'
    MUSICON = 'REMO_DEFAULT_ICONS_musicOn.png'
    NEXT = 'REMO_DEFAULT_ICONS_next.png'
    NOTEPAD = 'REMO_DEFAULT_ICONS_notepad.png'
    NOTEPAD_WRITE = 'REMO_DEFAULT_ICONS_notepad_write.png'
    OPEN = 'REMO_DEFAULT_ICONS_open.png'
    PAUSE = 'REMO_DEFAULT_ICONS_pause.png'
    PAWN = 'REMO_DEFAULT_ICONS_pawn.png'
    PAWNS = 'REMO_DEFAULT_ICONS_pawns.png'
    PAWN_CLOCKWISE = 'REMO_DEFAULT_ICONS_pawn_clockwise.png'
    PAWN_COUNTERCLOCKWISE = 'REMO_DEFAULT_ICONS_pawn_counterclockwise.png'
    PAWN_DOWN = 'REMO_DEFAULT_ICONS_pawn_down.png'
    PAWN_FLIP = 'REMO_DEFAULT_ICONS_pawn_flip.png'
    PAWN_LEFT = 'REMO_DEFAULT_ICONS_pawn_left.png'
    PAWN_REVERSE = 'REMO_DEFAULT_ICONS_pawn_reverse.png'
    PAWN_RIGHT = 'REMO_DEFAULT_ICONS_pawn_right.png'
    PAWN_SKIP = 'REMO_DEFAULT_ICONS_pawn_skip.png'
    PAWN_TABLE = 'REMO_DEFAULT_ICONS_pawn_table.png'
    PAWN_UP = 'REMO_DEFAULT_ICONS_pawn_up.png'
    PENTAGON = 'REMO_DEFAULT_ICONS_pentagon.png'
    PENTAGON_OUTLINE = 'REMO_DEFAULT_ICONS_pentagon_outline.png'
    PENTAGON_QUESTION = 'REMO_DEFAULT_ICONS_pentagon_question.png'
    PHONE = 'REMO_DEFAULT_ICONS_phone.png'
    PLUS = 'REMO_DEFAULT_ICONS_plus.png'
    POINTER = 'REMO_DEFAULT_ICONS_pointer.png'
    POUCH = 'REMO_DEFAULT_ICONS_pouch.png'
    POUCH_ADD = 'REMO_DEFAULT_ICONS_pouch_add.png'
    POUCH_REMOVE = 'REMO_DEFAULT_ICONS_pouch_remove.png'
    POWER = 'REMO_DEFAULT_ICONS_power.png'
    PREVIOUS = 'REMO_DEFAULT_ICONS_previous.png'
    PUZZLE = 'REMO_DEFAULT_ICONS_puzzle.png'
    QUESTION = 'REMO_DEFAULT_ICONS_question.png'
    RESOURCE_APPLE = 'REMO_DEFAULT_ICONS_resource_apple.png'
    RESOURCE_IRON = 'REMO_DEFAULT_ICONS_resource_iron.png'
    RESOURCE_LUMBER = 'REMO_DEFAULT_ICONS_resource_lumber.png'
    RESOURCE_PLANKS = 'REMO_DEFAULT_ICONS_resource_planks.png'
    RESOURCE_WHEAT = 'REMO_DEFAULT_ICONS_resource_wheat.png'
    RESOURCE_WOOD = 'REMO_DEFAULT_ICONS_resource_wood.png'
    RETURN = 'REMO_DEFAULT_ICONS_return.png'
    REWIND = 'REMO_DEFAULT_ICONS_rewind.png'
    RHOMBUS = 'REMO_DEFAULT_ICONS_rhombus.png'
    RHOMBUS_OUTLINE = 'REMO_DEFAULT_ICONS_rhombus_outline.png'
    RHOMBUS_QUESTION = 'REMO_DEFAULT_ICONS_rhombus_question.png'
    RIGHT = 'REMO_DEFAULT_ICONS_right.png'
    SAVE = 'REMO_DEFAULT_ICONS_save.png'
    SCROLLHORIZONTAL = 'REMO_DEFAULT_ICONS_scrollHorizontal.png'
    SCROLLVERTICAL = 'REMO_DEFAULT_ICONS_scrollVertical.png'
    SHARE1 = 'REMO_DEFAULT_ICONS_share1.png'
    SHARE2 = 'REMO_DEFAULT_ICONS_share2.png'
    SHIELD = 'REMO_DEFAULT_ICONS_shield.png'
    SHOPPINGBASKET = 'REMO_DEFAULT_ICONS_shoppingBasket.png'
    SHOPPINGCART = 'REMO_DEFAULT_ICONS_shoppingCart.png'
    SIGANL1 = 'REMO_DEFAULT_ICONS_siganl1.png'
    SIGNAL2 = 'REMO_DEFAULT_ICONS_signal2.png'
    SIGNAL3 = 'REMO_DEFAULT_ICONS_signal3.png'
    SINGLEPLAYER = 'REMO_DEFAULT_ICONS_singleplayer.png'
    SKULL = 'REMO_DEFAULT_ICONS_skull.png'
    SMALLER = 'REMO_DEFAULT_ICONS_smaller.png'
    SPINNER = 'REMO_DEFAULT_ICONS_spinner.png'
    SPINNER_SEGMENT = 'REMO_DEFAULT_ICONS_spinner_segment.png'
    STAR = 'REMO_DEFAULT_ICONS_star.png'
    STOP = 'REMO_DEFAULT_ICONS_stop.png'
    STRUCTURE_CHURCH = 'REMO_DEFAULT_ICONS_structure_church.png'
    STRUCTURE_FARM = 'REMO_DEFAULT_ICONS_structure_farm.png'
    STRUCTURE_GATE = 'REMO_DEFAULT_ICONS_structure_gate.png'
    STRUCTURE_HOUSE = 'REMO_DEFAULT_ICONS_structure_house.png'
    STRUCTURE_TOWER = 'REMO_DEFAULT_ICONS_structure_tower.png'
    STRUCTURE_WALL = 'REMO_DEFAULT_ICONS_structure_wall.png'
    STRUCTURE_WATCHTOWER = 'REMO_DEFAULT_ICONS_structure_watchtower.png'
    SUIT_CLUBS = 'REMO_DEFAULT_ICONS_suit_clubs.png'
    SUIT_DIAMONDS = 'REMO_DEFAULT_ICONS_suit_diamonds.png'
    SUIT_HEARTS = 'REMO_DEFAULT_ICONS_suit_hearts.png'
    SUIT_HEARTS_BROKEN = 'REMO_DEFAULT_ICONS_suit_hearts_broken.png'
    SUIT_SPADES = 'REMO_DEFAULT_ICONS_suit_spades.png'
    SWORD = 'REMO_DEFAULT_ICONS_sword.png'
    TABLET = 'REMO_DEFAULT_ICONS_tablet.png'
    TAG_1 = 'REMO_DEFAULT_ICONS_tag_1.png'
    TAG_10 = 'REMO_DEFAULT_ICONS_tag_10.png'
    TAG_2 = 'REMO_DEFAULT_ICONS_tag_2.png'
    TAG_3 = 'REMO_DEFAULT_ICONS_tag_3.png'
    TAG_4 = 'REMO_DEFAULT_ICONS_tag_4.png'
    TAG_5 = 'REMO_DEFAULT_ICONS_tag_5.png'
    TAG_6 = 'REMO_DEFAULT_ICONS_tag_6.png'
    TAG_7 = 'REMO_DEFAULT_ICONS_tag_7.png'
    TAG_8 = 'REMO_DEFAULT_ICONS_tag_8.png'
    TAG_9 = 'REMO_DEFAULT_ICONS_tag_9.png'
    TAG_D6 = 'REMO_DEFAULT_ICONS_tag_d6.png'
    TAG_D6_1 = 'REMO_DEFAULT_ICONS_tag_d6_1.png'
    TAG_D6_2 = 'REMO_DEFAULT_ICONS_tag_d6_2.png'
    TAG_D6_3 = 'REMO_DEFAULT_ICONS_tag_d6_3.png'
    TAG_D6_4 = 'REMO_DEFAULT_ICONS_tag_d6_4.png'
    TAG_D6_5 = 'REMO_DEFAULT_ICONS_tag_d6_5.png'
    TAG_D6_6 = 'REMO_DEFAULT_ICONS_tag_d6_6.png'
    TAG_D6_CHECK = 'REMO_DEFAULT_ICONS_tag_d6_check.png'
    TAG_D6_CROSS = 'REMO_DEFAULT_ICONS_tag_d6_cross.png'
    TAG_D6_INFINTE = 'REMO_DEFAULT_ICONS_tag_d6_infinte.png'
    TAG_EMPTY = 'REMO_DEFAULT_ICONS_tag_empty.png'
    TAG_INFINITE = 'REMO_DEFAULT_ICONS_tag_infinite.png'
    TAG_SHIELD = 'REMO_DEFAULT_ICONS_tag_shield.png'
    TAG_SHIELD_1 = 'REMO_DEFAULT_ICONS_tag_shield_1.png'
    TAG_SHIELD_10 = 'REMO_DEFAULT_ICONS_tag_shield_10.png'
    TAG_SHIELD_2 = 'REMO_DEFAULT_ICONS_tag_shield_2.png'
    TAG_SHIELD_3 = 'REMO_DEFAULT_ICONS_tag_shield_3.png'
    TAG_SHIELD_4 = 'REMO_DEFAULT_ICONS_tag_shield_4.png'
    TAG_SHIELD_5 = 'REMO_DEFAULT_ICONS_tag_shield_5.png'
    TAG_SHIELD_6 = 'REMO_DEFAULT_ICONS_tag_shield_6.png'
    TAG_SHIELD_7 = 'REMO_DEFAULT_ICONS_tag_shield_7.png'
    TAG_SHIELD_8 = 'REMO_DEFAULT_ICONS_tag_shield_8.png'
    TAG_SHIELD_9 = 'REMO_DEFAULT_ICONS_tag_shield_9.png'
    TAG_SHIELD_INFINITE = 'REMO_DEFAULT_ICONS_tag_shield_infinite.png'
    TARGET = 'REMO_DEFAULT_ICONS_target.png'
    TIMER_0 = 'REMO_DEFAULT_ICONS_timer_0.png'
    TIMER_100 = 'REMO_DEFAULT_ICONS_timer_100.png'
    TIMER_CCW_25 = 'REMO_DEFAULT_ICONS_timer_CCW_25.png'
    TIMER_CCW_50 = 'REMO_DEFAULT_ICONS_timer_CCW_50.png'
    TIMER_CCW_75 = 'REMO_DEFAULT_ICONS_timer_CCW_75.png'
    TIMER_CW_25 = 'REMO_DEFAULT_ICONS_timer_CW_25.png'
    TIMER_CW_50 = 'REMO_DEFAULT_ICONS_timer_CW_50.png'
    TIMER_CW_75 = 'REMO_DEFAULT_ICONS_timer_CW_75.png'
    TOKEN = 'REMO_DEFAULT_ICONS_token.png'
    TOKENS = 'REMO_DEFAULT_ICONS_tokens.png'
    TOKENS_SHADOW = 'REMO_DEFAULT_ICONS_tokens_shadow.png'
    TOKENS_STACK = 'REMO_DEFAULT_ICONS_tokens_stack.png'
    TOKEN_ADD = 'REMO_DEFAULT_ICONS_token_add.png'
    TOKEN_GIVE = 'REMO_DEFAULT_ICONS_token_give.png'
    TOKEN_IN = 'REMO_DEFAULT_ICONS_token_in.png'
    TOKEN_OUT = 'REMO_DEFAULT_ICONS_token_out.png'
    TOKEN_REMOVE = 'REMO_DEFAULT_ICONS_token_remove.png'
    TOKEN_SUBTRACT = 'REMO_DEFAULT_ICONS_token_subtract.png'
    TOOLBRUSH = 'REMO_DEFAULT_ICONS_toolBrush.png'
    TOOLERASER = 'REMO_DEFAULT_ICONS_toolEraser.png'
    TOOLFILL = 'REMO_DEFAULT_ICONS_toolFill.png'
    TOOLPENCIL = 'REMO_DEFAULT_ICONS_toolPencil.png'
    TRASHCAN = 'REMO_DEFAULT_ICONS_trashcan.png'
    TRASHCANOPEN = 'REMO_DEFAULT_ICONS_trashcanOpen.png'
    TROPHY = 'REMO_DEFAULT_ICONS_trophy.png'
    UNLOCKED = 'REMO_DEFAULT_ICONS_unlocked.png'
    UP = 'REMO_DEFAULT_ICONS_up.png'
    UPLEFT = 'REMO_DEFAULT_ICONS_upLeft.png'
    UPLOAD = 'REMO_DEFAULT_ICONS_upload.png'
    UPRIGHT = 'REMO_DEFAULT_ICONS_upRight.png'
    USERROBOT = 'REMO_DEFAULT_ICONS_userRobot.png'
    VIDEO = 'REMO_DEFAULT_ICONS_video.png'
    WARNING = 'REMO_DEFAULT_ICONS_warning.png'
    WRENCH = 'REMO_DEFAULT_ICONS_wrench.png'
    ZOOM = 'REMO_DEFAULT_ICONS_zoom.png'
    ZOOMDEFAULT = 'REMO_DEFAULT_ICONS_zoomDefault.png'
    ZOOMIN = 'REMO_DEFAULT_ICONS_zoomIn.png'
    ZOOMOUT = 'REMO_DEFAULT_ICONS_zoomOut.png'
