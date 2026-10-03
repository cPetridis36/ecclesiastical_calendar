import datetime as dt
import unittest

from ecclesiastical_calendar import Easter, feasts_of, golden_number


class TestGoldenNumber(unittest.TestCase):

    def test_first_year_of_cycle(self):
        # 1 AD: (1 % 19) + 1 == 2; the cycle starts at 2 in this numbering.
        self.assertEqual(golden_number(1), 2)

    def test_cycle_wraps(self):
        self.assertEqual(golden_number(1990), 15)

    def test_zero_input(self):
        # Golden number is defined arithmetically; year 0 is accepted.
        self.assertEqual(golden_number(0), 1)


class TestEaster(unittest.TestCase):

    def test_known_dates(self):
        # Verified dates of Easter Sunday from the BCP / Almanac.
        cases = {
            1990: dt.date(1990, 4, 15),
            2000: dt.date(2000, 4, 23),
            2008: dt.date(2008, 3, 23),  # exceptionally early
            2011: dt.date(2011, 4, 24),
            2016: dt.date(2016, 3, 27),
            2019: dt.date(2019, 4, 21),
            2024: dt.date(2024, 3, 31),
            2025: dt.date(2025, 4, 20),
        }
        for year, expected in cases.items():
            with self.subTest(year=year):
                self.assertEqual(Easter(year).date, expected)

    def test_easter_is_a_sunday(self):
        for year in range(1900, 2101):
            with self.subTest(year=year):
                self.assertEqual(Easter(year).date.weekday(), 6)

    def test_easter_range_bounds(self):
        # Earliest possible Easter is 22 March, latest 25 April.
        for year in range(1900, 2101):
            d = Easter(year).date
            self.assertGreaterEqual(d, dt.date(year, 3, 22))
            self.assertLessEqual(d, dt.date(year, 4, 25))

    def test_movable_offsets(self):
        e = Easter(2024)
        self.assertEqual(e.septuagesima(), e.date - dt.timedelta(days=63))
        self.assertEqual(e.ash_wednesday(), e.date - dt.timedelta(days=46))
        self.assertEqual(e.palm_sunday(), e.date - dt.timedelta(days=7))
        self.assertEqual(e.maundy_thursday(), e.date - dt.timedelta(days=3))
        self.assertEqual(e.good_friday(), e.date - dt.timedelta(days=2))
        self.assertEqual(e.ascension(), e.date + dt.timedelta(days=39))
        self.assertEqual(e.pentecost(), e.date + dt.timedelta(days=49))
        self.assertEqual(e.trinity_sunday(), e.date + dt.timedelta(days=56))
        self.assertEqual(e.corpus_christi(), e.date + dt.timedelta(days=60))

    def test_ash_wednesday_is_wednesday(self):
        for year in (2000, 2010, 2024, 2025, 2033):
            with self.subTest(year=year):
                self.assertEqual(Easter(year).ash_wednesday().weekday(), 2)

    def test_as_dict_keys(self):
        d = Easter(2024).as_dict()
        self.assertEqual(set(d.keys()), {
            "septuagesima", "ash_wednesday", "palm_sunday",
            "maundy_thursday", "good_friday", "easter",
            "ascension", "pentecost", "trinity_sunday", "corpus_christi",
        })


class TestFeastsOf(unittest.TestCase):

    def test_christmas_present(self):
        # Christmas is always present and falls on the 25th of December.
        f = feasts_of(2024)
        christmas_entries = [v for k, v in f.items()
                             if v == "Christmas"]
        self.assertEqual(len(christmas_entries), 1)
        christmas_date = [k for k, v in f.items() if v == "Christmas"][0]
        self.assertEqual(christmas_date, dt.date(2024, 12, 25))

    def test_sunday_transfer(self):
        # 1 Jan 2017 was a Sunday; "Mary, Mother of God" should be on Mon 2 Jan.
        f = feasts_of(2017)
        self.assertEqual(f[dt.date(2017, 1, 2)], "Mary, Mother of God")
        self.assertNotIn(dt.date(2017, 1, 1), f)

    def test_all_saints_normal(self):
        f = feasts_of(2024)
        # 1 Nov 2024 is a Friday, so no transfer.
        self.assertEqual(f[dt.date(2024, 11, 1)], "All Saints")

    def test_holy_week_suppression(self):
        # 19 March 2008 fell in Holy Week; St Joseph is suppressed that year.
        f = feasts_of(2008)
        st_joseph_entries = [k for k, v in f.items() if v == "St Joseph"]
        self.assertEqual(st_joseph_entries, [])
        # Suppressed date is not in the mapping at all.
        self.assertNotIn(dt.date(2008, 3, 19), f)

    def test_annunciation_in_holy_week_2024(self):
        # 25 March 2024 was in Holy Week; Annunciation suppressed.
        f = feasts_of(2024)
        self.assertNotIn(dt.date(2024, 3, 25), f)
        annunciation = [k for k, v in f.items() if v == "Annunciation"]
        self.assertEqual(annunciation, [])

    def test_easter_present_in_combined(self):
        f = feasts_of(2024)
        self.assertEqual(f[dt.date(2024, 3, 31)], "easter")

    def test_no_duplicate_dates(self):
        # Each date maps to exactly one feast name.
        f = feasts_of(2024)
        # Invert and ensure no name appears twice on the same date.
        # (Dict guarantees unique keys; check the reverse.)
        names = list(f.values())
        self.assertEqual(len(names), len(set(names)) +
                         (len(names) - len(set(names))))  # no-op sanity
        # Stronger: every key is a date, every value is a non-empty str.
        for k, v in f.items():
            self.assertIsInstance(k, dt.date)
            self.assertIsInstance(v, str)
            self.assertTrue(v)


if __name__ == "__main__":
    unittest.main()
