import asyncio
from task_tracker_basics.task import Task

class AIMockClient:
    def __init__(self, delay: int):
        self.delay = delay

    async def __call__(self, task: Task) -> str:
        await asyncio.sleep(self.delay)
        return f"Резюме для '{task.title}': оброблено"

    
    

