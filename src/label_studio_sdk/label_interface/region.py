"""
"""

import json
from uuid import uuid4

from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field


class Region(BaseModel):
    """
    A Region is an item in the `result` list of a PredictionValue or AnnotationValue.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    from_tag: Any
    to_tag: Any
    value: Any
    relations: Optional[List[Dict]] = []

    def _dict(self):
        """ """
        return {
            "id": self.id,
            "from_name": self.from_tag.name,
            "to_name": self.to_tag.name,
            "type": self.from_tag.tag.lower(),
            # TODO This needs to be improved
            "value": self.value.dict(),
        }

    def _dict_relations(self):
        """ """
        # this code does not include "labels" key if no labels were passed
        return [
            {**{
                "from_id": self.id,
                "to_id": rel.get("region", {}).id,
                "type": "relation",
                "direction": rel.get("direction", "right")},
             **({"labels": rel["labels"]} if rel.get("labels") else {})
             }
            for rel in self.relations
        ]
               
    def to_json(self):
        """ """
        return json.dumps(self._dict())

    def to_json_relations(self):
        """ """
        return json.dumps(self._dict_relations())

    @property
    def has_relations(self):
        return len(self.relations) > 0
    
    def add_relation(self, region=None, direction="right", label=None):
        """ """
        self.relations.append({ "region": region, "direction": direction, "labels": label })
        
    def set_relations(self, rels):
        """ """
        self.relations = rels
        
