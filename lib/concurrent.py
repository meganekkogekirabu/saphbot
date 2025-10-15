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
