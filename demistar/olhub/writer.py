import math
import os
import subprocess

from datetime import datetime
from ffmpy import FFmpeg
from PIL import Image, ImageDraw


class ScrollingWriter:
    def __init__(self, prefix: str, bg: Image.Image) -> None:
        self.prefix = prefix
        self.frame = bg.crop((0, 0, 1080, 1920))
        self.draw = ImageDraw.Draw(self.frame)

        # Create subdirectories
        os.makedirs(f"out/{self.prefix}", exist_ok=True)

    def save(self, time: datetime, scrolled: list, window_width: int, progress: bool = False) -> int:
        timestamp = f"{time:%Y%m%dT%H%M}"

        # Nothing to scroll, single frame
        if len(scrolled) == 0:
            if progress:
                print("single frame", end='')
            self.frame.save(f"out/{self.prefix}/{self.prefix}-{timestamp}.jpg")
            return 1

        # Render all frames
        length = max(text.width for _, text in scrolled) + window_width
        digits = math.ceil(math.log10(length))

        ff = FFmpeg(
            global_options=['-hide_banner', '-loglevel error'],
            inputs={'pipe:0': '-y -f image2pipe -r 30'},
            outputs={f"out/{self.prefix}/{self.prefix}-{timestamp}.mp4": None})
        proc = subprocess.Popen(ff.cmd, stdin=subprocess.PIPE)

        if progress:
            print(" " * (digits * 2 + 1), end="")

        for i in range(length):
            frame = self.frame.copy()
            frame_draw = ImageDraw.Draw(frame)
            for position, text in scrolled:
                frame_draw.bitmap(position, text.crop(
                    (i - window_width, 0, i, text.height)))

            frame.save(proc.stdin, format="jpeg")
            if progress:
                print("\b" * (digits * 2 + 1) +
                      f"{(i + 1):{digits}}/{length}", end="", flush=True)

        proc.stdin.close()
        assert 0 == proc.wait()
        return length
