import unittest

from pyrummy.chips import Chip, Book
from pyrummy.game import Player, Game


class PlayerInitTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = Player(0, [Chip.from_str("r2")])
        return cls

    def test_victorious(self):
        self.assertFalse(self.player.victorious())

    def test_draw(self):
        self.player.draw(Chip.from_str("k9"))
        self.assertListEqual(self.player._hand,
                [Chip.from_str("r2"), Chip.from_str("k9")])

    def test_hand(self):
        self.player.draw(Chip.from_str("k10"))
        self.assertTrue(all([chip.location == 0 for chip in self.player._hand]))

class PlayerSimplePlayTestCase(unittest.TestCase):
    def test_yard(self):
        player = Player(0, [
            Chip.from_str("b8"), Chip.from_str("b7"),
            Chip.from_str("r7"), Chip.from_str("y7")])
        Game.THRESHOLD = 0
        player.play()
        book = player._yard[0]
        self.assertEqual(1, len(player._yard))
        self.assertEqual(3, len(book))
        self.assertTrue(all([c.value == 7 for c in book]))
        self.assertSetEqual({Chip.YELLOW, Chip.BLUE, Chip.RED},
                {c.color for c in book})
        self.assertEqual(Chip.from_str("b8"), player._hand[-1])
        # self.assertListEqual(player._yard, [Book(Chip.from_str("b7"),
        #                 Chip.from_str("r7"), Chip.from_str("y7"))])

    def test_yard_again(self):
        player = Player(0, [
            Chip.from_str("r9"), Chip.from_str("r8"), Chip.from_str("r7"),
            Chip.from_str("b8"), Chip.from_str("y8"),
            Chip.from_str("y7"), Chip.from_str("y6"),
            Chip.from_str("k11"), Chip.from_str("b2"), Chip.from_str("b1")])
        Game.THRESHOLD = 40
        player.play()
        combi = player._yard[0]
        # algorithm picks either r987 or rby8
        self.assertEqual(24, combi.value)
        self.assertEqual(4, len(player._hand))

    def test_yard_double_chip(self):
        player = Player(0, [
            Chip.from_str("y2", index=0), Chip.from_str("y3"), Chip.from_str("y4"),
            Chip.from_str("y2", index=1), Chip.from_str("r2"), Chip.from_str("k2")])
        Game.THRESHOLD = 10
        player.play()
        self.assertEqual(2, len(player._yard))
        self.assertEqual(0, len(player._hand))

    def test_below_threshold(self):
        player = Player(0, [
            Chip.from_str("y2", index=0), Chip.from_str("y3"), Chip.from_str("y4"),
            Chip.from_str("y2", index=1), Chip.from_str("r2"), Chip.from_str("k2")])
        Game.THRESHOLD = 20
        player.play()
        self.assertEqual(0, len(player._yard))
        self.assertEqual(6, len(player._hand))

if __name__ == "__main__":
    unittest.main()
