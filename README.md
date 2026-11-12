# Calendar UID Map

Before importing two calendar exports, check which records describe the same series. A master event, a moved occurrence, and its reminder can each carry identifiers. This local CLI lists them by component and flags missing resource UIDs and repeated master records of the same component type and UID.

## Try the example

With Python 3.10 or newer, run these commands from the checkout.

```sh
python -m pip install .
calendar-uid-map examples/series.ics
```

The sample has one master meeting, one reminder with its own UID, and one occurrence that moved from 09:00 to 10:00. The occurrence keeps its original 09:00 recurrence ID and shares the master’s UID.

## Compare exports

```sh
calendar-uid-map --json --check old.ics new.ics
```

Exit status 0 means the scan finished without a flagged identity (or check mode was off), 1 means there were findings, and 2 means an input or argument error. A repeated master can be an intentional copy across calendars. Inspect both records before importing. All processing is local and read-only. The report includes file paths and identifiers.

Run the tests with `python -m unittest`.
