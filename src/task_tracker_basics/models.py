from pydantic import BaseModel, field_validator


class TaskModel(BaseModel):
    task_id: int
    title: str
    done: bool = False

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must not be blank")
        return value

class TaskListModel(BaseModel):
    owner_name: str
    tasks: list[TaskModel]