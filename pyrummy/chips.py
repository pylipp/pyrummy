from abc import ABCMeta, abstractmethod
from collections import deque
from operator import attrgetter


class Chip(object):

    YELLOW = 0
    RED = 1
    BLUE = 2
    BLACK = 3
    NR_COLORS = 4

    MAX_VALUE = 13

    POOL = 6
    YARDS = 7

    def __init__(self, color, value, location=POOL, index=0):
        self._color = color
        self._value = value
        self._location = location
        self._index = index

    @classmethod
    def from_str(cls, code, location=POOL, index=0):
        """Convenience method for quickly generating a Chip from a string code,
        f.i. 'y9', 'Y9', 'y09' or 'Y09' for a yellow nine."""
        color_codes = "yrbk"
        color = color_codes.find(code[0].lower())
        value = int(code[1:])
        return cls(color, value, location, index)

    @property
    def value(self):
        return self._value

    @property
    def color(self):
        return self._color

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    def __hash__(self):
        return self._value + (self._color << 5) + (self._location << 7) +\
                (self._index << 10)

    def __eq__(self, other):
        return self._color == other._color and self._value == other._value


class Combination(object):

    __metaclass__ = ABCMeta

    @property
    def value(self):
        return sum([chip.value for chip in self])

    @abstractmethod
    def candidates(self):
        pass


class Book(set, Combination):

    def __init__(self, *args):
        super().__init__(args)
        self._chip_value = args[0].value

    def candidates(self):
        all_colors = set(range(Chip.NR_COLORS))
        self_colors = set([chip.color for chip in self])
        for color in all_colors.difference(self_colors):
            yield Chip(color, self._chip_value)


class Run(deque, Combination):

    def __init__(self, *args):
        super().__init__(sorted(list(args), key=attrgetter("value")))
        self._chip_color = args[0].color

    def candidates(self):
        if self[-1].value < Chip.MAX_VALUE:
            yield Chip(self._chip_color, self[-1].value + 1)
        if self[0].value > 1:
            yield Chip(self._chip_color, self[0].value - 1)

