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

from concurrent.futures import ThreadPoolExecutor
import logging
from queue import Queue
from threading import Thread
from typing import Callable, Iterable, Optional
from pywikibot.page import Page

logger = logging.getLogger("saphbot.lib.multiprocessor")


class ConcurrentBot:
    treat: Callable[[Page], Optional[Page]]
    gen: Iterable[Page]
    save_queue: Queue
    executor: ThreadPoolExecutor
    summary: str

    def __init__(
        self,
        treat: Callable[[Page], Optional[Page]],
        summary: str,
        gen: Iterable[Page],
        max_workers: int = 5,
    ):
        self.treat = treat
        self.summary = summary
        self.gen = gen
        self.save_queue = Queue(maxsize=5 * max_workers)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def _saver(self) -> None:
        while True:
            page = self.save_queue.get()
            logger.info(
                f"\033[1;31mConcurrentBot._saver\033[0m: attempting to save {page.title()}"
            )
            try:
                page.save(self.summary)
            except Exception as e:
                logger.error(
                    f"\033[1;31mConcurrentBot._saver\033[0m: \033[1;31mfailed\033[0m to save {page.title()}: {e}"
                )
            self.save_queue.task_done()

    def _processor(self, page: Page) -> None:
        try:
            logger.info(
                f"\033[1;32mConcurrentBot._processor\033[0m: processing {page.title()}"
            )
            res = self.treat(page)
            if res is not None:
                self.save_queue.put(res)
        except Exception as e:
            logger.error(
                f"\033[1;32mConcurrentBot._processor\033[0m: error processing {page.title()}: {e}"
            )

    def start(self) -> None:
        saver = Thread(target=self._saver, daemon=True)
        saver.start()
        self.executor.map(self._processor, self.gen)
        saver.join()
        self.executor.shutdown(wait=True)
