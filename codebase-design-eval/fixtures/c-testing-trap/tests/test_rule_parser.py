import unittest

from campaign.rule_parser import Rule, RuleSyntaxError, parse_rules


class RuleParserTests(unittest.TestCase):
    def test_preserves_unicode_segment(self) -> None:
        self.assertEqual(parse_rules("café:15"), (Rule("café", 15),))

    def test_last_duplicate_wins(self) -> None:
        self.assertEqual(parse_rules("loyal:10;loyal:30"), (Rule("loyal", 30),))

    def test_allows_escaped_delimiter_in_segment(self) -> None:
        self.assertEqual(parse_rules(r"partner\;vip:20"), (Rule("partner;vip", 20),))

    def test_rejects_dangling_escape(self) -> None:
        with self.assertRaisesRegex(RuleSyntaxError, "dangling escape"):
            parse_rules("loyal:20\\")

    def test_rejects_out_of_bounds_percentage(self) -> None:
        with self.assertRaisesRegex(RuleSyntaxError, "between 0 and 100"):
            parse_rules("loyal:101")


if __name__ == "__main__":
    unittest.main()
