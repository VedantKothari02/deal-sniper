import asyncio

class JobQueue:
    def __init__(self):
        self.queue = None

    def _init_queue(self):
        if self.queue is None:
            self.queue = asyncio.Queue()

    async def put(self, item):
        self._init_queue()
        await self.queue.put(item)

    async def get(self):
        self._init_queue()
        return await self.queue.get()

    def task_done(self):
        self._init_queue()
        self.queue.task_done()

    def qsize(self):
        if self.queue is None:
            return 0
        return self.queue.qsize()
