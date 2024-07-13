from typing import Type, Dict, Optional, List, Tuple, Any, Union
from pydantic import BaseModel, Field, confloat, field_serializer

from .region import Region


def serialize_regions(result):
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

    class Config:
        populate_by_name = True
        protected_namespaces = ()

    @field_serializer('result')
    def serialize_result(self, result):
        return serialize_regions(result)


class AnnotationValue(BaseModel):
    """ """
    
    was_cancelled: Optional[bool] = False
    ground_truth: Optional[bool] = False
    lead_time: Optional[float] = 0.0
    result_count: Optional[int] = 0
    completed_by: int

    result: Optional[List[Union[Dict[str, Any], Region]]]
    
    class Config:
        populate_by_name = True

    @field_serializer('result')
    def serialize_result(self, result):
        return serialize_regions(result)


class TaskValue(BaseModel):
    """ """
    
    data: Optional[dict]
    annotations: Optional[List[AnnotationValue]] = Field(default_factory=list)
    predictions: Optional[List[PredictionValue]] = Field(default_factory=list)
