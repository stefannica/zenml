from typing import List, Any

from pydantic import BaseModel


class Artifact(BaseModel):
    name: str = None
    is_dir: bool = None
    signed_url: List[str] = []
    children: List[Any] = []
