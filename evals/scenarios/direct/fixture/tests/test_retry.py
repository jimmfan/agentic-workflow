import unittest

from src.retry import retry_delay


class RetryDelayTests(unittest.TestCase):
    def test_default_backoff_and_cap(self) -> None:
        self.assertEqual(retry_delay(0), 1.0)
        self.assertEqual(retry_delay(1), 2.0)
        self.assertEqual(retry_delay(4), 16.0)
        self.assertEqual(retry_delay(5), 30.0)
        self.assertEqual(retry_delay(10), 30.0)

    def test_custom_base_and_cap(self) -> None:
        self.assertEqual(retry_delay(2, base_seconds=0.5, max_seconds=10.0), 2.0)

    def test_negative_attempt_is_invalid(self) -> None:
        with self.assertRaises(ValueError):
            retry_delay(-1)


if __name__ == "__main__":
    unittest.main()
