from operator import attrgetter
from itertools import combinations
import random
import logging
import time

from pyrummy.chips import Chip, Run, Book


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
        filename="log_{}".format(int(time.time())))


class _Constellation(object):
    """Container for chip combinations during the combination search.
    `combinations` is a list of Books or Runs that can be formed from the given
    chips. `rest` is a list of chips not contained in combinations."""

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
    """Representing a Rummy player and his playing actions.
    Every player has an individual index (integer starting from 0). A player
    administers chips on his hand and on his yard. He holds a status indicating
    whether the player has published any chips from his hand to his yard."""

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
        logger.debug("Player {} hand: {}".format(self._index, self._hand))
        logger.debug("Player {} yard: {}".format(self._index, self._yard))

    def victorious(self):
        return len(self._hand) == 0

    def draw(self, chip):
        chip.location = self._index
        self._hand.append(chip)
        logger.debug("Player {} draws: {}".format(self._index, chip))

    def drop(self):
        """Remove the designated chip from the hand and return it, s.t. it can
        be added to the pool. Returns None if no chip is available."""
        chip = self._drop_chip
        logger.debug("Player {} drops: {}".format(self._index, chip))
        if chip is None:
            return None
        chip.location = Chip.POOL
        self._hand.remove(chip)
        self._drop_chip = None
        return chip

    def play(self):
        """Main routine. Searches for optimal constellation of hand chips,
        publishes combinations to the yard, if possible, and determines the
        chip to drop."""
        constellations = set()

        # start with the highest chips
        pool = sorted(self._hand, key=attrgetter("value"))[::-1]

        # TODO: with status==PUBLISHED, take pendants from yards into account.

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
            # with status=PUBLISHED, other players' yards can be searched, too
            constellation.rest = [c for c in pool if c not in
                    constellation.combination_chips()]
            # TODO: hash constellation
            constellations.add(constellation)

        # find best (i.e. largest) constellation among existing ones
        constellations = list(constellations)
        constellations_sizes = [len(list(c.combination_chips())) for c in
                constellations if c.value >= Game.THRESHOLD or
                (self._status > Player.HAND_ONLY and c.value > 0)]
        if constellations_sizes:
            for best_constellation in constellations:
                if len(list(best_constellation.combination_chips())) == \
                        max(constellations_sizes):
                    break

            # update player yard and hand
            self._yard.extend(best_constellation.combinations)

            for c in best_constellation.combination_chips():
                self._hand.remove(c)

            if self._status == Player.HAND_ONLY:
                self._status = Player.PUBLISHED

            logger.debug("Player {} publishes: {}".format(self._index,
                best_constellation.combinations))
            logger.debug("Player {} hand: {}".format(self._index, self._hand))
            self._find_drop_chip(best_constellation.rest)
        else:
            # constellations found, but unsufficient in value; or none found
            constellations_values = [c.value for c in constellations]
            max_index = constellations_values.index(max(constellations_values))
            max_constellation = constellations[max_index]
            if max_constellation.value > 2:
                self._find_drop_chip(max_constellation.rest)
            else:
                self._find_drop_chip(self._hand)

    def _find_drop_chip(self, chips_):
        """Helper routine to find the chip that is most unlikely to be combined
        with another hand chip in the future. This chip will be dropped."""
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
                # TODO: this should depending on player stage, see below
                random.shuffle(chips)
                self._drop_chip = chips[0]
                return
        if len(chips) == 1:
            self._drop_chip = chips[0]

        # all chips are remote candidates, pick the smallest one
        # TODO this could be adjusted to the stage of the player (about to
        # publish, or trying to finish).
        self._drop_chip = sorted(chips_, key=attrgetter("value"))[0]


class Pool(list):
    """Container holding chips that players draw from and drop to.
    By default, a double-deck pool is initialized, holding 2x52 chips. If a
    list of chips is passed, the pool is created from the list. This is most
    useful for testing."""

    def __init__(self, chips=None):
        if chips is None:
            for value in range(Chip.MIN_VALUE, Chip.MAX_VALUE+1):
                for color in range(Chip.NR_COLORS):
                    for index in range(2):
                        chip = Chip(color, value, index=index)
                        self.append(chip)
        else:
            self.extend(chips)
        logger.debug("Pool contains: {}".format(self))

    def pop_random_chip(self):
        random.shuffle(self)
        return self.pop()


class Game(object):
    """Create a game and run it.
    There are two options for game generation. One can specify a number of
    players between 1 and 6. The standard pool (two decks with 52 chips each)
    is created and each player are given random hands of 14 chips.
    Another option (which is particularly useful for testing) is to pass a
    custum `Pool` instance and a `hands` list that is assigns a custom hand to
    each player.
    A game organizes all player instances, the pool and the yards."""

    THRESHOLD = 40
    HAND_START_SIZE = 14

    def __init__(self, nr_players=4, pool=None, hands=None):
        if (pool is None) ^ (hands is None):
            raise ValueError("Specify either both pool and hands or none.")
        self._yards = {}
        self._pool = Pool() if pool is None else pool

        self._nr_players = nr_players if hands is None else len(hands)
        self._players = self._nr_players * [None]
        self._current_player_index = 0

        self._winner = None

        self._generate(hands)

    def _generate(self, hands):
        logger.info("Generating game with {} player{}...".format(
            self._nr_players, "s" if self._nr_players > 1 else ""))
        if hands is None:
            for i in range(self._nr_players):
                hand = []
                for _ in range(Game.HAND_START_SIZE):
                    hand.append(self._pool.pop_random_chip())
                self._players[i] = Player(i, hand, self)
        else:
            for i, hand in enumerate(hands):
                self._players[i] = Player(i, hand, self)

    def run(self):
        """Main game routine. The players are taking turns with drawing,
        playing and dropping. The first player who gets rid of his hand wins."""
        logger.info("Starting the game...")
        while True:
            current_player = self._players[self._current_player_index]
            current_player.draw(self._pool.pop_random_chip())
            current_player.play()
            self._pool.append(current_player.drop())
            logger.debug("Pool contains: {}".format(self._pool))

            if current_player.victorious():
                self._winner = current_player
                logger.info("Player {} wins!".format(self._current_player_index))
                break

            self._current_player_index = (self._current_player_index + 1) %\
                    self._nr_players


def main():
    Game(4).run()
