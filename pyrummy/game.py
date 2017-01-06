from operator import attrgetter
from itertools import chain

from pyrummy.chips import Chip, Run, Book


class _Constellation(object):

    def __init__(self):
        self.combinations = []
        self.rest = None

    @property
    def value(self):
        return sum([c.value for c in self.combinations])

    def combination_chips(self):
        for combi in self.combinations:
            for chip in combi:
                yield chip

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
        self._yard = []

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

    def play(self):
        constellations = set()
        pool = sorted(self._hand, key=attrgetter("value"))[::-1]

        for p in range(len(pool)):
            # copy the pool, subpool will be modified
            subpool = [c for c in pool[p:]]
            constellation = _Constellation()

            while len(subpool):
                highest_chip = subpool[0]
                highest_chip.status = Chip.EVALUATED

                candidates = list(highest_chip.candidates())
                for chip in subpool:
                    if chip.code in candidates:
                        i = subpool.index(chip)
                        subpool.remove(chip)
                        if chip.color == highest_chip.color:
                            pair = Run(highest_chip, chip)
                        else:
                            pair = Book(highest_chip, chip)
                        pair_candidates = list(pair.candidates())
                        combination = None
                        for cchip in subpool:
                            if cchip.code in pair_candidates:
                                highest_chip.status = Chip.COMBINED
                                chip.status = Chip.COMBINED
                                cchip.status = Chip.COMBINED
                                combination = pair.__class__(
                                        highest_chip, chip, cchip)
                                break
                        if combination is not None:
                            constellation.combinations.append(combination)
                            break
                        else:
                            subpool.insert(i, chip)
                subpool = [c for c in subpool if c.status == Chip.UNUSED]
            # TODO: search rest for combinations longer than 3 chips
            # FIXME: this needs the chip index for correctness
            constellation.rest = [c for c in pool if c not in
                    constellation.combination_chips()]
            constellations.add(constellation)

        # TODO: best constellation is actually the one that contains most chips
        constellations = list(constellations)
        constellations_values = [c.value for c in constellations]
        max_index = constellations_values.index(max(constellations_values))

        best_constellation = constellations[max_index]
        self._yard.extend(best_constellation.combinations)

        for c in best_constellation.combination_chips():
            self._hand.remove(c)

        # TODO: determine chip to drop from constellation rest
