import unittest

from campaign.engine import CampaignEngine


class CampaignEngineTests(unittest.TestCase):
    def test_applies_matching_campaign(self) -> None:
        self.assertEqual(
            CampaignEngine().discount_percent("new:10;loyal:25", "loyal"),
            25,
        )

    def test_defaults_to_no_discount(self) -> None:
        self.assertEqual(CampaignEngine().discount_percent("new:10", "guest"), 0)


if __name__ == "__main__":
    unittest.main()
