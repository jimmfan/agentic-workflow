import unittest

from quote.application import QuoteApplication


class QuoteApplicationTests(unittest.TestCase):
    def test_applies_discount(self) -> None:
        self.assertEqual(
            QuoteApplication().execute([800, 200], 25),
            {"total": 750},
        )

    def test_clamps_discount(self) -> None:
        self.assertEqual(QuoteApplication().execute([500], 140), {"total": 0})


if __name__ == "__main__":
    unittest.main()
