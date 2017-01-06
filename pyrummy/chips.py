from abc import ABCMeta, abstractmethod
from collections import deque
from operator import attrgetter


class Chip(object):

    # color enum
    YELLOW = 0
    RED = 1
    BLUE = 2
    BLACK = 3
    NR_COLORS = 4

    MAX_VALUE = 13

    # location enum; 0-5 indicate player hand
    POOL = 6
    YARDS = 7

    # status enum indicating chip usage in combination search
    UNUSED = 0
    EVALUATED = 1
    COMBINED = 2

    def __init__(self, color, value, location=POOL, index=0):
        self._color = color
        self._value = value
        self._location = location
        self._index = index
        self._status = Chip.UNUSED

    @classmethod
    def from_str(cls, code, location=POOL, index=0):
        """Convenience method for quickly generating a Chip from a string code,
        f.i. 'y9', 'Y9', 'y09' or 'Y09' for a yellow nine."""
        color_codes = "yrbk"
        color = color_codes.find(code[0].lower())
        value = int(code[1:])
        return cls(color, value, location, index)

    @property
    def code(self):
        """Returns a string representing color and value, e.g. "k08" for a black
        8. The chip index does not matter. This function is useful if the chip
        as a unique object is not required, i.e. when comparing a chip to
        another chip's candidates."""
        return "{}{:02}".format("yrbk"[self._color], self._value)

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

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def __hash__(self):
        return self._value + (self._color << 5) + (self._location << 7) +\
                (self._index << 10)

    def __eq__(self, other):
        return self._color == other._color and self._value == other._value and\
                self._index == other._index

    def candidates(self):
        all_colors = set(range(Chip.NR_COLORS))
        for color in all_colors.difference({self._color}):
            yield Chip(color, self._value).code
        if self._value < Chip.MAX_VALUE:
            yield Chip(self._color, self._value + 1).code
        if self._value > 1:
            yield Chip(self._color, self._value - 1).code

    def __repr__(self):
        """Similar to `Chip.code()` but also shows the chip index. For
        debugging purposes."""
        return "{}{:02} {}".format("yrbk"[self._color], self._value, self._index)


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
            yield Chip(color, self._chip_value).code


class Run(deque, Combination):

    def __init__(self, *args):
        super().__init__(sorted(list(args), key=attrgetter("value")))
        self._chip_color = args[0].color

    def candidates(self):
        if self[-1].value < Chip.MAX_VALUE:
            yield Chip(self._chip_color, self[-1].value + 1).code
        if self[0].value > 1:
            yield Chip(self._chip_color, self[0].value - 1).code

