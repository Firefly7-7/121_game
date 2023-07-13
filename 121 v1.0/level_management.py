"""
contains class for level data management.  Importing, exporting, saving, etc.
"""

from level_data import Level
from block_data import *
from typing import Union
from os.path import exists
from math import floor, ceil
from copy import deepcopy
from constants import VERSION, ADDED_DEFAULT_UPDATE_BLOCK_ATTRIBUTES, LETTER_CODES, BLOCKS, BARRIERS, SAVE_CODE, SavingFieldGroups, FieldType
import traceback


def make_blank_level() -> Level:
    """
    creates empty level
    :return: constructed level
    """
    return Level(
        False,
        "New Level",
        (0, -1.0),
        {},
        [],
        [(1, 1)],
    )


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
                if isinstance(blocks[coordinates].other, tuple):
                    blocks[coordinates].other = {}
                blocks[coordinates].other["link"] = i
            else:
                blocks[coordinates] = Block(
                    "",
                    [],
                    {"link": i}
                )
    players = [(x * 30 + 15, y * 30 + 15) for x, y in level.player_starts]
    return level.dimensions, level.gravity, blocks, links, players


def unpack_level(level_name: str, custom: int, easter_egg: bool = False) -> Union[Level, None, Exception]:
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
    name = f"{prepend}{level_name}.txt"
    if exists(name):
        with open(name, "r", encoding="utf-8") as file:
            data = file.read()
        return decode_safety_wrap(data)
    return None


def update_level(level_data: Level) -> None:
    """
    updates a level to current version to prevent errors
    :param level_data: data to update
    :return: None, does it in place
    """
    for version in range(level_data.version + 1, VERSION + 1):
        if version not in ADDED_DEFAULT_UPDATE_BLOCK_ATTRIBUTES:
            continue
        for block in level_data.blocks.values():
            if block.type in ADDED_DEFAULT_UPDATE_BLOCK_ATTRIBUTES[version]:
                block.other.update(ADDED_DEFAULT_UPDATE_BLOCK_ATTRIBUTES[version][block.type])


def save_level(level: Level) -> None:
    """
    saves a level to txt file
    :param level: level data
    :return: None
    """
    prepend = "custom_levels/"
    name = f"{prepend}{level.name}.txt"
    with open(name, "w", encoding="utf-8") as file:
        file.write(encode_level_to_string(level))


def max_info_number_length(data: dict[str, list[tuple]]) -> int:
    """
    finds length of the required
    :param data: block entry in SAVE_CODE
    :return: length of maximum possible number
    """
    maximum = 1
    if SavingFieldGroups.string_to_number in data:
        for stn in data[SavingFieldGroups.string_to_number]:
            maximum *= len(stn[1])
    if SavingFieldGroups.number in data:
        for n in data[SavingFieldGroups.number]:
            times = 1
            if len(n) == 5:
                times = n[4]
            maximum *= (n[1] - n[2]) * times + 1 + n[3]
    length = 0
    while 100 ** length <= maximum:
        length += 1
    return length


def decode_safety_wrap(level_string: str) -> Union[Level, None, ValueError, Exception]:
    """
    decode level from string safety wrap.  If it errors, return None
    :param level_string: encoded level string
    :return: organized level object or None, if failed
    """
    # noinspection PyBroadException
    try:
        final_level = None
        for line in reversed(level_string.split("\n")):
            data = decode_level_from_string(line)
            if isinstance(data, Exception):
                return data
            update_level(data)
            data.next = final_level
            final_level = data
        return final_level
    except:
        traceback.print_exc()
        # print("Errored")
        return ValueError("Level string errored in decode.")


def decode_level_from_string(level_string: str, published: bool = True) -> Union[Level, TypeError, ValueError]:
    """
    decodes a level from a code string
    :param level_string: encoded level string
    :param published: if it was successfully published (previously assumed to be true)
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

    convert_constant = 1 if level_string[0] in "123" else 0

    def convert_from_b100(string: str) -> int:
        """
        converts string from given b100 to b10
        :param string: b100 string
        :return: number in b10
        """
        b100 = 0
        for rep3 in range(len(string)):
            if string[rep3] not in letter_code:
                print(string[rep3], convert_constant, level_string.index(string[rep3]))
                print(level_string)
            b100 += (letter_code.index(string[rep3]) - convert_constant) * 100 ** rep3
        return b100

    letter_code = LETTER_CODES.get(level_string[0], "Whoops, what's going on here?")
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
                    players.append(((coord - 1) % x + 1, ceil(coord / x)))
                else:
                    if typ in ["gravity", "jump"]:
                        i4 += 1
                        if typ == "jump":
                            attributes[PointedBlock.grav_locked] = letter_code.index(block[i4])
                            i4 += 1
                            attributes[PointedBlock.rotation] = (4 - letter_code.index(block[i4])) % 4
                        elif typ == "gravity":
                            buffer = letter_code.index(block[i4])
                            i4 += 1
                            if buffer < 2:
                                attributes[Gravity.type] = "direction"
                                attributes[Gravity.grav_locked] = buffer
                                if i4 == len(block):
                                    attributes[Gravity.rotation] = 3
                                else:
                                    attributes[Gravity.rotation] = (2 - letter_code.index(block[i4])) % 4
                            else:
                                attributes[Gravity.type] = "set"
                                attributes[Gravity.mode] = buffer - 2
                                if i4 == len(block):
                                    attributes[Gravity.value] = 0
                                else:
                                    attributes[Gravity.value] = letter_code.index(block[i4]) * 0.25
                    elif typ == "repel":
                        i4 += 1
                        attributes[Repel.mode] = letter_code.index(block[i4])
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
            return ValueError("String for version 1 unpack had incorrect length indicator.")
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
                    attributes[PointedBlock.grav_locked] = letter_code.index(block_data[i2])
                    i2 += 1
                    attributes[PointedBlock.rotation] = (4 - letter_code.index(block_data[i2])) % 4
                elif typ == "gravity":
                    buffer = letter_code.index(block_data[i2])
                    i2 += 1
                    if buffer < 2:
                        attributes[Gravity.type] = "direction"
                        attributes[Gravity.grav_locked] = buffer
                        attributes[Gravity.rotation] = (2 - letter_code.index(block_data[i2])) % 4
                    else:
                        attributes[Gravity.type] = "set"
                        attributes[Gravity.mode] = buffer - 2
                        attributes[Gravity.value] = letter_code.index(block_data[i2]) * 0.25
            elif typ == "repel":
                if len(block_data) == 1:
                    attributes[Repel.mode] = 1
                    i2 += 0
                elif block_data[1] == letter_code[15]:
                    attributes[Repel.mode] = 0
                    i2 += 1
                else:
                    attributes[Repel.mode] = 1
            elif typ == "activator":
                attributes[Activator.delay] = letter_code.index(block_data[1]) / 4
                attributes[Activator.grav_locked] = 1 - floor(letter_code.index(block_data[2]) / 4)
                attributes[Activator.rotation] = (letter_code.index(block_data[2]) - 1) % 4
                i2 = 2
            elif typ == "msg":
                i2, length = decode_length_indicator(1, string=block_data)
                attributes[HasTextField.text] = ""
                for rep2 in range(length):
                    attributes[HasTextField.text] += block_data[i2]
                    i2 += 1
            elif typ == "easter egg":
                i2, length = decode_length_indicator(2, string=block_data)
                attributes[EasterEgg.type] = "level"
                attributes[EasterEgg.level] = ""
                for rep2 in range(length):
                    attributes[EasterEgg.level] += block_data[i2]
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
            published,
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
                    attributes[PointedBlock.grav_locked] = letter_code.index(block_data[i2])
                    i2 += 1
                    attributes[PointedBlock.rotation] = (4 - letter_code.index(block_data[2])) % 4
                elif typ == "gravity":
                    buffer = letter_code.index(block_data[i2])
                    i2 += 1
                    if buffer < 2:
                        attributes[Gravity.type] = "direction"
                        attributes[Gravity.grav_locked] = buffer
                        attributes[Gravity.rotation] = (2 - letter_code.index(block_data[2])) % 4
                    else:
                        attributes[Gravity.type] = "set"
                        attributes[Gravity.mode] = buffer - 2
                        attributes[Gravity.value] = letter_code.index(block_data[i2]) * 0.25
            elif typ == "repel":
                # print(len(block_data))
                if len(block_data) == 1:
                    attributes[Repel.mode] = 1
                    i2 += 0
                elif block_data[1] == letter_code[15]:
                    attributes[Repel.mode] = 0
                    i2 += 1
                else:
                    attributes[Repel.mode] = 1
            elif typ == "activator":
                attributes[Activator.delay] = letter_code.index(block_data[1]) / 4
                attributes[Activator.grav_locked] = 1 - floor(letter_code.index(block_data[2]) / 4)
                attributes[Activator.rotation] = (1 - letter_code.index(block_data[2])) % 4
                i2 = 2
            elif typ == "msg":
                i2, length = decode_length_indicator(1, string=block_data)
                attributes[HasTextField.text] = ""
                for rep2 in range(length):
                    attributes[HasTextField.text] += block_data[i2]
                    i2 += 1
                i2 -= 1
            elif typ == "easter egg":
                i2, length = decode_length_indicator(2, string=block_data)
                attributes[EasterEgg.type] = "level"
                attributes[EasterEgg.level] = ""
                for rep2 in range(length):
                    attributes[EasterEgg.level] += block_data[i2]
                    i2 += 1
            # print(typ)
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
            published,
            level_name,
            (gravity_angle, gravity_strength),
            blocks,
            links,
            players,
            (x, y),
            3
        )
    elif level_string[0] == "4":
        save_code = SAVE_CODE["4"]
        i1 = 3 + letter_code.index(level_string[1])
        # gets level dimensions
        x = letter_code.index(level_string[i1])
        y = letter_code.index(level_string[i1 + 1])
        level = Level(
            published,
            level_string[2:i1],
            (letter_code.index(level_string[i1 + 2]),
             letter_code.index(level_string[i1 + 3]) * -0.25),
            {},
            [],
            [],
            (x, y),
            4
        )
        # print(level.name, len(level_string), level.gravity)  # correct
        # print(x, y)  # correct
        players = letter_code.index(level_string[i1 + 4])
        # print(players)  # correct
        i1 += 5
        for p in range(players):
            level.player_starts.append((letter_code.index(level_string[i1]), letter_code.index(level_string[i1 + 1])))
            i1 += 2
        # print(convert_from_b100(level_string[i1:i1 + 2]))  # correct... I think
        for i2 in range(convert_from_b100(level_string[i1:i1 + 2])):
            block = Block(
                BLOCKS[letter_code.index(level_string[i1 + 2])],
                [],
                {}
            )
            # print(block.type, letter_code.index(level_string[i1 + 2]), level_string[i1 + 2], i1 + 2)
            i1 += 3
            for i3 in range(letter_code.index(level_string[i1])):
                i1 += 2
                # print(letter_code.index(level_string[i1 - 1]))
                barrier_number = letter_code.index(level_string[i1])
                # print(level_string[i1])
                # print(barrier_number % 32)
                block.barriers.append((
                    BARRIERS[letter_code.index(level_string[i1 - 1])],
                    barrier_number % 2 == 1,
                    (
                        barrier_number // 2 % 2 == 1,
                        barrier_number // 4 % 2 == 1,
                        barrier_number // 8 % 2 == 1,
                        barrier_number // 16 % 2 == 1
                    )
                ))
            # print(block.barriers)
            attributes = list()
            if block.type in save_code:
                length = max_info_number_length(save_code[block.type])
                if length > 0:  # check to make sure any of the following is necessary
                    # print("Has attributes.")
                    if SavingFieldGroups.string_to_number in save_code[block.type]:
                        for stn in save_code[block.type][SavingFieldGroups.string_to_number]:  # loops through string to number types
                            attributes.append(len(stn[1]))
                    if SavingFieldGroups.number in save_code[block.type]:
                        for n in save_code[block.type][SavingFieldGroups.number]:
                            times = 1
                            if len(n) == 5:
                                times = n[4]
                            attributes.append((n[1] - n[2]) * times + 1 + n[3])
                        del times
                    # print(f"Numerical attributes on {block.type}")
                    # print(f"Numerical attributes length: {length}")
                    i1 += 1
                    other_value = convert_from_b100(level_string[i1:i1 + length])
                    i1 += length - 1
                    # print(letter_code.index(level_string[i1 - 1]), [letter_code.index(char) for char in level_string[i1 - 5:]])
                    cumulative = 1
                    i4 = -1
                    if SavingFieldGroups.string_to_number in save_code[block.type]:
                        for stn in save_code[block.type][SavingFieldGroups.string_to_number]:  # loops through string to number types
                            i4 += 1
                            block.other[stn[0]] = stn[1][int(other_value // cumulative) % attributes[i4]]
                            cumulative *= attributes[i4]
                    if SavingFieldGroups.number in save_code[block.type]:
                        for n in save_code[block.type][SavingFieldGroups.number]:
                            i4 += 1
                            if len(n) == 5:
                                if not n[3] or other_value // cumulative % attributes[i4] != attributes[i4] - 1:
                                    block.other[n[0]] = (int(other_value // cumulative) % attributes[i4]) / n[4] + n[2]
                            else:
                                if not n[3] or other_value // cumulative % attributes[i4] != attributes[i4] - 1:
                                    block.other[n[0]] = (int(other_value // cumulative) % attributes[i4]) + n[2]
                            cumulative *= attributes[i4]
                if SavingFieldGroups.string in save_code[block.type]:
                    # print("retrieving string fields")
                    for s in save_code[block.type][SavingFieldGroups.string]:
                        if s[1] is not None and block.other[s[1]] != s[2]:
                            # print("text field continued")
                            continue
                        i1 += 1
                        # print(i1, level_string[i1:i1 + 2], convert_from_b100(level_string[i1:i1 + 2]))
                        block.other[s[0]] = level_string[i1 + 2: i1 + convert_from_b100(level_string[i1:i1 + 2]) + 2]
                        i1 += convert_from_b100(level_string[i1:i1 + 2])
                    i1 += 1
            i1 += 1
            # print(block.type, block.other)
            # print("Number of blocks:", convert_from_b100(level_string[i1:i1 + 2:1]) + 1)
            # print("Number of blocks (shift -1):", convert_from_b100(level_string[i1-1:i1 + 1:1]) + 1)
            # print("Number of blocks (shift +1):", convert_from_b100(level_string[i1+1:i1 + 3:1]) + 1)
            for i5 in range(convert_from_b100(level_string[i1:i1 + 2:1])):
                i1 += 2
                # print(level_string[i1], level_string[i1 + 1])
                level.blocks[(letter_code.index(level_string[i1]), letter_code.index(level_string[i1 + 1]))] = deepcopy(
                    block
                )
        i1 += 2
        # print(letter_code.index(level_string[i1]), i1 == len(level_string) - 1)
        for i5 in range(letter_code.index(level_string[i1])):
            level.links.append([])
            i1 += 1
            for i6 in range(letter_code.index(level_string[i1])):
                i1 += 2
                level.links[-1].append((letter_code.index(level_string[i1 - 1]), letter_code.index(level_string[i1])))
        # if (10, 0) in level.blocks:
        #     level.blocks[(1, 1)] = level.blocks.pop((10, 0))
        # print(level.blocks.keys())
        return level
    else:
        return TypeError("Level code does not start with a version indicator.")


# noinspection IncorrectFormatting
def encode_level_to_string(level_data: Level) -> str:
    """
    encodes a level to a shareable string
    :param level_data: level data object
    :return: encoded string
    """

    i = 0
    while i < len(level_data.links):
        if not level_data.links[i]:
            del level_data.links[i]
        else:
            i += 1

    def convert_to_b100(num: int, required_length: int = None) -> str:
        """
        converts to b100 with letter_code
        :param num: integer to convert
        :param required_length: length the number needs to be for code to work
        :return: string representation
        """
        digit = 1
        string = ""
        while num >= digit:
            string += letter_code[num // digit % 100]
            digit *= 100  # look, misnomer, k?  But means the same thing and made the first part easier
        if required_length is None:
            res = string
        elif len(string) > required_length:
            raise OverflowError(
                f"b100 conversion exceeded max length ({required_length}, {100 ** required_length - 1})"
            )
        else:
            res = string + letter_code[0] * (required_length - len(string))
            # print(len(res), required_length)
        return res[::1]

    level_string = "4"  # version indicator
    letter_code = LETTER_CODES[level_string]
    save_code = SAVE_CODE.get(level_string, {})
    level_string += letter_code[len(level_data.name) - 1] + level_data.name  # saves level name
    level_string += letter_code[level_data.dimensions[0]] + letter_code[level_data.dimensions[1]]  # saves level dimensions
    level_string += letter_code[level_data.gravity[0]] + letter_code[int(level_data.gravity[1] * -4)]  # saves gravity info
    level_string += letter_code[len(level_data.player_starts)]  # indicator for # of players
    for player in level_data.player_starts:
        level_string += letter_code[player[0]] + letter_code[player[1]]  # saves indidual player starts
    block_saves = dict()
    for coordinates, block in level_data.blocks.items():  # loops through block items in block save, makes save code
        if block.type == "" and block.barriers == []:
            continue
        specific_save = ""
        specific_save += letter_code[BLOCKS.index(block.type)]  # adds type indicator to specific save
        specific_save += letter_code[len(block.barriers)]  # adds indicator for number of barriers
        for barrier in block.barriers:  # adds barriers to the specific save
            specific_save += letter_code[BARRIERS.index(barrier[0])]
            specific_save += letter_code[barrier[1] + barrier[2][0] * 2 + barrier[2][1] * 4 + barrier[2][2] * 8 + barrier[2][3] * 16]
        attributes = list()  # format: [multiplicatory, value]
        if block.type in save_code:
            length = max_info_number_length(save_code[block.type])
            if length > 0:  # checks to make sure number is necessary
                if SavingFieldGroups.string_to_number in save_code[block.type]:
                    for stn in save_code[block.type][SavingFieldGroups.string_to_number]:  # loops through string to number types
                        # noinspection PyTypeChecker,PyUnresolvedReferences
                        attributes.append((len(stn[1]), stn[1].index(block.other[stn[0]])))
                if SavingFieldGroups.number in save_code[block.type]:
                    for n in save_code[block.type][SavingFieldGroups.number]:
                        times = 1
                        if len(n) == 5:
                            times = n[4]
                        # noinspection PyUnresolvedReferences
                        mult = (n[1] - n[2]) * times + 1 + n[3]
                        if n[0] in block.other:
                            attributes.append((mult, (block.other[n[0]] - n[2]) * times))
                        else:
                            attributes.append((mult, (mult - 1)))
                    del mult, times
                additive = 0
                cumulative = 1
                for mult, val in attributes:  # loops through attributes list with multiplicatory property and adds together, creating custom base number
                    additive += cumulative * val
                    cumulative *= mult
                # print(block.type, additive)
                specific_save += convert_to_b100(int(additive), length)
            if SavingFieldGroups.string in save_code[block.type]:
                for s in save_code[block.type][SavingFieldGroups.string]:
                    # noinspection PyTypeChecker
                    if s[1] is None:
                        specific_save += convert_to_b100(len(block.other[s[0]]), 2) + block.other[s[0]]
                    elif block.other[s[1]] == s[2]:
                        specific_save += convert_to_b100(len(block.other[s[0]]), 2) + block.other[s[0]]
        if specific_save in block_saves:  # check for duplicates
            block_saves[specific_save].append(coordinates)
        else:
            block_saves[specific_save] = [coordinates]  # add for multiple
    level_string += convert_to_b100(len(block_saves), 2)  # number of unique block saves
    for block_save, coordinates in block_saves.items():  # goes through block save and coordinate lists
        # print(BLOCKS[letter_code.index(block_save[0])], len(coordinates))
        level_string += block_save  # adds block save code to string
        level_string += convert_to_b100(len(coordinates), 2)  # indicator for how many blocks
        # print(convert_to_b100(len(coordinates), 2))
        for coordinate in coordinates:  # loops and adds coordinates
            level_string += letter_code[coordinate[0]] + letter_code[coordinate[1]]
    level_string += letter_code[len(level_data.links)]  # adds indicator for number of types of links
    # print(len(level_data.links))
    for link_data in level_data.links:  # loops through types of links
        level_string += letter_code[len(link_data)]  # indicator for number of specific type of link
        for link in link_data:  # loops through and adds link coordinates
            level_string += letter_code[link[0]] + letter_code[link[1]]
    if level_data.next is None:
        return level_string
    else:
        return level_string + "\n" + encode_level_to_string(level_data.next)