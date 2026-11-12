import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from calendar_uid_map import main, scan

EXAMPLE = Path(__file__).parent / "examples" / "series.ics"


class IdentityTests(unittest.TestCase):
    def test_alarm_and_override(self):
        master, override = scan([EXAMPLE])
        self.assertEqual(master["uid"], "meeting@example.invalid")
        self.assertEqual(master["alarm_uids"], ["reminder@example.invalid"])
        self.assertEqual(override["recurrence"], "20261113T090000Z")
        self.assertFalse(any(row["finding"] for row in (master, override)))

    def test_two_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            other = Path(tmp) / "copy.ics"
            other.write_bytes(EXAMPLE.read_bytes())
            rows = scan([EXAMPLE, other])
            self.assertEqual([r["finding"] for r in rows],
                             ["repeated master", None, "repeated master", None])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--check", str(EXAMPLE), str(other)]), 1)

    def test_missing_uid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.ics"
            path.write_text(EXAMPLE.read_text().replace("UID:meeting@example.invalid\n", "", 1))
            self.assertEqual(scan([path])[0]["finding"], "missing UID")


if __name__ == "__main__":
    unittest.main()
