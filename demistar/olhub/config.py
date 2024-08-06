from configparser import ConfigParser
from datetime import datetime


class Configuration:
    def __init__(self, filename: str) -> None:
        parser = ConfigParser()
        parser.read(filename)

        self.start_time = datetime.strptime(
            parser['event']['start'], '%Y-%m-%d %H:%M')
        self.end_time = datetime.strptime(
            parser['event']['end'], '%Y-%m-%d %H:%M')
        self.schedule_file = parser['event']['schedule']
        self.rooms = {k: tuple(s.strip() for s in v.split(',', 1))[0]
                      for k, v in parser['rooms'].items()}
