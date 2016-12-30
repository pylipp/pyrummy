import unittest

from pyrummy.chips import Chip


class ChipTestCase(unittest.TestCase):

    def test_init(self):
        chip = Chip(Chip.RED, 1, Chip.YARDS, 1)
        self.assertEqual(hash(chip), 1953)
        self.assertEqual(chip.location, Chip.YARDS)

    def test_from_str(self):
        chip = Chip.from_str("b10")
        self.assertEqual(hash(chip), 842)
        self.assertEqual(chip.location, Chip.POOL)

if __name__ == "__main__":
    unittest.main()
