from pydantic import BaseModel
from typing import List, Optional


class KeyInformation(BaseModel):

    label: str

    value: str


class ExtractedTask(BaseModel):

    title: str

    deadline: Optional[str] = None

    source: Optional[str] = None


class ProcessResponse(BaseModel):

    success: bool

    filename: str

    transcript: str

    summary: str

    key_information: List[KeyInformation]

    tasks: List[ExtractedTask]