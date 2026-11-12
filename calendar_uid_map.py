"""Map iCalendar resource identities without loading them into a calendar service."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

from icalendar import Calendar


def scan(paths):
    entries = []
    positions = defaultdict(list)
    for path in paths:
        calendars = Calendar.from_ical(path.read_bytes(), multiple=True)
        if not calendars or any(cal.name != "VCALENDAR" for cal in calendars):
            raise ValueError(f"{path}: expected a VCALENDAR export")
        for calendar in calendars:
            for component in calendar.subcomponents:
                if component.name not in {"VEVENT", "VTODO", "VJOURNAL", "VFREEBUSY"}:
                    continue
                uid = str(component.get("UID", ""))
                recurrence = component.get("RECURRENCE-ID")
                occurrence = None
                zone = None
                if recurrence is not None:
                    occurrence = recurrence.to_ical().decode()
                    zone = recurrence.params.get("TZID")
                alarms = [str(alarm["UID"]) for alarm in component.subcomponents
                          if alarm.name == "VALARM" and "UID" in alarm]
                row = dict(file=str(path), component=component.name, uid=uid,
                           recurrence=occurrence, timezone=zone, alarm_uids=alarms)
                entries.append(row)
                if uid and occurrence is None:
                    positions[component.name, uid].append(len(entries) - 1)
    duplicates = {i for indices in positions.values() if len(indices) > 1 for i in indices}
    for index, row in enumerate(entries):
        row["finding"] = ("missing UID" if not row["uid"] else
                          "repeated master" if index in duplicates else None)
    return entries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", type=Path, nargs="+", help="local .ics exports")
    parser.add_argument("--json", action="store_true", help="emit machine-readable rows")
    parser.add_argument("--check", action="store_true", help="exit 1 for identity findings")
    args = parser.parse_args(argv)
    try:
        rows = scan(args.files)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"{parser.prog}: {exc}\n")
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for row in rows:
            recurrence = row["recurrence"] or "master"
            if row["timezone"]:
                recurrence += f' ({row["timezone"]})'
            print(f'{row["file"]}  {row["component"]}  {row["uid"] or "(missing)"}  {recurrence}')
            for uid in row["alarm_uids"]:
                print(f'  alarm: {uid}')
            if row["finding"]:
                print(f'  finding: {row["finding"]}')
    return int(args.check and any(row["finding"] for row in rows))


if __name__ == "__main__":
    sys.exit(main())
