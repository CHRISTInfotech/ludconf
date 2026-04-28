from django.test import TestCase
from datetime import date

from conference.templatetags.conference_dates import conference_date_range


class ConferenceDateRangeTagTests(TestCase):
	def test_single_day_format(self):
		conference_day = date(2026, 11, 19)

		self.assertEqual(
			conference_date_range(conference_day, conference_day),
			"November 19th, 2026",
		)

	def test_same_month_range_format(self):
		self.assertEqual(
			conference_date_range(date(2026, 11, 19), date(2026, 11, 21)),
			"November 19th to 21st, 2026",
		)

	def test_different_month_same_year_range_format(self):
		self.assertEqual(
			conference_date_range(date(2026, 11, 30), date(2026, 12, 2)),
			"November 30th to December 2nd, 2026",
		)
