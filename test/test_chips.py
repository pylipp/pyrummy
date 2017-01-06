import unittest
from collections import deque

from pyrummy.chips import Chip, Book, Run


class ChipTestCase(unittest.TestCase):

    def test_init(self):
        chip = Chip(Chip.RED, 1, Chip.YARDS, 1)
        self.assertEqual(hash(chip), 1953)
        self.assertEqual(chip.location, Chip.YARDS)

    def test_from_str(self):
        chip = Chip.from_str("b10")
        self.assertEqual(hash(chip), 842)
        self.assertEqual(chip.location, Chip.POOL)

    def test_code(self):
        chip = Chip.from_str("y1")
        self.assertEqual(chip.code, "y01")

    def test_eq(self):
        self.assertEqual(Chip.from_str("Y05"), Chip(Chip.YELLOW, 5))

    def test_r1_candidates(self):
        chip = Chip.from_str("r1")
        self.assertSetEqual(set(chip.candidates()), {"y01", "b01", "k01", "r02"})

    def test_r2_candidates(self):
        chip = Chip.from_str("r2")
        self.assertSetEqual(set(chip.candidates()),
                {"y02", "b02", "k02", "r03", "r01"})

class BookTestCase(unittest.TestCase):
    def test_two_chip_book(self):
        book = Book(Chip.from_str("k11"), Chip.from_str("y11"))
        candidates = set(book.candidates())
        self.assertSetEqual(candidates, {"r11", "b11"})
        self.assertEqual(book.value, 22)

    def test_four_chip_book(self):
        book = Book(*[Chip(color, 4) for color in range(Chip.NR_COLORS)])
        candidates = list(book.candidates())
        self.assertEqual(0, len(candidates))

class RunTestCase(unittest.TestCase):
    def test_init_sort(self):
        run = Run(Chip.from_str("r9"), Chip.from_str("r8"), Chip.from_str("r10"))
        self.assertEqual(run, deque([Chip.from_str("r8"), Chip.from_str("r9"),
            Chip.from_str("r10")]))

    def test_candidates(self):
        run = Run(Chip.from_str("r9"), Chip.from_str("r8"), Chip.from_str("r10"))
        candidates = list(run.candidates())
        self.assertListEqual(candidates, ["r11", "r07"])

    def test_no_candidates(self):
        run = Run(*[Chip(Chip.BLACK, v) for v in range(Chip.MAX_VALUE, 0, -1)])
        self.assertEqual(0, len(list(run.candidates())))

if __name__ == "__main__":
    unittest.main()
