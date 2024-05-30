from typing import Type, Dict, Optional, List, Tuple, Any, Union
from pydantic import BaseModel, Field, confloat

from label_studio_sdk.label_interface.region import Region


def serialize_regions(result):
    """ """
    res = []
    relations = []
    for r in result:
        if isinstance(r, Region):
            res.append(r._dict())
            if r.has_relations:
                relations.append(r._dict_relations())
        else:
            res.append(r)

    return res + relations


class PredictionValue(BaseModel):
    """ """

    model_version: Optional[Any] = None
    score: Optional[float] = 0.00
    result: Optional[List[Union[Dict[str, Any], Region]]]
    # cluster: Optional[Any] = None
    # neighbors: Optional[Any] = None

    class Config:
        allow_population_by_field_name = True

    def serialize(self):
        """ """
        return {
            "model_version": self.model_version,
            "score": self.score,
            "result": serialize_regions(self.result),
        }


class AnnotationValue(BaseModel):
    """ """
    
    was_cancelled: Optional[bool] = False
    ground_truth: Optional[bool] = False
    lead_time: Optional[float] = 0.0
    result_count: Optional[int] = 0
    completed_by: int

    result: Optional[List[Union[Dict[str, Any], Region]]]
    
    class Config:
        allow_population_by_field_name = True

    def serialize(self):
        """ """
        return {
            "was_cancelled": self.was_cancelled,
            "ground_truth": self.ground_truth,
            "lead_time": self.lead_time,
            "result_count": self.result_count,
            "completed_by": self.completed_by,
            "result": serialize_regions(self.result),
        }


class TaskValue(BaseModel):
    """ """
    
    data: Optional[dict]
    annotations: Optional[List[AnnotationValue]]
    predictions: Optional[List[PredictionValue]]
