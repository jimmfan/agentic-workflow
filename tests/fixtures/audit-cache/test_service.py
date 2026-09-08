import unittest
from service import Reports, Store


class ReportsTest(unittest.TestCase):
    def test_reuses_total(self):
        store = Store({"alpha": 12})
        report = Reports(store)
        self.assertEqual(report.total("alpha", 0), 12)
        self.assertEqual(report.total("alpha", 10), 12)
        self.assertEqual(store.reads, 1)

    def test_refreshes_at_boundary(self):
        store = Store({"alpha": 12})
        report = Reports(store)
        report.total("alpha", 0)
        store.totals["alpha"] = 19
        self.assertEqual(report.total("alpha", 30), 19)


if __name__ == "__main__":
    unittest.main()
