from asyncio import run, Queue, gather, sleep
from os import listdir, cpu_count
from os.path import isfile, isdir, join, getsize
from shutil import disk_usage
from typing import Tuple

from config import Config
from display import Display
from util import DiskUsage, timer_async


class DiskFull(Exception):
    """Raised when the disk usage is above the set threshold"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def get_disk_usage(path: str) -> Tuple[float, float]:
    usage = disk_usage(path)
    return usage.free / usage.total, usage.used / usage.total


async def get_directory_items(directory: str, file_queue: Queue, directory_queue: Queue) -> Tuple[int, int, int]:
    files_found = 0
    directories_found = 0
    total_bytes = 0

    for item in listdir(directory):
        absolute_path = join(directory, item)
        if isfile(absolute_path):
            await file_queue.put(absolute_path)
            files_found += 1
            total_bytes += getsize(absolute_path)
        elif isdir(absolute_path):
            await directory_queue.put(absolute_path)
            directories_found += 1
        else:
            print(f"Skipping {absolute_path}")

    return files_found, directories_found, total_bytes


async def item_gatherer_worker(file_queue: Queue, directory_queue: Queue):
    files_found = 0
    directories_found = 0
    file_size = 0
    while not directory_queue.empty():
        directory = await directory_queue.get()
        ff, df, fs = await get_directory_items(directory, file_queue, directory_queue)
        files_found += ff
        directories_found += df
        file_size += fs

    return files_found, directories_found, file_size


@timer_async
async def get_items(file_directory: str) -> Tuple[int, int, int]:
    file_queue = Queue()
    directory_queue = Queue()

    files_found, directories_found, file_size = await get_directory_items(file_directory, file_queue, directory_queue)
    results = await gather(*[item_gatherer_worker(file_queue, directory_queue) for _ in range(cpu_count())])
    for files, directories, num_bytes in results:
        files_found += files
        directories_found += directories
        file_size += num_bytes

    return files_found, directories_found, file_size


def disk_monitor(path: str, used_threshold: DiskUsage = DiskUsage.VERY_HIGH):
    free, used = get_disk_usage(path)
    if used > used_threshold.value:
        raise DiskFull()


async def monitor_thread(config: Config, display: Display):
    while True:
        try:
            disk_monitor(config.path, config.used_threshold)
            await sleep(config.interval.value)
        except DiskFull:
            display.disk_full_notification()
            (files, directories, size), exec_time = await get_items(config.file_directory)
            display.print_stats(files, directories, size, exec_time)
            await sleep(config.interval.value)


if __name__ == "__main__":
    run(monitor_thread(
        config=Config.from_file("config.json"),
        display=Display()
    ))
