"""
sets constants for the program
"""
import pygame

# for options key change
# noinspection IncorrectFormatting
KEY_CONSTANTS = (pygame.K_BACKSPACE, pygame.K_TAB, pygame.K_CLEAR, pygame.K_RETURN, pygame.K_PAUSE, pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_EXCLAIM, pygame.K_QUOTEDBL, pygame.K_HASH, pygame.K_DOLLAR, pygame.K_AMPERSAND, pygame.K_QUOTE, pygame.K_LEFTPAREN, pygame.K_RIGHTPAREN, pygame.K_ASTERISK, pygame.K_PLUS, pygame.K_COMMA, pygame.K_MINUS, pygame.K_PERIOD, pygame.K_SLASH, pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_COLON, pygame.K_SEMICOLON, pygame.K_LESS, pygame.K_EQUALS, pygame.K_GREATER, pygame.K_QUESTION, pygame.K_AT, pygame.K_LEFTBRACKET, pygame.K_BACKSLASH, pygame.K_RIGHTBRACKET, pygame.K_CARET, pygame.K_UNDERSCORE, pygame.K_BACKQUOTE, pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z, pygame.K_DELETE, pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9, pygame.K_KP_PERIOD, pygame.K_KP_DIVIDE, pygame.K_KP_MULTIPLY, pygame.K_KP_MINUS, pygame.K_KP_PLUS, pygame.K_KP_ENTER, pygame.K_KP_EQUALS, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_INSERT, pygame.K_HOME, pygame.K_END, pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6, pygame.K_F7, pygame.K_F8, pygame.K_F9, pygame.K_F10, pygame.K_F11, pygame.K_F12, pygame.K_F13, pygame.K_F14, pygame.K_F15, pygame.K_NUMLOCK, pygame.K_CAPSLOCK, pygame.K_SCROLLOCK, pygame.K_RSHIFT, pygame.K_LSHIFT, pygame.K_RCTRL, pygame.K_LCTRL, pygame.K_RALT, pygame.K_LALT, pygame.K_RMETA, pygame.K_LMETA, pygame.K_LSUPER, pygame.K_RSUPER, pygame.K_MODE, pygame.K_HELP, pygame.K_PRINT, pygame.K_SYSREQ, pygame.K_BREAK, pygame.K_MENU, pygame.K_POWER, pygame.K_EURO, pygame.K_AC_BACK)

# for level and player data saving (change... I think?  Sometime.)
VERSION = 4

# for level saving, new code every update (probably use randomizer on previous one)
# noinspection SpellCheckingInspection
LETTER_CODES = {
    "1": "1234567890qwertyuiopasdfghjklzxcvbnm`-=[]\;',./~!@#$%^&*_+{}|:\"<>?←↑→↓↔↖↗↘↙↚↛↜↝↞↟↠↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇋⇊⇉⇈⇇",
    "2": "1234567890qwertyuiopasdfghjklzxcvbnm`-=[]\;',./~!()\"#$%^&*_+{}|:<>?←↑→↓↔↖↗↘↙↚↛↜↝↞↟↠↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇋⇊⇉⇈⇇",
    "3": "n|tao↯q↛x↠p↣0+k_>5)↬↔fv↝c6y%↢↰7w<(↪gh↙su8i'9m↨}[↖↭`↥?↫↚*2↧↲jl↞eb↑\\r↟↮↦=3↤/-]↗$z\",;↩14!←:^{~.↱d→↜#↓&↘",
    "4": "1234567890-=qwertyuiop[]asdfghjkàl;’zxcvbnm,./!@#$%^&()+QWERTYUIOP{}|ASDFGHJKL:ZXCVBNM<?úíóáéç:â€èìùòÀÈÙÌÒÁÉÚÍÓÄËÏÜÖêûîôÂÊÛÎÔ"
}

# for level saving
# noinspection IncorrectFormatting
BLOCKS = ("player", "ground", "goal", "lava", "jump", "gravity", "easter egg", "repel", "activator", "coin", "msg", "mud", "sticky", "bouncy", "")
BARRIERS = ("ground", "lava", "repel", "mud", "sticky", "")

# for construction
BLOCK_LIST = ()

# for barrier collision
SOLID_BLOCKS = {"ground", "jump", "gravity", "sticky", "mud"}

# for rendering
BLOCK_FILLS = {
    "ground": (0, 0, 0),
    "goal": (50, 191, 0),
    "lava": (255, 77, 0),
    "jump": (128, 255, 0),
    "repel": (255, 184, 0),
    "gravity": (255, 0, 138),
    "activator": (204, 41, 41),
    "mud": (171, 24, 10),
    "sticky": (204, 37, 0),
    "bouncy": (171, 204, 78)
}
BARRIER_COLORS = {
    "ground": {True: (128, 128, 128), False: (0, 0, 0)},
    "lava": {True: (255, 168, 128), False: (255, 77, 0)},
    "repel": {True: (255, 219, 128), False: (255, 184, 0)},
    "mud": {True: (179, 104, 71), False: (102, 31, 0)},
    "sticky": {True: (179, 148, 89), False: (128, 84, 0)},
    "": {True: (222, 222, 222), False: (255, 255, 255)}
}
# for saving
# block type:
#  dictionary of option type:
#    string-to-number type:
#      (list)
#      tuple: (name: str, map: list[strings])
#    number type:
#      (list)
#      tuple: (name: str, max value: int, min value: int, optional: bool, [multiplier]) - does not exist value is 1 more than max value
#    string type:
#      (list)
#      tuple: (name: str, [dependent name]: str/None, [dependent value]: Any)
SAVE_CODE = {
    "4": {
        "jump": {
            "number": [
                ("grav_locked", 1, 0, False),
                ("rotation", 3, 0, False)
            ],
        },
        "gravity": {
            "string_to_number": [
                ("type", ["direction", "set"])
            ],
            "number": [
                ("grav_locked", 1, 0, True),
                ("rotation", 3, 0, True),
                ("mode", 4, 0, True),
                ("value", 2.5, 0, True, 4)
            ]
        },
        "easter egg": {
            "string_to_number": [
                ("type", ["level", "achievement", "skin"])
            ],
            "string": [
                ("level", "type", "level"),
                ("achievement", "type", "achievement"),
                ("skin", "type", "skin")
            ]
        },
        "repel": {
            "number": [
                ("mode", 1, 0, False)
            ]
        },
        "activator": {
            "number": [
                ("delay", 24.75, 0, False, 4),
                ("grav_locked", 1, 0, False),
                ("rotation", 3, 0, False)
            ]
        },
        "msg": {
            "string": [
                ("text", None)
            ]
        }
    }
}

# for updating to current standards
ADDED_DEFAULT_UPDATE_BLOCK_ATTRIBUTES = {
    4: {"easter egg": {"type": "level"}}
}

# for file writing and reading of player data
PATH = ""
NAME = "player_data"

# for setting up player data with correct level list
# noinspection IncorrectFormatting
LEVEL_LIST = ("Baby Crawl", "Jump!", "Leap", "Danger!", "The Needle", "Gravity!", "Double Jump", "I Believe I can Fly", "Barriers", "Tap and Tap Again", "Sliding", "Hot Feet", "Gravity Collider", "Loop de loop", "Weird Jump", "Flip Flop", "The End...")
