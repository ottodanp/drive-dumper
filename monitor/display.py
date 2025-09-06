from asyncio import Queue, sleep

from config import Config
from util import SizeDivisor

DIVISOR_EXTENSIONS = {
    SizeDivisor.GB: "GB",
    SizeDivisor.MB: "MB",
    SizeDivisor.KB: "KB",
    SizeDivisor.BYTES: "BYTES",
}


class Stats:
    _files_sent: int = 0
    _bytes_sent: int = 0

    def __init__(self):
        return

    @property
    def files_sent(self) -> int:
        return self._files_sent

    @files_sent.setter
    def files_sent(self, value):
        self._files_sent += value

    @property
    def bytes_sent(self) -> int:
        return self._bytes_sent

    @bytes_sent.setter
    def bytes_sent(self, value):
        self._bytes_sent += value


class Display:
    _config: Config
    _stats: Stats

    def __init__(self, config: Config):
        self._config = config
        self._stats = Stats()

    def print_stats(self, files: int, directories: int, size: int, time: float) -> None:
        print(f"Found {files} files and {directories} directories ({self.format_bytes(size)}) in {time:.2f} seconds.")

    def format_bytes(self, size: int) -> str:
        if size > SizeDivisor.GB.value:
            div = SizeDivisor.GB
        elif size > SizeDivisor.MB.value:
            div = SizeDivisor.MB
        elif size > SizeDivisor.KB.value:
            div = SizeDivisor.KB
        else:
            div = SizeDivisor.BYTES

        return f"{self.calculate_size(size, div)}{DIVISOR_EXTENSIONS[div]}"

    async def sender_display_thread(self, display_queue: Queue):
        while True:
            await sleep(2)
            message = ""
            i = 0
            while not display_queue.empty() and i < self._config.display_chunk_size:
                i += 1
                item = await display_queue.get()
                if item is None:
                    continue

                message += f"{item}\n"

            formatted_bytes = self.format_bytes(self._stats.bytes_sent)
            message += f"Files sent: {self._stats.files_sent}\n"
            message += f"Data sent: {formatted_bytes}\n"
            print(message)

    @staticmethod
    def disk_full_notification():
        print("Disk is full, moving files")

    @staticmethod
    def calculate_size(size: int, divisor: SizeDivisor) -> float:
        return round((size / divisor.value), 3)

    @property
    def stats(self) -> Stats:
        return self._stats
