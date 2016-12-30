

class Chip(object):

    YELLOW = 0
    RED = 1
    BLUE = 2
    BLACK = 3

    POOL = 6
    YARDS = 7

    def __init__(self, color, value, location, index):
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
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    def __hash__(self):
        return self._value + (self._color << 5) + (self._location << 7) +\
                (self._index << 10)
