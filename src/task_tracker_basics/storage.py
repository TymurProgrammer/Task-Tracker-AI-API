from task_tracker_basics.models import TaskModel


_tasks: list[TaskModel] = []
_next_id = 1


def add_task(title: str) -> TaskModel:
    global _next_id 

    new_task = TaskModel(task_id=_next_id,title=title)
    _tasks.append(new_task)

    _next_id +=1 
    
    return new_task


def get_all_tasks() -> list[TaskModel]:
    return _tasks


def get_task_by_id(task_id: int) -> TaskModel | None:
    for task in _tasks:
        if task.task_id == task_id:
            return task
    return None


    