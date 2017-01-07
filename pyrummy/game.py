from operator import attrgetter
from itertools import combinations
import random

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
        if chip is None:
            return None
        chip.location = Chip.POOL
        self._hand.remove(chip)
        self._drop_chip = None
        return chip

    def play(self):
        constellations = set()
        # start with the highest chips
        pool = sorted(self._hand, key=attrgetter("value"))[::-1]

        for p in range(len(pool)):
            # copy the pool, subpool will be modified
            subpool = [c for c in pool[p:]]
            constellation = _Constellation()

            # at least 3 remaining cheps required for combination
            while len(subpool) > 2:
                # fetch and remove the first chip
                highest_chip = subpool[0]
                subpool.remove(highest_chip)

                # create list of chip candidates once to not repeat in every iteration
                candidates = list(highest_chip.candidates())

                for chip in subpool:
                    if chip.code in candidates:
                        if chip.color == highest_chip.color:
                            pair = Run(highest_chip, chip)
                        else:
                            pair = Book(highest_chip, chip)

                        # try to find 3rd chip for full combination
                        pair_candidates = list(pair.candidates())
                        combination = None

                        for cchip in subpool:
                            if cchip.code in pair_candidates:
                                combination = pair.__class__(
                                        highest_chip, chip, cchip)
                                subpool.remove(cchip)
                                subpool.remove(chip)
                                break

                        # also break out of the outer for loop. If more than
                        # one candidate for `chip` was available, it will be
                        # found in another iteration of the outermost for-loop.
                        if combination is not None:
                            constellation.combinations.append(combination)
                            break

            # TODO: search rest for combinations longer than 3 chips
            constellation.rest = [c for c in pool if c not in
                    constellation.combination_chips()]
            constellations.add(constellation)

        # find best (i.e. largest) constellation among existing ones
        constellations = list(constellations)
        constellations_sizes = [len(list(c.combination_chips())) for c in
                constellations if c.value >= Game.THRESHOLD]
        if constellations_sizes:
            for best_constellation in constellations:
                if len(list(best_constellation.combination_chips())) == \
                        max(constellations_sizes):
                    break

            # update player yard and hand
            self._yard.extend(best_constellation.combinations)

            for c in best_constellation.combination_chips():
                self._hand.remove(c)

            self._find_drop_chip(best_constellation.rest)
        else:
            # constellations found, but unsufficient in value
            constellations_values = [c.value for c in constellations]
            max_index = constellations_values.index(max(constellations_values))
            max_constellation = constellations[max_index]
            if max_constellation.value > 2:
                self._find_drop_chip(max_constellation.rest)
            else:
                self._find_drop_chip(self._hand)

    def _find_drop_chip(self, chips_):
        if len(chips_) == 0:
            # FIXME In this situation, the entire hand has been formed into
            # combinations and no chip is left to drop. AFAIK dropping a chip
            # at the end of a player's turn is mandatory, so the combinations
            # would have to be ripped apart in order to find a chip to drop.
            # For now, this scenario is ignored and a player can win without
            # dropped a final chip.
            self._drop_chip = None
            return
        chips = chips_[:]
        while len(chips) > 1:
            for pair in combinations(chips, 2):
                if Chip.remote_candidates(*pair):
                    chips.remove(pair[0])
                    chips.remove(pair[1])
                    break
            else:
                # no remote candidates found, pick any of the remaining chips
                random.shuffle(chips)
                self._drop_chip = chips[0]
                return
        if len(chips) == 1:
            self._drop_chip = chips[0]

        # all chips are remote candidates, pick the smallest one
        # TODO this could be adjusted to the stage of the player (about to
        # publish, or trying to finish).
        self._drop_chip = sorted(chips_, key=attrgetter("value"))[0]


class Game(object):

    THRESHOLD = 40
