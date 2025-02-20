from dataclasses import dataclass
from typing import Any

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class JsonAPIResourceSchema:
    id: str

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, JsonAPIResourceSchema) and self.__class__ == other.__class__:
            return self.id == other.id
        return False

@dataclass_json
@dataclass
class JsonAPIError:
    status: str
    detail: str
    code: str


@dataclass_json
@dataclass
class JsonAPIResourceIdentifier:
    id: str
    type: str
