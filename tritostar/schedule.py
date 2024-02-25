import csv
from datetime import datetime, timedelta
from typing import Generator


class Meeting:
    def __init__(self, line: list[str]) -> None:
        self.room = line[0]
        self.start = datetime.strptime(line[1], "%d.%m.%Y %H:%M")
        self.duration = int(line[2])
        self.title = line[3]
        self.host = line[4]
        self.annotations = line[5]
        self.no_hub = bool(line[6])

    def __str__(self) -> str:
        return f"<Meeting in {self.room} at {self.start}: \"{self.title}\" by {self.host} ({self.duration}m)>"

    def end(self) -> datetime:
        return self.start + timedelta(minutes=self.duration)


def from_file(name: str, rooms: list[str], hub: bool) -> Generator[Meeting, None, None]:
    with open(name, encoding="utf-8") as tsv:
        for line in csv.reader(tsv, dialect="excel-tab"):
            meeting = Meeting(line)
            if meeting.room not in rooms:
                continue

            if hub and meeting.no_hub:
                continue

            yield meeting
