"""
contains class for level data management.  Importing, exporting, saving, etc.
"""

from level_data import Level, LevelWrap
from block_data import *
from typing import Union
from os.path import exists
from math import floor, ceil
from copy import deepcopy, copy
from constants import VERSION, ADDED_DEFAULT_UPDATE_BLOCK_ATTRIBUTES, LETTER_CODES, BLOCKS, BARRIERS, SAVE_CODE, SavingFieldGroups, FieldType
from safe_paths import getpath
import traceback


def make_blank_level() -> Level:
    """
    creates empty level
    :return: constructed level
    """
    return Level(
        "New Level",
        [0, -1.0],
        {},
        [],
        [(1, 1)],
        (6, 6)
    )


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
    name = getpath(f"{prepend}{level_name}.txt")
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


def save_level(level: LevelWrap) -> None:
    """
    saves a level to txt file
    :param level: level data
    :return: None
    """
    prepend = "custom_levels/"
    name = f"{prepend}{level.level_on.name}.txt"
    with open(name, "w", encoding="utf-8") as file:
        file.write(encode_level_to_string(level.level_on))


def max_info_number_length(data: dict[SavingFieldGroups, list[tuple]]) -> int:
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


def decode_safety_wrap(level_string: str) -> Union[LevelWrap, None, ValueError, Exception]:
    """
    decode level from string safety wrap.  If it errors, return None
    :param level_string: encoded level string
    :return: organized level object or None, if failed
    """
    # noinspection PyBroadException
    try:
        final_level = None
        for line_ in reversed(level_string.split("\n")):
            data = decode_level_from_string(line_)
            if isinstance(data, Exception):
                return data
            update_level(data)
            data.next = final_level
            final_level = data
        return LevelWrap(final_level)
    except:
        traceback.print_exc()
        # print("Errored")
        return ValueError("Level string errored in decode.")


def set_field(index: int, lst: list, val: Any) -> None:
    """
    sets a field and expands the list if index is out of range
    :param index:
    :param lst:
    :param val:
    :return:
    """
    while index >= len(lst):
        lst.append(None)
    lst[index] = val


def decode_level_from_string(level_string: str, published: bool = True) -> Union[Level, TypeError, ValueError]:
    """
    decodes a level from a code string
    :param level_string: encoded level string
    :param published: if it was successfully published (previously assumed to be true)
    :return: a fully organized level object
    """

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
        if string[point] == letter_code[100]:
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
            if string[rep3] in letter_code:
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
                attributes = list()
                if typ == Blocks.player:
                    players.append(((coord - 1) % x + 1, ceil(coord / x)))
                else:
                    if typ in [Blocks.gravity, Blocks.jump]:
                        i4 += 1
                        if typ == Blocks.jump:
                            set_field(Jump.grav_locked, attributes, letter_code.index(block[i4]))
                            i4 += 1
                            set_field(Jump.rotation, attributes,(4 - letter_code.index(block[i4])) % 4)
                        elif typ == Blocks.gravity:
                            buffer = letter_code.index(block[i4])
                            i4 += 1
                            if buffer < 2:
                                set_field(Gravity.type, attributes, "direction")
                                set_field(Gravity.grav_locked, attributes, buffer)
                                if i4 == len(block):
                                    set_field(Gravity.rotation, attributes, 3)
                                else:
                                    set_field(Gravity.rotation, attributes, (2 - letter_code.index(block[i4])) % 4)
                            else:
                                set_field(Gravity.type, attributes, "set")
                                set_field(Gravity.mode, attributes, buffer - 2)
                                if i4 == len(block):
                                    set_field(Gravity.variable_value, attributes, 0)
                                else:
                                    set_field(Gravity.variable_value, attributes, letter_code.index(block[i4]) * 0.25)
                    elif typ == Blocks.repel:
                        i4 += 1
                        set_field(Repel.mode, attributes, letter_code.index(block[i4]))
                    block_data[((coord - 1) % x + 1, ceil(coord / x))] = Block(
                        typ,
                        list(),
                        attributes
                    )
            # print(level_name, block_data)
            return Level(
                level_name,
                (gravity_angle, gravity_strength),
                block_data,
                list(),
                players,
                (6, 6),
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
            attributes = list()
            if block_data[0] == letter_code[99]:
                typ = Blocks.air
            else:
                typ = BLOCKS[letter_code.index(block_data[0])]
            i2 = 0
            if typ in [Gravity, Jump]:
                i2 += 1
                if typ == Jump:
                    set_field(Jump.grav_locked, attributes, letter_code.index(block_data[i2]))
                    i2 += 1
                    set_field(Jump.rotation, attributes, (4 - letter_code.index(block_data[i2])) % 4)
                elif typ == Gravity:
                    buffer = letter_code.index(block_data[i2])
                    i2 += 1
                    if buffer < 2:
                        set_field(Gravity.type, attributes, "direction")
                        set_field(Gravity.grav_locked, attributes, buffer)
                        set_field(Gravity.rotation, attributes, (2 - letter_code.index(block_data[i2])) % 4)
                    else:
                        set_field(Gravity.type, attributes, "set")
                        set_field(Gravity.mode, attributes, buffer - 2)
                        set_field(Gravity.variable_value, attributes, letter_code.index(block_data[i2]) * 0.25)
            elif typ == Repel:
                if len(block_data) == 1:
                    set_field(Repel.mode, attributes, 1)
                    i2 += 0
                elif block_data[1] == letter_code[15]:
                    set_field(Repel.mode, attributes, 0)
                    i2 += 1
                else:
                    set_field(Repel.mode, attributes, 1)
            elif typ == Activator:
                set_field(Activator.delay, attributes, letter_code.index(block_data[1]) / 4)
                set_field(Activator.grav_locked, attributes, 1 - floor(letter_code.index(block_data[2]) / 4))
                set_field(Activator.rotation, attributes, (letter_code.index(block_data[2]) - 1) % 4)
                i2 = 2
            elif typ == Msg:
                i2, length = decode_length_indicator(1, string=block_data)
                set_field(Msg.text, attributes, "")
                for rep2 in range(length):
                    attributes[Msg.text] += block_data[i2]
                    i2 += 1
            elif typ == EasterEgg:
                i2, length = decode_length_indicator(2, string=block_data)
                set_field(EasterEgg.type, attributes, "level")
                set_field(EasterEgg.level, attributes, "")
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
            level_name,
            (gravity_angle, gravity_strength),
            blocks,
            links,
            players,
            (6, 6),
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
            attributes = list()
            if block_data[0] == letter_code[99]:
                typ = Blocks.air
            else:
                typ = BLOCKS[letter_code.index(block_data[0])]
                # print(block_data[0], letter_code.index(block_data[0]), typ)
            i2 = 0
            if typ in [Blocks.gravity, Blocks.jump]:
                i2 += 1
                if typ is Blocks.jump:
                    set_field(Gravity.grav_locked, attributes, letter_code.index(block_data[i2]))
                    i2 += 1
                    set_field(Gravity.rotation, attributes, (4 - letter_code.index(block_data[2])) % 4)
                elif typ is Blocks.gravity:
                    buffer = letter_code.index(block_data[i2])
                    i2 += 1
                    if buffer < 2:
                        set_field(Gravity.type, attributes, "direction")
                        set_field(Gravity.grav_locked, attributes, buffer)
                        set_field(Gravity.rotation, attributes, (2 - letter_code.index(block_data[2])) % 4)
                    else:
                        set_field(Gravity.type, attributes, "set")
                        set_field(Gravity.mode, attributes, buffer - 2)
                        set_field(Gravity.variable_value, attributes, letter_code.index(block_data[i2]) * 0.25)
            elif typ == Blocks.repel:
                # print(len(block_data))
                if len(block_data) == 1:
                    set_field(Repel.mode, attributes, 1)
                    i2 += 0
                elif block_data[1] == letter_code[15]:
                    set_field(Repel.mode, attributes, 0)
                    i2 += 1
                else:
                    set_field(Repel.mode, attributes, 1)
            elif typ == Blocks.activator:
                set_field(Activator.delay, attributes, letter_code.index(block_data[1]) / 4)
                set_field(Activator.grav_locked, attributes, 1 - floor(letter_code.index(block_data[2]) / 4))
                set_field(Activator.rotation, attributes, (1 - letter_code.index(block_data[2])) % 4)
                i2 = 2
            elif typ == Blocks.msg:
                i2, length = decode_length_indicator(1, string=block_data)
                set_field(Msg.text, attributes, "")
                for rep2 in range(length):
                    attributes[Msg.text] += block_data[i2]
                    i2 += 1
                i2 -= 1
            elif typ == Blocks.easter_egg:
                i2, length = decode_length_indicator(2, string=block_data)
                set_field(EasterEgg.type, attributes, "level")
                set_field(EasterEgg.level, attributes, "")
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
            level_name,
            (gravity_angle, gravity_strength),
            blocks,
            links,
            players,
            (6, 6),
            3
        )
    elif level_string[0] == "4":
        save_code = SAVE_CODE["4"]
        i1 = 3 + letter_code.index(level_string[1])
        # gets level dimensions
        x = letter_code.index(level_string[i1])
        y = letter_code.index(level_string[i1 + 1])
        level = Level(
            level_string[2:i1],
            (letter_code.index(level_string[i1 + 2]),
             letter_code.index(level_string[i1 + 3]) * -0.25),
            {},
            [],
            [],
            (6, 6),
            4
        )
        # print(level.name, len(level_string), level.gravity)  # correct
        # print(x, y)  # correct
        players = letter_code.index(level_string[i1 + 4])
        i1 += 5
        for p in range(players):
            level.player_starts.append((letter_code.index(level_string[i1]), letter_code.index(level_string[i1 + 1])))
            i1 += 2
        # print(convert_from_b100(level_string[i1:i1 + 2]))  # correct... I think
        for i2 in range(convert_from_b100(level_string[i1:i1 + 2])):
            block = Block(
                BLOCKS[letter_code.index(level_string[i1 + 2])],
                [],
                []
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
                            set_field(stn[0], block.other, stn[1][int(other_value // cumulative) % attributes[i4]])
                            cumulative *= attributes[i4]
                    if SavingFieldGroups.number in save_code[block.type]:
                        for n in save_code[block.type][SavingFieldGroups.number]:
                            i4 += 1
                            if len(n) == 5:
                                if not n[3] or other_value // cumulative % attributes[i4] != attributes[i4] - 1:
                                    set_field(n[0], block.other, (int(other_value // cumulative) % attributes[i4]) / n[4] + n[2])
                            else:
                                if not n[3] or other_value // cumulative % attributes[i4] != attributes[i4] - 1:
                                    set_field(n[0], block.other, (int(other_value // cumulative) % attributes[i4]) + n[2])
                            cumulative *= attributes[i4]
                if SavingFieldGroups.string in save_code[block.type]:
                    # print("retrieving string fields")
                    for s in save_code[block.type][SavingFieldGroups.string]:
                        if s[1] is not None and block.other[s[1]] != s[2]:
                            # print("text field continued")
                            continue
                        i1 += 1
                        # print(i1, level_string[i1:i1 + 2], convert_from_b100(level_string[i1:i1 + 2]))
                        set_field(s[0], block.other, level_string[i1 + 2: i1 + convert_from_b100(level_string[i1:i1 + 2]) + 2])
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
    elif level_string[0] == "5":
        save_code = copy(SAVE_CODE["4"])
        save_code.update(SAVE_CODE["5"])
        i1 = 3 + letter_code.index(level_string[1])
        # gets max length
        i1, x_l = decode_length_indicator(i1)
        i1, y_l = decode_length_indicator(i1)
        x_c = 1
        if level_string[i1] == "-":
            x_c = -1
            i1 += 1
        x_c *= convert_from_b100(level_string[i1:i1 + x_l])
        i1 += x_l
        y_c = 1
        if level_string[i1] == "-":
            y_c = -1
            i1 += 1
        y_c *= convert_from_b100(level_string[i1:i1 + y_l])
        i1 += y_l
        level = Level(
            level_string[2:3 + letter_code.index(level_string[1])],
            (letter_code.index(level_string[i1]),
             letter_code.index(level_string[i1 + 1]) * -0.25),
            {},
            [],
            [],
            (x_c, y_c),
            5
        )
        i1, players = decode_length_indicator(i1 + 2)  # find number of players
        for p in range(players):
            x = 1
            if level_string[i1] == "-":
                x = -1
                i1 += 1
            x *= convert_from_b100(level_string[i1:i1 + x_l])
            i1 += x_l
            y = 1
            if level_string[i1] == "-":
                y = -1
                i1 += 1
            y *= convert_from_b100(level_string[i1:i1 + y_l])
            i1 += y_l
            level.player_starts.append((x, y))
        i1, blocks = decode_length_indicator(i1)
        for i2 in range(blocks):  # repeat for number of unique blocks
            i1, block_type_index = decode_length_indicator(i1)
            block = Block(
                BLOCKS[block_type_index],  # find block type
                [],
                []
            )
            i1, barrier_layers = decode_length_indicator(i1)
            for i3 in range(barrier_layers):  # find number of barriers
                i1, barrier_index = decode_length_indicator(i1)
                # print(letter_code.index(level_string[i1 - 1]))
                barrier_number = letter_code.index(level_string[i1])
                # print(level_string[i1])
                # print(barrier_number % 32)
                block.barriers.append((
                    BARRIERS[barrier_index],
                    barrier_number % 2 == 1,
                    (
                        barrier_number // 2 % 2 == 1,
                        barrier_number // 4 % 2 == 1,
                        barrier_number // 8 % 2 == 1,
                        barrier_number // 16 % 2 == 1
                    )
                ))
                i1 += 1
            attributes = list()  # finds number of attributes
            if block.type in save_code:
                length = max_info_number_length(save_code[block.type])
                if length > 0:  # check to make sure any of the following is necessary
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
                    # i1 += 1
                    other_value = convert_from_b100(level_string[i1:i1 + length])
                    i1 += length
                    # print(letter_code.index(level_string[i1 - 1]), [letter_code.index(char) for char in level_string[i1 - 5:]])
                    cumulative = 1
                    i4 = -1
                    if SavingFieldGroups.string_to_number in save_code[block.type]:
                        for stn in save_code[block.type][SavingFieldGroups.string_to_number]:  # loops through string to number types
                            i4 += 1
                            set_field(stn[0], block.other, stn[1][int(other_value // cumulative) % attributes[i4]])
                            cumulative *= attributes[i4]
                    if SavingFieldGroups.number in save_code[block.type]:
                        for n in save_code[block.type][SavingFieldGroups.number]:
                            i4 += 1
                            if len(n) == 5:
                                if not n[3] or other_value // cumulative % attributes[i4] != attributes[i4] - 1:
                                    set_field(n[0], block.other, (int(other_value // cumulative) % attributes[i4]) / n[4] + n[2])
                            else:
                                if not n[3] or other_value // cumulative % attributes[i4] != attributes[i4] - 1:
                                    set_field(n[0], block.other, (int(other_value // cumulative) % attributes[i4]) + n[2])
                            cumulative *= attributes[i4]
                if SavingFieldGroups.string in save_code[block.type]:
                    # print("retrieving string fields")
                    for s in save_code[block.type][SavingFieldGroups.string]:
                        if s[1] is not None and block.other[s[1]] != s[2]:
                            # print("text field continued")
                            continue
                        # i1 += 1
                        i1, length = decode_length_indicator(i1)
                        # print(f"Getting text field from '{level_string}', range: {i1}-{i1 + length}, res: '{level_string[i1: i1 + length]}'")
                        # print(i1, level_string[i1:i1 + 2], convert_from_b100(level_string[i1:i1 + 2]))
                        set_field(s[0], block.other, level_string[i1: i1 + length])
                        i1 += length
                    # i1 += 1
            # i1 -= 1
            i1, reps = decode_length_indicator(i1)
            # print("Number of blocks:", convert_from_b100(level_string[i1:i1 + 2:1]) + 1)
            # print("Number of blocks (shift -1):", convert_from_b100(level_string[i1-1:i1 + 1:1]) + 1)
            # print("Number of blocks (shift +1):", convert_from_b100(level_string[i1+1:i1 + 3:1]) + 1)
            for i5 in range(reps):
                # print(level_string[i1], level_string[i1 + 1])
                x = 1
                if level_string[i1] == "-":
                    x = -1
                    i1 += 1
                x *= convert_from_b100(level_string[i1:i1 + x_l])
                i1 += x_l
                y = 1
                if level_string[i1] == "-":
                    y = -1
                    i1 += 1
                y *= convert_from_b100(level_string[i1:i1 + y_l])
                i1 += y_l
                # print(f"({x},{y}) for block {block}")
                level.blocks[(x, y)] = deepcopy(
                    block
                )
        # print(letter_code.index(level_string[i1]), i1 == len(level_string) - 1)
        i1 += 1
        for i5 in range(letter_code.index(level_string[i1 - 1])):
            level.links.append([])
            i1, num_links = decode_length_indicator(i1)
            for i6 in range(num_links):
                x = 1
                if level_string[i1] == "-":
                    x = -1
                    i1 += 1
                x *= convert_from_b100(level_string[i1:i1 + x_l])
                i1 += x_l
                y = 1
                if level_string[i1] == "-":
                    y = -1
                    i1 += 1
                y *= convert_from_b100(level_string[i1:i1 + y_l])
                i1 += y_l
                level.links[-1].append((x, y))
        # if (10, 0) in level.blocks:
        #     level.blocks[(1, 1)] = level.blocks.pop((10, 0))
        # print(level.blocks.keys())
        return level
    else:
        return TypeError("Level code does not start with a valid version indicator. (might be invalid code or game version might be out of date)")


# noinspection IncorrectFormatting
def encode_level_to_string(level_data: Union[LevelWrap, Level]) -> str:
    """
    encodes a level to a shareable string
    :param level_data: level data object or level wrap
    :return: encoded string
    """

    if isinstance(level_data, LevelWrap):
        return encode_level_to_string(level_data.level_on)

    i = 0
    while i < len(level_data.links):
        if not level_data.links[i]:
            del level_data.links[i]
        else:
            i += 1

    def required_length(num: int) -> int:
        """
        finds minimum required length for an input in b100
        :param num:
        :return:
        """
        if num < 0:
            return required_length(abs(num))
        res = 0
        digit = 1
        while num >= digit:
            digit *= 100
            res += 1
        return res

    def convert_to_b100(num: int, req_length: int = None) -> str:
        """
        converts to b100 with letter_code
        :param num: integer to convert
        :param req_length: length the number needs to be for code to work
        :return: string representation
        """
        if num < 0:
            return "-" + convert_to_b100(abs(num), req_length)
        digit = 1
        string = ""
        while num >= digit:
            string += letter_code[(num // digit) % 100]
            digit *= 100  # look, misnomer, k?  But means the same thing and made the first part easier
        if req_length is None:
            res = string
        elif len(string) > req_length:
            raise OverflowError(
                f"b100 conversion exceeded max length (max length: {req_length}, max value: {100 ** (req_length - 1)}, result length: {len(string)}, input value: {num})"
            )
        else:
            res = string + letter_code[0] * (req_length - len(string))
            # print(len(res), req_length)
        return res[::1]

    def make_length_indicator(num: int) -> str:
        """
        generates a length indicator for the string
        :param num:
        :return:
        """
        res = convert_to_b100(num)
        if num == 0:
            res = letter_code[0]
        if len(res) > 1:
            res = letter_code[100] + make_length_indicator(len(res)) + res
        return res

    level_string = "5"  # version indicator
    letter_code = LETTER_CODES[level_string]
    save_code = copy(SAVE_CODE.get("4", {}))
    save_code.update(SAVE_CODE.get("5", {}))
    level_string += letter_code[len(level_data.name) - 1] + level_data.name  # saves level name
    x_l = 0
    y_l = 0
    for coords in level_data.blocks:
        x_l = max(x_l, required_length(coords[0]))
        y_l = max(y_l, required_length(coords[1]))
    for coords in level_data.player_starts:
        x_l = max(x_l, required_length(coords[0]))
        y_l = max(y_l, required_length(coords[1]))
    for links in level_data.links:
        for coords in links:
            x_l = max(x_l, required_length(coords[0]))
            y_l = max(y_l, required_length(coords[1]))
    level_string += make_length_indicator(x_l) + make_length_indicator(y_l)
    level_string += convert_to_b100(level_data.center[0], x_l) + convert_to_b100(level_data.center[1], y_l)
    level_string += letter_code[level_data.gravity[0]] + letter_code[int(level_data.gravity[1] * -4)]  # saves gravity info
    level_string += make_length_indicator(len(level_data.player_starts))  # indicator for # of players
    for player in level_data.player_starts:
        level_string += convert_to_b100(player[0], x_l) + convert_to_b100(player[1], y_l)  # saves indidual player starts
    block_saves = dict()
    for coordinates, block in level_data.blocks.items():  # loops through block items in block save, makes save code
        if block.type == Blocks.air and block.barriers == [] and block.link is None:
            continue
        specific_save = ""
        specific_save += make_length_indicator(BLOCKS.index(block.type))  # adds type indicator to specific save
        specific_save += make_length_indicator(len(block.barriers))  # adds indicator for number of barriers
        for barrier in block.barriers:  # adds barriers to the specific save
            specific_save += make_length_indicator(BARRIERS.index(barrier[0]))
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
                        if len(block.other) > n[0] and block.other[n[0]] is not None:
                            attributes.append((mult, (block.other[n[0]] - n[2]) * times))
                        else:
                            attributes.append((mult, (mult - 1)))
                    del mult, times
                additive = 0
                cumulative = 1
                for mult, val in attributes:  # loops through attributes list with multiplicatory property and adds together, creating custom base number
                    additive += cumulative * val
                    cumulative *= mult
                specific_save += convert_to_b100(int(additive), length)
            if SavingFieldGroups.string in save_code[block.type]:
                for s in save_code[block.type][SavingFieldGroups.string]:
                    # noinspection PyTypeChecker
                    if s[1] is None:
                        specific_save += make_length_indicator(len(block.other[s[0]])) + block.other[s[0]]
                    elif block.other[s[1]] == s[2]:
                        specific_save += make_length_indicator(len(block.other[s[0]])) + block.other[s[0]]
        if specific_save in block_saves:  # check for duplicates
            block_saves[specific_save].append(coordinates)
        else:
            block_saves[specific_save] = [coordinates]  # add for multiple
    level_string += make_length_indicator(len(block_saves))  # number of unique block saves
    for block_save, coordinates in block_saves.items():  # goes through block save and coordinate lists
        # print(BLOCKS[letter_code.index(block_save[0])], len(coordinates))
        level_string += block_save  # adds block save code to string
        level_string += make_length_indicator(len(coordinates))  # indicator for how many blocks
        # print(convert_to_b100(len(coordinates), 2))
        for coordinate in coordinates:  # loops and adds coordinates
            level_string += convert_to_b100(coordinate[0], x_l) + convert_to_b100(coordinate[1], y_l)
    level_string += letter_code[len(level_data.links)]  # adds indicator for number of types of links
    # print(len(level_data.links))
    for link_data in level_data.links:  # loops through types of links
        level_string += make_length_indicator(len(link_data))  # indicator for number of specific type of link
        for link in link_data:  # loops through and adds link coordinates
            level_string += convert_to_b100(link[0], x_l) + convert_to_b100(link[1], y_l)
    if level_data.next is None:
        return level_string
    else:
        return level_string + "\n" + encode_level_to_string(level_data.next)