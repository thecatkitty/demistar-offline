from argparse import ArgumentParser
from datetime import datetime, timedelta
from PIL import Image

from demistar.olhub import Configuration, HubDisplay, RoomDisplay, timeline

parser = ArgumentParser(description='Demistar Offline Hub generator script')
parser.add_argument('room',
                    nargs='+', help='room identifier(s)', metavar='ROOM')
parser.add_argument('-c', '--config',
                    help='configuration file path', default='demistar.ini')
parser.add_argument('-f', '--feature',
                    help='featured room identifier', metavar='ROOM')
parser.add_argument('-p', '--prefix',
                    help='hub output file name prefix', metavar='PREFIX', default='hub')
parser.add_argument('-t', '--title',
                    help='hub title')
args = parser.parse_args()

is_hub = len(args.room) > 1
config = Configuration(args.config)
sch = list(timeline.from_file(config.schedule_file, args.room, is_hub))

feat = list()
feat_title = ''
if not is_hub and args.feature is not None:
    feat = list(timeline.from_file(config.schedule_file, [args.feature], True))
    feat_title = config.rooms[args.feature][0]


def get_display(now: datetime) -> object:
    def upcoming(m: timeline.Meeting): return m.end() > now

    if is_hub:
        return HubDisplay(args.prefix, args.title.split(';'), list(sorted(filter(upcoming, sch), key=lambda m: m.start)), config, now)

    room = args.room[0]
    return RoomDisplay(room, config.rooms[room][0], list(filter(upcoming, sch)), feat_title, list(filter(upcoming, feat)), config, now)


bg = Image.open(config.hub_bg if is_hub else config.room_bg)
prev = None
now = config.start_time
while now < config.end_time:
    print(f"{now}: ", end="")

    display = get_display(now)
    if display.no_change(prev):
        print("no change")
    else:
        display.save_image(bg, True)

    prev = display
    now += timedelta(minutes=30)
