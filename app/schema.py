from pydantic import BaseModel
from typing import Optional, List

class TitanicRequest(BaseModel):
    Pclass: int
    Sex: str
    Age: Optional[float] = None
    SibSp: int
    Parch: int
    Fare: float
    Embarked: Optional[str] = None

class BatchRequest(BaseModel):
    instances: List[TitanicRequest]