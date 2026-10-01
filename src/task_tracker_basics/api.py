from fastapi import FastAPI, HTTPException
from task_tracker_basics.models import TaskModel
from task_tracker_basics import storage


from fastapi.responses import StreamingResponse
import asyncio


app = FastAPI()

async def _stream_words(text: str):
    for word in text:
        yield f"{word}"
        await asyncio.sleep(0.3)


@app.get("/tasks")
def list_tasks() -> list[TaskModel]:
    return storage.get_all_tasks()


@app.post("/tasks")
def create_task(title: str) -> TaskModel:
    return storage.add_task(title=title)


@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> TaskModel:
    task = storage.get_task_by_id(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks/{task_id}/stream-summary")
async def stream_summary(task_id: int):
    task = storage.get_task_by_id(task_id=task_id)
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return StreamingResponse(
        _stream_words(f"Резюме для {task.title}: оброблено успішно"),
        media_type="text/plain",
    )


