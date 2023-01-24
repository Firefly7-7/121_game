"""
contains class for level data management.  Importing, exporting, saving, etc.
"""

import pickle
from level_data import Level
from block_data import Block
from typing import Union
from os.path import exists
from math import floor, ceil
from copy import deepcopy


def make_playable(
        level: Level
) -> tuple[
    tuple[int, int],  # dimensions
    tuple[int, float],  # gravity info
    dict[tuple[int, int], Block],  # block info
    list[list[tuple[int, int]]],  # link info
    list[tuple[int, int]]  # player starts
]:
    """
    from a level data, returns all data needed to play the level
    :param level: level object containing data
    :return: tuple of tuple of dimensions, gravity information, dictionary with block data, list of link data, list of player starts
    """
    blocks = deepcopy(level.blocks)
    links = deepcopy(level.links)
    for i, link_objects in enumerate(links):
        for coordinates in link_objects:
            if coordinates in blocks.keys():
                blocks[coordinates].other["link"] = i
            else:
                blocks[coordinates] = Block(
                    "",
                    [],
                    {"link": i}
                )
    players = [(x * 30 + 15, y * 30 + 15) for x, y in level.player_starts]
    return level.dimensions, level.gravity, blocks, links, players


def unpack_level(level_name: str, custom: int, easter_egg: bool = False) -> Union[Level, None]:
    """
    gets a level from a a pkl file
    :param level_name: string level name to get
    :param custom: if the level is a custom level
    :param easter_egg: if it's an easter egg
    :return: level object if such a level exists, otherwise none object
    """
    if custom == 0:
        if easter_egg:
            prepend = "easter_eggs/"
        else:
            prepend = "premade_levels/"
    else:
        prepend = "custom_levels/"
    name = f"{prepend}{level_name}.pkl"
    if exists(name):
        # print(f"File {name} exists.")
        with open(name, "rb") as file:
            return pickle.load(file)
    else:
        # print(f"File {name} does not exist.")
        return None


def save_level(level: Level) -> None:
    """
    saves a level to pkl file
    :param level: level data
    :return: None
    """
    prepend = "custom_levels/"
    name = f"{prepend}{level.name}.pkl"
    with open(name, "wb") as file:
        pickle.dump(level, file)


# noinspection SpellCheckingInspection
LETTER_CODES = {
    "1": "1234567890qwertyuiopasdfghjklzxcvbnm`-=[]\;',./~!@#$%^&*_+{}|:\"<>?←↑→↓↔↖↗↘↙↚↛↜↝↞↟↠↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇋⇊⇉⇈⇇",
    "2": "1234567890qwertyuiopasdfghjklzxcvbnm`-=[]\;',./~!()\"#$%^&*_+{}|:<>?←↑→↓↔↖↗↘↙↚↛↜↝↞↟↠↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇋⇊⇉⇈⇇",
    "3": "n|tao↯q↛x↠p↣0+k_>5)↬↔fv↝c6y%↢↰7w<(↪gh↙su8i'9m↨}[↖↭`↥?↫↚*2↧↲jl↞eb↑\\r↟↮↦=3↤/-]↗$z\",;↩14!←:^{~.↱d→↜#↓&↘"
}
# noinspection IncorrectFormatting
BLOCKS = ("player", "ground", "goal", "lava", "jump", "gravity", "easter egg", "repel", "activator", "coin", "msg", "mud", "sticky", "bouncy")
BARRIERS = ("ground", "lava", "repel", "mud", "sticky")


def decode_safety_wrap(level_string: str) -> Union[Level, None]:
    """
    decode level from string safety wrap.  If it errors, return None
    :param level_string: encoded level string
    :return: organized level object or None, if failed
    """
    return decode_level_from_string(level_string)
    # noinspection PyBroadException
    try:
        return decode_level_from_string(level_string)
    except:
        print("Errored")
        return None


def decode_level_from_string(level_string: str) -> Union[Level, None]:
    """
    decodes a level from a code string
    :param level_string: encoded level string
    :return: a fully organized level object
    """

    # print(level_string)

    def decode_length_indicator(start: int, prev: int = 1, string: str = level_string) -> tuple[int, int]:
        """
        decode length indicator for decoding level string
        :param start: start index
        :param prev: previous info
        :param string: string to decode in
        :return: new pointer, length found
        """
        point = start
        length_indicator = 0
        if string[point] == letter_code[0]:
            point += 1
            for rep3 in range(prev):
                length_indicator = 100 * length_indicator + letter_code.index(string[point])
                point += 1
            return decode_length_indicator(point, length_indicator, string)
        else:
            for rep3 in range(prev):
                length_indicator = 100 * length_indicator + letter_code.index(string[point])
                point += 1
            return point, length_indicator

    def convert_from_b100(string: str) -> int:
        """
        converts string from given b100 to b10
        :param string: b100 string
        :return: number in b10
        """
        b100 = 0
        for rep3 in range(len(string)):
            b100 += (letter_code.index(string[rep3]) - 1) * 10 ** (rep3 * 2)
        return b100

    letter_code = LETTER_CODES[level_string[0]]
    if level_string[0] == "1":
        i1 = 0
        storage = 0
        while storage + i1 + 2 <= len(level_string):
            i1 += 1
            storage += letter_code.index(level_string[-i1]) * 10 ** ((i1 - 1) * 2)
        if storage + i1 + 1 == len(level_string):
            # print("Version 1 primary check passed")
            level_name = ""
            i2 = 1
            while level_string[i2] != '"':
                level_name += level_string[i2]
                i2 += 1
            i2 += 1
            gravity_angle = floor(letter_code.index(level_string[i2]) / 11)
            gravity_strength = (letter_code.index(level_string[i2]) % 11) / -4
            i2 += 1
            x = letter_code.index(level_string[i2]) + 1
            i2 += 1
            y = letter_code.index(level_string[i2]) + 1
            block_codes = list()
            for rep in range(storage - i2):
                i2 += 1
                if level_string[i2] == "(":
                    block_codes.insert(0, "")
                else:
                    block_codes[0] += level_string[i2]
            block_data = dict()
            players = list()
            for block in block_codes:
                coord = 0
                i4 = 0
                for rep in range(ceil(len(str(x * y)) / 2)):
                    i4 += 1
                    coord += letter_code.index(block[i4 - 1]) * 10 ** ((i4 - 1) * 2)
                # i4 += 1
                typ = BLOCKS[letter_code.index(block[i4])]
                attributes = dict()
                if typ == "player":
                    players.append(((coord - 1) % x + 1, 13 - ceil(coord / x)))
                else:
                    if typ in ["gravity", "jump"]:
                        i4 += 1
                        if typ == "jump":
                            attributes["grav_locked"] = letter_code.index(block[i4])
                            i4 += 1
                            attributes["rotation"] = (4 - letter_code.index(block[i4])) % 4
                        elif typ == "gravity":
                            buffer = letter_code.index(block[i4])
                            i4 += 1
                            if buffer < 2:
                                attributes["type"] = "direction"
                                attributes["grav_locked"] = buffer
                                if i4 == len(block):
                                    attributes["rotation"] = 3
                                else:
                                    attributes["rotation"] = (2 - letter_code.index(block[i4])) % 4
                            else:
                                attributes["type"] = "set"
                                attributes["mode"] = buffer - 2
                                if i4 == len(block):
                                    attributes["value"] = 0
                                else:
                                    attributes["value"] = letter_code.index(block[i4]) * 0.25
                    elif typ == "repel":
                        i4 += 1
                        attributes["mode"] = letter_code.index(block[i4])
                    block_data[((coord - 1) % x + 1, ceil(coord / x))] = Block(
                        typ,
                        list(),
                        attributes
                    )
            # print(level_name, block_data)
            return Level(
                True,
                level_name,
                (gravity_angle, gravity_strength),
                block_data,
                list(),
                players,
                (x, y),
                1
            )
        else:
            print("Fail on version 1 check")
            return None
    elif level_string[0] == "2":
        # print(level_string)
        level_name = ""
        i1 = 2
        for rep in range(letter_code.index(level_string[1]) + 1):
            level_name += level_string[i1]
            i1 += 1
        # print(level_name)
        gravity_angle = floor(letter_code.index(level_string[i1]) / 11)
        gravity_strength = (letter_code.index(level_string[i1]) % 11) / -4
        # print(gravity_angle, gravity_strength)
        i1 += 1
        x = letter_code.index(level_string[i1]) + 1
        i1 += 1
        y = letter_code.index(level_string[i1]) + 1
        i1 += 1
        players = list()
        players.append((letter_code.index(level_string[i1]) + 1, letter_code.index(level_string[i1 + 1]) + 1))
        i1 += 2
        i1, length = decode_length_indicator(i1)
        block_types = ""
        for rep in range(length):
            block_types += level_string[i1]
            i1 += 1
        blocks = dict()
        for rep in range(convert_from_b100(block_types) + 1):
            i1, length = decode_length_indicator(i1)
            block_data = ""
            for rep2 in range(length):
                block_data += level_string[i1]
                i1 += 1
            # begin specific load
            barriers = list()
            attributes = dict()
            if block_data[0] == letter_code[99]:
                typ = ""
            else:
                typ = BLOCKS[letter_code.index(block_data[0])]
            i2 = 0
            if typ in ["gravity", "jump"]:
                i2 += 1
                if typ == "jump":
                    attributes["grav_locked"] = letter_code.index(block_data[i2])
                    i2 += 1
                    attributes["rotation"] = (4 - letter_code.index(block_data[i2])) % 4
                elif typ == "gravity":
                    buffer = letter_code.index(block_data[i2])
                    i2 += 1
                    if buffer < 2:
                        attributes["type"] = "direction"
                        attributes["grav_locked"] = buffer
                        attributes["rotation"] = (2 - letter_code.index(block_data[i2])) % 4
                    else:
                        attributes["type"] = "set"
                        attributes["mode"] = buffer - 2
                        attributes["value"] = letter_code.index(block_data[i2]) * 0.25
            elif typ == "repel":
                attributes["mode"] = letter_code.index(level_string[i2])
            elif typ == "activator":
                attributes["delay"] = letter_code.index(block_data[1]) / 4
                attributes["grav_locked"] = 1 - floor(letter_code.index(block_data[2]) / 4)
                attributes["rotation"] = (letter_code.index(block_data[2]) - 1) % 4
                i2 = 2
            elif typ == "msg":
                i2, length = decode_length_indicator(1, string=block_data)
                attributes["text"] = ""
                for rep2 in range(length):
                    attributes["text"] += block_data[i2]
                    i2 += 1
            elif typ == "easter egg":
                i2, length = decode_length_indicator(2, string=block_data)
                attributes["level"] = ""
                for rep2 in range(length):
                    attributes["level"] += block_data[i2]
                    i2 += 1
            for rep2 in range(len(block_data) - i2 - 1):
                i2 += 1
                dat = (letter_code.index(block_data[i2]) + 1) % 16
                barriers.append((
                    BARRIERS[floor(letter_code.index(block_data[i2]) / 16) // 2],
                    (floor(letter_code.index(block_data[i2]) / 16)) % 2 == 1,
                    (floor(dat / 2) % 2 == 1, floor(dat / 4) % 2 == 1, floor(dat / 8) % 2 == 1, floor(dat / 1) % 2 == 1)
                ))
            # end specific load
            i1, length = decode_length_indicator(i1)
            for rep2 in range(floor(length / 2)):
                blocks[(letter_code.index(level_string[i1]) + 1, letter_code.index(level_string[i1 + 1]) + 1)] = Block(
                    typ,
                    barriers.copy(),
                    attributes.copy()
                )
                i1 += 2
        links = list()
        if i1 < len(level_string):
            reps = convert_from_b100(level_string[i1])
            i1 += 1
            for rep in range(reps):
                links.append(list())
                i1, length = decode_length_indicator(i1)
                for rep2 in range(round(length / 2)):
                    links[-1].append((
                        letter_code.index(level_string[i1]) + 1,
                        letter_code.index(level_string[i1 + 1]) + 1
                    ))
                    i1 += 2
        return Level(
            True,
            level_name,
            (gravity_angle, gravity_strength),
            blocks,
            links,
            players,
            (x, y),
            2
        )
    elif level_string[0] == "3":
        # print(level_string)
        level_name = ""
        i1 = 2
        for rep in range(letter_code.index(level_string[1]) + 1):
            level_name += level_string[i1]
            i1 += 1
        # print(level_name)
        gravity_angle = floor(letter_code.index(level_string[i1]) / 11)
        gravity_strength = (letter_code.index(level_string[i1]) % 11) / -4
        # print(gravity_angle, gravity_strength)
        i1 += 1
        x = letter_code.index(level_string[i1]) + 1
        i1 += 1
        y = letter_code.index(level_string[i1]) + 1
        # print(x, y)
        i1 += 1
        players = list()
        players.append((letter_code.index(level_string[i1]) + 1, letter_code.index(level_string[i1 + 1]) + 1))
        # print(players)
        i1 += 2
        i1, length = decode_length_indicator(i1)
        # print(i1, length)
        # issue is decoding length indicator for
        block_types = ""
        for rep in range(length):
            block_types += level_string[i1]
            i1 += 1
        blocks = dict()
        for rep in range(convert_from_b100(block_types) + 1):
            # print("rep", rep + 1, i1)
            i1, length = decode_length_indicator(i1)
            block_data = ""
            for rep2 in range(length):
                block_data += level_string[i1]
                i1 += 1
            # begin specific load
            # print(block_data)
            barriers = list()
            attributes = dict()
            if block_data[0] == letter_code[99]:
                typ = ""
            else:
                typ = BLOCKS[letter_code.index(block_data[0])]
                # print(block_data[0], letter_code.index(block_data[0]), typ)
            i2 = 0
            if typ in ["gravity", "jump"]:
                i2 += 1
                if typ == "jump":
                    attributes["grav_locked"] = letter_code.index(block_data[i2])
                    i2 += 1
                    attributes["rotation"] = (4 - letter_code.index(block_data[2])) % 4
                elif typ == "gravity":
                    buffer = letter_code.index(block_data[i2])
                    i2 += 1
                    if buffer < 2:
                        attributes["type"] = "direction"
                        attributes["grav_locked"] = buffer
                        attributes["rotation"] = (2 - letter_code.index(block_data[2])) % 4
                    else:
                        attributes["type"] = "set"
                        attributes["mode"] = buffer - 2
                        attributes["value"] = letter_code.index(block_data[i2]) * 0.25
            elif typ == "repel":
                if len(block_data) == 1:
                    attributes["mode"] = 1
                else:
                    i2 += 1
                    attributes["mode"] = 0
            elif typ == "activator":
                attributes["delay"] = letter_code.index(block_data[1]) / 4
                attributes["grav_locked"] = 1 - floor(letter_code.index(block_data[2]) / 4)
                attributes["rotation"] = (1 - letter_code.index(block_data[2])) % 4
                i2 = 3
            elif typ == "msg":
                i2, length = decode_length_indicator(1, string=block_data)
                attributes["text"] = ""
                for rep2 in range(length):
                    attributes["text"] += block_data[i2]
                    i2 += 1
            elif typ == "easter egg":
                i2, length = decode_length_indicator(2, string=block_data)
                attributes["level"] = ""
                for rep2 in range(length):
                    attributes["level"] += block_data[i2]
                    i2 += 1
            for rep2 in range(floor((len(block_data) - i2) / 2)):
                i2 += 2
                dat = letter_code.index(block_data[i2]) + 1
                barriers.append((
                    BARRIERS[letter_code.index(block_data[i2 - 1])],
                    (floor(letter_code.index(block_data[i2]) / 16)) % 2 == 1,
                    (
                        floor(dat / 4) % 2 == 1,
                        floor(dat / 8) % 2 == 1,
                        floor(dat / 1) % 2 == 1,
                        floor(dat / 2) % 2 == 1
                    )
                ))
            # end specific load
            # print(Block(
            #     typ,
            #     barriers.copy(),
            #     attributes.copy()
            # ))
            i1, length = decode_length_indicator(i1)
            for rep2 in range(floor(length / 2)):
                blocks[(letter_code.index(level_string[i1]) + 1, letter_code.index(level_string[i1 + 1]) + 1)] = Block(
                    typ,
                    barriers.copy(),
                    attributes.copy()
                )
                # print(letter_code.index(level_string[i1]) + 1, letter_code.index(level_string[i1 + 1]) + 1)
                i1 += 2
        links = list()
        if i1 < len(level_string):
            reps = convert_from_b100(level_string[i1])
            i1 += 1
            for rep in range(reps + 1):
                links.append(list())
                i1, length = decode_length_indicator(i1)
                for rep2 in range(round(length / 2)):
                    links[-1].append((
                        letter_code.index(level_string[i1]) + 1,
                        letter_code.index(level_string[i1 + 1]) + 1
                    ))
                    i1 += 2
        # print(links)
        return Level(
            True,
            level_name,
            (gravity_angle, gravity_strength),
            blocks,
            links,
            players,
            (x, y),
            3
        )
    else:
        return None