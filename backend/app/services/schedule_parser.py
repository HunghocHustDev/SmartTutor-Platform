"""
Schedule parsing utilities for preferred_schedule field.

Format: "<days> <start_time>-<end_time>"
Examples:
  "T2,T4 17:00-19:00"
  "T2 17:00-19:00"
  "T2,T3,T6 08:00-12:00"
  "T7,CN 14:00-17:00"

Days are Vietnamese abbreviations:
  T2 = Monday (1), T3 = Tuesday (2), T4 = Wednesday (3),
  T5 = Thursday (4), T6 = Friday (5), T7 = Saturday (6),
  CN  = Sunday (7)
"""

from dataclasses import dataclass
from datetime import time
from typing import Optional


# Inlined here to avoid circular import with app.services.common
DAY_LABELS = {
    1: "T2",
    2: "T3",
    3: "T4",
    4: "T5",
    5: "T6",
    6: "T7",
    7: "CN",
}


DAY_TO_NUM = {v: k for k, v in DAY_LABELS.items()}


@dataclass
class ParsedSchedule:
    days: set[int]
    start_time: Optional[time]
    end_time: Optional[time]

    def has_time(self) -> bool:
        return self.start_time is not None and self.end_time is not None

    def to_display(self) -> str:
        if not self.days:
            return ""
        day_names = sorted(self.days, key=lambda d: d)
        day_str = ",".join(DAY_LABELS.get(d, str(d)) for d in day_names)
        if self.start_time and self.end_time:
            return f"{day_str} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
        return day_str


def _parse_time(time_str: str) -> Optional[time]:
    time_str = time_str.strip()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p"):
        try:
            from datetime import datetime
            t = datetime.strptime(time_str, fmt).time()
            return t
        except ValueError:
            pass
    return None


def parse_preferred_schedule(raw: Optional[str]) -> ParsedSchedule:
    """
    Parse a preferred_schedule string into structured data.
    Returns a ParsedSchedule with:
      - days: set of day numbers (1=Mon .. 7=Sun), empty if unparseable
      - start_time / end_time: time objects, None if unparseable
    """
    if not raw or not raw.strip():
        return ParsedSchedule(days=set(), start_time=None, end_time=None)

    raw = raw.strip()

    days: set[int] = set()
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    # Normalize: remove extra spaces, normalize "CN"
    raw = raw.upper().replace("CHỦ NHẬT", "CN").replace("C.N", "CN").replace("C.N.", "CN")
    parts = raw.split()

    # First part(s) should be day tokens
    day_part = ""
    time_part = ""
    for i, part in enumerate(parts):
        part_clean = part.strip(",")
        # Try to parse as day token
        day_num = _try_parse_day(part_clean)
        if day_num is not None:
            days.add(day_num)
            day_part += part_clean + ","
        else:
            day_part = day_part.strip(",")
            # Everything after day tokens is time part
            time_part = " ".join(parts[i:])
            break

    # Parse time part "HH:MM-HH:MM"
    time_part = time_part.strip()
    if "-" in time_part:
        segs = time_part.split("-")
        if len(segs) == 2:
            start_time = _parse_time(segs[0])
            end_time = _parse_time(segs[1])
            if end_time and start_time and end_time <= start_time:
                # Try swapping if parsed incorrectly
                end_time = None
    elif time_part:
        # Could be just start time
        t = _parse_time(time_part)
        if t:
            start_time = t

    return ParsedSchedule(days=days, start_time=start_time, end_time=end_time)


def _try_parse_day(token: str) -> Optional[int]:
    token = token.strip(",").strip()
    if token in DAY_TO_NUM:
        return DAY_TO_NUM[token]
    # Try T + number
    if token.startswith("T") and token[1:].isdigit():
        num = int(token[1:])
        if 2 <= num <= 7:
            return num
    # "T10" -> 2, "T11" -> 3 etc. (not applicable)
    return None


def check_time_overlap(
    req_start: time,
    req_end: time,
    avail_start: time,
    avail_end: time,
) -> tuple[bool, int]:
    """
    Check if two time ranges overlap, and return overlap duration in minutes.

    Returns (has_overlap, overlap_minutes).
    """
    if req_start >= avail_end or req_end <= avail_start:
        return False, 0
    overlap_start = max(req_start, avail_start)
    overlap_end = min(req_end, avail_end)
    if overlap_start >= overlap_end:
        return False, 0
    from datetime import datetime, timedelta
    d = datetime.combine(datetime.today(), overlap_end) - datetime.combine(datetime.today(), overlap_start)
    return True, int(d.total_seconds() / 60)


def build_schedule_display(days: set[int], start_time: Optional[time], end_time: Optional[time]) -> str:
    """Build a human-readable schedule string."""
    if not days:
        return ""
    sorted_days = sorted(days, key=lambda d: d)
    parts = [DAY_LABELS.get(d, str(d)) for d in sorted_days]
    day_str = ",".join(parts)
    if start_time and end_time:
        return f"{day_str} {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
    return day_str
