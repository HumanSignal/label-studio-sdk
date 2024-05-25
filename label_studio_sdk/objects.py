from typing import Type, Dict, Optional, List, Tuple, Any, Union
from pydantic import BaseModel, confloat

from label_studio_sdk.label_interface.region import Region


class PredictionValue(BaseModel):
    """ """

    model_version: Optional[Any] = None
    score: Optional[float] = 0.00
    result: Optional[List[Union[Dict[str, Any], Region]]] = []
    # cluster: Optional[Any] = None
    # neighbors: Optional[Any] = None

    def serialize(self):
        """ """
        res = []
        relations = []
        for r in self.result:
            if isinstance(r, Region):
                res.append(r._dict())
                if r.has_relations():
                    relations.append(r._dict_relations())
            else:
                res.append(r)

        result = res + relations
        
        return {
            "model_version": self.model_version,
            "score": self.score,
            "result": result,
        }


class AnnotationValue(BaseModel):
    """ """

    result: Optional[List[dict]]


class TaskValue(BaseModel):
    """ """

    data: Optional[dict]
    annotations: Optional[List[AnnotationValue]]
    predictions: Optional[List[PredictionValue]]
