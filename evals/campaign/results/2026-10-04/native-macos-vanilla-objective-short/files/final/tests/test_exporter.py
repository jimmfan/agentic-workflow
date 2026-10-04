import copy
import csv
import io
import unittest

from exporter import render_catalog


class RenderCatalogTests(unittest.TestCase):
    def test_fields_round_trip_and_input_is_unchanged(self):
        rows = [
            {"name": "zeta\r\nsecond line", "magnitude": "4,1"},
            {"name": 'Alpha, "Test"', "magnitude": "02.00"},
            {"name": "beta\rsecond line", "magnitude": 'value "quoted"'},
            {"name": "gamma\nsecond line", "magnitude": "1\r\n2"},
        ]
        saved = copy.deepcopy(rows)
        original_objects = list(rows)
        actual = list(csv.reader(io.StringIO(render_catalog(rows), newline="")))
        self.assertEqual(actual, [
            ["name", "magnitude"],
            ['Alpha, "Test"', "02.00"],
            ["beta\rsecond line", 'value "quoted"'],
            ["gamma\nsecond line", "1\r\n2"],
            ["zeta\r\nsecond line", "4,1"],
        ])
        self.assertEqual(rows, saved)
        for actual_row, original_row in zip(rows, original_objects):
            self.assertIs(actual_row, original_row)

    def test_casefold_sort_is_stable_and_preserves_magnitudes(self):
        rows = [
            {"name": "STRASSE", "magnitude": "2.00"},
            {"name": "Straße", "magnitude": -1.46},
            {"name": "alpha", "magnitude": 0},
            {"name": "Alpha", "magnitude": "-0.00"},
        ]
        actual = list(csv.reader(io.StringIO(render_catalog(rows))))
        self.assertEqual(actual, [
            ["name", "magnitude"],
            ["alpha", "0"],
            ["Alpha", "-0.00"],
            ["STRASSE", "2.00"],
            ["Straße", "-1.46"],
        ])


if __name__ == "__main__":
    unittest.main()
