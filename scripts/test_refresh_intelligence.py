import unittest
from datetime import date, timedelta
from collections import Counter
import xml.etree.ElementTree as ET
from refresh_intelligence import read_calendar, render

class IntelligenceTests(unittest.TestCase):
    def test_calendar_levels_and_missing_days(self):
        today = date(2026, 11, 27)
        html = "".join(f'<td data-date="{today-timedelta(days=i)}" data-level="{i%5}"></td>' for i in range(364))
        days = read_calendar(html, today)
        self.assertEqual(len(days), 364)
        self.assertEqual(days[today], 0)
        self.assertNotIn(today-timedelta(days=364), days)

    def test_incomplete_calendar_rejected(self):
        with self.assertRaises(ValueError):
            read_calendar('<td data-date="2026-11-27" data-level="2"></td>', date(2026,11,27))

    def test_svg_escapes_labels_and_uses_actual_values(self):
        today = date(2026,11,27)
        svg = render([{"stargazers_count": 7, "forks_count": 2}], Counter({"A&B": 12}), {today: 4}, today)
        ET.fromstring(svg)
        self.assertIn("A&amp;B", svg)
        self.assertIn("100.0%", svg)
        self.assertIn(">7</text>", svg)

if __name__ == "__main__":
    unittest.main()
