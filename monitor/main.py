from asyncio import run, Queue, gather, sleep
from os import listdir, cpu_count
from os.path import isfile, isdir, join, getsize, relpath
from shutil import disk_usage
from typing import Tuple, Optional, Any
from urllib.parse import quote

from aiohttp import ClientSession, FormData, ClientTimeout, ClientError

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


async def get_directory_items(directory: str, file_queue: Queue, directory_queue: Queue, base_dir: str) -> Tuple[
    int, int, int]:
    files_found = 0
    directories_found = 0
    total_bytes = 0

    for item in listdir(directory):
        if item.startswith("."):
            continue
        absolute_path = join(directory, item)
        if isfile(absolute_path):
            parent_relative = relpath(directory, base_dir)
            target_dir: Optional[str]
            if parent_relative == "." or parent_relative == "":
                target_dir = None
            else:
                target_dir = parent_relative.replace("\\", "/")

            total_bytes += getsize(absolute_path)
            await file_queue.put((absolute_path, target_dir, total_bytes))
            files_found += 1
        elif isdir(absolute_path):
            await directory_queue.put(absolute_path)
            directories_found += 1
        else:
            print(f"Skipping {absolute_path}")

    return files_found, directories_found, total_bytes


async def item_gatherer_worker(file_queue: Queue, directory_queue: Queue, base_dir: str):
    files_found = 0
    directories_found = 0
    file_size = 0
    while not directory_queue.empty():
        directory = await directory_queue.get()
        ff, df, fs = await get_directory_items(directory, file_queue, directory_queue, base_dir)
        files_found += ff
        directories_found += df
        file_size += fs

    return files_found, directories_found, file_size


@timer_async
async def get_items(file_directory: str) -> tuple[int, int, int, Queue[Any]]:
    file_queue = Queue()
    directory_queue = Queue()

    files_found, directories_found, file_size = await get_directory_items(file_directory, file_queue, directory_queue,
                                                                          file_directory)
    results = await gather(
        *[item_gatherer_worker(file_queue, directory_queue, file_directory) for _ in range(cpu_count())])
    for files, directories, num_bytes in results:
        files_found += files
        directories_found += directories
        file_size += num_bytes

    return files_found, directories_found, file_size, file_queue


def disk_monitor(path: str, used_threshold: DiskUsage = DiskUsage.VERY_HIGH):
    free, used = get_disk_usage(path)
    if used > used_threshold.value:
        raise DiskFull()


async def send_file(session: ClientSession, config: Config, target_file: str, target_directory: Optional[str]):
    if target_directory:
        url = f"http://{config.host}/upload?target_directory=uploads/{quote(target_directory)}"
    else:
        url = f"http://{config.host}/upload"
    if "/" in target_file:
        filename = target_file.split("/")[-1]
    elif "\\" in target_file:
        filename = target_file.split("\\")[-1]
    else:
        filename = target_file
    with open(target_file, "rb") as f:
        data = FormData()
        data.add_field(
            name="file",
            value=f,
            filename=filename,
            content_type="text/plain"
        )

        timeout = ClientTimeout(total=600)
        try:
            async with session.post(url, data=data, timeout=timeout) as resp:
                if resp.status != 200:
                    print(f"Failed to send file {target_file}")
                    print(resp.status)
                    print(await resp.text())
        except ClientError as e:
            print(f"Failed to send file {target_file}")
            print(e)
            await send_file(session, config, target_file, target_directory)


async def send_files(session: ClientSession, config: Config, file_queue: Queue, display_queue: Queue, display: Display):
    while not file_queue.empty():
        target_file, target_directory, size = await file_queue.get()
        await send_file(session, config, target_file, target_directory)
        display.stats.files_sent = 1
        display.stats.bytes_sent = size
        await display_queue.put(target_file)


async def monitor_thread(config: Config, display: Display):
    file_directory = config.file_directory
    display_queue = Queue()
    async with ClientSession() as session:
        while True:
            try:
                disk_monitor(config.path, config.used_threshold)
                await sleep(config.interval.value)
            except DiskFull:
                display.disk_full_notification()
                (files, directories, size, file_queue), exec_time = await get_items(file_directory)
                display.print_stats(files, directories, size, exec_time)
                await gather(*[send_files(session, config, file_queue, display_queue, display) for _ in
                               range(config.sender_threads)], display.sender_display_thread(display_queue))


if __name__ == "__main__":
    cfg = Config.from_file("config.json")
    disp = Display(cfg)
    run(monitor_thread(
        config=cfg,
        display=disp,
    ))
