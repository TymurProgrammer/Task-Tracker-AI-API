from task_tracker_basics.task import Task
from task_tracker_basics.ai_client import AIMockClient
import asyncio
import time

async def summarize_all(tasks: list[Task], client: AIMockClient) -> list[str]:
    coroutines = [client(task) for task in tasks]
    results = await asyncio.gather(*coroutines)
    return results

def main():
    start = time.perf_counter()

    task1 = Task(1, "Go swimming", False)
    task2 = Task(2, "Wash the dishes", True)
    task3 = Task(3, "Stretch", False)

    tasks = []
    tasks.append(task1)
    tasks.append(task2)
    tasks.append(task3)

    ai_client = AIMockClient(2)

    task_dup1 = Task(1, "Something")
    task_dup2 = Task(1, "Something else")
    print(task_dup1 == task_dup2)

    results = asyncio.run(summarize_all(tasks, ai_client))
    print(results)

    end = time.perf_counter()
    print(f"Час виконання: {end - start:.2f} сек")
    

if __name__ == "__main__":
    main()
