from __future__ import annotations

import datetime as _dt
from typing import Dict, Optional, Tuple

__all__ = ["Easter", "feasts_of", "golden_number"]


def golden_number(year: int) -> int:
    """Return the Golden Number for a Gregorian calendar year.

    The Golden Number is 1 + (year mod 19). The Catholic liturgical tradition
    numbers the years 1-19 rather than 0-18, which is why we add 1.
    """
    return (year % 19) + 1


def _easter_anonymous_gregorian(year: int) -> _dt.date:
    """Compute Easter (Gregorian) for *year* using the Anonymous Gregorian
    algorithm.

    This is Meeus's closed-form algorithm, which is mathematically identical
    to the 19th-century Gauss / Meeuwes computations but avoids the table of
    epacts the classical method relies on. Chosen because it has no branches
    and, therefore, nothing to get wrong at a boundary.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return _dt.date(year, month, day)


class Easter:
    """Compute the date of Easter and the major movable feasts that depend
    on it.

    Western Christian tradition (Catholic and most Protestant churches)
    follows the Gregorian computus. Eastern Orthodox churches use the Julian
    calendar and a different paschal full-moon table; this class deliberately
    does not support them.

    The offset-based feasts (Septuagesima, Ash Wednesday, Ascension,
    Pentecost, Trinity) are fixed relative to Easter by centuries of rubric.
    The class computes them directly because every one of them is a simple
    day-count offset; inventing a more elaborate mechanism would be worse
    than the problem it solves.
    """

    def __init__(self, year: int) -> None:
        self.year = year
        self._easter = _easter_anonymous_gregorian(year)

    @property
    def date(self) -> _dt.date:
        """The date of Easter Sunday."""
        return self._easter

    def _shifted(self, days: int) -> _dt.date:
        """Return Easter shifted by *days* days (may be negative)."""
        return self._easter + _dt.timedelta(days=days)

    def septuagesima(self) -> _dt.date:
        """Ninth Sunday before Easter (63 days before)."""
        return self._shifted(-63)

    def ash_wednesday(self) -> _dt.date:
        """First day of Lent: 46 days before Easter."""
        return self._shifted(-46)

    def palm_sunday(self) -> _dt.date:
        """Sunday before Easter."""
        return self._shifted(-7)

    def maundy_thursday(self) -> _dt.date:
        """Thursday of Holy Week."""
        return self._shifted(-3)

    def good_friday(self) -> _dt.date:
        """Friday before Easter."""
        return self._shifted(-2)

    def ascension(self) -> _dt.date:
        """Ascension Day, 39 days after Easter (traditional Thursday).

        Some modern provinces transfer Ascension to the following Sunday;
        that is a pastoral decision and not part of the computus, so it is
        not supported here.
        """
        return self._shifted(39)

    def pentecost(self) -> _dt.date:
        """Whit Sunday, 49 days after Easter."""
        return self._shifted(49)

    def trinity_sunday(self) -> _dt.date:
        """First Sunday after Pentecost (56 days after Easter)."""
        return self._shifted(56)

    def corpus_christi(self) -> _dt.date:
        """Thursday after Trinity Sunday (60 days after Easter).

        Like Ascension, Corpus Christi is transferred to Sunday in some
        provinces; we return the traditional Thursday date.
        """
        return self._shifted(60)

    def as_dict(self) -> Dict[str, _dt.date]:
        """Return every feast in a name->date mapping."""
        return {
            "septuagesima": self.septuagesima(),
            "ash_wednesday": self.ash_wednesday(),
            "palm_sunday": self.palm_sunday(),
            "maundy_thursday": self.maundy_thursday(),
            "good_friday": self.good_friday(),
            "easter": self.date,
            "ascension": self.ascension(),
            "pentecost": self.pentecost(),
            "trinity_sunday": self.trinity_sunday(),
            "corpus_christi": self.corpus_christi(),
        }


# Fixed (immovable) solemnities in the modern Roman calendar. Dates that
# change based on whether they fall on a Sunday are given as (month, day);
# if the weekday equals Sunday the celebration is transferred to Monday
# (per the General Roman Calendar, 1969). This list is deliberately narrow.
_FIXED: Tuple[Tuple[int, int, str], ...] = (
    (1, 1, "Mary, Mother of God"),
    (1, 6, "Epiphany"),
    (3, 19, "St Joseph"),
    (3, 25, "Annunciation"),
    (6, 24, "Nativity of John the Baptist"),
    (6, 29, "SS Peter and Paul"),
    (8, 15, "Assumption"),
    (11, 1, "All Saints"),
    (12, 8, "Immaculate Conception"),
    (12, 25, "Christmas"),
)


def feasts_of(year: int) -> Dict[_dt.date, str]:
    """Return a mapping of date -> feast name for the given year.

    Combines the movable feasts (via :class:`Easter`) with a small set of
    immovable solemnities. When a fixed solemnity falls on a Sunday it is
    celebrated on the following Monday — this matches the post-1969 Roman
    rubric and is the only transfer we attempt. Solemnities that clash with
    Holy Week or the Easter octave are suppressed entirely; this is rare
    (e.g. St Joseph on 19 March 2008) and the suppression is itself the
    legitimate rubrical outcome, so we return nothing for that date rather
    than inventing a new one.
    """
    e = Easter(year)
    movable = e.as_dict()
    movable_dates = set(movable.values())

    # Holy Week and the Easter octave take precedence over everything; a
    # solemnity landing here is not celebrated at all that year.
    suppressed = set()
    holy_week_start = e.palm_sunday()
    low_sunday = e._shifted(7)  # Sunday after Easter = end of the octave
    cur = holy_week_start
    while cur <= low_sunday:
        suppressed.add(cur)
        cur += _dt.timedelta(days=1)

    result: Dict[_dt.date, str] = {d: n for n, d in movable.items()}

    for month, day, name in _FIXED:
        d = _dt.date(year, month, day)
        if d in suppressed:
            continue
        if d.weekday() == 6:  # Sunday
            d = d + _dt.timedelta(days=1)
        result[d] = name

    return result
