from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
class JsonAPIResourceSchema:
    pass


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
