"""
sets constants for the program
"""
import pygame
from safe_paths import safe_listdir
from skin_management import decode_skin, Skin
from dataclasses import dataclass
from typing import Union, Any
from enum import Enum
from block_data import Blocks, BlockType

# for options key change
# noinspection IncorrectFormatting
KEY_CONSTANTS: tuple[int, ...] = (pygame.K_BACKSPACE, pygame.K_TAB, pygame.K_CLEAR, pygame.K_RETURN, pygame.K_PAUSE, pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_EXCLAIM, pygame.K_QUOTEDBL, pygame.K_HASH, pygame.K_DOLLAR, pygame.K_AMPERSAND, pygame.K_QUOTE, pygame.K_LEFTPAREN, pygame.K_RIGHTPAREN, pygame.K_ASTERISK, pygame.K_PLUS, pygame.K_COMMA, pygame.K_MINUS, pygame.K_PERIOD, pygame.K_SLASH, pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_COLON, pygame.K_SEMICOLON, pygame.K_LESS, pygame.K_EQUALS, pygame.K_GREATER, pygame.K_QUESTION, pygame.K_AT, pygame.K_LEFTBRACKET, pygame.K_BACKSLASH, pygame.K_RIGHTBRACKET, pygame.K_CARET, pygame.K_UNDERSCORE, pygame.K_BACKQUOTE, pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z, pygame.K_DELETE, pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9, pygame.K_KP_PERIOD, pygame.K_KP_DIVIDE, pygame.K_KP_MULTIPLY, pygame.K_KP_MINUS, pygame.K_KP_PLUS, pygame.K_KP_ENTER, pygame.K_KP_EQUALS, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_INSERT, pygame.K_HOME, pygame.K_END, pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6, pygame.K_F7, pygame.K_F8, pygame.K_F9, pygame.K_F10, pygame.K_F11, pygame.K_F12, pygame.K_F13, pygame.K_F14, pygame.K_F15, pygame.K_NUMLOCK, pygame.K_CAPSLOCK, pygame.K_SCROLLOCK, pygame.K_RSHIFT, pygame.K_LSHIFT, pygame.K_RCTRL, pygame.K_LCTRL, pygame.K_RALT, pygame.K_LALT, pygame.K_RMETA, pygame.K_LMETA, pygame.K_LSUPER, pygame.K_RSUPER, pygame.K_MODE, pygame.K_HELP, pygame.K_PRINT, pygame.K_SYSREQ, pygame.K_BREAK, pygame.K_MENU, pygame.K_POWER, pygame.K_EURO, pygame.K_AC_BACK)

# for level and player data saving (change... I think?  Sometime.)
VERSION: int = 5

# for level saving, new code every update (probably use randomizer on previous one)
# noinspection SpellCheckingInspection
LETTER_CODES: dict[str, str] = {
    "1": "1234567890qwertyuiopasdfghjklzxcvbnm`-=[]\;',./~!@#$%^&*_+{}|:\"<>?←↑→↓↔↖↗↘↙↚↛↜↝↞↟↠↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇋⇊⇉⇈⇇",
    "2": "1234567890qwertyuiopasdfghjklzxcvbnm`-=[]\;',./~!()\"#$%^&*_+{}|:<>?←↑→↓↔↖↗↘↙↚↛↜↝↞↟↠↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇋⇊⇉⇈⇇",
    "3": "n|tao↯q↛x↠p↣0+k_>5)↬↔fv↝c6y%↢↰7w<(↪gh↙su8i'9m↨}[↖↭`↥?↫↚*2↧↲jl↞eb↑\\r↟↮↦=3↤/-]↗$z\",;↩14!←:^{~.↱d→↜#↓&↘",
    "4": "1234567890-=qwertyuiop[]asdfghjkàl;’zxcvbnm,./!@#$%^&()+QWERTYUIOP{}|ASDFGHJKL:ZXCVBNM<?úíóáéç:â€èìùòÀÈÙÌÒÁÉÚÍÓÄËÏÜÖêûîôÂÊÛÎÔ",
    "5": "1234567890=qwertyuiop[]asdfghjkàl;’zxcvbnm,./!@#$%^&()+QWERTYUIOP{}|ASDFGHJKL:ZXCVBNM<?úíóáéç:â€èìùòÀÈÙÌÒÁÉÚÍÓÄËÏÜÖêûîôÂÊÛÎÔ"
}

# noinspection IncorrectFormatting
DEFAULT_SKINS: dict[str, Skin] = {
    "Default": decode_skin("Default,0,ffffff,rect/-1+-1*41+41/6/1/000000"),
    "Gravity": decode_skin("Gravity,0,ff008a,rect/-1+-1*41+41/4/1/000000_lines/19.5+10*19.5+30/6/0/000000_lines/10+25*19.5+30*29+25/6/0/000000"),
    "Hard Mode": decode_skin("Hard Mode,1,ffffff00,"),
    "Pride": decode_skin("Pride,0,ffffff,lines/0+2*40+2/7/0/e40203_lines/0+9*40+9/7/0/ff8b00_lines/0+16*40+16/7/0/feed00_lines/0+23*40+23/7/0/008026_lines/0+30*40+30/7/0/004dff_lines/0+37*40+37/7/0/750686"),
    "Lava": decode_skin("Lava,0,ff4d00,rect/-1+-1*41+41/4/1/000000"),
    "Mud": decode_skin("Mud,0,ab180a,rect/-1+-1*41+41/4/1/000000"),
    "Sticky": decode_skin("Sticky,0,cc2500,rect/-1+-1*41+41/4/1/000000"),
    "Bouncy": decode_skin("Bouncy,0,abcc4e,rect/-1+-1*41+41/4/1/000000"),
    "Ice": decode_skin("Ice,0,abdbe3,rect/-1+-1*41+41/4/1/000000"),
    "Goal": decode_skin("Goal,0,32bf0a,rect/-1+-1*41+41/4/1/000000"),
    "Activator": decode_skin("Activator,0,cc2929,rect/-1+-1*41+41/4/1/000000_lines/19.5+10*19.5+30/6/0/000000_lines/10+25*19.5+30*29+25/6/0/000000"),
    "Jump": decode_skin("Jump,0,80ff00,rect/-1+-1*41+41/4/1/000000_lines/19.5+10*19.5+30/6/0/000000_lines/10+25*19.5+30*29+25/6/0/000000")

}

EASTER_EGG_LEVELS: tuple[str, ...] = tuple(sorted(c_lvl[:-4] for c_lvl in safe_listdir("easter_eggs")))
SKIN_LIST: tuple[str, ...] = tuple(sorted(DEFAULT_SKINS.keys()))


@dataclass()
class Achievement:
    """
    holds achievement data
    """
    description: str
    skins: tuple[str] = ()
    easter_egg_levels: tuple[str] = ()
    nest_achievements: Union[list[tuple[str, dict[str, set]]], tuple[tuple[str, dict[str, set]]]] = ()


# noinspection IncorrectFormatting
BASE_ACHIEVEMENTS: dict[str, Achievement] = {
    "14233221": Achievement("Click the title placard 11 times to its final state.  Click again to view your achievements!"),
    "Victory!": Achievement(
        "Complete the game with any skin.",
        nest_achievements=[
            ("Victory! (Hard Mode)", {"skins": {"Hard Mode"}}),
            ("Victory! (Pride Mode)", {"skins": {"Pride"}})
        ]
    ),
    "Victory! (Hard Mode)": Achievement("Complete the final level with the Hard Mode skin."),
    "Victory! (Pride Mode)": Achievement("Complete the final level with the Pride skin."),
    # easter egg level achievements
    "Pride": Achievement(
        "Complete the Pride easter egg level.",
        skins=tuple(["Pride"])
    ),
    "Bouncy-Bounce": Achievement("Complete the Bouncy Castle easter egg level.  It's honestly such a shame this was completed before the bouncy block was added."),
    "Do a Barrel Roll": Achievement("Complete the Roll easter egg level"),
    # more or less meme acheivements
    "Large Graviton Collider": Achievement("Finish the Gravity Collider level."),
    # introduction achievements
    "Start": Achievement(
        "Complete the first level.",
        skins=tuple(["Goal"])
    ),  # goal
    "Jump": Achievement(
        "Finish the level introducing jump blocks.",
        skins=tuple(["Jump"])
    ),
    "Gravity": Achievement(
        "Finish the level introducing you to gravity blocks.",
        skins=tuple(["Gravity"])
    ),
    "The floor is lava!": Achievement(
        "Finish the level introducing you to lava blocks.",
        skins=tuple(["Lava"])
    ),
    "Timed Detonation": Achievement(
        "Finish the level introducing you to activator blocks.",
        skins=tuple(["Activator"])
    ),
    "Wings": Achievement(
        "Believe you can fly.",
    ),
    "Blocked": Achievement(
        "Finish the level introducing you to barriers.  Fun fact, one block can have up to 1.4x10^32 different combinations of barriers on it."
    ),
    "Repulsed": Achievement(
        "Finish the level introducing you to repulsion blocks."
    ),
    "Dirty": Achievement(
        "Finish the level introducing you to mud blocks.",
        skins=tuple(["Mud"])
    ),
    "Sticky": Achievement(
        "Finish the level introducing you to sticky blocks.",
        skins=tuple(["Sticky"])
    ),
    "Bouncy": Achievement(
        "Finish the level introducing you to bouncy blocks.",
        skins=tuple(["Bouncy"])
    ),
    "Brrr": Achievement(
        "Finish the level introducing you to ice blocks.",
        skins=tuple(["Ice"])
    ),
    "The floor is actually lava this time!": Achievement("Finish the level 'Hot Feet'."),
    "Remote Activation": Achievement("Finish the level introducing you to links."),
    "Around and Around": Achievement("Finish the level introducing you to rotator blocks."),
    "Breaking and Entering": Achievement("Finish the level introducing you to destroyer blocks."),
    "Multiply": Achievement("Play the level 'Two'!  Play the level 'Two'!"),
    "Quantum Tunneling": Achievement("Finish the level introducing you to portal blocks."),
    "Capitalism": Achievement("Collect coins, obviously to buy something with."),
    "This was always a TTRPG": Achievement("Finish the level introducing you to campaigns.")
}
achievement_list = tuple(sorted(list(BASE_ACHIEVEMENTS.keys())))

# for level saving.  DO NOT CHANGE ORDERING, only add to end
# noinspection IncorrectFormatting
BLOCKS: tuple[BlockType, ...] = (Blocks.player, Blocks.ground, Blocks.goal, Blocks.lava, Blocks.jump, Blocks.gravity, Blocks.easter_egg, Blocks.repel, Blocks.activator, Blocks.coin, Blocks.msg, Blocks.mud, Blocks.sticky, Blocks.bouncy, Blocks.air, Blocks.ice, Blocks.portal, Blocks.achievement_goal, Blocks.fragile_ground, Blocks.destroyer, Blocks.rotator, Blocks.error_block)
BARRIERS: tuple[BlockType, ...] = (Blocks.ground, Blocks.lava, Blocks.repel, Blocks.mud, Blocks.sticky, Blocks.air, Blocks.ice, Blocks.goal, Blocks.bouncy)

# noinspection IncorrectFormatting
WORKING_BLOCK_LIST: list[[BlockType]] = [Blocks.air, Blocks.ground, Blocks.goal, Blocks.lava, Blocks.ice, Blocks.mud, Blocks.sticky, Blocks.bouncy, Blocks.fragile_ground, Blocks.jump, Blocks.repel, Blocks.coin, Blocks.msg, Blocks.gravity, Blocks.portal, Blocks.activator, Blocks.destroyer]

# for construction
# noinspection IncorrectFormatting
BLOCK_LIST: list[BlockType] = [Blocks.delete, Blocks.ground, Blocks.goal, Blocks.lava, Blocks.ice, Blocks.mud, Blocks.sticky, Blocks.bouncy, Blocks.fragile_ground, Blocks.jump, Blocks.repel, Blocks.coin, Blocks.msg, Blocks.gravity, Blocks.portal, Blocks.activator, Blocks.destroyer, Blocks.rotator]
ADMIN_BLOCKS: list[BlockType] = [Blocks.easter_egg, Blocks.achievement_goal, Blocks.error_block]
# dict of block type string to list of field tuples
# entries into field list go as follows:
# 0: name of field
# 1: display name of field
# 2: type of field ["iterator", "boolean", "text", "list"]
# 3: default value for field
# 4: if a field needs to be in a state, then set of tuples of field name and then set of accepted values ex: (2, {"5", 3})
# 4 cont: if unconditional, then just empty set
# 5+ specific information required for that control
# iterator: lower bound, upper bound (not inclusive), step
# boolean: no more information required
# freeform_num: step
# text: lowest # of characters, highest # of characters
# list: a list/tuple of the options for the field
# -1: override displays (can be nonexistant).  tuple for boolean and iterator, dictionary for list
# noinspection IncorrectFormatting


class FieldType(Enum):
    """
    enumerator for field types
    """
    iterator = 0
    boolean = 1
    freeform_num = 2
    text = 3
    list = 4


BUTTON_COUNT: dict[FieldType, int] = {
    FieldType.boolean: 1,
    FieldType.iterator: 3,
    FieldType.list: 1,
    FieldType.text: 1,
    FieldType.freeform_num: 3
}
BLOCK_CONSTRUCTION: dict[BlockType, list[tuple[str, str, str, Any, set, Any, ...]]] = {
    Blocks.delete: [],
    Blocks.ground: [],
    Blocks.goal: [],
    Blocks.lava: [],
    Blocks.jump: [
        (Blocks.jump.grav_locked, "Gravity Locked", FieldType.boolean, False, {}),
        (Blocks.jump.rotation, "Rotation", FieldType.iterator, 0, {}, 0, 4, 1, ("Up", "Right", "Down", "Left"))
    ],
    Blocks.gravity: [
        (Blocks.gravity.type, "Type", FieldType.list, "direction", {}, ("direction", "set")),
        (Blocks.gravity.grav_locked, "Gravity Locked", FieldType.boolean, False, {(Blocks.gravity.type, frozenset({"direction"}))}),
        (Blocks.gravity.rotation, "Rotation", FieldType.iterator, 0, {(Blocks.gravity.type, frozenset({"direction"}))}, 0, 4, 1, ("Up", "Right", "Down", "Left")),
        (Blocks.gravity.mode, "Mode", FieldType.iterator, 0, {(Blocks.gravity.type, frozenset({"set"}))}, 0, 5, 1),
        (Blocks.gravity.variable_value, "Value", FieldType.iterator, 0, {(Blocks.gravity.type, frozenset({"set"}))}, 0, 2.75, 0.25)
    ],
    Blocks.easter_egg: [
        (Blocks.easter_egg.type, "Type", FieldType.list, "level", {}, ("level", "achievement", "skin")),
        (Blocks.easter_egg.level, "Level", FieldType.list, EASTER_EGG_LEVELS[0], {(Blocks.easter_egg.type, frozenset({"level"}))}, EASTER_EGG_LEVELS),
        (Blocks.easter_egg.achievement, "Achievement", FieldType.list, achievement_list[0], {(Blocks.easter_egg.type, frozenset({"achievement"}))}, achievement_list),
        (Blocks.easter_egg.skin, "Skin", FieldType.list, SKIN_LIST[0], {(Blocks.easter_egg.type, frozenset({"skin"}))}, SKIN_LIST)
    ],
    Blocks.achievement_goal: [
        (Blocks.achievement_goal.achievement, "Achievement", FieldType.list, achievement_list[0], {}, achievement_list),
    ],
    Blocks.repel: [
        (Blocks.repel.mode, "Mode", FieldType.boolean, False, {}, ("Linear", "Direct"))
    ],
    Blocks.activator: [
        (Blocks.activator.grav_locked, "Gravity Locked", FieldType.boolean, False, {}),
        (Blocks.activator.rotation, "Rotation", FieldType.iterator, 0, {}, 0, 4, 1, ("Up", "Right", "Down", "Left")),
        (Blocks.activator.delay, "Delay", FieldType.iterator, 0, {}, 0, 25, 0.25)
    ],
    Blocks.coin: [],
    Blocks.msg: [
        (Blocks.msg.text, "Message", FieldType.text, "Hello World!", {}, 0, 9999)
    ],
    Blocks.mud: [],
    Blocks.sticky: [],
    Blocks.bouncy: [],
    Blocks.ice: [],
    Blocks.portal: [
        (Blocks.portal.relative, "Relative Positioning", FieldType.iterator, 0, {}, 0, 2, 1, ("Screen", "Player", "Portal")),
        (Blocks.portal.x, "X", FieldType.iterator, 0, {}, -11, 12, 1),
        (Blocks.portal.y, "Y", FieldType.iterator, 0, {}, -11, 12, 1),
        (Blocks.portal.reflect_x, "Reflect X Momentum", FieldType.boolean, False, {}),
        (Blocks.portal.reflect_y, "Reflect Y Momentum", FieldType.boolean, False, {}),
        (Blocks.portal.rotation, "Rotate Momentum", FieldType.iterator, 0, {}, 0, 4, 1, ("No effect", "Clockwise", "Reverse", "Counterclockwise"))
    ],
    Blocks.fragile_ground: [
        (Blocks.fragile_ground.sturdiness, "Sturdiness", FieldType.iterator, 0, {}, 0, 31, 1),
        (Blocks.fragile_ground.remove_barriers, "Remove Barriers", FieldType.boolean, False, {}),
        (Blocks.fragile_ground.remove_link, "Remove Link", FieldType.boolean, False, {})
    ],
    Blocks.destroyer: [
        (Blocks.destroyer.rotation, "Direction", FieldType.iterator, 0, {}, 0, 4, 1, ("Up", "Right", "Down", "Left")),
        (Blocks.destroyer.grav_locked, "Gravity Locked", FieldType.boolean, False, {}),
        (Blocks.destroyer.destroy_link, "Destroy Link", FieldType.boolean, True, {}),
        (Blocks.destroyer.destroy_barriers, "Destroy Barriers", FieldType.iterator, 1, {}, 0, 3, 1, ("None", "All", "Top")),
        (Blocks.destroyer.destroy_block, "Destroy Block", FieldType.boolean, True, {}),
        (Blocks.destroyer.match_block, "Match Block", FieldType.list, False, {}, tuple([False] + WORKING_BLOCK_LIST), {False: "Don't check", **{block: block.name for block in WORKING_BLOCK_LIST}})
    ],
    Blocks.rotator: [
        (Blocks.rotator.rotation, "Direction", FieldType.iterator, 0, {}, 0, 4, 1, ("Up", "Right", "Down", "Left")),
        (Blocks.rotator.grav_locked, "Gravity Locked", FieldType.boolean, False, {}),
        (Blocks.rotator.mode, "Mode", FieldType.boolean, True, {}, ("Set Direction", "Rotate")),
        (Blocks.rotator.grav_account, "Account for Gravity", FieldType.boolean, False, {(Blocks.rotator.mode, tuple([False]))}),
        (Blocks.rotator.variable_value, "Amount", FieldType.iterator, 0, {}, 0, 4, 1, ("No Effect/Up", "Clockwise/Right", "Reverse/Down", "Counterclockwise/Left")),
        (Blocks.rotator.rotate_block, "Rotate Block", FieldType.boolean, True, {}),
        (Blocks.rotator.rotate_barriers, "Rotate Barriers", FieldType.boolean, True, {}),
    ],
    Blocks.error_block: []
}


# block type to tuple of color tuples, first color tuple is when doesn't change with gravity, second is when does
BARRIER_COLORS: dict[BlockType, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    Blocks.ground: ((0, 0, 0), (128, 128, 128)),
    Blocks.lava: ((255, 77, 0), (255, 168, 128)),
    Blocks.repel: ((255, 184, 0), (255, 219, 128)),
    Blocks.mud: ((102, 31, 0), (179, 104, 71)),
    Blocks.sticky: ((128, 84, 0), (179, 148, 89)),
    Blocks.air: ((230, 230, 245), (220, 220, 220)),
    Blocks.ice: ((48, 167, 205), (171, 219, 227)),
    Blocks.goal: ((50, 191, 0), (125, 200, 100)),
    Blocks.bouncy: ((171, 204, 78), (213, 229, 162))
}
# for saving
# block type:
#  dictionary of option type:
#    string-to-number type:
#      (list)
#      tuple: (name: enum member, map: list[strings])
#    freeform number type:
#      (list)
#      tuple: (name: enum member, step)
#    number type:
#      (list)
#      tuple: (name: enum member, max value: int, min value: int, optional: bool, [multiplier]) - does not exist value is 1 more than max value
#    string type:
#      (list)
#      tuple: (name: enum member, [dependent name]: enum member/None, [dependent value]: Any)


class SavingFieldGroups(Enum):
    """
    enum for saving field groups
    """
    string_to_number = 0
    freeform_num = 3
    number = 1
    string = 2


SAVE_CODE: dict[str, dict[BlockType, dict[SavingFieldGroups, list[tuple[int, Any, ...]]]]] = {
    "4": {
        Blocks.jump: {
            SavingFieldGroups.number: [
                (Blocks.jump.grav_locked, 1, 0, False),
                (Blocks.jump.rotation, 3, 0, False)
            ],
        },
        Blocks.gravity: {
            SavingFieldGroups.string_to_number: [
                (Blocks.gravity.type, ["direction", "set"])
            ],
            SavingFieldGroups.number: [
                (Blocks.gravity.grav_locked, 1, 0, True),
                (Blocks.gravity.rotation, 3, 0, True),
                (Blocks.gravity.mode, 4, 0, True),
                (Blocks.gravity.variable_value, 2.5, 0, True, 4)
            ]
        },
        Blocks.easter_egg: {
            SavingFieldGroups.string_to_number: [
                (Blocks.easter_egg.type, ["level", "achievement", "skin"])
            ],
            SavingFieldGroups.string: [
                (Blocks.easter_egg.level, Blocks.easter_egg.type, "level"),
                (Blocks.easter_egg.achievement, Blocks.easter_egg.type, "achievement"),
                (Blocks.easter_egg.skin, Blocks.easter_egg.type, "skin")
            ]
        },
        Blocks.achievement_goal: {
            SavingFieldGroups.string: [
                (Blocks.achievement_goal.achievement, None)
            ]
        },
        Blocks.repel: {
            SavingFieldGroups.number: [
                (Blocks.repel.mode, 1, 0, False)
            ]
        },
        Blocks.activator: {
            SavingFieldGroups.number: [
                (Blocks.activator.delay, 24.75, 0, False, 4),
                (Blocks.activator.grav_locked, 1, 0, False),
                (Blocks.activator.rotation, 3, 0, False)
            ]
        },
        Blocks.msg: {
            SavingFieldGroups.string: [
                (Blocks.msg.text, None)
            ]
        },
        Blocks.portal: {
            SavingFieldGroups.number: [
                (Blocks.portal.relative, 1, 0, False),
                (Blocks.portal.x, 11, -11, False),
                (Blocks.portal.y, 11, -11, False),
                (Blocks.portal.reflect_x, 1, 0, False),
                (Blocks.portal.reflect_y, 1, 0, False),
                (Blocks.portal.rotation, 3, 0, True)
            ]
        },
        Blocks.fragile_ground: {
            SavingFieldGroups.number: [
                (Blocks.fragile_ground.sturdiness, 30, 0, False),
                (Blocks.fragile_ground.remove_barriers, 1, 0, False),
                (Blocks.fragile_ground.remove_link, 1, 0, False),
            ]
        },
        Blocks.destroyer: {
            SavingFieldGroups.string_to_number: [
                (Blocks.destroyer.match_block, [False, Blocks.air, Blocks.ground, Blocks.goal, Blocks.lava, Blocks.ice, Blocks.mud, Blocks.sticky, Blocks.bouncy, Blocks.fragile_ground, Blocks.jump, Blocks.repel, Blocks.coin, Blocks.msg, Blocks.gravity, Blocks.portal, Blocks.activator, Blocks.destroyer])
            ],
            SavingFieldGroups.number: [
                (Blocks.destroyer.grav_locked, 1, 0, False),
                (Blocks.destroyer.rotation, 3, 0, False),
                (Blocks.destroyer.destroy_link, 1, 0, False),
                (Blocks.destroyer.destroy_barriers, 2, 0, False),
                (Blocks.destroyer.destroy_block, 1, 0, False)
            ]
        },
        Blocks.rotator: {
            SavingFieldGroups.number: [
                (Blocks.rotator.rotation, 3, 0, False),
                (Blocks.rotator.grav_locked, 1, 0, False),
                (Blocks.rotator.mode, 1, 0, False),
                (Blocks.rotator.variable_value, 3, 0, False),
                (Blocks.rotator.rotate_block, 1, 0, False),
                (Blocks.rotator.rotate_barriers, 1, 0, False),
                (Blocks.rotator.grav_account, 1, 0, True)
            ]
        }
    },
    "5": {
        Blocks.portal: {
            SavingFieldGroups.number: [
                (Blocks.portal.relative, 2, 0, False),
                (Blocks.portal.x, 11, -11, False),
                (Blocks.portal.y, 11, -11, False),
                (Blocks.portal.reflect_x, 1, 0, False),
                (Blocks.portal.reflect_y, 1, 0, False),
                (Blocks.portal.rotation, 3, 0, True)
            ]
        },
        Blocks.destroyer: {
            SavingFieldGroups.string_to_number: [
                (Blocks.destroyer.match_block, [False] + WORKING_BLOCK_LIST)
            ],
            SavingFieldGroups.number: [
                (Blocks.destroyer.grav_locked, 1, 0, False),
                (Blocks.destroyer.rotation, 3, 0, False),
                (Blocks.destroyer.destroy_link, 1, 0, False),
                (Blocks.destroyer.destroy_barriers, 2, 0, False),
                (Blocks.destroyer.destroy_block, 1, 0, False)
            ]
        }
    }
}

# for updating to current standards
ADDED_DEFAULT_UPDATE_BLOCK_ATTRIBUTES: dict[int, dict[BlockType, dict[int, Any]]] = {
    4: {Blocks.easter_egg: {Blocks.easter_egg.type: "level"}}
}

# for file writing and reading of player data
PATH: str = ""
NAME: str = "player_data"

# for setting up player data with correct level list
# noinspection IncorrectFormatting
LEVEL_LIST: tuple[str, ...] = ("Baby Crawl", "Jump!", "Parkour", "Leap", "Hops", "Danger!", "Lava Pools", "The Needle", "Weaving", "Gravity!", "Around the World", "Double Jump", "20 Seconds Later", "I Believe I can Fly", "Across the World", "Repulsion", "Around the Core", "Barriers", "Wall Jump", "One Way or Another", "Tap and Tap Again", "Sliding", "Slip n Slide", "Hot Feet", "More Sliding", "Ice Shelves", "Air and Links", "Gravity Collider", "No Jumping for you!", "Linked Effect", "Boing", "High Stakes Bouncing", "Fragility", "Ice Climber", "Campaigns", "Loop de Loop", "Turning", "Turn Around", "Removal", "Destruction", "Two", "Weird Jump", "Currency", "Flip Flop", "FTL", "Wormholes", "Four", "The End...")

CONSTRUCTION_MENUS: tuple[str, ...] = ("Players", "Gravity", "Blocks", "Barriers", "Links")

print("Blocks:", len(BLOCKS))
print("Achievements:", len(BASE_ACHIEVEMENTS))
print("Levels:", len(LEVEL_LIST))
print("Easter egg levels:", len(EASTER_EGG_LEVELS))