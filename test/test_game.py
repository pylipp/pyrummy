import unittest

from pyrummy.chips import Chip
from pyrummy.game import Player


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

if __name__ == "__main__":
    unittest.main()
