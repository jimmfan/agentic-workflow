import unittest

from campaign.validator import validate_for_authoring


class ValidatorTests(unittest.TestCase):
    def test_reports_parser_error(self) -> None:
        self.assertEqual(
            validate_for_authoring("loyal:101"),
            ["percentage must be between 0 and 100"],
        )


if __name__ == "__main__":
    unittest.main()
