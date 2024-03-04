
from typing import Type, Dict, Optional, List, Tuple, Any, Union
from pydantic import BaseModel, confloat


class PredictionValue(BaseModel):
    """
    """
    model_version: Optional[Any] = None
    score: Optional[float] = 0.00
    result: Optional[List[Any]] = []
    # cluster: Optional[Any] = None
    # neighbors: Optional[Any] = None

    def serialize(self):
        from label_studio_sdk.label_interface.region import Region
        
        return {
            "model_version": self.model_version,
            "score": self.score,
            "result": [r._dict() if isinstance(r, Region) else r for r in self.result]
        }


class AnnotationValue(BaseModel):
    """
    """
    result: Optional[List[dict]]
    

class TaskValue(BaseModel):
    """
    """
    data: Optional[dict]
    annotations: Optional[List[AnnotationValue]]
    predictions: Optional[List[PredictionValue]]
