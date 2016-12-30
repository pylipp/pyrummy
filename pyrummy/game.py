from pyrummy.chips import Chip


class Player(object):

    HAND_ONLY = 0
    JUST_PUBLISHED = 1
    PUBLISHED = 2

    def __init__(self, index, hand, game=None):
        self._index = index
        self._hand = []
        for chip in hand:
            self.draw(chip)
        self._game = game
        self._status = Player.HAND_ONLY
        self._drop_chip = None

    def victorious(self):
        return len(self._hand) == 0

    def draw(self, chip):
        chip.location = self._index
        self._hand.append(chip)

    def drop(self):
        chip = self._drop_chip
        chip.location = Chip.POOL
        self._hand.remove(chip)
        self._drop_chip = None
        return chip
