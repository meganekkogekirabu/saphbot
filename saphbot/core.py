"""
Core boilerplate code for SaphBot.

Copyright (c) 2026 Choi Madeleine

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

from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import logging
from pywikibot.page import Page
from queue import Queue
from threading import Thread
from typing import Iterable, Optional
from typing_extensions import Self

from lib.misc import normalise

logger = logging.getLogger("saphbot.core")


@dataclass
class SaphBotOptions:
    dry_run: bool
    normalise: bool


# Subclasses must implement gen, summary, and treat.
class SaphBot:
    gen: Iterable[Page]
    summary: str
    _save_queue: Queue[Optional[Page]]
    _executor: ThreadPoolExecutor
    __options: SaphBotOptions

    @abstractmethod
    def treat(self, page: Page) -> Optional[Page]:
        pass

    def __init__(self, options: SaphBotOptions):
        self.__options = options
        self._save_queue = Queue(maxsize=25)
        self._saver = self._saver_dry if self.__options.dry_run else self._saver_wet
        self._executor = ThreadPoolExecutor()

    # Subclass bullshittery.

    __subclass: type[Self]

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls is SaphBot:
            return
        SaphBot.__subclass = cls

    @classmethod
    def get_entry(cls) -> type[Self]:
        if cls.__subclass is None:
            logger.error("no entry point registered")
            raise RuntimeError
        return cls.__subclass

    # To avoid having a check on self.__options.dry_run every
    # time we save, initialise with one of two separate
    # versions of saver.

    def _saver_wet(self):
        while True:
            page = self._save_queue.get()
            if page is None:
                break
            logger.info(f"attempting to save {page.title()}")
            try:
                page.save(self.summary, quiet=True)
            except Exception as e:
                print(type(e))
                logger.error(f"failed to save {page.title()}: {e}")
            self._save_queue.task_done()

    def _saver_dry(self):
        while True:
            page = self._save_queue.get()
            if page is None:
                break
            logger.info(f"dry run: saving {page.title()}")
            self._save_queue.task_done()

    def _processor(self, page: Page):
        try:
            logger.debug(f"processing {page.title()}")
            new = self.treat(page)
            if new is not None:
                if self.__options.normalise:
                    new = normalise(new)
                self._save_queue.put(new)
        except Exception as e:
            logger.error(f"error processing {page.title()}: {e}")

    def _start(self):
        saver = Thread(target=self._saver, daemon=True)
        saver.start()
        for _ in self._executor.map(self._processor, self.gen):
            pass
        self._save_queue.join()
        self._save_queue.put(None)
        saver.join()
        self._executor.shutdown(wait=True)
