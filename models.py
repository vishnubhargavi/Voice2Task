from pydantic import BaseModel
from typing import Optional


class TaskCreate(BaseModel):

    title: str

    deadline: Optional[str] = None

    source: Optional[str] = None


class TaskUpdate(BaseModel):

    title: Optional[str] = None

    deadline: Optional[str] = None

    completed: Optional[bool] = None