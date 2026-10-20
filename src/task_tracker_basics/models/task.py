from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import UserORM

from sqlalchemy import ForeignKey, Text, String, func, false, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TaskORM(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text,default=None)
    is_done: Mapped[bool] = mapped_column(server_default=false(), default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["UserORM"] = relationship(back_populates="tasks")
