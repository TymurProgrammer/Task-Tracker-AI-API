class Task:
    def __init__(self, task_id: int, title: str, done: bool = False) -> None:
        self.task_id = task_id
        self.title = title
        self.done = done

    def __repr__(self) -> str:
        return f"Task(id = {self.task_id}, title={self.title}, done={self.done})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.task_id == other.task_id
