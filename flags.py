import json
import multiprocessing
import os
import shutil
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime

import requests

# Constants for getting flags from this website
LIST_URL: str = 'https://flagcdn.com/en/codes.json'
URL: str = 'https://flagcdn.com/w40/'
POSTFIX: str = '.png'

# Options for download methods
SEQUENTIAL: str = 'sequential'
THREADING: str = 'threading'
MULTIPROCESSING: str = 'multiprocessing'

# Constants for changing the behavior of the program
FOLDER: str = 'flags'
# Possible values: sequential, threading, multiprocessing
METHOD: str = MULTIPROCESSING


# flag downloader interface
class FlagDownloader(ABC):
    @abstractmethod
    def download_flags(self, country_codes):
        pass


# each implementation of FlagDownloader has an internal method to download one flag
# and a public method to download all flags
class SequentialFlagDownloader(FlagDownloader):
    @classmethod
    def _download_flag(cls, country_code):
        r = requests.get(f'{URL}{country_code}{POSTFIX}')
        if r.ok:
            with open(f'{FOLDER}/{country_code}{POSTFIX}', 'wb') as f:
                f.write(r.content)
        return len(r.content)

    def download_flags(self, country_codes):
        bytes_downloaded = 0
        for country_code in country_codes:
            bytes_downloaded += self._download_flag(country_code)
        return bytes_downloaded


class ThreadedFlagDownloader(FlagDownloader):
    @classmethod
    def _download_flag(cls, country_code, bytes_list):
        r = requests.get(f'{URL}{country_code}{POSTFIX}')
        if r.ok:
            with open(f'{FOLDER}/{country_code}{POSTFIX}', 'wb') as f:
                f.write(r.content)
        bytes_list.append(len(r.content))

    def download_flags(self, country_codes):
        bytes_list = []
        threads = []
        for country_code in country_codes:
            thread = threading.Thread(target=self._download_flag, args=(country_code, bytes_list))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        return sum(bytes_list)


class MultiProcessFlagDownloader(FlagDownloader):
    @classmethod
    def _download_flag(cls, country_code, bytes_queue):
        r = requests.get(f'{URL}{country_code}{POSTFIX}')
        if r.ok:
            with open(f'{FOLDER}/{country_code}{POSTFIX}', 'wb') as f:
                f.write(r.content)
        bytes_queue.put(len(r.content))

    def download_flags(self, country_codes):
        processes = []
        bytes_queue = multiprocessing.Queue()
        for flag in flags:
            process = multiprocessing.Process(target=self._download_flag, args=(flag, bytes_queue))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
        bytes_downloaded = 0
        while not bytes_queue.empty():
            bytes_downloaded += bytes_queue.get()
        return bytes_downloaded


if __name__ == '__main__':
    # remove folder if exists, then create it
    try:
        shutil.rmtree(FOLDER)
    except FileNotFoundError:
        pass
    os.mkdir(FOLDER)

    # get list of country codes from request
    list_request = requests.get(LIST_URL)
    if not list_request.ok:
        raise RuntimeError('Could not get list of flag code to download')
    try:
        flags = json.loads(list_request.content)
    except json.JSONDecodeError:
        raise RuntimeError('Could not decode flag codes json')

    print(f'Downloading {len(flags)} flags ({METHOD})')

    # determine type of flag_downloader
    flag_downloader = None
    if METHOD == SEQUENTIAL:
        flag_downloader = SequentialFlagDownloader()
    elif METHOD == THREADING:
        flag_downloader = ThreadedFlagDownloader()
    elif METHOD == MULTIPROCESSING:
        flag_downloader = MultiProcessFlagDownloader()
    else:
        raise RuntimeError(f'Unknown download method: {METHOD}')

    # initialize start variables
    start_time = time.perf_counter()

    # download
    bytes_downloaded = flag_downloader.download_flags(flags.keys())

    # end timer
    end_time = time.perf_counter()

    # print summary
    if len(os.listdir(FOLDER)) == len(flags):
        print('Items downloaded successfully')
    else:
        print('Error downloading some items')
    date_time = datetime.fromtimestamp(end_time - start_time)
    print(f'Elapsed time: {date_time.strftime("%M:%S")}')
    print(f'{bytes_downloaded} bytes downloaded')
