# Ecclesiastical Calendar

Computes Western (Gregorian) liturgical dates: Easter and the movable feasts
derived from it, plus a small set of fixed solemnities from the modern Roman
calendar.

## Usage

```python
from ecclesiastical_calendar import Easter, feasts_of, golden_number

# Easter Sunday and the major movable feasts
e = Easter(2024)
print(e.date)                 # 2024-03-31
print(e.ash_wednesday())      # 2024-02-14
print(e.pentecost())          # 2024-05-19
print(e.as_dict())             # name -> date for all movable feasts

# Fixed and movable solemnities combined, keyed by date
for date, name in sorted(feasts_of(2024).items()):
    print(date, name)

# Golden Number of the liturgical cycle
print(golden_number(2024))    # 11
```

Exported names: `Easter` (class), `feasts_of` (function), `golden_number`
(function).

## Why this exists

The computus for Western Easter is a closed-form arithmetic expression; it
does not require a library. What does require code is the *collection* of
feasts that depend on it (Septuagesima, Ash Wednesday, Ascension, Pentecost,
Trinity, Corpus Christi) plus the rules for what happens when fixed
solemnities collide with Sundays or Holy Week. This library packages those
rules so that downstream code does not have to re-derive them.

The trade-off: scope is deliberately narrow. Only the modern Roman calendar's
principal solemnities are included. Local calendars, saints' days, and the
pre-1969 (Tridentine) calendar are out of scope. Eastern Orthodox computus is
not supported — the Julian paschalion is a separate problem.

## Awkward edges

When a fixed solemnity falls on a Sunday it is transferred to the following
Monday (the post-1969 Roman rubric). When one falls in Holy Week or the
Easter octave it is *suppressed* entirely for that year — not transferred.
Both behaviours are reflected in `feasts_of`. For example, St Joseph (19
March) was suppressed in 2008, and the Annunciation (25 March) was
suppressed in 2024. If you need a transferred date in those cases, this
library will not give it to you; that is a pastoral decision outside the
computus.

Ascension and Corpus Christi are returned on their traditional Thursday
dates. Many provinces transfer them to the following Sunday; that transfer is
not applied here.
