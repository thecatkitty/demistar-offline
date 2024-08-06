from configparser import ConfigParser
from datetime import datetime
from PIL import ImageFont

from .metrics import hub, room


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

        self.hub_fonts = {
            'spot': ImageFont.truetype(parser['spotlight']['font'], hub.TITLE_SIZE),
            'listl': ImageFont.truetype(parser['list']['font'], hub.LIST_SIZE),
            'lists': ImageFont.truetype(parser['list']['font'], int(hub.LIST_SIZE / 2)),
        }
        self.room_fonts = {
            'spotl': ImageFont.truetype(parser['spotlight']['font'], room.TITLE_SIZE),
            'spots': ImageFont.truetype(parser['spotlight']['font'], room.HOST_SIZE),
            'listl': ImageFont.truetype(parser['list']['font'], room.LIST_SIZE),
            'lists': ImageFont.truetype(parser['list']['font'], int(room.LIST_SIZE / 2)),
        }
