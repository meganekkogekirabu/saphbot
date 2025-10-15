"""
Framework for concurrently processing pages while saving them
sequentially.

Copyright (c) 2025 Choi Madeleine

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

__all__ = ["ConcurrentBot"]

from concurrent.futures import as_completed, ThreadPoolExecutor
from queue import Queue
from threading import Thread
from typing import Callable, Iterable
from pywikibot.page import Page


class ConcurrentBot:
    treat: Callable[[Page], Page | None]
    gen: Iterable[Page]
    save_queue: Queue
    executor: ThreadPoolExecutor
    summary: str

    def __init__(
        self,
        treat: Callable[[Page], Page | None],
        summary: str,
        gen: Iterable[Page],
        max_workers: int = 5,
    ):
        self.treat = treat
        self.summary = summary
        self.gen = gen
        self.save_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def saver(self) -> None:
        while True:
            page = self.save_queue.get()
            page.save(self.summary)
            self.save_queue.task_done()

    def start(self) -> None:
        Thread(target=self.saver).start()
        future_to_page = {
            self.executor.submit(self.treat, page): page for page in self.gen
        }
        for future in as_completed(future_to_page):
            page = future.result()
            if page is None:
                continue
            else:
                self.save_queue.put(page)
