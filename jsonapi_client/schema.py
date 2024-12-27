from dataclasses import dataclass
from datetime import date, datetime

from dataclasses_json import cfg, dataclass_json

cfg.global_config.decoders[date] = date.fromisoformat
cfg.global_config.decoders[datetime] = datetime.fromisoformat


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
